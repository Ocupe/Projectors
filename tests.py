import unittest
import bpy
from bpy.app.handlers import persistent
from bpy.types import Operator


class TestAddon(unittest.TestCase):
    def test_existenc_of_operators(self):
        pass


class TestProjector(unittest.TestCase):
    def setUp(self):
        bpy.ops.projector.create()
        self.c = bpy.context.object  # Camera
        self.s = self.c.children[0]  # Spot Light
        self.nodes = self.s.data.node_tree.nodes

    def test_correct_projector_creation(self):
        # Camera
        self.assertEqual(self.c.type, 'CAMERA')
        self.assertEqual(self.c.data.lens_unit, 'FOV')
        self.assertEqual(self.c.data.lens_unit, 'FOV')
        # Light
        self.assertEqual(self.c.children[0].type, 'LIGHT')
        self.assertEqual(self.c.children[0].data.type, 'SPOT')
        self.assertEqual(self.c.children[0].hide_select, True)
        self.assertAlmostEqual(self.c.children[0].data.shadow_soft_size, 0.0)
        self.assertAlmostEqual(
            self.c.children[0].data.cycles.use_multiple_importance_sampling, False)

    def test_existences_of_custom_properties(self):
        self.assertIn('proj_settings', self.c)
        self.assertIn('h_shift', self.c.proj_settings)
        self.assertIn('v_shift', self.c.proj_settings)
        self.assertIn('power', self.c.proj_settings)
        self.assertIn('projected_color', self.c.proj_settings)
        self.assertIn('projected_texture', self.c.proj_settings)
        self.assertIn('throw_ratio', self.c.proj_settings)
        self.assertIn('resolution', self.c.proj_settings)
        self.assertIn('use_custom_texture_res', self.c.proj_settings)

    def test_update_throw_ratio(self):
        self.c.proj_settings.throw_ratio = 1
        self.assertEqual(self.c.proj_settings.throw_ratio, 1)
        self.assertAlmostEqual(self.c.data.angle, 0.9272952180016123, places=6)
        # Test if mapping nodes was updated correctly
        mapping_node = self.s.data.node_tree.nodes['Group'].node_tree.nodes['Mapping.001']
        if bpy.app.version < (2, 81):
            self.assertEqual(mapping_node.scale[0], 1)
            self.assertAlmostEqual(mapping_node.scale[1], 0.5625)
        else:
            self.assertEqual(mapping_node.inputs['Scale'].default_value[0], 1)
            self.assertAlmostEqual(
                mapping_node.inputs['Scale'].default_value[1], 0.5625)
        # Test 2
        self.c.proj_settings.throw_ratio = 0.8
        self.assertAlmostEqual(self.c.proj_settings.throw_ratio, 0.8)
        self.assertAlmostEqual(self.c.data.angle, 1.1171986306871249, places=6)
        if bpy.app.version < (2, 81):
            self.assertEqual(mapping_node.scale[0], 1.250)
            self.assertAlmostEqual(mapping_node.scale[1], 0.703125)
        else:
            self.assertEqual(
                mapping_node.inputs['Scale'].default_value[0], 1.250)
            self.assertAlmostEqual(
                mapping_node.inputs['Scale'].default_value[1], 0.703125)

    def test_update_lens_shift(self):
        self.c.proj_settings.throw_ratio = 1
        shift = 10  # 10%
        # x shift
        self.c.proj_settings.h_shift = shift
        self.assertAlmostEqual(self.c.data.shift_x, 0.1)
        # y shift
        self.c.proj_settings.v_shift = shift
        self.assertAlmostEqual(self.c.data.shift_y, 0.1)
        # Check correct update of mapping node
        mapping_node = self.s.data.node_tree.nodes['Group'].node_tree.nodes['Mapping.001']
        if bpy.app.version < (2, 81):
            self.assertAlmostEqual(mapping_node.translation[0], 0.1)
            self.assertAlmostEqual(mapping_node.translation[1], 0.1)
        else:
            self.assertAlmostEqual(
                mapping_node.inputs['Location'].default_value[0], 0.1)
            self.assertAlmostEqual(
                mapping_node.inputs['Location'].default_value[1], 0.1)

    def test_pixel_gird_on_off(self):
        # Turn Pixel Grid on
        self.c.proj_settings.show_pixel_grid = True
        links_as_node_names = []
        for link in self.s.data.node_tree.links:
            links_as_node_names.append(
                (link.from_node.name, link.to_node.name))
        else:
            self.assertIn(('pixel_grid', 'Light Output'), links_as_node_names)
            self.assertNotIn(('Emission', 'Light Output'), links_as_node_names)
        # Turn Pixel Grid off
        self.c.proj_settings.show_pixel_grid = False
        links_as_node_names = []
        for link in self.s.data.node_tree.links:
            links_as_node_names.append(
                (link.from_node.name, link.to_node.name))
        else:
            self.assertNotIn(('pixel_grid', 'Light Output'),
                             links_as_node_names)
            self.assertIn(('Emission', 'Light Output'), links_as_node_names)

    def test_pixel_grid_resolution(self):
        nodes = self.s.data.node_tree.nodes['pixel_grid'].node_tree.nodes
        # Check Pixel Grid default resolution
        width, height = self.c.proj_settings.resolution.split('x')
        self.assertEqual(
            nodes['_width'].outputs[0].default_value, float(width))
        self.assertEqual(
            nodes['_height'].outputs[0].default_value, float(height))
        # Check Pixel Grid resolution update
        x, y = 1024, 768
        self.c.proj_settings.resolution = f'{x}x{y}'
        self.assertEqual(
            nodes['_width'].outputs[0].default_value, float(x))
        self.assertEqual(
            nodes['_height'].outputs[0].default_value, float(y))
        



    def test_update_power(self):
        new_power = 30
        self.c.proj_settings.power = new_power
        self.assertEqual(self.s.data.energy, new_power)

    def tearDown(self):
        bpy.ops.object.select_all(action='DESELECT')
        self.c.select_set(True)
        bpy.ops.projector.delete()


def run_tests():
    testLoader = unittest.TestLoader()
    testLoader.testMethodPrefix = "test"
    all_tests = testLoader.discover(".", pattern="test*")
    unittest.TextTestRunner(verbosity=1).run(all_tests)


if __name__ == "__main__":
    run_tests()
