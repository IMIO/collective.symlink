# -*- coding: utf-8 -*-

from collective.symlink.testing import COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING
from plone import api
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield import RelationValue

import unittest


def test_foo():
    return "foo"


def test_bar():
    return "bar"


class TestSymlinkAdaptedContext(unittest.TestCase):
    layer = COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING

    def setUp(self):
        intids = getUtility(IIntIds)
        self.portal = api.portal.get()
        self.base = api.content.create(
            type="Document",
            id="document",
            title="Title",
            description="Description",
            container=self.portal,
            test="test",
            foo="test",
        )
        self.base.test_method = test_foo
        self.folder = api.content.create(
            type="Folder", id="folder", container=self.portal
        )
        self.link = api.content.create(
            type="symlink",
            id="link",
            symbolic_link=RelationValue(intids.getId(self.base)),
            container=self.folder,
            foo="bar",
        )
        self.link.test_method = test_bar

    def tearDown(self):
        for e in ("folder", "document"):
            if e in self.portal:
                api.content.delete(self.portal[e])

    def test_id(self):
        self.assertEqual("link", self.link.id)

    def test_url(self):
        self.assertEqual(
            "http://localhost:55001/plone/folder/link", self.link.absolute_url()
        )

    def test_title(self):
        self.assertEqual("Title", self.link.Title())

    def test_description(self):
        self.assertEqual("Description", self.link.Description())

    def test_portal_type(self):
        self.assertEqual("symlink", self.link._link_portal_type)
        self.assertEqual("Document", self.link.portal_type)

    def test_allowed_content_types(self):
        self.assertEqual([], self.link.allowedContentTypes())

    def test_parent(self):
        from Acquisition import aq_parent

        self.assertTrue(self.link.__parent__ == self.folder)
        self.assertTrue(aq_parent(self.link) == self.folder)

    def test_attribute_inheritance(self):
        self.assertEqual("bar", self.link.foo)
        self.assertEqual("test", self.link.test)
        self.assertEqual("bar", self.link.test_method())
        self.assertEqual("foo", self.base.test_method())
