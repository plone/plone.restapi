from datetime import datetime
from DateTime import DateTime
from datetime import timedelta
from operator import itemgetter
from plone import api
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplies
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import ITTWLockable
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.tests.statictime import StaticTime
from zope.component import createObject
from zope.component import getUtility
from zope.interface import alsoProvides
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.restapi.serializer.working_copy import WorkingCopyInfo
from plone.restapi.testing import PLONE_RESTAPI_ITERATE_FUNCTIONAL_TESTING
from plone.restapi.serializer.converters import json_compatible

import transaction
import unittest


class TestStaticTime(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True

        transaction.commit()

    def create_document(self, id_):
        self.portal.invokeFactory("Document", id=id_)
        document = self.portal[id_]
        document.title = "My title"
        return document

    def create_comments(self, document):
        document.allow_discussion = True

        conversation = IConversation(document)
        replies = IReplies(conversation)
        comments = []
        for x in range(1, 2):
            comment = createObject("plone.Comment")
            comment.text = "Comment %d" % x
            comment = replies[replies.addComment(comment)]

            comment_replies = IReplies(comment)
            for y in range(1, 2):
                comment = createObject("plone.Comment")
                comment.text = "Comment %d.%d" % (x, y)
                comment_replies.addComment(comment)
                comments.append(comment)

        return comments

    def assert_roughly_now(self, dt):
        pydt = dt
        if isinstance(pydt, DateTime):
            pydt = pydt.asdatetime()
        elif isinstance(pydt, float):
            pydt = datetime.fromtimestamp(pydt)

        epsilon = timedelta(minutes=5)
        now = datetime.now()
        if pydt.tzinfo is not None:
            now = pydt.tzinfo.localize(now)

        upper = now + epsilon
        lower = now - epsilon

        self.assertTrue(
            lower < pydt < upper,
            "Expected %r to be now (within +/- %r). "
            "It's currently %s though, and the date time is off by %r"
            % (pydt, epsilon, now, now - pydt),
        )

    def assert_of_same_type(self, fake_datetimes, real_datetimes):
        for fake, real in zip(fake_datetimes, real_datetimes):
            # Guard against accidentally comparing the same objects
            self.assertNotEqual(fake, real)
            self.assertIsInstance(
                fake,
                real.__class__,
                "Faked static time %r is of a different "
                "type than the real %r" % (fake, real),
            )

    def test_statictime_dxcontent_created(self):
        frozen_time = datetime(1950, 7, 31, 13, 45)
        statictime = StaticTime(created=frozen_time)

        statictime.start()
        doc1 = self.create_document("doc1")
        self.assertEqual(DateTime(frozen_time), doc1.creation_date)
        fake_datetimes = [doc1.creation_date]

        statictime.stop()
        doc2 = self.create_document("doc2")
        self.assert_roughly_now(doc2.creation_date)
        real_datetimes = [doc2.creation_date]

        self.assert_of_same_type(fake_datetimes, real_datetimes)

    def test_statictime_dxcontent_modified(self):
        frozen_time = datetime(1950, 7, 31, 17, 30)
        statictime = StaticTime(modified=frozen_time)

        statictime.start()
        doc1 = self.create_document("doc1")
        self.assertEqual(DateTime(frozen_time), doc1.modification_date)
        fake_datetimes = [doc1.modification_date]

        statictime.stop()
        doc2 = self.create_document("doc2")
        self.assert_roughly_now(doc2.modification_date)
        real_datetimes = [doc2.modification_date]

        self.assert_of_same_type(fake_datetimes, real_datetimes)

    def test_statictime_comment_created(self):
        frozen_time = datetime(1950, 7, 31, 13, 45)
        statictime = StaticTime(created=frozen_time)

        statictime.start()
        doc1 = self.create_document("doc1")
        comments = self.create_comments(doc1)
        self.assertEqual(frozen_time, comments[0].creation_date)
        fake_datetimes = [comments[0].creation_date]

        statictime.stop()
        doc2 = self.create_document("doc2")
        comments = self.create_comments(doc2)
        self.assert_roughly_now(comments[0].creation_date)
        real_datetimes = [comments[0].creation_date]

        self.assert_of_same_type(fake_datetimes, real_datetimes)

    def test_statictime_comment_modified(self):
        frozen_time = datetime(1950, 7, 31, 17, 30)
        statictime = StaticTime(modified=frozen_time)

        statictime.start()
        doc1 = self.create_document("doc1")
        comments = self.create_comments(doc1)
        self.assertEqual(frozen_time, comments[0].modification_date)
        fake_datetimes = [comments[0].modification_date]

        statictime.stop()
        doc2 = self.create_document("doc2")
        comments = self.create_comments(doc2)
        self.assert_roughly_now(comments[0].modification_date)
        real_datetimes = [comments[0].modification_date]

        self.assert_of_same_type(fake_datetimes, real_datetimes)

    def test_statictime_get_info_for(self):
        frozen_time = datetime(1950, 7, 31, 17, 30)
        wftool = api.portal.get_tool("portal_workflow")
        statictime = StaticTime(modified=frozen_time)

        statictime.start()
        doc1 = self.create_document("doc1")
        api.content.transition(doc1, "publish")

        history = wftool.getInfoFor(doc1, "review_history")

        fake_datetimes = list(map(itemgetter("time"), history))
        self.assertEqual(
            fake_datetimes,
            [DateTime("1950/07/31 17:30:00 UTC"), DateTime("1950/07/31 18:30:00 UTC")],
        )

        statictime.stop()
        doc2 = self.create_document("doc2")
        api.content.transition(doc2, "publish")

        history = wftool.getInfoFor(doc2, "review_history")
        real_datetimes = list(map(itemgetter("time"), history))
        for ts in real_datetimes:
            self.assert_roughly_now(ts)

        self.assert_of_same_type(fake_datetimes, real_datetimes)

    def test_statictime_full_history(self):
        frozen_time = datetime(1950, 7, 31, 17, 30)
        statictime = StaticTime(modified=frozen_time)

        statictime.start()
        doc1 = self.create_document("doc1")
        doc1.setTitle("Current version")
        api.content.transition(doc1, "publish")
        viewlet = ContentHistoryViewlet(doc1, doc1.REQUEST, None)
        viewlet.update()

        history = viewlet.fullHistory()

        real_datetimes = list(map(itemgetter("time"), history))
        self.assertEqual(
            real_datetimes,
            [
                DateTime("1950/07/31 17:30:00 UTC"),
                -612855000.0,
                DateTime("1950/07/31 19:30:00 UTC"),
            ],
        )

        statictime.stop()
        doc2 = self.create_document("doc2")
        doc2.setTitle("Current version")
        api.content.transition(doc2, "publish")
        viewlet = ContentHistoryViewlet(doc2, doc2.REQUEST, None)
        viewlet.update()

        history = viewlet.fullHistory()

        fake_datetimes = list(map(itemgetter("time"), history))
        for ts in fake_datetimes:
            self.assert_roughly_now(ts)

        self.assert_of_same_type(fake_datetimes, real_datetimes)

    def test_statictime_lockinfo(self):
        frozen_time = datetime(1950, 7, 31, 17, 30)
        statictime = StaticTime(modified=frozen_time)

        doc1 = self.create_document("doc1")
        alsoProvides(doc1, ITTWLockable)
        lockable = ILockable(doc1)
        lockable.lock()

        statictime.start()
        lock_infos = lockable.lock_info()
        self.assertEqual(1, len(lock_infos))
        self.assertEqual(-612858600.0, lock_infos[0]["time"])
        fake_datetimes = [lock_infos[0]["time"]]

        statictime.stop()
        lock_infos = lockable.lock_info()
        self.assertEqual(1, len(lock_infos))
        self.assert_roughly_now(lock_infos[0]["time"])
        real_datetimes = [lock_infos[0]["time"]]

        self.assert_of_same_type(fake_datetimes, real_datetimes)


class TestStaticTimeWorkingCopy(unittest.TestCase):

    layer = PLONE_RESTAPI_ITERATE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True

        transaction.commit()

    def create_document(self, id_):
        self.portal.invokeFactory("Document", id=id_)
        document = self.portal[id_]
        document.title = "My title"
        return document

    def test_statictime_wc_created(self):
        frozen_time = datetime(1950, 7, 31, 13, 45)
        statictime = StaticTime(created=frozen_time)

        statictime.start()
        doc1 = self.create_document("doc1")

        policy = ICheckinCheckoutPolicy(doc1)
        policy.checkout(self.portal)
        baseline, working_copy = WorkingCopyInfo(doc1).get_working_copy_info()

        self.assertEqual(json_compatible(frozen_time), working_copy["created"])

        statictime.stop()
