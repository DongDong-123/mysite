import markdown
# from markdown.extensions.toc import TocExtension
from django.shortcuts import render, get_object_or_404
from .models import Post, Tag, Category
from comments.forms import CommentForm
from django.views.generic import ListView, DetailView
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.utils.text import slugify
from django.http import HttpResponse
from django.db.models import Q
# import time
# from django.views.generic import View
# from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import requests
from pyquery import PyQuery as pq

import redis
from random import choice

# 反爬22
from apilimiter.mixin import LimiterMixin
from apilimiter.decorators import limiter

# 邮件计数
MAIL_NUM = 0


# 首页
class IndexView(LimiterMixin, ListView):
   # key = 'user.id'
   # times = 20
   # redirect = ''
   # rate = 60

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'content'
    # 设置每页文章数量
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        pagination_data = self.pagination_data(paginator, page, is_paginated)

        context.update(pagination_data)

        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}
        # 当前页左边连续的页码号，初始值为空
        left = []
        # 当前页右边连续的页码号，初始值为空
        right = []
        # 标示第 1 页页码后是否需要显示省略号
        left_has_more = False
        # 标示最后一页页码前是否需要显示省略号
        right_has_more = False
        # 标示是否需要显示第 1 页的页码号
        first = False
        # 标示是否需要显示最后一页的页码号
        last = False
        # 获得用户当前请求的页码号
        page_number = page.number
        # 获取分页后的总页数
        total_page = paginator.num_pages
        # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
        page_range = paginator.page_range
        # 首页
        if page_number == 1:
            right = page_range[page_number:page_number + 2]
            if right[-1] < total_page - 1:
                right_has_more = True

            if right[-1] < total_page:
                last = True
        # 尾页
        elif page_number == total_page:
            left = page_range[total_page - 3 if total_page > 3 else 0: page_number - 1]

            if left[0] > 2:
                left_has_more = True

            if left[0] > 1:
                first = True
        # 中间页
        else:
            left = page_range[page_number - 3 if page_number - 3 > 0 else 0: page_number - 1]

            right = page_range[page_number:page_number + 2]

            if left[0] > 2:
                left_has_more = True

            if left[0] > 1:
                first = True

            if right[-1] < total_page - 1:
                right_has_more = True

            if right[-1] < total_page:
                last = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return data


# 分类
class CategoryView(IndexView):
    key = 'user.id'
    times = 20
    redirect = ''
    rate = 60

    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


# 归档
class ArchivesView(IndexView):
    key = 'user.id'
    times = 20
    redirect = ''
    rate = 60

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year, created_time__month=month)


# 标签云
class TagsView(LimiterMixin, ListView):
    key = 'user.id'
    times = 20
    redirect = ''
    rate = 60
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'content'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagsView, self).get_queryset().filter(tags=tag)


# 详情页
class PostDetialView(LimiterMixin, DetailView):
    key = 'user.id'
    times = 20
    redirect = ''
    rate = 60

    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'content'

    # read = Post()
    # read.increase_views()

    def get(self, request, *args, **kwargs):
        response = super(PostDetialView, self).get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    def get_object(self, queryset=None):
        post = super(PostDetialView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=['markdown.extensions.extra',
                                           'markdown.extensions.codehilite',
                                           'markdown.extensions.toc',
                                           ])
        # TocExtension(slugify=slugify)

        post.body = md.convert(post.body)
        # 给post添加toc属性
        post.toc = md.toc

        return post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetialView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all().order_by('-created_time')
        context.update({
            'form': form,
            'comment_list': comment_list,
        })

        return context


@limiter(key='', times=30, rate=60)
def search(request):
    find = request.GET.get('find')
    error_msg = ''

    #def get_visit_num_data(self, *args):
    #    if request.META.get('visit_num'):
    #        print('ok')
    #    else:
    #        print('false')
    

    if not find:
        error_msg = '请输入关键字'
        return render(request, 'blog/index.html', {'error_msg': error_msg})

    post_list = Post.objects.filter(Q(title__icontains=find) | Q(body__icontains=find))
    return render(request, 'blog/index.html', {'error_msg': error_msg, 'content': post_list})


# 发邮件
@limiter(key='', times=30, rate=60)
def mail_me(request):
    contact_name = request.POST['name']
    contact_email = request.POST['email']
    contact_subject = request.POST['subject']
    contact_message = request.POST['message']
    content = {
        "姓名": contact_name,
        "邮箱": contact_email,
        "内容": contact_message
    }
    global MAIL_NUM
    if MAIL_NUM > 10:
        return HttpResponse('<script>alert("今日邮件次数已用完,请明天再发"); location.href="/blog/index/"</script>')
    else:
        try:
            send_mail(contact_subject, content, settings.EMAIL_HOST_USER, [settings.EMAIL_BACK], fail_silently=False)
            MAIL_NUM += 1
            return HttpResponse('<script>alert("发送成功"); location.href="/blog/index/"</script>')
        except Exception as e:
            print(e)
            return HttpResponse('<script>alert("发送失败"); location.href="/blog/contact/"</script>')


@limiter(key='', times=30, rate=60)
def search_ip(request):
    data = request.POST.get('data')
    #print('data', data)
    search = 'https://apikey.net/?ip={}'.format(data)
    header = {
        "accept": "*/*",
        "accept-language": "ZH-cn,zh;q=0.9,en;q=0.8",
        "host": "apikey.net",
        "referer": "https://www.apikey.net/",
        "user-agent": "mozilla/5.0 (windoWS NT 10.0; Win64; x64) apPleWebKit/537.36 (KHTMl, liKe geckO) chrome/70.0.3538.110 safari/537.36",
    }
    res = requests.get(search, headers=header, verify=False)
    code = res.status_code
    #print(code)
    if code == 200:
        text = res.text
        #print(text)
        html = pq(text)
        return HttpResponse("{}".format(html.text()))
    else:
        return HttpResponse("查询失败:", code)


# 代理
@limiter(key='', times=30, rate=60)
def proxy_pool(request):
    conn = redis.Redis(connection_pool=settings.POOL)
    proxy_result = conn.zrangebyscore('proxies', 100, 100)
    if len(proxy_result):
        return HttpResponse(choice(proxy_result))
    else:
        proxy_result = conn.zrangebyscore('proxies', 90, 100)
        if len(proxy_result):
            return choice(proxy_result)
        else:
            raise PoolEmptyError


class PoolEmptyError(Exception):

    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return repr('代理池已经枯竭')

# 文本对比工具
def compare(request):
    return render(request, 'blog/compare.html')




# 首页 以下弃用
def index(request):
    post_queryset = Post.objects.all().order_by('-created_time')
    content = {'content': post_queryset}
    return render(request, 'blog/index.html', content)


def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-created_time')
    return render(request, 'blog/index.html', context={'content': post_list})


def archives(request, year, month):
    # print(year, month, type(year), type(month))
    post_list = Post.objects.filter(created_time__year=year, created_time__month=month).order_by('-created_time')
    archives_num = post_list.count()
    # print(archives_num)
    content = {'content': post_list, 'archives_num': archives_num}
    return render(request, 'blog/index.html', content)


# 文章详情
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.increase_views()
    post.body = markdown.markdown(post.body, extensions=['markdown.extensions.extra', 'markdown.extensions.codehilite',
                                                         'markdown.extensions.toc'])
    form = CommentForm()
    comment_list = post.comment_set.all()
    #print('post', post)
    content = {'post': post, 'form': form, 'comment_list': comment_list}
    return render(request, 'blog/detail.html', content)

def contact(request):
    return render(request, 'blog/contact.html')
