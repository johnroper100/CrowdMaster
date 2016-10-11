# Copyright 2016 CrowdMaster Developer Team
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

from random import randrange, choice

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
        print("Match produced duplicates")
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

    assert isinstance(targets[0][0], int), "Actual val"+str(targets[0])
    assert isinstance(sources[0][0], int), "Actual val"+str(sources[0])

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

# ======================================================================

# ============================== TESTING ===============================

# ======================================================================

if __name__ == "__main__":
    # For testing purposes
    import sys
    from PySide import QtGui, QtCore
    import time

    startMoving = False

    class agent(QtGui.QGraphicsItem):
        def __init__(self, radius, x, y):
            QtGui.QGraphicsItem.__init__(self)
            self.radius = radius
            self.setPos(x, y)
            self.inGroup1 = True
            self.isGroupMarker = False
            self.goingTo = None

        def boundingRect(self):
            """sets the area that is updated by drawing"""
            adjust = 4.0
            return QtCore.QRectF(-self.radius - adjust, -self.radius - adjust,
                                 2 * self.radius + 2 * adjust,
                                 2 * self.radius + 2 * adjust)

        def paint(self, painter, option, widget):
            if self.isGroupMarker:
                painter.setPen(QtGui.QPen(QtCore.Qt.black, 10))
            elif self.inGroup1:
                painter.setPen(QtGui.QPen(QtCore.Qt.blue, 1))
            else:
                painter.setPen(QtGui.QPen(QtCore.Qt.red, 1))
            bounding = QtCore.QRect(-self.radius, -self.radius,
                                    2 * self.radius, 2 * self.radius)
            painter.drawEllipse(bounding)
            self.update()

        def move(self):
            if self.goingTo:
                newX = (49*self.pos().x() + self.goingTo.x())/50
                newY = (49*self.pos().y() + self.goingTo.y())/50
                self.setPos(newX, newY)

    class target(QtGui.QGraphicsItem):
        def __init__(self, radius, x, y):
            QtGui.QGraphicsItem.__init__(self)
            self.radius = radius
            self.setPos(x, y)
            self.inGroup1 = True
            self.isGroupMarker = False

        def boundingRect(self):
            """sets the area that is updated by drawing"""
            adjust = 4.0
            return QtCore.QRectF(-self.radius - adjust, -self.radius - adjust, 2 * self.radius + 2 * adjust, 2 * self.radius + 2 * adjust)

        def paint(self, painter, option, widget):
            if self.isGroupMarker:
                painter.setPen(QtGui.QPen(QtCore.Qt.darkGreen, 10))
            elif self.inGroup1:
                painter.setPen(QtGui.QPen(QtCore.Qt.magenta, 1))
            else:
                painter.setPen(QtGui.QPen(QtCore.Qt.yellow, 1))
            bounding = QtCore.QRect(-self.radius,
                                    -self.radius, 2 * self.radius,
                                    2 * self.radius)
            painter.drawEllipse(bounding)
            self.update()

        def move(self):
            self.setPos(self.pos().x() + randrange(-2, 2), self.pos().y() + randrange(-2, 2))
            if self.pos().x() >= 600:
                self.setPos(599, self.pos().y())
            elif self.pos().x() <= -600:
                self.setPos(-599, self.pos().y())
            if self.pos().y() >= 400:
                self.setPos(self.pos().x(), 399)
            elif self.pos().y() <= -400:
                self.setPos(self.pos().x(), -399)

    class View(QtGui.QGraphicsView):
        def __init__(self):
            QtGui.QGraphicsView.__init__(self)

            self.scene = QtGui.QGraphicsScene(self)
            self.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
            self.scene.setSceneRect(-600, -600, 1200, 1200)
            self.setScene(self.scene)
            self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
            self.setRenderHint(QtGui.QPainter.Antialiasing)
            self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
            self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

            self.setBackgroundBrush(QtCore.Qt.lightGray)

            self.scale(0.8, 0.8)
            self.setMinimumSize(1500, 900)
            self.setWindowTitle(self.tr("Clustering test"))

            self.agents = []
            noofagents = 40*8

            for f in range(noofagents):
                item = agent(5, (randrange(-800, 800)), (randrange(-600, 600)))
                self.scene.addItem(item)
                self.agents.append(item)

            self.targets = []
            """nooftargets = 110

            for f in range(nooftargets):
                item = target(7, (randrange(-900, 900)),
                                 (randrange(-200, 200)))
                self.scene.addItem(item)
                self.targets.append(item)"""

            rows = 40
            columns = 8
            for row in range(rows):
                for col in range(columns):
                    item = target(7, -500 + 1100*row/rows,
                                  -100 + 250*col/columns)
                    self.scene.addItem(item)
                    self.targets.append(item)

            accessFunc = lambda x: (x.pos().x(), x.pos().y(), 0)

            t = time.time()
            success, pairings = clusterMatch(self.agents, self.targets,
                                             accessFunc, accessFunc)
            print(time.time()-t)
            assert success, "There was a problem executing clusterMatch"

            for p in pairings:
                self.agents[p[0][0]].goingTo = p[1][1]

            self.timer = QtCore.QTimer(self)
            self.connect(self.timer, QtCore.SIGNAL("timeout()"),  self.step)
            self.timer.start(50)

        def step(self):
            global startMoving
            if startMoving:
                for a in self.agents:
                    a.move()

        def mousePressEvent(self, event):
            global startMoving
            startMoving = True

    app = QtGui.QApplication(sys.argv)

    widget = View()
    widget.show()

    sys.exit(app.exec_())
