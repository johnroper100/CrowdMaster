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

import blf
import bgl
from bgl import *

dpi = 72


def set_drawing_dpi(new_dpi):
    global dpi
    dpi = new_dpi


def draw_horizontal_line(x, y, length, color, width):
    draw_line(x, y, x + length, y, color, width)


def draw_line(x1, y1, x2, y2, color, width):
    glLineWidth(width)
    glColor4f(*color)
    glEnable(GL_BLEND)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()
    glLineWidth(1)


def draw_boolean(state, x, y, size=12, alpha=1):
    if state:
        draw_text("ON", x, y, align="LEFT", size=size,
                  color=(0.8, 1, 0.8, alpha))
    else:
        draw_text("OFF", x, y, align="LEFT", size=size,
                  color=(1, 0.8, 0.8, alpha))


def draw_text_default(text, x, y, align="LEFT", size=12, color=(1.0, 1.0, 1.0, 1.0)):
    font = 0

    blf.size(font, size, int(dpi))
    glColor4f(*color)

    if align == "LEFT":
        blf.position(font, x, y, 0)
    else:
        width, height = blf.dimensions(font, text)
        if align == "RIGHT":
            blf.position(font, x - width, y, 0)

    blf.draw(font, text)


def draw_text_custom(text, x, y, font_file_path, shadow_on, align="LEFT", size=12, color=(1.0, 1.0, 1.0, 1.0)):
    font_path = font_file_path
    font_id = blf.load(font_path)
    font = font_id

    blf.size(font, size, int(dpi))
    glColor4f(*color)

    if shadow_on == "ON":
        blf.shadow(font, 5, 0.0, 0.0, 0.0, 1.0)

    if align == "LEFT":
        blf.position(font, x, y, 0)
    else:
        width, height = blf.dimensions(font, text)
        if align == "RIGHT":
            blf.position(font, x - width, y, 0)

    blf.draw(font, text)


def unload_custom_font(font_file_path):
    font_path = font_file_path
    font_id = blf.unload(font_path)


def draw_box(x0, y0, width, height, color):

    x1 = x0 + width
    y1 = y0 - height/2
    y0 += height/2

    position = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]

    for mode in [bgl.GL_QUADS]:
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBegin(mode)
        bgl.glColor4f(*color)
        for v1, v2 in position:
            bgl.glVertex2f(v1, v2)
    bgl.glEnd()
