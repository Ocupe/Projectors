from . import ui
from . import projector
from . import operators

bl_info = {
    "name": "Projector RC1",
    "author": "Jonas Schell",
    "description": "Easy Projector creation and modification.",
    "blender": (2, 81, 0),
    "version": (2024, 0, 0),
    "location": "3D Viewport > Add > Light > Projector",
    "category": "Lighting",
    "wiki_url": "https://github.com/Ocupe/Projectors/wiki",
    "tracker_url": "https://github.com/Ocupe/Projectors/issues"
}


def register():
    projector.register()
    operators.register()
    ui.register()


def unregister():
    ui.unregister()
    operators.unregister()
    projector.unregister()
