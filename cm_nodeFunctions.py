from collections import OrderedDict
import math
from . import cm_brainClasses
from .cm_brainClasses import Neuron, State
from . import cm_pythonEmbededInterpreter
from .cm_pythonEmbededInterpreter import Interpreter
import copy
import bpy
import os


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

class LogicGRAPH(Neuron):
    """Return value 0 to 1 mapping from graph"""

    def core(self, inps, settings):
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
                if i.key in output:
                    print("""LogicGRAPH data lost due to multiple inputs
                             with the same key""")
                else:
                    if settings["CurveType"] == "RBF":
                        output[i.key] = (RBF(i.val)*settings["Multiply"])
                    elif settings["CurveType"] == "RANGE":
                        output[i.key] = (linear(i.val)*settings["Multiply"])
                    # cubic bezier could also be an option here (1/2 sided)
        return output


class LogicAND(Neuron):
    """returns the values multiplied together"""

    def core(self, inps, settings):
        results = {}
        for into in inps:
            for i in into:
                if i.key in results:
                    if settings["Method"] == "MUL":
                        results[i.key] *= i.val
                    else:  # Method == "MIN"
                        results[i.key] = min(results[i.key], i.val)
                else:
                    inAll = True
                    if settings["IncludeAll"]:
                        for intoB in inps:
                            inAll &= i.key in intoB
                    if inAll:
                        results[i.key] = i.val

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
            total = 1
            for into in inps:
                if settings["Method"] == "MUL":
                    for i in [i.val for i in into]:
                        total *= (1-i)
                else:  # Method == "MAX"
                    total = max(into.values())
            if settings["Method"] == "MUL":
                total = 1 - total
            return total
        else:
            results = {}
            for into in inps:
                for i in into:
                    if i.key in results:
                        if settings["Method"] == "MUL":
                            results[i.key] *= (1-i.val)
                        else:  # Method == "MAX"
                            results[i.key] = min(1-results[i.key], 1-i.val)
                    else:
                        results[i.key] = (1-i.val)
            results.update((k, 1-v) for k, v in results.items())
            return results


class LogicSTRONG(Neuron):
    """Make 1's and 0's stronger"""
    # https://www.desmos.com/calculator/izfhogpchr

    def core(self, inps, settings):
        results = {}
        for into in inps:
            for i in into:
                results[i.key] = i.val**2 * (-2*i.val + 3)
        return results


class LogicWEAK(Neuron):
    """Make 1's and 0's stronger"""
    # https://www.desmos.com/calculator/izfhogpchr

    def core(self, inps, settings):
        results = {}
        for into in inps:
            for i in into:
                results[i.key] = 2*i.val - (i.val**2 * (-2*i.val + 3))
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
                if i.val > settings["Threshold"]:
                    condition = True
                total += i.val
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
                self.brain.agvars[settings["Variable"]] += i.val
                count += 1
        if count:
            self.brain.agvars[settings["Variable"]] /= count
        if settings["Variable"] in self.brain.agvars:
            out = self.brain.agvars[settings["Variable"]]
        else:
            out = 0
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
                    if i.val == self.settings["Value"]:
                        result[i.key] = i.val
        elif self.settings["Operation"] == "NOT EQUAL":
            for into in inps:
                for i in into:
                    if i.val != self.settings["Value"]:
                        result[i.key] = i.val
        elif self.settings["Operation"] == "LESS":
            for into in inps:
                for i in into:
                    if i.val <= self.settings["Value"]:
                        result[i.key] = i.val
        elif self.settings["Operation"] == "GREATER":
            for into in inps:
                for i in into:
                    if i.val > self.settings["Value"]:
                        result[i.key] = i.val
        elif self.settings["Operation"] == "LEAST":
            leastVal = -float("inf")
            leastName = "None"
            for into in inps:
                for i in into:
                    if i.val < leastVal:
                        leastVal = i.val
                        leastName = i.key
            result = {leastName: leastVal}
        elif self.settings["Operation"] == "MOST":
            mostVal = -float("inf")
            mostName = "None"
            for into in inps:
                for i in into:
                    if i.val > mostVal:
                        mostVal = i.val
                        mostName = i.key
            result = {mostName: mostVal}
        elif self.settings["Operation"] == "AVERAGE":
            total = 0
            count = 0
            for into in inps:
                for i in into:
                    total += i.val
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
                    num = i.val
                    li = settings["LowerInput"]
                    ui = settings["UpperInput"]
                    lo = settings["LowerOutput"]
                    uo = settings["UpperOutput"]
                    result[i.key] = ((uo - lo) / (ui - li)) * (num - li) + lo
        return result


class LogicOUTPUT(Neuron):
    """Sets an agents output. (Has to be picked up in cm_agents.Agents)"""

    def core(self, inps, settings):
        val = 0
        if settings["MultiInputType"] == "AVERAGE":
            count = 0
            for into in inps:
                for i in into:
                    val += i.val
                    count += 1
            out = val/(max(1, count))
        elif settings["MultiInputType"] == "MAX":
            out = 0
            for into in inps:
                for i in into:
                    if abs(i.val) > abs(out):
                        out = i.val
        elif settings["MultiInputType"] == "SIZEAVERAGE":
            """Takes a weighed average of the inputs where smaller values have
            less of an impact on the final result"""
            Sm = 0
            SmSquared = 0
            for into in inps:
                for i in into:
                    print("Val:", i.val)
                    Sm += i.val
                    SmSquared += i.val * abs(i.val)  # To retain sign
            # print(Sm, SmSquared)
            if Sm == 0:
                out = 0
            else:
                out = SmSquared / Sm
        elif settings["MultiInputType"] == "SUM":
            out = 0
            for into in inps:
                for i in into:
                    out += i.val
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
                if i.key in priority:
                    # TODO what if priority[i.key] < 0?
                    if i.key in result:
                        contribution = priority[i.key].val * remaining[i.key]
                        result[i.key] += i.val * contribution
                        remaining[i.key] -= contribution
                    else:
                        result[i.key] = i.val * priority[i.key].val
                        remaining[i.key] = 1 - priority[i.key].val
                elif not usesPriority:
                    if i.key in result:
                        contribution = remaining[i.key]
                        result[i.key] += i.val * contribution
                        remaining[i.key] -= 0
                    else:
                        result[i.key] = i.val
                        remaining[i.key] = 0
            #print("resultPartial", result)
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
                            message = settings["Label"] + " >> " + str(i.key) + " " + str(i.val) + "\n"
                            output.write(message)
                    else:
                        print(settings["Label"], ">>", i.key, i.val)
        return 0


class LogicAction(Neuron):
    pass


logictypes = OrderedDict([
    ("InputNode", LogicINPUT),
    ("GraphNode", LogicGRAPH),
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
                strip = tr.strips.new("", currentFrame, action)
                strip.extrapolation = 'NOTHING'
                strip.use_auto_blend = True
            self.length = actionobj.length

            """tr = obj.animation_data.nla_tracks.new()  # NLA track
            action = actionobj.motion
            if action:
                strip = tr.strips.new("", sce.frame_current, action)
                strip.extrapolation = 'HOLD_FORWARD'
                strip.use_auto_blend = False
                strip.blend_type = 'ADD'"""

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
            # print(con, val)
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
    ("ActionState", StateAction)
])
