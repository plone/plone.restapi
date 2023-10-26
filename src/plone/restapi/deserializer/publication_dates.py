"""Make effective and expiration dates timezone-aware.

These data managers bypass the IPublication behavior adapter,
which strips timezone information from the dates.

Falls back to the normal adapter for non-API requests,
to avoid breaking compatibility with classic widgets.
"""
from DateTime import DateTime
from plone.app.dexterity.behaviors.metadata import IPublication
from plone.rest.interfaces import IAPIRequest
from z3c.form.datamanager import AttributeField
from z3c.form.util import getSpecification
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.interface import Interface


class PublicationDateDataManager(AttributeField):
    name = None

    def __init__(self, context, field):
        super().__init__(context, field)
        self.request = getRequest()
        self.is_api_request = IAPIRequest.providedBy(self.request)

    def get(self):
        if not self.is_api_request:
            return super().get()
        value = getattr(self.context, self.name)
        if value is not None:
            return value.asdatetime()

    def set(self, value):
        if not self.is_api_request:
            return super().set(value)
        if value is not None:
            value = DateTime(value)
        setattr(self.context, self.name, value)


@adapter(Interface, getSpecification(IPublication["effective"]))
class EffectiveDateDataManager(PublicationDateDataManager):
    name = "effective_date"


@adapter(Interface, getSpecification(IPublication["expires"]))
class ExpirationDateDataManager(PublicationDateDataManager):
    name = "expiration_date"
