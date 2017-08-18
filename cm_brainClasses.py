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
import random
import time

import bpy
import mathutils
from bpy.props import BoolProperty

from . import cm_timings

logger = logging.getLogger("CrowdMaster")


class Neuron():
    """The representation of the nodes. Not to be used on own"""

    def __init__(self, brain, bpyNode):
        self.brain = brain  # type: Brain
        self.neurons = self.brain.neurons  # type: List[Neuron]
        self.inputs = []  # type: List[str] - strings are names of neurons
        self.result = None  # type: None | ImpulseContainer - Cache for current
        self.resultLog = [(0, 0, 0), (0, 0, 0)]  # type: List[(int, int, int)]
        self.fillOutput = BoolProperty(default=True)
        self.bpyNode = bpyNode  # type: cm_bpyNodes.LogicNode
        self.settings = {}  # type: Dict[str, bpy.props.*]
        self.dependantOn = []  # type: List[str] - strings are names of neurons

    def evaluate(self):
        """Called by any neurons that take this neuron as an input"""
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if preferences.show_debug_options:
            t = time.time()
        if self.result:
            # Return a cached version of the answer if possible
            return self.result
        noDeps = len(self.dependantOn) == 0
        dep = False
        for x in self.dependantOn:
            if self.neurons[x].isCurrent:
                dep = True
                break
        # Only output something if the node isn't dependant on a state
        #  or if one of it's dependancies is the current state
        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.neuron["deps"] += time.time() - t

        if noDeps or dep:
            inps = []
            for i in self.inputs:
                got = self.neurons[i].evaluate()
                """For each of the inputs the result is collected. If the
                input in not a dictionary then it is made into one"""
                if got is not None:
                    inps.append(got)
            if preferences.show_debug_options and preferences.show_debug_timings:
                coreT = time.time()
            output = self.core(inps, self.settings)
            if preferences.show_debug_options and preferences.show_debug_timings:
                cm_timings.coreTimes[self.__class__.__name__] += time.time() - \
                    coreT
                cm_timings.coreNumber[self.__class__.__name__] += 1
            if output is None:
                output = {}
            elif not (isinstance(output, dict) or output is None):
                output = {"None": output}
        else:
            output = None
        self.result = output

        if preferences.show_debug_options:
            t = time.time()
        # Calculate the colour that would be displayed in the agent is selected
        total = 0
        if output:
            val = 1
            av = sum(output.values()) / len(output)
            if av > 0:
                startHue = 0.333
            else:
                startHue = 0.5

            if av > 1:
                hueChange = -(-(abs(av) + 1) / abs(av) + 2) * (1 / 3)
                hue = 0.333 + hueChange
                sat = 1
            elif av < -1:
                hueChange = (-(abs(av) + 1) / abs(av) + 2) * (1 / 3)
                hue = 0.5 + hueChange
                sat = 1
            else:
                hue = startHue

            if abs(av) < 1:
                sat = abs(av)**(1 / 2)
            else:
                sat = 1
        else:
            hue = 0
            sat = 0
            val = 0.5
        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.neuron["sumColour"] += time.time() - t
        self.resultLog[-1] = (hue, sat, val)

        return output

    def newFrame(self):
        self.result = None
        self.resultLog.append((0, 0, 0.5))

    def highLight(self, frame):
        """Colour the nodes in the interface to reflect the output"""
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if preferences.use_node_color:
            hue, sat, val = self.resultLog[frame]
            self.bpyNode.use_custom_color = True
            c = mathutils.Color()
            c.hsv = hue, sat, val
            self.bpyNode.color = c
            self.bpyNode.keyframe_insert("color")


class State:
    """The basic element of the state machine. Abstract class"""

    def __init__(self, brain, bpyNode, name):
        """A lot of the fields are modified by the compileBrain function"""
        self.name = name
        self.brain = brain
        self.neurons = self.brain.neurons
        self.outputs = []
        self.valueInputs = []  # Left empty by start state
        self.finalValue = 1.0
        self.finalValueCalcd = False
        self.settings = {}
        self.isCurrent = False

        self.length = 0
        self.cycleState = False
        self.currentFrame = 0

        self.bpyNode = bpyNode
        self.resultLog = {0: (0, 0, 0), 1: (0, 0, 0)}

    def query(self):
        """If this state is a valid next move return float > 0"""
        if not self.finalValueCalcd:
            self.evaluate()
        return self.finalValue

    def moveTo(self):
        """Called when the current state moves to this node"""
        self.currentFrame = 0
        self.isCurrent = True

    def evaluate(self):
        """Called while all the neurons are being evaluated"""
        if self.finalValueCalcd:
            return
        self.finalValueCalcd = True
        if len(self.valueInputs) == 0:
            self.finalValue = self.settings["ValueDefault"]
            if self.settings["RandomInput"]:
                self.finalValue += random.random()
            return
        values = []
        for inp in self.valueInputs:
            values.append(self.neurons[inp].evaluate())

        total = 0
        num = 0
        vals = []

        for v in values:
            if v is not None:
                if self.settings["ValueFilter"] == "AVERAGE":
                    for i in v.values():
                        total += i
                        num += 1
                vals += v.values()
        if num == 0:
            num = 1
        if len(vals) == 0:
            result = 0
        elif self.settings["ValueFilter"] == "AVERAGE":
            result = total / num
        elif self.settings["ValueFilter"] == "MAX":
            result = max(vals)
        elif self.settings["ValueFilter"] == "MIN":
            result = min(vals)
        self.finalValue = result
        if self.settings["RandomInput"]:
            self.finalValue += random.random()

    def evaluateState(self):
        """Return the state to move to (allowed to return itself)

        :returns: moving to new state, name of new state or None
        :rtype: bool, string | None
        """
        self.currentFrame += 1

        # The proportion of the way through the state
        if self.length == 0:
            complete = 1
        else:
            complete = self.currentFrame / self.length
            complete = 0.5 + complete / 2
        sceneFrame = bpy.context.scene.frame_current
        self.resultLog[sceneFrame] = ((0.15, 0.4, complete))

        if self.currentFrame < self.length - 1:
            return False, self.name

        # ==== Will stop here is this state hasn't reached its end ====

        options = []
        for con in self.outputs:
            val = self.neurons[con].query()
            if val is not None:
                options.append((con, val))

        # If the cycleState button is checked then add a contection back to
        #    this state again.
        if self.cycleState and self.name not in self.outputs:
            val = self.neurons[self.name].query()
            if val is not None:
                options.append((self.name, val))

        if len(options) > 0:
            if len(options) == 1:
                return True, options[0][0]
            else:
                return True, max(options, key=lambda v: v[1])[0]

        return False, None

    def newFrame(self):
        self.finalValueCalcd = False

    def highLight(self, frame):
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        if preferences.use_node_color:
            if frame in self.resultLog:
                hue, sat, val = self.resultLog[frame]
            else:
                hue = 0.0
                sat = 0.0
                val = 1.0
            self.bpyNode.use_custom_color = True
            c = mathutils.Color()
            c.hsv = hue, sat, val
            self.bpyNode.color = c
            self.bpyNode.keyframe_insert("color")


class Brain():
    """An executable brain object. One created per agent"""

    def __init__(self, sim, userid, freezeAnimation):
        self.userid = userid
        self.sim = sim
        self.lvars = self.sim.lvars
        self.outvars = {}
        self.tags = {}
        self.isActiveSelection = False
        self.freeze = freezeAnimation

        self.currentState = None
        self.startState = None

        # set in compileBrian
        self.outputs = []
        self.neurons = {}
        self.states = []

    def setStartState(self, stateNode):
        """Used by compileBrian"""
        self.currentState = stateNode
        self.startState = stateNode

    def reset(self):
        self.outvars = {"rx": 0, "ry": 0, "rz": 0,
                        "px": 0, "py": 0, "pz": 0, "sk": {}}
        self.tags = self.sim.agents[self.userid].access["tags"]

    def execute(self):
        """Called for each time the agents needs to evaluate"""
        preferences = bpy.context.user_preferences.addons[__package__].preferences

        actv = bpy.context.active_object
        self.isActiveSelection = actv is not None and actv.name == self.userid
        self.reset()
        randstate = hash(self.userid) + self.sim.framelast
        random.seed(randstate)

        if preferences.show_debug_options:
            t = time.time()

        for name, var in self.lvars.items():
            var.setuser(self.userid)

        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.brain["setUser"] += time.time() - t
            t = time.time()

        for neur in self.neurons.values():
            neur.newFrame()

        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.brain["newFrame"] += time.time() - t
            t = time.time()

        for out in self.outputs:
            self.neurons[out].evaluate()

        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.brain["evaluate"] += time.time() - t
            t = time.time()

        if self.currentState:
            new, nextState = self.neurons[self.currentState].evaluateState()
            self.neurons[self.currentState].isCurrent = False
            if nextState is None:
                nextState = self.startState
            self.currentState = nextState
            self.neurons[self.currentState].isCurrent = True
            if new:
                self.neurons[nextState].moveTo()

        if preferences.show_debug_options and preferences.show_debug_timings:
            cm_timings.brain["evalState"] += time.time() - t

    def hightLight(self, frame):
        """This will be called for the agent that is the active selection"""
        for n in self.neurons.values():
            n.highLight(frame)
