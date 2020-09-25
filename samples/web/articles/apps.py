from django import apps


class AppConfig(apps.AppConfig):
    name = "articles"

    def ready(self):
        from articles.models import indexers

        indexers.ArticleIndexer.init()
