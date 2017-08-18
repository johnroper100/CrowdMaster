# Copyright 2017 CrowdMaster Developer Team
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

import logging
import math

import bmesh
import bpy
import mathutils
from bpy.props import (CollectionProperty, EnumProperty, FloatProperty,
                       IntProperty, PointerProperty, StringProperty)
from bpy.types import Operator, Panel, PropertyGroup, UIList

from ..libs import cm_draw
from .cm_masterChannels import MasterChannel as Mc
from .cm_masterChannels import timeChannel

Rotation = mathutils.Matrix.Rotation
Euler = mathutils.Euler
Vector = mathutils.Vector

logger = logging.getLogger("CrowdMaster")


class Path(Mc):
    """Used to access data about paths in the scene"""

    def __init__(self, sim):
        Mc.__init__(self, sim)

        self.pathObjectCache = {}
        self.resultsCache = {}
        self.laneCache = {}  # {pathName: {vertexID: [(objectID, pathPos)]}}

    def newframe(self):
        self.pathObjectCache = {}
        self.laneCache = {}

    def setuser(self, userid):
        Mc.setuser(self, userid)
        self.resultsCache = {}
        self.laneCache = {}

    def calcPathData(self, pathObject, revDirec):
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

        bm.edges.layers.int.new("revDirec")
        revDirecLayer = bm.edges.layers.int["revDirec"]
        bm.edges.ensure_lookup_table()

        if revDirec is not None:
            for edge in bm.edges:
                if str(edge.index) in revDirec:
                    edge[revDirecLayer] = 0
                else:
                    edge[revDirecLayer] = 1

        bm.verts.ensure_lookup_table()

        pathMatrixInverse = obj.matrix_world.inverted()

        x, y, z = obj.rotation_euler
        z = mathutils.Matrix.Rotation(obj.rotation_euler[2], 4, 'Z')
        y = mathutils.Matrix.Rotation(obj.rotation_euler[1], 4, 'Y')
        x = mathutils.Matrix.Rotation(obj.rotation_euler[0], 4, 'X')

        rotation = x * y * z

        self.pathObjectCache[pathObject] = (
            kd, bm, pathMatrixInverse, rotation)

        return kd, bm, pathMatrixInverse, rotation

    def firstPointOnPath(self, bm, co, index, co_find, nDirec, isDirectional):
        """
        :param bm: bmesh object
        :param co: the location of the nearest vertex on the path object
        :param index: the index of co
        :param co_find: the location of the point to search. In local space.
        :param nDirec: the direction that the agent is facing in
        :param isDirectional: type of the path
        """
        bestScore = -2  # scores in range -1 -> 1 (worst to best)
        nextIndex = None
        nextVert = None
        nextDirec = None
        nextRevDirec = None

        edges = bm.verts[index].link_edges

        # TODO look for new path segement when only 1 connecting edge
        if len(edges) <= 2:
            normNearestToAgent = (co_find - co).normalized()
            # Select next nearest edge based on nearest connecting edge.
            for e in edges:
                if isDirectional:
                    revDirecLayer = bm.edges.layers.int["revDirec"]
                    if e.verts[0].index != index:
                        otherVert = e.verts[0]
                        direcNearestToOther = e[revDirecLayer] == 1
                    else:
                        otherVert = e.verts[1]
                        direcNearestToOther = e[revDirecLayer] == 0
                else:
                    if e.verts[0].index != index:
                        otherVert = e.verts[0]
                    else:
                        otherVert = e.verts[1]
                nearestToOther = otherVert.co - bm.verts[index].co
                normNearestToOther = nearestToOther.normalized()
                score = normNearestToOther.dot(normNearestToAgent)
                if score > bestScore:
                    bestScore = score
                    nextIndex = otherVert.index
                    nextVert = otherVert.co
                    nextDirec = normNearestToOther
                    if isDirectional:
                        nextRevDirec = direcNearestToOther
            wrongDirectional = isDirectional and nextRevDirec
            notDirec = not isDirectional
            if notDirec and nextDirec.dot(nDirec) < 0 or wrongDirectional:
                nextVert, co = co, nextVert
                nextIndex, index = index, nextIndex
        else:
            # Select next edge with nearest matching direction
            for e in edges:
                if isDirectional:
                    revDirecLayer = bm.edges.layers.int["revDirec"]
                    if e.verts[0].index != index:
                        otherVert = e.verts[0]
                        direcNearestToOther = e[revDirecLayer] == 0
                    else:
                        otherVert = e.verts[1]
                        direcNearestToOther = e[revDirecLayer] == 1
                else:
                    if e.verts[0].index != index:
                        otherVert = e.verts[0]
                    else:
                        otherVert = e.verts[1]
                score = (otherVert.co -
                         bm.verts[index].co).normalized().dot(nDirec)
                notDirec = not isDirectional
                if notDirec or (direcNearestToOther and score > bestScore):
                    bestScore = score
                    nextIndex = otherVert.index
                    nextVert = otherVert.co

        if nextVert is None or co is None:
            raise Exception("Invalid mesh")

        ab = nextVert - co
        ap = co_find - co

        if ab.x == 0 and ab.y == 0 and ab.z == 0:
            raise Exception("Path mesh must not have vertices with identical\
                             positions. Verts: " + str(index) + ", " + str(nextIndex))

        fac = ap.dot(ab) / ab.dot(ab)
        adjust = fac * ab
        # lVel += ab.length * fac
        adjustLength = ab.length * fac
        # whole length of current edge is compared to lVel so add length that
        #   is behind the agent.
        start = co + adjust

        return nextIndex, nextVert, nextDirec, nextRevDirec, start, adjustLength, index, co

    def followPath(self, bm, co, index, vel, co_find, radius, laneSeparation,
                   isDirectional, pathEntry):
        """
        :param bm: bmesh object
        :param co: coordinates of nearest vertex
        :param index: index of nearest vertex

        :param co_find: position of agent

        :param isDirectional: is this path a directional path
        """
        nVel = vel.normalized()
        lVel = vel.length

        res = self.firstPointOnPath(
            bm, co, index, co_find, nVel, isDirectional)
        nextIndex, nextVert, nextDirec, nextRevDirec, start, adjustLength, index, co = res

        lVel += adjustLength

        while True:
            currentVert = bm.verts[index].co
            nextVert = bm.verts[nextIndex].co

            # ============ Move along current edge ============

            direc = nextVert - currentVert

            if laneSeparation is not None:
                zaxis = Vector((0, 0, 1))
                if isDirectional:
                    laneSeparation = 0.0
                sepVec = direc.cross(zaxis).normalized() * laneSeparation

            length = direc.length
            if lVel < length:
                fac = lVel / length
                target = currentVert * (1 - fac) + nextVert * fac
                rCorrect = start - co_find

                if laneSeparation is not None:
                    rCorrect += sepVec

                offTargetDist = rCorrect.length - radius
                if offTargetDist > 0:
                    rCorrect *= (offTargetDist / rCorrect.length)
                    return target - start + rCorrect
                    # TODO For variable radius add here AND BELOW!!!!!!!!!!
                return target - start
            lVel -= length

            # ============ Select next edge ============

            edges = bm.verts[nextIndex].link_edges
            bestScore = -2  # scores in range -1 -> 1 (worst to best)
            nextCo = nextVert
            nextVert = None

            endOfPath = True
            for e in edges:
                # don't go back in the direction agent has come from.
                if e.verts[0].index != index and e.verts[1].index != index:
                    endOfPath = False
                    if isDirectional:
                        revDirecLayer = bm.edges.layers.int["revDirec"]
                        if e.verts[0].index != nextIndex:
                            otherVert = e.verts[0]
                            direcNearestToOther = e[revDirecLayer] == 0
                        else:
                            otherVert = e.verts[1]
                            direcNearestToOther = e[revDirecLayer] == 1
                    else:
                        if e.verts[0].index != nextIndex:
                            otherVert = e.verts[0]
                        else:
                            otherVert = e.verts[1]
                    score = (otherVert.co -
                             bm.verts[nextIndex].co).normalized().dot(nVel)
                    notDirec = not isDirectional
                    if notDirec or direcNearestToOther and score > bestScore:
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
            if nextVert is None:
                logger.info("no next {}".format(index))
            nextIndex = nextVert.index

    def alignToPath(self, pathEntry, point, nDirec):
        pathObject = pathEntry.objectName
        isDirectional = pathEntry.mode == "directional"
        revDirec = pathEntry.revDirec if isDirectional else None
        kd, bm, pathMatrixInverse, rotation = self.calcPathData(pathObject,
                                                                revDirec)
        co_find = pathMatrixInverse * point
        co, index, dist = kd.find(co_find)

        isDirectional = pathEntry.mode == "directional"

        res = self.firstPointOnPath(
            bm, co, index, co_find, nDirec, isDirectional)
        nextIndex, nextVert, nextDirec, nextRevDirec, start, adjustLength, index, co = res

        obj = bpy.context.scene.objects[pathObject]
        globalPos = start * obj.matrix_world

        pointTowards = nextVert * obj.matrix_world

        return globalPos, pointTowards, nextIndex

    def calcRelativeTarget(self, pathEntry, lookahead):
        context = bpy.context

        pathObject = pathEntry.objectName
        radius = pathEntry.radius
        laneSep = pathEntry.laneSeparation
        isDirectional = pathEntry.mode == "directional"
        revDirec = pathEntry.revDirec if isDirectional else None

        kd, bm, pathMatrixInverse, rotation = self.calcPathData(pathObject,
                                                                revDirec)

        vel = self.sim.agents[self.userid].globalVelocity * lookahead
        if vel.x == 0 and vel.y == 0 and vel.z == 0:
            vel = Vector((0, lookahead, 0))
            vel.rotate(bpy.context.scene.objects[self.userid].rotation_euler)
        vel = vel * rotation
        co_find = pathMatrixInverse * \
            context.scene.objects[self.userid].location
        co, index, dist = kd.find(co_find)
        offset = self.followPath(bm, co, index, vel, co_find, radius, laneSep,
                                 isDirectional, pathEntry)

        offset = offset * pathMatrixInverse

        eul = Euler(
            [-x for x in context.scene.objects[self.userid].rotation_euler], 'ZYX')
        offset.rotate(eul)

        return offset

    @timeChannel("Path")
    def rz(self, pathName):
        if pathName in self.resultsCache:
            target = self.resultsCache[pathName]
        else:
            lookahead = 2  # Hard coded for simplicity
            pathEntry = bpy.context.scene.cm_paths.coll.get(pathName)
            target = self.calcRelativeTarget(pathEntry, lookahead)
            self.resultsCache[pathEntry.objectName] = target
        return math.atan2(target[0], target[1]) / math.pi

    @timeChannel("Path")
    def rx(self, pathName):
        if pathName in self.resultsCache:
            target = self.resultsCache[pathName]
        else:
            lookahead = 2  # Hard coded for simplicity
            pathEntry = bpy.context.scene.cm_paths.coll.get(pathName)
            target = self.calcRelativeTarget(pathEntry, lookahead)
            self.resultsCache[pathEntry.objectName] = target
        return math.atan2(target[2], target[1]) / math.pi

    def laneSearch(self, bm, index, lastIndex, length, edgeCache, result):
        for e in bm.verts[index].link_edges:
            if e.verts[0].index == index:
                nextInd = e.verts[1].index
            else:
                nextInd = e.verts[0].index
            if nextInd != lastIndex:
                if e.index in edgeCache:
                    for agent, start in edgeCache[e.index]:
                        if (bm.verts[index].co - start).length < length:
                            result[agent] = 1

                rem = length - e.calc_length()
                if rem > 0:
                    self.laneSearch(bm, nextInd, index, rem, edgeCache,
                                    result)

    def startEdgeAndPoint(self, bm, kd, loc):
        co, index, dist = kd.find(loc)

        normToAgent = (loc - co).normalized()

        bestScore = -2
        nextVert = None
        edgeIndex = None

        for e in bm.verts[index].link_edges:
            if e.verts[0].index == index:
                potentialNextVert = e.verts[1]
            else:
                potentialNextVert = e.verts[0]
            normToNextVert = (potentialNextVert.co - co).normalized()
            score = normToNextVert.dot(normToAgent)
            if score > bestScore:
                bestScore = score
                nextVert = potentialNextVert
                edgeIndex = e.index

        ab = nextVert.co - co
        ap = loc - co

        fac = ap.dot(ab) / ab.dot(ab)
        adjust = fac * ab
        point = co + adjust

        return edgeIndex, point

    @timeChannel("Path")
    def inlane(self, pathName, length, agents):
        context = bpy.context

        pathEntry = bpy.context.scene.cm_paths.coll.get(pathName)
        pathObject = pathEntry.objectName
        radius = pathEntry.radius
        laneSep = pathEntry.laneSeparation
        isDirectional = pathEntry.mode == "directional"
        revDirec = pathEntry.revDirec if isDirectional else None

        kd, bm, pathMatrixInverse, rotation = self.calcPathData(pathObject,
                                                                revDirec)

        co_find = pathMatrixInverse * \
            context.scene.objects[self.userid].location
        myEdgeIndex, myStart = self.startEdgeAndPoint(bm, kd, co_find)

        edgeAgentCache = {}

        for agent in agents:
            loc = pathMatrixInverse * context.scene.objects[agent].location
            edgeIndex, start = self.startEdgeAndPoint(bm, kd, loc)
            if edgeIndex not in edgeAgentCache:
                edgeAgentCache[edgeIndex] = []
            edgeAgentCache[edgeIndex].append((agent, start))

        result = {}

        if myEdgeIndex in edgeAgentCache:
            for agent, start in edgeAgentCache[myEdgeIndex]:
                if (start - myStart).length < length:
                    result[agent] = 1

        # Start a recursive search in each direction
        myEdge = bm.edges[myEdgeIndex]

        nextIndex = myEdge.verts[0].index
        lastIndex = myEdge.verts[1].index
        rem = length - (myEdge.verts[0].co - myStart).length
        self.laneSearch(bm, nextIndex, lastIndex, rem, edgeAgentCache, result)

        nextIndex = myEdge.verts[1].index
        lastIndex = myEdge.verts[0].index
        rem = length - (myEdge.verts[1].co - myStart).length
        self.laneSearch(bm, nextIndex, lastIndex, rem, edgeAgentCache, result)

        return result


class draw_path_directions_operator(Operator):
    bl_idname = "view3d.draw_path_operator"
    bl_label = "Draw Directions"

    pathName = StringProperty(name="Name Of Path")

    def drawCallback(self, context, path):
        with cm_draw.bglWrapper:
            obj = bpy.data.objects[path.objectName]
            M = obj.matrix_world
            up = Vector((0.0, 0.0, 1.0))
            for edge in obj.data.edges:
                a = M * obj.data.vertices[edge.vertices[0]].co
                b = M * obj.data.vertices[edge.vertices[1]].co
                if str(edge.index) in path.revDirec:
                    a, b = b, a
                close = (2 * a + b) / 3
                far = (a + 2 * b) / 3
                mid = (a + b) / 2
                edgeVec = a - b
                perp = edgeVec.cross(up).normalized() * (edgeVec.length / 12)
                cm_draw.drawLine3D((0, 1, 0, 0.7), close + perp, far)
                cm_draw.drawLine3D((0, 1, 0, 0.7), close - perp, far)

    def modal(self, context, event):
        global activePath

        context.area.tag_redraw()

        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(
                self._handle_3d, 'WINDOW')
            activePath = None
            # Hack to force redraw
            bpy.context.scene.objects.active = bpy.context.scene.objects.active
            return {'CANCELLED'}
        if activePath != self.pathName:
            bpy.types.SpaceView3D.draw_handler_remove(
                self._handle_3d, 'WINDOW')
            # Hack to force redraw
            bpy.context.scene.objects.active = bpy.context.scene.objects.active
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        global activePath
        activePath = self.pathName
        args = (context, bpy.context.scene.cm_paths.coll[self.pathName])

        self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(
            self.drawCallback, args, 'WINDOW', 'POST_VIEW')
        # self._handle_2d = bpy.types.SpaceView3D.draw_handler_add(cm_draw.draw_callback_2d, args, 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)

        # Hack to force redraw
        bpy.context.scene.objects.active = bpy.context.scene.objects.active
        return {'RUNNING_MODAL'}


class path_entry(PropertyGroup):
    """For storing a single path"""
    # name - aliase given to the path
    objectName = StringProperty(name="Object Name")
    radius = FloatProperty(name="Radius", min=0)
    mode = EnumProperty(name="Mode",
                        items=[("bidirectional", "Bidirectional", "", 1),
                               ("road", "Road", "", 2),
                               ("directional", "Directional", "", 3)])
    laneSeparation = FloatProperty(name="Lane Separation")
    revDirec = CollectionProperty(name="Directions", type=PropertyGroup)


class paths_collection(PropertyGroup):
    coll = CollectionProperty(type=path_entry)
    index = IntProperty()


class SCENE_OT_cm_path_populate(Operator):
    bl_idname = "scene.cm_paths_populate"
    bl_label = "Add A Path"

    def execute(self, context):
        item = context.scene.cm_paths.coll.add()
        return {'FINISHED'}


class SCENE_OT_cm_path_remove(Operator):
    bl_idname = "scene.cm_paths_remove"
    bl_label = "Remove A Path"

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
        layout.prop(item, "mode")
        if item.mode == "road":
            layout.prop(item, "laneSeparation")
        if item.mode == "directional":
            if bpy.context.scene.objects.active == bpy.data.objects[item.objectName]:
                oper = layout.operator("view3d.draw_path_operator")
                oper.pathName = item.name


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
        row.operator(cm_path_bfs.bl_idname)
        row.operator(cm_path_dfs.bl_idname)

        row = layout.row()
        row.operator(Switch_Selected_Path.bl_idname)
        row.operator(Switch_Connected_Path.bl_idname)

        row = layout.row()

        row.template_list("SCENE_UL_cm_path", "", sce.cm_paths,
                          "coll", sce.cm_paths, "index")

        col = row.column()
        sub = col.column(True)
        blid_ap = SCENE_OT_cm_path_populate.bl_idname
        sub.operator(blid_ap, text="", icon="ZOOMIN")
        blid_ar = SCENE_OT_cm_path_remove.bl_idname
        sub.operator(blid_ar, text="", icon="ZOOMOUT")

# ==========================================================================
#                       Path editing operators
# ==========================================================================


activePath = None


class Switch_Selected_Path(Operator):
    bl_idname = "view3d.cm_switch_selected_path"
    bl_label = "Switch The Direction Of The Selected Edges"

    @classmethod
    def poll(cls, context):
        global activePath
        C = bpy.context
        if activePath is None or activePath not in C.scene.cm_paths.coll:
            return False
        pathEntry = C.scene.cm_paths.coll[activePath]
        if pathEntry.mode != "directional":
            return False
        if C.active_object.mode != "EDIT":
            return False
        return True

    def invoke(self, context, event):
        bm = bmesh.from_edit_mesh(bpy.context.object.data)
        revDirec = bpy.context.scene.cm_paths.coll[activePath].revDirec
        for edge in bm.edges:
            if edge.select:
                indexStr = str(edge.index)
                if indexStr in revDirec:
                    revDirec.remove(revDirec.find(indexStr))
                else:
                    revEdge = revDirec.add()
                    revEdge.name = indexStr

        # Hack to force redraw
        bpy.context.scene.objects.active = bpy.context.scene.objects.active
        return {'FINISHED'}


class Switch_Connected_Path(Operator):
    bl_idname = "view3d.cm_switch_connected_path"
    bl_label = "Switch The Direction Of The Connected Edges"

    @classmethod
    def poll(cls, context):
        global activePath
        C = bpy.context
        if activePath is None or activePath not in C.scene.cm_paths.coll:
            return False
        pathEntry = C.scene.cm_paths.coll[activePath]
        if pathEntry.mode != "directional":
            return False
        if C.active_object.mode != "EDIT":
            return False
        return True

    def invoke(self, context, event):
        global activePath
        C = bpy.context
        pathEntry = C.scene.cm_paths.coll[activePath]
        bm = bmesh.from_edit_mesh(bpy.context.object.data)
        fringe = {v for v in bm.verts if v.select}
        seenEdges = {e for e in bm.edges if e.select}
        while len(fringe) > 0:
            nextFrige = set()
            for v in fringe:
                for e in v.link_edges:
                    if e not in seenEdges:
                        indexStr = str(e.index)
                        if indexStr in pathEntry.revDirec:
                            toRm = pathEntry.revDirec.find(indexStr)
                            pathEntry.revDirec.remove(toRm)
                        else:
                            revEdge = pathEntry.revDirec.add()
                            revEdge.name = indexStr
                        other = e.other_vert(v)
                        nextFrige.add(other)
                        seenEdges.add(e)
            fringe = nextFrige

        # Hack to force redraw
        bpy.context.scene.objects.active = bpy.context.scene.objects.active
        return {'FINISHED'}


class cm_path_bfs(Operator):
    bl_idname = "view3d.cm_paths_bfs"
    bl_label = "Breadth First Search To Direct Edges"

    @classmethod
    def poll(cls, context):
        global activePath
        C = bpy.context
        if activePath is None or activePath not in C.scene.cm_paths.coll:
            return False
        pathEntry = C.scene.cm_paths.coll[activePath]
        if pathEntry.mode != "directional":
            return False
        if C.active_object.mode != "EDIT":
            return False
        return True

    def execute(self, context):
        global activePath
        C = bpy.context
        pathEntry = C.scene.cm_paths.coll[activePath]
        bm = bmesh.from_edit_mesh(C.active_object.data)

        fringe = {v for v in bm.verts if v.select}
        seen = {v for v in bm.verts if v.select}
        while len(fringe) > 0:
            nextFrige = set()
            for v in fringe:
                for e in v.link_edges:
                    other = e.other_vert(v)
                    if other not in seen:
                        indexStr = str(e.index)
                        if v.index == e.verts[0].index:
                            if indexStr in pathEntry.revDirec:
                                toRm = pathEntry.revDirec.find(indexStr)
                                pathEntry.revDirec.remove(toRm)
                        else:
                            if indexStr not in pathEntry.revDirec:
                                revEdge = pathEntry.revDirec.add()
                                revEdge.name = indexStr
                        nextFrige.add(other)
                seen.add(v)
            fringe = nextFrige

        # Hack to force redraw
        bpy.context.scene.objects.active = bpy.context.scene.objects.active
        return {'FINISHED'}


class cm_path_dfs(Operator):
    bl_idname = "view3d.cm_paths_dfs"
    bl_label = "Depth First Search To Direct Edges"

    @classmethod
    def poll(cls, context):
        global activePath
        C = bpy.context
        if activePath is None or activePath not in C.scene.cm_paths.coll:
            return False
        pathEntry = C.scene.cm_paths.coll[activePath]
        if pathEntry.mode != "directional":
            return False
        if C.active_object.mode != "EDIT":
            return False
        return True

    def dfs(self, startVert):
        stack = [startVert]
        while len(stack) > 0:
            v = stack.pop()
            for e in v.link_edges:
                if e not in self.seen:
                    other = e.other_vert(v)
                    indexStr = str(e.index)
                    if v.index == e.verts[0].index:
                        if indexStr in self.pathEntry.revDirec:
                            toRm = self.pathEntry.revDirec.find(indexStr)
                            self.pathEntry.revDirec.remove(toRm)
                    else:
                        if indexStr not in self.pathEntry.revDirec:
                            revEdge = self.pathEntry.revDirec.add()
                            revEdge.name = indexStr
                    self.seen.add(e)
                    stack.append(other)

    def execute(self, context):
        global activePath
        C = bpy.context
        self.pathEntry = C.scene.cm_paths.coll[activePath]
        bm = bmesh.from_edit_mesh(C.active_object.data)

        self.seen = {e for e in bm.edges if e.select}
        for v in {v for v in bm.verts if v.select}:
            self.dfs(v)

        # Hack to force redraw
        bpy.context.scene.objects.active = bpy.context.scene.objects.active
        return {'FINISHED'}


def register():
    bpy.utils.register_class(draw_path_directions_operator)
    bpy.utils.register_class(path_entry)
    bpy.utils.register_class(paths_collection)
    bpy.utils.register_class(SCENE_OT_cm_path_populate)
    bpy.utils.register_class(SCENE_OT_cm_path_remove)
    bpy.utils.register_class(SCENE_UL_cm_path)
    bpy.utils.register_class(SCENE_PT_path)
    bpy.utils.register_class(Switch_Selected_Path)
    bpy.utils.register_class(Switch_Connected_Path)
    bpy.utils.register_class(cm_path_bfs)
    bpy.utils.register_class(cm_path_dfs)
    bpy.types.Scene.cm_paths = PointerProperty(type=paths_collection)


def unregister():
    bpy.utils.unregister_class(draw_path_directions_operator)
    bpy.utils.unregister_class(path_entry)
    bpy.utils.unregister_class(paths_collection)
    bpy.utils.unregister_class(SCENE_OT_cm_path_populate)
    bpy.utils.unregister_class(SCENE_OT_cm_path_remove)
    bpy.utils.unregister_class(SCENE_UL_cm_path)
    bpy.utils.unregister_class(SCENE_PT_path)
    bpy.utils.unregister_class(Switch_Selected_Path)
    bpy.utils.unregister_class(Switch_Connected_Path)
    bpy.utils.unregister_class(cm_path_bfs)
    bpy.utils.unregister_class(cm_path_dfs)
    del bpy.types.Scene.cm_paths
