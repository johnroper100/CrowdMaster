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
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty

from . icon_load import cicon

from . cm_graphics . cm_nodeHUD import update_hud_text, update_hud_text2
from . cm_graphics . utils import cm_redrawAll

bpy.types.Scene.show_utilities = BoolProperty(
        name="Show or hide the utilities",
        description="Show/hide the utilities",
        default=False,
        options={'HIDDEN'}
    )

bpy.types.Scene.append_to_tree = BoolProperty(
        name="Append To Tree",
        description="Append the sample nodes to an existing node tree",
        default=False
    )

bpy.types.Scene.node_tree_name = StringProperty(name="Node Tree")

bpy.types.Scene.nodeTreeType = EnumProperty(
        items=[("sim", "Simulation", "Simulation node setups"),
               ("gen", "Generation", "Generation node setups")],
        name="Node Tree Type",
        description="Which node tree setups to show",
        default="gen"
    )


class CrowdMaster_setup_sample_nodes(bpy.types.Operator):
    bl_idname = "scene.cm_setup_sample_nodes"
    bl_label = "Sample Node Setups"

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences

        if preferences.show_node_hud:
            newhudText = "Sample Node Setups Created!"
            update_hud_text(newhudText)
            cm_redrawAll()

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        preferences = context.user_preferences.addons[__package__].preferences

        if scene.nodeTreeType == "gen":
            row = layout.row()
            row.scale_y = 1.15
            if preferences.use_custom_icons:
                row.operator("scene.cm_gennodes_pos_random_simple", icon_value=cicon('shuffle'))
            else:
                row.operator("scene.cm_gennodes_pos_random_simple", icon="FILE_REFRESH")

            row = layout.row()
            row.scale_y = 1.15
            if preferences.use_custom_icons:
                row.operator("scene.cm_gennodes_pos_formation_simple", icon_value=cicon('array'))
            else:
                row.operator("scene.cm_gennodes_pos_formation_simple", icon="MOD_ARRAY")

            row = layout.row()
            row.scale_y = 1.15
            if preferences.use_custom_icons:
                row.operator("scene.cm_gennodes_pos_target_simple", icon_value=cicon('target'))
            else:
                row.operator("scene.cm_gennodes_pos_target_simple", icon="CURSOR")

        elif scene.nodeTreeType == "sim":
            row = layout.row()
            row.scale_y = 1.15
            if preferences.use_custom_icons:
                row.operator("scene.cm_simnodes_mov_simple", icon_value=cicon('motion'))
            else:
                row.operator("scene.cm_simnodes_mov_simple", icon="MOD_OCEAN")

            row = layout.row()
            row.scale_y = 1.15
            if preferences.use_custom_icons:
                row.operator("scene.cm_simnodes_action_random", icon_value=cicon('dice'))
            else:
                row.operator("scene.cm_simnodes_action_random", icon="FILE_REFRESH")


class CrowdMaster_genNodes_pos_random_simple(bpy.types.Operator):
    bl_idname = "scene.cm_gennodes_pos_random_simple"
    bl_label = "Simple Random Positioning"

    def execute(self, context):
        scene = context.scene

        if scene.append_to_tree:
            ng = bpy.data.node_groups[scene.node_tree_name]
        else:
            ng = bpy.data.node_groups.new("SimpleRandomPositioning", "CrowdMasterAGenTreeType")

        object_node = ng.nodes.new("ObjectInputNodeType")
        object_node.location = (-1200, 0)
        object_node.inputObject = "Cube"

        template_node = ng.nodes.new("TemplateNodeType")
        template_node.location = (-800, 0)
        template_node.brainType = "Sample Random"

        rand_node = ng.nodes.new("RandomPositionNodeType")
        rand_node.location = (-400, 0)
        rand_node.noToPlace = 25
        rand_node.radius = 25.00

        gen_node = ng.nodes.new("GenerateNodeType")
        gen_node.location = (0, 0)

        links = ng.links
        links.new(object_node.outputs[0], template_node.inputs[0])
        links.new(template_node.outputs[0], rand_node.inputs[0])
        links.new(rand_node.outputs[0], gen_node.inputs[0])

        return {'FINISHED'}


class CrowdMaster_genNodes_pos_formation_simple(bpy.types.Operator):
    bl_idname = "scene.cm_gennodes_pos_formation_simple"
    bl_label = "Simple Formation Positioning"

    def execute(self, context):
        scene = context.scene

        if scene.append_to_tree:
            ng = bpy.data.node_groups[scene.node_tree_name]
        else:
            ng = bpy.data.node_groups.new("SimpleFormationPositioning", "CrowdMasterAGenTreeType")

        object_node = ng.nodes.new("ObjectInputNodeType")
        object_node.location = (-1200, 0)
        object_node.inputObject = "Cube"

        template_node = ng.nodes.new("TemplateNodeType")
        template_node.location = (-925, 0)
        template_node.brainType = "Sample Formation"

        form_node = ng.nodes.new("FormationPositionNodeType")
        form_node.location = (-550, 0)
        form_node.noToPlace = 25
        form_node.ArrayRows = 5
        form_node.ArrayRowMargin = 5.00
        form_node.ArrayColumnMargin = 5.00

        gen_node = ng.nodes.new("GenerateNodeType")
        gen_node.location = (0, 0)

        links = ng.links
        links.new(object_node.outputs[0], template_node.inputs[0])
        links.new(template_node.outputs[0], form_node.inputs[0])
        links.new(form_node.outputs[0], gen_node.inputs[0])

        return {'FINISHED'}


class CrowdMaster_genNodes_pos_target_simple(bpy.types.Operator):
    bl_idname = "scene.cm_gennodes_pos_target_simple"
    bl_label = "Simple Target Positioning"

    def execute(self, context):
        scene = context.scene

        if scene.append_to_tree:
            ng = bpy.data.node_groups[scene.node_tree_name]
        else:
            ng = bpy.data.node_groups.new("SimpleTargetPositioning", "CrowdMasterAGenTreeType")

        object_node = ng.nodes.new("ObjectInputNodeType")
        object_node.location = (-1050, 0)
        object_node.inputObject = "Cube"

        template_node = ng.nodes.new("TemplateNodeType")
        template_node.location = (-800, 0)
        template_node.brainType = "Sample Target"

        target_node = ng.nodes.new("TargetPositionNodeType")
        target_node.location = (-400, 0)
        target_node.targetType = "vertex"
        target_node.targetObject = "Grid"

        gen_node = ng.nodes.new("GenerateNodeType")
        gen_node.location = (0, 0)

        links = ng.links
        links.new(object_node.outputs[0], template_node.inputs[0])
        links.new(template_node.outputs[0], target_node.inputs[0])
        links.new(target_node.outputs[0], gen_node.inputs[0])

        return {'FINISHED'}


class CrowdMaster_simNodes_mov_simple(bpy.types.Operator):
    bl_idname = "scene.cm_simnodes_mov_simple"
    bl_label = "Simple Movement"

    def execute(self, context):
        scene = context.scene

        if scene.append_to_tree:
            ng = bpy.data.node_groups[scene.node_tree_name]
        else:
            ng = bpy.data.node_groups.new("SimpleMovement", "CrowdMasterTreeType")

        input_node = ng.nodes.new("NewInputNode")
        input_node.location = (-300, 0)
        input_node.InputSource = "CONSTANT"
        input_node.Constant = 0.1

        output_node = ng.nodes.new("OutputNode")
        output_node.location = (0, 0)
        output_node.Output = 'py'

        links = ng.links
        links.new(input_node.outputs[0], output_node.inputs[0])

        return {'FINISHED'}


class CrowdMaster_simNodes_action_random(bpy.types.Operator):
    bl_idname = "scene.cm_simnodes_action_random"
    bl_label = "Random Actions"

    def execute(self, context):
        scene = context.scene

        if scene.append_to_tree:
            ng = bpy.data.node_groups[scene.node_tree_name]
        else:
            ng = bpy.data.node_groups.new("RandomActions", "CrowdMasterTreeType")

        start_node = ng.nodes.new("StartState")
        start_node.location = (-125, -75)

        action1_node = ng.nodes.new("ActionState")
        action1_node.location = (100, 200)
        action1_node.actionName = "action1"
        action1_node.randomInputValue = True

        action2_node = ng.nodes.new("ActionState")
        action2_node.location = (100, 0)
        action2_node.actionName = "action2"
        action2_node.randomInputValue = True

        action3_node = ng.nodes.new("ActionState")
        action3_node.location = (100, -200)
        action3_node.actionName = "action3"
        action3_node.randomInputValue = True

        links = ng.links
        links.new(start_node.outputs[0], action1_node.inputs[0])
        links.new(start_node.outputs[0], action2_node.inputs[0])
        links.new(start_node.outputs[0], action3_node.inputs[0])

        return {'FINISHED'}


class CrowdMaster_convert_to_bound_box(bpy.types.Operator):
    bl_idname = "scene.cm_convert_to_bound_box"
    bl_label = "Convert Selected To Bounding Box"

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences
        
        if preferences.show_node_hud:
            startT = time.time()

        selected = bpy.context.selected_objects
        for obj in selected:
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            bpy.ops.mesh.primitive_cube_add()
            bound_box = bpy.context.active_object

            bound_box.location = obj.location
            bound_box.rotation_euler = obj.rotation_euler
            bound_box.select = True

        if preferences.show_node_hud:
            endT = time.time() - startT

            newhudText = "Done Converting to Bounding Boxes!"
            update_hud_text(newhudText)

            newhudText2 = "Time taken: {} seconds".format(str(endT))
            update_hud_text2(newhudText2)

            cm_redrawAll()

        return {'FINISHED'}


class CrowdMaster_setup_agent(bpy.types.Operator):
    bl_idname = "scene.cm_setup_agent"
    bl_label = "Setup Agent"

    def execute(self, context):

        selected = bpy.context.selected_objects
        for _ in selected:
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        return {'FINISHED'}


class Crowdmaster_place_deferred_geo(bpy.types.Operator):
    bl_idname = "scene.cm_place_deferred_geo"
    bl_label = "Place Deferred Geometry"

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences
        
        if preferences.show_node_hud:
            newhudText = "Placing Deferred Geometry!"
            update_hud_text(newhudText)
            cm_redrawAll()

        groups = bpy.data.groups
        objects = context.scene.objects
        for group in context.scene.cm_groups:
            for agentType in group.agentTypes:
                for agent in agentType.agents:
                    for obj in groups[agent.geoGroup].objects:
                        if preferences.show_node_hud:
                            if preferences.show_sim_data:
                                newhudText = "Placing Object {}".format(obj.name)
                                update_hud_text(newhudText)
                                cm_redrawAll()
                                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                        if "cm_deferObj" in obj:
                            newObj = objects[obj["cm_deferObj"]].copy()
                            newObj.matrix_world = obj.matrix_world
                            for con in obj.constraints:
                                if con.type == "CHILD_OF":
                                    nCon = newObj.constraints.new("CHILD_OF")
                                    nCon.target = con.target
                                    nCon.subtarget = con.subtarget
                                    nCon.inverse_matrix = con.inverse_matrix
                                    newObj.data.update()
                            bpy.context.scene.objects.link(newObj)
                            for user_group in obj.users_group:
                                user_group.objects.link(newObj)
                        elif "cm_deferGroup" in obj:
                            df = obj["cm_deferGroup"]
                            originalGroup = df["group"]
                            aName = df["aName"]

                            newObjs = []
                            gp = list(groups[originalGroup].objects)
                            for groupObj in gp:
                                if groupObj.name != aName:
                                    newObjs.append(groupObj.copy())
                                else:
                                    newObjs.append(context.scene.objects[agent.name])

                            for nObj in newObjs:
                                if nObj.name == agent.name:
                                    continue
                                if nObj.parent in gp:
                                    nObj.parent = newObjs[gp.index(nObj.parent)]

                                groups[agent.geoGroup].objects.link(nObj)
                                bpy.context.scene.objects.link(nObj)
                                if nObj.type == 'MESH' and len(nObj.modifiers) > 0:
                                    for mod in nObj.modifiers:
                                        if mod.type == "ARMATURE":
                                            mod.object = objects[agent.name]

        if preferences.show_node_hud:
            newhudText = "Done Placing Deferred Geometry!"
            update_hud_text(newhudText)
            cm_redrawAll()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CrowdMaster_setup_sample_nodes)
    bpy.utils.register_class(CrowdMaster_genNodes_pos_random_simple)
    bpy.utils.register_class(CrowdMaster_genNodes_pos_formation_simple)
    bpy.utils.register_class(CrowdMaster_genNodes_pos_target_simple)
    bpy.utils.register_class(CrowdMaster_simNodes_mov_simple)
    bpy.utils.register_class(CrowdMaster_simNodes_action_random)
    bpy.utils.register_class(CrowdMaster_convert_to_bound_box)
    bpy.utils.register_class(CrowdMaster_setup_agent)
    bpy.utils.register_class(Crowdmaster_place_deferred_geo)


def unregister():
    bpy.utils.unregister_class(CrowdMaster_setup_sample_nodes)
    bpy.utils.unregister_class(CrowdMaster_genNodes_pos_random_simple)
    bpy.utils.unregister_class(CrowdMaster_genNodes_pos_formation_simple)
    bpy.utils.unregister_class(CrowdMaster_genNodes_pos_target_simple)
    bpy.utils.unregister_class(CrowdMaster_simNodes_mov_simple)
    bpy.utils.unregister_class(CrowdMaster_simNodes_action_random)
    bpy.utils.unregister_class(CrowdMaster_convert_to_bound_box)
    bpy.utils.unregister_class(CrowdMaster_setup_agent)
    bpy.utils.unregister_class(Crowdmaster_place_deferred_geo)

if __name__ == "__main__":
    register()
