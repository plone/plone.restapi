from plone.restapi import form_token
from plone.restapi.services import Service


class FormTokenGet(Service):
    """A token for one submission of a form, see plone.restapi.form_token."""

    def reply(self):
        # Each visitor needs a token of their own: caches must not share it.
        self.request.response.setHeader("Cache-Control", "no-store, private")
        token = form_token.issue_token() if form_token.is_enabled() else None
        if token is None:
            self.request.response.setStatus(503)
            return {
                "error": {
                    "type": "ServiceUnavailable",
                    "message": "Form tokens are not available.",
                }
            }
        return {"token": token, "min_age": form_token.get_min_age()}
