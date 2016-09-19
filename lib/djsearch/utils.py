# coding: utf-8
from django.contrib.contenttypes.models import ContentType


def get_contenttype(instance_or_class):
    if isinstance(instance_or_class, ContentType):
        return instance_or_class
    return ContentType.objects.get_for_model(instance_or_class)


def to_natural_key(instance_or_class):
    return get_contenttype(instance_or_class).natural_key()


def to_natural_key_string(instance_or_class):
    return ".".join(to_natural_key(instance_or_class))


def from_natual_key(app_lable, model_name, **queries):
    ct = ContentType.objects.get_by_natural_key(app_lable, model_name)
    if queries:
        return ct.get_object_for_this_type(**queries)
    return ct.model_class()


def from_natual_key_string(natural_key_string, **queries):
    return from_natual_key(*natural_key_string.split('.'), **queries)
