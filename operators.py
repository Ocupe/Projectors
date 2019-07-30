import bpy
from bpy.types import Operator


class PROJECTOR_OT_switch_to_cycles(Operator):
    """ Change the render engin to cycles. """
    bl_idname = 'projector.switch_to_cycles'
    bl_label = ' Change Render Engine to Cycles. '
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.render.engine = 'CYCLES'
        return {'FINISHED'}


def register():
    bpy.utils.register_class(PROJECTOR_OT_switch_to_cycles)


def unregister():
    bpy.utils.unregister_class(PROJECTOR_OT_switch_to_cycles)
