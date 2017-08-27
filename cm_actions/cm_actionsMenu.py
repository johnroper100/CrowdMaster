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
from bpy.props import (CollectionProperty, EnumProperty, IntProperty,
                       PointerProperty, StringProperty)
from bpy.types import Operator, Panel, PropertyGroup, UIList


def updateGroups(self, context):
    """update context.scene.cm_action_groups with any new actions"""
    newGroups = []
    for action in context.scene.cm_actions.coll:
        if action.name != "" and action.name not in newGroups:
            newGroups.append(action.name)
        groups = [g.strip() for g in action.groups.split(",")]
        for g in groups:
            if g != "":
                name = "[" + g + "]"
                if name not in newGroups:
                    newGroups.append("[" + g + "]")
    context.scene.cm_action_groups.groups.clear()
    for g in sorted(newGroups):
        a = context.scene.cm_action_groups.groups.add()
        a.name = g


class action_entry(PropertyGroup):
    """The data structure for the action entries"""
    name = StringProperty(update=updateGroups)
    action = StringProperty()
    motion = StringProperty()
    groups = StringProperty(update=updateGroups)


class actions_collection(PropertyGroup):
    coll = CollectionProperty(type=action_entry)
    index = IntProperty()


class SCENE_OT_cm_actions_populate(Operator):
    bl_idname = "scene.cm_actions_populate"
    bl_label = "Populate CM actions list"

    def execute(self, context):
        item = context.scene.cm_actions.coll.add()
        return {'FINISHED'}


class SCENE_OT_action_remove(Operator):
    bl_idname = "scene.cm_actions_remove"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.cm_actions.coll) > s.cm_actions.index >= 0

    def execute(self, context):
        s = context.scene
        s.cm_actions.coll.remove(s.cm_actions.index)
        if s.cm_actions.index > 0:
            s.cm_actions.index -= 1
        return {'FINISHED'}


class SCENE_OT_agent_move(Operator):
    bl_idname = "scene.cm_agents_move"
    bl_label = "Move"

    direction = EnumProperty(items=(
        ('UP', "Up", "Move up"),
        ('DOWN', "Down", "Move down"))
    )

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.cm_actions.coll) > s.cm_actions.index >= 0

    def execute(self, context):
        s = context.scene
        d = -1 if self.direction == 'UP' else 1
        new_index = (s.cm_actions.index + d) % len(s.cm_actions.coll)
        s.cm_actions.coll.move(s.cm_actions.index, new_index)
        s.cm_actions.index = new_index
        return {'FINISHED'}


class SCENE_UL_action(UIList):
    """for drawing each row"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="")
            layout.prop_search(item, "action", bpy.data, "actions", text="")
            layout.prop_search(item, "motion", bpy.data, "actions", text="")
            layout.prop(item, "groups", text="")

# =========================== Action groups (for search boxes) ================


class action_group(PropertyGroup):
    pass


class action_groups_collection(PropertyGroup):
    groups = CollectionProperty(type=action_group)
    index = IntProperty()


# =========================== Action pair definitions =========================

class action_pair(PropertyGroup):
    """The data structure for the action entries"""
    source = StringProperty()
    target = StringProperty()


class action_pair_collection(PropertyGroup):
    coll = CollectionProperty(type=action_pair)
    index = IntProperty()


class SCENE_OT_cm_action_pair_populate(Operator):
    bl_idname = "scene.cm_action_pair_populate"
    bl_label = "Populate CM action pairs list"

    def execute(self, context):
        item = context.scene.cm_action_pairs.coll.add()
        return {'FINISHED'}


class SCENE_OT_action_pair_remove(Operator):
    bl_idname = "scene.cm_action_pair_remove"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.cm_action_pairs.coll) > s.cm_action_pairs.index >= 0

    def execute(self, context):
        s = context.scene
        s.cm_action_pairs.coll.remove(s.cm_action_pairs.index)
        if s.cm_action_pairs.index > 0:
            s.cm_action_pairs.index -= 1
        return {'FINISHED'}


class SCENE_OT_action_pair_move(Operator):
    bl_idname = "scene.cm_action_pair_move"
    bl_label = "Move"

    direction = EnumProperty(items=(
        ('UP', "Up", "Move up"),
        ('DOWN', "Down", "Move down"))
    )

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.cm_action_pairs.coll) > s.cm_action_pairs.index >= 0

    def execute(self, context):
        s = context.scene
        d = -1 if self.direction == 'UP' else 1
        new_index = (s.cm_action_pairs.index + d) % len(s.cm_action_pairs.coll)
        s.cm_action_pairs.coll.move(s.cm_action_pairs.index, new_index)
        s.cm_action_pairs.index = new_index
        return {'FINISHED'}


class SCENE_UL_action_pair(UIList):
    """for drawing each row"""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop_search(item, "source", context.scene.cm_action_groups,
                               "groups", text="")
            layout.prop_search(item, "target", context.scene.cm_action_groups,
                               "groups", text="")


class SCENE_PT_action(Panel):
    """Creates CrowdMaster Panel in the node editor."""
    bl_label = "Actions"
    bl_idname = "SCENE_PT_action"
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

        row = layout.row()
        row.label("Name")
        row.label("Armature Action")
        row.label("Motion Action")
        row.label("Groups")

        row = layout.row()

        sce = bpy.context.scene

        row.template_list("SCENE_UL_action", "", sce.cm_actions,
                          "coll", sce.cm_actions, "index")

        col = row.column()
        sub = col.column(True)
        blid_ap = SCENE_OT_cm_actions_populate.bl_idname
        sub.operator(blid_ap, text="", icon="ZOOMIN")
        blid_ar = SCENE_OT_action_remove.bl_idname
        sub.operator(blid_ar, text="", icon="ZOOMOUT")

        sub = col.column(True)
        sub.separator()
        blid_am = SCENE_OT_agent_move.bl_idname
        sub.operator(blid_am, text="", icon="TRIA_UP").direction = 'UP'
        sub.operator(blid_am, text="", icon="TRIA_DOWN").direction = 'DOWN'

        layout.label("Action pairings:")
        row = layout.row()

        row.label("Source")
        row.label("Target")

        row = layout.row()

        row.template_list("SCENE_UL_action_pair", "", sce.cm_action_pairs,
                          "coll", sce.cm_action_pairs, "index")

        col = row.column()
        sub = col.column(True)
        blid_app = SCENE_OT_cm_action_pair_populate.bl_idname
        sub.operator(blid_app, text="", icon="ZOOMIN")
        blid_apr = SCENE_OT_action_pair_remove.bl_idname
        sub.operator(blid_apr, text="", icon="ZOOMOUT")

        sub = col.column(True)
        sub.separator()
        blid_apm = SCENE_OT_action_pair_move.bl_idname
        sub.operator(blid_apm, text="", icon="TRIA_UP").direction = 'UP'
        sub.operator(blid_apm, text="", icon="TRIA_DOWN").direction = 'DOWN'


def action_register():
    bpy.utils.register_class(action_entry)
    bpy.utils.register_class(SCENE_OT_cm_actions_populate)
    bpy.utils.register_class(SCENE_OT_action_remove)
    bpy.utils.register_class(SCENE_OT_agent_move)
    bpy.utils.register_class(actions_collection)
    bpy.utils.register_class(SCENE_UL_action)
    bpy.utils.register_class(SCENE_PT_action)
    bpy.types.Scene.cm_actions = PointerProperty(type=actions_collection)

    bpy.utils.register_class(action_pair)
    bpy.utils.register_class(SCENE_OT_cm_action_pair_populate)
    bpy.utils.register_class(SCENE_OT_action_pair_remove)
    bpy.utils.register_class(SCENE_OT_action_pair_move)
    bpy.utils.register_class(action_pair_collection)
    bpy.utils.register_class(SCENE_UL_action_pair)
    bpy.types.Scene.cm_action_pairs = PointerProperty(
        type=action_pair_collection)

    bpy.utils.register_class(action_group)
    bpy.utils.register_class(action_groups_collection)
    bpy.types.Scene.cm_action_groups = PointerProperty(
        type=action_groups_collection)


def action_unregister():
    bpy.utils.unregister_class(SCENE_UL_action)
    bpy.utils.unregister_class(SCENE_PT_action)
    bpy.utils.unregister_class(SCENE_OT_agent_move)
    bpy.utils.unregister_class(SCENE_OT_action_remove)
    bpy.utils.unregister_class(SCENE_OT_cm_actions_populate)
    bpy.utils.unregister_class(actions_collection)
    bpy.utils.unregister_class(action_entry)

    bpy.utils.unregister_class(SCENE_UL_action_pair)
    bpy.utils.unregister_class(SCENE_OT_action_pair_move)
    bpy.utils.unregister_class(SCENE_OT_action_pair_remove)
    bpy.utils.unregister_class(SCENE_OT_cm_action_pair_populate)
    bpy.utils.unregister_class(action_pair_collection)
    bpy.utils.unregister_class(action_pair)

    bpy.utils.unregister_class(action_group)
    bpy.utils.unregister_class(action_groups_collection)
