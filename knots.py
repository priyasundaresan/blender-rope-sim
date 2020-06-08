import bpy
import numpy as np

from math import pi
import os
import sys
sys.path.append(os.getcwd())

from rigidbody_rope import *

def set_animation_settings(anim_end):
    # Sets up the animation to run till frame anim_end (otherwise default terminates @ 250)
    scene = bpy.context.scene
    scene.frame_end = anim_end
    scene.rigidbody_world.point_cache.frame_end = anim_end

def get_piece(piece_name, piece_id):
    # Returns the piece with name piece_name, index piece_id
    # if piece_id == -1:
    if piece_id == -1 or piece_id == 0:
        return bpy.data.objects['%s' % (piece_name)]
    return bpy.data.objects['%s.%03d' % (piece_name, piece_id)]

def toggle_animation(obj, frame, animate):
    # Sets the obj to be animable or non-animable at particular frame
    obj.rigid_body.kinematic = animate
    obj.keyframe_insert(data_path="rigid_body.kinematic", frame=frame)

def take_action(obj, frame, action_vec, animate=True):
    # Keyframes a displacement for obj given by action_vec at given frame
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
    obj.rotation_euler = obj.matrix_world.to_euler()
    obj.keyframe_insert(data_path="location", frame=frame)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame)

def tie_pretzel_knot(params, chain=False, render=False):

    piece = "Cylinder"
    last = params["num_segments"]-1
    end1 = get_piece(piece, -1)
    end2 = get_piece(piece, last)
    for i in range(last+1):
        obj = get_piece(piece, i if i != 0 else -1)
        take_action(obj, 1, (0,0,0), animate=(i==0 or i==last))

    # Wrap endpoint one circularly around endpoint 2
    take_action(end2, 80, (10,0,0))
    take_action(end1, 80, (-15,5,0))
    take_action(end1, 120, (-1,-7,0))
    take_action(end1, 150, (3,0,-4))
    take_action(end1, 170, (0,2.5,0))

    # Thread endpoint 1 through the loop (downward)
    take_action(end1, 180, (0,0,-2))

    # Pull to tighten knot
    take_action(end1, 200, (5,0,2))
    take_action(end2, 200, (0,0,0))
    take_action(end1, 230, (8,0,5))
    take_action(end2, 230, (-6,0,0))

    take_action(end1, 260, (-1,0,-1))
    take_action(end2, 260, (1,0,-1))
    toggle_animation(end1, 280, False)
    toggle_animation(end2, 280, False)

    ## Reidemeister
    for step in range(1, 350):
        bpy.context.scene.frame_set(step)
        #if render:
        #    render_frame(step, render_offset=render_offset)
    return 350

def tie_figure_eight(params, chain=False, render=False):

    piece = "Cylinder"
    last = params["num_segments"]-1
    end1 = get_piece(piece, -1)
    end2 = get_piece(piece, last)
    for i in range(last+1):
        obj = get_piece(piece, i if i != 0 else -1)
        take_action(obj, 1, (0,0,0), animate=(i==0 or i==last))

    take_action(end2, 80, (10,0,2))
    take_action(end1, 80, (-15,2,2))
    take_action(end2, 130, (1,3,0))
    take_action(end2, 180, (-4,0,0))
    take_action(end2, 200, (0,-2,0))
    take_action(end2, 250, (4.5,-0.25,-6))
    take_action(end2, 300, (0,0,-2))
    take_action(end2, 350, (9,0,8))
    take_action(end2, 400, (-16,0,0))

    take_action(end1, 350, (0,0,0))
    take_action(end1, 400, (14,-2,-2))

    # Take some time to settle
    toggle_animation(end1, 450, False)
    toggle_animation(end2, 450, False)

    for step in range(1, 500):
        bpy.context.scene.frame_set(step)
        #if render:
        #    render_frame(step)
    return 500

def tie_stevedore(params, chain=False, render=False):

    piece = "Cylinder"
    last = params["num_segments"]-1
    end1 = get_piece(piece, -1)
    end2 = get_piece(piece, last)
    for i in range(last+1):
        obj = get_piece(piece, i if i != 0 else -1)
        take_action(obj, 1, (0,0,0), animate=(i==0 or i==last))

    take_action(end2, 80, (10,0,2))
    take_action(end1, 80, (-15,2,2))
    take_action(end2, 100, (1,3,0))
    take_action(end2, 130, (-4,0,0))
    take_action(end2, 150, (0,-2,0))

    take_action(end2, 170, (3,0,0))
    take_action(end2, 190, (0,2,0))
    take_action(end2, 210, (-2,0,0))
    take_action(end2, 230, (0,-2,0))

    take_action(end2, 300, (3.5,-0.25,-6))
    take_action(end2, 310, (0,0,-3))
    take_action(end2, 350, (9,0,8))
    take_action(end1, 350, (0,0,0))
    #take_action(end2, 400, (-16,0,-3))
    #take_action(end1, 400, (8,-2,-5))
    take_action(end2, 400, (-12,0,-3))
    take_action(end1, 400, (12,-2,-5))

    # Take some time to settle
    toggle_animation(end1, 430, False)
    toggle_animation(end2, 430, False)
    for step in range(1, 470):
        bpy.context.scene.frame_set(step)
        #if render:
        #    render_frame(step)
    return 470

def tie_double_pretzel(params, chain=False, render=False):

    piece = "Cylinder"
    last = params["num_segments"]-1
    end1 = get_piece(piece, -1)
    end2 = get_piece(piece, last)
    for i in range(last+1):
        obj = get_piece(piece, i if i != 0 else -1)
        take_action(obj, 1, (0,0,0), animate=(i==0 or i==last))

    take_action(end2, 80, (5,0,-1))
    take_action(end1, 80, (-20,2,2))

    take_action(end2, 100, (2,2,0))
    take_action(end1, 100, (0,0,0))
    take_action(end1, 150, (6,-1,0))
    take_action(end2, 150, (0,0,0))
    take_action(end2, 200, (2,-1.5,-3))
    take_action(end2, 220, (0,0,-3))
    take_action(end2, 240, (-6,0,0))
    take_action(end1, 240, (0,0,0))
    take_action(end2, 300, (-3,0,5))
    take_action(end1, 300, (4,0,0))

    take_action(end1, 320, (0,0,0))
    take_action(end1, 360, (-11,3,-5))
    take_action(end1, 380, (-1,-3,0))
    take_action(end1, 410, (1,1,-2))
    take_action(end1, 430, (-2,6,2))
    take_action(end1, 460, (0,0,0))
    take_action(end1, 490, (0,-5,3))
    take_action(end2, 490, (0,0,0))
    take_action(end2, 520, (11,0,-2))
    take_action(end1, 520, (18,-3,-2))
    toggle_animation(end1, 540, False)
    toggle_animation(end2, 540, False)

    for step in range(1, 560):
        bpy.context.scene.frame_set(step)
        #if render:
        #    render_frame(step)
    return 560

def tie_knot_7(params, chain=False, render=True):
    piece = "Cylinder"
    last = params["num_segments"]-1
    end1 = get_piece(piece, -1)
    end2 = get_piece(piece, last)
    for i in range(last+1):
        obj = get_piece(piece, i if i != 0 else -1)
        take_action(obj, 1, (0,0,0), animate=(i==0 or i==last))

    take_action(end2, 80, (11,0,3))
    take_action(end1, 80, (-7,2,-1))

    take_action(end2, 130, (0,-3,-2))
    take_action(end2, 150, (4,0,-2))
    take_action(end1, 180, (0,0,0))
    take_action(end2, 180, (0,6,-1))

def tie_cornell1_knot(params, chain=False, render=True):
    piece = "Cylinder"
    last = params["num_segments"]-1
    end1 = get_piece(piece, -1)
    end2 = get_piece(piece, last)
    for i in range(last+1):
        obj = get_piece(piece, i if i != 0 else -1)
        take_action(obj, 1, (0,0,0), animate=(i==0 or i==last))

    # make center loop
    take_action(end2, 80, (10,1,5))
    # take_action(end2, 120, (3,1,-3))
    take_action(end2, 120, (3,2,-3))
    take_action(end2, 160, (0,-3,-2))
    take_action(end2, 200, (0,-2,-4))
    toggle_animation(end2, 200, False)
    toggle_animation(end2, 200, True)
    take_action(end2, 240, (0,-1,2))
    take_action(end2, 280, (-4,3,-2))

    # move other end across
    take_action(end1, 80, (-10,1,5))
    take_action(end1, 120, (-5,0,0))
    take_action(end1, 160, (0,-2,-4))
    toggle_animation(end1, 160, False)
    toggle_animation(end1, 160, True)
    take_action(end2, 320, (0,-1,0))
    # take_action(end2, 320, (1,-1,0))
    take_action(end1, 360, (6,0,-5))
    # take_action(end1, 360, (5,0,-5))
    toggle_animation(end1, 360, False)
    toggle_animation(end2, 360, False)

    settle_time = 10
    ## Reidemeister
    for step in range(1, 360+settle_time):
        bpy.context.scene.frame_set(step)
        if render:
           render_frame(step, render_offset=render_offset)
    return 360

def tie_cornell2_knot(params, chain=False, render=False):
    end_frame = tie_pretzel_knot(params, chain=chain, render=render)
    for _ in range(2):
        end_frame = rend.random_loosen(params, end_frame, render=render, mapping={}, annot=False)
    return end_frame

if __name__ == '__main__':
    with open("rigidbody_params.json", "r") as f:
        params = json.load(f)
    clear_scene()
    make_capsule_rope(params)
    # UNCOMMENT TO SEE CYLINDER REPR
    #rig_rope(params, mode="braid") 
    rig_rope(params, mode="cable") 
    add_camera_light()
    set_animation_settings(600)
    make_table(params)
    #tie_figure_eight(params, render=True)
    #start = time.time()
    #tie_pretzel_knot(params, render=True)
    #end = time.time()
    #print(end-start)
    #tie_stevedore(params, render=True)
    #tie_double_pretzel(params, render=True)
    tie_cornell1_knot(params, render=False)
