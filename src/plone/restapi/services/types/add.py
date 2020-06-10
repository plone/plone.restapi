# -*- coding: utf-8 -*-
import plone.protect.interfaces
from zope.schema.interfaces import IVocabularyFactory
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import noLongerProvides
from zope.interface import implementer
from zope.interface import alsoProvides
from zope.component import queryMultiAdapter, queryUtility
from zExceptions import BadRequest
from plone.restapi.services import Service
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.deserializer import json_body
from plone.i18n.normalizer import idnormalizer


@implementer(IPublishTraverse)
class TypesPost(Service):
    """ Creates a new field/fieldset
    """
    def __init__(self, context, request):
        super(TypesPost, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        if not self.params:
            raise BadRequest("Missing parameter typename")

        data = json_body(self.request)

        title = data.get("title", None)
        if not title:
            raise BadRequest("Property 'title' is required")

        tid = data.get("id", None)
        if not tid:
            tid = idnormalizer.normalize(title).replace("-", "_")

        description = data.get("description", "")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request,
                plone.protect.interfaces.IDisableCSRFProtection
            )

        # Make sure we get the right dexterity-types adapter
        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        name = self.params.pop()
        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )
        context = context.publishTraverse(self.request, name)

        factory = data.get('@type', '')
        if not factory:
            raise BadRequest("Property '@type' is required")

        # Adding new fieldset
        if factory == "fieldset":
            add = queryMultiAdapter((context, self.request),
                                    name="add-fieldset")
            properties = {
                "label": title,
                "__name__": tid,
                "description": description
            }
        # Adding new field
        else:
            klass = None
            vocabulary = queryUtility(IVocabularyFactory, name='Fields')
            for term in vocabulary(context):
                if factory in (term.title, term.token):
                    klass = term.value

            if not klass:
                raise BadRequest("Invalid '@type' %s" % factory)

            self.request.form["fieldset_id"] = data.get("fieldset_id", 0)
            add = queryMultiAdapter((context, self.request),
                                    name="add-field")
            properties = {
                "title": title,
                "__name__": tid,
                "description": description,
                "factory": klass,
                "required": data.get("required", False)
            }

        field = add.form_instance.create(data=properties)
        add.form_instance.add(field)

        # TODO Return added field/fieldset
        return self.reply_no_content()
