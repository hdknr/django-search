from django.db.models.signals import post_save, post_delete
import elasticsearch_dsl as dsl
from elasticsearch_dsl.document import IndexMeta

from .utils import to_natural_key_string
from .settings import djsearch_settings as settings
import traceback


class ModelDocumentMeta(IndexMeta):
    def __new__(cls, name, bases, attrs):
        if "Index" in attrs:
            attrs["_connection"] = getattr(
                attrs["Index"], "connection", settings.CONNECTION
            )
            attrs["_model"] = getattr(attrs["Index"], "model", None)
            attrs["Index"].name = to_natural_key_string(attrs["_model"])

        ret = super().__new__(cls, name, bases, attrs)
        return ret


class ModelDocument(dsl.Document, metaclass=ModelDocumentMeta):
    def __init__(self, instance=None, meta=None, **kwargs):
        if instance and instance.id:
            kwargs = self.map_instance(instance) or kwargs
            meta = meta or {"id": instance.id}
        print("????", instance, meta, kwargs)
        super().__init__(meta=meta, **kwargs)

    def map_data(self, instance):
        return {}

    def map_instance(self, instance, kwargs={}):
        data = self.map_data(instance)
        params = dict(
            [
                (i, data.get(i, getattr(instance, i, None)))
                for i in self._doc_type.mapping
            ],
            **kwargs
        )
        return params

    @classmethod
    def from_hit(cls, hit):
        return cls._model.objects.get(pk=hit.meta.id)

    @classmethod
    def on_save(cls, sender, instance, created, **kwargs):
        if isinstance(instance, cls._model):
            try:
                cls(instance=instance, **kwargs).save()
            except KeyError:
                pass

    @classmethod
    def on_delete(cls, sender, instance, **kwargs):
        if isinstance(instance, cls._model):
            try:
                cls(instance=instance, **kwargs).delete()
            except:
                pass

    @classmethod
    def init(cls):
        super().init()
        if hasattr(cls, "_model"):
            post_save.connect(cls.on_save, sender=cls._model)
            post_delete.connect(cls.on_delete, sender=cls._model)


html_strip = dsl.analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)