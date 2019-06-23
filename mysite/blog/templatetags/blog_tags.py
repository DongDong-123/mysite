from django import template
from ..models import Post, Category, Tag
from django.db.models.aggregates import Count


register = template.Library()


# 最新文章
@register.simple_tag
def get_recent_posts(num=5):
    return Post.objects.all().order_by('-created_time')[:num]


# 归档
@register.simple_tag
def archives():

    result = Post.objects.dates('created_time', 'month', order='DESC')
    # print(result)
    return result


# 分类
@register.simple_tag
def get_categories():
    # return Category.objects.all()
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)


@register.simple_tag
def get_tag():
    return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)

