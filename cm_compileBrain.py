import bpy

from .cm_nodeFunctions import logictypes, statetypes
from collections import OrderedDict
from .cm_brainClasses import Neuron, Brain, State
import functools


def getInputs(inp):
    result = []
    for link in inp.links:
        fr = link.from_node
        if fr.bl_idname == "NodeReroute":
            result += getInputs(fr.inputs[0])
        else:
            result += [fr.name]
    return result


def getMultiInputs(inputs):
    result = []
    for inp in inputs:
        for link in inp.links:
            fr = link.from_node
            if fr.bl_idname == "NodeReroute":
                result += getInputs(fr.inputs[0])
            else:
                result += [fr.name]
    return result


def getOutputs(out):
    result = []
    for link in out.links:
        fr = link.to_node
        if fr.bl_idname == "NodeReroute":
            result += getOutputs(fr.outputs[0])
        else:
            result += [fr.name]
    return result


def compileBrain(nodeGroup, sim, userid):
    """Compile the brain that defines how and agent moves and is animated"""
    result = Brain(sim, userid)
    """create the connections from the node"""
    for node in nodeGroup.nodes:
        if node.bl_idname in logictypes:
            # node.name  -  The identifier
            # node.bl_idname  -  The type
            item = logictypes[node.bl_idname](result, node)
            node.getSettings(item)
            if node.bl_idname == "PriorityNode":
                item.inputs = getMultiInputs(node.inputs)
            else:
                item.inputs = getInputs(node.inputs["Input"])
            item.dependantOn = getOutputs(node.outputs["Dependant"])
            if not node.outputs["Output"].is_linked:
                result.outputs.append(node.name)
            result.neurons[node.name] = item
        elif node.bl_idname in statetypes:
            item = statetypes[node.bl_idname](result, node, node.name)
            node.getSettings(item)
            item.outputs = getOutputs(node.outputs["To"])
            print(node.name, "outputs", item.outputs)
            if node.bl_idname == "StartState":
                result.setStartState(node.name)
            else:
                item.valueInputs = getInputs(node.inputs["Value"])
                if len(item.valueInputs) != 0:
                    result.outputs.append(node.name)
            result.neurons[node.name] = item
    return result
