# Copyright 2016 CrowdMaster Developer Team
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
import textwrap
from mathutils import Vector


def iterActiveSpacesByType(type):
    for space in iterActiveSpaces():
        if space.type == type:
            yield space


def iterActiveSpaces():
    for area in iterAreas():
        yield area.spaces.active


def getAreaWithType(type):
    for area in iterAreasByType(type):
        return area


def iterAreasByType(type):
    for area in iterAreas():
        if area.type == type:
            yield area


def iterAreas():
    for screen in iterActiveScreens():
        for area in screen.areas:
            yield area


def iterActiveScreens():
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            yield window.screen


def cm_redrawAll():
    for area in iterAreas():
        area.tag_redraw()        


def get_dpi_factor():
    return get_dpi() / 72


def get_dpi():
    systemPreferences = bpy.context.user_preferences.system
    retinaFactor = getattr(systemPreferences, "pixel_size", 1)
    return int(systemPreferences.dpi * retinaFactor)


def open_error_message(message="", title="Error", icon="ERROR"):
    def draw_error_message(self, context):
        self.layout.label(message)
    bpy.context.window_manager.popup_menu(draw_error_message, title=title, icon=icon)


def get_location_in_current_3d_view(horizontal="CENTER", vertical="CENTER", offset=(0, 0), adapt_offset_to_dpi=True):
    area = bpy.context.area
    if area.type == "VIEW_3D":
        for region in area.regions:
            if region.type == "WINDOW":
                return get_location_in_region(region, horizontal, vertical, offset, adapt_offset_to_dpi)
    return Vector((0, 0))


def get_location_in_region(region, horizontal="CENTER", vertical="CENTER", offset=(0, 0), adapt_offset_to_dpi=True):
    if horizontal == "LEFT":
        x = 0
    elif horizontal == "CENTER":
        x = region.width / 2
    elif horizontal == "RIGHT":
        x = region.width
    else:
        raise Exception("'{}' is not in ('LEFT', 'CENTER', 'RIGHT')".format(horizontal))

    if vertical == "TOP":
        y = region.height
    elif vertical == "CENTER":
        y = region.height / 2
    elif vertical == "BOTTOM":
        y = 0
    else:
        raise Exception("'{}' is not in ('TOP', 'CENTER', 'BOTTOM')".format(vertical))

    offset = Vector(offset)
    if adapt_offset_to_dpi:
        offset *= get_dpi_factor()
    return Vector((x, y)) + offset


def get_3d_view_tools_panel_overlay_width(area):
    use_region_overlap = bpy.context.user_preferences.system.use_region_overlap

    n = 0
    if use_region_overlap:
        for region in area.regions:
            if region.type == "UI":
                if region.x < bpy.context.region.width/3:
                    n = region.width

    if use_region_overlap:
        for region in area.regions:
            if region.type == "TOOLS":
                return region.width + n
    return 0


def write_text(layout, text, width=30, icon="NONE"):
    col = layout.column(align=True)
    col.scale_y = 0.85
    prefix = " "
    for paragraph in text.split("\n"):
        for line in textwrap.wrap(paragraph, width):
            col.label(prefix + line, icon=icon)
            if icon != "NONE":
                prefix = "     "
            icon = "NONE"

mouse_position = Vector((0, 0))


def get_mouse_position_in_current_region():
    bpy.ops.cm_store_mouse_position("INVOKE_DEFAULT")
    return mouse_position.copy()


class StoreMousePosition(bpy.types.Operator):
    bl_idname = "cm_store_mouse_position"
    bl_label = "Store Mouse Position"
    bl_options = {"REGISTER", "INTERNAL"}

    def invoke(self, context, event):
        mouse_position.x = event.mouse_region_x
        mouse_position.y = event.mouse_region_y
        return {"FINISHED"}
