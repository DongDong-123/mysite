#!/usr/bin/env python
# coding=utf-8


from django_hosts import patterns, host
from django.conf import settings


from news import viewsnews
from blog import views

host_patterns = patterns('',
    host(r'news', 'news.urlsnews', name='news'),                    
    host(r'blog', 'blog.urls', name='blog'),                    
)
