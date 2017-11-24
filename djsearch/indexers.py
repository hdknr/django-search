from django.db.models.signals import post_save, post_delete
import elasticsearch_dsl as dsl
from elasticsearch_dsl.document import DocTypeMeta
from elasticsearch_dsl.connections import connections

from .utils import to_natural_key_string
from .settings import ELASTICSEARCH


es = connections.create_connection(**ELASTICSEARCH)


class ModelDocTypeMeta(DocTypeMeta):

    def __new__(cls, name, bases, attrs):
        if 'Meta' in attrs and hasattr(attrs['Meta'], 'model'):
            attrs['Meta'].doc_type = to_natural_key_string(attrs['Meta'].model)
            attrs['_model'] = attrs['Meta'].model
            if not hasattr(attrs['Meta'], 'index'):
                attrs['Meta'].index = ELASTICSEARCH['index']
        ret = super(ModelDocTypeMeta, cls).__new__(cls, name, bases, attrs)
        return ret


class ModelDocType(dsl.DocType, metaclass=ModelDocTypeMeta):

    def __init__(self, instance, meta=None, **kwargs):
        kwargs = self.map_instance(instance) or kwargs
        meta = meta or {'id': instance.id}
        super(ModelDocType, self).__init__(meta=meta, **kwargs)

    def map_data(self, instance):
        return {}

    def map_instance(self, instance, kwargs={}):
        data = self.map_data(instance)
        params = dict(
            [(i, data.get(i, getattr(instance, i, None)))
             for i in self._doc_type.mapping],
            **kwargs)
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
        super(ModelDocType, cls).init()
        if hasattr(cls, '_model'):
            post_save.connect(cls.on_save, sender=cls._model)
            post_delete.connect(cls.on_delete, sender=cls._model)
