"""Helpers for tests related to emitting events to the tracking logs."""

from datetime import datetime

from django.test import TestCase
from django.test.utils import override_settings
from freezegun import freeze_time
from pytz import UTC

from eventtracking import tracker
from eventtracking.django import DjangoTracker


FROZEN_TIME = datetime(2013, 10, 3, 8, 24, 55, tzinfo=UTC)
IN_MEMORY_BACKEND_CONFIG = {
    'mem': {
        'ENGINE': 'track.tests.InMemoryBackend'
    }
}


class InMemoryBackend(object):
    """A backend that simply stores all events in memory"""

    def __init__(self):
        super(InMemoryBackend, self).__init__()
        self.events = []

    def send(self, event):
        """Store the event in a list"""
        self.events.append(event)


def unicode_flatten(tree):
    """
    Test cases have funny issues where some strings are unicode, and
    some are not. This does not cause test failures, but causes test
    output diffs to show many more difference than actually occur in the
    data. This will convert everything to a common form.
    """
    if isinstance(tree, basestring):
        return unicode(tree)
    elif isinstance(tree, list):
        return map(unicode_flatten, list)
    elif isinstance(tree, dict):
        return dict([(unicode_flatten(key), unicode_flatten(value)) for key, value in tree.iteritems()])
    return tree


@freeze_time(FROZEN_TIME)
@override_settings(
    EVENT_TRACKING_BACKENDS=IN_MEMORY_BACKEND_CONFIG
)
class EventTrackingTestCase(TestCase):
    """
    Supports capturing of emitted events in memory and inspecting them.

    Each test gets a "clean slate" and can retrieve any events emitted during their execution.

    """

    # Make this more robust to the addition of new events that the test doesn't care about.

    def setUp(self):
        super(EventTrackingTestCase, self).setUp()

        self.tracker = DjangoTracker()
        tracker.register_tracker(self.tracker)

    @property
    def backend(self):
        """A reference to the in-memory backend that stores the events."""
        return self.tracker.backends['mem']

    def get_event(self, idx=0):
        """Retrieve an event emitted up to this point in the test."""
        return self.backend.events[idx]

    def assert_no_events_emitted(self):
        """Ensure no events were emitted at this point in the test."""
        self.assertEquals(len(self.backend.events), 0)

    def assert_events_emitted(self):
        """Ensure at least one event has been emitted at this point in the test."""
        self.assertGreaterEqual(len(self.backend.events), 1)

    def assertEqualUnicode(self, tree_a, tree_b):
        """Like assertEqual, but give nicer errors for unicode vs. non-unicode"""
        self.assertEqual(unicode_flatten(tree_a), unicode_flatten(tree_b))
