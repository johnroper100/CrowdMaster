import bpy
import mathutils
from mathutils import Vector
Rotation = mathutils.Matrix.Rotation
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

        # context.scene.objects["Empty.005"].location = start

        next = nextVert.index

        while True:
            currentVert = bm.verts[index].co
            nextVert = bm.verts[next].co

            length = (nextVert - currentVert).length
            if lVel < length:
                fac = lVel/length
                target = currentVert * (1 - fac) + nextVert * fac
                # context.scene.objects["Empty.003"].location = target
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
            nextVert = None

            endOfPath = True
            for e in edges:
                if e.verts[0].index != index and e.verts[1].index != index:
                    endOfPath = False
                    otherVert = e.verts[0] if e.verts[0].index != next else e.verts[1]
                    score = (otherVert.co - bm.verts[next].co).normalized().dot(nVel)
                    if score > bestScore:
                        bestScore = score
                        nextVert = otherVert
            if endOfPath:
                rCorrect = start - co_find
                offTargetDist = rCorrect.length - radius
                if offTargetDist > 0:
                    rCorrect *= (offTargetDist / rCorrect.length)
                    return target - start + rCorrect
                    # Also add here for variable length path
                return target - start

            index = next
            next = nextVert.index


    def calcRelativeTarget(self, pathObject, radius, lookahead):
        context = bpy.context

        kd, bm, pathMatrixInverse, rotation = self.calcPathData(pathObject)

        obj = context.scene.objects[pathObject]
        vel = self.sim.agents[self.userid].globalVelocity
        vel = vel * rotation
        co_find = pathMatrixInverse * context.scene.objects[self.userid].location
        co, index, dist = kd.find(co_find)
        offset = self.followPath(bm, co, index, vel, co_find, radius)

        x, y, z = obj.rotation_euler

        if x != 0.0 or y != 0.0 or z != 0.0:
            z = Rotation(-obj.rotation_euler[2], 4, 'Z')
            y = Rotation(-obj.rotation_euler[1], 4, 'Y')
            x = Rotation(-obj.rotation_euler[0], 4, 'X')

            rotation = x * y * z
            offset = offset * rotation

        if x != 0.0 or y != 0.0 or z != 0.0:
            z = Rotation(context.scene.objects[self.userid].rotation_euler[2], 4, 'Z')
            y = Rotation(context.scene.objects[self.userid].rotation_euler[1], 4, 'Y')
            x = Rotation(context.scene.objects[self.userid].rotation_euler[0], 4, 'X')

            rotation = x * y * z
            return offset * rotation

        return offset

    def rz(self, pathObject, radius, lookahead=5):
        target = None
        if self.userid in self.resultsCache:
            target = self.resultsCache[self.userid]
        target = self.calcRelativeTarget(pathObject, radius, lookahead)

        ag = bpy.context.scene.objects[self.userid]

        z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
        y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
        x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

        rotation = x * y * z
        relative = target * rotation

        return math.atan2(relative[0], relative[1])/math.pi

    def rx(self, pathObject, radius, lookahead=5):
        target = None
        if self.userid in self.resultsCache:
            target = self.resultsCache[self.userid]
        target = self.calcRelativeTarget(pathObject, radius, lookahead)

        ag = bpy.context.scene.objects[self.userid]

        z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
        y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
        x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

        rotation = x * y * z
        relative = target * rotation

        return math.atan2(relative[2], relative[1])/math.pi
