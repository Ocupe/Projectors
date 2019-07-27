import os
import logging
import math
import os
import bpy
from . import ui
from . import projector
from . import operators

bl_info = {
    "version": (0.1.0),
    "name": "Projector",
    "author": "Jonas Schell",
    "description": "Easy Projector creation and modification.",
    "blender": (2, 80, 0),
    "location": "3D Viewport > Add > Light > Projector",
    "category": "Lighting",
    "wiki_url":    "https://github.com/Ocupe/Projectors",
    "tracker_url": "https://github.com/Ocupe/Projectors/issues",

}

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s %(levelname)8s %(name)s %(message)s')
log = logging.getLogger(__name__)


def register():
    projector.register()
    operators.register()
    ui.register()


def unregister():
    ui.unregister()
    operators.unregister()
    projector.unregister()
