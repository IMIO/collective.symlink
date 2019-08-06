# -*- coding: utf-8 -*-

from collective.symlink import _
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.content import Container
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from zope.interface import implements


class ISymlink(model.Schema):
    symbolic_link = RelationChoice(
        title=_(u"Symbolic link"), source=ObjPathSourceBinder(), required=True
    )


class Symlink(Container):
    implements(ISymlink)

    def __call__(self):
        link_obj = self.symbolic_link.to_object
        template = link_obj.unrestrictedTraverse(link_obj.getLayout())
        template.context = AdaptedContext(self)
        return template()


class AdaptedContext(object):
    _not_inherited_attrs = ("id", "absolute_url", "__parent__")

    def __init__(self, symlink):
        self._symlink = symlink
        self._original_object = symlink.symbolic_link.to_object

    def __getattr__(self, key):
        if key in self._not_inherited_attrs:
            return getattr(self._symlink, key)
        else:
            return getattr(self._original_object, key)


class SymlinkView(DefaultView):
    def __call__(self):
        return self.context()
