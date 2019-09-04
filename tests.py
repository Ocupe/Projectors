import unittest
import bpy
from bpy.app.handlers import persistent

class TestProjector(unittest.TestCase):
    def setUp(self):
        pass

    def test_projector_creation(self):
        self.assertEqual(1,2)

    def tearDown(self):
        pass

# ########### Test Setup ########## 
def runTests():
    print("\n" * 2)
    print("Start running the Projectors Addon test suite.")

    testLoader = unittest.TestLoader()
    testLoader.testMethodPrefix = "test" # <- change to only run selected tests
    all_tests = testLoader.discover(".", pattern="test*")
    unittest.TextTestRunner(verbosity=1).run(all_tests)

    print("\n" * 2)


addon_changed = False


@persistent
def scene_updated_post(scene):
    global addon_changed
    if addon_changed:
        addon_changed = False
        runTests()


def register():
    bpy.app.handlers.depsgraph_update_post.append(scene_updated_post)
    global addon_changed
    addon_changed = True


def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(scene_updated_post)
