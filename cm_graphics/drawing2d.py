import blf
import bgl
from bgl import *
import bpy
from . utils import get_dpi_factor

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

def draw_boolean(state, x, y, size = 12, alpha = 1):
    if state:
        draw_text("ON", x, y, align = "LEFT", size = size,
                  color = (0.8, 1, 0.8, alpha))
    else:
        draw_text("OFF", x, y, align = "LEFT", size = size,
                  color = (1, 0.8, 0.8, alpha))

def draw_text(text, x, y, align = "LEFT", size = 12, color = (1, 1, 1, 1)):
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


# Kept for example
def draw_logo_csharp(color):

    rw = bpy.context.region.width
    rh = bpy.context.region.height
    d = get_dpi_factor()
    x = - 80 *d
    y = 4 *d

    bgl.glColor4f(*color)

    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw + 0 + x, 13*d + y)
    bgl.glVertex2f(rw + 2.5*d + x, 13*d + y)
    bgl.glVertex2f(rw + 2.5*d + x, 4*d + y)
    bgl.glVertex2f(rw + 3*d + x, 3*d + y)
    bgl.glVertex2f(rw + 1.7*d + x, 1.7*d + y)
    bgl.glVertex2f(rw + 0 + x, 3*d + y)
    bgl.glEnd()

    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw + 13*d + x, 0 + y)
    bgl.glVertex2f(rw + 13*d + x, 2.5*d + y)
    bgl.glVertex2f(rw + 4*d + x, 2.5*d + y)
    bgl.glVertex2f(rw + 3*d + x, 3*d + y)
    bgl.glVertex2f(rw + 1.7*d + x, 1.7*d + y)
    bgl.glVertex2f(rw + 3*d + x, 0 + y)
    bgl.glEnd()

    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw+ 7*d + x, 4*d + y)
    bgl.glVertex2f(rw+ 12*d + x, 4*d + y)
    bgl.glVertex2f(rw+ 12*d + x, 12*d + y)
    bgl.glVertex2f(rw+ 7*d + x, 14*d + y)
    bgl.glEnd()

    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw+ 7*d + x, 14*d + y)
    bgl.glVertex2f(rw+ 12*d + x, 12*d + y)
    bgl.glVertex2f(rw+ 18*d + x, 18*d + y)
    bgl.glVertex2f(rw+ 16*d + x, 23*d + y)
    bgl.glEnd()

    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw+ 16*d + x, 23*d + y)
    bgl.glVertex2f(rw+ 18*d + x, 18*d + y)
    bgl.glVertex2f(rw+ 26*d + x, 18*d + y)
    bgl.glVertex2f(rw+ 26*d + x, 23*d + y)
    bgl.glEnd()

    x = x +30 *d 


    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw- 0 + x, 13*d + y)
    bgl.glVertex2f(rw- 2.5*d + x, 13*d + y)
    bgl.glVertex2f(rw- 2.5*d + x, 4*d + y)
    bgl.glVertex2f(rw- 3*d + x, 3*d + y)
    bgl.glVertex2f(rw- 1.7*d + x, 1.7*d + y)
    bgl.glVertex2f(rw- 0 + x, 3*d + y)
    bgl.glEnd()

    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw- 13*d + x, 0 + y)
    bgl.glVertex2f(rw- 13*d + x, 2.5*d + y)
    bgl.glVertex2f(rw- 4*d + x, 2.5*d + y)
    bgl.glVertex2f(rw- 3*d + x, 3*d + y)
    bgl.glVertex2f(rw- 1.7*d + x, 1.7*d + y)
    bgl.glVertex2f(rw- 3*d + x, 0 + y)
    bgl.glEnd()


    x = - 80 *d
    y = y + 30*d

    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw + 0 + x, -13*d + y)
    bgl.glVertex2f(rw + 2.5*d + x, -13*d + y)
    bgl.glVertex2f(rw + 2.5*d + x, -4*d + y)
    bgl.glVertex2f(rw + 3*d + x, -3*d + y)
    bgl.glVertex2f(rw + 1.7*d + x, -1.7*d + y)
    bgl.glVertex2f(rw + 0 + x, -3*d + y)
    bgl.glEnd()

    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw + 13*d + x, -0 + y)
    bgl.glVertex2f(rw + 13*d + x, -2.5*d + y)
    bgl.glVertex2f(rw + 4*d + x, -2.5*d + y)
    bgl.glVertex2f(rw + 3*d + x, -3*d + y)
    bgl.glVertex2f(rw + 1.7*d + x, -1.7*d + y)
    bgl.glVertex2f(rw + 3*d + x, -0 + y)
    bgl.glEnd()

    x = x +30 *d 

    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw- 0 + x, -13*d + y)
    bgl.glVertex2f(rw- 2.5*d + x, -13*d + y)
    bgl.glVertex2f(rw- 2.5*d + x, -4*d + y)
    bgl.glVertex2f(rw- 3*d + x, -3*d + y)
    bgl.glVertex2f(rw- 1.7*d + x, -1.7*d + y)
    bgl.glVertex2f(rw- 0 + x, -3*d + y)
    bgl.glEnd()

    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glVertex2f(rw- 13*d + x, -0 + y)
    bgl.glVertex2f(rw- 13*d + x, -2.5*d + y)
    bgl.glVertex2f(rw- 4*d + x, -2.5*d + y)
    bgl.glVertex2f(rw- 3*d + x, -3*d + y)
    bgl.glVertex2f(rw- 1.7*d + x, -1.7*d + y)
    bgl.glVertex2f(rw- 3*d + x, -0 + y)
    bgl.glEnd()
