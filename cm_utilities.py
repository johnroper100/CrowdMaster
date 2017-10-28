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
from bpy.props import BoolProperty
from bpy.types import Operator

from .cm_iconLoad import cicon

bpy.types.Scene.show_utilities = BoolProperty(
    name="Show or hide the utilities",
    description="Show/hide the utilities",
    default=False,
    options={'HIDDEN'}
)


class Crowdmaster_place_deferred_geo(Operator):
    bl_idname = "scene.cm_place_deferred_geo"
    bl_label = "Place Deferred Geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences

        groups = bpy.data.groups
        objects = context.scene.objects
        for group in context.scene.cm_groups:
            for agentType in group.agentTypes:
                for agent in agentType.agents:
                    for obj in groups[agent.geoGroup].objects:
                        if "cm_deferObj" in obj:
                            newObj = objects[obj["cm_deferObj"]].copy()

                            materials = obj["cm_materials"]
                            D = bpy.data
                            for m in newObj.material_slots:
                                if m.name in materials:
                                    replacement = materials[m.name]
                                    m.material = D.materials[replacement]

                            child = False
                            for con in obj.constraints:
                                if con.type == "CHILD_OF":
                                    child = True
                                    nCon = newObj.constraints.new("CHILD_OF")
                                    nCon.target = con.target
                                    nCon.subtarget = con.subtarget
                                    nCon.inverse_matrix = con.inverse_matrix
                                    newObj.data.update()
                            if not child:
                                newObj.matrix_world = obj.matrix_world
                            bpy.context.scene.objects.link(newObj)
                            for user_group in obj.users_group:
                                user_group.objects.link(newObj)
                        elif "cm_deferGroup" in obj:
                            df = obj["cm_deferGroup"]
                            originalGroup = df["group"]
                            newObjs = []
                            if "aName" in df:
                                aName = df["aName"]

                                gp = list(groups[originalGroup].objects)
                                for groupObj in gp:
                                    if groupObj.name != aName:
                                        newObjs.append(groupObj.copy())
                                    else:
                                        newObjs.append(
                                            context.scene.objects[agent.name])

                                for nObj in newObjs:
                                    if nObj.name == agent.name:
                                        continue
                                    if nObj.parent in gp:
                                        nObj.parent = newObjs[gp.index(
                                            nObj.parent)]

                                    groups[agent.geoGroup].objects.link(nObj)
                                    bpy.context.scene.objects.link(nObj)
                                    if nObj.type == 'MESH' and len(nObj.modifiers) > 0:
                                        for mod in nObj.modifiers:
                                            if mod.type == "ARMATURE":
                                                mod.object = objects[agent.name]
                            else:
                                gp = list(groups[originalGroup].objects)
                                for groupObj in gp:
                                    newObjs.append(groupObj.copy())

                                for nObj in newObjs:
                                    if nObj.parent in gp:
                                        nObj.parent = newObjs[gp.index(
                                            nObj.parent)]
                                    elif nObj.parent is None:
                                        nObj.parent = obj

                                    groups[agent.geoGroup].objects.link(nObj)
                                    bpy.context.scene.objects.link(nObj)
                            if "cm_materials" in obj:
                                materials = obj["cm_materials"]
                                for nObj in newObjs:
                                    D = bpy.data
                                    for m in nObj.material_slots:
                                        if m.name in materials:
                                            replacement = materials[m.name]
                                            m.material = D.materials[replacement]

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
    bpy.utils.register_class(Crowdmaster_place_deferred_geo)
    bpy.utils.register_class(Crowdmaster_switch_dupli_group)


def unregister():
    bpy.utils.unregister_class(Crowdmaster_place_deferred_geo)
    bpy.utils.unregister_class(Crowdmaster_switch_dupli_group)


if __name__ == "__main__":
    register()
