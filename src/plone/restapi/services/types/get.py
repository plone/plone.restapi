from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.services import Service
from plone.restapi.types.utils import get_info_for_type
from plone.restapi.types.utils import get_info_for_field
from plone.restapi.types.utils import get_info_for_fieldset
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import noLongerProvides
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory


def check_security(context):
    # Only expose type information to authenticated users
    portal_membership = getToolByName(context, "portal_membership")
    if portal_membership.isAnonymousUser():
        raise Unauthorized


@implementer(IExpandableElement)
@adapter(IDexterityContent, Interface)
class TypesInfo:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"types": {"@id": f"{self.context.absolute_url()}/@types"}}
        if not expand:
            return result

        check_security(self.context)

        vocab_factory = getUtility(
            IVocabularyFactory, name="plone.app.vocabularies.ReallyUserFriendlyTypes"
        )

        portal_types = getToolByName(self.context, "portal_types")

        # allowedContentTypes already checks for permissions
        allowed_types = [x.getId() for x in self.context.allowedContentTypes()]

        portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        portal_url = portal.absolute_url()

        # only addables if the content type is folderish
        can_add = IFolderish.providedBy(self.context)

        # Filter out any type that doesn't have lookupSchema. We are depended
        # on that in lower level code.
        ftis = [portal_types[x.value] for x in vocab_factory(self.context)]
        ftis = [fti for fti in ftis if getattr(fti, "lookupSchema", None)]

        result["types"] = [
            {
                "@id": f"{portal_url}/@types/{fti.getId()}",
                "title": translate(fti.Title(), context=self.request),
                "addable": fti.getId() in allowed_types if can_add else False,
            }
            for fti in ftis
        ]

        return result


@implementer(IPublishTraverse)
class TypesGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    @property
    def _get_record_name(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (dotted name of"
                "the record to be retrieved)"
            )

        return self.params[0]

    def reply(self):
        if not self.params:
            # List type info, including addable_types
            info = TypesInfo(self.context, self.request)
            return info(expand=True)["types"]

        if len(self.params) == 1:
            return self.reply_for_type()

        if len(self.params) == 2:
            return self.reply_for_field()

    def reply_for_type(self):
        check_security(self.context)
        portal_type = self.params.pop()

        # Make sure we get the right dexterity-types adapter
        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        try:
            dtool = queryMultiAdapter(
                (self.context, self.request), name="dexterity-types"
            )
            dtype = dtool.publishTraverse(self.request, portal_type)
        except Exception:
            dtype = self.context

        try:
            schema = get_info_for_type(dtype, self.request, portal_type)
        except KeyError:
            self.content_type = "application/json"
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": "Type '%s' could not be found." % portal_type,
            }

        self.content_type = "application/json+schema"
        return schema

    def reply_for_field(self):
        check_security(self.context)
        name = self.params[0]
        field_name = self.params[1]

        # Make sure we get the right dexterity-types adapter
        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )
        context = context.publishTraverse(self.request, name)

        try:
            # Get field
            return get_info_for_field(context, self.request, field_name)
        except (KeyError, AttributeError):
            # Get fieldset
            return self.reply_for_fieldset()

    def reply_for_fieldset(self):
        name = self.params[0]
        field_name = self.params[1]

        # Make sure we get the right dexterity-types adapter
        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )
        context = context.publishTraverse(self.request, name)

        try:
            return get_info_for_fieldset(context, self.request, field_name)
        except KeyError:
            self.content_type = "application/json"
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": "Field(set) '%s' could not be found." % field_name,
            }
