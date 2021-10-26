# pylint: disable=E0211, W0221
# E0211: Method has no argument
# W0221: Arguments number differs from overridden '__call__' method

from zope.interface import Attribute
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IPloneRestapiLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ISerializeToJson(Interface):
    """Adapter to serialize a Dexterity object into a JSON object."""


class ISerializeToJsonSummary(Interface):
    """Adapter to serialize an object into a JSON compatible summary that
    contains only the most basic information.
    """


class IJsonCompatible(Interface):
    """Convert a value to a JSON compatible data structure."""


class IContextawareJsonCompatible(IJsonCompatible):
    """Convert a value to a JSON compatible data structure, using a context."""

    def __init__(value, context):
        """Adapts value and a context"""


class IFieldSerializer(Interface):
    """The field serializer multi adapter serializes the field value into
    JSON compatible python data.
    """

    def __init__(field, context, request):
        """Adapts field, context and request."""

    def __call__():
        """Returns JSON compatible python data."""


class IPrimaryFieldTarget(Interface):
    """Return a URL to direct the user to if this is the primary field.
    Useful e.g. if you want to redirect certain users to a download url
    instead of the item's view.
    """

    def __init__(field, context, request):
        """Adapts field, context and request."""

    def __call__():
        """Returns a URL."""


class IObjectPrimaryFieldTarget(Interface):
    """Return a URL to direct the user to if the object has a primary field
    that provides an IPrimaryFieldTarget.
    """

    def __init__(field, context, request):
        """Adapts field, context and request."""

    def __call__():
        """Returns a URL."""


class IDeserializeFromJson(Interface):
    """An adapter to deserialize a JSON object into an object in Plone."""


class IFieldDeserializer(Interface):
    """An adapter to deserialize a JSON value into a field value."""

    def __init__(field, context, request):
        """Adapts a field, it's context and the request."""

    def __call__(value):
        """Convert the provided JSON value to a field value."""


class IBlockFieldDeserializationTransformer(Interface):
    """Convert/adjust raw block deserialized value into block value."""

    block_type = Attribute(
        "A string with the type of block, the @type from " "the block value"
    )
    order = Attribute(
        "A number used in sorting value transformers. " "Smaller is executed first"
    )
    disabled = Attribute("Boolean that disables the transformer if required")

    def __init__(field, context, request):
        """Adapts context and the request."""

    def __call__(value):
        """Convert the provided raw Python value to a block value."""


class IBlockFieldSerializationTransformer(Interface):
    """Transform block value before final JSON serialization"""

    block_type = Attribute(
        "A string with the type of block, the @type from " "the block value"
    )
    order = Attribute(
        "A number used in sorting value transformers for the "
        "same block. Smaller is executed first"
    )
    disabled = Attribute("Boolean that disables the transformer if required")

    def __init__(field, context, request):
        """Adapts context and the request."""

    def __call__(value):
        """Convert the provided raw Python value to a block value."""


class IExpandableElement(Interface):
    """A named adapter that deserializes an element in expanded or collapsed
    form.
    """

    def __call__(expand=False):
        """ """


class IZCatalogCompatibleQuery(Interface):
    """A multi adapter responsible for converting a catalog query provided as
    a Python dictionary, but with possibly incorrect value types, to a
    Python dictionary that can be passed directly to catalog.searchResults().

    Values (query values or query options) that can't be serialized in JSON
    (like datetimes) or a query string (any type other than string) must be
    converted back by this adapter, by delegating that job to an
    IIndexQueryParser for each of the queried indexes.
    """

    global_query_params = Attribute(
        "A mapping of query-wide parameters (like 'sort_on') to their data "
        "type. These need to be treated separately from indexes."
    )

    def __init__(context, request):
        """Adapts context and request."""

    def __call__(query):
        """Returns a ZCatalog compatible query (Python dictionary)."""


class IIndexQueryParser(Interface):
    """A multi adapter responsible for deserializing values in catalog query
    options for a particular index type.

    The main issue here is typing of query values and query options: ZCatalog
    expects any values in queries to have the proper type, and fails
    unpredictably otherwise.

    Because we can't avoid losing (some of) this typing information when
    submitting queries to the API via a HTTP query string, we need to
    reconstruct it based on what the index that is queried expects.

    This adapter therefore needs to know what data types the adapted index
    expects, and turn any values (query values or query options) back into the
    proper data type.
    """

    query_value_type = Attribute(
        "The data type of the query value for queries against this index. "
        "The query value may also be a sequence of values of that type."
    )

    query_options = Attribute(
        "A mapping of query options this index type supports to their type."
    )

    def __init__(index, context, request):
        """Adapts a ZCatalog index, context and request."""

    def parse(idx_query):
        """Takes a query against a single index (the value part of a
        {'index_name': idx_query} pair).

        `idx_query` can therefore be
          - a single string value
          - a list of string values
          - a dictionary with one or more query options, among them the actual
            query value identified by the 'query' key

        Returns a transformed `idx_query` whose query options and query values
        have been reconstructed to the proper data types that the adapted
        index expects.
        """


class IBlockSearchableText(Interface):
    """Allow blocks to provide text for the SearchableText index

    Register as a named adapter, where the name is the block @type
    """

    def __init__(field, context, request):
        """Adapts a context and the request."""

    def __call__(value):
        """Extract text from the block value. Returns text"""
