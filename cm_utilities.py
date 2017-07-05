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

import time

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

from .cm_iconLoad import cicon

bpy.types.Scene.show_utilities = BoolProperty(
    name="Show or hide the utilities",
    description="Show/hide the utilities",
    default=False,
    options={'HIDDEN'}
)


class CrowdMaster_convert_to_bound_box(Operator):
    bl_idname = "scene.cm_convert_to_bound_box"
    bl_label = "Convert Selected To Bounding Box"

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences

        selected = bpy.context.selected_objects
        for obj in selected:
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            bpy.ops.mesh.primitive_cube_add()
            bound_box = bpy.context.active_object

            bound_box.location = obj.location
            bound_box.rotation_euler = obj.rotation_euler
            bound_box.select = True

        return {'FINISHED'}


class Crowdmaster_switch_dupli_group(Operator):
    bl_idname = "scene.cm_switch_dupli_groups"
    bl_label = "Switch Dupli Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.dupli_type == "GROUP":
                suffix = bpy.context.scene.cm_switch_dupli_group_suffix
                if obj.dupli_group.name[-len(suffix):] == suffix:
                    target = bpy.context.scene.cm_switch_dupli_group_target
                    replaceName = obj.dupli_group.name[:-len(suffix)] + target
                    replaceSource = obj.dupli_group.library
                    for grp in bpy.data.groups:
                        if grp.name == replaceName:
                            if grp.library == replaceSource:
                                obj.dupli_group = grp
        return {'FINISHED'}


def register():
    bpy.utils.register_class(CrowdMaster_convert_to_bound_box)
    bpy.utils.register_class(Crowdmaster_switch_dupli_group)

def unregister():
    bpy.utils.unregister_class(CrowdMaster_convert_to_bound_box)
    bpy.utils.unregister_class(Crowdmaster_switch_dupli_group)

if __name__ == "__main__":
    register()
