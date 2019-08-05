# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.utils import get_installer
from collective.symlink.testing import COLLECTIVE_SYMLINK_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.symlink is properly installed."""

    layer = COLLECTIVE_SYMLINK_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal, self.layer['request'])

    def test_product_installed(self):
        """Test if collective.symlink is installed."""
        self.assertTrue(self.installer.is_product_installed(
            'collective.symlink'))

    def test_browserlayer(self):
        """Test that ICollectiveSymlinkLayer is registered."""
        from collective.symlink.interfaces import (
            ICollectiveSymlinkLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectiveSymlinkLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_SYMLINK_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal, self.layer['request'])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstall_product('collective.symlink')
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.symlink is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'collective.symlink'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveSymlinkLayer is removed."""
        from collective.symlink.interfaces import \
            ICollectiveSymlinkLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            ICollectiveSymlinkLayer,
            utils.registered_layers())
