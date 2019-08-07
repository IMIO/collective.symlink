# -*- coding: utf-8 -*-

from collective.symlink.testing import COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING
from collective.symlink.content.symlink import AdaptedContext
from plone import api
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield import RelationValue

import unittest


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
        )
        self.folder = api.content.create(
            type="Folder", id="folder", container=self.portal
        )
        self.link = api.content.create(
            type="symlink",
            id="link",
            symbolic_link=RelationValue(intids.getId(self.base)),
            container=self.folder,
        )

    def tearDown(self):
        for e in ("document", "folder"):
            if e in self.portal:
                api.content.delete(self.portal[e])

    def test_id(self):
        self.assertEqual("link", self.link.id)

    def test_url(self):
        self.assertEqual(
            "http://localhost:55001/plone/folder/link",
            self.link.absolute_url(),
        )

    def test_parent(self):
        from Acquisition import aq_parent

        self.assertTrue(self.link.__parent__ == self.folder)
        self.assertTrue(aq_parent(self.link) == self.folder)
