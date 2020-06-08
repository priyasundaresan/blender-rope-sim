import bpy
import numpy as np

from math import pi
import os
import sys
sys.path.append(os.getcwd())

from rigidbody_rope import *
from sklearn.neighbors import NearestNeighbors
import knots

def set_animation_settings(anim_end):
    # Sets up the animation cache to run till frame anim_end (otherwise default terminates @ 250)
    scene = bpy.context.scene
    scene.frame_end = anim_end
    scene.rigidbody_world.point_cache.frame_end = anim_end

def set_render_settings(engine, render_size):
    # Set rendering engine, dimensions, colorspace, images settings
    if not os.path.exists("./images"):
        os.makedirs('./images')
    else:
        os.system('rm -r ./images')
    if not os.path.exists("./images_depth"):
        os.makedirs('./images_depth')
    else:
        os.system('rm -r ./images_depth')
        os.makedirs('./images_depth')
    if not os.path.exists("./image_masks"):
        os.makedirs('./image_masks')
    else:
        os.system('rm -r ./image_masks')
        os.makedirs('./image_masks')
    scene = bpy.context.scene
    scene.render.engine = engine
    render_width, render_height = render_size
    scene.render.resolution_x = render_width
    scene.render.resolution_y = render_height
    if engine == 'BLENDER_WORKBENCH':
        scene.render.image_settings.color_mode = 'RGB'
        scene.display_settings.display_device = 'None'
        scene.sequencer_colorspace_settings.name = 'XYZ'
        scene.render.image_settings.file_format='PNG'
    elif engine == "BLENDER_EEVEE":
        scene.eevee.taa_samples = 1
        scene.view_settings.view_transform = 'Raw'
        scene.eevee.taa_render_samples = 1

def annotate(frame, mapping, num_annotations, knot_only=True, end_only=False, offset=1):
    # Export pixelwise annotations for rope at current frame; if knot-only, only annotate the knot, if end_only, only annotate the ends of the rope, if both are false, annotate the full rope
    scene = bpy.context.scene
    render_scale = scene.render.resolution_percentage / 100
    render_size = (
            int(scene.render.resolution_x * render_scale),
            int(scene.render.resolution_y * render_scale),
            )
    pixels = []
    if knot_only:
        annot_list = []
        pull, hold, _ = find_knot(50)
        indices = list(range(pull-offset, pull+offset+1)) + list(range(hold-offset, hold+offset+1))
    elif end_only:
        indices = list(range(4)) + list(range(46,50))
    else:
        indices = list(range(50))
    for i in indices:
        cyl = get_piece("Cylinder", i if i != 0 else -1)
        cyl_verts = list(cyl.data.vertices)
        step_size = max(len(indices)*len(cyl_verts)//num_annotations, 1)
        vertex_coords = [cyl.matrix_world @ v.co for v in cyl_verts][::step_size]
        for i in range(len(vertex_coords)):
            v = vertex_coords[i]
            camera_coord = bpy_extras.object_utils.world_to_camera_view(scene, bpy.context.scene.camera, v)
            pixel = [round(camera_coord.x * render_size[0]), round(render_size[1] - camera_coord.y * render_size[1])]
            pixels.append([pixel])
    mapping[frame] = pixels

def get_piece(piece_name, piece_id):
    # Returns the piece with name piece_name, index piece_id
    if piece_id == -1 or piece_id == 0 or piece_id is None:
        return bpy.data.objects['%s' % (piece_name)]
    return bpy.data.objects['%s.%03d' % (piece_name, piece_id)]

def toggle_animation(obj, frame, animate):
    # Sets the obj to be animable or non-animable at particular frame
    obj.rigid_body.kinematic = animate
    obj.keyframe_insert(data_path="rigid_body.kinematic", frame=frame)

def take_action(obj, frame, action_vec, animate=True):
    # Wrapper for taking an action given by action_vec on the object (cylinder)
    curr_frame = bpy.context.scene.frame_current
    dx,dy,dz = action_vec
    if animate != obj.rigid_body.kinematic:
        # We are "picking up" a dropped object, so we need its updated location
        obj.location = obj.matrix_world.translation
        obj.rotation_euler = obj.matrix_world.to_euler()
        obj.keyframe_insert(data_path="location", frame=curr_frame)
        obj.keyframe_insert(data_path="rotation_euler", frame=curr_frame)
    toggle_animation(obj, curr_frame, animate)
    obj.location += Vector((dx,dy,dz))
    obj.keyframe_insert(data_path="location", frame=frame)

def find_knot(num_segments, chain=False, depth_thresh=0.4, idx_thresh=3, pull_offset=3):
    piece = "Torus" if chain else "Cylinder"
    cache = {}

    # Make a single pass, store the xy positions of the cylinders
    for i in range(num_segments):
        cyl = get_piece(piece, i if i else -1)
        x,y,z = cyl.matrix_world.translation
        key = tuple((x,y))
        val = {"idx":i, "depth":z}
        cache[key] = val
    neigh = NearestNeighbors(2, 0)
    planar_coords = list(cache.keys())
    neigh.fit(planar_coords)
    # Now traverse and look for the under crossing
    for i in range(num_segments):
        cyl = get_piece(piece, i if i else -1)
        x,y,z = cyl.matrix_world.translation
        match_idxs = neigh.kneighbors([(x,y)], 2, return_distance=False) # 1st neighbor is always identical, we want 2nd
        nearest = match_idxs.squeeze().tolist()[1:][0]
        x1,y1 = planar_coords[nearest]
        curr_cyl, match_cyl = cache[(x,y)], cache[(x1,y1)]
        depth_diff = match_cyl["depth"] - curr_cyl["depth"]
        idx_diff = abs(match_cyl["idx"] - curr_cyl["idx"])
        if depth_diff > depth_thresh and idx_diff > idx_thresh:
            pull_idx = i + pull_offset # Pick a point slightly past under crossing to do the pull
            dx = planar_coords[pull_idx][0] - x
            dy = planar_coords[pull_idx][1] - y
            hold_idx = match_cyl["idx"]
            SCALE_X = 1
            SCALE_Y = 1
            Z_OFF = 2
            action_vec = [SCALE_X*dx, SCALE_Y*dy, Z_OFF] 
            return pull_idx, hold_idx, action_vec # Found! Return the pull, hold, and action
    return 16, 25, [0,0,0] # Didn't find a pull/hold, 16 and 25 are arbitrary cylinder indices

def randomize_camera():
    pass
    #bpy.context.scene.camera.rotation_euler = (0, 0, np.random.uniform(-np.pi/4, np.pi/4))

def render_frame(frame, render_offset=0, step=2, num_annotations=300, filename="%06d_rgb.png", folder="images", annot=True, mapping=None):
    # Renders a single frame in a sequence (if frame%step == 0)
    frame -= render_offset
    randomize_camera()
    if frame%step == 0:
        scene = bpy.context.scene

        index = frame//step
        render_mask("image_masks/%06d_visible_mask.png", "images_depth/%06d_rgb.png", index)
        scene.render.filepath = os.path.join(folder, filename) % index
        bpy.ops.render.render(write_still=True)
        if annot:
            annotate(index, mapping, num_annotations)

def render_mask(mask_filename, depth_filename, index):
    scene = bpy.context.scene
    saved = scene.render.engine
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_samples = 1
    scene.eevee.taa_render_samples = 1
    scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    render_node = tree.nodes["Render Layers"]
    norm_node = tree.nodes.new(type="CompositorNodeNormalize")
    inv_node = tree.nodes.new(type="CompositorNodeInvert")
    math_node = tree.nodes.new(type="CompositorNodeMath")
    math_node.operation = 'CEIL' # Threshold the depth image
    composite = tree.nodes.new(type = "CompositorNodeComposite")

    links.new(render_node.outputs["Depth"], inv_node.inputs["Color"])
    links.new(inv_node.outputs[0], norm_node.inputs[0])
    links.new(norm_node.outputs[0], composite.inputs["Image"])

    scene.render.filepath = depth_filename % index
    bpy.ops.render.render(write_still=True)

    links.new(norm_node.outputs[0], math_node.inputs[0])
    links.new(math_node.outputs[0], composite.inputs["Image"])

    scene.render.filepath = mask_filename % index
    bpy.ops.render.render(write_still=True)
    # Clean up
    scene.render.engine = saved
    for node in tree.nodes:
        if node.name != "Render Layers":
            tree.nodes.remove(node)
    scene.use_nodes = False

def take_undo_action_oracle(params, start_frame, render=False, render_offset=0, annot=True, mapping=None):
    # Takes an action to loosen the knot using ground truth info
    piece = "Cylinder"
    pull_idx, hold_idx, action_vec = find_knot(50)
    action_vec = np.array(action_vec) + np.random.uniform(-0.5, 0.5, 3)
    action_vec /= np.linalg.norm(action_vec)
    action_vec *= 2
    pull_cyl = get_piece(piece, pull_idx)
    hold_cyl = get_piece(piece, hold_idx)
    end_frame = start_frame + 100
    take_action(hold_cyl, end_frame, (0,0,0))

    for step in range(start_frame, start_frame + 10):
        bpy.context.scene.frame_set(step)
        #render_frame(step, render_offset=render_offset, annot=annot, mapping=mapping)
        if render and (abs(step-start_frame) < 5 or abs(step-(start_frame+10)) < 5):
            render_frame(step, render_offset=render_offset, annot=annot, mapping=mapping)
        elif render:
            render_offset += 1

    take_action(pull_cyl, end_frame, action_vec)
    ## Release both pull, hold
    toggle_animation(pull_cyl, end_frame, False)
    toggle_animation(hold_cyl, end_frame, False)
    settle_time = 30
    # Let the rope settle after the action, so we can know where the ends are afterwards
    for step in range(start_frame + 10, end_frame+settle_time):
        bpy.context.scene.frame_set(step)
        #render_frame(step, render_offset=render_offset, annot=annot, mapping=mapping)
        if render and (abs(step-(start_frame+10)) < 2 or abs(step-(end_frame+settle_time)) < 2):
            render_frame(step, render_offset=render_offset, annot=annot, mapping=mapping)
        elif render:
            render_offset += 1
    return end_frame+settle_time, render_offset

def reidemeister(params, start_frame,render=False, render_offset=0, annot=True, mapping=None):
    # Straightens out the rope
    piece = "Cylinder"
    last = params["num_segments"]-1
    end1 = get_piece(piece, -1)
    end2 = get_piece(piece, last)

    middle_frame = start_frame+25
    end_frame = start_frame+75
    take_action(end2, middle_frame, (-6-end2.matrix_world.translation[0],np.random.uniform(-2,2),0))
    for step in range(start_frame, middle_frame):
        bpy.context.scene.frame_set(step)
        if render:
            render_frame(step, render_offset=render_offset, annot=annot, mapping=mapping)
    take_action(end1, end_frame, (9-end1.matrix_world.translation[0],np.random.uniform(-2,2),0))

    # Drop the ends
    toggle_animation(end1, end_frame, False)
    toggle_animation(end2, end_frame, False)

    for step in range(middle_frame, end_frame):
        bpy.context.scene.frame_set(step)
        if render:
            render_frame(step, render_offset=render_offset, annot=annot, mapping=mapping)
    return end_frame

def generate_dataset(params, iters=1, chain=False, render=False):
    # Generates a dataset of rope renderings
    set_animation_settings(15000) # Cache length to use for simulation 
    piece = "Cylinder"
    last = params["num_segments"]-1
    mapping = {}

    render_offset = 0
    num_loosens = 5 # For each knot, we can do num_loosens loosening actions
    for i in range(iters):
        num_knots = 1
        # Tie a knot
        if i%2==0:
            knot_end_frame = knots.tie_pretzel_knot(params, render=False)
        elif i%2==1:
            knot_end_frame = knots.tie_figure_eight(params, render=False)
        # Straighten rope out
        reid_end_frame = reidemeister(params, knot_end_frame, render=False, mapping=mapping) 
        render_offset += reid_end_frame
        # Loosen the knot
        loosen_start = reid_end_frame
        for i in range(num_loosens):
            loosen_end_frame, offset = take_undo_action_oracle(params, loosen_start, render=render, render_offset=render_offset, mapping=mapping)
            loosen_start = loosen_end_frame
            render_offset = offset
        render_offset -= loosen_end_frame
        # Delete all keyframes to make a new knot and reset the frame counter
        bpy.context.scene.frame_set(0)
        for a in bpy.data.actions:
            bpy.data.actions.remove(a)
    # Export pixelwise annotations
    with open("./images/knots_info.json", 'w') as outfile:
        json.dump(mapping, outfile, sort_keys=True, indent=2)

if __name__ == '__main__':
    with open("rigidbody_params.json", "r") as f:
        params = json.load(f)
    clear_scene()
    make_capsule_rope(params)
    rig_rope(params, 'cable')
    add_camera_light()
    set_render_settings(params["engine"],(params["render_width"],params["render_height"]))
    make_table(params)
    start = time.time()
    generate_dataset(params, iters=2, render=True)
    end = time.time()
    print("Time:", end-start)
