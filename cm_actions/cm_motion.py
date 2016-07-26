import bpy
import math


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
            alen = 0

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
            mlen = 0

        self.length = max(alen, mlen)


def getmotions():
    """Turn all the entries for actions into action objects"""
    sce = bpy.context.scene
    result = {}
    for m in sce.cm_actions.coll:
        result[m.name] = Action(m.name, m.action, m.motion)
    return result
