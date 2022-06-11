from OFS.Image import Image
from plone import api
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplies
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import normalize_html
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.tests import dummy
from unittest import TestCase
from zope.component import createObject
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility


class TestCommentsSerializers(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()

        # Allow discussion
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        settings.edit_comment_enabled = True
        settings.delete_own_comment_enabled = True

        # doc with comments
        self.doc = api.content.create(
            container=self.portal,
            type="Document",
            id="doc_with_comments",
            title="Document with comments",
            allow_discussion=True,
        )
        self.conversation = IConversation(self.doc)
        self.replies = IReplies(self.conversation)
        comment = createObject("plone.Comment")
        comment.text = "Comment"
        self.comment = self.replies[self.replies.addComment(comment)]

        comment = createObject("plone.Comment")
        comment.text = "Comment 2"
        self.replies.addComment(comment)

    def test_conversation(self):
        serializer = getMultiAdapter(
            (self.conversation, self.request), ISerializeToJson
        )

        output = serializer()
        self.assertEqual(set(output), {"@id", "permissions", "items_total", "items"})

    def test_conversation_batched(self):
        self.request.form["b_size"] = 1
        serializer = getMultiAdapter(
            (self.conversation, self.request), ISerializeToJson
        )

        output = serializer()
        self.assertIn("batching", output)

    def test_comment(self):
        serializer = getMultiAdapter((self.comment, self.request), ISerializeToJson)

        output = serializer()

        expected = [
            "@id",
            "@type",
            "@parent",
            "comment_id",
            "in_reply_to",
            "text",
            "user_notification",
            "author_username",
            "author_name",
            "author_image",
            "creation_date",
            "modification_date",
            "is_editable",
            "is_deletable",
            "can_reply",
        ]
        self.assertEqual(set(output), set(expected))

        self.assertEqual(set(output["text"]), {"data", "mime-type"})

    def test_comment_with_author_image(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        # set member portrait
        membertool = getToolByName(self.portal, "portal_memberdata")
        membertool._setPortrait(
            Image(id=TEST_USER_ID, file=dummy.File(), title=""), TEST_USER_ID
        )
        self.conversation = IConversation(self.doc)
        self.replies = IReplies(self.conversation)
        comment = createObject("plone.Comment")
        comment.text = "Hey ho, let's go!"
        comment.author_username = TEST_USER_ID
        self.comment = self.replies[self.replies.addComment(comment)]

        serializer = getMultiAdapter((self.comment, self.request), ISerializeToJson)
        self.assertEqual(
            f"{self.portal_url}/portal_memberdata/portraits/test_user_1_",
            serializer().get("author_image"),
        )

    def test_comment_with_no_author_image(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.conversation = IConversation(self.doc)
        self.replies = IReplies(self.conversation)
        comment = createObject("plone.Comment")
        comment.text = "Hey ho, let's go!"
        comment.author_username = TEST_USER_ID
        self.comment = self.replies[self.replies.addComment(comment)]

        serializer = getMultiAdapter((self.comment, self.request), ISerializeToJson)
        self.assertEqual(
            None,
            serializer().get("author_image"),
        )

    def test_comment_with_mimetype_text_plain(self):
        self.conversation = IConversation(self.doc)
        self.replies = IReplies(self.conversation)
        comment = createObject("plone.Comment")
        comment.text = "Hey, I am plain text!"
        comment.mime_type = "text/plain"
        self.comment = self.replies[self.replies.addComment(comment)]

        serializer = getMultiAdapter((self.comment, self.request), ISerializeToJson)

        # serializer should return HTML with a clickable link
        self.assertEqual(
            "Hey, I am plain text!",
            serializer()["text"]["data"],
        )
        # serializer should return mimetype = text/x-web-intelligent
        self.assertEqual("text/plain", serializer()["text"]["mime-type"])

    def test_comment_with_mimetype_intelligent_text(self):
        # Set text transform to intelligent text
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.text_transform = "text/x-web-intelligent"

        self.conversation = IConversation(self.doc)
        self.replies = IReplies(self.conversation)
        comment = createObject("plone.Comment")
        comment.text = "Go to https://www.plone.org"
        comment.mime_type = "text/x-web-intelligent"
        self.comment = self.replies[self.replies.addComment(comment)]

        serializer = getMultiAdapter((self.comment, self.request), ISerializeToJson)

        # serializer should return HTML with a clickable link
        self.assertEqual(
            'Go to <a href="https://www.plone.org" '
            + 'rel="nofollow">https://www.plone.org</a>',
            normalize_html(serializer()["text"]["data"]),
        )
        # serializer should return mimetype = text/html
        self.assertEqual("text/html", serializer()["text"]["mime-type"])

    def test_comment_with_mimetype_html(self):
        # Set text transform to text/html
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.text_transform = "text/html"

        self.conversation = IConversation(self.doc)
        self.replies = IReplies(self.conversation)
        comment = createObject("plone.Comment")
        comment.text = "Go to <a href='https://www.plone.org'>Plone</a>"
        comment.mime_type = "text/html"
        self.comment = self.replies[self.replies.addComment(comment)]

        serializer = getMultiAdapter((self.comment, self.request), ISerializeToJson)

        # serializer should return HTML
        self.assertEqual(
            'Go to <a href="https://www.plone.org">Plone</a>',
            normalize_html(serializer()["text"]["data"]),
        )
        # serializer should return mimetype = text/html
        self.assertEqual("text/html", serializer()["text"]["mime-type"])
