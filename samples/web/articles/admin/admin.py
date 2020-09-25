from django.contrib import admin
from .. import models


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "subject"]
    search_fields = ["subject", "content"]
