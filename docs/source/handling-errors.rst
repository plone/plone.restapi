Handling Errors
===============

When you develop a service you will have to return errors to your users. To return an error you raise an :py:class:`plone.rest.errors.RestApiException`.

Example:

.. literalinclude:: ../../src/plone/restapi/tests/test_error_handling.py
   :language: python
   :pyobject: ApiExceptionExampleService

The arguments you pass to `RestApiException` are:

status
    A :ref:`HTTP status code<httpstatuscodes>` matching the error that occured.
type
    A short human readeble description of the error. This might be used for 
    frontend translation.
message
    A long human readable message for the user. This message is intended 
    for developers using the API and not for the end user details.
details (optional)
    An object that is serializable to JSON. This commanly is a dict with 
    keys/values describing the problem.
exception (optional)
    If you create your RestApiException in the except branch of a try/except block
    you can pass the original exception as a keyword argument and a traceback will be
    added to details. In this case details have to be `None` or a `dict`.

    
When you raise an exception in a service the restapi error handling
will serialized it to a standartized error response with the status
code and the information we passed to the `RestApiException`:

.. literalinclude:: api_exception.resp
   :language: http


This will also abort the transaction for you. Changes to the ZODB
during the request will not be committed. This is generally the right
approach. You should only circumvent it if you have a use case that
absolutely requires writing data despite returning an error.


