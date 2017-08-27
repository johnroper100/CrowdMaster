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
from random import choice, randrange

logger = logging.getLogger("CrowdMaster")


try:
    from ins_vector import Vector, sortAlongLine
except:
    from .ins_vector import Vector, sortAlongLine


def clusterMatch(sources, targets, srcAccessFunc, trgAccessFunc):
    """
    :param sources: a list of objects representing the sources
    :param targets: a list of objects representing the targets
    :param srcAccessFunc: a function that given an element from sources will
                            give back (x, y, z).
    :param trgAccessFunc: a function that given an element from targets will
                            give back (x, y, z).
    """
    t = [(x[0], Vector(trgAccessFunc(x[1]))) for x in enumerate(targets)]
    s = [(x[0], Vector(srcAccessFunc(x[1]))) for x in enumerate(sources)]
    result = matchGroups(s, t)
    check = [(x[0][0], x[1][0]) for x in result[1]]
    fst = [x[0] for x in check]
    scd = [x[1] for x in check]
    if len(set(fst)) != len(fst) or len(set(scd)) != len(scd):
        logger.info("Match produced duplicates")
    return result


def KMean2(points, groups=None):
    """
    :param points: [(enumerate, Vector)]
    :param groups: None or [(enumerate, Vector), (enumerate, Vector)]
                            group 1              group 2
    """
    assert isinstance(points[0][0], int) and isinstance(points[0][1], Vector),\
        "points is in the wrong format"
    if groups:
        group1pos = Vector()
        for p in groups[0]:
            group1pos += p[1]
        group1pos /= len(groups[0])

        group2pos = Vector()
        for p in groups[1]:
            group2pos += p[1]
        group2pos /= len(groups[1])
    else:
        group1pos = choice(points)[1]
        group2pos = choice(points)[1]
        while group1pos == group2pos:
            group2pos = choice(points)[1]

    assert isinstance(group1pos, Vector), "Should be converted to Vector"
    assert isinstance(group2pos, Vector), "Should be converted to Vector"

    groups = [[], []]

    for p in points:
        d1 = (p[1].x - group1pos.x)**2 + (p[1].y - group1pos.y)**2 \
            + (p[1].z - group1pos.z)**2
        d2 = (p[1].x - group2pos.x)**2 + (p[1].y - group2pos.y)**2 \
            + (p[1].z - group2pos.z)**2
        if d1 < d2:
            groups[0].append(p)
        else:
            groups[1].append(p)

    assert len(groups[0]) != 0 and len(groups[1]) != 0, "ERROR" + str(groups)

    return groups, group1pos, group2pos


def iterateKMean2(points, iterations=5):
    """
    :type points: [(int, Vector)]
    """
    groups = None
    for i in range(iterations):
        groups, group1pos, group2pos = KMean2(points, groups=groups)
    return groups, group1pos, group2pos


def splitGroupOnLine(points, group1pos, group2pos, groupSizes):
    """
    :type points: [(int, Vector)]
    :type group1pos: Vector
    :type group2pos: Vector
    :type groupSizes: (int, int)
    """
    if len(points) > sum(groupSizes):
        return False
    order = sortAlongLine(points, group1pos, group2pos, access=lambda x: x[1],
                          incTValue=True)
    # typ order: [(float, (int, Vector))]
    #          t value, objIndex, position
    groups = [[], []]
    for o in order:
        if o[0] < 0.5:
            groups[0].append(o[1])
        else:
            groups[1].append(o[1])
    while len(groups[0]) > groupSizes[0]:
        groups[1].append(groups[0].pop())
    while len(groups[1]) > groupSizes[1]:
        groups[0].append(groups[1].pop(0))
    return groups


def matchGroups(sources, targets):
    """
    returns False if not all the sources match and a list of tuples of the
    indexes of pairs and the paired objects.

    :type sources: [(int, Vector)]
    :type targets: [(int, Vector)]

    """
    if len(sources) == 0:
        # This occurs when there are more targets than sources
        return True, []

    assert isinstance(targets[0][0], int), "Actual val" + str(targets[0])
    assert isinstance(sources[0][0], int), "Actual val" + str(sources[0])

    if len(sources) > len(targets):
        return False, sources
    elif len(sources) == 1:
        if len(targets) == 1:
            return True, [(sources[0], targets[0])]
        closest = min(targets, key=lambda x: x[1].x**2 + x[1].y**2 + x[1].z**2)
        return True, [(sources[0], closest)]
    else:
        t1, t2, t3 = iterateKMean2(targets)
        s1 = splitGroupOnLine(sources, t2, t3,
                              groupSizes=(len(t1[0]), len(t1[1])))

        group1Success, group1 = matchGroups(s1[0], t1[0])
        assert group1Success, "Something has gone wrong in matchGroups"
        group2Success, group2 = matchGroups(s1[1], t1[1])
        assert group2Success, "Something has gone wrong in matchGroups"
        return True, group1 + group2
