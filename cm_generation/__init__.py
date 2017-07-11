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

import time

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from . import cm_genNodes
from .cm_templates import TemplateRequest, templates, tmpPathChannel, GeoRequest


def getInput(inp):
    fr = inp.links[0].from_node
    if fr.bl_idname == "NodeReroute":
        return getInput(fr.inputs[0])
    else:
        return fr

def construct(current, cache):
    """returns: bool - successfully built, Template"""
    tmpPathChannel.newframe()

    idName = current.bl_idname
    if idName in templates:
        inps = {}
        for i in current.inputs:
            nm = i.name
            if i.is_linked:
                from_node = getInput(i)
                if from_node in cache:
                    inps[nm] = cache[from_node.name]
                else:
                    suc, temp = construct(from_node, cache)
                    if not suc:
                        return False, None
                    inps[nm] = temp
        tmpt = templates[idName](inps, current.getSettings(), current)
        if not tmpt.check():
            current.use_custom_color = True
            current.color = (255, 0, 0)
            return False, None
        # if len(current.outputs[0].links) > 1:
        #    cache[self.name] = tmpt
        # TODO caching not working
        current.use_custom_color = False
        return True, tmpt
    else:
        current.use_custom_color = True
        current.color = (255, 0, 0)
        return False, None


class SCENE_OT_agent_nodes_generate(Operator):
    bl_idname = "scene.cm_agent_nodes_generate"
    bl_label = "Generate Agents"
    bl_options = {'REGISTER', 'UNDO'}

    nodeName = StringProperty(name="node name")
    nodeTreeName = StringProperty(name="node tree")

    def execute(self, context):
        if bpy.context.active_object is not None:
            bpy.ops.object.mode_set(mode='OBJECT')
        ntree = bpy.data.node_groups[self.nodeTreeName]
        generateNode = ntree.nodes[self.nodeName]
        preferences = context.user_preferences.addons["CrowdMaster"].preferences

        cache = {}
        genSpaces = {}
        allSuccess = True

        for space in generateNode.inputs[0].links:
            tipNode = space.from_node
            if tipNode.bl_idname == "NodeReroute":
                tipNode = self.getInput(tipNode.inputs[0])
            suc, temp = construct(tipNode, cache)
            if suc:
                genSpaces[tipNode] = temp
            else:
                allSuccess = False

        if allSuccess:
            for gpName in [g.name for g in context.scene.cm_groups]:
                bpy.ops.scene.cm_groups_reset(groupName=gpName)

            for space in generateNode.inputs[0].links:
                tipNode = space.from_node
                if tipNode.bl_idname == "NodeReroute":
                    tipNode = getInput(tipNode.inputs[0])
                buildRequest = TemplateRequest()
                genSpaces[tipNode].build(buildRequest)
        else:
            return {'CANCELLED'}

        return {'FINISHED'}


class SCENE_OT_agent_nodes_place_defer_geo(Operator):
    bl_idname = "scene.cm_agent_nodes_place_defer_geo"
    bl_label = "Place defer geo"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for agentGroup in bpy.context.scene.cm_groups:
            for agentType in agentGroup.agentTypes:
                for agent in agentType.agents:
                    obj = bpy.context.scene.objects[agent.name]
                    rig = bpy.context.scene.objects[agent.rigOverwrite]
                    if obj["cm_deferGeo"]:
                        obj["cm_deferGeo"] = False
                        buildRequest = GeoRequest.fromObject(obj)
                        cache = {}
                        suc, temp = construct(buildRequest.bpyNode, cache)
                        if suc:
                            gr = temp.build(buildRequest)
                            for o in bpy.context.selected_objects:
                                o.select = False
                            gr.obj.select = True
                            bpy.context.scene.objects.active = obj
                            bpy.ops.object.make_links_data(type="ANIMATION")
                            gr.obj.select = False

                            if gr.overwriteRig.proxy is None:
                                gr.overwriteRig.select = True
                                bpy.context.scene.objects.active = rig
                                bpy.ops.object.make_links_data(type="ANIMATION")
                            else:
                                bpy.context.scene.objects.active = rig
                                if rig.animation_data is None:
                                    rig.animation_data_create()
                                if rig.animation_data.action is None:
                                    action = bpy.data.actions.new(name=rig.name+".Action")
                                    rig.animation_data.action = action
                                else:
                                    action = rig.animation_data.action
                                if gr.overwriteRig.animation_data is None:
                                    gr.overwriteRig.animation_data_create()

                                gr.overwriteRig.animation_data.action = action
                        else:
                            return {'CANCELLED'}
        # For rig update
        bpy.context.scene.frame_current = bpy.context.scene.frame_current
        return {'FINISHED'}


class SCENE_OT_agent_nodes_remove_defer_geo(Operator):
    bl_idname = "scene.cm_agent_nodes_remove_defer_geo"
    bl_label = "Remove defer geo"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for agentGroup in bpy.context.scene.cm_groups:
            for agentType in agentGroup.agentTypes:
                for agent in agentType.agents:
                    obj = bpy.context.scene.objects[agent.name]
                    rig = bpy.context.scene.objects[agent.rigOverwrite]
                    if not obj["cm_deferGeo"]:
                        obj["cm_deferGeo"] = True

                        geoGroup = bpy.data.groups[agent.geoGroup]
                        for obj in list(geoGroup.objects):
                            if obj.name != agent.name:
                                if obj.name != agent.rigOverwrite:
                                    bpy.data.objects.remove(obj,
                                                            do_unlink=True)
                        else:
                            return {'CANCELLED'}
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SCENE_OT_agent_nodes_generate)
    bpy.utils.register_class(SCENE_OT_agent_nodes_place_defer_geo)
    bpy.utils.register_class(SCENE_OT_agent_nodes_remove_defer_geo)
    cm_genNodes.register()


def unregister():
    bpy.utils.unregister_class(SCENE_OT_agent_nodes_generate)
    bpy.utils.unregister_class(SCENE_OT_agent_nodes_place_defer_geo)
    bpy.utils.unregister_class(SCENE_OT_agent_nodes_remove_defer_geo)
    cm_genNodes.unregister()
