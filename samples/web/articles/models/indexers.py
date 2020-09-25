from articles import models
from djsearch.indexers import ModelDocument, dsl


class ArticleIndexer(ModelDocument):
    subject = dsl.Text()
    content = dsl.Text()

    class Index:
        model = models.Article
