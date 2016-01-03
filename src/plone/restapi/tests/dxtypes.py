# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Item
from plone.namedfile import field as namedfile
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema


class IDXTestDocumentSchema(model.Schema):

    # zope.schema fields
    test_ascii_field = schema.ASCII(required=False)
    test_asciiline_field = schema.ASCIILine(required=False)
    test_bool_field = schema.Bool(required=False)
    test_bytes_field = schema.Bytes(required=False)
    test_bytesline_field = schema.BytesLine(required=False)
    test_choice_field = schema.Choice(values=[u'foo', u'bar'], required=False)
    test_date_field = schema.Date(required=False)
    test_datetime_field = schema.Datetime(required=False)
    test_decimal_field = schema.Decimal(required=False)
    test_dict_field = schema.Dict(required=False)
    test_float_field = schema.Float(required=False)
    test_frozenset_field = schema.FrozenSet(required=False)
    test_int_field = schema.Int(required=False)
    test_list_field = schema.List(required=False)
    test_set_field = schema.Set(required=False)
    test_text_field = schema.Text(required=False)
    test_textline_field = schema.TextLine(required=False)
    test_time_field = schema.Time(required=False)
    test_timedelta_field = schema.Timedelta(required=False)
    test_tuple_field = schema.Tuple(required=False)
    test_nested_list_field = schema.List(
        required=False, value_type=schema.Tuple())
    test_nested_dict_field = schema.Dict(
        required=False, key_type=schema.ASCIILine(), value_type=schema.Tuple())

    # plone.app.textfield
    test_richtext_field = RichText(required=False)

    # plone.namedfile fields
    test_namedfile_field = namedfile.NamedFile(required=False)
    test_namedimage_field = namedfile.NamedImage(required=False)
    test_namedblobfile_field = namedfile.NamedBlobFile(required=False)
    test_namedblobimage_field = namedfile.NamedBlobImage(required=False)

    # z3c.relationfield
    test_relationchoice_field = RelationChoice(
        required=False, vocabulary="plone.app.vocabularies.Catalog")
    test_relationlist_field = RelationList(
        required=False, value_type=RelationChoice(
            vocabulary="plone.app.vocabularies.Catalog"))


class DXTestDocument(Item):
    """A Dexterity based test type containing a set of standard fields."""
