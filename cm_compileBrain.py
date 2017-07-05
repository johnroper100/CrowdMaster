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


def getInputs(inp, nodeKey):
    result = []
    prefix, nodeGroup, node = nodeKey
    for link in inp.links:
        fr = link.from_node
        if fr.bl_idname == "NodeReroute":
            result += getInputs(fr.inputs[0], nodeKey)
        elif fr.bl_idname == "GroupNode":
            groupPrefix = (prefix, nodeGroup, fr.name)
            group = bpy.data.node_groups[fr.groupName]
            socketName = link.from_socket.name
            for n in group.nodes:
                if n.bl_idname == "GroupOutputs":
                    if socketName in n.inputs:
                        subPrefix = (groupPrefix, fr.groupName, n.name)
                        result += getInputs(n.inputs[socketName], subPrefix)
        elif fr.bl_idname == "GroupInputs":
            parentPrefix, parentNodeGroup, parentNode = prefix
            groupNode = bpy.data.node_groups[parentNodeGroup].nodes[parentNode]
            soc = groupNode.inputs[link.from_socket.name]
            result += getInputs(soc, prefix)
        else:
            result += [(prefix, nodeGroup, fr.name)]
    return result


def getMultiInputs(inputs, nodeKey):
    result = []
    for inp in inputs:
        result += getInputs(inp, nodeKey)
    return result


def getOutputs(out, nodeKey):
    result = []
    prefix, nodeGroup, node = nodeKey
    for link in out.links:
        fr = link.to_node
        if fr.bl_idname == "NodeReroute":
            result += getOutputs(fr.outputs[0], nodeKey)
        elif fr.bl_idname == "GroupNode":
            groupPrefix = (prefix, nodeGroup, fr.name)
            group = bpy.data.node_groups[fr.groupName]
            socketName = link.to_socket.name
            for n in group.nodes:
                if n.bl_idname == "GroupInputs":
                    if socketName in n.outputs:
                        subPrefix = (groupPrefix, fr.groupName, n.name)
                        result += getOutputs(n.outputs[socketName], groupPrefix)
        elif fr.bl_idname == "GroupOutputs":
            parentPrefix, parentNodeGroup, parentNode = prefix
            groupNode = bpy.data.node_groups[parentNodeGroup].nodes[parentNode]
            soc = groupNode.outputs[link.to_socket.name]
            result += getOutputs(soc, prefix)
        else:
            result += [(prefix, nodeGroup, fr.name)]
    return result


def compileNodeGroup(nodeGroup, prefix, brain):
    for node in nodeGroup.nodes:
        nodeKey = (prefix, nodeGroup.name, node.name)
        if node.bl_idname in logictypes:
            item = logictypes[node.bl_idname](brain, node)
            node.getSettings(item)
            if node.bl_idname == "PriorityNode":
                item.inputs = getMultiInputs(node.inputs, nodeKey)
            else:
                item.inputs = getInputs(node.inputs["Input"], nodeKey)
            item.dependantOn = getOutputs(node.outputs["Dependant"], nodeKey)
            if not node.outputs["Output"].is_linked:
                brain.outputs.append(nodeKey)
            brain.neurons[nodeKey] = item
        elif node.bl_idname == "GroupNode":
            compileNodeGroup(bpy.data.node_groups[node.groupName], nodeKey,
                             brain)
        elif node.bl_idname in statetypes:
            item = statetypes[node.bl_idname](brain, node, node.name)
            node.getSettings(item)
            item.outputs = getOutputs(node.outputs["To"], nodeKey)
            if node.bl_idname == "StartState":
                brain.setStartState(node.name)
            else:
                item.valueInputs = getInputs(node.inputs["Value"], nodeKey)
                item.inputs = getInputs(node.inputs["From"], nodeKey)
                if len(item.valueInputs) != 0:
                    brain.outputs.append(nodeKey)
            brain.neurons[nodeKey] = item


def compileBrain(nodeGroup, sim, userid, freezeAnimation):
    """Compile the brain that defines how and agent moves and is animated"""
    result = Brain(sim, userid, freezeAnimation)
    """create the connections from the node"""
    compileNodeGroup(nodeGroup, None, result)
    return result
