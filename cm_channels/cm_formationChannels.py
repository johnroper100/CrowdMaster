from .cm_masterChannels import MasterChannel as Mc
import mathutils
from mathutils import Vector
import math

from ..libs.ins_clustering import clusterMatch

import bpy


class Formation(Mc):
    """Get and set data to allow agents to align themselves into formations"""
    def __init__(self, sim):
        Mc.__init__(self, sim)
        self.formations = {}

    def newframe(self):
        for f in self.formations.values():
            f.newFrame()

    def setuser(self, userid):
        for chan in self.formations.values():
            chan.newuser(userid)
        Mc.setuser(self, userid)

    def register(self, agent, formID, val):
        """Adds an object that is a formation target"""
        if formID in dir(self):
            print("""Formation ID must not be an attribute of this
                  python object""")
        else:
            if formID not in self.formations:
                ch = Channel(formID, self.sim)
                self.formations[formID] = ch
            self.formations[formID].register(agent.id, val)

    def retrieve(self, formID):
        """Dynamic properties"""
        if (formID in self.formations):
            return self.formations[formID]
        else:
            return EmptyChannel()
            # TODO this is really hacky...


class EmptyChannel():
    # TODO Way too hacky... need to think of another way of stopping crashes
    #   if the channel doesn't exist.
    def __getattr__(self, attr):
        if attr in ("dist", "rz", "rx"):
            return 0
        return self

    def __call__(self, *args, **kwargs):
        return None


class Channel:
    def __init__(self, formID, sim):
        self.sim = sim

        self.targetObjects = set()
        self.targets = []
        self.formI = formID

        self.inpBuffer = []
        self.priority = []
        self.calcd = {}  # {str: Vector()}
        self.lastCalcd = None  # Store from last frame to reduce jittering

    def register(self, agentID, val):
        """Add a formation target object"""
        self.targetObjects.add(agentID)

    def newuser(self, userid):
        """Called when a new agent is using this channel"""
        self.userid = userid

    def newFrame(self):
        """Called at the beginning of each new frame.
        (see def checkCalcd for description of how this is used)"""
        objs = bpy.data.objects

        self.calcd = {}
        new = []
        for p in self.priority:
            if p in self.inpBuffer:
                new.append(p)
        for i in self.inpBuffer:
            if i not in new:
                new.append(i)
        self.priority = new
        self.inpBuffer = []

        self.targets = []
        for t in self.targetObjects:
            ob = objs[t]
            wrld = ob.matrix_world
            self.targets += [wrld*v.co for v in ob.data.vertices]

    def calculate(self):
        """Collect data and use clusterMatch to work out pairings"""
        objs = bpy.data.objects

        agAccess = lambda x: (objs[x].location.x, objs[x].location.y,
                              objs[x].location.z)
        tgAccess = lambda x: (x.x, x.y, x.z)
        setOfTargets = set([tgAccess(x) for x in self.targets])
        if self.lastCalcd:
            # TODO if the same agents are inputed the same result as last time
            #  will be returned. This prevents jittering but may result in
            #  problems in the future.
            if self.lastCalcd[0] == set(self.priority[:len(self.targets)]) and\
                    self.lastCalcd[1] == setOfTargets:
                self.calcd = self.lastCalcd[2]
                return
        success, pairs = clusterMatch(self.priority[:len(self.targets)],
                                      self.targets, agAccess, tgAccess)
        if success:
            for p in pairs:
                self.calcd[self.priority[p[0][0]]] = p[1][1]

        self.lastCalcd = (set(self.priority[:len(self.targets)]),
                          setOfTargets, self.calcd)

    def checkCalcd(self):
        """When a user accesses data decide if anything needs calculating. When
        a user requests data that wasn't part of the last calculation it is
        added to self.inpBuffer. At the beginning of each frame anything in
        inpBuffer that is already in priority remains there, anything that
        isn't already there is added to the end and anything not it inpBuffer
        is left out. The values from inpBuffer are used to match. If there
        aren't enough target positions enough sources are used from the
        beginning of self.priority."""
        if self.userid not in self.inpBuffer:
            self.inpBuffer.append(self.userid)
        if self.userid in self.calcd:
            return self.calcd[self.userid]
        elif self.userid in self.priority[:len(self.targets)]:
            self.calculate()
            return self.calcd[self.userid]
        else:
            return False

    def fixedDist(self, fixedPoint):
        """Distance from this agent to the position in formation.
        :type fixedPoint: int
        :param fixedPoint: overrides the cluster matching behaviour so that an
                            agent can always target the same point"""
        objs = bpy.data.objects

        if fixedPoint < len(self.targets):
            to = self.targets[fixedPoint]
            loc = objs[self.userid].location
            return math.sqrt((loc[0] - to[0])**2 + (loc[1] - to[1])**2
                             + (loc[2] - to[2])**2)
        else:
            return None

    @property
    def dist(self):
        """Distance from this agent to the position in formation"""
        objs = bpy.data.objects
        to = self.checkCalcd()

        if to:
            loc = objs[self.userid].location
            return math.sqrt((loc[0] - to[0])**2 + (loc[1] - to[1])**2
                             + (loc[2] - to[2])**2)
        else:
            return None

    def fixedRz(self, fixedPoint):
        """Horizontal rotation to be pointing at position in formation.
        :type fixedPoint: int
        :param fixedPoint: overrides the cluster matching behaviour so that an
                            agent can always target the same point"""
        objs = bpy.data.objects

        if fixedPoint < len(self.targets):
            to = self.targets[fixedPoint]

            ag = objs[self.userid]

            target = to - ag.location

            z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
            y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
            x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

            rotation = x * y * z
            relative = target * rotation

            return math.atan2(relative[0], relative[1])/math.pi

    @property
    def rz(self):
        """Horizontal rotation to be pointing at position in formation"""
        objs = bpy.data.objects
        to = self.checkCalcd()

        if to:
            ag = objs[self.userid]

            target = to - ag.location

            z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
            y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
            x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

            rotation = x * y * z
            relative = target * rotation

            return math.atan2(relative[0], relative[1])/math.pi
        else:
            return None

    def fixedRx(self, fixedPoint):
        """Vertical rotation to be pointing at position in formation.
        :type fixedPoint: int
        :param fixedPoint: overrides the cluster matching behaviour so that an
                            agent can always target the same point"""
        objs = bpy.data.objects

        if fixedPoint < len(self.targets):
            to = self.targets[fixedPoint]

            ag = objs[self.userid]

            target = to - ag.location

            z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
            y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
            x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

            rotation = x * y * z
            relative = target * rotation

            return math.atan2(relative[2], relative[1])/math.pi


    @property
    def rx(self):
        """Vertical rotation to be pointing at position in formation"""
        objs = bpy.data.objects
        to = self.checkCalcd()

        if to:
            ag = objs[self.userid]

            target = to - ag.location

            z = mathutils.Matrix.Rotation(ag.rotation_euler[2], 4, 'Z')
            y = mathutils.Matrix.Rotation(ag.rotation_euler[1], 4, 'Y')
            x = mathutils.Matrix.Rotation(ag.rotation_euler[0], 4, 'X')

            rotation = x * y * z
            relative = target * rotation

            return math.atan2(relative[2], relative[1])/math.pi
        else:
            return None
