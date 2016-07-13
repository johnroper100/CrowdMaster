import bpy
import bgl
import blf
import sys
from ..nodes import main

def line(color, start, end):
    bgl.glColor4f(*color)
    bgl.glBegin(bgl.GL_LINES)
    bgl.glVertex3f(*start)
    bgl.glVertex3f(*end)
    bgl.glEnd()

def draw_callback_px(self, context):
    bgl.glPushAttrib(bgl.GL_ENABLE_BIT)

    bgl.glLineStipple(10, 0x9999)
    bgl.glEnable(bgl.GL_LINE_STIPPLE)

    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 1.0, 0.5)
    bgl.glLineWidth(5)

    bgl.glPopAttrib()

    width = context.area.width
    height = context.area.height

    p1 = (0,0,0)
    p4 = (0, height, 0)
    p3 = (width, height, 0)
    p5 = (width, 0, 0)

    line((1.0, 0.0, 0.0, 0.1), p1, p3)
    line((0.0, 1.0, 0.0, 0.1), p4, p5)

    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

class ShowPositionGraphics(bpy.types.Operator):
    """Show the positional graphics"""
    bl_idname = "scene.cm_show_position_graphics"
    bl_label = "Show Diagram"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'ESC':
            bpy.types.SpaceNodeEditor.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    def invoke(self, context, event):
        if context.area.type == 'NODE_EDITOR':
            args = (self, context)
            self._handle = bpy.types.SpaceNodeEditor.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            return {'RUNNING_MODAL'}
        elif event.type == 'ESC':
            bpy.types.SpaceNodeEditor.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "NODE_EDITOR not found, cannot run operator")
            return {'CANCELLED'}

    def execute(self, context):
        print("Showing the graphics!")

        return {'FINISHED'}

class HidePositionGraphics(bpy.types.Operator):
    """Hide the positional graphics"""
    bl_idname = "scene.cm_hide_position_graphics"
    bl_label = "Hide Diagram"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.area.type == 'NODE_EDITOR':
            args = (self, context)
            print("Hiding the graphics!")
            bpy.types.SpaceNodeEditor.draw_handler_remove(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        return {'FINISHED'}

class RunSimulation(bpy.types.Operator):
    """Run CrowdMaster simulation"""
    bl_idname = "scene.cm_run_simulation"
    bl_label = "Run Simulation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Running simulation!")
        
        links = bpy.data.node_groups["NodeTree"].links
        print(links)

        return {'FINISHED'}
