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

import copy
import logging
import math
import os
import random
from collections import OrderedDict

import bpy

from .cm_brainClasses import Neuron, State

"""
class Logic{NAME}(Neuron):
    def core(self, inps, settings):
        :param inps: list of form [ImpulseContainer |
                                   dict of form {str: float | int}, ]
        :param settings: dict of form {str: str | int | float, }
        :rtype: int | dict of form {str: float | int}
"""

logger = logging.getLogger("CrowdMaster")


class LogicNEWINPUT(Neuron):
    """Retrieve information from the scene or about the agent"""

    def core(self, inps, settings):
        channels = self.brain.sim.lvars
        if settings["InputSource"] == "CONSTANT":
            return {"None": settings["Constant"]}

        elif settings["InputSource"] == "FLOCK":
            if settings["Flocking"] == "SEPARATE":
                if settings["TranslationAxis"] == "TX":
                    separateTx = channels["Flock"].separateTx(inps)
                    if separateTx is None:
                        return {}
                    return {"None": separateTx}
                elif settings["TranslationAxis"] == "TY":
                    separateTy = channels["Flock"].separateTy(inps)
                    if separateTy is None:
                        return {}
                    return {"None": separateTy}
                elif settings["TranslationAxis"] == "TZ":
                    separateTz = channels["Flock"].separateTz(inps)
                    if separateTz is None:
                        return {}
                    return {"None": separateTz}
            elif settings["Flocking"] == "COHERE":
                if settings["TranslationAxis"] == "TX":
                    cohereTx = channels["Flock"].cohereTx(inps)
                    if cohereTx is None:
                        return {}
                    return {"None": cohereTx}
                elif settings["TranslationAxis"] == "TY":
                    cohereTy = channels["Flock"].cohereTy(inps)
                    if cohereTy is None:
                        return {}
                    return {"None": cohereTy}
                elif settings["TranslationAxis"] == "TZ":
                    cohereTz = channels["Flock"].cohereTz(inps)
                    if cohereTz is None:
                        return {}
                    return {"None": cohereTz}
            else:  # ie. settings["Flocking"] == "ALIGN"
                if settings["RotationAxis"] == "RZ":
                    alignRz = channels["Flock"].alignRz(inps)
                    if alignRz is None:
                        return {}
                    return {"None": alignRz}
                elif settings["RotationAxis"] == "RX":
                    alignRx = channels["Flock"].alignRx(inps)
                    if alignRx is None:
                        return {}
                    return {"None": alignRx}

        elif settings["InputSource"] == "FORMATION":
            fChan = channels["Formation"].retrieve(settings["FormationGroup"])
            if fChan is None:
                return {}
            # TODO  Add fixed formations
            if settings["FormationOptions"] == "RZ":
                rz = fChan.rz
                if rz is None:
                    return {}
                return {"None": rz}
            elif settings["FormationOptions"] == "RX":
                rx = fChan.rx
                if rx is None:
                    return {}
                return {"None": rx}
            elif settings["FormationOptions"] == "DIST":
                dist = fChan.dist
                if dist is None:
                    return {}
                return {"None": dist}

        elif settings["InputSource"] == "GROUND":
            if settings["GroundOptions"] == "DH":
                gChan = channels["Ground"].retrieve(settings["GroundGroup"])
                dh = gChan.dh()
                return {"None": dh} if dh is not None else {}
            elif settings["GroundOptions"] == "ARZ":
                gChan = channels["Ground"].retrieve(settings["GroundGroup"])
                return {"None": gChan.aheadRz(self.settings["GroundAheadOffset"])}
            elif settings["GroundOptions"] == "ARX":
                gChan = channels["Ground"].retrieve(settings["GroundGroup"])
                return {"None": gChan.aheadRx(self.settings["GroundAheadOffset"])}

        elif settings["InputSource"] == "NOISE":
            noise = channels["Noise"]
            if settings["NoiseOptions"] == "RANDOM":
                return {"None": noise.random()}
            elif settings["NoiseOptions"] == "AGENTRANDOM":
                return {"None": noise.agentRandom(offset=hash(self))}
            elif settings["NoiseOptions"] == "WAVE":
                return {"None": noise.wave(self.settings["WaveOffset"],
                                           self.settings["WaveLength"])}

        elif settings["InputSource"] == "PATH":
            if settings["PathOptions"] == "RZ":
                return {"None": channels["Path"].rz(settings["PathName"])}
            elif settings["PathOptions"] == "RX":
                return {"None": channels["Path"].rx(settings["PathName"])}
            elif settings["PathOptions"] == "INLANE":
                agents = set()
                for into in inps:
                    for i in into:
                        agents.add(i)
                return channels["Path"].inlane(settings["PathName"],
                                               settings["PathLaneSearchDistance"],
                                               agents)

        elif settings["InputSource"] == "SOUND":
            sound = channels["Sound"]
            ch = sound.retrieve(settings["SoundFrequency"])
            if ch is None:
                return {}
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
                return ch.rz(settings["MinusRadius"])
            elif settings["SoundOptions"] == "RX":
                return ch.rx(settings["MinusRadius"])
            elif settings["SoundOptions"] == "DIST":
                return ch.dist(settings["MinusRadius"])
            elif settings["SoundOptions"] == "CLOSE":
                return ch.close(settings["MinusRadius"])
            elif settings["SoundOptions"] == "DB":
                return ch.db(settings["MinusRadius"])
            elif settings["SoundOptions"] == "CERT":
                return ch.cert(settings["MinusRadius"])
            elif settings["SoundOptions"] == "ACC":
                return ch.acc(settings["MinusRadius"])
            elif settings["SoundOptions"] == "OVER":
                return ch.over(settings["MinusRadius"])
            elif settings["SoundOptions"] == "HEADRZ":
                return ch.headrz(settings["MinusRadius"])
            elif settings["SoundOptions"] == "HEADRX":
                return ch.headrx(settings["MinusRadius"])

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
            elif settings["StateOptions"] == "QUERYTAG":
                return state.getTag(settings["StateTagName"])

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
            elif settings["WorldOptions"] == "EVENT":
                return world.event(settings["EventName"], settings["EventOptions"])

        elif settings["InputSource"] == "AGENTINFO":
            agent = channels["AgentInfo"]
            if settings["AgentInfoOptions"] == "GETTAG":
                if settings["GetTagName"].strip() != "":
                    return agent.getTag(inps, settings["GetTagName"].strip())
            elif settings["AgentInfoOptions"] == "HEADRZ":
                return agent.headingRz(inps)
            elif settings["AgentInfoOptions"] == "HEADRX":
                return agent.headingRx(inps)


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
            return math.e**(a * (value - u)**2)

        output = {}
        for into in inps:
            for i in into:
                if i in output:
                    logger.debug(
                        """LogicGRAPH data lost due to multiple inputs with the same key""")
                else:
                    if settings["CurveType"] == "RBF":
                        output[i] = (RBF(into[i]) * settings["Multiply"])
                    elif settings["CurveType"] == "RANGE":
                        output[i] = (linear(into[i]) * settings["Multiply"])
                    # cubic bezier could also be an option here (1/2 sided)
                    if settings["Invert"]:
                        output[i] = -output[i] + 1
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
                elif settings["operation"] == "set":
                    result[i] = settings["num1"]
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

        if len(results) > 0:
            if settings["SingleOutput"]:
                total = 1
                if settings["Method"] == "MUL":
                    for k, v in results.items():
                        total *= v
                else:  # Method == "MIN"
                    total = min(results.values()) if len(results) > 0 else 0
                return {"None": total}
            else:
                return results
        else:
            return {}


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
                        total *= (1 - i)
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
                            results[i] *= (1 - into[i])
                        else:  # Method == "MAX"
                            results[i] = min(1 - results[i], 1 - into[i])
                    else:
                        results[i] = (1 - into[i])
            results.update((k, 1 - v) for k, v in results.items())
            return results


class LogicNOT(Neuron):
    """Flip the logic state"""

    def core(self, inps, settings):
        result = {}
        for into in inps:
            for i in into:
                result[i] = -into[i] + 1
        return result


class LogicSTRONG(Neuron):
    """Make 1's and 0's stronger"""
    # https://www.desmos.com/calculator/izfhogpchr

    def core(self, inps, settings):
        results = {}
        for into in inps:
            for i in into:
                results[i] = into[i]**2 * (-2 * into[i] + 3)
        return results


class LogicWEAK(Neuron):
    """Make 1's and 0's stronger"""
    # https://www.desmos.com/calculator/izfhogpchr

    def core(self, inps, settings):
        results = {}
        for into in inps:
            for i in into:
                results[i] = 2 * into[i] - (into[i]**2 * (-2 * into[i] + 3))
        return results


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


class LogicFILTER(Neuron):
    """Only allow some values through"""

    def core(self, inps, settings):
        result = {}

        allEmpty = True
        for into in inps:
            if len(into) > 0:
                allEmpty = False
        if allEmpty:
            return result

        useTag = settings["Tag"]
        if useTag:
            tagName = settings["TagName"]
            if tagName in self.brain.tags:
                tagValue = self.brain.tags[tagName]
            else:
                tagValue = None

        # TODO what if multiple inputs have the same keys?
        if self.settings["Operation"] == "EQUAL":
            for into in inps:
                for i in into:
                    if useTag:
                        if into[i] == tagValue:
                            result[i] = into[i]
                    else:
                        if into[i] == self.settings["Value"]:
                            result[i] = into[i]
        elif self.settings["Operation"] == "NOT EQUAL":
            for into in inps:
                for i in into:
                    if useTag:
                        if into[i] != tagValue:
                            result[i] = into[i]
                    else:
                        if into[i] != self.settings["Value"]:
                            result[i] = into[i]
        elif self.settings["Operation"] == "LESS":
            for into in inps:
                for i in into:
                    if useTag:
                        if into[i] <= tagValue:
                            result[i] = into[i]
                    else:
                        if into[i] <= self.settings["Value"]:
                            result[i] = into[i]
        elif self.settings["Operation"] == "GREATER":
            for into in inps:
                for i in into:
                    if useTag:
                        if into[i] > tagValue:
                            result[i] = into[i]
                    else:
                        if into[i] > self.settings["Value"]:
                            result[i] = into[i]
        elif self.settings["Operation"] == "LEAST":
            leastVal = float("inf")
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
                result = {"None": total / count}
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
            out = val / (max(1, count))
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
                    logger.debug("Val: {}".format(into[i]))
                    Sm += into[i]
                    SmSquared += into[i] * abs(into[i])  # To retain sign
            if Sm == 0:
                out = 0
            else:
                out = SmSquared / Sm
        elif settings["MultiInputType"] == "SUM":
            out = 0
            for into in inps:
                for i in into:
                    out += into[i]
        outNm = settings["Output"]
        if outNm == "sk":
            self.brain.outvars["sk"][settings["SKName"]] = out
        else:
            self.brain.outvars[settings["Output"]] = out
        return out


class LogicPRIORITY(Neuron):
    """Combine inputs by priority"""

    def core(self, inps, settings):
        result = {}
        remaining = {}
        for v in range((len(inps) + 1) // 2):
            into = inps[2 * v]
            if 2 * v + 1 < len(inps):
                priority = inps[2 * v + 1]
                usesPriority = True
            else:
                priority = []
                usesPriority = False
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
        for key, rem in remaining.items():
            if rem != 0:
                result[key] += settings["defaultValue"] * rem
        return result


class LogicPRINT(Neuron):
    """print everything that is given to it"""

    def core(self, inps, settings):
        selected = [o.name for o in bpy.context.selected_objects]
        if self.brain.userid in selected:
            for into in inps:
                for i in into:
                    if settings["save_to_file"]:
                        with open(os.path.join(settings["output_filepath"], "CrowdMasterOutput.txt"), "a") as output:
                            message = settings["Label"] + " >> " + \
                                str(i) + " " + str(into[i]) + "\n"
                            output.write(message)
                    else:
                        logger.info("{} >> {} {}".format(
                            settings["Label"], i, into[i]))
        return 0


class LogicAction(Neuron):
    pass


logictypes = OrderedDict([
    ("NewInputNode", LogicNEWINPUT),
    ("GraphNode", LogicGRAPH),
    ("MathNode", LogicMATH),
    ("AndNode", LogicAND),
    ("OrNode", LogicOR),
    ("NotNode", LogicNOT),
    ("StrongNode", LogicSTRONG),
    ("WeakNode", LogicWEAK),
    ("SetTagNode", LogicSETTAG),
    ("FilterNode", LogicFILTER),
    ("MapNode", LogicMAP),
    ("OutputNode", LogicOUTPUT),
    ("PriorityNode", LogicPRIORITY),
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

    def __init__(self, *args, **kwargs):
        self.action = None
        self.strip = None
        State.__init__(self, *args, **kwargs)

    def isGroup(self):
        if len(self.actionName) > 0:
            return self.actionName[0] == "[" and self.actionName[-1] == "]"
        return False

    def moveTo(self):
        State.moveTo(self)

        if self.action in self.brain.sim.actions:
            actionobj = self.brain.sim.actions[self.action]
            # from .cm_motion.py
            obj = bpy.context.scene.objects[self.brain.userid]  # bpy object

            tr = obj.animation_data.nla_tracks.new()  # NLA track
            action = actionobj.action  # bpy action
            if action:
                currentFrame = bpy.context.scene.frame_current
                startTime = currentFrame - self.settings["Overlap"]
                self.strip = tr.strips.new("", startTime, action)
                self.strip.extrapolation = 'NOTHING'
                self.strip.use_auto_blend = True
                self.strip.mute = self.brain.freeze
            self.length = actionobj.length - self.settings["Overlap"]

        self.currentAction = self.action

    def evaluate(self):
        act = self.actionName
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
                        if self.isGroup():
                            acNm = self.actionName
                            for act in self.brain.sim.actionGroups[acNm[1:-1]]:
                                sm.tell(userid, key, act, val, self.name)
                        else:
                            sm.tell(userid, key, self.actionName,
                                    val, self.name)

            (state, action), pairedAgent = sm.getResult(userid)

            if state == self.name:
                self.finalValue = 1
                self.action = action
            else:
                self.finalValue = 0
            self.finalValueCalcd = True
        elif self.isGroup():
            State.evaluate(self)
            acNm = self.actionName
            state = random.getstate()
            if not self.randomActionFromGroup:
                random.seed(hash(self.brain.userid))
            self.action = random.choice(
                self.brain.sim.actionGroups[acNm[1:-1]])
            random.setstate(state)
        else:
            State.evaluate(self)
            self.action = self.actionName

    def evaluateState(self):
        self.currentFrame += 1

        """Check to see if the current state is still playing an animation"""

        # The proportion of the way through the state
        if self.length <= 0:
            complete = 1
        else:
            complete = self.currentFrame / self.length
            complete = 0.5 + complete / 2
        currentFrame = bpy.context.scene.frame_current
        self.resultLog[currentFrame] = (0.15, 0.4, complete)

        if self.currentAction in self.brain.sim.actions:
            actionobj = self.brain.sim.actions[self.currentAction]

            for data_path, data in actionobj.motiondata.items():
                x = data[0][self.currentFrame] - data[0][self.currentFrame - 1]
                y = data[1][self.currentFrame] - data[1][self.currentFrame - 1]
                z = data[2][self.currentFrame] - data[2][self.currentFrame - 1]
                scale = bpy.context.scene.objects[self.brain.userid].scale
                if data_path == "location":
                    self.brain.outvars["px"] += x * scale.x
                    self.brain.outvars["py"] += y * scale.y
                    self.brain.outvars["pz"] += z * scale.z
                elif data_path == "rotation_euler":
                    self.brain.outvars["rx"] += x
                    self.brain.outvars["ry"] += y
                    self.brain.outvars["rz"] += z

        # Check to see if there is a valid sync state to move to

        syncOptions = []
        for con in self.outputs:
            if self.neurons[con].interuptState and self.neurons[con].syncState:
                val = self.neurons[con].query()
                if val is not None and val > 0:
                    syncOptions.append((con, val))

        if len(syncOptions) > 0:
            self.strip.action_frame_end = self.currentFrame + 1
            if len(syncOptions) == 1:
                return True, syncOptions[0][0]
            else:
                return True, max(syncOptions, key=lambda v: v[1])[0]

        # Check to see if there is a valid interupt state to move to

        interuptOptions = []
        for con in self.outputs:
            conNeu = self.neurons[con]
            if conNeu.interuptState and not conNeu.syncState:
                val = conNeu.query()
                if val is not None and val > 0:
                    interuptOptions.append((con, val))

        if len(interuptOptions) > 0:
            if len(interuptOptions) == 1:
                nextState, nextVal = interuptOptions[0]
                # return True, interuptOptions[0][0]
            else:
                nextState, nextVal = max(interuptOptions, key=lambda v: v[1])
                # return True, max(interuptOptions, key=lambda v: v[1])[0]

            moveToInterupt = True

            val = self.neurons[self.name].query()
            if val is not None and val >= nextVal:
                moveToInterupt = False

            if moveToInterupt:
                self.strip.action_frame_end = self.currentFrame + 1
                return True, nextState

        # ==== Will stop here if there is a valid sync or interupt state ====

        if self.currentFrame < self.length - 1:
            return False, self.name

        # ==== Will stop here is this state hasn't reached its end ====

        options = []
        for con in self.outputs:
            val = self.neurons[con].query()
            if val is not None and val > 0:
                options.append((con, val))

        # If the cycleState button is checked then add a connection back to
        #    this state again.
        if self.cycleState and self.name not in self.outputs:
            val = self.neurons[self.name].query()
            if val is not None and val > 0:
                options.append((self.name, val))

        if len(options) > 0:
            if len(options) == 1:
                return True, options[0][0]
            else:
                return True, max(options, key=lambda v: v[1])[0]

        return False, None


statetypes = OrderedDict([
    ("StartState", StateSTART),
    ("ActionState", StateAction)
])
