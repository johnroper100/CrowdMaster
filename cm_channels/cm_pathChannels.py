# Copyright 2016 CrowdMaster Developer Team
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of CrowdMaster.
#
# CrowdMaster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CrowdMaster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CrowdMaster.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import bpy
import mathutils
Rotation = mathutils.Matrix.Rotation
Euler = mathutils.Euler
import math
import bmesh

from bpy.props import IntProperty, EnumProperty, CollectionProperty
from bpy.props import PointerProperty, BoolProperty, StringProperty
from bpy.props import FloatProperty
from bpy.types import PropertyGroup, UIList, Panel, Operator

from .cm_masterChannels import MasterChannel as Mc
from .cm_masterChannels import timeChannel


class Path(Mc):
    """Used to access data about paths in the scene"""
    def __init__(self, sim):
        Mc.__init__(self, sim)

        self.pathObjectCache = {}
        self.resultsCache = {}

    def newframe(self):
        self.pathObjectCache = {}

    def setuser(self, userid):
        Mc.setuser(self, userid)
        self.resultsCache = {}

    def calcPathData(self, pathObject):
        if pathObject in self.pathObjectCache:
            return self.pathObjectCache[pathObject]
        obj = bpy.context.scene.objects[pathObject]
        mesh = obj.data
        size = len(mesh.vertices)
        kd = mathutils.kdtree.KDTree(size)

        for i, v in enumerate(mesh.vertices):
            kd.insert(v.co, i)

        kd.balance()

        bm = bmesh.new()
        bm.from_mesh(mesh)

        bm.verts.ensure_lookup_table()

        pathMatrixInverse = obj.matrix_world.inverted()

        x, y, z = obj.rotation_euler
        z = mathutils.Matrix.Rotation(obj.rotation_euler[2], 4, 'Z')
        y = mathutils.Matrix.Rotation(obj.rotation_euler[1], 4, 'Y')
        x = mathutils.Matrix.Rotation(obj.rotation_euler[0], 4, 'X')

        rotation = x * y * z

        self.pathObjectCache[pathObject] = (kd, bm, pathMatrixInverse, rotation)

        return kd, bm, pathMatrixInverse, rotation

    def followPath(self, bm, co, index, vel, co_find, radius):
        nVel = vel.normalized()
        lVel = vel.length
        next = index

        edges = bm.verts[next].link_edges

        bestScore = -2  # scores in range -1 -> 1 (worst to best)
        nextVert = None

        for e in edges:
            otherVert = e.verts[0] if e.verts[0].index != next else e.verts[1]
            score = (otherVert.co - bm.verts[next].co).normalized().dot(nVel)
            if score > bestScore:
                bestScore = score
                nextVert = otherVert

        if nextVert is None:
            raise Exception("Invalid mesh")

        ab = nextVert.co - co
        ap = co_find - co

        fac = ap.dot(ab) / ab.dot(ab)
        adjust = fac * ab
        lVel += ab.length * fac
        start = co + adjust

        nextIndex = nextVert.index

        while True:
            currentVert = bm.verts[index].co
            nextVert = bm.verts[nextIndex].co

            length = (nextVert - currentVert).length
            if lVel < length:
                fac = lVel/length
                target = currentVert * (1 - fac) + nextVert * fac
                rCorrect = start - co_find
                offTargetDist = rCorrect.length - radius
                if offTargetDist > 0:
                    rCorrect *= (offTargetDist / rCorrect.length)
                    return target - start + rCorrect
                    # TODO For variable radius add here AND BELOW!!!!!!!!!!
                return target - start
            lVel -= length

            edges = bm.verts[next].link_edges
            bestScore = -2  # scores in range -1 -> 1 (worst to best)
            nextCo = nextVert
            nextVert = None

            endOfPath = True
            for e in edges:
                if e.verts[0].index != index and e.verts[1].index != index:
                    endOfPath = False
                    otherVert = e.verts[0] if e.verts[0].index != nextIndex else e.verts[1]
                    score = (otherVert.co - bm.verts[nextIndex].co).normalized().dot(nVel)
                    if score > bestScore:
                        bestScore = score
                        nextVert = otherVert
            if endOfPath:
                rCorrect = start - co_find
                offTargetDist = rCorrect.length - radius
                target = nextCo
                if offTargetDist > 0:
                    rCorrect *= (offTargetDist / rCorrect.length)
                    return target - start + rCorrect
                    # Also add here for variable length path
                return target - start

            index = nextIndex
            nextIndex = nextVert.index

    def calcRelativeTarget(self, pathObject, radius, lookahead):
        context = bpy.context

        if pathObject in self.pathObjectCache:
            kd, bm, pathMatrixInverse, rotation = self.pathObjectCache[pathObject]
        else:
            kd, bm, pathMatrixInverse, rotation = self.calcPathData(pathObject)

        vel = self.sim.agents[self.userid].globalVelocity * lookahead
        vel = vel * rotation
        co_find = pathMatrixInverse * context.scene.objects[self.userid].location
        co, index, dist = kd.find(co_find)
        offset = self.followPath(bm, co, index, vel, co_find, radius)

        offset = offset * pathMatrixInverse

        eul = Euler([-x for x in context.scene.objects[self.userid].rotation_euler], 'ZYX')
        offset.rotate(eul)

        return offset

    @timeChannel("Path")
    def rz(self, pathName):
        if pathName in self.resultsCache:
            target = self.resultsCache[pathName]
        else:
            lookahead = 25  # Hard coded for simplicity
            pathEntry = bpy.context.scene.cm_paths.coll.get(pathName)
            pathObject = pathEntry.objectName
            radius = pathEntry.radius
            target = self.calcRelativeTarget(pathObject, radius, lookahead)
            self.resultsCache[pathObject] = target
        return math.atan2(target[0], target[1])/math.pi

    @timeChannel("Path")
    def rx(self, pathName):
        if pathName in self.resultsCache:
            target = self.resultsCache[pathName]
        else:
            lookahead = 25  # Hard coded for simplicity
            pathEntry = bpy.context.scene.cm_paths.coll.get(pathName)
            pathObject = pathEntry.objectName
            radius = pathEntry.radius
            target = self.calcRelativeTarget(pathObject, radius, lookahead)
            self.resultsCache[pathObject] = target
        return math.atan2(target[2], target[1])/math.pi


class path_entry(PropertyGroup):
    """For storing a single path"""
    # name - aliase given to the path
    objectName = StringProperty(name="Object Name")
    radius = FloatProperty(name="Radius", min=0)


class paths_collection(PropertyGroup):
    coll = CollectionProperty(type=path_entry)
    index = IntProperty()


class SCENE_OT_cm_path_populate(Operator):
    bl_idname = "scene.cm_paths_populate"
    bl_label = "Add a path"

    def execute(self, context):
        item = context.scene.cm_paths.coll.add()
        return {'FINISHED'}


class SCENE_OT_cm_path_remove(Operator):
    bl_idname = "scene.cm_paths_remove"
    bl_label = "Remove a path"

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.cm_paths.coll) > s.cm_paths.index >= 0

    def execute(self, context):
        s = context.scene
        s.cm_paths.coll.remove(s.cm_paths.index)
        if s.cm_paths.index > 0:
            s.cm_paths.index -= 1
        return {'FINISHED'}


class SCENE_UL_cm_path(UIList):
    """for drawing each row"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        layout.prop(item, "name", text="")
        layout.prop_search(item, "objectName", bpy.data, "objects", text="")
        layout.prop(item, "radius")


class SCENE_PT_path(Panel):
    """Creates CrowdMaster Panel in the node editor"""
    bl_label = "Paths"
    bl_idname = "SCENE_PT_path"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "CrowdMaster"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        try:
            return bpy.context.space_data.tree_type == 'CrowdMasterTreeType', bpy.context.space_data.tree_type == 'CrowdMasterGenTreeType'
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        sce = context.scene

        row = layout.row()

        row.template_list("SCENE_UL_cm_path", "", sce.cm_paths,
                          "coll", sce.cm_paths, "index")

        col = row.column()
        sub = col.column(True)
        blid_ap = SCENE_OT_cm_path_populate.bl_idname
        sub.operator(blid_ap, text="", icon="ZOOMIN")
        blid_ar = SCENE_OT_cm_path_remove.bl_idname
        sub.operator(blid_ar, text="", icon="ZOOMOUT")


def register():
    bpy.utils.register_class(path_entry)
    bpy.utils.register_class(paths_collection)
    bpy.utils.register_class(SCENE_OT_cm_path_populate)
    bpy.utils.register_class(SCENE_OT_cm_path_remove)
    bpy.utils.register_class(SCENE_UL_cm_path)
    bpy.utils.register_class(SCENE_PT_path)
    bpy.types.Scene.cm_paths = PointerProperty(type=paths_collection)


def unregister():
    bpy.utils.unregister_class(path_entry)
    bpy.utils.unregister_class(paths_collection)
    bpy.utils.unregister_class(SCENE_OT_cm_path_populate)
    bpy.utils.unregister_class(SCENE_OT_cm_path_remove)
    bpy.utils.unregister_class(SCENE_UL_cm_path)
    bpy.utils.unregister_class(SCENE_PT_path)
    del bpy.types.Scene.cm_paths
