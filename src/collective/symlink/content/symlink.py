# -*- coding: utf-8 -*-

from Acquisition import aq_base, aq_inner, aq_parent
from collective.symlink import _
from plone.app.iterate.interfaces import IIterateAware
from plone.app.layout.globals.context import ContextState
from plone.app.versioningbehavior.behaviors import IVersioningSupport
from plone.dexterity.browser import edit
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.content import Container
from plone.folder.ordered import CMFOrderedBTreeFolderBase
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from plone.uuid.interfaces import IAttributeUUID
from plone.uuid.interfaces import IUUIDAware
from z3c.relationfield.schema import RelationChoice
from zope.component import ComponentLookupError
from zope.interface import implementer
from zope.interface.declarations import ObjectSpecificationDescriptor
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import implementedBy
from zope.interface.declarations import providedBy
from zope.intid.interfaces import IIntIds

import types

_marker = object()


class ISymlink(model.Schema):
    symbolic_link = RelationChoice(
        title=_(u"Symbolic link"), source=ObjPathSourceBinder(), required=True
    )


class DelegatingSpecification(ObjectSpecificationDescriptor):
    """
    Get from collective.alias
    A __providedBy__ decorator that returns the interfaces provided by
    the object, plus those of the cached object.
    """

    def __get__(self, inst, cls=None):
        # We're looking at a class - fall back on default
        if inst is None:
            return getObjectSpecification(cls)

        # Find the cached value.
        cache = getattr(inst, "_v__providedBy__", None)

        # Find the data we need to know if our cache needs to be invalidated
        provided = link_provides = getattr(inst, "__provides__", None)

        # See if we have a valid cache, and if so return it
        if cache is not None:
            cached_mtime, cached_provides, cached_provided = cache

            if inst._p_mtime == cached_mtime and link_provides is cached_provides:
                return cached_provided

        # If the instance doesn't have a __provides__ attribute, get the
        # interfaces implied by the class as a starting point.
        if provided is None:
            provided = implementedBy(cls)

        # Add the interfaces provided by the target
        link = aq_base(inst._link)
        if link is None:
            return provided - IIterateAware - IVersioningSupport  # don't cache yet!

        # Add the interfaces provided by the target, but ensure that some problematic
        # interfaces are removed
        provided += providedBy(link) - IIterateAware - IVersioningSupport

        inst._v__providedBy__ = inst._p_mtime, link_provides, provided
        return provided


@implementer(ISymlink, IUUIDAware, IAttributeUUID)
class Symlink(Container):

    cmf_uid = None
    cb_dataValid = False  # This hide the paste button
    _link_portal_type = None
    __providedBy__ = DelegatingSpecification()

    def __call__(self):
        template = self._link.unrestrictedTraverse(self._link.getLayout())
        template.context = self
        return template()

    def Title(self):
        link = self._link
        if link is not None:
            return aq_inner(link).Title()

    def Description(self):
        link = self._link
        if link is not None:
            return aq_inner(link).Description()

    @property
    def portal_type(self):
        link = self._link
        if self._link is None:
            return self.__getattribute__("_link_portal_type")
        return aq_inner(link).portal_type

    @portal_type.setter
    def portal_type(self, value):
        self._link_portal_type = value

    @property
    def workflow_history(self):
        link = self._link
        if self._link is None:
            return None
        return aq_inner(link).workflow_history

    @workflow_history.setter
    def workflow_history(self, value):
        return

    @workflow_history.deleter
    def workflow_history(self):
        return

    def allowedContentTypes(self):
        return []

    @property
    def _link(self):
        if "symbolic_link" not in self.__dict__:
            return None
        try:
            return self.__getattribute__("symbolic_link").to_object
        except ComponentLookupError as e:
            if getattr(e, "args", [""])[0] == IIntIds:
                return  # This happen when we try to remove the Plone object
            raise e

    def __getattr__(self, key):
        # Inspired by collective.alias
        if (
            key.startswith("_v_")
            or key.startswith("_p_")
            or key.endswith("_Permission")
        ):
            raise AttributeError(key)

        if key == "_plone.uuid":
            return super(Symlink, self).__getattr__(key)

        link = self._link
        if link is None:
            return super(Symlink, self).__getattr__(key)

        link = aq_inner(link)

        if not hasattr(aq_base(link), key):
            return super(Symlink, self).__getattr__(key)

        link_attr = getattr(link, key, _marker)

        if link_attr is _marker:
            return super(Symlink, self).__getattr__(key)

        # if this is an acquisition wrapped object, re-wrap it in the alias
        if aq_parent(link_attr) is link:
            link_attr = aq_base(link_attr).__of__(self)

        # if it is a bound method, re-bind it so that im_self is the alias
        if isinstance(link_attr, types.MethodType):
            return types.MethodType(link_attr.im_func, self, type(self))

        return link_attr

    # Inspired by collective.alias
    def _getOb(self, id, default=_marker):
        link = self._link
        if link is not None:
            obj = link._getOb(id, default)
            if obj is default:
                if default is _marker:
                    raise KeyError(id)
                return default
            return aq_base(obj).__of__(self)
        return CMFOrderedBTreeFolderBase._getOb(self, id, default)

    def objectIds(self, spec=None, ordered=True):
        link = self._link
        if link is not None:
            return link.objectIds(spec)
        return CMFOrderedBTreeFolderBase.objectIds(self, spec, ordered)

    def __getitem__(self, key):
        link = self._link
        if link is not None:
            return link.__getitem__(key)
        return CMFOrderedBTreeFolderBase.__getitem__(self, key)


class SymlinkView(DefaultView):
    def __call__(self):
        return self.context()


class EditForm(edit.DefaultEditForm):
    @property
    def portal_type(self):
        return self.context._link_portal_type

    @portal_type.setter
    def portal_type(self, value):
        return  # Avoid override during update in plone.dexterity.browser.edit

    @property
    def additionalSchemata(self):
        return []


class SymlinkContextState(ContextState):
    def workflow_state(self):
        return None


def clear_caches(obj, event):
    """If the link is modified, clear the _v_ attribute caches"""
    obj._v__providedBy__ = None
