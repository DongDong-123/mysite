from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include


urlpatterns = [
    path('admins/', admin.site.urls),
    path('', include('blog.urls')),
    path('', include('polls.urls')),
    path('', include('shop.urlshome')),
    path('', include('news.urlsnews')),
    path('', include('myadmin.urls')),
    path('', include('comments.urls')),
    path('', include('wxkf.urls')),
    path('', include('usersystem.urls')),
    path('', include('Empire.urls')),
    url(r'^ueditor/', include('ueditor.urls')),

]
