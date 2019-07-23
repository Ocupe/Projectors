from .helper import get_projectors
from .projector import resolutions

import bpy

from bpy.types import Panel, PropertyGroup, UIList, Operator
from bpy.props import StringProperty
import logging
log = logging.getLogger(__file__)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s %(levelname)8s %(name)s %(message)s')


class PROJECTOR_PT_panel(Panel):
    bl_idname = 'OBJECT_PT_projector_n_panel'
    bl_label = 'Projector'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Projector"

    def draw(self, context):

        self.layout.use_property_split = True

        row = self.layout.row(align=True)
        row.operator('projector.create',
                     icon='ADD', text="New")
        row.operator('projector.delete',
                     text='Remove', icon='REMOVE')

        selected_projectors = get_projectors(context, only_selected=True)
        if len(selected_projectors) == 1:
            projector = selected_projectors[0]

            self.layout.label(text='Projector Settings:')
            box = self.layout.box()
            box.prop(projector, 'throw_ratio')
            box.prop(projector, 'projector_power', text='Power')
            box.prop(projector, 'resolution', text='Resolution')
            box.prop(projector, 'use_img_texture', text='Use Image Texture')
            if not projector.use_img_texture:
                box.operator('projector.change_color',
                             icon='MODIFIER_ON', text='Random Color')
            row = box.row(align=True)
            row.label(text='Lens Shift')
            box.prop(projector, 'h_shift', text='Horizontal')
            box.prop(projector, 'v_shift', text='Vertical')
            


def add_to_blender_add_menu(self, context):
    self.layout.operator('projector.create',
                         text='Projector', icon='CAMERA_DATA')


def register():
    bpy.utils.register_class(PROJECTOR_PT_panel)
    # Register create  in the blender add menu.
    bpy.types.VIEW3D_MT_light_add.append(add_to_blender_add_menu)


def unregister():
    # Register create  in the blender add menu.
    bpy.types.VIEW3D_MT_light_add.remove(add_to_blender_add_menu)
    bpy.utils.unregister_class(PROJECTOR_PT_panel)
