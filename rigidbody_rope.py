import bpy
import os
import json
import time
import sys
import bpy, bpy_extras
from math import *
from mathutils import *
import random
import numpy as np
import random
from random import sample
import bmesh

'''Usage: blender -P rigidbody-rope.py'''

def clear_scene():
    '''Clear existing objects in scene'''
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)
    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def make_capsule_rope(params):
    '''Make a rigid rope composed of capsules linked by rigid body constraints'''
    radius = params["segment_radius"]
    rope_length = radius * params["num_segments"]
    num_segments = int(rope_length / radius)
    separation = radius*1.1 # HACKY - artificially increase the separation to avoid link-to-link collision
    link_mass = params["segment_mass"] # TODO: this may need to be scaled
    link_friction = params["segment_friction"]
    twist_stiffness = 20
    twist_damping = 10
    bend_stiffness = 0
    bend_damping = 5
    num_joints = int(radius/separation)*2+1
    bpy.ops.import_mesh.stl(filepath="data/capsule_12_8_1_2.stl")
    loc0 = (radius*num_segments,0,0)
    link0 = bpy.context.object
    link0.location = loc0
    loc0 = loc0[0]
    link0.name = "Cylinder"
    bpy.ops.transform.resize(value=(radius, radius, radius))
    link0.rotation_euler = (0, pi/2, 0)
    bpy.ops.rigidbody.object_add()
    link0.rigid_body.mass = link_mass
    link0.rigid_body.friction = link_friction
    link0.rigid_body.linear_damping = params["linear_damping"]
    link0.rigid_body.angular_damping = params["angular_damping"] # NOTE: this makes the rope a lot less wiggly
    # These are simulation parameters that seemed to work well for simulation speed & collision handling
    bpy.context.scene.rigidbody_world.steps_per_second = 120
    bpy.context.scene.rigidbody_world.solver_iterations = 20
    for i in range(num_segments-1):
        bpy.ops.object.duplicate_move(TRANSFORM_OT_translate={"value":(-2*radius, 0, 0)})
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.rigidbody.connect(con_type='POINT', connection_pattern='CHAIN_DISTANCE')
    bpy.ops.object.select_all(action='DESELECT')
    links = [bpy.data.objects['Cylinder.%03d' % (i) if i>0 else "Cylinder"] for i in range(num_segments)]
    return links

def createNewBone(obj, new_bone_name, head, tail):
    '''A helper function to create armature'''
    bpy.ops.object.editmode_toggle()
    bpy.ops.armature.bone_primitive_add(name=new_bone_name)
    new_edit_bone = obj.data.edit_bones[new_bone_name]
    new_edit_bone.head = head
    new_edit_bone.tail = tail
    bpy.ops.object.editmode_toggle()
    bone = obj.pose.bones[-1]
    constraint = bone.constraints.new('COPY_TRANSFORMS')
    target_obj_name = "Cylinder" if new_bone_name == "Bone.000" else new_bone_name.replace("Bone", "Cylinder")
    constraint.target = bpy.data.objects[target_obj_name]

def make_braid_rig(params, bezier):
    '''Braided rope armature'''
    n = params["num_segments"]
    radius = params["segment_radius"]
    bpy.ops.mesh.primitive_circle_add(location=(0,0,0))
    radius = 0.125
    bpy.ops.transform.resize(value=(radius, radius, radius))
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.rotate(value= pi / 2, orient_axis='X')
    bpy.ops.transform.translate(value=(radius, 0, 0))
    bpy.ops.object.mode_set(mode='OBJECT')
    num_chords = 4
    for i in range(1, num_chords):
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate=None, TRANSFORM_OT_translate=None)
        ob = bpy.context.active_object
        ob.rotation_euler = (0, 0, i * (2*pi / num_chords))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    bpy.ops.object.modifier_add(type='SCREW')
    rope = bpy.context.object
    rope.rotation_euler = (0,pi/2,0)
    rope.modifiers["Screw"].screw_offset = 12 
    rope.modifiers["Screw"].iterations = 16 
    bpy.ops.object.modifier_add(type='CURVE')
    rope.modifiers["Curve"].object = bezier
    rope.modifiers["Curve"].show_in_editmode = True
    rope.modifiers["Curve"].show_on_cage = True
    return rope

def make_cable_rig(params, bezier):
    '''Cable armature'''
    bpy.ops.object.modifier_add(type='CURVE')
    bpy.ops.curve.primitive_bezier_circle_add(radius=0.02)
    bezier.data.bevel_object = bpy.data.objects["BezierCircle"]
    bpy.context.view_layer.objects.active = bezier
    return bezier

def rig_rope(params, mode):
    '''Adds rig (either braid or cable), hides capsules'''
    bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
    arm = bpy.context.object
    n = params["num_segments"]
    radius = params["segment_radius"]
    for i in range(n):
        loc = 2*radius*((n-i) - n//2)
        createNewBone(arm, "Bone.%03d"%i, (loc,0,0), (loc,0,1))
    bpy.ops.curve.primitive_bezier_curve_add(location=(radius,0,0))
    bezier_scale = n*radius
    bpy.ops.transform.resize(value=(bezier_scale, bezier_scale, bezier_scale))
    bezier = bpy.context.active_object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.curve.select_all(action='SELECT')
    bpy.ops.curve.handle_type_set(type='VECTOR')
    bpy.ops.curve.handle_type_set(type='AUTOMATIC')
    num_control_points = 40 # Tune this
    bpy.ops.curve.subdivide(number_cuts=num_control_points-2)
    bpy.ops.object.mode_set(mode='OBJECT')
    bezier_points = bezier.data.splines[0].bezier_points
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.curve.select_all(action='DESELECT')
    for i in range(num_control_points):
        bpy.ops.curve.select_all(action='DESELECT')
        hook = bezier.modifiers.new(name = "Hook.%03d"%i, type = 'HOOK' )
        hook.object = arm
        hook.subtarget = "Bone.%03d"%(n-1-(i*n/num_control_points))
        pt = bpy.data.curves['BezierCurve'].splines[0].bezier_points[i]
        pt.select_control_point = True
        bpy.ops.object.hook_assign(modifier="Hook.%03d"%i)
        pt.select_control_point = False
    bpy.ops.object.mode_set(mode='OBJECT')
    for i in range(n):
        obj_name = "Cylinder.%03d"%i if i else "Cylinder"
        bpy.data.objects[obj_name].hide_set(True)
        bpy.data.objects[obj_name].hide_render = True
    bezier.select_set(False)
    if mode == 'braid':
        rope = make_braid_rig(params, bezier)
    else:
        rope = make_cable_rig(params, bezier)

def add_camera_light():
    bpy.ops.object.light_add(type='SUN', radius=1, location=(0,0,0))
    bpy.ops.object.camera_add(location=(2,0,28), rotation=(0,0,0))
    bpy.context.scene.camera = bpy.context.object

def make_table(params):
    bpy.ops.mesh.primitive_plane_add(size=params["table_size"], location=(0,0,-5))
    bpy.ops.rigidbody.object_add()
    table = bpy.context.object
    table.rigid_body.type = 'PASSIVE'
    table.rigid_body.friction = 0.8
    bpy.ops.object.select_all(action='DESELECT')

if __name__ == '__main__':
    with open("rigidbody_params.json", "r") as f:
        params = json.load(f)
    clear_scene()
    links = make_capsule_rope(params)
    make_table(params)
    add_camera_light()
