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

bl_info = {
    "name": "CrowdMaster",
    "author": "Peter Noble, John Roper, Jake Dube, Patrick Crawford",
    "version": (1, 3, 2),
    "blender": (2, 78, 0),
    "location": "Node Editor > CrowdMaster Node Trees",
    "description": "Crowd Simulation for the Masses",
    "warning": "",
    "wiki_url": "http://crowdmaster.org/docs/",
    "tracker_url": "https://github.com/johnroper100/CrowdMaster/issues",
    "category": "Simulation"
}

import logging
import time
from . import cm_timings

import bpy
from bpy.props import CollectionProperty, StringProperty
from bpy.types import Operator, Panel, UIList

from . import addon_updater_ops, cm_prefs
from .cm_blenderData import initialTagProperty, modifyBoneProperty
from .cm_iconLoad import cicon, register_icons, unregister_icons

# =============== GROUPS LIST START ===============#

logger = logging.getLogger("CrowdMaster")


class SCENE_UL_group(UIList):
    """for drawing each row"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        # layout.label(item.name)
        op = layout.operator(SCENE_OT_CrowdMasterSelectGroup.bl_idname,
                             text=item.name)
        op.groupName = item.name
        layout.label(str(item.totalAgents) + " | " + item.groupType)
        if item.freezePlacement:
            if item.freezeAnimation:
                label = "Anim frozen"
            else:
                label = "Geo frozen"
        else:
            label = "Unlocked"
        layout.label(label)


class SCENE_UL_agent_type(UIList):
    """for drawing each row"""
    use_filter_sort_alpha = True

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        layout.label(item.name)
        layout.label(str(len(item.agents)))


class SCENE_OT_cm_groups_reset(Operator):
    """Delete the selected group and all the agents in it (including the agent's geometry)."""
    bl_idname = "scene.cm_groups_reset"
    bl_label = "Reset Group"

    groupName = StringProperty()

    def execute(self, context):
        context.scene.frame_set(context.scene.cm_sim_start_frame)
        bpy.ops.scene.cm_stop()

        if bpy.context.active_object is not None:
            bpy.ops.object.mode_set(mode='OBJECT')
        scene = context.scene
        preferences = context.user_preferences.addons[__package__].preferences

        group = scene.cm_groups.get(self.groupName)
        for obj in bpy.context.selected_objects:
            obj.select = False
        for agentType in group.agentTypes:
            for agent in agentType.agents:
                if group.groupType == "auto":
                    if group.freezePlacement:
                        if not group.freezeAnimation:
                            if agent.name in scene.objects:
                                scene.objects[agent.name].animation_data_clear()
                    else:
                        if agent.geoGroup in bpy.data.groups:
                            for obj in bpy.data.groups[agent.geoGroup].objects:
                                obj.select = True
                            bpy.data.groups.remove(bpy.data.groups[agent.geoGroup],
                                                   do_unlink=True)
                elif group.groupType == "manual":
                    if not group.freezeAnimation:
                        if agent.name in scene.objects:
                            scene.objects[agent.name].animation_data_clear()
        if not group.freezePlacement and group.groupType == "auto":
            bpy.ops.object.delete(use_global=True)
            groupIndex = scene.cm_groups.find(self.groupName)
            scene.cm_groups.remove(groupIndex)

        return {'FINISHED'}


# =============== GROUPS LIST END ===============#

# =============== AGENTS LIST START ===============#


class SCENE_OT_cm_agent_add(Operator):
    """Add a single agent to the list of agents in the current group."""
    bl_idname = "scene.cm_agent_add"
    bl_label = "Add single agent to CM agents list"

    agentName = StringProperty()
    brainType = StringProperty()
    groupName = StringProperty()
    geoGroupName = StringProperty()
    initialTags = CollectionProperty(type=initialTagProperty)
    rigOverwrite = StringProperty()
    constrainBone = StringProperty()
    modifyBones = CollectionProperty(type=modifyBoneProperty)

    @staticmethod
    def _execute(context, agentName, brainType, groupName, geoGroupName,
                 initialTags, rigOverwrite, constrainBone, modifyBones):
        t = time.time()
        scene = context.scene

        if scene.cm_groups.find(groupName) == -1:
            newGroup = scene.cm_groups.add()
            newGroup.name = groupName
            newGroup.groupType = "auto"
        group = scene.cm_groups.get(groupName)
        if group.groupType == "manual" or group.freezePlacement:
            return {'CANCELLED'}
        ty = group.agentTypes.find(brainType)
        if ty == -1:
            at = group.agentTypes.add()
            at.name = brainType
            ty = group.agentTypes.find(at.name)
        agentType = group.agentTypes[ty]
        newAgent = agentType.agents.add()
        newAgent.name = agentName
        newAgent.geoGroup = geoGroupName
        newAgent.rigOverwrite = rigOverwrite
        newAgent.constrainBone = constrainBone
        for x in initialTags:
            tag = newAgent.initialTags.add()
            tag.name = x["name"]
            tag.value = x["value"]
        for x in modifyBones:
            modify = newAgent.modifyBones.add()
            modify.name = x["name"]
            modify.tag = x["tag"]
            modify.attribute = x["attribute"]
        group.totalAgents += 1

        cm_timings.placement["cm_agent_add"] += time.time() - t
        cm_timings.placementNum["cm_agent_add"] += 1
        return {'FINISHED'}

    def execute(self, context):
        return self._execute(context, self.agentName, self.brainType,
                             self.groupName, self.geoGroupName,
                             self.initialTags, self.rigOverwrite,
                             self.constrainBone, self.modifyBones)


class SCENE_OT_cm_agent_add_selected(Operator):
    """Generate an agent group manually from the selected objects."""
    bl_idname = "scene.cm_agent_add_selected"
    bl_label = "Create Manual Agents"

    groupName = StringProperty(name="New Group Name")
    brainType = StringProperty(name="Brain Type")

    def execute(self, context):
        scene = context.scene
        preferences = context.user_preferences.addons[__package__].preferences

        if self.groupName.strip() == "" or self.brainType.strip() == "":
            return {'CANCELLED'}
        if scene.cm_groups.find(self.groupName) == -1:
            newGroup = scene.cm_groups.add()
            newGroup.name = self.groupName
            newGroup.groupType = "manual"
        group = scene.cm_groups.get(self.groupName)
        if group.groupType == "auto":
            return {'CANCELLED'}
        ty = group.agentTypes.find(self.brainType)
        if ty == -1:
            at = group.agentTypes.add()
            at.name = self.brainType
            ty = group.agentTypes.find(at.name)
        agentType = group.agentTypes[ty]

        if not self.groupName in bpy.data.groups:
            bpy.ops.group.create(name=self.groupName)
        for obj in context.selected_objects:
            bpy.context.scene.objects[obj.name].select = True
            bpy.ops.object.group_link(group=self.groupName)
            bpy.context.scene.objects[obj.name].select = False

            inGroup = agentType.agents.find(obj.name)
            if inGroup == -1:
                newAgent = agentType.agents.add()
                newAgent.name = obj.name
                newAgent.geoGroup = self.groupName
                group.totalAgents += 1

        return {'FINISHED'}


# =============== AGENTS LIST END ===============#


# =============== SIMULATION START ===============#

customSyncMode = 'NONE'  # This saves the sync_mode value
customOutline = True  # This saves the outline value
customRLines = True  # This saves the relationship lines value


class SCENE_OT_cm_start(Operator):
    """Start to simulate the CrowdMaster agents."""
    bl_idname = "scene.cm_start"
    bl_label = "Start Simulation"

    def execute(self, context):
        scene = context.scene
        global customSyncMode
        global customOutline
        global customRLines

        preferences = context.user_preferences.addons[__package__].preferences
        if (preferences.ask_to_save) and (bpy.data.is_dirty):
            self.report({'ERROR'}, "You must save your file first!")
            return {'CANCELLED'}

        customSyncMode = scene.sync_mode
        bpy.context.scene.sync_mode = 'NONE'

        if bpy.context.screen is not None:
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    customOutline = area.spaces[0].show_outline_selected
                    customRLines = area.spaces[0].show_relationship_lines
                    area.spaces[0].show_outline_selected = False
                    area.spaces[0].show_relationship_lines = False

        scene.frame_current = scene.cm_sim_start_frame

        global sim
        if "sim" in globals():
            sim.stopFrameHandler()
            del sim
        sim = Simulation()
        sim.setupActions()

        for group in scene.cm_groups:
            sim.createAgents(group)

        sim.startFrameHandler()

        if preferences.play_animation:
            bpy.ops.screen.animation_play()

        return {'FINISHED'}


class SCENE_OT_cm_stop(Operator):
    """Stop simulating the CrowdMaster agents."""
    bl_idname = "scene.cm_stop"
    bl_label = "Stop Simulation"

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences
        global customSyncMode
        global customOutline
        global customRLines

        if preferences.play_animation:
            bpy.ops.screen.animation_cancel()

        global sim
        if "sim" in globals():
            sim.stopFrameHandler()

        bpy.context.scene.sync_mode = customSyncMode
        if bpy.context.screen is not None:
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.spaces[0].show_outline_selected = customOutline
                    area.spaces[0].show_relationship_lines = customRLines

        return {'FINISHED'}

# =============== SIMULATION END ===============#


class SCENE_PT_CrowdMaster(Panel):
    """Creates CrowdMaster main panel in the node editor."""
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
            row.operator(SCENE_OT_cm_start.bl_idname,
                         icon_value=cicon('start_sim'))
        else:
            row.operator(SCENE_OT_cm_start.bl_idname, icon='FILE_TICK')

        row = layout.row()
        row.scale_y = 1.25
        if preferences.use_custom_icons:
            row.operator(SCENE_OT_cm_stop.bl_idname,
                         icon_value=cicon('stop_sim'))
        else:
            row.operator(SCENE_OT_cm_stop.bl_idname, icon='CANCEL')

        row = layout.row(align=True)
        row.prop(scene, "cm_sim_start_frame")
        row.prop(scene, "cm_sim_end_frame")

        row = layout.row()
        row.separator()

        row = layout.row()
        if not scene.show_utilities:
            row.prop(scene, "show_utilities",
                     icon="RIGHTARROW", text="Utilities")
        else:
            row.prop(scene, "show_utilities",
                     icon="TRIA_DOWN", text="Utilities")

            box = layout.box()
            row = box.row()
            row.scale_y = 1.5
            row.operator("scene.cm_place_deferred_geo", icon="EDITMODE_HLT")

            box = layout.box()
            row = box.row()
            row.prop(scene, "cm_switch_dupli_group_suffix")
            row = box.row()
            row.prop(scene, "cm_switch_dupli_group_target")
            row = box.row()
            row.scale_y = 1.5
            row.operator("scene.cm_switch_dupli_groups", icon="GROUP_VERTEX")


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
        layout = self.layout
        scene = context.scene
        preferences = context.user_preferences.addons[__package__].preferences

        row = layout.row()
        row.label("Group Name")
        row.label("Number | Origin")
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
            if 0 <= index < len(scene.cm_groups):
                group = scene.cm_groups[index]

                box.template_list("SCENE_UL_agent_type", "", group,
                                  "agentTypes", scene, "cm_view_details_index")

                if group.name == "cm":
                    box.label("cm: To freeze use add to group")
                else:
                    if group.groupType == "auto":
                        box.prop(group, "freezePlacement")
                        if group.freezePlacement:
                            box.prop(group, "freezeAnimation")
                    else:
                        box.prop(group, "freezeAnimation")
                if preferences.use_custom_icons:
                    op = box.operator(
                        SCENE_OT_cm_groups_reset.bl_idname, icon_value=cicon('reset'))
                else:
                    op = box.operator(SCENE_OT_cm_groups_reset.bl_idname)
                op.groupName = group.name
            else:
                box.label("No group selected")


class SCENE_OT_CrowdMasterSelectGroup(Operator):
    """Select only the objects that are part of an agent"""
    bl_idname = "scene.cm_groups_select"
    bl_label = "Select Group"

    groupName = StringProperty()

    @classmethod
    def poll(cls, context):
        return bpy.context.object is None or bpy.context.object.mode == "OBJECT"

    def invoke(self, context, event):
        scene = context.scene
        group = scene.cm_groups.get(self.groupName)

        allSelected = True

        for gtype in group.agentTypes:
            for agent in gtype.agents:
                agGroup = bpy.data.groups[agent.geoGroup]
                for obj in agGroup.objects:
                    allSelected &= obj.select

        if not event.shift:
            for obj in bpy.context.selected_objects:
                if obj.select:
                    obj.select = False

        setTo = not allSelected

        for gtype in group.agentTypes:
            for agent in gtype.agents:
                agGroup = bpy.data.groups[agent.geoGroup]
                for obj in agGroup.objects:
                    obj.select = setTo

        return {"FINISHED"}


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
        scene = context.scene
        preferences = context.user_preferences.addons[__package__].preferences

        layout.prop(scene.cm_manual, "groupName", text="Group Name")
        layout.prop(scene.cm_manual, "brainType", text="Brain Type")
        if preferences.use_custom_icons:
            op = layout.operator(
                SCENE_OT_cm_agent_add_selected.bl_idname, icon_value=cicon('agents'))
        else:
            op = layout.operator(SCENE_OT_cm_agent_add_selected.bl_idname)
        op.groupName = "cm_" + scene.cm_manual.groupName
        op.brainType = scene.cm_manual.brainType


@bpy.app.handlers.persistent
def nodeTreeSetFakeUser(scene):
    for grp in bpy.data.node_groups:
        if grp.bl_idname in ["CrowdMasterAGenTreeType", "CrowdMasterTreeType"]:
            if not grp.savedOnce:
                grp.savedOnce = True
                grp.use_fake_user = True


def register():
    global cm_documentation
    from . import cm_documentation
    cm_documentation.register()

    global cm_translations
    from . import cm_translations
    cm_translations.register()

    register_icons()

    addon_updater_ops.register(bl_info)
    cm_prefs.register()

    from . import cm_blenderData
    cm_blenderData.registerTypes()

    bpy.utils.register_class(SCENE_UL_group)
    bpy.utils.register_class(SCENE_UL_agent_type)
    bpy.utils.register_class(SCENE_OT_cm_groups_reset)
    bpy.utils.register_class(SCENE_OT_cm_agent_add)
    bpy.utils.register_class(SCENE_OT_cm_agent_add_selected)
    bpy.utils.register_class(SCENE_OT_cm_start)
    bpy.utils.register_class(SCENE_OT_cm_stop)
    bpy.utils.register_class(SCENE_PT_CrowdMaster)
    bpy.utils.register_class(SCENE_PT_CrowdMasterAgents)
    bpy.utils.register_class(SCENE_OT_CrowdMasterSelectGroup)
    bpy.utils.register_class(SCENE_PT_CrowdMasterManualAgents)

    global Simulation
    from .cm_simulate import Simulation

    global action_register
    from .cm_actions import action_register
    global action_unregister
    from .cm_actions import action_unregister

    global event_register
    from .cm_events import event_register
    global event_unregister
    from .cm_events import event_unregister

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

    global cm_tests
    from . import cm_tests
    cm_tests.register()

    global cm_pieMenus
    from . import cm_pieMenus
    cm_pieMenus.register()

    if nodeTreeSetFakeUser not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(nodeTreeSetFakeUser)

    preferences = bpy.context.user_preferences.addons[__package__].preferences
    if preferences.show_debug_options:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')


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
    bpy.utils.unregister_class(SCENE_OT_CrowdMasterSelectGroup)
    bpy.utils.unregister_class(SCENE_PT_CrowdMasterManualAgents)

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

    cm_tests.unregister()

    cm_pieMenus.unregister()

    if "sim" in globals():
        if sim.frameChangeHighlight in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(sim.frameChangeHighlight)

    cm_documentation.unregister()
    cm_translations.unregister()

    if nodeTreeSetFakeUser in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(nodeTreeSetFakeUser)


if __name__ == "__main__":
    register()
