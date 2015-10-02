# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.restapi.interfaces import IContext

from zope.site.hooks import getSite
from zope.schema import Datetime
from zope.interface import implementer
from zope.component import adapter
from zope.component import getUtility


def get_context(portal):
    return [
        'http://www.w3.org/ns/hydra/context.jsonld',
        {
            '@vocab': '{0}/@@contexts#'.format(
                portal.absolute_url())
        }
    ]


@implementer(IContext)
@adapter(IPloneSiteRoot)
def ContextSiteRoot(context):
    return get_context(context)


@implementer(IContext)
@adapter(IContentish)
def ContextContentish(context):
    portal = getSite()
    return get_context(portal)


@implementer(IContext)
@adapter(IFile)
def ContextFile(context):
    portal = getSite()
    return get_context(portal)


@implementer(IContext)
@adapter(IImage)
def ContextImage(context):
    portal = getSite()
    return get_context(portal)