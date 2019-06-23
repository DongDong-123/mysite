from django.db import models

# Create your models here.

class Userinfo(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField()
    passwd = models.CharField(max_length=255)
    gender = models.IntegerField()
    createtime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username



