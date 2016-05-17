HTTP Status Codes
=================

This is the list of status codes that are used in plone.restapi. Here is a `full list of all HTTP status codes <https://en.wikipedia.org/wiki/List_of_HTTP_status_codes>`_.


.. glossary::
    :sorted:

    2xx Success
        This class of status codes indicates the action requested by the client was received, understood, accepted and processed successfully.

    200 OK
        Standard response for successful HTTP requests.
        The actual response will depend on the request method used.
        In a GET request, the response will contain an entity corresponding to the requested resource.
        In a POST request, the response will contain an entity describing or containing the result of the action.

    201 Created
        The request has been fulfilled and resulted in a new resource being created.

    204 No Content
        The server successfully processed the request, but is not returning any content.
        Usually used as a response to a successful delete request.

    4xx Client Error
        The 4xx class of status code is intended for cases in which the client seems to have errored.

    400 Bad Request
        The server cannot or will not process the request due to something that is perceived to be a client error (e.g., malformed request syntax, invalid request message framing, or deceptive request routing)

    401 Unauthorized
        Similar to 403 Forbidden, but specifically for use when authentication is required and has failed or has not yet been provided.
        The response must include a WWW-Authenticate header field containing a challenge applicable to the requested resource.

    403 Forbidden
        The request was a valid request, but the server is refusing to respond to it.
        Unlike a 401 Unauthorized response, authenticating will make no difference.

    404 Not Found
        The requested resource could not be found but may be available again in the future.
        Subsequent requests by the client are permissible.

    405 Method Not Allowed
        A request method is not supported for the requested resource; for example, a GET request on a form which requires data to be presented via POST, or a PUT request on a read-only resource.

    409 Conflict
        Indicates that the request could not be processed because of conflict in the request, such as an edit conflict in the case of multiple updates.

    5xx Server Error
        The server failed to fulfill an apparently valid request.

    500 Internal Server Error
        The server failed to fulfill an apparently valid request.