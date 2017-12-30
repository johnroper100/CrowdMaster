# Copyright 2018 CrowdMaster Developer Team
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

import bpy
import mathutils

from .cm_masterChannels import MasterChannel as Mc
from .cm_masterChannels import timeChannel

from . import channel_world

class World(Mc):
    """Used to access other data from the scene"""

    def __init__(self, sim):
        Mc.__init__(self, sim)
        self.store = {}
        self.eventVolStore = []
        self.eventQueried = False
        channel_world.event_clear()
        events = bpy.context.scene.cm_events.coll
        for e in events:
            if e.category == "Volume":
                if e.volumeType == "Object":
                    objs = [bpy.data.objects[e.volume]]
                else:
                    objs = bpy.data.groups[e.volumeType].objects
                for obj in objs:
                    mw = obj.matrix_world
                    channel_world.event_volume_create(e.eventname, obj.name,
                                                      mw.to_translation(),
                                                      mw.to_euler(),
                                                      mw.to_scale())
            elif e.category == "Time":
                channel_world.event_time_create(e.eventname, e.timeMin, e.timeMax)

    def target(self, target):
        """Dynamic properties"""
        if target not in self.store:
            self.store[target] = Channel(target, self.userid, self.sim)
        return self.store[target]

    def newframe(self):
        self.store = {}
        self.eventVolStore = []
        self.eventQueried = False

        events = bpy.context.scene.cm_events.coll
        for e in events:
            if e.category == "Volume":
                if e.volumeType == "Object":
                    objs = [bpy.data.objects[e.volume]]
                else:
                    objs = bpy.data.groups[e.volumeType].objects
                for obj in objs:
                    mw = obj.matrix_world
                    channel_world.event_volume_update(e.name, obj.name,
                                                      mw.to_translation(),
                                                      mw.to_euler(),
                                                      mw.to_scale())
        channel_world.event_construct_bvt()
        channel_world.event_set_time(bpy.context.scene.frame_current)

    def setuser(self, userid):
        self.store = {}
        self.eventVolStore = []
        self.eventQueried = False
        Mc.setuser(self, userid)

    @property
    def time(self):
        return bpy.context.scene.frame_current

    @timeChannel("World")
    def event(self, eventName, eventType):
        pt = bpy.data.objects[self.userid].location
        return {"None": channel_world.event_query(eventName, pt, eventType)}


class Channel:
    def __init__(self, target, user, sim):
        self.sim = sim

        self.target = target
        self.userid = user

        self.store = {}
        self.calcd = False

    def calculate(self):
        O = bpy.context.scene.objects

        to = O[self.target]
        ag = O[self.userid]
        userDim = bpy.context.scene.objects[self.userid].dimensions

        tDim = max(bpy.context.scene.objects[self.target].dimensions)
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

        changez = math.atan2(relative[0], relative[1]) / math.pi
        changex = math.atan2(relative[2], relative[1]) / math.pi
        self.store = {"rz": changez,
                      "rx": changex,
                      "arrived": 1 if dist < (tDim + uDim) else 0}

        self.calcd = True

    @property
    @timeChannel("World")
    def rz(self):
        if not self.calcd:
            self.calculate()
        return self.store["rz"]

    @property
    @timeChannel("World")
    def rx(self):
        if not self.calcd:
            self.calculate()
        return self.store["rx"]

    @property
    @timeChannel("World")
    def arrived(self):
        if not self.calcd:
            self.calculate()
        return self.store["arrived"]
