import bpy

from math import *
from mathutils import *
BVHTree = bvhtree.BVHTree

from .cm_masterChannels import MasterChannel as Mc

import time


class Ground(Mc):
    """Get data about the ground near the agent"""
    def __init__(self, sim):
        Mc.__init__(self, sim)
        self.store = {}
        self.calced = False
        self.groundTrees = {}

    def newframe(self):
        self.store = {}
        self.calced = False

    def setuser(self, userid):
        self.store = {}
        self.calced = False
        Mc.setuser(self, userid)

    def calcground(self):
        """Called the first time each agent uses the Ground channel"""
        results = []
        s = bpy.context.scene.objects[self.userid]
        for ag in self.sim.agents.values():
            if "Ground" in ag.access["tags"]:
                # TODO record this when the tags are set
                gnd = bpy.context.scene.objects[ag.id]
                if ag.id not in self.groundTrees:
                    r = gnd.rotation_euler
                    if not (r[0] or r[1] or r[2]):
                        print(ag.id, "rotation must be applied")
                        # TODO make ray_cast work with rotation
                    sce = bpy.context.scene
                    self.groundTrees[ag.id] = BVHTree.FromObject(gnd, sce)
                point = s.location - gnd.location
                calcd = self.groundTrees[ag.id].ray_cast(point, (0, 0, -1))
                if calcd[0]:
                    results.append(calcd + (1,))
                calcd = self.groundTrees[ag.id].ray_cast(point, (0, 0, 1))
                if calcd[0]:
                    results.append(calcd + (-1,))

        if len(results) > 0:
            loc, norm, ind, dist, direc = min(results, key=lambda x: x[3])
            self.store["location"] = loc
            self.store["normal"] = norm
            self.store["index"] = ind
            self.store["distance"] = dist * direc  # direc is +/-1

        self.calced = True

    @property
    def dh(self):
        """Return the vertical distance to the nearest ground object"""
        if not self.calced:
            self.calcground()
        if self.store:
            return self.store["distance"]
        else:
            return 0

    @property
    def dx(self):
        # Tilt
        pass

    @property
    def dy(self):
        # Roll
        pass
