from django.http import HttpResponse
import re


class AdminLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # shop_urllist = ['/myadmin/login', '/myadmin/dologin', '/myadmin/logout', '/myadmin/verifycode']
        # if re.match('/myadmin/', request.path) and request.path not in shop_urllist:
        #     shop_admin = request.session.get('AdminLoginS', '')
        #     if not shop_admin:
        #         return HttpResponse('<script>alert("请登录");location.href="/myadmin/login";</script>')
        #
        # userurls = ['/user/createorder/', '/user/confimorder/', '/user/displayorder/', '/user/payonline',
        #             '/user/personal']
        # if request.path in userurls:
        #     user_vip = request.session.get('VipUser', '')
        #     # 检测是否登录
        #     if not user_vip:
        #         # 如果在session没有记录,则证明没有登录,跳转到登录页面
        #         return HttpResponse('<script>alert("请先登录");location.href="/user/login/";</script>')

        # blog_url_list = ['blog/index/', 'blog/detail', 'blog/archives', 'blog/category', 'blog/tag/', 'blog/contact/',
        #                  'blog/mail/', 'blog/search/', ]
        # blog_url_list = ['comment/post', 'news/comment']

        if re.search(r'/comment/', request.path):
            blog_vip = request.session.get('username', '')
            if not blog_vip:
                return HttpResponse('<script>alert("请登录后评论");location.href="/blog/login";</script>')

        # print(request.path)
        response = self.get_response(request)
        return response
