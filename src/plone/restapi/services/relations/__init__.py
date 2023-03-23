try:
    from plone.api.relation import create as api_relation_create
    from plone.api.relation import delete as api_relation_delete
except ImportError:
    api_relation_create = None
    api_relation_delete = None
