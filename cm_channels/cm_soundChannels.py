from .cm_masterChannels import MasterChannel as Mc
import math
import mathutils
Vector = mathutils.Vector

from ..libs import ins_octree as ot

if __name__ != "__main__":
    import bpy

else:
    import unittest

    from .cm_masterChannels import Wrapper as wr

    class FakeObject():
        """Impersonate bpy.context.scene.objects[n]"""
        def __init__(self, location, rotation):
            self.location = mathutils.Vector(location)
            self.rotation_euler = mathutils.Euler(rotation)

    class FakeAgent():
        """Impersonate Simulation.agents[n]"""
        def __init__(self, bid):
            self.id = bid

    class FakeSimulation():
        """Impersonate the Simulation object"""
        def __init__(self):
            self.framelast = 1

    class Test(unittest.TestCase):
        def setUp(self):
            O = bpy.context.scene.objects
            # Impersonate bpy.context.scene.objects
            # These are the objects that can be used to emit and hear sounds
            O = {"OB1": FakeObject([0, 0, 0], [0, 0, 0]),
                 "OB2": FakeObject([1, 0, 0], [0, 0, 0]),
                 "OB3": FakeObject([0, 1, 0], [0, 0, 0]),
                 "OB4": FakeObject([0, -1, 0], [0, 0, 0]),
                 "OB5": FakeObject([-0.1, -1, 0], [0, 0, 0])}

            self.FSim = FakeSimulation()

            self.sound = wr(Sound(self.FSim))

        def testOne(self):
            """Some simple test cases"""
            self.sound.register(FakeAgent("OB1", "A", 1))
            self.sound.register(FakeAgent("OB2", "A", 1))
            self.sound.register(FakeAgent("OB3", "A", 1))

            self.sound.setuser("OB1")
            self.assertEqual(self.sound.A.rz, {"OB2": 0.5,
                                               "OB3": 0})
            self.assertEqual(self.sound.A.db, {"OB2": 0,
                                               "OB3": 0})

        def testBoundryRotations(self):
            """Testing the extremes of the rotation"""
            self.sound.register(FakeAgent("OB1", "A", 1))
            self.sound.register(FakeAgent("OB4", "A", 1))
            self.sound.register(FakeAgent("OB5", "A", 1))

            self.sound.setuser("OB1")
            self.assertEqual(self.sound.A.rz["OB4"], 1)
            self.assertTrue(-1 < self.sound.A.rz["OB5"] < -0.75)

        def tearDown(self):
            self.sound.newFrame()

    # Run unit test
    unittest.main()


class Sound(Mc):
    """The object containing all of the sound channels"""
    def __init__(self, sim):
        Mc.__init__(self, sim)
        # All the different sound frequencies that were emitted last frame
        self.channels = {}

    def register(self, agent, frequency, val):
        """Adds an object that is emitting a sound"""
        if frequency in dir(self):
            print("""frequency must not be an attribute of this
                  python object""")
        else:
            if frequency not in self.channels:
                ch = Channel(frequency, self.sim)
                self.channels[frequency] = ch
            self.channels[frequency].register(agent.id, val)

    def retrieve(self, freq):
        """Dynamic properties"""
        if (freq in self.channels):
            return self.channels[freq]
        else:
            return EmptyChannel()
            # TODO this is really hacky...

    def newframe(self):
        self.channels = {}

    def setuser(self, userid):
        for chan in self.channels.values():
            chan.newuser(userid)
        Mc.setuser(self, userid)


class EmptyChannel():
    def __getattr__(self, attr):
        if attr == "pred" or attr == "steer":
            return self
        else:
            return None


class Channel:
    """Holds a record of all objects that are emitting on a
    certain frequency"""
    def __init__(self, frequency, sim):
        """
        :param frequency: The identifier for this channel
        :type frequency: String"""
        self.sim = sim

        self.emitters = {}
        self.frequency = frequency
        # Temporary storage which is reset after each agents has used it
        self.store = {}
        self.storePrediction = {}
        self.storeSteering = {}

        self.predictNext = False
        self.steeringNext = False

        self.octree = None

    def register(self, objectid, val):
        """Add an object that emits sound"""
        self.emitters[objectid] = val

    def newuser(self, userid):
        self.userid = userid
        self.store = {}
        self.storePrediction = {}
        self.storeSteering = {}

    def calculate(self):
        """Called the first time an agent uses this frequency"""
        O = bpy.context.scene.objects
        userDim = self.sim.agents[self.userid].dimensions

        if self.octree is None:
            bss = []  # List of bounding spheres
            for emitterid, val in self.emitters.items():
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
            val = self.emitters[emitterid]

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
                                     "distProp": dist/(val+eDim+uDim)}
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
        for emitterid, val in self.emitters.items():
            if emitterid != self.userid:
                to = O[emitterid]
                toSim = self.sim.agents[emitterid]

                p1 = mathutils.Vector((agSim.apx, agSim.apy, agSim.apz))
                p2 = mathutils.Vector((toSim.apx, toSim.apy, toSim.apz))

                d1 = mathutils.Vector(agSim.globalVelocity)
                d2 = mathutils.Vector(toSim.globalVelocity)

                # O["Cube.Pointer"].location = p1 + (d1 * 2)
                # O["Cube.001.Pointer"].location = p2 + (d2 * 2)

                a = d1.dot(d1)
                b = d1.dot(d2)
                e = d2.dot(d2)

                d = a*e - b*b

                if (d != 0):  # If the two lines are not parallel.
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

        for emitterid, val in self.emitters.items():
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

            # ax^2 + bx + (c - d) = 0
            a = (vx - vy).length**2
            # a = (vx[0] - vy[0])**2 + (vx[1] - vy[1])**2 + \
            #     (vx[2] - vy[2])**2

            b = 2*(px[0] - py[0])*(vx[0] - vy[0]) +\
                2*(px[1] - py[1])*(vx[1] - vy[1]) +\
                2*(px[2] - py[2])*(vx[2] - vy[2])

            c = (px - py).length**2 - (rx + ry)**2

            # c = (px[0] - py[0])**2 + (px[1] - py[1])**2 +
            #     (px[2] - py[2])**2 - (rx + ry)**2

            """Calculate the time at which the agents will be at their closest
            and the distance between at that time"""
            if a == 0:
                tc = 0
            else:
                tc = -b/(2*a)  # Time that they are closest

            xc = px + tc * vx
            yc = py + tc * vy

            # bpy.data.objects["Empty.001"].location = xc
            # bpy.data.objects["Empty.002"].location = yc

            distTmp = (xc - yc).length
            dist = distTmp - (agSim.radius + toSim.radius)
            dist = max(dist, 0)  # The distance can't be negative

            """Check if they actually collide"""
            det = b**2 - 4*a*c
            if det > 0:
                t0 = (-b - det**0.5)/(2*a)
                t1 = (-b + det**0.5)/(2*a)
                if ((t0 >= 0) or (t1 >= 0)):
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

                    # bpy.data.objects["Empty"].location = target
                    # (z rot, x rot, dist proportion, recommended acceleration)
            elif dist < val and tc >= 0:
                target = yc - xc
                target.normalize()
                target *= (rx + ry)

                # bpy.data.objects["Empty"].location = target

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
                    cert = 0
                else:
                    # collision in the future
                    if tc > MAXLOOKAHEAD:
                        c = 1
                    else:
                        c = tc / MAXLOOKAHEAD
                    cert = (1 - ((-(c**3)/3 + (c**2)/2) * 6))**2
                    # https://www.desmos.com/calculator/godi4zejgd

                self.storeSteering[emitterid] = {"rz": changez,
                                                 "rx": changex,
                                                 "distProp": dstp,
                                                 "acc": 0,
                                                 "overlap": 0,
                                                 "cert": 0}
                # (z rot, x rot, dist proportion, recommended acceleration)


    # TODO The following is extraordinary hacky... do something about it!

    @property
    def steer(self):
        self.steeringNext = True
        self.predictNext = False  # So you can't do Sound.A.pred.steer...
        return self

    @property
    def pred(self):
        self.predictNext = True
        self.steeringNext = False  # So you can't do Sound.A.steer.pred...
        return self

    def calcAndGetItems(self):
        # TODO this gets called for both the sender and the receiver but I
        #   think it always calculates the same results...
        """If this channel hasn't been used then calculate and then return the
        correct values to use"""
        pre = self.predictNext
        ste = self.steeringNext
        self.predictNext = False
        self.steeringNext = False
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
    def rz(self):
        """Return the horizontal angle of sound emitting agents"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "rz")

    @property
    def rx(self):
        """Return the vertical angle of sound emitting agents"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "rx")

    @property
    def dist(self):
        """Return the distance to the sound emitting agents 0-1"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "distProp")

    @property
    def close(self):
        """Return how close the sound emitting is 0-1"""
        items = self.calcAndGetItems()
        if items:
            result = self._buildDictFromProperty(items, "distProp")
            return {k: 1-v for k, v in result.items()}

    @property
    def db(self):
        """Return the volume (dist^2) of sound emitting agents"""
        items = self.calcAndGetItems()
        if items:
            tmp = self._buildDictFromProperty(items, "distProp")
            return {k: (1-v)**2 for k, v in tmp.items()}

    @property
    def cert(self):
        """Return the certainty of a prediction 0-1"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "cert", default=1)

    @property
    def acc(self):
        """Return the recommended acceleration to avoid a collision"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "acc")

    @property
    def over(self):
        """Return the predicted worst case overlap"""
        items = self.calcAndGetItems()
        if items:
            return self._buildDictFromProperty(items, "overlap")
