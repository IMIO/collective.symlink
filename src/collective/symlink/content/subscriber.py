# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def clear_caches(obj, event):
    """If the link is modified, clear the _v_ attribute caches"""
    obj._v__providedBy__ = None


def element_modified(obj, event):
    elements = []
    link_objects = []
    for obj in iterate_until_root(obj):
        elements.append(obj.id)
        intids = getUtility(IIntIds)
        to_id = intids.queryId(obj)
        if to_id:
            catalog = getUtility(ICatalog)
            links = catalog.findRelations(
                {"to_id": to_id, "from_attribute": "symbolic_link"}
            )
            for link in links:
                link_objects.append(link.from_object)
            if link_objects:
                # We found a link we do not want to iterate over link parents
                break
    elements = elements[:-1]
    reindex_symlink(link_objects, elements)


def reindex_symlink(link_objects, elements):
    if not link_objects:
        return
    to_reindex = []
    if not elements:
        to_reindex.extend(link_objects)
    else:
        for link_object in link_objects:
            idx = 0
            sub_object = link_object
            while idx < len(elements):
                sub_object = getattr(sub_object, elements[idx])
                idx += 1
            to_reindex.append(sub_object)
    for obj in to_reindex:
        obj.reindexObject()


def iterate_until_root(obj):
    """ Iterate over object parents until reaching the Plone Site Root object """
    result = [obj]
    obj = aq_parent(obj)
    while obj and not IPloneSiteRoot.providedBy(obj):
        result.append(obj)
        obj = aq_parent(obj)
    return result
