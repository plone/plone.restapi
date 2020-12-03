# -*- coding: utf-8 -*-

from Products.CMFQuickInstallerTool.QuickInstallerTool import QuickInstallerTool

_original_QuickInstallerTool_install_profile_info = (
    QuickInstallerTool._install_profile_info
)


def _install_profile_info(self, productname):
    install_profile_info = _original_QuickInstallerTool_install_profile_info(
        self, productname
    )
    if productname == "plone.restapi" and install_profile_info:
        default_profile = u"plone.restapi:default"
        first_profile = install_profile_info[0]["id"]
        if default_profile != first_profile:
            install_profile_info[0], install_profile_info[1] = (
                install_profile_info[1],
                install_profile_info[0],
            )
    return install_profile_info


def apply_patch():
    # BBB: In Plone 4, the profile that runs when installing a product is the first in
    # the list of profiles, ordered alphabetically. Since plone.restapi has profile
    # blocks, it comes before the default and that is why it is what is listed for
    # installing of plone.restapi. This patch changes the order, of the profiles blocks
    # and default, so that the default is the installed profile.
    QuickInstallerTool._install_profile_info = _install_profile_info
