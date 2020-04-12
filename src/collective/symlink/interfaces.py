# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveSymlinkLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class ISymlinkable(Interface):
    """Marker interface that defines a content type who is allowable by a symlink."""
