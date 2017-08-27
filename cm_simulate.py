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
import time

import bpy

from . import cm_channels as chan
from . import cm_timings
from .cm_actions import getmotions
from .cm_agent import Agent
from .cm_syncManager import syncManager

logger = logging.getLogger("CrowdMaster")


class Simulation:
    """The object that contains everything once the simulation starts"""

    def __init__(self):
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        self.agents = {}
        self.framelast = bpy.context.scene.cm_sim_start_frame
        self.compbrains = {}
        Noise = chan.Noise(self)
        Sound = chan.Sound(self)
        State = chan.State(self)
        World = chan.World(self)
        Flock = chan.Flock(self)
        Ground = chan.Ground(self)
        Formation = chan.Formation(self)
        AgentInfo = chan.AgentInfo(self)
        Path = chan.Path(self)
        self.lvars = {"Noise": Noise,
                      "Sound": Sound,
                      "State": State,
                      "World": World,
                      "Flock": Flock,
                      "Ground": Ground,
                      "Formation": Formation,
                      "Path": Path,
                      "AgentInfo": AgentInfo}
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
            sources = []
            targets = []
            if m.source[0] == "[" and m.source[-1] == "]":
                sources += self.actionGroups[m.source[1:-1]]
            else:
                sources = [m.source]
            if m.target[0] == "[" and m.target[-1] == "]":
                targets += self.actionGroups[m.target[1:-1]]
            else:
                targets = [m.target]
            for s in sources:
                for t in targets:
                    self.syncManager.actionPair(s, t)
                    self.syncManager.actionPair(t, s)

    def newagent(self, name, brain, rigOverwrite, constrainBone, initialTags,
                 modifyBones, freezeAnimation, geoGroup):
        """Set up an agent"""
        nGps = bpy.data.node_groups
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if brain in nGps and nGps[brain].bl_idname == "CrowdMasterTreeType":
            ag = Agent(name, nGps[brain], self, rigOverwrite, constrainBone,
                       tags=initialTags, modifyBones=modifyBones,
                       freezeAnimation=freezeAnimation, geoGroup=geoGroup)
            self.agents[name] = ag
        else:
            logger.debug("No such brain type: {}".format(brain))

    def createAgents(self, group):
        """Set up all the agents at the beginning of the simulation"""
        for ty in group.agentTypes:
            for ag in ty.agents:
                self.newagent(ag.name, ty.name, ag.rigOverwrite,
                              ag.constrainBone, ag.initialTags,
                              ag.modifyBones, group.freezeAnimation, ag.geoGroup)

    def step(self, scene):
        """Called when the next frame is moved to"""
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if preferences.show_debug_options:
            t = time.time()
            logger.debug("NEWFRAME {}".format(bpy.context.scene.frame_current))
            if preferences.show_debug_timings:
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
            logger.debug("Frame time {}".format(newT - t))
            cm_timings.simulation["total"] += newT - t
            logger.debug("Total time {}".format(
                cm_timings.simulation["total"]))
            cm_timings.simulation["totalFrames"] += 1
            tf = cm_timings.simulation["totalFrames"]
            tt = cm_timings.simulation["total"]
            logger.debug("spf {}".format(tt / tf))  # seconds per frame
            self.lastFrameTime = time.time()

    def frameChangeHandler(self, scene):
        """Given to Blender to call whenever the scene moves to a new frame"""
        if bpy.context.scene.cm_sim_end_frame <= bpy.context.scene.frame_current:
            self.stopFrameHandler()
            bpy.ops.screen.animation_cancel(restore_frame=False)
        elif self.framelast + 1 == bpy.context.scene.frame_current:
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
        logger.debug("Registering frame change handler")
        if self.frameChangeHandler in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.remove(self.frameChangeHandler)
        bpy.app.handlers.frame_change_pre.append(self.frameChangeHandler)
        if self.frameChangeHighlight not in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(
                self.frameChangeHighlight)

    def stopFrameHandler(self):
        """Remove self.frameChangeHandler from Blenders event handlers"""
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if self.frameChangeHandler in bpy.app.handlers.frame_change_pre:
            logger.debug("Unregistering frame change handler")
            bpy.app.handlers.frame_change_pre.remove(self.frameChangeHandler)
