# -*- coding: utf-8 -*-

from Acquisition import aq_inner  # noqa
from Acquisition import aq_parent  # noqa
from Products.CMFPlone.utils import base_hasattr


def is_linked_object(obj):
    """ Check if the obj is a symlink or is a child of a symlink.
    :param obj: obj to check
    :type obj: object
    :returns: tuple with link, symlink object, original object, relative_path
    """
    ret = ['', None, None, '']
    parent = obj
    while not parent.portal_type == 'Plone Site':
        if base_hasattr(parent, '_link_portal_type'):
            ret = [parent._link_portal_type, parent, parent._link, '']  # noqa
            if obj != parent:
                ret[3] = '/'.join(obj.getPhysicalPath()[len(parent.getPhysicalPath()):])
            break
        parent = aq_parent(aq_inner(parent))
    return tuple(ret)
