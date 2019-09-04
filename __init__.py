import os
import logging
import math
import os
import bpy
from . import ui
from . import projector
from . import operators
from . import tests

bl_info = {
    "name": "Projector",
    "author": "Jonas Schell",
    "description": "Easy Projector creation and modification.",
    "blender": (2, 80, 0),
    "version": (0, 2, 0),
    "location": "3D Viewport > Add > Light > Projector",
    "category": "Lighting",
    "wiki_url": "https://github.com/Ocupe/Projectors/wiki",
    "tracker_url": "https://github.com/Ocupe/Projectors/issues"
}

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s %(levelname)8s %(name)s %(message)s')
log = logging.getLogger(__name__)


def register():
    projector.register()
    operators.register()
    ui.register()
    tests.register()


def unregister():
    tests.unregister()
    ui.unregister()
    operators.unregister()
    projector.unregister()
