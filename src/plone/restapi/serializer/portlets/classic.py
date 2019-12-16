from . import PortletSerializer
from Acquisition import aq_base
from plone import api
from plone.app.portlets.portlets.classic import Renderer
from plone.registry.interfaces import IRegistry
from Products.CMFPlone import utils
from zope.component import getUtility


class ClassicPortletSerializer(PortletSerializer):
    """ Portlet serializer for navigation portlet
    """

    def __call__(self):
        res = super(ClassicPortletSerializer, self).__call__()
        renderer = Renderer(
            self.context,
            self.request,
            None,
            None,
            self.assignment
        )

        res['classicportlet'] = renderer.render()

        return res
