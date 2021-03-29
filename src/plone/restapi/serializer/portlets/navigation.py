from . import PortletSerializer
from Acquisition import aq_base
from plone import api
from plone.app.portlets.portlets.navigation import Renderer
from plone.registry.interfaces import IRegistry
from Products.CMFPlone import utils
from zope.component import getUtility


class NavigationPortletSerializer(PortletSerializer):
    """ Portlet serializer for navigation portlet
    """

    def __call__(self):
        res = super(NavigationPortletSerializer, self).__call__()
        renderer = NavtreePortletRenderer(
            self.context,
            self.request,
            None,
            None,
            self.assignment
        )

        res['navigationportlet'] = renderer.render()

        return res


def get_url(item):
    if not item:
        return None

    if hasattr(aq_base(item), 'getURL'):
        # Looks like a brain

        return item.getURL()

    return item.absolute_url()


def get_id(item):
    if not item:
        return None
    getId = getattr(item, 'getId')

    if not utils.safe_callable(getId):
        # Looks like a brain

        return getId

    return getId()


def get_view_url(context):
    registry = getUtility(IRegistry)
    view_action_types = registry.get(
        'plone.types_use_view_action_in_listings', [])
    item_url = get_url(context)
    name = get_id(context)

    if getattr(context, 'portal_type', {}) in view_action_types:
        item_url += '/view'
        name += '/view'

    return name, item_url


class NavtreePortletRenderer(Renderer):
    def render(self):
        res = {
            'title': self.title(),
            'url': self.heading_link_target(),
            'has_custom_name': bool(self.hasName()),
            'items': [],
        }

        if self.include_top():
            root = self.navigation_root()
            root_is_portal = self.root_is_portal()

            if root is None:
                root = self.urltool.getPortalObject()
                root_is_portal = True

            if utils.safe_hasattr(self.context, 'getRemoteUrl'):
                root_url = root.getRemoteUrl()
            else:
                cid, root_url = get_view_url(root)

            root_title = ('Home'
                          if root_is_portal else root.pretty_title_or_id())
            root_type = ('plone-site'
                         if root_is_portal else utils.normalizeString(
                             root.portal_type, context=root))
            normalized_id = utils.normalizeString(root.Title(), context=root)

            if root_is_portal:
                state = ''
            else:
                state = api.content.get_state(root)

            res['items'].append({
                '@id': root.absolute_url(),
                'description': root.Description() or '',
                'href': root_url,
                'icon': '',
                'is_current': bool(self.root_item_class()),
                'is_folderish': True,
                'is_in_path': True,
                'items': [],
                'normalized_id': normalized_id,
                'thumb': '',
                'title': root_title,
                'type': root_type,
                'review_state': state,
            })

        res['items'].extend(self.createNavTree())

        return res

    def recurse(self, children, level, bottomLevel):
        # TODO: we should avoid recursion. This is just a rewrite of the TAL
        # template, but ideally we should use a dequeue structure to avoid
        # recursion problems.

        res = []

        show_thumbs = not self.data.no_thumbs
        show_icons = not self.data.no_icons

        thumb_scale = self.thumb_scale()

        for node in children:
            brain = node['item']

            icon = ''

            if show_icons:
                if (node['portal_type'] == 'File'):
                    icon = self.getMimeTypeIcon(node)

            has_thumb = brain.getIcon
            thumb = ''

            if show_thumbs and has_thumb and thumb_scale:
                thumb = '{}/@@images/image/{}'.format(
                        node['item'].getURL(), thumb_scale)

            show_children = node['show_children']
            item_remote_url = node['getRemoteUrl']
            use_remote_url = node['useRemoteUrl']
            item_url = node['getURL']
            item = {
                '@id': item_url,
                'description': node['Description'],
                'href': item_remote_url if use_remote_url else item_url,
                'icon': icon,
                'is_current': node['currentItem'],
                'is_folderish': node['show_children'],
                'is_in_path': node['currentParent'],
                'items': [],
                'normalized_id': node['normalized_id'],
                'review_state': node['review_state'] or '',
                'thumb': thumb,
                'title': node['Title'],
                'type': node['normalized_portal_type'],
            }

            nodechildren = node['children']

            if nodechildren and show_children and \
                    ((bottomLevel < level) or (bottomLevel == 0)):
                item['items'] = self.recurse(
                    nodechildren, level=level + 1, bottomLevel=bottomLevel)

            res.append(item)

        return res
