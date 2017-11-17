# -*- coding: utf-8 -*-
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from unittest import TestCase
from zope.component import getMultiAdapter

from plone.restapi.interfaces import ISerializeToJson
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IReplies
from plone.registry.interfaces import IRegistry

from zope.component import createObject
from zope.component import getUtility

from plone import api


class TestCommentsSerializers(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
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
            type='Document',
            id='doc_with_comments',
            title='Document with comments',
            allow_discussion=True
        )
        self.conversation = IConversation(self.doc)
        self.replies = IReplies(self.conversation)
        comment = createObject('plone.Comment')
        comment.text = 'Comment'
        self.comment = self.replies[self.replies.addComment(comment)]

        comment = createObject('plone.Comment')
        comment.text = 'Comment 2'
        self.replies.addComment(comment)

    def test_conversation(self):
        serializer = getMultiAdapter(
            (self.conversation, self.request),
            ISerializeToJson
        )

        output = serializer()
        self.assertEqual(
            set(output.keys()),
            set(['@id', 'items_total', 'items'])
        )

    def test_conversation_batched(self):
        self.request.form['b_size'] = 1
        serializer = getMultiAdapter(
            (self.conversation, self.request),
            ISerializeToJson
        )

        output = serializer()
        self.assertIn('batching', output)

    def test_comment(self):
        serializer = getMultiAdapter(
            (self.comment, self.request),
            ISerializeToJson
        )

        output = serializer()

        expected = [
            '@id',
            '@type',
            '@parent',
            'comment_id',
            'in_reply_to',
            'text',
            'user_notification',
            'author_username',
            'author_name',
            'creation_date',
            'modification_date',
            'is_editable',
            'is_deletable'
        ]
        self.assertEqual(
            set(output.keys()),
            set(expected)
        )

        self.assertEqual(
            set(output['text'].keys()),
            set(['data', 'mime-type'])
        )
