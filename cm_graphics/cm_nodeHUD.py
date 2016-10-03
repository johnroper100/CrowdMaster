import bpy
from . drawing2d import *
from . utils import get_dpi, get_dpi_factor, get_3d_view_tools_panel_overlay_width

cm_hudText = "Press the Start Simulation button to get started simulating"

def update_hud_text(new_text):
    global cm_hudText
    cm_hudText = new_text

def draw_hud():
    if getattr(bpy.context.space_data.node_tree, "bl_idname", "") not in ("CrowdMasterTreeType", "CrowdMasterAGenTreeType"): 
        return
    else:
        set_drawing_dpi(get_dpi())
        dpi_factor = get_dpi_factor()

        object = bpy.context.active_object
        if object is not None:
            draw_object_status(object, dpi_factor)

def draw_object_status(object, dpi_factor):
    print("Is it working?")
    if getattr(bpy.context.space_data.node_tree, "bl_idname", "") in "CrowdMasterTreeType":
        text1 = "CrowdMaster Simulation: {}".format(cm_hudText)
    elif getattr(bpy.context.space_data.node_tree, "bl_idname", "") in "CrowdMasterAGenTreeType":
        text1 = "CrowdMaster Agent Generation: {}".format(cm_hudText)
    text2 = "For more info go to http://jmroper.com/crowdmaster"
    x = get_3d_view_tools_panel_overlay_width(bpy.context.area) + 20 * dpi_factor
    y1 = bpy.context.region.height - get_vertical_offset() * dpi_factor
    y2 = bpy.context.region.height - get_vertical_offset() - 25 * dpi_factor
    draw_text(text1, x, y1, size = 15, color = (0.8, 0.5, 0.0, 1.0))
    draw_text(text2, x, y2, size = 12, color = (1.0, 1.0, 1.0, 0.5))

def get_vertical_offset():
    if bpy.context.scene.unit_settings.system == "NONE":
        return 40
    else:
        return 60



# Register
################################################################################

draw_handler = None

def register():
    global draw_handler
    draw_handler = bpy.types.SpaceNodeEditor.draw_handler_add(draw_hud, tuple(), "WINDOW", "POST_PIXEL")

def unregister():
    global draw_handler
    bpy.types.SpaceNodeEditor.draw_handler_remove(draw_handler, "WINDOW")
    draw_handler = None