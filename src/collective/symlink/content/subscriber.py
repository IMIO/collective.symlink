# -*- coding: utf-8 -*-

from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def clear_caches(obj, event):
    """If the link is modified, clear the _v_ attribute caches"""
    obj._v__providedBy__ = None


def element_modified(obj, event):
    intids = getUtility(IIntIds)
    to_id = intids.queryId(obj)
    if to_id:
        catalog = getUtility(ICatalog)
        links = catalog.findRelations(
            {"to_id": to_id, "from_attribute": "symbolic_link"}
        )
        for link in links:
            link.from_object.reindexObject()
