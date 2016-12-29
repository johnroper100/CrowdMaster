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

import bpy

import time

from . import cm_channels as chan

from .cm_agent import Agent
from .cm_actions import getmotions
from .cm_syncManager import syncManager

from . import cm_timings


class Simulation:
    """The object that contains everything once the simulation starts"""
    def __init__(self):
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        self.agents = {}
        self.framelast = 1
        self.compbrains = {}
        Noise = chan.Noise(self)
        Sound = chan.Sound(self)
        State = chan.State(self)
        World = chan.World(self)
        Crowd = chan.Crowd(self)
        Ground = chan.Ground(self)
        Formation = chan.Formation(self)
        Path = chan.Path(self)
        self.lvars = {"Noise": Noise,
                      "Sound": Sound,
                      "State": State,
                      "World": World,
                      "Crowd": Crowd,
                      "Ground": Ground,
                      "Formation": Formation,
                      "Path": Path}
        if preferences.show_debug_options:
            self.totalTime = 0
            self.totalFrames = 0
            self.lastFrameTime = None

        self.actions = {}
        self.actionGroups = {}

        self.syncManager = syncManager()

    def setupActions(self):
        """Set up the actions"""
        self.actions, self.actionGroups = getmotions()
        for m in bpy.context.scene.cm_action_pairs.coll:
            self.syncManager.actionPair(m.source, m.target)
            self.syncManager.actionPair(m.target, m.source)

    def newagent(self, name, brain):
        """Set up an agent"""
        nGps = bpy.data.node_groups
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if brain in nGps and nGps[brain].bl_idname == "CrowdMasterTreeType":
            ag = Agent(name, nGps[brain], self)
            self.agents[name] = ag
        else:
            if preferences.show_debug_options:
                print("No such brain type:" + brain)

    def createAgents(self, group):
        """Set up all the agents at the beginning of the simulation"""
        for ty in group.agentTypes:
            for ag in ty.agents:
                self.newagent(ag.name, ty.name)

    def step(self, scene):
        """Called when the next frame is moved to"""
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if preferences.show_debug_options:
            t = time.time()
            print("NEWFRAME", bpy.context.scene.frame_current)
            if preferences.show_debug_options and preferences.show_debug_timings:
                if self.lastFrameTime is not None:
                    between = time.time() - self.lastFrameTime
                    cm_timings.simulation["betweenFrames"] += between
        for agent in self.agents.values():
            for tag in agent.access["tags"]:
                for channel in self.lvars:
                    if tag[:len(channel)] == channel:
                        self.lvars[channel].register(agent, tag[len(channel):],
                                                     agent.access["tags"][tag])
        # TODO registering channels would be much more efficient if done
        # straight after the agent is evaluated.

        self.syncManager.newFrame()

        for a in self.agents.values():
            a.step()
        for a in self.agents.values():
            a.apply()
        for chan in self.lvars.values():
            chan.newframe()
        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.printTimings()
            newT = time.time()
            print("Frame time", newT - t)
            cm_timings.simulation["total"] += newT - t
            print("Total time", cm_timings.simulation["total"])
            cm_timings.simulation["totalFrames"] += 1
            tf = cm_timings.simulation["totalFrames"]
            tt = cm_timings.simulation["total"]
            print("spf", tt/tf)  # seconds per frame
            self.lastFrameTime = time.time()

    def frameChangeHandler(self, scene):
        """Given to Blender to call whenever the scene moves to a new frame"""
        if self.framelast+1 == bpy.context.scene.frame_current:
            self.framelast = bpy.context.scene.frame_current
            self.step(scene)

    def frameChangeHighlight(self, scene):
        """Not unregistered when simulation stopped"""
        if self.framelast >= bpy.context.scene.frame_current:
            active = bpy.context.active_object
            if active and active in self.agents:
                self.agents[bpy.context.active_object.name].highLight()

    def startFrameHandler(self):
        """Add self.frameChangeHandler to the Blender event handlers"""
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if preferences.show_debug_options:
            self.totalTime = 0
            self.totalFrames = 0
            print("Registering frame change handler")
        if self.frameChangeHandler in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.remove(self.frameChangeHandler)
        bpy.app.handlers.frame_change_pre.append(self.frameChangeHandler)
        if self.frameChangeHighlight not in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(self.frameChangeHighlight)

    def stopFrameHandler(self):
        """Remove self.frameChangeHandler from Blenders event handlers"""
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if self.frameChangeHandler in bpy.app.handlers.frame_change_pre:
            if preferences.show_debug_options:
                print("Unregistering frame change handler")
            bpy.app.handlers.frame_change_pre.remove(self.frameChangeHandler)
