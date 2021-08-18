from zope.interface import Attribute
from zope.interface import Interface


class IControlpanel(Interface):
    __name__ = Attribute("Name of the controlpanel in the URL")
    title = Attribute("Title of this controlpanel")
    group = Attribute("Group name of this controlpanel")
    schema = Attribute("Registry schema of this controlpanel")

    configlet_id = Attribute("Id of the configlet, e.g. MailHost")
    configlet_category_id = Attribute(
        "Category of the configlet, e.g. plone-general"
    )  # noqa

    def add(names):
        """Create controlpanel children by names"""

    def get(names):
        """Read controlpanel children by names"""

    def update(names):
        """Update controlpanel children by names"""

    def delete(names):
        """Remove controlpanel children by names"""


class IDexterityTypesControlpanel(IControlpanel):
    """Dexterity Types Control panel"""
