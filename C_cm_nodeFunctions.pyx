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


class LogicINPUT(Neuron):
    """Retrieve information from the scene or about the agent"""

    def core(self, list inps, dict settings):
        lvars = copy.copy(self.brain.lvars)
        lvars["math"] = math
        lvars["inps"] = inps
        result = eval(settings["Input"], lvars)
        return result


class LogicNEWINPUT(Neuron):
    """Retrieve information from the scene or about the agent"""

    def core(self, list inps, dict settings):
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

    def core(self, list inps, dict settings):
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
                if settings["CurveType"] == "RBF":
                    output[i] = (RBF(into[i])*settings["Multiply"])
                elif settings["CurveType"] == "RANGE":
                    output[i] = (linear(into[i])*settings["Multiply"])
                # cubic bezier could also be an option here (1/2 sided)
        return output


class LogicMATH(Neuron):
    """returns the values added/subtracted/multiplied/divided together"""

    def core(self, list inps, dict settings):
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

    def core(self, list inps, dict settings):
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

    def core(self, list inps, dict settings):
        cdef double lookup, lookupResults, total, tmp
        results = {}
        if settings["SingleOutput"]:
            method = settings["Method"]
            if method == "MUL":
                total = 1
            else:
                total = 0
            for into in inps:
                #if method == "MUL":
                for i in into:
                    lookup = into[i]
                    tmp = -lookup
                    tmp = 1 + tmp
                    total *= tmp
                else:  # Method == "MAX"
                    total = max(list(into.values()) + [total])
            if method == "MUL":
                total = 1 - total
            results["None"] = total
            #return total
        else:
            #results = {}
            for into in inps:
                for i in into:
                    if i in results:
                        method = settings["Method"] == "MUL"
                        if method:
                            lookup = into[i]
                            tmp = -lookup
                            tmp = 1 + tmp
                            results[i] = tmp
                        else:  # Method == "MAX"
                            lookup = into[i]
                            lookupResults = results[i]
                            tmp = max(lookupResults, lookup)
                            tmp = 1 - tmp
                            results[i] = tmp
                            #results[i] = min(1-results[i], 1-lookup)
                    else:
                        lookup = into[i]
                        tmp = 1 - lookup
                        results[i] = tmp
            #results.update((k, 1-v) for k, v in results.items())
            for k in results:
                lookup = results[k]
                tmp = 1 - lookup
                results[k] = tmp
        return results


class LogicSTRONG(Neuron):
    """Make 1's and 0's stronger"""
    # https://www.desmos.com/calculator/izfhogpchr

    def core(self, list inps, dict settings):
        cdef double lookup, tmp
        results = {}
        for into in inps:
            for i in into:
                lookup = into[i]
                tmp = lookup**2 * (-2*lookup + 3)
                #results[i] = into[i]**2 * (-2*into[i] + 3)
                results[i] = tmp
        return results


class LogicWEAK(Neuron):
    """Make 1's and 0's stronger"""
    # https://www.desmos.com/calculator/izfhogpchr

    def core(self, list inps, dict settings):
        cdef double lookup, tmp
        results = {}
        for into in inps:
            for i in into:
                lookup = into[i]
                tmp = 2*lookup - (lookup**2 * (-2*lookup + 3))
                #results[i] = 2*into[i] - (into[i]**2 * (-2*into[i] + 3))
                results[i] = tmp
        return results


class LogicQUERYTAG(Neuron):

    def core(self, list inps, dict settings):
        results = {}
        if settings["Tag"] in self.brain.tags:
            return self.brain.tags[settings["Tag"]]
        else:
            return 0


class LogicSETTAG(Neuron):

    def core(self, list inps, dict settings):
        cdef double lookup, tmp, threshold, count
        condition = False
        total = 0
        count = 0
        for into in inps:
            for i in into:
                lookup = into[i]
                threshold = settings["Threshold"]
                if lookup > threshold:
                    condition = True
                total += lookup
                count = count + 1
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

"""
class LogicVARIABLE(Neuron):

    def core(self, list inps, dict settings):
        cdef lookup, tmp
        count = 0
        for into in inps:
            for i in into:
                lookup = into[i]
                self.brain.agvars[settings["Variable"]] += lookup
                count += 1
        if count:
            self.brain.agvars[settings["Variable"]] /= count
        if settings["Variable"] in self.brain.agvars:
            out = self.brain.agvars[settings["Variable"]]  # out is not actually used!
        else:
            out = 0  # out is not actually used!
        # TODO Doesn't work
        return self.brain.agvars[settings["Variable"]]
"""

class LogicFILTER(Neuron):

    def core(self, list inps, dict settings):
        cdef double lookup, count

        result = {}

        # TODO what if multiple inputs have the same keys?
        if self.settings["Operation"] == "EQUAL":
            for into in inps:
                for i in into:
                    lookup = into[i]
                    if lookup == self.settings["Value"]:
                        result[i] = lookup
        elif self.settings["Operation"] == "NOT EQUAL":
            for into in inps:
                for i in into:
                    lookup = into[i]
                    if not (lookup == self.settings["Value"]):
                        result[i] = lookup
        elif self.settings["Operation"] == "LESS":
            for into in inps:
                for i in into:
                    lookup = into[i]
                    if lookup <= self.settings["Value"]:
                        result[i] = lookup
        elif self.settings["Operation"] == "GREATER":
            for into in inps:
                for i in into:
                    lookup = into[i]
                    if lookup > self.settings["Value"]:
                        result[i] = lookup
        elif self.settings["Operation"] == "LEAST":
            leastVal = -float("inf")
            leastName = "None"
            for into in inps:
                for i in into:
                    lookup = into[i]
                    if lookup < leastVal:
                        leastVal = lookup
                        leastName = i
            result = {leastName: leastVal}
        elif self.settings["Operation"] == "MOST":
            mostVal = -float("inf")
            mostName = "None"
            for into in inps:
                for i in into:
                    lookup = into[i]
                    if lookup > mostVal:
                        mostVal = lookup
                        mostName = i
            result = {mostName: mostVal}
        elif self.settings["Operation"] == "AVERAGE":
            total = 0
            count = 0
            for into in inps:
                for i in into:
                    lookup = into[i]
                    total += lookup
                    count += 1
            if count > 0:
                result = {"None": total/count}
        return result


class LogicMAP(Neuron):

    def core(self, list inps, dict settings):
        cdef double num, li, ui, lo, uo, oo, ii, oi
        result = {}

        li = settings["LowerInput"]
        ui = settings["UpperInput"]
        lo = settings["LowerOutput"]
        uo = settings["UpperOutput"]

        if not (li == ui):
            oo = uo - lo
            ii = ui - li
            io = oo / ii
            for into in inps:
                for i in into:
                    num = into[i]
                    result[i] = io * (num - li) + lo
        return result


class LogicOUTPUT(Neuron):

    def core(self, list inps, dict settings):
        cdef lookup, count, val, out

        val = 0
        if settings["MultiInputType"] == "AVERAGE":
            count = 0
            for into in inps:
                for i in into:
                    lookup = into[i]
                    val = val + lookup
                count = count + len(into)
            out = val/(max(1, count))
        elif settings["MultiInputType"] == "MAX":
            out = 0
            for into in inps:
                for i in into:
                    lookup = into[i]
                    if abs(lookup) > abs(out):
                        out = lookup
        elif settings["MultiInputType"] == "SIZEAVERAGE":
            Sm = 0
            SmSquared = 0
            for into in inps:
                for i in into:
                    lookup = into[i]
                    Sm += lookup
                    SmSquared += lookup * abs(lookup)  # To retain sign
            # print(Sm, SmSquared)
            if Sm == 0:
                out = 0
            else:
                out = SmSquared / Sm
        elif settings["MultiInputType"] == "SUM":
            out = 0
            for into in inps:
                for i in into:
                    lookup = into[i]
                    out += lookup
        self.brain.outvars[settings["Output"]] = out
        return out


class LogicPRIORITY(Neuron):

    def core(self, list inps, dict settings):
        cdef double lookup, pLookup, rLookup, contribution
        cdef int d, do

        result = {}
        remaining = {}
        for v in range((len(inps)+1)//2):
            d = 2*v
            do = d + 1
            into = inps[d]
            if do < len(inps):
                priority = inps[do]
                usesPriority = True
            else:
                priority = []
                usesPriority = False
            # print("priority", priority)
            for i in into:
                lookup = into[i]
                if i in priority:
                    pLookup = priority[i]
                    if pLookup < 0:
                        pLookup = 0
                    if i in result:
                        rLookup = remaining[i]
                        contribution = pLookup * rLookup
                        result[i] += lookup * contribution
                        remaining[i] -= contribution
                    else:
                        result[i] = lookup * pLookup
                        remaining[i] = 1 - pLookup
                elif not usesPriority:
                    if i in result:
                        rLookup = remaining[i]
                        contribution = rLookup
                        result[i] += lookup * contribution
                    else:
                        result[i] = lookup
                        remaining[i] = 0
            # print("resultPartial", result)
        for key, rem in remaining.items():
            if rem != 0:
                result[key] += settings["defaultValue"] * rem
        return result


class LogicEVENT(Neuron):

    def core(self, list inps, dict settings):
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

    def core(self, list inps, dict settings):
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

    def core(self, list inps, dict settings):
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
    #("VariableNode", LogicVARIABLE),
    ("FilterNode", LogicFILTER),
    ("MapNode", LogicMAP),
    ("OutputNode", LogicOUTPUT),
    ("PriorityNode", LogicPRIORITY),
    ("EventNode", LogicEVENT),
    ("PythonNode", LogicPYTHON),
    ("PrintNode", LogicPRINT)
])


class StateSTART(State):
    def moveTo(self):
        self.length = random.randint(self.settings["minRandWait"],
                                         self.settings["maxRandWait"])
        State.moveTo(self)


class StateAction(State):
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
        cdef int currentFrame, plusOne
        currentFrame = self.currentFrame
        plusOne = currentFrame + 1
        self.currentFrame = plusOne

        #Check to see if the current state is still playing an animation
        # print("currentFrame", self.currentFrame, "length", self.length)
        # print("Value compared", self.length - 2 - self.settings["Fade out"])

        cdef double complete

        # The proportion of the way through the state
        if self.length == 0:
            complete = 1
        else:
            complete = self.currentFrame/self.length
            complete = 0.5 + complete/2
        currentFrame = bpy.context.scene.frame_current
        self.resultLog[currentFrame] = ((0.15, 0.4, complete))

        cdef int cur, prv, nxt
        cur = self.currentFrame
        prv = cur - 1
        nxt = cur + 1

        cdef double x, y, z

        if self.actionName in self.brain.sim.actions:
            actionobj = self.brain.sim.actions[self.actionName]

            for data_path, data in actionobj.motiondata.items():
                x = data[0][cur] - data[0][prv]
                y = data[1][cur] - data[1][prv]
                z = data[2][cur] - data[2][prv]
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
                        self.strip.action_frame_end = nxt
                        if len(syncOptions) == 1:
                            return True, syncOptions[0][0]
                        else:
                            return True, max(syncOptions, key=lambda v: v[1])[0]

        # ==== Will stop here if there is a valid sync state ====

        cdef int length, lenMinOne
        length = self.length
        lenMinOne = length - 1

        if self.currentFrame < lenMinOne:
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

"""
class StateActionGroup(State):
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

        #Check to see if the current state is still playing an animation
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
"""

statetypes = OrderedDict([
    ("StartState", StateSTART),
    ("ActionState", StateAction),
    #("ActionGroupState", StateActionGroup)
])
