from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Userinfo
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.views.generic import TemplateView
import logging
from django.core.mail import send_mail
import random
import redis
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import random
# 反爬
from apilimiter.decorators import limiter
from apilimiter.mixin import LimiterMixin


class Login(LimiterMixin, TemplateView):
    key = 'user.id'
    times = 10
    redirect = ''
    rate = 60
    template_name = 'blog/login.html'


# 测试
@limiter(key='', times=5, rate=60)
def myview(request):

    return HttpResponse('error')


# 登录
@limiter(key='', times=10, rate=60)
def dologin(request):
    save_info = Userinfo.objects.all().filter(username=request.POST.get('username'))

    if save_info:
        user = save_info[0]
        passwd = request.POST.get('passwd')
        remeber = request.POST.get('remeber')
        # print(remeber)
        if check_password(passwd, user.passwd):
            request.session['userinfo'] = {'name': user.username, 'id': user.id}
            print(request.session['userinfo'])
            return HttpResponse('<script>alert("登录成功"),location.href="/"</script>')

    else:
        return HttpResponse('<script>alert("验证失败,请重试！"),location.href="/blog_login"</script>')


# 退出
def logout(request):
    request.session['userinfo'] = None
    
    return HttpResponse('<script>alert("退出成功"),location.href="/"</script>')


# 注册
class Create_Account(TemplateView):
    template_name = 'blog/create-account.html'


# 执行注册
@limiter(key='', times=10, rate=60)
def docreate(request):
    verify_code = request.POST.get('code')
    username = request.POST.get('username')
    conn = redis.StrictRedis(connection_pool=settings.POOL)
    save_code = conn.get(username).decode('utf-8')
    print('save_code',save_code,'verify_code=',verify_code)
    print('username',username)
    if save_code == verify_code:
        print('验证码一致')
        Userinfo.objects.create(
            username=username,
            email=request.POST.get('email'),
            gender=request.POST.get('optionsRadios'),
            passwd=make_password(request.POST.get('pwd2'), None, 'pbkdf2_sha256')
        )
        return HttpResponse('<script>alert("注册成功"),location.href="/blog_login"</script>')
    else:
        return HttpResponse('<script>alert("验证码错误"),location.href="/blog_account"</script>')


# 忘记密码
class ForgotPWD(TemplateView):
    template_name = 'blog/forgot-password.html'


# 密码重置，邮箱验证
@limiter(key='', times=10, rate=60)
def resetpwd(request):
    email = request.POST.get('email')
    name = request.POST.get('name')
    # 增加type数据，发送请求的对象进行分辨，响应相应的数据；数据范围0和1。
    check_type = request.POST.get('type')
    #print(email)
    #print(check_type, type(check_type))
    # 0 为注册账户发送请求，已在前端对邮箱进行验证，不在重复验证，直接设为True
    if check_type == '0':
        subject = '用户注册'
        check_email = True
        username = name
    # 1为密码重置发送的请求
    else:
        subject = '密码重置'
        # 邮箱也在前端使用ajax验证过，为了获取用户名，此时重新进行查询
        check_email = get_object_or_404(Userinfo, email=email)
        username = check_email.username

    if check_email:
        code = random.randint(100000, 999999)
        print('makecode=',code)
        try:  # 验证码存入redis，有效期10分钟，
            conn = redis.StrictRedis(connection_pool=settings.POOL)
            conn.setex(username, 600, code)
            # 调用邮箱模块，发送邮件，参数，1：主题；2：内容；3：收件人；发件人在setting内配置，4：是否抛出异常，false为抛出，
            send_mail(subject, '亲爱的{}用户您好，您的验证码为：{}，有效期10分钟。'.format(username, code), settings.EMAIL_HOST_USER, [email],
                      fail_silently=False)
        except ConnectionError as e:
            print(e)
        # send_mass_mail  # 多封邮件
        result = '1'
        return HttpResponse(result)
    else:
        result = '0'
        return HttpResponse(result)


# ajax验证复用
@limiter(key='', times=60, rate=60)
def test(request):
    email = request.POST.get('email')  # 接收ajax数据
    username = request.POST.get('username')  # 接收ajax数据
    print('email', email)
    print('username', username)
    if email:
        # 数据库查询邮箱是否存在
        check_email = Userinfo.objects.filter(email=email)
        if check_email:  # 存在，返回1
            result = '1'
            return HttpResponse(result)
        else:  # 不存在，返回0
            print('no')
            result = '0'
            return HttpResponse(result)
    elif username:
        check_email = Userinfo.objects.filter(username=username)
        if check_email:  # 存在，返回1
            result = '1'
            return HttpResponse(result)
        else:  # 不存在，返回0
            print('no')
            result = '0'
            return HttpResponse(result)


# 生成验证码
@limiter(key='', times=20, rate=60)
def verifycode(request):
    bgcolor = (random.randrange(20, 300), random.randrange(20, 300), 255)
    width = 100
    height = 30
    im = Image.new('RGB', (width, height), bgcolor)
    draw = ImageDraw.Draw(im)

    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # str1 = '你好啊我是管理员想登陆吗需要验证啊输入验证码吧哈'
    str1 = '123456789'
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]

    #font = ImageFont.truetype('back/fonts/BRADHITC.TTF', 23)  # win
    font = ImageFont.truetype('blog/fonts/NotoSansCJK-Regular.ttc', 23)  # linux

    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    del draw
    request.session['verifycode'] = rand_str
    import io
    buf = io.BytesIO()
    im.save(buf, 'png')
    # print('code', buf.getbuffer())
    return HttpResponse(buf.getvalue(), 'image/png')


# 修改密码
class ChangePWD(TemplateView):
    template_name = 'blog/changepwd.html'
