from django.urls import path
from django.conf.urls import url, include
from . import views

app_name = 'usersystem'
urlpatterns = [

    path(r'blog_login/', views.Login.as_view(), name='login'),
    path(r'blog_dologin/', views.dologin, name='dologin'),
    path(r'blog_logout/', views.logout, name='logout'),

    path(r'blog_account/', views.Create_Account.as_view(), name='create_account'),
    path(r'blog_docreate/', views.docreate, name='docreate'),

    path(r'blog_forgotpwd/', views.ForgotPWD.as_view(), name='forgotpwd'),
    path(r'resetpwd/', views.resetpwd, name='resetpwd'),
    path(r'blog_changepwd/', views.ChangePWD.as_view(), name='changepwd'),
    path(r'blog_test/', views.test, name='test'),
    path(r'blog_vcode/', views.verifycode, name='vcode'),
    path(r'blog_limit/', views.myview, name='limit'),

]
