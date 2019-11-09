BLENDER = /Applications/Blender.app/Contents/MacOS/Blender
BLENDER_VERSIONS_DIR = "/Applications/Blender Versions/"
BLENDER_2_80 = $(BLENDER_VERSIONS_DIR)"Blender 2.80.app/Contents/MacOS/Blender"
BLENDER_2_81 = $(BLENDER_VERSIONS_DIR)"Blender 2.81 beta.app/Contents/MacOS/Blender"
BLENDER_2_82 = $(BLENDER_VERSIONS_DIR)"Blender 2.82 alpha.app/Contents/MacOS/Blender"

APP_SUPPORT = Users/Jonas/Library/Application\ Support/Blender/
APP_SUPPORT_END = /scripts/addons/Projectors/


build:
	# Build the Blender addon.
	rm Projectors.zip
	find *.py -print | zip Projectors -@
	zip Projectors . -xi README.md LICENSE
	

sync:
	# Sync the addon on the different Blender versions.
	rsync --delete ../Projectors/ ~/Library/Application\ Support/Blender/2.80/scripts/addons/Projectors/
	rsync --delete ../Projectors/ ~/Library/Application\ Support/Blender/2.81/scripts/addons/Projectors/

test: sync
	# Run the test suite with multiple versions of Blender.
	echo "\n\n\n\n\n"
	echo "======================= START 2.80 ================================="
	$(BLENDER_2_80) --addons Projectors --factory-startup -noaudio -b -P tests.py
	echo "======================= END 2.80 ================================="

	echo "\n\n\n\n\n"
	echo "======================= START 2.81 ================================="
	$(BLENDER_2_81) --addons Projectors --factory-startup -noaudio -b -P tests.py
	echo "======================= END 2.81 ================================="
	echo "\n\n\n\n\n"