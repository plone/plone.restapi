# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView


class InternalServerErrorView(BrowserView):

    def __call__(self):  # pragma: no cover
        from urllib2 import HTTPError
        raise HTTPError(
            'http://nohost/plone/internal_server_error',
            500,
            'InternalServerError',
            {},
            None
        )
        raise HTTPError
