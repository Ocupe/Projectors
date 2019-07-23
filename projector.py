import logging
import math
import os

import bpy
from bpy.types import Operator

from .helper import (ADDON_ID, auto_offset,
                     get_projectors, random_color)

log = logging.getLogger(name=__file__)


resolutions = [
    # 16:10 aspect ratio
    ('1280x800', 'WXGA (1280x800) 16:10', '', 1),
    ('1440x900', 'WXGA+ (1440x900) 16:10', '', 2),
    ('1920x1200', 'WUXGA (1920x1200) 16:10', '', 3),
    # 16:9 aspect ratio
    ('1280x720', '720p (1280x720) 16:9', '', 4),
    ('1920x1080', '1080p (1920x1080) 16:9', '', 5),
    ('3840x2160', '4K Ultra HD (3840x2160) 16:9', '', 6),
    # 4:3 aspect ratio
    ('800x600', 'SVGA (800x600) 4:3', '', 7),
    ('1024x768', 'XGA (1024x768) 4:3', '', 8),
    ('1400x1050', 'SXGA+ (1400x1050) 4:3', '', 9),
    ('1600x1200', 'UXGA (1600x1200) 4:3', '', 10),
    # 17:9 aspect ratio
    ('4096x2160', 'Native 4K (4096x2160) 17:9', '', 11)
]


def change_texture_color(context, projector):
    projector.children[0].data.node_tree.nodes['Checker Texture'].inputs['Color2'].default_value = random_color()


class PROJECTOR_OT_change_color(Operator):
    """ Randomly change the color of the projected texture."""
    bl_idname = 'projector.change_color'
    bl_label = 'Change color of projection texture'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(get_projectors(context, only_selected=True))

    def execute(self, context):
        projectors = get_projectors(context, only_selected=True)
        for projector in projectors:
            change_texture_color(context, projector)
        return {'FINISHED'}


def create_projector_textures():
    """ This function checks if the needed images exist and if not creates them. """
    log.info('Adding new Images')
    name_template = '_proj.tex.{}'
    for res in resolutions:
        img_name = name_template.format(res[0])
        w, h = res[0].split('x')
        if not bpy.data.images.get(img_name):
            bpy.ops.image.new(name=img_name,
                              width=int(w),
                              height=int(h),
                              color=(0.0, 0.0, 0.0, 1.0),
                              alpha=True,
                              generated_type='COLOR_GRID',
                              float=False)

        bpy.data.images[img_name].use_fake_user = True


def add_projector_node_tree_to_spot(spot):
    """ 
    This function turns a spot light into a projector.
    This is achived through a texture on the spot light and some basic math. 
    """

    spot.data.use_nodes = True
    tree = spot.data.node_tree
    tree.nodes.clear()

    auto_pos = auto_offset()
    nodes = tree.nodes

    tex = nodes.new('ShaderNodeTexCoord')
    tex.location = auto_pos(200)

    map_1 = nodes.new('ShaderNodeMapping')
    map_1.vector_type = 'TEXTURE'
    # Flip the image horizontaly and verticaly to display it the intendet way.
    map_1.scale[0] = -1
    map_1.scale[1] = -1
    map_1.location = auto_pos(200)

    sep = nodes.new('ShaderNodeSeparateXYZ')
    sep.location = auto_pos(350)

    div_1 = nodes.new('ShaderNodeMath')
    div_1.operation = 'DIVIDE'
    div_1.name = ADDON_ID + 'div_01'
    div_1.location = auto_pos(200)

    div_2 = nodes.new('ShaderNodeMath')
    div_2.operation = 'DIVIDE'
    div_2.name = ADDON_ID + 'div_02'
    div_2.location = auto_pos(y=-200)

    com = nodes.new('ShaderNodeCombineXYZ')
    com.inputs['Z'].default_value = 1.0
    com.location = auto_pos(200)

    map_2 = nodes.new('ShaderNodeMapping')
    map_2.location = auto_pos(200)
    map_2.vector_type = 'TEXTURE'

    add = nodes.new('ShaderNodeMixRGB')
    add.blend_type = 'ADD'
    add.inputs[0].default_value = 1
    add.location = auto_pos(350)

    # Texturen
    # a) Image
    img = nodes.new('ShaderNodeTexImage')
    img.extension = 'CLIP'
    img.location = auto_pos(200)

    # b) Generated checker texture.
    checker_tex = nodes.new('ShaderNodeTexChecker')
    checker_tex.inputs['Color2'].default_value = random_color()
    checker_tex.inputs[3].default_value = 8
    checker_tex.location = auto_pos(y=-300)

    mix_rgb = nodes.new('ShaderNodeMixRGB')
    mix_rgb.inputs[1].default_value = (0, 0, 0, 0)
    mix_rgb.location = auto_pos(200, y=-300)

    # Emission
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Strength'].default_value = 1
    emission.location = auto_pos(100)

    output = nodes.new('ShaderNodeOutputLight')
    output.location = auto_pos(200)

    # ### LINK NODES ###
    tree.links.new(tex.outputs['Normal'], map_1.inputs['Vector'])
    tree.links.new(map_1.outputs['Vector'], sep.inputs['Vector'])

    tree.links.new(sep.outputs[0], div_1.inputs[0])  # X -> value0
    tree.links.new(sep.outputs[2], div_1.inputs[1])  # Z -> value1
    tree.links.new(sep.outputs[1], div_2.inputs[0])  # Y -> value0
    tree.links.new(sep.outputs[2], div_2.inputs[1])  # Z -> value1

    tree.links.new(div_1.outputs[0], com.inputs[0])
    tree.links.new(div_2.outputs[0], com.inputs[1])

    tree.links.new(com.outputs['Vector'], map_2.inputs['Vector'])

    # Textures
    # a)
    tree.links.new(map_2.outputs['Vector'], add.inputs['Color1'])
    tree.links.new(add.outputs['Color'], img.inputs['Vector'])
    # b)
    tree.links.new(map_2.outputs['Vector'], checker_tex.inputs['Vector'])
    tree.links.new(img.outputs['Alpha'], mix_rgb.inputs[0])
    tree.links.new(checker_tex.outputs['Color'], mix_rgb.inputs[2])

    tree.links.new(img.outputs['Color'], emission.inputs['Color'])
    tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])


def update_throw_ratio(projector):
    """
    Addust some settings on a camera to achive a throw ratio 
    """
    throw_ratio = projector.get('throw_ratio')
    distance = 1
    alpha = math.atan((distance/throw_ratio)*.5) * 2
    projector.data.lens_unit = 'FOV'
    projector.data.angle = alpha
    projector.data.sensor_width = 10
    projector.data.display_size = 1


def update_lens_shift(projector):
    """
    Apply the shift to the camera and texture.
    """
    h_shift = projector.get('h_shift')
    v_shift = projector.get('v_shift')
    throw_ratio = projector.get('throw_ratio')

    # Update the properties of the camera.
    cam = projector
    cam.data.shift_x = h_shift
    cam.data.shift_y = v_shift

    # Update the properties of the spotlight.
    spot = projector.children[0]
    spot.data.node_tree.nodes['Mapping.001'].translation[0] = h_shift / throw_ratio
    spot.data.node_tree.nodes['Mapping.001'].translation[1] = v_shift / throw_ratio


def update_projector(projector, context):
    """ This function is called to update the projector.
    It gets the properties stored on the camera obj to update the projector.
    """
    # Update throw ratio
    throw = projector.get("throw_ratio")
    update_throw_ratio(projector)

    # Adujust Texture to fit new camera ###
    w, h = projector.resolution.split('x')
    w = int(w)
    h = int(h)
    aspect_ratio = w/h
    inverted_aspect_ratio = 1/aspect_ratio

    try:
        if projector.use_img_texture:
            change_projector_output(True, projector)
        else:
            change_projector_output(False, projector)
    except Exception as e:
        log.warning(
            'Projector: {} has a problem rebuilding the node_tree of spot. {}'.format(projector.name, e))
        add_projector_node_tree_to_spot(projector.children[0])

    spot = projector.children[0]
    spot.data.node_tree.nodes['Mapping.001'].scale[0] = 1 / \
        throw
    spot.data.node_tree.nodes['Mapping.001'].scale[1] = 1 / \
        throw * inverted_aspect_ratio

    # Change image texture
    spot.data.node_tree.nodes['Image Texture'].image = bpy.data.images['_proj.tex.{}'.format(
        projector.resolution)]

    # Update light power
    spot.data.energy = projector["projector_power"]

    # Update Lens Shift
    update_lens_shift(projector)


def create_projector(context):
    """ 
    Create a new projector composed out of a camera (parent obj) and a spotlight (child not intndet for user interaction). 
    The camera is the object intendet for the user to manipulate and custom properties are stored there.
    The spotlight with a custom nodetree is responsible for actual projection of the texture. 
    """
    create_projector_textures()

    # Create a camera and a spotlight
    # ### Spot Light ###
    bpy.ops.object.light_add(type='SPOT', location=(0, 0, 0))
    spot = context.object
    spot.name = 'Projector.Spot'
    spot.scale = (.01, .01, .01)
    spot.data.spot_size = math.pi
    spot.data.spot_blend = 0
    spot.data.shadow_soft_size = 0.00000001
    spot.hide_select = True
    spot[ADDON_ID.format('spot')] = True
    spot.data.cycles.use_multiple_importance_sampling = False
    add_projector_node_tree_to_spot(spot)

    # ### Camera ###
    bpy.ops.object.camera_add(enter_editmode=False,
                              location=(0, 0, 0), rotation=(0, 0, 0))
    cam = context.object
    cam.name = 'Projector'

    # Add custom properties to store projector settings on the camera obj.
    cam['throw_ratio'] = 0.8
    cam['projector_power'] = 500.0
    cam['use_img_texture'] = False
    cam['h_shift'] = 0.0
    cam['v_shift'] = 0.0

    update_throw_ratio(cam)

    # Parent light to cam.
    spot.parent = cam

    # Move newly create projector (cam and spotlight) to 3D cursor position.
    cam.location = context.scene.cursor.location
    cam.rotation_euler = context.scene.cursor.rotation_euler

    return cam


class PROJECTOR_OT_create(Operator):
    """ Create Projector """
    bl_idname = 'projector.create'
    bl_label = 'Create a new Projector'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        projector = create_projector(context)
        update_projector(projector, context)
        return {'FINISHED'}


def change_projector_output(use_img, projector):
    """ Toggle between image and generated checker texture. """
    tree = projector.children[0].data.node_tree
    img_node = tree.nodes['Image Texture']
    mix_node = tree.nodes['Mix.001']
    emission_node = tree.nodes['Emission']

    if use_img:
        tree.links.new(
            img_node.outputs['Color'], emission_node.inputs['Color'])
    else:
        tree.links.new(
            mix_node.outputs['Color'], emission_node.inputs['Color'])


class PROJECTOR_OT_delete(Operator):
    bl_idname = 'projector.delete'
    bl_label = 'Delete Projector'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(get_projectors(context, only_selected=True))

    def execute(self, context):
        selected_projectors = get_projectors(context, only_selected=True)
        for projector in selected_projectors:
            for child in projector.children:
                bpy.data.objects.remove(child, do_unlink=True)
            else:
                bpy.data.objects.remove(projector, do_unlink=True)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(PROJECTOR_OT_create)
    bpy.utils.register_class(PROJECTOR_OT_delete)
    bpy.utils.register_class(PROJECTOR_OT_change_color)

    bpy.types.Object.throw_ratio = bpy.props.FloatProperty(
        name="Throw Ratio", min=0.01, max=10, update=update_projector)
    bpy.types.Object.projector_power = bpy.props.FloatProperty(
        name="Projector Power", min=0, max=999999, update=update_projector)
    bpy.types.Object.use_img_texture = bpy.props.BoolProperty(
        name="Use Img Texture", update=update_projector)
    bpy.types.Object.resolution = bpy.props.EnumProperty(
        items=resolutions, default='1920x1080', description="Select a Resolution for your projector", update=update_projector)
    
    shift_limit = 5
    bpy.types.Object.h_shift = bpy.props.FloatProperty(
        name="Horizontal Shift", min=-shift_limit, max=shift_limit, update=update_projector)
    bpy.types.Object.v_shift = bpy.props.FloatProperty(
        name="Vertical Shift", min=-shift_limit, max=shift_limit, update=update_projector)


def unregister():
    bpy.utils.unregister_class(PROJECTOR_OT_change_color)
    bpy.utils.unregister_class(PROJECTOR_OT_delete)
    bpy.utils.unregister_class(PROJECTOR_OT_create)
