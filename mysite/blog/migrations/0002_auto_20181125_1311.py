# Generated by Django 2.0.7 on 2018-11-25 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='comment_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='read_num',
            field=models.IntegerField(default=0),
        ),
    ]