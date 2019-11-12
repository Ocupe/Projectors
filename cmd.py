import fire
import os
from pathlib import Path
import subprocess
from loguru import logger as log
import tempfile
from distutils.dir_util import copy_tree
from typing import Dict

blender_versions_dir = Path('/Applications/Blender Versions/')


def blender_binaries(directory: Path) -> Dict:
    """Return the name of the Blender .app and the path to the blender binary inside the .app directory."""
    assert directory.is_dir()
    app_binaries = {}
    for app in directory.glob('Blender*.app'):
        log.debug(f'found {app.name}')
        binary = app / 'Contents/MacOS/blender'
        if binary.exists():
            app_binaries[app.name] = binary
        else:
            log.error(f'Binary does not exist: {binary}')

    else:
        return app_binaries


class CMD(object):
    def test(self, versions_dir=None):
        """ This function allows running the test suite agains different version of Blender.
        !!MacOS only!!
        """
        versions_dir = versions_dir if versions_dir else blender_versions_dir
        binaries = blender_binaries(versions_dir)

        # 1) Mimic the Blender User Script directory.
        # 2) Copy the addon into the temporally created structure.
        # 3) Use the BLENDER_USER_SCRIPTS environment variable to point Blender to the created scripts directory.
        with tempfile.TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)
            addon_dir = tempdir / 'scripts' / 'addons' / 'Projectors'
            addon_dir.mkdir(parents=True)
            scripts_dir = addon_dir.parent.parent
            # Copy addon into temp dir.
            copy_tree(str(Path(__file__).parent), str(addon_dir))

            # Set the environment variable to the temp scripts dir.
            os.environ['BLENDER_USER_SCRIPTS'] = str(scripts_dir)
            log.debug(
                f'BLENDER_USER_SCRIPTS: {os.environ.get("BLENDER_USER_SCRIPTS")}')

            # Run the tests against all Blender versions.
            for name, path in binaries.items():
                print('\n'*3)
                log.info(f'Testing against: {name}')
                print('=='*50)
                subprocess.run([str(path.resolve()), '--addons',
                                'Projectors', '--factory-startup', '-noaudio', '-b', '-P', 'tests.py'])

        log.debug(f'Temp dir { tempdir } was deleted: {not tempdir.exists()}')

        return 'Finished Testing'


if __name__ == '__main__':
    fire.Fire(CMD)
