# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import time
from datetime import timedelta
from plone.app.textfield import RichText
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.namedfile import field as namedfile
from plone.restapi.tests.helpers import ascii_token
from plone.supermodel import model
from plone.supermodel.directives import primary
from Products.CMFCore.utils import getToolByName
from pytz import timezone
from z3c.formwidget.query.interfaces import IQuerySource
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IIterableSource
from zope.schema.interfaces import ISource
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


INDEXES = (
    ("test_int_field", "FieldIndex"),
    ("test_list_field", "KeywordIndex"),
    ("test_bool_field", "BooleanIndex"),
)


@implementer(ISource)
class MyNonIterableSource(object):
    divisor = 2

    def __contains__(self, value):
        return bool(value % self.divisor)


@implementer(IIterableSource)
class MyIterableSource(object):
    values = [1, 2, 3]

    def __contains__(self, value):
        return value in self.values

    def __iter__(self):
        terms = [
            SimpleTerm(value=v, token="token%s" % v, title="Title %s" % v)
            for v in self.values
        ]
        return iter(terms)


@implementer(IQuerySource)
class MyIterableQuerySource(object):
    values = [1, 2, 3]

    def __contains__(self, value):
        return value in self.values

    def search(self, query):
        terms = [
            SimpleTerm(value=v, token="token%s" % v, title="Title %s" % v)
            for v in self.values
        ]
        return [t for t in terms if query in str(t.token)]

    def __iter__(self):
        # The @querysources endpoint should never attempt to enumerate terms
        raise NotImplementedError


@implementer(IIterableSource)
class MyIterableContextSource(object):
    def __init__(self, context):
        self.context = context

        title_words = self.context.title.split()
        self.terms = [
            SimpleTerm(value=w.lower(), token=ascii_token(w.lower()), title=w)
            for w in title_words
        ]

    def __contains__(self, value):
        return value in [t.value for t in self.terms]

    def __iter__(self):
        return iter(self.terms)


@implementer(IQuerySource)
class MyContextQuerySource(object):
    def __init__(self, context):
        self.context = context

        title_words = self.context.title.split()
        self.terms = [
            SimpleTerm(value=w.lower(), token=ascii_token(w.lower()), title=w)
            for w in title_words
        ]

    def __contains__(self, value):
        return value in [t.value for t in self.terms]

    def __iter__(self):
        # The @querysources endpoint should never attempt to enumerate terms
        raise NotImplementedError

    def search(self, query):
        return [t for t in iter(self.terms) if query in str(t.token)]


my_iterable_source = MyIterableSource()
my_non_iterable_source = MyNonIterableSource()
my_querysource = MyIterableQuerySource()


def my_context_source_binder(context):
    return MyIterableContextSource(context)


directlyProvides(my_context_source_binder, IContextSourceBinder)


def my_context_querysource_binder(context):
    return MyContextQuerySource(context)


directlyProvides(my_context_querysource_binder, IContextSourceBinder)


def vocabularyRequireingContextFactory(context):
    catalog = getToolByName(context, "portal_catalog")
    return SimpleVocabulary([SimpleTerm(catalog.id, catalog.id, catalog.id)])


class IDXTestDocumentSchema(model.Schema):

    # zope.schema fields
    test_ascii_field = schema.ASCII(required=False)
    test_asciiline_field = schema.ASCIILine(required=False)
    test_bool_field = schema.Bool(required=False)
    test_bytes_field = schema.Bytes(required=False)
    test_bytesline_field = schema.BytesLine(required=False)
    test_choice_field = schema.Choice(values=[u"foo", u"bar"], required=False)
    test_choice_field_with_vocabulary = schema.Choice(
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm(u"value1", "token1", u"title1"),
                SimpleTerm(u"value2", "token2", u"title2"),
            ]
        ),
        required=False,
    )

    test_choice_with_non_iterable_source = schema.Choice(
        required=False, source=my_non_iterable_source
    )
    test_choice_with_source = schema.Choice(required=False, source=my_iterable_source)
    test_choice_with_context_source = schema.Choice(
        required=False, source=my_context_source_binder
    )
    test_choice_with_querysource = schema.Choice(required=False, source=my_querysource)
    test_choice_with_context_querysource = schema.Choice(
        required=False, source=my_context_querysource_binder
    )

    test_date_field = schema.Date(required=False)
    test_datetime_field = schema.Datetime(required=False)
    test_datetime_tz_field = schema.Datetime(
        required=False,
        defaultFactory=lambda: timezone("Europe/Zurich").localize(
            datetime(2017, 10, 31, 10, 0)
        ),
    )
    test_decimal_field = schema.Decimal(required=False)
    test_dict_field = schema.Dict(required=False)
    test_float_field = schema.Float(required=False)
    test_frozenset_field = schema.FrozenSet(required=False)
    test_int_field = schema.Int(required=False)
    test_list_field = schema.List(required=False)
    test_list_field_with_choice_with_vocabulary = schema.List(
        value_type=schema.Choice(
            vocabulary=SimpleVocabulary(
                [
                    SimpleTerm(u"value1", "token1", u"title1"),
                    SimpleTerm(u"value2", "token2", u"title2"),
                    SimpleTerm(u"value3", "token3", u"title3"),
                ]
            )
        ),
        required=False,
    )
    test_set_field = schema.Set(required=False)
    test_set_field_with_choice_with_vocabulary = schema.Set(
        value_type=schema.Choice(
            vocabulary=SimpleVocabulary(
                [
                    SimpleTerm(u"value1", "token1", u"title1"),
                    SimpleTerm(u"value2", "token2", u"title2"),
                    SimpleTerm(u"value3", "token3", u"title3"),
                ]
            )
        ),
        required=False,
    )
    test_text_field = schema.Text(required=False)
    test_textline_field = schema.TextLine(required=False)
    test_time_field = schema.Time(required=False)
    test_timedelta_field = schema.Timedelta(required=False)
    test_tuple_field = schema.Tuple(required=False)
    test_nested_list_field = schema.List(required=False, value_type=schema.Tuple())
    test_nested_dict_field = schema.Dict(
        required=False, key_type=schema.ASCIILine(), value_type=schema.Tuple()
    )
    test_list_choice_with_context_vocabulary_field = schema.List(
        title=u"Field",
        value_type=schema.Choice(vocabulary="plone.restapi.testing.context_vocabulary"),
        required=False,
    )

    # plone.app.textfield
    test_richtext_field = RichText(
        required=False, allowed_mime_types=["text/html", "text/plain"]
    )

    # plone.namedfile fields
    test_namedfile_field = namedfile.NamedFile(required=False)
    test_namedimage_field = namedfile.NamedImage(required=False)
    test_namedblobfile_field = namedfile.NamedBlobFile(required=False)
    test_namedblobimage_field = namedfile.NamedBlobImage(required=False)

    primary("test_primary_namedfile_field")
    test_primary_namedfile_field = namedfile.NamedFile(required=False)

    # z3c.relationfield
    test_relationchoice_field = RelationChoice(
        required=False, source=CatalogSource(id=["doc1", "doc2"])
    )
    test_relationlist_field = RelationList(
        required=False,
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
    )

    # Test fields for validation
    test_required_field = schema.TextLine(required=True)
    test_readonly_field = schema.TextLine(required=False, readonly=True)
    test_maxlength_field = schema.TextLine(required=False, max_length=10)
    test_constraint_field = schema.TextLine(
        required=False, constraint=lambda x: u"00" in x
    )
    test_datetime_min_field = schema.Datetime(required=False, min=datetime(2000, 1, 1))
    test_time_min_field = schema.Time(required=False, min=time(1))
    test_timedelta_min_field = schema.Timedelta(required=False, min=timedelta(100))
    test_list_value_type_field = schema.List(required=False, value_type=schema.Int())
    test_dict_key_type_field = schema.Dict(required=False, key_type=schema.Int())

    read_permission(test_read_permission_field="cmf.ManagePortal")
    test_read_permission_field = schema.TextLine(required=False)
    write_permission(test_write_permission_field="cmf.ManagePortal")
    test_write_permission_field = schema.TextLine(required=False)

    read_permission(test_read_permission_field="cmf.ManagePortal")
    test_read_permission_field = schema.TextLine(required=False)

    test_invariant_field1 = schema.TextLine(required=False)
    test_invariant_field2 = schema.TextLine(required=False)

    test_missing_value_field = schema.TextLine(
        required=False, missing_value=u"missing", default=u"default"
    )

    test_missing_value_required_field = schema.TextLine(
        required=True, missing_value=u"missing", default=u"some value"
    )

    @invariant
    def validate_same_value(data):
        if data.test_invariant_field1 != data.test_invariant_field2:
            raise Invalid(u"Must have same values")

    # Test fields with default values
    test_default_value_field = schema.TextLine(required=True, default=u"Default")

    @provider(IContextAwareDefaultFactory)
    def default_factory(context):
        return u"DefaultFactory"

    test_default_factory_field = schema.TextLine(
        required=True, defaultFactory=default_factory
    )


class DXTestDocument(Item):
    """A Dexterity based test type containing a set of standard fields."""

    # Plone standard types (both, dx and at) do provide exclude_from_nav
    # and at least one test expect it to be here, so make it explicit
    exclude_from_nav = False


@provider(IFormFieldProvider)
class ITestBehavior(model.Schema):

    test_behavior_field = schema.TextLine(required=False)


@provider(IFormFieldProvider)
class ITestAnnotationsBehavior(model.Schema):

    test_annotations_behavior_field = schema.TextLine(required=False)
