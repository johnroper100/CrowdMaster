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

from collections import OrderedDict
import math
from .cm_brainClasses import Neuron, State
from .cm_pythonEmbededInterpreter import Interpreter
import copy
import bpy
import os
import random


"""
class Logic{NAME}(Neuron):
    def core(self, inps, settings):
        :param inps: list of form [ImpulseContainer |
                                   dict of form {str: float | int}, ]
        :param settings: dict of form {str: str | int | float, }
        :rtype: int | dict of form {str: float | int}
"""


class LogicINPUT(Neuron):
    """Retrieve information from the scene or about the agent"""

    def core(self, inps, settings):
        lvars = copy.copy(self.brain.lvars)
        lvars["math"] = math
        lvars["inps"] = inps
        result = eval(settings["Input"], lvars)
        return result


class LogicNEWINPUT(Neuron):
    """Retrieve information from the scene or about the agent"""

    def core(self, inps, settings):
        channels = self.brain.sim.lvars
        if settings["InputSource"] == "CONSTANT":
            return {"None": settings["Constant"]}

        elif settings["InputSource"] == "CROWD":
            if settings["Flocking"] == "SEPARATE":
                if settings["TranslationAxis"] == "TX":
                    separateTx = channels["Crowd"].separateTx(inps)
                    if separateTx is None:
                        return None
                    return {"None": separateTx}
                elif settings["TranslationAxis"] == "TY":
                    separateTy = channels["Crowd"].separateTy(inps)
                    if separateTy is None:
                        return None
                    return {"None": separateTy}
                elif settings["TranslationAxis"] == "TZ":
                    separateTz = channels["Crowd"].separateTz(inps)
                    if separateTz is None:
                        return None
                    return {"None": separateTz}
            elif settings["Flocking"] == "COHERE":
                if settings["TranslationAxis"] == "TX":
                    cohereTx = channels["Crowd"].cohereTx(inps)
                    if cohereTx is None:
                        return None
                    return {"None": cohereTx}
                elif settings["TranslationAxis"] == "TY":
                    cohereTy = channels["Crowd"].cohereTy(inps)
                    if cohereTy is None:
                        return None
                    return {"None": cohereTy}
                elif settings["TranslationAxis"] == "TZ":
                    cohereTz = channels["Crowd"].cohereTz(inps)
                    if cohereTz is None:
                        return None
                    return {"None": cohereTz}
            else:  # ie. settings["Flocking"] == "ALIGN"
                if settings["RotationAxis"] == "RZ":
                    alignRz = channels["Crowd"].alignRz(inps)
                    if alignRz is None:
                        return None
                    return {"None": alignRz}
                elif settings["RotationAxis"] == "RX":
                    alignRx = channels["Crowd"].alignRx(inps)
                    if alignRx is None:
                        return None
                    return {"None": alignRx}

        elif settings["InputSource"] == "FORMATION":
            fChan = channels["Formation"].retrieve(settings["FormationGroup"])
            if fChan is None:
                return None
            # TODO  Add fixed formations
            if settings["FormationOptions"] == "RZ":
                rz = fChan.rz
                if rz is None:
                    return None
                return {"None": rz}
            elif settings["FormationOptions"] == "RX":
                rx = fChan.rx
                if rx is None:
                    return None
                return {"None": rx}
            elif settings["FormationOptions"] == "DIST":
                dist = fChan.dist
                if dist is None:
                    return None
                return {"None": dist}

        elif settings["InputSource"] == "GROUND":
            gChan = channels["Ground"].retrieve(settings["GroundGroup"])
            return {"None": gChan.dh()}

        elif settings["InputSource"] == "NOISE":
            noise = channels["Noise"]
            if settings["NoiseOptions"] == "RANDOM":
                return {"None": noise.random()}
            elif settings["NoiseOptions"] == "AGENTRANDOM":
                return {"None": noise.agentRandom(offset=hash(self))}

        elif settings["InputSource"] == "PATH":
            if settings["PathOptions"] == "RZ":
                return {"None": channels["Path"].rz(settings["PathName"])}
            elif settings["PathOptions"] == "RX":
                return {"None": channels["Path"].rx(settings["PathName"])}

        elif settings["InputSource"] == "SOUND":
            sound = channels["Sound"]
            ch = sound.retrieve(settings["SoundFrequency"])
            if ch is None:
                return None
            if settings["SoundMode"] == "BASIC":
                ch.predictNext = False
                ch.steeringNext = False
            elif settings["SoundMode"] == "PREDICTION":
                ch.predictNext = True
                ch.steeringNext = False
            elif settings["SoundMode"] == "STEERING":
                ch.predictNext = False
                ch.steeringNext = True
            if settings["SoundOptions"] == "RZ":
                return ch.rz
            elif settings["SoundOptions"] == "RX":
                return ch.rx
            elif settings["SoundOptions"] == "DIST":
                return ch.dist
            elif settings["SoundOptions"] == "CLOSE":
                return ch.close
            elif settings["SoundOptions"] == "DB":
                return ch.db
            elif settings["SoundOptions"] == "CERT":
                return ch.cert
            elif settings["SoundOptions"] == "ACC":
                return ch.acc
            elif settings["SoundOptions"] == "OVER":
                return ch.over

        elif settings["InputSource"] == "STATE":
            state = channels["State"]
            if settings["StateOptions"] == "RADIUS":
                return {"None": state.radius}
            elif settings["StateOptions"] == "SPEED":
                return {"None": state.speed}
            elif settings["StateOptions"] == "GLOBALVELX":
                return {"None": state.velocity.x}
            elif settings["StateOptions"] == "GLOBALVELY":
                return {"None": state.velocity.y}
            elif settings["StateOptions"] == "GLOBALVELZ":
                return {"None": state.velocity.z}

        elif settings["InputSource"] == "WORLD":
            world = channels["World"]
            if settings["WorldOptions"] == "TARGET":
                if settings["TargetOptions"] == "RZ":
                    tgt = world.target(settings["TargetObject"])
                    return {"None": tgt.rz}
                elif settings["TargetOptions"] == "RX":
                    tgt = world.target(settings["TargetObject"])
                    return {"None": tgt.rx}
                elif settings["TargetOptions"] == "ARRIVED":
                    tgt = world.target(settings["TargetObject"])
                    return {"None": tgt.arrived}
            elif settings["WorldOptions"] == "TIME":
                return {"None": channels["World"].time}


class LogicGRAPH(Neuron):
    """Return value 0 to 1 mapping from graph"""

    def core(self, inps, settings):
        preferences = bpy.context.user_preferences.addons[__package__].preferences

        def linear(value):
            lz = settings["LowerZero"]
            lo = settings["LowerOne"]
            uo = settings["UpperOne"]
            uz = settings["UpperZero"]

            if value < lz:
                return 0
            elif value < lo:
                return (value - lz) / (lo - lz)
            elif value <= uo:
                return 1
            elif value < uz:
                return (uz - value) / (uz - uo)
            else:
                return 0

        def RBF(value):
            u = settings["RBFMiddle"]
            TPP = settings["RBFTenPP"]

            a = math.log(0.1) / (TPP**2)
            return math.e**(a*(value-u)**2)

        output = {}
        for into in inps:
            for i in into:
                if i in output:
                    if preferences.show_debug_options:
                        print("""LogicGRAPH data lost due to multiple inputs with the same key""")
                else:
                    if settings["CurveType"] == "RBF":
                        output[i] = (RBF(into[i])*settings["Multiply"])
                    elif settings["CurveType"] == "RANGE":
                        output[i] = (linear(into[i])*settings["Multiply"])
                    # cubic bezier could also be an option here (1/2 sided)
        return output

class LogicMATH(Neuron):
    """returns the values added/subtracted/multiplied/divided together"""

    def core(self, inps, settings):
        result = {}
        for into in inps:
            for i in into:
                if settings["operation"] == "add":
                    result[i] = into[i] + settings["num1"]
                elif settings["operation"] == "sub":
                    result[i] = into[i] - settings["num1"]
                elif settings["operation"] == "mul":
                    result[i] = into[i] * settings["num1"]
                elif settings["operation"] == "div":
                    result[i] = into[i] / settings["num1"]
        return result


class LogicAND(Neuron):
    """returns the values multiplied together"""

    def core(self, inps, settings):
        results = {}
        for into in inps:
            for i in into:
                if i in results:
                    if settings["Method"] == "MUL":
                        results[i] *= into[i]
                    else:  # Method == "MIN"
                        results[i] = min(results[i], into[i])
                else:
                    inAll = True
                    if settings["IncludeAll"]:
                        for intoB in inps:
                            inAll &= i in intoB
                    if inAll:
                        results[i] = into[i]

        if settings["SingleOutput"]:
            total = 1
            for k, v in results.items():
                total *= v
            if settings["Method"] == "MUL":
                for k, v in results.items():
                    total *= v
            else:  # Method == "MIN"
                total = min(results)
            return {"None": total}
        else:
            return results


class LogicOR(Neuron):
    """If any of the values are high return a high value
    1 - ((1-a) * (1-b) * (1-c)...)"""

    def core(self, inps, settings):
        if settings["SingleOutput"]:
            if settings["Method"] == "MUL":
                total = 1
            else:
                total = 0
            for into in inps:
                if settings["Method"] == "MUL":
                    for i in [into[i] for i in into]:
                        total *= (1-i)
                else:  # Method == "MAX"
                    total = max(list(into.values()) + [total])
            if settings["Method"] == "MUL":
                total = 1 - total
            return total
        else:
            results = {}
            for into in inps:
                for i in into:
                    if i in results:
                        if settings["Method"] == "MUL":
                            results[i] *= (1-into[i])
                        else:  # Method == "MAX"
                            results[i] = min(1-results[i], 1-into[i])
                    else:
                        results[i] = (1-into[i])
            results.update((k, 1-v) for k, v in results.items())
            return results


class LogicSTRONG(Neuron):
    """Make 1's and 0's stronger"""
    # https://www.desmos.com/calculator/izfhogpchr

    def core(self, inps, settings):
        results = {}
        for into in inps:
            for i in into:
                results[i] = into[i]**2 * (-2*into[i] + 3)
        return results


class LogicWEAK(Neuron):
    """Make 1's and 0's stronger"""
    # https://www.desmos.com/calculator/izfhogpchr

    def core(self, inps, settings):
        results = {}
        for into in inps:
            for i in into:
                results[i] = 2*into[i] - (into[i]**2 * (-2*into[i] + 3))
        return results


class LogicQUERYTAG(Neuron):
    """Return the value of Tag (normally 1) or else 0"""

    def core(self, inps, settings):
        results = {}
        if settings["Tag"] in self.brain.tags:
            return self.brain.tags[settings["Tag"]]
        else:
            return 0


class LogicSETTAG(Neuron):
    """If any of the inputs are above the Threshold level add or remove the
    Tag from the agents tags"""

    def core(self, inps, settings):
        condition = False
        total = 0
        count = 0
        for into in inps:
            for i in into:
                if into[i] > settings["Threshold"]:
                    condition = True
                total += into[i]
                count += 1
        if settings["UseThreshold"]:
            if condition:
                if settings["Action"] == "ADD":
                    self.brain.tags[settings["Tag"]] = 1
                else:
                    if settings["Tag"] in self.brain.tags:
                        del self.brain.tags[settings["Tag"]]
        else:
            if settings["Action"] == "ADD":
                self.brain.tags[settings["Tag"]] = total
            else:
                if settings["Tag"] in self.brain.tags:
                    del self.brain.tags[settings["Tag"]]
        return settings["Threshold"]


class LogicVARIABLE(Neuron):
    """Set or retrieve (or both) an agent variable (0 if it doesn't exist)"""

    def core(self, inps, settings):
        count = 0
        for into in inps:
            for i in into:
                self.brain.agvars[settings["Variable"]] += into[i]
                count += 1
        if count:
            self.brain.agvars[settings["Variable"]] /= count
        if settings["Variable"] in self.brain.agvars:
            out = self.brain.agvars[settings["Variable"]]  # out is not actually used!
        else:
            out = 0  # out is not actually used!
        # TODO Doesn't work
        return self.brain.agvars[settings["Variable"]]


class LogicFILTER(Neuron):
    """Only allow some values through"""

    def core(self, inps, settings):
        result = {}

        # TODO what if multiple inputs have the same keys?
        if self.settings["Operation"] == "EQUAL":
            for into in inps:
                for i in into:
                    if into[i] == self.settings["Value"]:
                        result[i] = into[i]
        elif self.settings["Operation"] == "NOT EQUAL":
            for into in inps:
                for i in into:
                    if into[i] != self.settings["Value"]:
                        result[i] = into[i]
        elif self.settings["Operation"] == "LESS":
            for into in inps:
                for i in into:
                    if into[i] <= self.settings["Value"]:
                        result[i] = into[i]
        elif self.settings["Operation"] == "GREATER":
            for into in inps:
                for i in into:
                    if into[i] > self.settings["Value"]:
                        result[i] = into[i]
        elif self.settings["Operation"] == "LEAST":
            leastVal = -float("inf")
            leastName = "None"
            for into in inps:
                for i in into:
                    if into[i] < leastVal:
                        leastVal = into[i]
                        leastName = i
            result = {leastName: leastVal}
        elif self.settings["Operation"] == "MOST":
            mostVal = -float("inf")
            mostName = "None"
            for into in inps:
                for i in into:
                    if into[i] > mostVal:
                        mostVal = into[i]
                        mostName = i
            result = {mostName: mostVal}
        elif self.settings["Operation"] == "AVERAGE":
            total = 0
            count = 0
            for into in inps:
                for i in into:
                    total += into[i]
                    count += 1
            if count != 0:
                result = {"None": total/count}
        return result


class LogicMAP(Neuron):
    """Map the input from the input range to the output range
    (extrapolates outside of input range)"""

    def core(self, inps, settings):
        result = {}
        if settings["LowerInput"] != settings["UpperInput"]:
            for into in inps:
                for i in into:
                    num = into[i]
                    li = settings["LowerInput"]
                    ui = settings["UpperInput"]
                    lo = settings["LowerOutput"]
                    uo = settings["UpperOutput"]
                    result[i] = ((uo - lo) / (ui - li)) * (num - li) + lo
        return result


class LogicOUTPUT(Neuron):
    """Sets an agents output. (Has to be picked up in cm_agents.Agents)"""

    def core(self, inps, settings):
        preferences = bpy.context.user_preferences.addons[__package__].preferences
        val = 0
        if settings["MultiInputType"] == "AVERAGE":
            count = 0
            for into in inps:
                for i in into:
                    val += into[i]
                    count += 1
            out = val/(max(1, count))
        elif settings["MultiInputType"] == "MAX":
            out = 0
            for into in inps:
                for i in into:
                    if abs(into[i]) > abs(out):
                        out = into[i]
        elif settings["MultiInputType"] == "SIZEAVERAGE":
            """Takes a weighed average of the inputs where smaller values have
            less of an impact on the final result"""
            Sm = 0
            SmSquared = 0
            for into in inps:
                for i in into:
                    if preferences.show_debug_options:
                        print("Val:", into[i])
                    Sm += into[i]
                    SmSquared += into[i] * abs(into[i])  # To retain sign
            # print(Sm, SmSquared)
            if Sm == 0:
                out = 0
            else:
                out = SmSquared / Sm
        elif settings["MultiInputType"] == "SUM":
            out = 0
            for into in inps:
                for i in into:
                    out += into[i]
        self.brain.outvars[settings["Output"]] = out
        return out


class LogicPRIORITY(Neuron):
    """Combine inputs by priority"""

    def core(self, inps, settings):
        result = {}
        remaining = {}
        for v in range((len(inps)+1)//2):
            into = inps[2*v]
            # print("into", into)
            if 2*v+1 < len(inps):
                priority = inps[2*v+1]
                usesPriority = True
            else:
                priority = []
                usesPriority = False
            # print("priority", priority)
            for i in into:
                if i in priority:
                    # TODO what if priority[i] < 0?
                    if i in result:
                        contribution = priority[i] * remaining[i]
                        result[i] += into[i] * contribution
                        remaining[i] -= contribution
                    else:
                        result[i] = into[i] * priority[i]
                        remaining[i] = 1 - priority[i]
                elif not usesPriority:
                    if i in result:
                        contribution = remaining[i]
                        result[i] += into[i] * contribution
                        remaining[i] -= 0
                    else:
                        result[i] = into[i]
                        remaining[i] = 0
            # print("resultPartial", result)
        for key, rem in remaining.items():
            if rem != 0:
                result[key] += settings["defaultValue"] * rem
        return result


class LogicEVENT(Neuron):
    """Check if an event is happening that frame"""

    def core(self, inps, settings):
        events = bpy.context.scene.cm_events.coll
        en = settings["EventName"]
        for e in events:
            if e.eventname == en:
                result = 1
                if e.category == "Time" or e.category == "Time+Volume":
                    if e.time != bpy.context.scene.frame_current:
                        result = 0
                if e.category == "Volume" or e.category == "Time+Volume":
                    if result:
                        pt = bpy.data.objects[self.brain.userid].location
                        l = bpy.data.objects[e.volume].location
                        d = bpy.data.objects[e.volume].dimensions

                        if not (l.x-(d.x/2) <= pt.x <= l.x+(d.x/2) and
                                l.y-(d.y/2) <= pt.y <= l.y+(d.y/2) and
                                l.z-(d.z/2) <= pt.z <= l.z+(d.z/2)):
                            result = 0
                if result:
                    return result
        return 0


class LogicPYTHON(Neuron):
    """execute a python expression"""

    def core(self, inps, settings):
        global Inter
        setup = copy.copy(self.brain.lvars)
        setup["inps"] = inps
        setup["settings"] = settings
        Inter.setup(setup)
        Inter.enter(settings["Expression"]["value"])
        result = Inter.getoutput()
        return result


Inter = Interpreter()


class LogicPRINT(Neuron):
    """print everything that is given to it"""

    def core(self, inps, settings):
        selected = [o.name for o in bpy.context.selected_objects]
        if self.brain.userid in selected:
            for into in inps:
                for i in into:
                    if settings["save_to_file"] == True:
                        with open(os.path.join(settings["output_filepath"], "CrowdMasterOutput.txt"), "a") as output:
                            message = settings["Label"] + " >> " + str(i) + " " + str(into[i]) + "\n"
                            output.write(message)
                    else:
                        print(settings["Label"], ">>", i, into[i])
        return 0


class LogicAction(Neuron):
    pass


logictypes = OrderedDict([
    ("InputNode", LogicINPUT),
    ("NewInputNode", LogicNEWINPUT),
    ("GraphNode", LogicGRAPH),
    ("MathNode", LogicMATH),
    ("AndNode", LogicAND),
    ("OrNode", LogicOR),
    ("StrongNode", LogicSTRONG),
    ("WeakNode", LogicWEAK),
    ("QueryTagNode", LogicQUERYTAG),
    ("SetTagNode", LogicSETTAG),
    ("VariableNode", LogicVARIABLE),
    ("FilterNode", LogicFILTER),
    ("MapNode", LogicMAP),
    ("OutputNode", LogicOUTPUT),
    ("PriorityNode", LogicPRIORITY),
    ("EventNode", LogicEVENT),
    ("PythonNode", LogicPYTHON),
    ("PrintNode", LogicPRINT)
])


class StateSTART(State):
    """Points to the first state for the agent to be in"""
    def moveTo(self):
        self.length = random.randint(self.settings["minRandWait"],
                                         self.settings["maxRandWait"])
        State.moveTo(self)

class StateAction(State):
    """The normal state in a state machine"""
    def moveTo(self):
        State.moveTo(self)

        act = self.actionName
        if act in self.brain.sim.actions:
            actionobj = self.brain.sim.actions[act]  # from .cm_motion.py
            obj = bpy.context.scene.objects[self.brain.userid]  # bpy object

            tr = obj.animation_data.nla_tracks.new()  # NLA track
            action = actionobj.action  # bpy action
            if action:
                currentFrame = bpy.context.scene.frame_current
                self.strip = tr.strips.new("", currentFrame, action)
                self.strip.extrapolation = 'NOTHING'
                self.strip.use_auto_blend = True
            self.length = actionobj.length

            """tr = obj.animation_data.nla_tracks.new()  # NLA track
            action = actionobj.motion
            if action:
                strip = tr.strips.new("", sce.frame_current, action)
                strip.extrapolation = 'HOLD_FORWARD'
                strip.use_auto_blend = False
                strip.blend_type = 'ADD'"""

    def evaluate(self):
        if self.syncState:
            possible = False
            for sInp in self.inputs:
                if self.neurons[sInp].isCurrent:
                    possible = True
                    break

            if not possible or len(self.valueInputs) == 0:
                self.finalValue = 0
                self.finalValueCalcd = True
                return

            sm = self.brain.sim.syncManager
            userid = self.brain.userid

            for inp in self.valueInputs:
                vals = self.neurons[inp].evaluate()
                for key, v in vals.items():
                    if self.settings["RandomInput"]:
                        val = v + (self.settings["ValueDefault"] *
                                   v * random.random())
                    else:
                        val = v + (v * self.settings["ValueDefault"])
                    if val > 0:
                        sm.tell(userid, key, self.actionName, val, self.name)

            state, pairedAgent = sm.getResult(userid)

            if state == self.name:
                self.finalValue = 1
            else:
                self.finalValue = 0
            self.finalValueCalcd = True
        else:
            State.evaluate(self)

    def evaluateState(self):
        self.currentFrame += 1

        """Check to see if the current state is still playing an animation"""
        # print("currentFrame", self.currentFrame, "length", self.length)
        # print("Value compared", self.length - 2 - self.settings["Fade out"])

        # The proportion of the way through the state
        if self.length == 0:
            complete = 1
        else:
            complete = self.currentFrame/self.length
            complete = 0.5 + complete/2
        currentFrame = bpy.context.scene.frame_current
        self.resultLog[currentFrame] = ((0.15, 0.4, complete))

        if self.actionName in self.brain.sim.actions:
            actionobj = self.brain.sim.actions[self.actionName]

            for data_path, data in actionobj.motiondata.items():
                x = data[0][self.currentFrame] - data[0][self.currentFrame - 1]
                y = data[1][self.currentFrame] - data[1][self.currentFrame - 1]
                z = data[2][self.currentFrame] - data[2][self.currentFrame - 1]
                if data_path == "location":
                    self.brain.outvars["px"] += x
                    self.brain.outvars["py"] += y
                    self.brain.outvars["pz"] += z
                elif data_path == "rotation_euler":
                    self.brain.outvars["rx"] += x
                    self.brain.outvars["ry"] += y
                    self.brain.outvars["rz"] += z

        # Check to see if there is a valid sync state to move to

        syncOptions = []
        for con in self.outputs:
            if self.neurons[con].syncState:
                val = self.neurons[con].query()
                if val is not None and val > 0:
                    syncOptions.append((con, val))

                    if len(syncOptions) > 0:
                        self.strip.action_frame_end = self.currentFrame + 1
                        if len(syncOptions) == 1:
                            return True, syncOptions[0][0]
                        else:
                            return True, max(syncOptions, key=lambda v: v[1])[0]

        # ==== Will stop here if there is a valid sync state ====

        if self.currentFrame < self.length - 1:
            return False, self.name

        # ==== Will stop here is this state hasn't reached its end ====

        options = []
        for con in self.outputs:
            val = self.neurons[con].query()
            # print(con, val)
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


class StateActionGroup(State):
    """A state in a state machine containing a group of actions"""
    def moveTo(self):
        State.moveTo(self)

        actGp = self.brain.sim.actionGroups[self.settings["GroupName"]]

        self.actionName = random.choice(actGp)

        act = self.actionName
        if act in self.brain.sim.actions:
            actionobj = self.brain.sim.actions[act]  # from .cm_motion.py
            obj = bpy.context.scene.objects[self.brain.userid]  # bpy object

            tr = obj.animation_data.nla_tracks.new()  # NLA track
            action = actionobj.action  # bpy action
            if action:
                currentFrame = bpy.context.scene.frame_current
                self.strip = tr.strips.new("", currentFrame, action)
                self.strip.extrapolation = 'NOTHING'
                self.strip.use_auto_blend = True
            self.length = actionobj.length

    def evaluateState(self):
        self.currentFrame += 1

        """Check to see if the current state is still playing an animation"""
        # The proportion of the way through the state
        if self.length == 0:
            complete = 1
        else:
            complete = self.currentFrame/self.length
            complete = 0.5 + complete/2
        currentFrame = bpy.context.scene.frame_current
        self.resultLog[currentFrame] = ((0.15, 0.4, complete))

        if self.actionName in self.brain.sim.actions:
            actionobj = self.brain.sim.actions[self.actionName]

            for data_path, data in actionobj.motiondata.items():
                x = data[0][self.currentFrame] - data[0][self.currentFrame - 1]
                y = data[1][self.currentFrame] - data[1][self.currentFrame - 1]
                z = data[2][self.currentFrame] - data[2][self.currentFrame - 1]
                if data_path == "location":
                    self.brain.outvars["px"] += x
                    self.brain.outvars["py"] += y
                    self.brain.outvars["pz"] += z
                elif data_path == "rotation_euler":
                    self.brain.outvars["rx"] += x
                    self.brain.outvars["ry"] += y
                    self.brain.outvars["rz"] += z

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


statetypes = OrderedDict([
    ("StartState", StateSTART),
    ("ActionState", StateAction),
    ("ActionGroupState", StateActionGroup)
])
