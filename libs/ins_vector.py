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

try:
    from mathutils import Vector
except:
    class Vector:
        def __init__(self, *args):
            if args:
                self._vec = args[0]
            else:
                self._vec = (0, 0, 0)

        def __add__(self, add):
            """Returns the two vectors added together element wise. If one of
            the vectors has a higher dimension it will be reduced to the same
            dimension as the lower vector"""
            return Vector([a + b for a, b in zip(self, add)])

        def __iadd__(self, add):
            """additions for += operator"""
            return Vector([a + b for a, b in zip(self, add)])

        def __sub__(self, sub):
            return Vector([a - b for a, b in zip(self, sub)])

        def __iter__(self):
            return iter(self._vec)

        def __len__(self):
            return len(self._vec)

        def __getitem__(self, key):
            return self._vec[key]

        @property
        def x(self):
            return self[0]

        @property
        def y(self):
            return self[1]

        @property
        def z(self):
            return self[2]

        def dot(self, other):
            """Returns the dot product of the two vectors. If one of the
            vectors has a higher dimension it will be reduced to the same
            dimension as the lower vector"""
            return sum([a * b for a, b in zip(self, other)])

        def __mul__(self, mul):
            if isinstance(mul, int) or isinstance(mul, float):
                return Vector([x * mul for x in self])
            else:
                return self.dot(mul)

        def __rmul__(self, mul):
            return self.__mul__(self, mul)

        def __truediv__(self, div):
            if isinstance(div, int) or isinstance(div, float):
                return Vector([x / div for x in self])

        def __itruediv__(self, div):
            if isinstance(div, int) or isinstance(div, float):
                return Vector([x / div for x in self])

        @property
        def length(self):
            return sum([x**2 for x in self])

        def __eq__(self, eq):
            if not isinstance(eq, Vector) or (self.length() != eq.length()):
                return False
            for d1, d2 in zip(self._vec, eq._vec):
                if d1 != d2:
                    return False
            return True

        def __repr__(self):
            return "Vector" + self._vec.__str__()


def getClosestPoint(a, b, point, segmentClamp=False, returnFactor=False):
    """
    :param a: a is a point on the line
    :type a: Vector or tuple
    :param b: b is a point on the line
    :type b: Vector or tuple
    :param point: a point in the same dimensions as a and b
    :type point: Vector or tuple
    :returns: the closest point on the line ab or a float if returnFactor
    """
    if not isinstance(a, Vector):
        a = Vector(*a)
    if not isinstance(b, Vector):
        b = Vector(*b)
    if not isinstance(point, Vector):
        point = Vector(*point)
    ap = point - a
    ab = b - a

    ab2 = ab.length
    ap_ab = ap * ab

    t = ap_ab / ab2  # type: float
    if segmentClamp:
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
    if returnFactor:
        return t
    closest = a + ab * t  # type: Vector
    return closest


def sortAlongLine(points, p1, p2, access=lambda x: x, incTValue=False):
    """
    :param points: A list of point to be sorted
    :type points: [Vector]
    :param p1: A point on the line representing the lower points
    :type p1: Vector
    :param p2: A point on the line representing the higher points
    :type p2: Vector
    :param access: a func that given an elements of points returns a Vector
    :param access: function that access coordinates from each element of points
    :type access: function

    :rtype: [(float, pointobj)] if incTValue else [pointobj]
    """
    pointVals = []
    for point in points:
        pointVals.append((getClosestPoint(p1, p2, access(point),
                                          returnFactor=True), point))
        # getClosestPoint returns a float when returnFactor is True
    pointVals = sorted(pointVals, key=lambda x: x[0])
    if incTValue:
        return pointVals
    return [x[1] for x in pointVals]


# EXAMPLE - sort points along line
"""
import bpy

objs = bpy.context.scene.objects

l1 = objs["Empty"].location
l2 = objs["Empty.001"].location

points = [objs["Empty.002"], objs["Empty.003"], objs["Empty.004"],
          objs["Empty.005"], objs["Empty.006"], objs["Empty.007"],
          objs["Empty.008"], objs["Empty.009"], objs["Empty.010"]]

for f in sortAlongLine(points, l1, l2, access=lambda x : x.location):
    print(f)
"""
