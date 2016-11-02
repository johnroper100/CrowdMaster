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

import bpy
import time
from bpy.types import Operator
from bpy.props import StringProperty

from .. libs.ins_vector import Vector

from . cm_templates import templates, TemplateRequest
from .. cm_graphics . cm_nodeHUD import update_hud_text, update_hud_text2
from .. cm_graphics . utils import cm_redrawAll


class SCENE_OT_agent_nodes_generate(Operator):
    bl_idname = "scene.cm_agent_nodes_generate"
    bl_label = "Generate Agents"

    nodeName = StringProperty(name="node name")
    nodeTreeName = StringProperty(name="node tree")

    def getInput(self, inp):
        fr = inp.links[0].from_node
        if fr.bl_idname == "NodeReroute":
            return self.getInput(fr.inputs[0])
        else:
            return fr

    def construct(self, current, cache):
        """returns: bool - successfully built, Template"""

        idName = current.bl_idname
        if idName in templates:
            inps = {}
            for i in current.inputs:
                nm = i.name
                if i.is_linked:
                    from_node = self.getInput(i)
                    if from_node in cache:
                        inps[nm] = cache[from_node.name]
                    else:
                        suc, temp = self.construct(from_node, cache)
                        if not suc:
                            return False, None
                        inps[nm] = temp
            tmpt = templates[idName](inps, current.getSettings(), current.name)
            if not tmpt.check():
                current.use_custom_color = True
                current.color = (255, 0, 0)
                return False, None
            if len(current.outputs[0].links) > 1:
                cache[self.name] = tmpt
            current.use_custom_color = False
            return True, tmpt
        else:
            current.use_custom_color = True
            current.color = (255, 0, 0)
            return False, None

    def execute(self, context):
        startT = time.time()
        ntree = bpy.data.node_groups[self.nodeTreeName]
        generateNode = ntree.nodes[self.nodeName]

        cache = {}
        genSpaces = {}
        allSuccess = True

        for space in generateNode.inputs[0].links:
            tipNode = space.from_node
            if tipNode.bl_idname == "NodeReroute":
                tipNode = self.getInput(tipNode.inputs[0])
            suc, temp = self.construct(tipNode, cache)
            if suc:
                genSpaces[tipNode] = temp
            else:
                allSuccess = False

        if allSuccess:
            if "cm_allAgents" in context.scene.cm_groups:
                bpy.ops.scene.cm_groups_reset(groupName="cm_allAgents")
            newGroup = context.scene.cm_groups.add()
            newGroup.groupName = "cm_allAgents"
            newGroup.name = "cm_allAgents"

            for space in generateNode.inputs[0].links:
                tipNode = space.from_node
                if tipNode.bl_idname == "NodeReroute":
                    tipNode = self.getInput(tipNode.inputs[0])
                buildRequest = TemplateRequest()
                genSpaces[tipNode].build(buildRequest)
        else:
            return {'CANCELLED'}

        if allSuccess:
            newhudText = "Agents Generated!"
            update_hud_text(newhudText)

        else:
            newhudText = "Agents Generated With Errors!"
            update_hud_text(newhudText)

        endT = time.time() - startT

        newhudText2 = "Time taken: {} seconds".format(str(endT))
        update_hud_text2(newhudText2)

        cm_redrawAll()

        return {'FINISHED'}


from . import cm_genNodes


def register():
    bpy.utils.register_class(SCENE_OT_agent_nodes_generate)
    cm_genNodes.register()


def unregister():
    bpy.utils.unregister_class(SCENE_OT_agent_nodes_generate)
    cm_genNodes.unregister()
