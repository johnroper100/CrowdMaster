import math

def relativeRotation(toLocX, toLocY, toLocZ,
                     fromLocX, fromLocY, fromLocZ,
                     rotX, rotY, rotZ):
    """targetX = toLocX - fromLocX
    targetY = toLocY - fromLocY
    targetZ = toLocZ - fromLocZ

    ca = math.cos(targetX)
    cb = math.cos(targetY)
    cc = math.cos(targetZ)
    sa = math.sin(targetX)
    sb = math.sin(targetY)
    sc = math.sin(targetZ)

    R11 = cb * cc
    R21 = -cb * sc
    R31 = sb
    R12 = ca * sc + sa * sb * cc
    R22 = ca * cc - sa * sb * sc
    R23 = -sa * cb
    R13 = sa * sc - ca * sb * cc
    R32 = sa * cc + ca * sb * sc
    R33 = ca * cb

    relativeX = targetX * R11 + targetY * R21 + targetZ * R31
    relativeY = targetX * R12 + targetY * R22 + targetZ * R32
    relativeZ = targetX * R13 + targetY * R23 + targetZ * R33

    changez = math.atan2(relativeX, relativeY)/math.pi
    changex = math.atan2(relativeZ, relativeY)/math.pi11

    return changez, changex"""
    return 1
