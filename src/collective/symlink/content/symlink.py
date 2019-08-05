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


class SymlinkView(DefaultView):
    pass
