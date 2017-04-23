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
from .libs import cm_accelerate

preferences = bpy.context.user_preferences.addons[__package__].preferences
if preferences.show_debug_options:
    print("IMPORTED cm_nodeFunctions")


def compileBrain(nodeGroup, sim, userid):
    """Compile the brain that defines how and agent moves and is animated"""
    result = Brain(sim, userid)
    preferences = bpy.context.user_preferences.addons[__package__].preferences
    """create the connections from the node"""
    for node in nodeGroup.nodes:
        if node.bl_idname in logictypes:
            # node.name  -  The identifier
            # node.bl_idname  -  The type
            item = logictypes[node.bl_idname](result, node)
            node.getSettings(item)
            if node.bl_idname == "PriorityNode":
                item.inputs = cm_accelerate.getMultiInputs(node.inputs)
            else:
                item.inputs = cm_accelerate.getInputs(node.inputs["Input"])
            item.dependantOn = cm_accelerate.getOutputs(node.outputs["Dependant"])
            if not node.outputs["Output"].is_linked:
                result.outputs.append(node.name)
            result.neurons[node.name] = item
        elif node.bl_idname in statetypes:
            item = statetypes[node.bl_idname](result, node, node.name)
            node.getSettings(item)
            item.outputs = cm_accelerate.getOutputs(node.outputs["To"])
            if preferences.show_debug_options:
                print(node.name, "outputs", item.outputs)
            if node.bl_idname == "StartState":
                result.setStartState(node.name)
            else:
                item.valueInputs = cm_accelerate.getInputs(node.inputs["Value"])
                item.inputs = cm_accelerate.getInputs(node.inputs["From"])
                if len(item.valueInputs) != 0:
                    result.outputs.append(node.name)
            result.neurons[node.name] = item
    return result
