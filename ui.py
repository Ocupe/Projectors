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

        if context.scene.render.engine == 'BLENDER_EEVEE':
            box = self.layout.box()
            box.label(text='Image Projection only works in Cycles.', icon='ERROR')
            box.operator('projector.switch_to_cycles')

        selected_projectors = get_projectors(context, only_selected=True)
        if len(selected_projectors) == 1:
            projector = selected_projectors[0]

            self.layout.label(text='Projector Settings:')
            box = self.layout.box()
            box.prop(projector.proj_settings, 'throw_ratio')
            box.prop(projector.proj_settings, 'power', text='Power')
            box.prop(projector.proj_settings, 'resolution',
                     text='Resolution', icon='PRESET')
            # Lens Shift
            col = box.column(align=True)
            col.prop(projector.proj_settings,
                     'h_shift', text='Horizontal Shift')
            col.prop(projector.proj_settings, 'v_shift', text='Vertical Shift')
            # Projected Texture
            box.prop(projector.proj_settings, 'use_img_texture',
                     text='Use Image Texture')
            if not projector.proj_settings.use_img_texture:
                box.operator('projector.change_color',
                             icon='MODIFIER_ON', text='Random Color')


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
