from django.conf import settings

DJSEARCH = getattr(settings, 'DJSEARCH', {})

ELASTICSEARCH = {
    'hosts': ['localhost'],
    'port': 9200,
    'index': 'django',
}
ELASTICSEARCH.update(DJSEARCH.get('elasticsearch', {}))
