from django.db import models


class Article(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()
