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

import math

cdef float invPi = 1 / math.pi

cdef struct s_matrix:
    float R11
    float R21
    float R31
    float R12
    float R22
    float R32
    float R13
    float R23
    float R33

ctypedef s_matrix matrix

def makeRotationMatrix(float rotX, float rotY, float rotZ):
    cdef float ca = math.cos(rotX)
    cdef float cb = math.cos(rotY)
    cdef float cc = math.cos(rotZ)
    cdef float sa = math.sin(rotX)
    cdef float sb = math.sin(rotY)
    cdef float sc = math.sin(rotZ)

    cdef float sasb = sa * sb
    cdef float casc = ca * sc
    cdef float cacc = ca * cc

    cdef matrix m

    m.R11 = cb * cc
    m.R21 = -cb * sc
    m.R31 = sb
    m.R12 = casc + (sasb * cc)
    m.R22 = cacc - (sasb * sc)
    m.R32 = -sa * cb
    m.R13 = (sa * sc) - (cacc * sb)
    m.R23 = (sa * cc) + (casc * sb)
    m.R33 = ca * cb

    return m

def relativeRotation(float toLocX, float toLocY, float toLocZ,
                      float fromLocX, float fromLocY, float fromLocZ,
                      matrix rot):
        cdef float targetX = toLocX - fromLocX
        cdef float targetY = toLocY - fromLocY
        cdef float targetZ = toLocZ - fromLocZ

        cdef float relativeX = targetX * rot.R11 + targetY * rot.R12 + targetZ * rot.R13
        cdef float relativeY = targetX * rot.R21 + targetY * rot.R22 + targetZ * rot.R23
        cdef float relativeZ = targetX * rot.R31 + targetY * rot.R32 + targetZ * rot.R33

        changez = math.atan2(relativeX, relativeY) * invPi
        changex = math.atan2(relativeZ, relativeY) * invPi

        return changez, changex

def neuronColour(float total, Py_ssize_t length):
    cdef float hueChange
    cdef float absav

    cdef float hue
    cdef float sat
    cdef float val

    if length > 0:
        val = 1
        av = total / length

        if av > 0:
            startHue = 0.333
            absav = av
        else:
            startHue = 0.5
            absav = -av

        if av > 1:
            hueChange = absav
            hueChange += 1
            hueChange /= -absav
            hueChange += 2
            hueChange /= -3
            hue = 0.333 + hueChange
        elif av < -1:
            hueChange = absav
            hueChange += 1
            hueChange /= -absav
            hueChange += 2
            hueChange /= 3
            hue = 0.5 + hueChange
        else:
            hue = startHue

        if absav < 1:
            sat = math.sqrt(absav)
        else:
            sat = 1
    else:
        hue = 0
        sat = 0
        val = 0.5
    return hue, sat, val
