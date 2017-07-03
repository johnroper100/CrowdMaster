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

import bpy

from .cm_brainClasses import Brain
from .cm_nodeFunctions import logictypes, statetypes

preferences = bpy.context.user_preferences.addons[__package__].preferences


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


def compileBrain(nodeGroup, sim, userid, freezeAnimation):
    """Compile the brain that defines how and agent moves and is animated"""
    result = Brain(sim, userid, freezeAnimation)
    preferences = bpy.context.user_preferences.addons[__package__].preferences
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
            if node.bl_idname == "StartState":
                result.setStartState(node.name)
            else:
                item.valueInputs = getInputs(node.inputs["Value"])
                item.inputs = getInputs(node.inputs["From"])
                if len(item.valueInputs) != 0:
                    result.outputs.append(node.name)
            result.neurons[node.name] = item
    return result
