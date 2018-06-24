# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implements
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class AddonsGet(Service):

    def __init__(self, context, request):
        super(AddonsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@addons as parameters
        self.params.append(name)
        return self

    def reply(self):
        control_panel = getMultiAdapter((self.context, self.request),
                                        name='prefs_install_products_form')
        all_addons = control_panel.get_addons()

        if self.params:
            return self.serializeAddon(all_addons[self.params[0]])

        result = {
            'items': {
                '@id': '{}/@addons'.format(self.context.absolute_url()),
            },
        }
        addons_data = []
        for addon in all_addons.itervalues():
            addons_data.append(self.serializeAddon(addon))
        result['items'] = addons_data
        return result

    def serializeAddon(self, addon):
        return {'@id': '{}/@addons/{}'.format(
                    self.context.absolute_url(), addon['id']),
                'id': addon['id'],
                'title': addon['title'],
                'description': addon['description'],
                'install_profile_id': addon['install_profile_id'],
                'is_installed': addon['is_installed'],
                'profile_type': addon['profile_type'],
                'uninstall_profile_id': addon['uninstall_profile_id'],
                'version': addon['version'],
                'upgrade_info': addon['upgrade_info']
                }
