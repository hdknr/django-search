# coding: utf-8
from __future__ import unicode_literals
from django.db.models.signals import post_save, post_delete
import elasticsearch_dsl as dsl
from elasticsearch_dsl.document import DocTypeMeta
from .utils import to_natural_key_string
from .settings import ELASTICSEARCH


class ModelDocTypeMeta(DocTypeMeta):
    def __new__(cls, name, bases, attrs):
        if 'Meta' in attrs and hasattr(attrs['Meta'], 'model'):
            attrs['Meta'].doc_type = to_natural_key_string(attrs['Meta'].model)
            attrs['_model'] = attrs['Meta'].model
            if not hasattr(attrs['Meta'], 'index'):
                attrs['Meta'].index = ELASTICSEARCH['index']
        ret = super(ModelDocTypeMeta, cls).__new__(cls, name, bases, attrs)
        return ret


class ModelDocType(dsl.DocType):
    __metaclass__ = ModelDocTypeMeta

    def __init__(self, **kwargs):
        instance = kwargs.pop('instance', None)
        if instance:
            params = dict(
                (i, getattr(instance, i))
                for i in self._doc_type.mapping)
            params.update(kwargs)
            kwargs = params
        super(ModelDocType, self).__init__(**kwargs)
        if instance:
            self.meta.id = instance.pk

    @classmethod
    def from_hit(cls, hit):
        return cls._model.objects.get(pk=hit.meta.id)

    @classmethod
    def on_save(cls, sender, instance, created, **kwargs):
        if isinstance(instance, cls._model):
            cls(instance=instance).save()

    @classmethod
    def on_delete(cls, sender, instance, created, **kwargs):
        if isinstance(instance, cls._model):
            cls(instance=instance).delete()

    @classmethod
    def init(cls):
        super(ModelDocType, cls).init()
        post_save.connect(cls.on_save, sender=cls._model)
        post_delete.connect(cls.on_delete, sender=cls._model)
