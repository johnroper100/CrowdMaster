import bpy
from . drawing2d import *
from . utils import *

cm_hudText = "Setup Your Node Tree to Get Started"
cm_hudText2 = "Time taken: None yet"


def update_hud_text(new_text):
    global cm_hudText
    cm_hudText = new_text

def update_hud_text2(new_text):
    global cm_hudText2
    cm_hudText2 = new_text


def draw_hud():
    preferences = bpy.context.user_preferences.addons["CrowdMaster"].preferences
    if preferences.show_node_hud:
        if getattr(bpy.context.space_data.node_tree, "bl_idname", "") not in ("CrowdMasterTreeType", "CrowdMasterAGenTreeType"):
            return
        else:
            set_drawing_dpi(get_dpi())
            dpi_factor = get_dpi_factor()

            object = bpy.context.active_object
            if object is not None:
                draw_object_status(object, dpi_factor)


def draw_object_status(object, dpi_factor):
    preferences = bpy.context.user_preferences.addons["CrowdMaster"].preferences

    if getattr(bpy.context.space_data.node_tree, "bl_idname", "") in "CrowdMasterTreeType":
        text1 = "CrowdMaster Agent Simulation: {}".format(cm_hudText)
    elif getattr(bpy.context.space_data.node_tree, "bl_idname", "") in "CrowdMasterAGenTreeType":
        text1 = cm_hudText2 + " CrowdMaster Agent Generation: {}".format(cm_hudText)
    text2 = "Show Debug Options is currently set to: {} | {}".format(preferences.show_debug_options, cm_hudText2)
    x = get_3d_view_tools_panel_overlay_width(bpy.context.area) + 20 * dpi_factor
    y1 = bpy.context.region.height - get_vertical_offset() * dpi_factor
    y2 = bpy.context.region.height - get_vertical_offset() - 30 * dpi_factor
    size1 = bpy.context.region.width / 40
    size2 = bpy.context.region.width / 50
    font_file1 = os.path.dirname(__file__) + "/fonts/BebasNeue.otf"
    font_file2 = os.path.dirname(__file__) + "/fonts/AGENCYB.TTF"
    draw_text_custom(text1, x, y1, font_file1, "ON", size=int(size1), color=(0.8, 0.5, 0.0, 1.0))
    draw_text_custom(text2, x, y2, font_file2, "OFF", size=int(size2), color=(0.7, 0.7, 0.7, 1.0))


def get_vertical_offset():
    if bpy.context.scene.unit_settings.system == "NONE":
        return 45
    else:
        return 65

draw_handler = None


def register():
    global draw_handler
    draw_handler = bpy.types.SpaceNodeEditor.draw_handler_add(draw_hud, tuple(), "WINDOW", "POST_PIXEL")


def unregister():
    font_file1 = os.path.dirname(__file__) + "/fonts/BebasNeue.otf"
    unload_custom_font(font_file1)
    
    font_file2 = os.path.dirname(__file__) + "/fonts/AGENCYB.TTF"
    unload_custom_font(font_file2)

    global draw_handler
    bpy.types.SpaceNodeEditor.draw_handler_remove(draw_handler, "WINDOW")
    draw_handler = None