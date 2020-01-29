# -*- coding: utf-8 -*-

from collective.symlink.testing import COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING
from collective.symlink.utils import is_linked_object
from plone import api
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield import RelationValue

import unittest


class TestSymlink(unittest.TestCase):
    layer = COLLECTIVE_SYMLINK_ACCEPTANCE_TESTING

    def tearDown(self):
        portal = api.portal.get()
        for e in ("link", "document"):
            if e in portal:
                api.content.delete(portal[e])

    def test_is_linked_object(self):
        portal = api.portal.get()
        intids = getUtility(IIntIds)
        folder = api.content.create(type="Folder", id="folder", container=portal)
        doc = api.content.create(type="Document", id="document", title="Title", description="Description",
                                 container=folder)
        link = api.content.create(type="symlink", id="link", symbolic_link=RelationValue(intids.getId(folder)),
                                  container=portal)
        self.assertTupleEqual(is_linked_object(doc), ('', None, None, ''))
        self.assertTupleEqual(is_linked_object(folder), ('', None, None, ''))
        self.assertTupleEqual(is_linked_object(link), ('symlink', link, folder, ''))
        self.assertTupleEqual(is_linked_object(link.document), ('symlink', link, folder, 'document'))
        self.assertTupleEqual(is_linked_object(link['document']), ('symlink', link, folder, 'document'))
