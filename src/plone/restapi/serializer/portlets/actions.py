from . import PortletSerializer
from plone.app.portlets.portlets.actions import Renderer


class ActionsPortletSerializer(PortletSerializer):
    """ Portlet serializer for actions portlets
    """

    def __call__(self):
        res = super(ActionsPortletSerializer, self).__call__()
        renderer = Renderer(
            self.context,
            self.request,
            None,
            None,
            self.assignment
        )

        actions = []

        for action in renderer.actionLinks():
            if action['icon']:
                action['icon'] = action['icon'].absolute_url()
            actions.append(action)

        res['actionsportlet'] = {
            'category': renderer.category,
            'items': actions
        }

        return res
