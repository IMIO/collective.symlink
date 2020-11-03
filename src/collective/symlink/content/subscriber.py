# -*- coding: utf-8 -*-
from collective.symlink.interfaces import ISymlinkSource

from collective.symlink.utils import query_links_to_object
from zope.interface import alsoProvides


def clear_caches(obj, event):
    """If the link is modified, clear the _v_ attribute caches"""
    obj._v__providedBy__ = None


def element_modified(obj, event):
    links = query_links_to_object(obj)
    for link in links:
        link.from_object.reindexObject()


def element_added(obj, event):
    source = obj._link  # noqa
    if not ISymlinkSource.providedBy(source):
        alsoProvides(source, ISymlinkSource)
