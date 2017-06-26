# -*- coding: utf-8 -*-
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.interface import alsoProvides
from zope.component import queryMultiAdapter
from zope.security import checkPermission

import plone.protect.interfaces


class SharingGet(Service):
    """Returns a serialized content object.
    """

    def reply(self):
        # return 403 Forbidden if the user has no DelegateRoles permission
        if not checkPermission('plone.DelegateRoles', self.context):
            self.request.response.setStatus(403)
            return
        serializer = queryMultiAdapter((self.context, self.request),
                                       interface=ISerializeToJson,
                                       name='local_roles')
        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message='No serializer available.'))

        return serializer(search=self.request.form.get('search'))


class SharingPost(Service):
    def reply(self):
        # return 403 Forbidden if the user has no DelegateRoles permission
        if not checkPermission('plone.DelegateRoles', self.context):
            self.request.response.setStatus(403)
            return

        deserializer = queryMultiAdapter((self.context, self.request),
                                         interface=IDeserializeFromJson,
                                         name='local_roles')
        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        if deserializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(
                message='Cannot deserialize local roles for type {}'.format(
                    self.context.portal_type)))

        try:
            deserializer()
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='DeserializationError',
                message=str(e)))

        # TODO: alternativley return the patched object with a 200
        self.request.response.setStatus(204)
        return
