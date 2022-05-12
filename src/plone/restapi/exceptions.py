class APIError(Exception):
    """Base class for exceptions raised by plone.restapi."""


class DeserializationError(Exception):
    """An error happened during deserialization of content."""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class QueryParsingError(Exception):
    """An error happened while parsing a search query."""
