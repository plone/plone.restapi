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
        # import pdb; pdb.set_trace()
        self.assertEqual(len(result['items']), 2)

    def test_portlets_render_news(self):
        self.portal.invokeFactory('News Item', 'n1')
        self.portal.invokeFactory('News Item', 'n2')
        self.portal.invokeFactory('News Item', 'n3')
        self.portal.invokeFactory('News Item', 'n4')
        self.portal.portal_workflow.doActionFor(self.portal.n1, 'publish')
        self.portal.portal_workflow.doActionFor(self.portal.n2, 'publish')
        self.portal.portal_workflow.doActionFor(self.portal.n3, 'publish')

        assignment = news.Assignment(count=2)
        renderer = NewsPortletRenderer(
            self.context, self.request, None, None, assignment)
        result = renderer.render()

        self.assertEqual(len(result['items']), 2)

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

    @patch('plone.app.portlets.portlets')
    def test_portlets_render_rss(self, portlets):
        portlets.RSSFeed.items.return_value = [1, 2, 3]
        assignment = rss.Assignment(
            count=3, url='https://planetpython.org/rss20.xml')
        renderer = RssPortletRenderer(
            self.context, self.request, None, None, assignment)
        result = renderer.render()

        self.assertEqual(len(result['items']), 3)

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
