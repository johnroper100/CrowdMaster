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

from .cm_masterChannels import MasterChannel as Mc
from .cm_masterChannels import timeChannel
import math
import mathutils
Vector = mathutils.Vector

from ..libs import ins_octree as ot

import bpy


class Sound(Mc):
    """The object containing all of the sound channels"""
    def __init__(self, sim):
        Mc.__init__(self, sim)
        # All the different sound frequencies that were emitted last frame
        self.channels = {}

    def register(self, agent, frequency, val):
        """Adds an object that is emitting a sound"""
        if frequency not in self.channels:
            ch = Channel(frequency, self.sim)
            self.channels[frequency] = ch
        self.channels[frequency].register(agent.id, val)

    def retrieve(self, freq):
        """Get sound channel"""
        if freq in self.channels:
            return self.channels[freq]
        else:
            return None

    def newframe(self):
        self.channels = {}

    def setuser(self, userid):
        for chan in self.channels.values():
            chan.newuser(userid)
        Mc.setuser(self, userid)


class Channel:
    """Holds a record of all objects that are emitting on a
    certain frequency"""
    def __init__(self, frequency, sim):
        """
        :param frequency: The identifier for this channel
        :type frequency: String"""
        self.sim = sim

        self.emitters = []
        self.frequency = frequency
        # Temporary storage which is reset after each agents has used it
        self.store = {}
        self.storePrediction = {}
        self.storeSteering = {}

        self.predictNext = False
        self.steeringNext = False

        self.kdtree = None
        self.maxVal = 0

    def register(self, objectid, val):
        """Add an object that emits sound"""
        self.emitters.append((objectid, val))

    def newuser(self, userid):
        self.userid = userid
        self.store = {}
        self.storePrediction = {}
        self.storeSteering = {}

    def calculate(self):
        """Called the first time an agent uses this frequency"""
        O = bpy.context.scene.objects

        if self.kdtree is None:
            self.kdtree = mathutils.kdtree.KDTree(len(self.emitters))
            for i, item in enumerate(self.emitters):
                emitterid, val = item
                self.maxVal = max(self.maxVal, val)
                self.kdtree.insert(O[emitterid].location, i)

            self.kdtree.balance()

        ag = O[self.userid]

        collisions = self.kdtree.find_range(ag.location, self.maxVal)

        for (co, index, dist) in collisions:
            emitterid, val = self.emitters[index]
            if emitterid == self.userid:
                continue
            if dist <= val:
                to = O[emitterid]

                target = to.location - ag.location

                z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
                y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
                x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

                rotation = x * y * z
                relative = target * rotation

                changez = math.atan2(relative[0], relative[1])/math.pi
                changex = math.atan2(relative[2], relative[1])/math.pi
                self.store[emitterid] = {"rz": changez,
                                         "rx": changex,
                                         "distProp": dist/val}

    # Octree implementation
    """O = bpy.context.scene.objects
    userDim = self.sim.agents[self.userid].dimensions
    if self.octree is None:
        bss = []  # List of bounding spheres
        for emitterid, val in self.emitterDict.items():
            emitDim = self.sim.agents[emitterid].dimensions
            dim = (val + emitDim[a] + userDim[a] for a in range(3))
            bss.append(ot.boundingSphereFromBPY(O[emitterid], dim))
        self.octree = ot.createOctree(bss)
    ag = O[self.userid]
    collisions = self.octree.checkPoint(ag.location.to_tuple())
    for emitterid in collisions:
        if emitterid == self.userid:
            continue
        to = O[emitterid]
        val = self.emitterDict[emitterid]
        eDim = max(self.sim.agents[emitterid].dimensions)
        uDim = max(userDim)
        difx = to.location.x - ag.location.x
        dify = to.location.y - ag.location.y
        difz = to.location.z - ag.location.z
        dist = math.sqrt(difx**2 + dify**2 + difz**2)
        target = to.location - ag.location
        z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
        y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
        x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')
        rotation = x * y * z
        relative = target * rotation
        changez = math.atan2(relative[0], relative[1])/math.pi
        changex = math.atan2(relative[2], relative[1])/math.pi
        self.store[emitterid] = {"rz": changez,
                                 "rx": changex,
                                 "distProp": dist/(val+eDim+uDim)}"""
        # (z rot, x rot, dist proportion, time until prediction)"""

    # The old implementation not using octree
    """ag = O[self.userid]
    for emitterid, val in self.emitters.items():
        if emitterid != self.userid:
            to = O[emitterid]
            difx = to.location.x - ag.location.x
            dify = to.location.y - ag.location.y
            difz = to.location.z - ag.location.z
            dist = math.sqrt(difx**2 + dify**2 + difz**2)
            if dist <= val:
                target = to.location - ag.location
                z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
                y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
                x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')
                rotation = x * y * z
                relative = target * rotation
                changez = math.atan2(relative[0], relative[1])/math.pi
                changex = math.atan2(relative[2], relative[1])/math.pi
                self.store[emitterid] = (changez, changex, 1-(dist/val), 1)
                # (z rot, x rot, dist proportion, time until prediction)"""

    def calculatePrediction(self):
        """Called the first time an agent uses this frequency"""
        ag = O[self.userid]
        agSim = self.sim.agents[self.userid]
        for emitterid, val in self.emitters:
            if emitterid != self.userid:
                toSim = self.sim.agents[emitterid]

                p1 = mathutils.Vector((agSim.apx, agSim.apy, agSim.apz))
                p2 = mathutils.Vector((toSim.apx, toSim.apy, toSim.apz))

                d1 = mathutils.Vector(agSim.globalVelocity)
                d2 = mathutils.Vector(toSim.globalVelocity)

                a = d1.dot(d1)
                b = d1.dot(d2)
                e = d2.dot(d2)

                d = a*e - b*b

                if d != 0:  # If the two lines are not parallel.
                    r = p1 - p2
                    c = d1.dot(r)
                    f = d2.dot(r)

                    s = (b*f - c*e) / d
                    t = (a*f - b*c) / d
                    # t*d2 == closest point
                    # s*d2 == point 2 is at when 1 is at closest approach
                    pd1 = p1 + (s*d1)
                    pd2 = p2 + (s*d2)
                    dist = (pd1 - pd2).length
                else:
                    dist = float("inf")

                # pd1 and pd2 are the positions the agents will be when they
                #  make their closest approach
                if dist <= val:
                    target = pd2 - pd1

                    z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
                    y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
                    x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

                    rotation = x * y * z
                    relative = target * rotation

                    changez = math.atan2(relative[0], relative[1])/math.pi
                    changex = math.atan2(relative[2], relative[1])/math.pi
                    if (s < 1) or (t < 1):
                        cert = 0
                    else:
                        if s > 32:
                            c = 1
                        else:
                            c = s / 32
                        cert = (1 - ((-(c**3)/3 + (c**2)/2) * 6))**2
                        # https://www.desmos.com/calculator/godi4zejgd
                    self.storePrediction[emitterid] = {"rz": changez,
                                                       "changex": changex,
                                                       "distProp": dist/val,
                                                       "cert": cert}
                    # (z rot, x rot, dist proportion, time until prediction)

    def calculateSteering(self):
        """Called the first time an agent uses this frequency"""
        MAXLOOKAHEAD = 64
        O = bpy.data.objects

        ag = O[self.userid]
        agSim = self.sim.agents[self.userid]

        for emitterid, val in self.emitters:
            if emitterid == self.userid:
                continue
            to = O[emitterid]
            toSim = self.sim.agents[emitterid]

            x = ag
            rx = agSim.radius
            vx = mathutils.Vector(agSim.globalVelocity)
            px = x.location

            y = to
            ry = toSim.radius
            vy = mathutils.Vector(toSim.globalVelocity)
            py = y.location

            a = (vx - vy).length**2

            b = 2*(px[0] - py[0])*(vx[0] - vy[0]) +\
                2*(px[1] - py[1])*(vx[1] - vy[1]) +\
                2*(px[2] - py[2])*(vx[2] - vy[2])

            c = (px - py).length**2 - (rx + ry)**2

            """Calculate the time at which the agents will be at their closest
            and the distance between at that time"""
            if a == 0:
                tc = 0
            else:
                tc = -b/(2*a)  # Time that they are closest

            xc = px + tc * vx
            yc = py + tc * vy

            distTmp = (xc - yc).length
            dist = distTmp - (agSim.radius + toSim.radius)
            dist = max(dist, 0)  # The distance can't be negative

            """Check if they actually collide"""
            det = b**2 - 4*a*c
            if det > 0:
                t0 = (-b - det**0.5)/(2*a)
                t1 = (-b + det**0.5)/(2*a)
                if t0 >= 0 or t1 >= 0:
                    x0 = px + t0 * vx
                    x1 = px + t1 * vx

                    y0 = py + t0 * vy
                    y1 = py + t1 * vy

                    target = y0 - x0 + y1 - x1
                    target.normalize()
                    target *= (rx + ry)

                    z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
                    y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
                    x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

                    rotation = x * y * z
                    relative = target * rotation

                    changez = relative[0] / (abs(relative[0]) + 1)
                    changex = relative[2] / (abs(relative[2]) + 1)

                    acc = relative[1] / (abs(relative[1]) + 1)

                    overlap = 1 - (distTmp / (rx + ry))

                    if t1 < 0:
                        # collision in the past
                        cert = 0
                    elif t0 < 0:
                        # currently colliding
                        cert = 1
                    else:
                        # collision in the future
                        if t0 > MAXLOOKAHEAD:
                            c = 1
                        else:
                            c = t0 / MAXLOOKAHEAD
                        cert = (1 - ((-(c**3)/3 + (c**2)/2) * 6))**2
                        # https://www.desmos.com/calculator/godi4zejgd

                    self.storeSteering[emitterid] = {"rz": changez,
                                                     "rx": changex,
                                                     "distProp": 0,
                                                     "acc": acc,
                                                     "overlap": overlap,
                                                     "cert": cert}

                    # (z rot, x rot, dist proportion, recommended acceleration)
            elif dist < val and tc >= 0:
                target = yc - xc
                target.normalize()
                target *= (rx + ry)

                z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
                y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
                x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

                rotation = x * y * z
                relative = target * rotation

                changez = relative[0] / (abs(relative[0]) + 1)
                changex = relative[2] / (abs(relative[2]) + 1)

                dstp = dist/val  # distance proportion 1-0

                if tc < 0:
                    # collision in the past
                    cert = 0  # this is never used!
                else:
                    # collision in the future
                    if tc > MAXLOOKAHEAD:
                        c = 1
                    else:
                        c = tc / MAXLOOKAHEAD
                    cert = (1 - ((-(c**3)/3 + (c**2)/2) * 6))**2  # this is never used
                    # https://www.desmos.com/calculator/godi4zejgd

                self.storeSteering[emitterid] = {"rz": changez,
                                                 "rx": changex,
                                                 "distProp": dstp,
                                                 "acc": 0,
                                                 "overlap": 0,
                                                 "cert": 0}
                # (z rot, x rot, dist proportion, recommended acceleration)

    def calcAndGetItems(self):
        # TODO this gets called for both the sender and the receiver but I
        #   think it always calculates the same results...
        """If this channel hasn't been used then calculate and then return the
        correct values to use"""
        pre = self.predictNext
        ste = self.steeringNext
        if pre:
            # TODO if the dictionary is empty then this evaluates to false
            if not self.storePrediction:
                self.calculatePrediction()
            items = self.storePrediction.items()
        elif ste:
            # TODO if the dictionary is empty then this evaluates to false
            if not self.storeSteering:
                self.calculateSteering()
            items = self.storeSteering.items()
        else:
            # TODO if the dictionary is empty then this evaluates to false
            if not self.store:
                self.calculate()
            items = self.store.items()
        return items

    @staticmethod
    def _buildDictFromProperty(dictionary, prop, default=0):
        return {k: v[prop] if prop in v else default for k, v in dictionary}

    @property
    @timeChannel("Sound")
    def rz(self):
        """Return the horizontal angle of sound emitting agents"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "rz")

    @property
    @timeChannel("Sound")
    def rx(self):
        """Return the vertical angle of sound emitting agents"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "rx")

    @property
    @timeChannel("Sound")
    def dist(self):
        """Return the distance to the sound emitting agents 0-1"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "distProp")

    @property
    @timeChannel("Sound")
    def close(self):
        """Return how close the sound emitting is 0-1"""
        items = self.calcAndGetItems()
        if items:
            result = self._buildDictFromProperty(items, "distProp")
            return {k: 1-v for k, v in result.items()}

    @property
    @timeChannel("Sound")
    def db(self):
        """Return the volume (dist^2) of sound emitting agents"""
        items = self.calcAndGetItems()
        if items:
            tmp = self._buildDictFromProperty(items, "distProp")
            return {k: (1-v)**2 for k, v in tmp.items()}

    @property
    @timeChannel("Sound")
    def cert(self):
        """Return the certainty of a prediction 0-1"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "cert", default=1)

    @property
    @timeChannel("Sound")
    def acc(self):
        """Return the recommended acceleration to avoid a collision"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "acc")

    @property
    @timeChannel("Sound")
    def over(self):
        """Return the predicted worst case overlap"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "overlap")
