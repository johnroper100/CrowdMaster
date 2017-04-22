import math
import random
import time
import unittest

import bpy
import mathutils

from . import cm_accelerate


def pythonRelativeRotation(to, ag, rotation):
    target = to - ag

    z = mathutils.Matrix.Rotation(rotation[2], 4, 'Z')
    y = mathutils.Matrix.Rotation(rotation[1], 4, 'Y')
    x = mathutils.Matrix.Rotation(rotation[0], 4, 'X')

    rotation = x * y * z

    relative = target * rotation

    changez = math.atan2(relative[0], relative[1]) / math.pi
    changex = math.atan2(relative[2], relative[1]) / math.pi

    return changez, changex


class AccelerateTestCase(unittest.TestCase):
    def testRelativeRotation(self):
        to = mathutils.Vector((1, 2, 3))
        ag = mathutils.Vector((3, 2, 1))
        rotation = mathutils.Vector((math.pi, 0, 0))

        py = pythonRelativeRotation(to, ag, rotation)
        m = cm_accelerate.makeRotationMatrix(
            rotation.x, rotation.y, rotation.z)
        cy = cm_accelerate.relativeRotation(to.x, to.y, to.z,
                                            ag.x, ag.y, ag.z,
                                            m)
        self.assertAlmostEqual(py[0], cy[0])
        self.assertAlmostEqual(py[1], cy[1])

    def testRelativeRotation2(self):
        to = mathutils.Vector((1, 2, 3))
        ag = mathutils.Vector((3, 2, 1))
        rotation = mathutils.Vector((1, 0, 1))

        py = pythonRelativeRotation(to, ag, rotation)
        m = cm_accelerate.makeRotationMatrix(
            rotation.x, rotation.y, rotation.z)
        cy = cm_accelerate.relativeRotation(to.x, to.y, to.z,
                                            ag.x, ag.y, ag.z,
                                            m)
        self.assertAlmostEqual(py[0], cy[0], 6)
        self.assertAlmostEqual(py[1], cy[1], 6)

    def testNeuronColour(self):
        output = {"a": 1, "b": 2.5, "c": 2.53}
        if output:
            val = 1
            av = sum(output.values()) / len(output)
            if av > 0:
                startHue = 0.333
            else:
                startHue = 0.5

            if av > 1:
                hueChange = -(-(abs(av) + 1) / abs(av) + 2) * (1 / 3)
                hue = 0.333 + hueChange
                sat = 1
            elif av < -1:
                hueChange = (-(abs(av) + 1) / abs(av) + 2) * (1 / 3)
                hue = 0.5 + hueChange
                sat = 1
            else:
                hue = startHue

            if abs(av) < 1:
                sat = abs(av)**(1 / 2)
            else:
                sat = 1
        else:
            hue = 0
            sat = 0
            val = 0.5
        h, s, v = cm_accelerate.neuronColour(sum(output.values()), len(output))
        self.assertAlmostEqual(hue, h, 6)
        self.assertAlmostEqual(sat, s, 6)
        self.assertAlmostEqual(val, v, 6)

    def testNeuronColour2(self):
        output = {"a": 1, "b": -2.5, "c": -2.53}
        if output:
            val = 1
            av = sum(output.values()) / len(output)
            if av > 0:
                startHue = 0.333
            else:
                startHue = 0.5

            if av > 1:
                hueChange = -(-(abs(av) + 1) / abs(av) + 2) * (1 / 3)
                hue = 0.333 + hueChange
                sat = 1
            elif av < -1:
                hueChange = (-(abs(av) + 1) / abs(av) + 2) * (1 / 3)
                hue = 0.5 + hueChange
                sat = 1
            else:
                hue = startHue

            if abs(av) < 1:
                sat = abs(av)**(1 / 2)
            else:
                sat = 1
        else:
            hue = 0
            sat = 0
            val = 0.5
        h, s, v = cm_accelerate.neuronColour(sum(output.values()), len(output))
        self.assertAlmostEqual(hue, h, 6)
        self.assertAlmostEqual(sat, s, 6)
        self.assertAlmostEqual(val, v, 6)
