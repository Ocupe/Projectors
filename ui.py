from .helper import get_projectors
from .projector import resolutions

import bpy
from bpy.types import Panel, PropertyGroup, UIList, Operator


class PROJECTOR_PT_projector_settings(Panel):
    bl_idname = 'OBJECT_PT_projector_n_panel'
    bl_label = 'Projector'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Projector"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.operator('projector.create',
                     icon='ADD', text="New")
        row.operator('projector.delete',
                     text='Remove', icon='REMOVE')

        if context.scene.render.engine == 'BLENDER_EEVEE':
            box = layout.box()
            box.label(text='Image Projection only works in Cycles.', icon='ERROR')
            box.operator('projector.switch_to_cycles')

        selected_projectors = get_projectors(context, only_selected=True)
        if len(selected_projectors) == 1:
            projector = selected_projectors[0]

            layout.separator()

            layout.label(text='Projector Settings:')
            box = layout.box()
            box.prop(projector.proj_settings, 'throw_ratio')
            box.prop(projector.proj_settings, 'power', text='Power')
            box.prop(projector.proj_settings, 'resolution',
                     text='Resolution', icon='PRESET')
            # Lens Shift
            col = box.column(align=True)
            col.prop(projector.proj_settings,
                     'h_shift', text='Horizontal Shift')
            col.prop(projector.proj_settings, 'v_shift', text='Vertical Shift')
            layout.prop(projector.proj_settings,
                        'projected_texture', text='Project')

            # Custom Texture
            if projector.proj_settings.projected_texture == 'user_texture':
                box = layout.box()
                node = get_projectors(context, only_selected=True)[
                    0].children[0].data.node_tree.nodes['Image Texture']
                box.template_image(node, 'image', node.image_user)


class PROJECTOR_PT_projected_color(Panel):
    bl_label = "Projected Color"
    bl_parent_id = "OBJECT_PT_projector_n_panel"
    bl_option = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self, context):
        """ Only show if projected texture is set to  'checker'."""
        projector = context.object
        return bool(get_projectors(context, only_selected=True)) and projector.proj_settings.projected_texture == 'checker_texture'

    def draw(self, context):
        projector = context.object
        layout = self.layout
        layout.use_property_decorate = False
        col = layout.column()
        col.use_property_split = True
        col.prop(projector.proj_settings, 'projected_color', text='Color')
        col.operator('projector.change_color',
                     icon='MODIFIER_ON', text='Random Color')


def append_to_add_menu(self, context):
    self.layout.operator('projector.create',
                         text='Projector', icon='CAMERA_DATA')


def register():
    bpy.utils.register_class(PROJECTOR_PT_projector_settings)
    bpy.utils.register_class(PROJECTOR_PT_projected_color)
    # Register create  in the blender add menu.
    bpy.types.VIEW3D_MT_light_add.append(append_to_add_menu)


def unregister():
    # Register create in the blender add menu.
    bpy.types.VIEW3D_MT_light_add.remove(append_to_add_menu)
    bpy.utils.unregister_class(PROJECTOR_PT_projected_color)
    bpy.utils.unregister_class(PROJECTOR_PT_projector_settings)
