# TEMPORARY patch for low form memory limit introduced in Zope 5.8.4.
# See https://github.com/plone/Products.CMFPlone/issues/3848
# and https://github.com/zopefoundation/Zope/pull/1180
# Should be removed once `plone.restapi.deserializer.json_body` no longer
# reads the complete request BODY in memory.
from ZPublisher.HTTPRequest import ZopeFieldStorage

import logging


logger = logging.getLogger(__name__)
_attr = "VALUE_LIMIT"
_limit = getattr(ZopeFieldStorage, _attr, None)
if _limit:
    setattr(ZopeFieldStorage, _attr, None)
    logger.info(
        "PATCH: Disabled ZPublisher.HTTPRequest.ZopeFieldStorage.%s. "
        "This enables file uploads larger than 1MB.",
        _attr,
    )
