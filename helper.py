# Standard Lib imports
import logging
from random import uniform, random, uniform

# Blender imports
import bpy
import colorsys

log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s %(levelname)8s %(name)s %(message)s')

FALLBACK_WARNING = 'Falling back to pre 2.8 Blender Python API: {}'
ADDON_ID = 'protor_{}'


def random_color(alpha=False):
    """ Return a high contrast random color. """
    h = random()
    s = 1
    v = 1
    rgb = list(colorsys.hsv_to_rgb(h, s, v))
    if alpha:
        rgb.append(1)
    return rgb


def get_projectors(context, only_selected=False):
    """ Get all or only the selected projectors from the scene. """
    objs = context.selected_objects if only_selected else context.scene.objects
    projectors = []
    for obj in objs:
        if obj.type == 'CAMERA' and obj.name.startswith('Projector'):
            if only_selected:
                if obj.select_get():
                    projectors.append(obj)
            else:
                projectors.append(obj)
    return projectors


def get_projector(context):
    """ Return selected Projector or None if no projector is selected. """
    projectors = get_projectors(context, only_selected=True)
    if len(projectors) == 1:
        return projectors[0]
    else:
        return None


def auto_offset():
    offset = 0

    def inner(node_width=None, y=None, gap=None):
        nonlocal offset
        offset += node_width if node_width else 0
        y = y if y else 0
        gap = gap if gap else 60
        offset += gap
        return offset, y
    return inner
