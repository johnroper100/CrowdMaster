bl_info = {
    "name": "CrowdMaster",
    "author": "John Roper, Peter Noble, Patrick Crawford",
    "version": (1, 0, 9),
    "blender": (2, 77, 0),
    "location": "Node Editor > CrowdMaster",
    "description": "Blender crowd simulation",
    "warning": "This is still a work in progress. Make sure to save often.",
    "wiki_url": "https://github.com/johnroper100/CrowdMaster/wiki",
    "tracker_url": "https://github.com/johnroper100/CrowdMaster/issues",
    "category": "Simulation"
}

import bpy
import random
from bpy.props import IntProperty, EnumProperty, CollectionProperty
from bpy.props import PointerProperty, BoolProperty, StringProperty
from bpy.types import PropertyGroup, UIList, Panel, Operator

from . import cm_prefs
from . import icon_load
from . icon_load import register_icons, unregister_icons
from .cm_agent_generation import *

from . import addon_updater_ops

# =============== GROUPS LIST START ===============#


class SCENE_UL_group(UIList):
    """for drawing each row"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        layout.label(text=str(item.groupName))
        layout.label(text=str(len(item.agents)))


class SCENE_OT_cm_groups_reset(Operator):
    """Delete a group and all the agent in it (including the agents geo)"""
    bl_idname = "scene.cm_groups_reset"
    bl_label = "Reset group"

    groupName = StringProperty()

    def execute(self, context):
        group = context.scene.cm_groups.get(self.groupName)
        for obj in bpy.context.selected_objects:
            obj.select = False
        for agent in group.agents:
            for obj in bpy.data.groups[agent.geoGroup].objects:
                obj.select = True
            bpy.data.groups.remove(bpy.data.groups[agent.geoGroup])
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
            newGroup.groupName = self.groupName
        group = context.scene.cm_groups.get(self.groupName)
        newAgent = group.agents.add()
        newAgent.objectName = self.agentName
        newAgent.brainType = self.brainType
        newAgent.geoGroup = self.geoGroupName
        return {'FINISHED'}


# =============== AGENTS LIST END ===============#


# =============== SIMULATION START ===============#


class SCENE_OT_cm_start(Operator):
    bl_idname = "scene.cm_start"
    bl_label = "Start simulation"

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences
        if (bpy.data.is_dirty) and (preferences.show_debug_options == False):
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

        if preferences.play_animation == True:
            bpy.ops.screen.animation_play()
        return {'FINISHED'}

class SCENE_OT_cm_stop(Operator):
    bl_idname = "scene.cm_stop"
    bl_label = "Stop Simulation"

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences
        if preferences.play_animation == True:
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
             return bpy.context.space_data.tree_type == 'CrowdMasterTreeType', context.space_data.tree_type == 'CrowdMasterGenTreeType'
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        preferences = context.user_preferences.addons[__package__].preferences

        pcoll = icon_load.icon_collection["main"]
        def cicon(name):
            return pcoll[name].icon_id

        row = layout.row()
        row.scale_y = 1.1
        row.prop(scene, 'use_agent_generation', icon='MOD_ARRAY')

        if scene.use_agent_generation == True:
            box = layout.box()
            row = box.row()
            row.prop_search(scene, "agentGroup", bpy.data, "groups")

            row = box.row()
            row.prop_search(scene, "groundObject", scene, "objects")

            row = box.row()
            if (scene.agentGroup == "") or (scene.groundObject == ""):
                row.enabled = False
            row.scale_y = 1.15
            if preferences.use_custom_icons == True:
                row.operator(CrowdMaster_generate_agents.bl_idname, icon_value=cicon('plus_yellow'))
            else:
                row.operator(CrowdMaster_generate_agents.bl_idname, icon='MOD_ARMATURE')

        row = layout.row()
        row.separator()

        row = layout.row()
        row.scale_y = 1.5
        if preferences.use_custom_icons == True:
            row.operator(SCENE_OT_cm_start.bl_idname, icon_value=cicon('start_sim'))
        else:
            row.operator(SCENE_OT_cm_start.bl_idname, icon='FILE_TICK')

        row = layout.row()
        row.scale_y = 1.25
        if preferences.use_custom_icons == True:
            row.operator(SCENE_OT_cm_stop.bl_idname, icon_value=cicon('stop_sim'))
        else:
            row.operator(SCENE_OT_cm_stop.bl_idname, icon='CANCEL')

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
             return bpy.context.space_data.tree_type == 'CrowdMasterTreeType', context.space_data.tree_type == 'CrowdMasterGenTreeType'
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

        pcoll = icon_load.icon_collection["main"]
        def cicon(name):
            return pcoll[name].icon_id

        row = layout.row()
        row.template_list("SCENE_UL_group", "", scene,
                          "cm_groups", scene, "cm_groups_index")

def register():
    register_icons()
    addon_updater_ops.register(bl_info)
    bpy.utils.register_module(__name__)

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

    action_register()
    event_register()

def initialise():
    sce = bpy.context.scene

    global Simulation
    from .cm_simulate import Simulation

def unregister():
    unregister_icons()
    bpy.utils.unregister_module(__name__)

    action_unregister()
    event_unregister()
    from . import cm_blenderData
    cm_blenderData.unregisterAllTypes()

    addon_updater_ops.unregister()
    cm_bpyNodes.unregister()
    cm_generation.unregister()

if __name__ == "__main__":
    register()
