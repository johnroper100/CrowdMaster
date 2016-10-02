bl_info = {
    "name": "CrowdMaster",
    "author": "Peter Noble, John Roper, Patrick Crawford",
    "version": (1, 1, 1),
    "blender": (2, 78, 0),
    "location": "Node Editor > CrowdMaster",
    "description": "Blender crowd simulation",
    "warning": "",
    "wiki_url": "http://jmroper.com/crowdmaster/docs/",
    "tracker_url": "https://github.com/johnroper100/CrowdMaster/issues",
    "category": "Simulation"
}

import bpy
import random
import sys
from bpy.props import IntProperty, EnumProperty, CollectionProperty
from bpy.props import PointerProperty, BoolProperty, StringProperty
from bpy.types import PropertyGroup, UIList, Panel, Operator

from . import cm_prefs
from . import icon_load
from . icon_load import register_icons, unregister_icons, cicon
from . import addon_updater_ops
from . cm_graphics import cm_nodeHUD

# =============== GROUPS LIST START ===============#


class SCENE_UL_group(UIList):
    """for drawing each row"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        layout.label(item.name)
        layout.label(str(item.totalAgents) + " | " + item.groupType)
        layout.label("Frozen" if item.freezePlacement else "Unlocked")


class SCENE_UL_agent_type(UIList):
    """for drawing each row"""
    use_filter_sort_alpha = True

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        layout.label(item.name)
        layout.label(str(len(item.agents)))


class SCENE_OT_cm_groups_reset(Operator):
    """Delete a group and all the agent in it (including the agents geo)"""
    bl_idname = "scene.cm_groups_reset"
    bl_label = "Reset Group"

    groupName = StringProperty()

    def execute(self, context):
        group = context.scene.cm_groups.get(self.groupName)
        for obj in bpy.context.selected_objects:
            obj.select = False
        for agentType in group.agentTypes:
            for agent in agentType.agents:
                if group.groupType == "auto":
                    if group.freezePlacement:
                        if agent.name in context.scene.objects:
                            context.scene.objects[agent.name].animation_data_clear()
                    else:
                        if agent.geoGroup in bpy.data.groups:
                            for obj in bpy.data.groups[agent.geoGroup].objects:
                                obj.select = True
                            bpy.data.groups.remove(bpy.data.groups[agent.geoGroup],
                                                   do_unlink=True)
                elif group.groupType == "manual":
                    if agent.name in context.scene.objects:
                        context.scene.objects[agent.name].animation_data_clear()
        if not group.freezePlacement:
            bpy.ops.object.delete(use_global=True)
            groupIndex = context.scene.cm_groups.find(self.groupName)
            context.scene.cm_groups.remove(groupIndex)
        return {'FINISHED'}


# =============== GROUPS LIST END ===============#

# =============== AGENTS LIST START ===============#


class SCENE_OT_cm_agent_add(Operator):
    bl_idname = "scene.cm_agent_add"
    bl_label = "Add single agent to cm agents list"

    agentName = StringProperty()
    brainType = StringProperty()
    groupName = StringProperty()
    geoGroupName = StringProperty()

    def execute(self, context):
        if context.scene.cm_groups.find(self.groupName) == -1:
            newGroup = context.scene.cm_groups.add()
            newGroup.name = self.groupName
            newGroup.groupType = "auto"
        group = context.scene.cm_groups.get(self.groupName)
        if group.groupType == "manual" or group.freezePlacement:
            return {'CANCELLED'}
        ty = group.agentTypes.find(self.brainType)
        if ty == -1:
            at = group.agentTypes.add()
            at.name = self.brainType
            ty = group.agentTypes.find(at.name)
        agentType = group.agentTypes[ty]
        newAgent = agentType.agents.add()
        newAgent.name = self.agentName
        newAgent.geoGroup = self.geoGroupName
        group.totalAgents += 1
        return {'FINISHED'}


class SCENE_OT_cm_agent_add_selected(Operator):
    bl_idname = "scene.cm_agent_add_selected"
    bl_label = "Create Manual Agents"

    groupName = StringProperty(name="New Group Name")
    brainType = StringProperty(name="Brain Type")

    def execute(self, context):
        if self.groupName.strip() == "" or self.brainType.strip() == "":
            return {'CANCELLED'}
        if context.scene.cm_groups.find(self.groupName) == -1:
            newGroup = context.scene.cm_groups.add()
            newGroup.name = self.groupName
            newGroup.groupType = "manual"
        group = context.scene.cm_groups.get(self.groupName)
        if group.groupType == "auto":
            return {'CANCELLED'}
        ty = group.agentTypes.find(self.brainType)
        if ty == -1:
            at = group.agentTypes.add()
            at.name = self.brainType
            ty = group.agentTypes.find(at.name)
        agentType = group.agentTypes[ty]
        for obj in context.selected_objects:
            newAgent = agentType.agents.add()
            newAgent.name = obj.name
            group.totalAgents += 1
        return {'FINISHED'}


# =============== AGENTS LIST END ===============#


# =============== SIMULATION START ===============#


class SCENE_OT_cm_start(Operator):
    bl_idname = "scene.cm_start"
    bl_label = "Start simulation"

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences
        if (bpy.data.is_dirty) and (preferences.ask_to_save):
            self.report({'ERROR'}, "You must save your file first!")
            return {'CANCELLED'}

        context.scene.frame_current = context.scene.frame_start
        global sim
        if "sim" in globals():
            sim.stopFrameHandler()
            del sim
        sim = Simulation()
        sim.actions()

        for group in context.scene.cm_groups:
            sim.createAgents(group)

        sim.startFrameHandler()

        if preferences.play_animation:
            bpy.ops.screen.animation_play()

        return {'FINISHED'}


class SCENE_OT_cm_stop(Operator):
    bl_idname = "scene.cm_stop"
    bl_label = "Stop Simulation"

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences
        if preferences.play_animation:
            bpy.ops.screen.animation_cancel()

        global sim
        if "sim" in globals():
            sim.stopFrameHandler()

        return {'FINISHED'}

# =============== SIMULATION END ===============#

global initialised
initialised = False


class SCENE_PT_CrowdMaster(Panel):
    """Creates CrowdMaster Panel in the node editor."""
    bl_label = "Main"
    bl_idname = "SCENE_PT_CrowdMaster"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "CrowdMaster"

    @classmethod
    def poll(self, context):
        try:
            return bpy.context.space_data.tree_type == 'CrowdMasterTreeType', bpy.context.space_data.tree_type == 'CrowdMasterGenTreeType'
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        preferences = context.user_preferences.addons[__package__].preferences

        row = layout.row()
        row.scale_y = 1.5
        if preferences.use_custom_icons:
            row.operator(SCENE_OT_cm_start.bl_idname, icon_value=cicon('start_sim'))
        else:
            row.operator(SCENE_OT_cm_start.bl_idname, icon='FILE_TICK')

        row = layout.row()
        row.scale_y = 1.25
        if preferences.use_custom_icons:
            row.operator(SCENE_OT_cm_stop.bl_idname, icon_value=cicon('stop_sim'))
        else:
            row.operator(SCENE_OT_cm_stop.bl_idname, icon='CANCEL')

        row = layout.row()
        row.separator()

        row = layout.row()
        if not context.scene.show_utilities:
            row.prop(context.scene, "show_utilities", icon="RIGHTARROW", text="Utilities")
        else:
            row.prop(context.scene, "show_utilities", icon="TRIA_DOWN", text="Utilities")

            #box = layout.box()
            #row = box.row()
            #row.scale_y = 1.5
            #if preferences.use_custom_icons:
                #row.operator("scene.cm_setup_agent", icon_value=cicon('setup'))
            #else:
                #row.operator("scene.cm_setup_agent", icon="MOD_REMESH")

            box = layout.box()
            row = box.row()
            row.scale_y = 1.5
            row.operator("scene.cm_place_deferred_geo", icon="EDITMODE_VEC_HLT")

            box = layout.box()
            row = box.row()
            row.prop(scene, "nodeTreeType")

            row = box.row()
            row.prop(scene, "append_to_tree")

            if scene.append_to_tree:
                row = box.row()
                row.prop_search(scene, "node_tree_name", bpy.data, "node_groups")

            row = box.row()
            row.scale_y = 1.5
            if preferences.use_custom_icons:
                row.operator("scene.cm_setup_sample_nodes", icon_value=cicon('instant_setup'))
            else:
                row.operator("scene.cm_setup_sample_nodes", icon="NODETREE")

            box = layout.box()
            row = box.row()
            row.scale_y = 1.5
            row.operator("scene.cm_convert_to_bound_box", icon="BBOX")

            box = layout.box()
            row = box.row()
            row.label("You must have the Simplify Curves addon enabled and an agent selected.")
            row = box.row()
            row.scale_y = 1.5
            row.operator("graph.simplify", icon="IPO")


class SCENE_PT_CrowdMasterAgents(Panel):
    """Creates CrowdMaster agent panel in the node editor."""
    bl_label = "Agents"
    bl_idname = "SCENE_PT_CrowdMasterAgents"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "CrowdMaster"

    @classmethod
    def poll(self, context):
        try:
            return bpy.context.space_data.tree_type == 'CrowdMasterTreeType', bpy.context.space_data.tree_type == 'CrowdMasterGenTreeType'
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        global initialised
        if not initialised:
            initialised = True
            initialise()
        layout = self.layout
        scene = context.scene
        preferences = context.user_preferences.addons[__package__].preferences

        row = layout.row()
        row.label("Group name")
        row.label("Number | origin")
        row.label("Status")

        layout.template_list("SCENE_UL_group", "", scene,
                             "cm_groups", scene, "cm_groups_index")

        layout.separator()

        if not scene.cm_view_details:
            layout.prop(scene, "cm_view_details", icon='RIGHTARROW')
        else:
            layout.prop(scene, "cm_view_details", icon='TRIA_DOWN')

            box = layout.box()

            index = scene.cm_groups_index
            if index >= 0 and index < len(scene.cm_groups):
                group = scene.cm_groups[index]

                box.template_list("SCENE_UL_agent_type", "", group,
                                  "agentTypes", scene, "cm_view_details_index")

                if group.name == "cm_allAgents":
                    box.label("cm_allAgents: To freeze use AddToGroup node")
                else:
                    box.prop(group, "freezePlacement")

                if preferences.use_custom_icons:
                    op = box.operator(SCENE_OT_cm_groups_reset.bl_idname, icon_value=cicon('reset'))
                else:
                    op = box.operator(SCENE_OT_cm_groups_reset.bl_idname)
                op.groupName = group.name
            else:
                box.label("No group selected")


class SCENE_PT_CrowdMasterManualAgents(Panel):
    """Creates CrowdMaster agent panel in the node editor."""
    bl_label = "Manual Agents"
    bl_idname = "SCENE_PT_CrowdMasterManualAgents"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "CrowdMaster"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        try:
            return bpy.context.space_data.tree_type == 'CrowdMasterTreeType', bpy.context.space_data.tree_type == 'CrowdMasterGenTreeType'
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        preferences = context.user_preferences.addons[__package__].preferences

        layout.prop(context.scene.cm_manual, "groupName")
        layout.prop(context.scene.cm_manual, "brainType")
        if preferences.use_custom_icons:
            op = layout.operator(SCENE_OT_cm_agent_add_selected.bl_idname, icon_value=cicon('agents'))
        else:
            op = layout.operator(SCENE_OT_cm_agent_add_selected.bl_idname)
        op.groupName = "cm_" + context.scene.cm_manual.groupName
        op.brainType = context.scene.cm_manual.brainType


def register():
    # import addon_utils
    # addon_utils.enable("curve_simplify")

    register_icons()
    addon_updater_ops.register(bl_info)
    cm_prefs.register()
    
    cm_nodeHUD.register()

    bpy.utils.register_class(SCENE_UL_group)
    bpy.utils.register_class(SCENE_UL_agent_type)
    bpy.utils.register_class(SCENE_OT_cm_groups_reset)
    bpy.utils.register_class(SCENE_OT_cm_agent_add)
    bpy.utils.register_class(SCENE_OT_cm_agent_add_selected)
    bpy.utils.register_class(SCENE_OT_cm_start)
    bpy.utils.register_class(SCENE_OT_cm_stop)
    bpy.utils.register_class(SCENE_PT_CrowdMaster)
    bpy.utils.register_class(SCENE_PT_CrowdMasterAgents)
    bpy.utils.register_class(SCENE_PT_CrowdMasterManualAgents)

    global action_register
    from .cm_actions import action_register
    global action_unregister
    from .cm_actions import action_unregister

    global event_register
    from .cm_events import event_register
    global event_unregister
    from .cm_events import event_unregister

    from . import cm_blenderData
    cm_blenderData.registerTypes()

    global cm_bpyNodes
    from . import cm_bpyNodes
    cm_bpyNodes.register()

    global cm_generation
    from . import cm_generation
    cm_generation.register()

    global cm_utilities
    from . import cm_utilities
    cm_utilities.register()

    action_register()
    event_register()

    global cm_channels
    from . import cm_channels
    cm_channels.register()


def initialise():
    sce = bpy.context.scene

    global Simulation
    from .cm_simulate import Simulation


def unregister():
    unregister_icons()

    bpy.utils.unregister_class(SCENE_UL_group)
    bpy.utils.unregister_class(SCENE_UL_agent_type)
    bpy.utils.unregister_class(SCENE_OT_cm_groups_reset)
    bpy.utils.unregister_class(SCENE_OT_cm_agent_add)
    bpy.utils.unregister_class(SCENE_OT_cm_agent_add_selected)
    bpy.utils.unregister_class(SCENE_OT_cm_start)
    bpy.utils.unregister_class(SCENE_OT_cm_stop)
    bpy.utils.unregister_class(SCENE_PT_CrowdMaster)
    bpy.utils.unregister_class(SCENE_PT_CrowdMasterAgents)
    bpy.utils.unregister_class(SCENE_PT_CrowdMasterManualAgents)
    
    cm_nodeHUD.unregister()

    action_unregister()
    event_unregister()
    from . import cm_blenderData
    cm_blenderData.unregisterAllTypes()

    addon_updater_ops.unregister()
    cm_bpyNodes.unregister()
    cm_generation.unregister()
    cm_utilities.unregister()
    cm_prefs.unregister()

    cm_channels.unregister()

    if "sim" in globals():
        if sim.frameChangeHighlight in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(sim.frameChangeHighlight)

if __name__ == "__main__":
    register()
