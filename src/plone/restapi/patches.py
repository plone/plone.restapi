# TEMPORARY patch for low form memory limit introduced in Zope 5.8.4.
# See https://github.com/plone/Products.CMFPlone/issues/3848
# and https://github.com/zopefoundation/Zope/pull/1180
# Should be removed once `plone.restapi.deserializer.json_body` no longer
# reads the complete request BODY in memory.
from ZPublisher import HTTPRequest

import logging


logger = logging.getLogger(__name__)
_attr = "FORM_MEMORY_LIMIT"
_limit = getattr(HTTPRequest, _attr, None)
if _limit and _limit == 2**20:
    setattr(HTTPRequest, _attr, 2**24)
    logger.info(
        "PATCH: ZPublisher.HTTPRequest.%s is at a too low default of 1MB. "
        "Increased it to 16MB to enable larger file uploads.",
        _attr,
    )
