import bpy
import random
from bpy.props import IntProperty, EnumProperty, CollectionProperty
from bpy.props import PointerProperty, BoolProperty, StringProperty
from bpy.types import PropertyGroup, UIList, Panel, Operator


class action_entry(PropertyGroup):
    """The data structure for the action entries"""
    action = StringProperty()
    motion = StringProperty()
    # subtracted = BoolProperty()
    index = IntProperty(min=0)


class actions_collection(PropertyGroup):
    coll = CollectionProperty(type=action_entry)
    index = IntProperty()


class SCENE_OT_cm_actions_populate(Operator):
    bl_idname = "scene.cm_actions_populate"
    bl_label = "Populate cm actions list"

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
            # layout.label(text=str(item.name))
            layout.prop(item, "name", text="Name")
            layout.prop_search(item, "action", bpy.data, "actions", text="")
            layout.prop_search(item, "motion", bpy.data, "actions", text="")
            # layout.prop(item, "subtracted", text="")
            # this draws each row in the list. Each line is a widget
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            # no idea when this is actually used


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
             return bpy.context.space_data.tree_type == 'CrowdMasterTreeType', context.space_data.tree_type == 'CrowdMasterGenTreeType'
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        sce = context.scene

        row = layout.row()
        row.label("Actions must have location and rotation but not scale")

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


def action_register():
    # bpy.utils.register_module(__name__)
    bpy.utils.register_class(action_entry)
    bpy.utils.register_class(SCENE_OT_cm_actions_populate)
    bpy.utils.register_class(SCENE_OT_action_remove)
    bpy.utils.register_class(SCENE_OT_agent_move)
    bpy.utils.register_class(actions_collection)
    bpy.utils.register_class(SCENE_UL_action)
    bpy.utils.register_class(SCENE_PT_action)
    bpy.types.Scene.cm_actions = PointerProperty(type=actions_collection)
    # bpy.utils.register_class(SCENE_UL_action)


def action_unregister():
    # bpy.utils.unregister_module(__name__)
    # del bpy.types.Scene.cm_actions
    bpy.utils.unregister_class(SCENE_UL_action)
    bpy.utils.unregister_class(SCENE_PT_action)
    bpy.utils.unregister_class(SCENE_OT_agent_move)
    bpy.utils.unregister_class(SCENE_OT_action_remove)
    bpy.utils.unregister_class(SCENE_OT_cm_actions_populate)
    bpy.utils.unregister_class(actions_collection)
    bpy.utils.unregister_class(action_entry)
