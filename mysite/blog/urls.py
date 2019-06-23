from . import views
from django.urls import path


app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path(r'blog_detail/<pk>/', views.PostDetialView.as_view(), name='detail'),
    path(r'blog_archives/<year>/<month>/', views.ArchivesView.as_view(), name='archives'),
    path(r'blog_category/<pk>/', views.CategoryView.as_view(), name='category'),
    path(r'blog_tag/<pk>/', views.TagsView.as_view(), name='tag'),
    path(r'blog_contact/', views.contact, name='contact'),
    path(r'blog_mail/', views.mail_me, name='mail_me'),
    path(r'blog_search/', views.search, name='search'),
    path(r'blog_query_ip/', views.search_ip, name='search_ip'),
    path(r'proxy', views.proxy_pool, name='proxy'),
    path(r'compare', views.compare, name='compare'),
]
