# Copyright 2018 CrowdMaster Developer Team
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

import bgl
import blf


def drawLine3D(color, start, end, width=1):
    bgl.glLineWidth(width)
    bgl.glColor4f(*color)
    bgl.glBegin(bgl.GL_LINES)
    bgl.glVertex3f(*start)
    bgl.glVertex3f(*end)


def drawText2D(color, text):
    font_id = 0  # XXX, need to find out how best to get this.
    # draw some text
    bgl.glColor4f(*color)
    blf.position(font_id, 20, 70, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, text)


class bglWrapperClass:
    def __enter__(self):
        bgl.glEnable(bgl.GL_BLEND)

    def __exit__(self, type, value, traceback):
        bgl.glEnd()
        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glEnable(bgl.GL_DEPTH_TEST)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


bglWrapper = bglWrapperClass()


def draw_callback_2d(self, context):
    with bglWrapper:
        # draw text
        drawText2D((1.0, 1.0, 1.0, 1), "Hello Word ")
