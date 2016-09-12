import bpy
import os
from bpy.types import Panel, Operator
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty

from . import icon_load
from . icon_load import cicon

bpy.types.Scene.show_utilities = BoolProperty(
        name="Show or hide the utilities",
        description="Show/hide the utilities",
        default=False,
        options={'HIDDEN'}
    )

bpy.types.Scene.nodeTreeType = EnumProperty(
        items = [("sim", "Simulation", "Simulation node setups"),
                 ("gen", "Generation", "Generation node setups")],
        name = "Node Tree Type",
        description = "Which node tree setups to show",
        default = "gen"
    )

class CrowdMaster_setup_sample_nodes(bpy.types.Operator):
    bl_idname = "scene.cm_setup_sample_nodes"
    bl_label = "Sample Node Setups"

    def execute(self, context):
        scene = context.scene

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600)

    def check(self, context):
        scene = context.scene

    def draw(self, context):
        layout = self.layout
        scene = context.scene
<<<<<<< HEAD
        preferences = context.user_preferences.addons[__package__].preferences
        
        if scene.nodeTreeType == "gen":
            row = layout.row()
            if preferences.use_custom_icons == True:
                row.operator("scene.cm_gennodes_pos_random_simple", icon_value=cicon('shuffle'))
            else:
                row.operator("scene.cm_gennodes_pos_random_simple", icon="FILE_REFRESH")
            
            row = layout.row()
            if preferences.use_custom_icons == True:
                row.operator("scene.cm_gennodes_pos_formation_simple", icon_value=cicon('array'))
            else:
                row.operator("scene.cm_gennodes_pos_formation_simple", icon="MOD_ARRAY")
            
=======

        if scene.nodeTreeType == "gen":
            row = layout.row()
            row.operator("scene.cm_gennodes_pos_random_simple", icon_value=cicon('shuffle'))

            row = layout.row()
            row.operator("scene.cm_gennodes_pos_formation_simple", icon_value=cicon('array'))

>>>>>>> defer_geo
            row = layout.row()
            if preferences.use_custom_icons == True:
                row.operator("scene.cm_gennodes_pos_target_simple", icon_value=cicon('target'))
            else:
                row.operator("scene.cm_gennodes_pos_target_simple", icon="CURSOR")

        elif scene.nodeTreeType == "sim":
            row = layout.row()
            row.label("Sample simulation node setups: TODO")

class CrowdMaster_genNodes_pos_random_simple(bpy.types.Operator):
    bl_idname = "scene.cm_gennodes_pos_random_simple"
    bl_label = "Simple Random Positioning"

    def execute(self, context):
        scene = context.scene

        ng = bpy.data.node_groups.new("SimpleRandomPositioning", "CrowdMasterAGenTreeType")

        object_node = ng.nodes.new("ObjectInputNodeType")
        object_node.location = (-600, 0)
        object_node.inputObject = "Cone"

        template_node = ng.nodes.new("TemplateNodeType")
        template_node.location = (-400, 0)
        template_node.brainType = "Sample Random"

        rand_node = ng.nodes.new("RandomPositionNodeType")
        rand_node.location = (-200, 0)
        rand_node.noToPlace = 25
        rand_node.radius = 25.00

        gen_node = ng.nodes.new("GenerateNodeType")
        gen_node.location = (0, 0)

        links = ng.links
        link = links.new(object_node.outputs[0], template_node.inputs[0])
        link = links.new(template_node.outputs[0], rand_node.inputs[0])
        link = links.new(rand_node.outputs[0], gen_node.inputs[0])

        return {'FINISHED'}

class CrowdMaster_genNodes_pos_formation_simple(bpy.types.Operator):
    bl_idname = "scene.cm_gennodes_pos_formation_simple"
    bl_label = "Simple Formation Positioning"

    def execute(self, context):
        scene = context.scene

        ng = bpy.data.node_groups.new("SimpleFormationPositioning", "CrowdMasterAGenTreeType")

        object_node = ng.nodes.new("ObjectInputNodeType")
        object_node.location = (-600, 0)
        object_node.inputObject = "Cone"

        template_node = ng.nodes.new("TemplateNodeType")
        template_node.location = (-400, 0)
        template_node.brainType = "Sample Formation"

        form_node = ng.nodes.new("FormationPositionNodeType")
        form_node.location = (-200, 0)
        form_node.noToPlace = 25
        form_node.ArrayRows = 5
        form_node.ArrayRowMargin = 5.00
        form_node.ArrayColumnMargin = 5.00

        gen_node = ng.nodes.new("GenerateNodeType")
        gen_node.location = (0, 0)

        links = ng.links
        link = links.new(object_node.outputs[0], template_node.inputs[0])
        link = links.new(template_node.outputs[0], form_node.inputs[0])
        link = links.new(form_node.outputs[0], gen_node.inputs[0])

        return {'FINISHED'}

class CrowdMaster_genNodes_pos_target_simple(bpy.types.Operator):
    bl_idname = "scene.cm_gennodes_pos_target_simple"
    bl_label = "Simple Target Positioning"

    def execute(self, context):
        scene = context.scene

        ng = bpy.data.node_groups.new("SimpleTargetPositioning", "CrowdMasterAGenTreeType")

        object_node = ng.nodes.new("ObjectInputNodeType")
        object_node.location = (-600, 0)
        object_node.inputObject = "Cone"

        template_node = ng.nodes.new("TemplateNodeType")
        template_node.location = (-400, 0)
        template_node.brainType = "Sample Target"

        target_node = ng.nodes.new("TargetPositionNodeType")
        target_node.location = (-200, 0)
        target_node.targetType = "vertex"
        target_node.targetObject = "Grid"

        gen_node = ng.nodes.new("GenerateNodeType")
        gen_node.location = (0, 0)

        links = ng.links
        link = links.new(object_node.outputs[0], template_node.inputs[0])
        link = links.new(template_node.outputs[0], target_node.inputs[0])
        link = links.new(target_node.outputs[0], gen_node.inputs[0])

        return {'FINISHED'}

class CrowdMaster_convert_to_bound_box(bpy.types.Operator):
    bl_idname = "scene.cm_convert_to_bound_box"
    bl_label = "Convert Selected To Bounding Box"

    def execute(self, context):
        scene = context.scene

        selected = bpy.context.selected_objects
        for obj in selected:
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            bpy.ops.mesh.primitive_cube_add()
            bound_box = bpy.context.active_object

            bound_box.location = obj.location
            bound_box.rotation_euler = obj.rotation_euler
            bound_box.select = True

        return {'FINISHED'}

class Crowdmaster_place_deferred_geo(bpy.types.Operator):
    bl_idname = "scene.cm_place_deferred_geo"
    bl_label = "Place geo that was deferred"

    def execute(self, context):
        groups = bpy.data.groups
        objects = context.scene.objects
        for group in context.scene.cm_groups:
            for agentType in group.agentTypes:
                for agent in agentType.agents:
                    for obj in groups[agent.geoGroup].objects:
                        if "cm_deferObj" in obj:
                            newObj = objects[obj["cm_deferObj"]].copy()
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
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CrowdMaster_setup_sample_nodes)
    bpy.utils.register_class(CrowdMaster_convert_to_bound_box)
    bpy.utils.register_class(CrowdMaster_genNodes_pos_random_simple)
    bpy.utils.register_class(CrowdMaster_genNodes_pos_formation_simple)
    bpy.utils.register_class(CrowdMaster_genNodes_pos_target_simple)
    bpy.utils.register_class(Crowdmaster_place_deferred_geo)

def unregister():
    bpy.utils.unregister_class(CrowdMaster_setup_sample_nodes)
    bpy.utils.unregister_class(CrowdMaster_convert_to_bound_box)
    bpy.utils.unregister_class(CrowdMaster_genNodes_pos_random_simple)
    bpy.utils.unregister_class(CrowdMaster_genNodes_pos_formation_simple)
    bpy.utils.unregister_class(CrowdMaster_genNodes_pos_target_simple)
    bpy.utils.unregister_class(Crowdmaster_place_deferred_geo)

if __name__ == "__main__":
    register()
