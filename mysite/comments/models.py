from django.db import models



class Comment(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=250)
    url = models.URLField(blank=True)
    text = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='static/public/comment_img', blank=True)

    def __str__(self):
        return self.text[:20]


