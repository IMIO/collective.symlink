# -*- coding: utf-8 -*-

from Acquisition import aq_base, aq_inner, aq_parent
from collective.symlink import _
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.content import Container
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from zope.interface import implements

import types

_marker = object()


class ISymlink(model.Schema):
    symbolic_link = RelationChoice(
        title=_(u"Symbolic link"), source=ObjPathSourceBinder(), required=True
    )


class Symlink(Container):
    implements(ISymlink)

    cmf_uid = None

    def __call__(self):
        template = self._link.unrestrictedTraverse(self._link.getLayout())
        template.context = self
        return template()

    def Title(self):
        """Delegated title
        """
        link = self._link
        if link is not None:
            return aq_inner(link).Title()

    @property
    def _link(self):
        if 'symbolic_link' not in self.__dict__:
            return None
        return self.__getattribute__('symbolic_link').to_object

    def __getattr__(self, key):
        # Inspired by collective.alias
        if (
            key.startswith("_v_")
            or key.startswith("_p_")
            or key.endswith("_Permission")
        ):
            raise AttributeError(key)

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


class SymlinkView(DefaultView):
    def __call__(self):
        return self.context()
