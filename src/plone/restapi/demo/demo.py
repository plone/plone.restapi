from Products.Five.browser import BrowserView  # pragma: no cover


class InternalServerErrorView(BrowserView):  # pragma: no cover
    def __call__(self):
        from urllib.error import HTTPError

        raise HTTPError(
            "http://nohost/plone/internal_server_error",
            500,
            "InternalServerError",
            {},
            None,
        )
