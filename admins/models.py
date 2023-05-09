from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=200, null=True)
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class News(models.Model):
    heading = models.CharField(max_length=200, null=True, default='News Titles')
    image = models.ImageField(upload_to='news', default='news.png', null=True, blank=True)

    def __str__(self):
        return self.heading
    

class Banner(models.Model):
    heading = models.CharField(max_length=200, null=True, default='Banner Titles')
    image = models.ImageField(upload_to='banner', default='main-img.jpg', null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']