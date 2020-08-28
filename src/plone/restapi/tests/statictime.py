# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import datetime
from plone.app.discussion.comment import Comment
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from plone.dexterity.content import DexterityContent
from plone.locking.lockable import TTWLockable
from Products.CMFCore.WorkflowTool import _marker
from Products.CMFCore.WorkflowTool import WorkflowTool


_originals = {
    "WorkflowTool.getInfoFor": WorkflowTool.getInfoFor,
    "ContentHistoryViewlet.fullHistory": ContentHistoryViewlet.fullHistory,
    "TTWLockable.lock_info": TTWLockable.lock_info,
}


class StaticTime(object):
    """ContextManager to patch accessor methods that return dynamic timestamps,
    like creation and modification dates, with ones that return static
    timestamps.

    This is needed during testing to get stable serialization output,
    especially during the tests that dump HTTP response examples to the
    filesystem, because the content of those responses would otherwise
    change all the time.

    Specifically monkey-patching a few accessors (getter methods) in a
    targeted way like this was chosen as an alternative to freezing time
    entirely using libraries like `freezegun`, because that approach has
    caused issues in the past with code that assumes a monotonic clock, like
    the generation of ZODB transaction IDs.

    Instead, this helper aims to selectively patch only what we currently
    need to get stable test runs and HTTP response examples.

    The bulk of cases is addressed by patching `creation_date` and
    `modification_date` for Dexterity objects to return static times. In
    addition, a couple other places need some attention.

    These places will be patched on start() (and unpatched on stop()):

    - DexterityContent
        - creation_date
        - modification_date

    - p.a.discussion Comment
        - creation_date
        - modification_date

    - WorkflowTool.getInfoFor
        - (if asked for 'review_history')

    - ContentHistoryViewlet
        - fullHistory

    - TTWLockable
        - lock_info

    """

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, _type, exc, _traceback):
        self.stop()

    def __init__(
        self,
        created=datetime(1995, 7, 31, 13, 45),
        modified=datetime(1995, 7, 31, 17, 30),
    ):
        self.static_created = created
        self.static_modified = modified
        """Set up a static time helper.

        If given, the Python datetimes for `created` and `modified` will be
        used to determine the timestamps that should be returned by the
        static getters.

        Ensuring the appropriate type (Python datetime vs. Zope DateTime
        vs. float) is the responsiblity of the patched getter method. The user
        of the StaticTime class shouldn't need to care about it, and be able
        to pass Python datetimes that then will be casted appropriately if
        necessary.

        The `modified` timestamp will also be used as a basis when producing
        a sequence of fake times, for example when patching times for
        successive events in the review history.
        """

    def start(self):
        """Patch the respective getters so that they return static times."""
        # Patch created and modified times for DexterityContent.
        # creation_date and modification_date are instance-level attributes
        # on DX object that get initialized with datetime.now() during
        # __init__. In order to fake the returned times we patch a property
        # onto the class which will shadow these instance attributes.
        DexterityContent.creation_date = property(
            static_creation_date_getter_factory(self.static_created), nop_setter
        )
        DexterityContent.modification_date = property(
            static_modification_date_getter_factory(self.static_modified), nop_setter
        )

        # Patch the lightweight p.a.discussion 'Comment' type. Its dates are
        # Python datetimes, unlike DX Content types which use zope DateTimes.
        Comment.creation_date = property(
            static_creation_date_getter_factory(self.static_created, type_=datetime),
            nop_setter,
        )
        Comment.modification_date = property(
            static_modification_date_getter_factory(
                self.static_modified, type_=datetime
            ),
            nop_setter,
        )

        WorkflowTool.getInfoFor = static_get_info_for_factory(self.static_modified)

        ContentHistoryViewlet.fullHistory = static_full_history_factory(
            self.static_modified
        )

        TTWLockable.lock_info = static_lock_info_factory(self.static_modified)

    def stop(self):
        """Undo all the patches."""
        TTWLockable.lock_info = _originals["TTWLockable.lock_info"]
        ContentHistoryViewlet.fullHistory = _originals[
            "ContentHistoryViewlet.fullHistory"
        ]
        WorkflowTool.getInfoFor = _originals["WorkflowTool.getInfoFor"]

        Comment.modification_date = None
        Comment.creation_date = None

        del DexterityContent.modification_date
        del DexterityContent.creation_date


def static_get_info_for_factory(dt_value):
    """Returns a static time replacement for WorkflowTool.getInfoFor
    configured with the given datetime value as a base.
    """
    if isinstance(dt_value, datetime):
        dt_value = DateTime(dt_value)

    def static_get_info_for(self, ob, name, default=_marker, wf_id=None, *args, **kw):
        """This replacement function will, if 'review_history' is requested,
        replace timestamps in the returned list of dicts with static times.

        The timestamps for the successive events in this list will use the
        dt_value (which defaults to modification date) as a base, and then
        move forward in hourly steps to retain the chronological sequence of
        events.

        In other words, they will be stable (static), but different for each
        event, and should still reflect proper order of events.
        """
        res = _originals["WorkflowTool.getInfoFor"](
            self, ob, name, default=default, wf_id=wf_id, *args, **kw
        )
        if name == "review_history":
            base_date = dt_value

            # The ContentHistoryViewlet.fullHistory method assembles results
            # from both the review_history (i.e., this method's result) and
            # the revision history, and intertwines their elements in
            # chronological order. That doesn't work if we already return
            # faked timestamps here in that case.
            #
            # We therefore need to recognize this case by inspecting the call
            # stack to check whether we got called by the fullHistory method,
            # and in that case return the original results. (Since fullHistory
            # will also be patched, timestamps in the combined results will be
            # replaced there.)
            import traceback

            stack = traceback.format_stack()
            if "static_full_history" in str(stack):
                return res

            for idx, item in enumerate(res):
                fake_date = base_date + (idx / 24.0)  # plus one hour
                if "time" in item:
                    item["time"] = fake_date

        return res

    return static_get_info_for


def static_full_history_factory(dt_value):
    """Returns a static time replacement for ContentHistoryViewlet.fullHistory
    configured with the given datetime value as a base.
    """
    if isinstance(dt_value, datetime):
        dt_value = DateTime(dt_value)

    def static_full_history(self):
        """This replacement function will replace timestamps in the returned
        list of dicts with static times.

        The timestamps for the successive events in this list will use the
        dt_value (which defaults to modification date) as a base, and then
        move forward in hourly steps to retain the chronological sequence of
        events.

        In other words, they will be stable (static), but different for each
        event, and should still reflect proper order of events.
        """
        actions = _originals["ContentHistoryViewlet.fullHistory"](self)

        base_date = dt_value
        for idx, action in enumerate(actions):
            if "time" in action:
                fake_date = base_date + (idx / 24.0)  # plus one hour

                # Depending on the kind of action, timestamps may either
                # be zope DateTimes or floats. Let's reserve the same type.
                if isinstance(action["time"], float):
                    action["time"] = float(fake_date)
                elif isinstance(action["time"], DateTime):
                    action["time"] = fake_date
                else:
                    raise Exception("Don't know how to patch %r" % action["time"])

        return actions

    return static_full_history


def static_creation_date_getter_factory(dt_value, type_=DateTime):
    """Returns a static time replacement for creation date accessors,
    configured with the given datetime value and the indicated type_.
    """
    if isinstance(dt_value, datetime) and type_ is DateTime:
        dt_value = DateTime(dt_value)

    elif isinstance(dt_value, DateTime) and type_ is datetime:
        dt_value = dt_value.asdatetime()

    def static_creation_date_getter(self):
        return dt_value

    return static_creation_date_getter


def static_modification_date_getter_factory(dt_value, type_=DateTime):
    """Returns a static time replacement for modification date accessors,
    configured with the given datetime value and the indicated type_.
    """
    if isinstance(dt_value, datetime) and type_ is DateTime:
        dt_value = DateTime(dt_value)

    elif isinstance(dt_value, DateTime) and type_ is datetime:
        dt_value = dt_value.asdatetime()

    def static_modification_date_getter(self, value=None):
        return dt_value

    return static_modification_date_getter


def static_lock_info_factory(dt_value):
    """Returns a static time replacement for TTWLockable.lock_info
    configured with the given datetime value as a base.
    """
    if isinstance(dt_value, datetime):
        dt_value = DateTime(dt_value)

    def static_lock_info(self):
        """This replacement function will replace timestamps in the returned
        list of lock_info dicts with static times.

        The timestamps for the successive lock_infos in this list will use the
        dt_value (which defaults to modification date) as a base, and then
        move forward in hourly steps to retain the chronological sequence of
        events.

        In other words, they will be stable (static), but different for each
        lock_info, and should still reflect proper order of events.
        """
        infos = _originals["TTWLockable.lock_info"](self)
        base_date = dt_value
        for idx, info in enumerate(infos):
            fake_date = base_date + (idx / 24.0)  # plus one hour
            if "time" in info:
                info["time"] = float(fake_date)

        return infos

    return static_lock_info


def nop_setter(self, value):
    pass
