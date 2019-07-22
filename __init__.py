import os
import logging
import math
import os
import bpy
from . import ui
from . import projector

bl_info = {
    "name": "Projector",
    "author": "Jonas Schell",
    "description": "Easy Projector creation and modification.",
    "blender": (2, 80, 0),
    "location": "3D Viewport > Add > Light > Projector",
    "warning": "To see the projected image you have to use the Cycles renderer in rendered mode.",
    "category": "Lighting"
}

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s %(levelname)8s %(name)s %(message)s')
log = logging.getLogger(__name__)


def register():
    projector.register()
    ui.register()


def unregister():
    ui.unregister()
    projector.unregister()
