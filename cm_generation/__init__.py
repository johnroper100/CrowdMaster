import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from ..libs.ins_vector import Vector

from .cm_templates import templates

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
                genSpaces[tipNode].build(Vector((0, 0, 0)), Vector((0, 0, 0)),
                                                1, {},
                                                context.scene.cm_groups["cm_allAgents"])
        else:
            return {'CANCELLED'}
        return {'FINISHED'}


from . import cm_genNodes

def register():
    bpy.utils.register_class(SCENE_OT_agent_nodes_generate)
    cm_genNodes.register()

def unregister():
    bpy.utils.unregister_class(SCENE_OT_agent_nodes_generate)
    cm_genNodes.unregister()
