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
import re
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

class Crowdmaster_switch_dupli_group(Operator):
    bl_idname = "scene.cm_switch_dupli_groups"
    bl_label = "Switch Dupli Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        suffix = bpy.context.scene.cm_switch_dupli_group_suffix
        repRegex = re.compile("(?P<prefix>.*)({})(?P<number>.\d*)?".format(suffix))
        for obj in bpy.context.selected_objects:
            if obj.dupli_type == "GROUP":
                match = repRegex.match(obj.dupli_group.name)
                if match:
                    parts = match.groupdict(default="")
                    target = bpy.context.scene.cm_switch_dupli_group_target
                    searchRegex = re.compile(parts["prefix"] + target + parts["number"])
                    replaceSource = obj.dupli_group.library
                    for grp in bpy.data.groups:
                        if searchRegex.match(grp.name):
                            if grp.library == replaceSource:
                                obj.dupli_group = grp
        return {'FINISHED'}


def register():
    bpy.utils.register_class(Crowdmaster_switch_dupli_group)

def unregister():
    bpy.utils.unregister_class(Crowdmaster_switch_dupli_group)

if __name__ == "__main__":
    register()
