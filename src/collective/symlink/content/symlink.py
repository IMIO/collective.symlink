# -*- coding: utf-8 -*-

from plone.supermodel import model
from plone.dexterity.content import Container
from zope.interface import implements
from z3c.relationfield.schema import RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from collective.symlink import _


class ISymlink(model.Schema):
    symbolic_link = RelationChoice(
        title=_(u"Symbolic link"),
        source=ObjPathSourceBinder(),
        required=True,
    )


class Symlink(Container):
    implements(ISymlink)
