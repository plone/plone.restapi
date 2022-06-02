from DateTime import DateTime
from importlib import import_module
from plone.dexterity.utils import iterSchemata
from plone.namedfile.file import NamedImage
from plone.restapi.interfaces import IRelationObjectSerializer
from plone.restapi.serializer.relationobject import DefaultRelationObjectSerializer
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.tests.helpers import patch_scale_uuid
from unittest import TestCase
from z3c.form.interfaces import IDataManager
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass

import os


HAS_PLONE_6 = getattr(
    import_module("Products.CMFPlone.factory"), "PLONE60MARKER", False
)


class TestRelationObjectSerializing(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING
    maxDiff = None

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc1", title="Test Document"
            )
        ]
        self.doc2 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument",
                id="doc2",
                title="Test Document 2",
                description="Test Document 2 Description",
            )
        ]
        self.doc2.creation_date = DateTime("2016-01-21T01:14:48+00:00")
        self.doc2.modification_date = DateTime("2017-01-21T01:14:48+00:00")

    def serialize(self, fieldname, value, rel_obj):
        for schema in iterSchemata(self.doc1):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        dm = getMultiAdapter((self.doc1, field), IDataManager)
        dm.set(value)
        serializer = getMultiAdapter((rel_obj, field, self.doc1, self.request))
        return serializer()

    def test_empty_relationship(self):
        """Edge case: empty relationship

        Should not be used like this but since it's possible to call it with
        an empty relationship but a valid rel_obj, we include testing for this.
        """
        fn = "test_relationchoice_field"
        value = self.serialize(
            fn,
            None,
            self.doc2,
        )
        self.assertTrue(value is None)

    def test_default_relationship(self):
        fn = "test_relationchoice_field"
        value = self.serialize(
            fn,
            self.doc2,
            self.doc2,
        )
        self.assertTrue(isinstance(value, dict), "Not a <dict>")
        obj_url = self.doc2.absolute_url()
        obj_uid = self.doc2.UID()
        self.assertEqual(
            {
                "@id": obj_url,
                "@type": "DXTestDocument",
                "UID": obj_uid,
                "title": "Test Document 2",
                "description": "Test Document 2 Description",
                "id": "doc2",
                "created": "2016-01-21T01:14:48+00:00",
                "modified": "2017-01-21T01:14:48+00:00",
                "review_state": "private",
            },
            value,
        )


class TestRelationObjectImageSerializingOriginalAndPNGScales(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING
    maxDiff = None

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc1", title="Test Document"
            )
        ]
        self.image1 = self.portal[
            self.portal.invokeFactory(
                "Image",
                id="image1",
                title="Test Image",
                description="Test Image Description",
            )
        ]
        self.image1.creation_date = DateTime("2016-01-21T01:14:48+00:00")
        self.image1.modification_date = DateTime("2017-01-21T01:14:48+00:00")

    def serialize(self, fieldname, value, image):
        for schema in iterSchemata(self.doc1):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        dm = getMultiAdapter((self.doc1, field), IDataManager)
        dm.set(value)
        setattr(self.image1, "image", image)
        serializer = getMultiAdapter((self.image1, field, self.doc1, self.request))
        return serializer()

    def test_empty_relationship(self):
        """Edge case: empty relationship"""
        image_file = os.path.join(os.path.dirname(__file__), "1024x768.gif")
        with open(image_file, "rb") as f:
            image_data = f.read()
        fn = "test_relationchoice_field"
        value = self.serialize(
            fn,
            None,
            NamedImage(
                data=image_data, contentType="image/gif", filename="1024x768.gif"
            ),
        )
        self.assertTrue(value is None)

    def test_image_serialization_returns_dict_with_original_scale(self):
        """In Plone >= 5.2 the image returned when requesting an image
        scale with the same width and height of the original image is
        the actual original image in its original format"""
        image_file = os.path.join(os.path.dirname(__file__), "1024x768.gif")
        with open(image_file, "rb") as f:
            image_data = f.read()
        fn = "test_relationchoice_field"
        scale_url_uuid = "uuid_1"
        with patch_scale_uuid(scale_url_uuid):
            value = self.serialize(
                fn,
                self.image1,
                NamedImage(
                    data=image_data, contentType="image/gif", filename="1024x768.gif"
                ),
            )
            self.assertTrue(isinstance(value, dict), "Not a <dict>")
            obj_url = self.image1.absolute_url()
            obj_uid = self.image1.UID()
            # Original image is still a "scale"
            # scaled images are converted to PNG in Plone = 5.2
            original_download_url = "{}/@@images/{}.{}".format(
                obj_url, scale_url_uuid, "gif"
            )
            scale_download_url = "{}/@@images/{}.{}".format(
                obj_url, scale_url_uuid, "png"
            )
            scales = {
                "listing": {
                    "download": scale_download_url,
                    "width": 16,
                    "height": 12,
                },
                "icon": {"download": scale_download_url, "width": 32, "height": 24},
                "tile": {"download": scale_download_url, "width": 64, "height": 48},
                "thumb": {
                    "download": scale_download_url,
                    "width": 128,
                    "height": 96,
                },
                "mini": {
                    "download": scale_download_url,
                    "width": 200,
                    "height": 150,
                },
                "preview": {
                    "download": scale_download_url,
                    "width": 400,
                    "height": 300,
                },
                "large": {
                    "download": scale_download_url,
                    "width": 768,
                    "height": 576,
                },
            }
            if HAS_PLONE_6:
                # PLIP #3279 amended the image scales
                # https://github.com/plone/Products.CMFPlone/pull/3450
                scales["great"] = {
                    "download": scale_download_url,
                    "height": 768,
                    "width": 1024,
                }
                scales["huge"] = {
                    "download": scale_download_url,
                    "height": 768,
                    "width": 1024,
                }
                scales["larger"] = {
                    "download": scale_download_url,
                    "height": 750,
                    "width": 1000,
                }
                scales["large"] = {
                    "download": scale_download_url,
                    "height": 600,
                    "width": 800,
                }
                scales["teaser"] = {
                    "download": scale_download_url,
                    "height": 450,
                    "width": 600,
                }
            self.assertEqual(
                {
                    "filename": "1024x768.gif",
                    "content-type": "image/gif",
                    "size": 1514,
                    "download": original_download_url,
                    "width": 1024,
                    "height": 768,
                    "@id": obj_url,
                    "@type": "Image",
                    "UID": obj_uid,
                    "title": "Test Image",
                    "description": "Test Image Description",
                    "id": "image1",
                    "created": "2016-01-21T01:14:48+00:00",
                    "modified": "2017-01-21T01:14:48+00:00",
                    "review_state": None,
                    "scales": scales,
                },
                value,
            )

    def test_image_serialization_doesnt_choke_on_corrupt_image(self):
        """In Plone >= 5.2 the original image file is not a "scale", so its url
        is returned as is and we need to check it, but the scales should be empty"""
        image_data = b"INVALID IMAGE DATA"
        fn = "test_relationchoice_field"
        scale_url_uuid = "uuid_1"
        with patch_scale_uuid(scale_url_uuid):
            value = self.serialize(
                fn,
                self.image1,
                NamedImage(
                    data=image_data, contentType="image/gif", filename="1024x768.gif"
                ),
            )
            obj_url = self.image1.absolute_url()
            obj_uid = self.image1.UID()
            self.assertEqual(
                {
                    "content-type": "image/gif",
                    "download": "{}/@@images/{}.{}".format(
                        obj_url, scale_url_uuid, "gif"
                    ),
                    "filename": "1024x768.gif",
                    "height": -1,
                    "scales": {},
                    "size": 18,
                    "width": -1,
                    "@id": obj_url,
                    "@type": "Image",
                    "UID": obj_uid,
                    "title": "Test Image",
                    "description": "Test Image Description",
                    "id": "image1",
                    "created": "2016-01-21T01:14:48+00:00",
                    "modified": "2017-01-21T01:14:48+00:00",
                    "review_state": None,
                },
                value,
            )


class TestRelationObjectSerializers(TestCase):
    def test_default_relationobject_serializer(self):
        verifyClass(IRelationObjectSerializer, DefaultRelationObjectSerializer)
