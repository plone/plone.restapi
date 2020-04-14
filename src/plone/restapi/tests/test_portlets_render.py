# -*- coding: utf-8 -*-
from plone.app.event.portlets import portlet_events
from plone.app.portlets.portlets import news
from plone.app.portlets.portlets import rss
from plone.app.portlets.portlets import search
from plone.portlet.static import static
from plone.restapi.serializer.portlets.events import EventsPortletRenderer
from plone.restapi.serializer.portlets.news import NewsPortletRenderer
from plone.restapi.serializer.portlets.recent import RecentPortletRenderer
from plone.restapi.serializer.portlets.rss import RssPortletRenderer
from plone.restapi.serializer.portlets.search import SearchPortletRenderer
from plone.restapi.serializer.portlets.static import StaticTextPortletRenderer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from unittest.mock import patch

import datetime
import os
import transaction
import unittest


class TestPortletsRender(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.context = self.portal
        self.request = self.context.REQUEST

        transaction.commit()

    def test_portlets_render_events(self):
        self.portal.invokeFactory('Event', 'e1')
        self.portal.invokeFactory('Event', 'e2')
        self.portal.invokeFactory('Event', 'e3')
        self.portal.portal_workflow.doActionFor(self.portal.e1, 'publish')
        self.portal.portal_workflow.doActionFor(self.portal.e2, 'publish')

        assignment = portlet_events.Assignment(count=2)
        renderer = EventsPortletRenderer(
            self.context, self.request, None, None, assignment)
        result = renderer.render()
        self.assertEqual(len(result['items']), 2)

        today = datetime.date.today().isoformat()

        for item in result['items']:
            assert today in item['start']
            assert today in item['end']
            assert today in item['created']
            assert today in item['modified']

    def test_portlets_render_news(self):
        from plone.namedfile.file import NamedBlobImage

        filename = os.path.join(os.path.dirname(__file__), u"image.png")

        self.portal.invokeFactory('News Item', 'n1')
        self.portal.invokeFactory('News Item', 'n2')
        self.portal.invokeFactory('News Item', 'n3')
        self.portal.invokeFactory('News Item', 'n4')

        self.portal.n2.image = NamedBlobImage(
            data=open(filename, "rb").read(), filename=filename)

        self.portal.portal_workflow.doActionFor(self.portal.n1, 'publish')
        self.portal.portal_workflow.doActionFor(self.portal.n2, 'publish')
        self.portal.portal_workflow.doActionFor(self.portal.n3, 'publish')

        assignment = news.Assignment(count=2)
        renderer = NewsPortletRenderer(
            self.context, self.request, None, None, assignment)
        result = renderer.render()

        self.assertEqual(result['items'][0]['thumb'], '')
        self.assertTrue(
            '/plone/n2/@@images/image/icon' in result['items'][1]['thumb'])
        self.assertEqual(len(result['items']), 2)

        self.assertEqual(result['all_news_link'], None)

        self.portal.invokeFactory('Folder', 'news')

        renderer = NewsPortletRenderer(
            self.context, self.request, None, None, assignment)
        result = renderer.render()

        self.assertEqual(self.portal.news.absolute_url(),
                         result['all_news_link'])

    def test_portlets_render_recent(self):
        self.portal.invokeFactory('Event', 'e1')
        self.portal.invokeFactory('Event', 'e2')
        self.portal.invokeFactory('Event', 'e3')
        self.portal.portal_workflow.doActionFor(self.portal.e1, 'publish')
        self.portal.portal_workflow.doActionFor(self.portal.e2, 'publish')

        self.portal.invokeFactory('News Item', 'n1')
        self.portal.invokeFactory('News Item', 'n2')
        self.portal.invokeFactory('News Item', 'n3')
        self.portal.invokeFactory('News Item', 'n4')
        self.portal.portal_workflow.doActionFor(self.portal.n1, 'publish')
        self.portal.portal_workflow.doActionFor(self.portal.n2, 'publish')
        self.portal.portal_workflow.doActionFor(self.portal.n3, 'publish')

        assignment = news.Assignment(count=10)
        renderer = RecentPortletRenderer(
            self.context, self.request, None, None, assignment)
        result = renderer.render()

        self.assertEqual(len(result['items']), 7)

    # def test_portlets_render_rss(self, feedparser):
    @patch('plone.app.portlets.portlets.rss.RSSFeed')
    def disabled_test_portlets_render_rss(self, RSSFeed):
        RSSFeed.items.return_value = [1, 2, 3]
        assignment = rss.Assignment(
            count=3, url='https://planetpython.org/rss20.xml')
        renderer = RssPortletRenderer(
            self.context, self.request, None, None, assignment)
        result = renderer.render()

        self.assertEqual(len(result['items']), 2)

    def test_portlets_render_search(self):
        assignment = search.Assignment(enableLivesearch=False)

        renderer = SearchPortletRenderer(
            self.context, self.request, None, None, assignment)
        result = renderer.render()
        self.assertFalse(result['enable_livesearch'])

    def test_portlets_render_static(self):
        assignment = static.Assignment(
            header=u"a static title", text=u"a static text")

        renderer = StaticTextPortletRenderer(
            self.context, self.request, None, None, assignment)
        result = renderer.render()

        # self.assertEqual(result['header'], u'a static title')
        self.assertEqual(result['text'], u'a static text')

    # import mock
    #
    # @mock.patch('os.urandom')
    # def test_abc_urandom(self, urandom_function):
    #     import os
    #
    #     urandom_function.return_value = 'pumpkins'
    #     assert os.urandom(5) == 'pumpkins'
    #     urandom_function.return_value = 'lemons'
    #     assert os.urandom(5) == 'lemons'
    #     urandom_function.side_effect = (
    #         lambda l: 'f' * l
    #     )
    #     assert os.urandom(5) == 'fffff'
