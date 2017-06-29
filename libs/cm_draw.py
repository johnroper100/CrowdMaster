import bgl
import blf
import bpy


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
