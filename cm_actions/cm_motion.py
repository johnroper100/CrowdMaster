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


class ActionManager:
    def __init__(self):
        self.currentActions = []

    def registerAction(self, actionNode):
        pass


class Action:
    def __init__(self, name, actionname, motionname):
        """Both actions must be the same length and not contain scale"""
        A = bpy.data.actions
        sce = bpy.context.scene

        self.name = name
        self.actionname = actionname
        if actionname in A:
            self.action = A[self.actionname]
            arange = self.action.frame_range
            alen = arange[1] - arange[0] + 1
        else:
            self.action = None  # So that other code can do \- if action.action
            alen = float("inf")

        self.motiondata = {}

        self.motionname = motionname
        if motionname in A:
            # Extract the location and rotation data from the animation
            self.motion = A[self.motionname]
            mrange = self.motion.frame_range
            mlen = mrange[1] - mrange[0] + 1
            for c in self.motion.fcurves:
                if c.data_path not in self.motiondata:
                    self.motiondata[c.data_path] = []
                self.motiondata[c.data_path].append([])
                morange = self.motion.frame_range
                for frame in range(int(morange[0]), int(morange[1]) + 1):
                    val = c.evaluate(frame)
                    self.motiondata[c.data_path][-1].append(val)
        else:
            self.motion = None  # So that other code can do - if action.motion
            mlen = float("inf")

        self.length = min(alen, mlen)


def getmotions():
    """Turn all the entries for actions into action objects"""
    sce = bpy.context.scene
    result = {}
    groups = {}
    for m in sce.cm_actions.coll:
        result[m.name] = Action(m.name, m.action, m.motion)
        for gp in m.groups.split(","):
            gpName = gp.strip()
            if gpName not in groups:
                groups[gpName] = []
            groups[gpName].append(m.name)
    return result, groups
