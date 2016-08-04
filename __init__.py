bl_info = {
    "name": "CrowdMaster",
    "author": "John Roper",
    "version": (1, 0, 8),
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
from . import mysql
from . mysql import mysql_general as cmDB
from . import icon_load
from . icon_load import register_icons, unregister_icons
from .cm_agent_generation import *

from . import addon_updater_ops

# =============== GROUPS LIST START ===============#

class SCENE_UL_group(UIList):
    """for drawing each row"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=str(item.name))
            layout.prop(item, "type", text="Node tree name")
            # layout.prop_search(item, "type", bpy.data, "actions", text="")
            # this draws each row in the list. Each line is a widget
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            # no idea when this is actually used


class SCENE_OT_group_populate(Operator):
    bl_idname = "scene.cm_groups_populate"
    bl_label = "Populate group list"

    def execute(self, context):
        groups = []
        toRemove = []
        sce = context.scene
        for f in range(len(sce.cm_groups.coll)):
            name = context.scene.cm_groups.coll[f].name
            if name not in groups:
                if name in [str(x.group) for x in sce.cm_agents.coll]:
                    groups.append(context.scene.cm_groups.coll[f].name)
            else:
                toRemove.append(f)
        for f in reversed(toRemove):
            context.scene.cm_groups.coll.remove(f)
        for agent in context.scene.cm_agents.coll:
            if str(agent.group) not in groups:
                groups.append(str(agent.group))
                item = context.scene.cm_groups.coll.add()
                item.name = str(agent.group)
                item.type = 'NONE'
        return {'FINISHED'}

# TODO  needs list clean up adding


class SCENE_OT_group_remove(Operator):
    """NOT USED NEEDS REMOVING ONCE THE POPULATE KEEPS THE LIST CLEAR"""
    bl_idname = "scene.cm_groups_remove"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.cm_groups.coll) > s.cm_groups.index >= 0

    def execute(self, context):
        s = context.scene
        s.cm_groups.coll.remove(s.cm_groups.index)
        if s.cm_groups.index > 0:
            s.cm_groups.index -= 1
        return {'FINISHED'}


class SCENE_OT_group_move(Operator):
    """NEEDS TO BE REMOVED ONCE POPULATE IS WORKING"""
    bl_idname = "scene.cm_groups_move"
    bl_label = "Move"

    direction = EnumProperty(items=(
        ('UP', "Up", "Move up"),
        ('DOWN', "Down", "Move down"))
    )

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.cm_groups.coll) > s.cm_groups.index >= 0

    def execute(self, context):
        s = context.scene
        d = -1 if self.direction == 'UP' else 1
        new_index = (s.cm_groups.index + d) % len(s.cm_groups.coll)
        s.cm_groups.coll.move(s.cm_groups.index, new_index)
        s.cm_groups.index = new_index
        return {'FINISHED'}

# =============== GROUPS LIST END ===============#

# =============== AGENTS LIST START ===============#

class SCENE_UL_agents(UIList):
    """for drawing each row"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.name in context.scene.objects:
                ic = 'OBJECT_DATA'
            else:
                ic = 'ERROR'
            layout.prop_search(item, "name", bpy.data, "objects")
            layout.prop(item, "group", text="Group number")
            typ = [g.type for g in bpy.context.scene.cm_groups.coll
                   if int(g.name) == item.group][0]
            layout.label(text=typ)
            # this draws each row in the list. Each line is a widget
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            # no idea when this is actually used


class SCENE_OT_cm_agents_populate(Operator):
    bl_idname = "scene.cm_agents_populate"
    bl_label = "Populate cm agents list"

    def findNext(self):
        g = [x.group for x in bpy.context.scene.cm_agents.coll]
        i = 1
        while True:
            if i not in g:
                return i
            else:
                i += 1

    def execute(self, context):
        setcmBrains()

        ag = [x.name for x in bpy.context.scene.cm_agents.coll]

        if bpy.context.scene.cm_agents_default.startType == "Next":
            group = self.findNext()
        else:
            group = bpy.context.scene.cm_agents_default.setno

        for i in bpy.context.selected_objects:
            if i.name not in ag:
                item = context.scene.cm_agents.coll.add()
                item.name = i.name
                item.group = group
                if bpy.context.scene.cm_agents_default.contType == "Inc":
                    if context.scene.cm_agents_default.startType == "Next":
                        group = self.findNext()
                    else:
                        bpy.context.scene.cm_agents_default.setno += 1
                        group = bpy.context.scene.cm_agents_default.setno
                item.type = 'NONE'
        bpy.ops.scene.cm_groups_populate()
        return {'FINISHED'}


class SCENE_OT_agent_remove(Operator):
    bl_idname = "scene.cm_agents_remove"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.cm_agents.coll) > s.cm_agents.index >= 0

    def execute(self, context):
        s = context.scene
        s.cm_agents.coll.remove(s.cm_agents.index)
        if s.cm_agents.index > 0:
            s.cm_agents.index -= 1
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
        return len(s.cm_agents.coll) > s.cm_agents.index >= 0

    def execute(self, context):
        s = context.scene
        d = -1 if self.direction == 'UP' else 1
        new_index = (s.cm_agents.index + d) % len(s.cm_agents.coll)
        s.cm_agents.coll.move(s.cm_agents.index, new_index)
        s.cm_agents.index = new_index
        return {'FINISHED'}


# =============== AGENTS LIST END ===============#

# =============== SELECTED LIST START ===============#


class SCENE_UL_selected(UIList):
    """for drawing each row"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.name in context.scene.objects:
                ic = 'OBJECT_DATA'
            else:
                ic = 'ERROR'
            layout.prop(item, "name", text="", emboss=False, icon=ic)
            # this draws each row in the list. Each line is a widget
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            # no idea when this is actually used


class SCENE_OT_cm_selected_populate(Operator):
    bl_idname = "scene.cm_selected_populate"
    bl_label = "See group"

    def execute(self, context):
        self.group = bpy.context.scene.cm_groups
        self.group_selected = bpy.context.scene.cm_agents_selected
        self.group_selected.coll.clear()

        for i in bpy.context.scene.cm_agents.coll:
            if self.group.index < len(self.group.coll):
                if i.group == int(self.group.coll[self.group.index].name):
                    item = context.scene.cm_agents_selected.coll.add()
                    item.name = i.name
        return {'FINISHED'}

# =============== SELECTED LIST END ===============#

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
        """for ag in bpy.context.scene.cm_agents.coll:
            sim.newagent(ag.name)"""
        sim.createAgents(bpy.context.scene.cm_agents.coll)
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
             return bpy.context.space_data.tree_type == 'CrowdMasterTreeType'
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
            row.prop(scene, "positionMode")
            
            row = box.row()
            if (scene.agentGroup == "") or (scene.groundObject == ""):
                row.enabled = False
            row.prop(scene, "positionType")
            
            if scene.positionType == "formation":
                row = box.row()
                row.prop(scene, "formationPositionType")
            
            row = box.row()
            if (scene.agentGroup == "") or (scene.groundObject == ""):
                row.enabled = False
            row.scale_y = 1.15
            row.operator(CrowdMaster_generate_agents.bl_idname, icon_value=cicon('plus_green'))
        
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
             return bpy.context.space_data.tree_type == 'CrowdMasterTreeType'
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
        row.template_list("SCENE_UL_group", "", scene.cm_groups,
                          "coll", scene.cm_groups, "index")

        col = row.column()
        sub = col.column(True)
        sub.operator(SCENE_OT_group_populate.bl_idname, text="", icon="ZOOMIN")

        sub = col.column(True)
        sub.separator()
        blid_gm = SCENE_OT_group_move.bl_idname
        sub.operator(blid_gm, text="", icon="TRIA_UP").direction = 'UP'
        sub.operator(blid_gm, text="", icon="TRIA_DOWN").direction = 'DOWN'
        sub.separator()
        blid_sp = SCENE_OT_cm_selected_populate.bl_idname
        sub.operator(blid_sp, text="", icon="PLUS")

        #####

        layout.label(text="Selected Agents:")
        layout.template_list("SCENE_UL_selected", "", scene.cm_agents_selected,
                             "coll", scene.cm_agents_selected, "index")

        #####

        layout.label(text="All agents:")
        row = layout.row()
        row.template_list("SCENE_UL_agents", "", scene.cm_agents,
                          "coll", scene.cm_agents, "index")

        col = row.column()
        sub = col.column(True)
        blid_ap = SCENE_OT_cm_agents_populate.bl_idname
        sub.operator(blid_ap, text="", icon="ZOOMIN")
        blid_ar = SCENE_OT_agent_remove.bl_idname
        sub.operator(blid_ar, text="", icon="ZOOMOUT")

        sub = col.column(True)
        sub.separator()
        blid_am = SCENE_OT_agent_move.bl_idname
        sub.operator(blid_am, text="", icon="TRIA_UP").direction = 'UP'
        sub.operator(blid_am, text="", icon="TRIA_DOWN").direction = 'DOWN'
        
        default = bpy.context.scene.cm_agents_default
        layout.label(text="Default agents group:")

        row = layout.row()
        row.prop(default, "startType", expand=True)
        row.prop(default, "setno", text="Group number")

        row = layout.row()
        row.prop(default, "contType", expand=True)

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

    from .cm_blenderData import registerTypes

    global setcmBrains
    from .cm_blenderData import setcmBrains

    global cm_bpyNodes
    from . import cm_bpyNodes
    cm_bpyNodes.register()

    registerTypes()
    action_register()
    event_register()

def initialise():
    sce = bpy.context.scene

    global Simulation
    from .cm_simulate import Simulation

    global update_cm_brains
    from .cm_blenderData import update_cm_brains

    global cm_brains
    cm_brains = bpy.context.scene.cm_brains

def unregister():
    unregister_icons()
    bpy.utils.unregister_module(__name__)

    action_unregister()
    event_unregister()
    from .cm_blenderData import unregisterAllTypes
    unregisterAllTypes()

    addon_updater_ops.unregister()
    # cm_bpyNodes.unregister()

if __name__ == "__main__":
    register()
