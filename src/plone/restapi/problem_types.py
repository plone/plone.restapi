from zope.i18n import translate
from zope.i18nmessageid import Message

VALIDATION_ERROR = "/problem-types/validation-error"
MISSING_CREDENTIALS = "/problem-types/missing-credentials"
INVALID_CREDENTIALS = "/problem-types/invalid-credentials"
UNAUTHORIZED = "/problem-types/unauthorized"
FORBIDDEN = "/problem-types/forbidden"
RESOURCE_NOT_FOUND = "/problem-types/resource-not-found"
INTERNAL_ERROR = "/problem-types/internal-error"
QUERY_ERROR = "/problem-types/query-error"
CONFLICT = "/problem-types/conflict"

STATUS_MAP = {
    400: (VALIDATION_ERROR, "Bad Request"),
    401: (UNAUTHORIZED, "Unauthorized"),
    403: (FORBIDDEN, "Forbidden"),
    404: (RESOURCE_NOT_FOUND, "Not Found"),
    409: (CONFLICT, "Conflict"),
    500: (INTERNAL_ERROR, "Internal Server Error"),
}

BACKWARDS_COMPAT_MODE = True


def set_backwards_compat(enabled):
    """Enable or disable backwards compatible error fields.
    
    When disabled, error responses will only contain RFC 7807 fields:
    - type, title, status, detail, instance
    
    When enabled (default), error responses will also include deprecated fields:
    - message, context, error_type, traceback
    """
    global BACKWARDS_COMPAT_MODE
    BACKWARDS_COMPAT_MODE = enabled


def get_backwards_compat():
    """Return current backwards compatibility setting."""
    return BACKWARDS_COMPAT_MODE

RFC7807_ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "format": "uri",
            "description": "A URI reference that identifies the problem type.",
            "example": "/problem-types/validation-error",
        },
        "title": {
            "type": "string",
            "description": "A short, human-readable summary of the problem type.",
            "example": "Bad Request",
        },
        "status": {
            "type": "integer",
            "description": "The HTTP status code.",
            "example": 400,
        },
        "detail": {
            "type": "string",
            "description": "A human-readable explanation specific to this occurrence of the problem.",
            "example": "Login and password must be provided in body.",
        },
        "instance": {
            "type": "string",
            "format": "uri",
            "description": "The request path that caused the error.",
            "example": "/plone/@login",
        },
        "message": {
            "type": "string",
            "description": "[DEPRECATED] Human-readable error message. Same as 'detail'. Will be removed in future releases.",
            "example": "Login and password must be provided in body.",
            "deprecated": True,
        },
        "context": {
            "type": "string",
            "format": "uri",
            "description": "[DEPRECATED] URL of the closest visible context. Will be removed in future releases.",
            "example": "https://example.com/plone",
            "deprecated": True,
        },
        "error_type": {
            "type": "string",
            "description": "[DEPRECATED] Legacy field for backwards compatibility. Will be removed in future releases.",
            "example": "Missing credentials",
            "deprecated": True,
        },
        "traceback": {
            "type": "array",
            "items": {"type": "string"},
            "description": "[DEPRECATED] Stack trace for debugging. Only visible to users with ManagePortal permission. Will be removed in future releases.",
            "deprecated": True,
        },
    },
    "required": ["type", "title", "status", "detail"],
}

OPENAPI_RESPONSES = {
    400: {
        "description": "Bad Request - The request was invalid or cannot be served.",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/RFC7807Error"},
                "example": {
                    "type": "/problem-types/validation-error",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": "Login and password must be provided in body.",
                    "instance": "/plone/@login",
                },
            }
        },
    },
    401: {
        "description": "Unauthorized - Authentication is required.",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/RFC7807Error"},
                "example": {
                    "type": "/problem-types/unauthorized",
                    "title": "Unauthorized",
                    "status": 401,
                    "detail": "Authentication required.",
                    "instance": "/plone/@login",
                },
            }
        },
    },
    403: {
        "description": "Forbidden - The request was valid but access is denied.",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/RFC7807Error"},
                "example": {
                    "type": "/problem-types/forbidden",
                    "title": "Forbidden",
                    "status": 403,
                    "detail": "You do not have permission to access this resource.",
                    "instance": "/plone/document",
                },
            }
        },
    },
    404: {
        "description": "Not Found - The requested resource could not be found.",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/RFC7807Error"},
                "example": {
                    "type": "/problem-types/resource-not-found",
                    "title": "Not Found",
                    "status": 404,
                    "detail": "The requested resource could not be found.",
                    "instance": "/plone/non-existent",
                },
            }
        },
    },
    409: {
        "description": "Conflict - The request conflicts with the current state.",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/RFC7807Error"},
                "example": {
                    "type": "/problem-types/conflict",
                    "title": "Conflict",
                    "status": 409,
                    "detail": "The resource has been modified by another request.",
                    "instance": "/plone/document",
                },
            }
        },
    },
    500: {
        "description": "Internal Server Error - An unexpected error occurred.",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/RFC7807Error"},
                "example": {
                    "type": "/problem-types/internal-error",
                    "title": "Internal Server Error",
                    "status": 500,
                    "detail": "An unexpected error occurred.",
                    "instance": "/plone/@login",
                },
            }
        },
    },
}


def translate_message(msg, request):
    """Translate message if it's a Message object, otherwise return as-is."""
    if isinstance(msg, Message):
        return translate(msg, context=request)
    return msg
