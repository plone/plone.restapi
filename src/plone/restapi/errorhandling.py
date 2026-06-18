from plone.rest.errors import ErrorHandling as BaseErrorHandling
from plone.restapi.problem_types import INTERNAL_ERROR
from plone.restapi.problem_types import STATUS_MAP
from plone.restapi.problem_types import get_backwards_compat
from plone.restapi.problem_types import translate_message

import logging
import sys
import traceback

logger = logging.getLogger("plone.restapi")


class ErrorHandling(BaseErrorHandling):
    """Extended error handling for plone.restapi.

    - Logs exceptions to stderr with full traceback
    - Extends plone.rest error format with RFC 7807 fields
    - Optionally maintains backwards compatibility
    """

    def __call__(self):
        exception = self.context
        self._log_exception(exception)
        return super().__call__()

    def _log_exception(self, exception):
        """Log exception with full traceback to stderr."""
        exc_info = sys.exc_info()
        tb = "".join(traceback.format_exception(*exc_info))
        logger.error(
            "Exception during request %s %s:\n%s",
            self.request.get("METHOD"),
            self.request.get("PATH_INFO"),
            tb,
        )

    def render_exception(self, exception):
        result = super().render_exception(exception)

        if result is None:
            return None

        if get_backwards_compat():
            legacy_result = dict(result)
            legacy_result["message"] = translate_message(
                legacy_result.get("message", ""), self.request
            )
            return legacy_result

        status = self.request.response.getStatus()
        problem_type, title = STATUS_MAP.get(
            status, (INTERNAL_ERROR, "Internal Server Error")
        )

        message = result.get("message", "")
        translated_message = translate_message(message, self.request)

        error_response = {
            "type": problem_type,
            "title": title,
            "status": status,
            "detail": translated_message,
            "instance": self.request.get("PATH_INFO", ""),
        }

        return error_response
