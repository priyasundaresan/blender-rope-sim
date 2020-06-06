# blender-rope-sim

### Description
* This repo provides a lightweight simulator for rope using Blender 2.8X. It is intended to provide a simulation environment for downstream robotics tasks with rope (knot-tying, untangling, etc.), and models things like self-collision and knots while providing a realistic rope appearance with flexibility for customization.
  * `rigidbody-rope.py`: basic API for modelling a rope as a set of capsules connected with rigid body constraints
  * `rigidbody_params.json`: hyperparameters for our rope
  * `knots.py`: a set of trajectories for tying knots with our rope API
  * `render.py`: a script for rendering the rope in different knotted conigurations, taking actions on the rope, and exporting ground truth data (RGB images, depth images, segmentation masks, and pixelwise-annotations)
  * `vis.py`: visualizes annotations on rendered images and dumps them into `annotated`
  * `data`: contains the relevant capsule mesh for modelling the rope; can be updated later with other relevant meshes, textures, etc. to model more varieties of rope
  
### Dependencies
All in Python3:
* Blender (2.80) (Download here: https://www.blender.org/download/Blender2.80/blender-2.80-macOS.dmg/)
  * NOTE: Blender comes bundled with its own version of Python (different from your system Python). The script render.py uses `sklearn` so you will need to install that within Blender's Python. See 'Setup' below for instructions.
* cv2
* numpy
  
### Example Renderings
<p float="left">
 <img src="https://github.com/priyasundaresan/blender-rope-sim/blob/master/images/000010_rgb.png" height="200">
 <img src="https://github.com/priyasundaresan/blender-rope-sim/blob/master/images/000015_rgb.png" height="200">
 <img src="https://github.com/priyasundaresan/blender-rope-sim/blob/master/images/000020_rgb.png" height="200">
</p>

<p float="left">
 <img src="https://github.com/priyasundaresan/blender-rope-sim/blob/master/annotated/000003_annotated.png" height="200">
 <img src="https://github.com/priyasundaresan/blender-rope-sim/blob/master/annotated/000005_annotated.png" height="200">
 <img src="https://github.com/priyasundaresan/blender-rope-sim/blob/master/annotated/000009_annotated.png" height="200">
</p>

### Setup
* After downloading Blender version 2.8X, do the following steps:
* Add the following line to your .bashrc: 
  * `alias blender="/path/to/blender/blender.app/Contents/MacOS/blender"` replacing the path to blender.app with your downloaded version
* `cd` into the following directory: `/path/to/blender/blender.app/Contents/Resources/2.80/python/bin`
 * Note that your path might look like `/Applications/Blender.app/Contents/Resources/2.82/python/bin` or `$HOME/Downloads/blender-2.80-197661c7334d-linux-glibc224-x86_64/2.80/python/bin` on Linux
* Once here, you will either see `pip` listed or `python3.7m`
* Install any dependencies (only `scikit-learn` for this repository) with `./pip install X` if `pip` is listed in the current directory or `./python3.7m pip install X` if `python3.7m` is listed

### Rendering Usage
* Off-screen rendering: run `blender -b -P render.py` (`-b` signals that the process will run in the background (doesn't launch the Blender app), `-P` signals that you're running a Python script)
* On-screen rendering: run `blender -P render.py` (launches the Blender app once the script executes)

### Debugging/Development
* Bugs will most likely be caused by Blender version compatibility; note that this codebase is developed for Blender 2.8X, so no guarantees about 2.7X
* First thing to check is stdout if you're running `blender -P <script>`; (you won't see any output in the Blender app itself). If the error is about an API call, ensure that you're using Blender 2.8X (& if you're trying to make it forward or backward compatible, you may need to swap the call that errors with the version-compatible API call - check the Blender changelog)
* For adding new rope features, it is almost always easiest to manually play around directly with meshes and objects in the Blender app. Once you get the desired functionality through manually playing around with it, head to the `Scripting` tab and it would have logged the corresponding API calls for everything you did (which you can directly use for scripting the functionality)
* For implementing new things, YouTube Blender tutorials are incredible! Even if they're manual, you can always port the functionality to a script by copying the steps and then converting them to script form by looking at the `Scripting` tab

### Getting Started/Overview
#### Example of tying knots with our rope:
* Run `blender -P knots.py`; it will launch the Blender app, then set the playback to the beginning and hit space bar to show the trajectory of how the knot is tied
#### Example of off-screen rendering/data generation:
* Run `blender -b -P render.py` to produce renderings of the rope in different states
* Run `python make_vids.py` which will create a video called `output.mp4` visualizing your renderings and the ground truth info; (alternatively run `python mask.py` and `python vis.py` separately)
* Use the images (/images), annotations (/images/knots_info.json), and segmentation masks (/image_masks) as training data for your project
