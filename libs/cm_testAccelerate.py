import bpy
import mathutils
import math
import random
import time

from . import cm_accelerate

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


class AccelerateTestCase(unittest.TestCase):
    def testRelativeRotation(self):
        to = mathutils.Vector((1, 2, 3))
        ag = mathutils.Vector((3, 2, 1))
        rotation = mathutils.Vector((math.pi, 0, 0))

        py = pythonRelativeRotation(to, ag, rotation)
        m = cm_accelerate.makeRotationMatrix(rotation.x, rotation.y, rotation.z)
        cy = cm_accelerate.relativeRotation(to.x, to.y, to.z,
                                            ag.x, ag.y, ag.z,
                                            m)
        self.assertAlmostEqual(py[0], cy[0])
        self.assertAlmostEqual(py[1], cy[1])
