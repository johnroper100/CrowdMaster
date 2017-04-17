import bpy
import mathutils
import math
import random
import time

from . import cm_soundAccel

import unittest

def pythonRelativeRotation(to, ag, rotation):
    target = to - ag

    z = mathutils.Matrix.Rotation(rotation[2], 4, 'Z')
    y = mathutils.Matrix.Rotation(rotation[1], 4, 'Y')
    x = mathutils.Matrix.Rotation(rotation[0], 4, 'X')

    rotation = x * y * z

    relative = target * rotation

    changez = math.atan2(relative[0], relative[1])/math.pi
    changex = math.atan2(relative[2], relative[1])/math.pi

    return changez, changex


class SoundAccelTestCase(unittest.TestCase):
    def testRelativeRotation(self):
        to = mathutils.Vector((1, 2, 3))
        ag = mathutils.Vector((3, 2, 1))
        rotation = mathutils.Vector((math.pi, 0, 0))

        py = pythonRelativeRotation(to, ag, rotation)
        m = cm_soundAccel.makeRotationMatrix(rotation.x, rotation.y, rotation.z)
        cy = cm_soundAccel.relativeRotation(to.x, to.y, to.z,
                                            ag.x, ag.y, ag.z,
                                            m)
        self.assertAlmostEqual(py[0], cy[0])
        self.assertAlmostEqual(py[1], cy[1])


class SoundAccelTimingCase(unittest.TestCase):
    def testRelativeRotationTiming(self):
        ITERATIONS = 1
        tos = []
        ag = bpy.context.scene.objects["Cube"].location
        rot = bpy.context.scene.objects["Cube"].rotation_euler
        for f in range(ITERATIONS):
            tos.append(mathutils.Vector((random.random() * 100,
                                         random.random() * 100,
                                         random.random() * 100)))
        t = time.time()
        for f in range(ITERATIONS):
            r = pythonRelativeRotation(tos[f], ag, rot)
            print(r)
        py = time.time() - t

        t = time.time()
        for f in range(ITERATIONS):
            m = cm_soundAccel.makeRotationMatrix(rot.x, rot.y, rot.z)
            r = cm_soundAccel.relativeRotation(tos[f].x, tos[f].y, tos[f].z,
                                               ag.x, ag.y, ag.z,
                                               m)
            print(r)
        cy = time.time() - t

        t = time.time()
        m = cm_soundAccel.makeRotationMatrix(rot.x, rot.y, rot.z)
        for f in range(ITERATIONS):
            r = cm_soundAccel.relativeRotation(tos[f].x, tos[f].y, tos[f].z,
                                               ag.x, ag.y, ag.z, m)
            print(r)
        cym = time.time() - t

        t = time.time()
        m = bpy.context.scene.objects["Cube"].matrix_world.inverted()
        for f in range(ITERATIONS):
            r = tos[f] * m
            changez = math.atan2(r.x, r.y)/math.pi
            changex = math.atan2(r.z, r.y)/math.pi
            print((changez, changex))
        pyi = time.time() - t

        t = time.time()
        for f in range(ITERATIONS):
            m = bpy.context.scene.objects["Cube"].matrix_world.inverted()
            r = tos[f] * m
            changez = math.atan2(r.x, r.y)/math.pi
            changex = math.atan2(r.z, r.y)/math.pi
            print((changez, changex))
        pyio = time.time() - t

        self.assertGreaterEqual(py, cy)
        # eg. py == 0.0026421546936035156, cy == 0.0021142959594726562
        print(py)
        print(cy)
        print(cym)
        print(pyi)
        print(pyio)
