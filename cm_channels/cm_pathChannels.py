import bpy
import mathutils
from mathutils import Vector
Rotation = mathutils.Matrix.Rotation
Euler = mathutils.Euler
import math
import bmesh

from .cm_masterChannels import MasterChannel as Mc

class Path(Mc):
    """Used to access data about paths in the scene"""
    def __init__(self, sim):
        Mc.__init__(self, sim)

        self.pathObjectCache = {}
        self.resultsCache = {}

    def newframe(self):
        self.pathObjectCache = {}
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

        startDistFac = (co_find - start).length / radius

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

        kd, bm, pathMatrixInverse, rotation = self.calcPathData(pathObject)

        obj = context.scene.objects[pathObject]
        vel = self.sim.agents[self.userid].globalVelocity * lookahead
        vel = vel * rotation
        co_find = pathMatrixInverse * context.scene.objects[self.userid].location
        co, index, dist = kd.find(co_find)
        offset = self.followPath(bm, co, index, vel, co_find, radius)

        offset = offset * pathMatrixInverse

        eul = Euler([-x for x in context.scene.objects[self.userid].rotation_euler], 'ZYX')
        offset.rotate(eul)

        return offset

    def rz(self, pathObject, radius, lookahead=25):
        target = None
        if self.userid in self.resultsCache:
            target = self.resultsCache[self.userid]
        target = self.calcRelativeTarget(pathObject, radius, lookahead)

        return math.atan2(target[0], target[1])/math.pi

    def rx(self, pathObject, radius, lookahead=25):
        target = None
        if self.userid in self.resultsCache:
            target = self.resultsCache[self.userid]
        target = self.calcRelativeTarget(pathObject, radius, lookahead)

        return math.atan2(target[2], target[1])/math.pi
