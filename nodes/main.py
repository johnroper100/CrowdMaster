import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
from mathutils import Vector
from .. icon_load import cicon

class CrowdMasterTree(NodeTree):
    '''The CrowdMaster node tree'''
    bl_idname = 'CrowdMasterTreeType'
    bl_label = 'CrowdMaster'
    bl_icon = 'MOD_REMESH'

class CrowdSocket(NodeSocket):
    '''Crowd socket used for transferring crowd data'''
    bl_idname = 'CrowdSocketType'
    bl_label = 'Crowd'
    
    def draw(self, context, layout, node, text):
        layout.label("Crowd")

    def draw_color(self, context, node):
        if self.is_linked:
            return (0.8, 0.514, 0.0, 1)
        else:
            return (0.8, 0.514, 0.0, 0.5)

class VectorSocket(NodeSocket):
    '''Vector socket used for transferring location data'''
    bl_idname = 'VectorSocketType'
    bl_label = 'Vector'
    dataType = "Vector"
    allowedInputTypes = ["Vector"]
    
    value = FloatVectorProperty(default = [0, 0, 0], subtype = "XYZ")
    
    def draw(self, context, layout, node, text):
        col = layout.column(align = True)
        if text != "": col.label(text)
        col.prop(self, "value", index = 0, text = "X")
        col.prop(self, "value", index = 1, text = "Y")
        col.prop(self, "value", index = 2, text = "Z")

    def draw_color(self, context, node):
        if self.is_linked:
            return (0.4, 0.4, 0.7, 1)
        else:
            return (0.4, 0.4, 0.7, 0.5)

class IntegerSocket(NodeSocket):
    '''Integer socket used for transferring integers'''
    bl_idname = 'IntegerSocketType'
    bl_label = 'Integer'
    dataType = "Integer"
    allowedInputTypes = ["Integer"]
    
    value = IntProperty(default = 0)
    
    def draw(self, context, layout, node, text):
        layout.prop(self, "value", text = text)

    def draw_color(self, context, node):
        if self.is_linked:
            return (0.4, 0.4, 0.7, 1)
        else:
            return (0.4, 0.4, 0.7, 0.5)

class FloatSocket(NodeSocket):
    '''Float socket used for transferring floats'''
    bl_idname = 'FloatSocketType'
    bl_label = 'Float'
    dataType = "Float"
    allowedInputTypes = ["Float", "Integer"]
    
    value = FloatProperty(default = 0.0)
    
    def draw(self, context, layout, node, text):
        layout.prop(self, "value", text = text)

    def draw_color(self, context, node):
        if self.is_linked:
            return (0.4, 0.4, 0.7, 1)
        else:
            return (0.4, 0.4, 0.7, 0.5)

class CrowdMasterTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CrowdMasterTreeType'

class CrowdDataOutputNode(Node, CrowdMasterTreeNode):
    '''The crowd data output node'''
    bl_idname = 'CrowdDataOutputNode'
    bl_label = 'Data Output'
    bl_icon = 'NODE'
    
    outputPath = bpy.props.StringProperty \
      (
      name = "Output Path",
      default = "",
      description = "Define the output path",
      subtype = 'DIR_PATH'
      )

    def init(self, context):
        self.inputs.new('CrowdSocketType', "Crowd")

    def draw_buttons(self, context, layout):
        layout.prop(self, "outputPath")

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "outputPath")

    def draw_label(self):
        return "Data Output"

class SimulateNode(Node, CrowdMasterTreeNode):
    '''The simulate node'''
    bl_idname = 'SimulateNode'
    bl_label = 'Simulate'
    bl_icon = 'NODE'

    def init(self, context):
        self.inputs.new('CrowdSocketType', "Crowd")

    def draw_buttons(self, context, layout):
        if self.inputs['Crowd'].is_linked == False:
            layout.enabled = False
        layout.scale_y = 1.5
        layout.operator("scene.cm_run_simulation", icon_value=cicon('run_sim'))

    def draw_buttons_ext(self, context, layout):
        if self.inputs['Crowd'].is_linked == False:
            layout.enabled = False
        layout.operator("scene.cm_run_simulation", icon_value=cicon('run_sim'))

    def draw_label(self):
        return "Simulate"

class IntegerNode(Node, CrowdMasterTreeNode):
    '''The integer node'''
    bl_idname = 'IntegerNode'
    bl_label = 'Integer'
    bl_icon = 'NODE'

    def init(self, context):
        self.outputs.new('IntegerSocketType', "Integer")
    
    def draw_buttons(self, context, layout):
        return None

    def draw_buttons_ext(self, context, layout):
        return None

    def draw_label(self):
        return "Integer"

class FloatNode(Node, CrowdMasterTreeNode):
    '''The float node'''
    bl_idname = 'FloatNode'
    bl_label = 'Float'
    bl_icon = 'NODE'
    
    Float = bpy.props.FloatProperty(default=2.5)

    def init(self, context):
        self.outputs.new('FloatSocketType', "Float")
    
    def draw_buttons(self, context, layout):
        return None

    def draw_buttons_ext(self, context, layout):
        return None

    def draw_label(self):
        return "Float"

class PositionNode(Node, CrowdMasterTreeNode):
    '''The main position node'''
    bl_idname = 'PositionNode'
    bl_label = 'Position'
    bl_icon = 'NODE'

    def init(self, context):
        self.inputs.new('VectorSocketType', "Vector")
        self.outputs.new('VectorSocketType', "Vector")

    def draw_buttons(self, context, layout):
        return None

    def draw_buttons_ext(self, context, layout):
        return None

    def draw_label(self):
        return "Position"

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class CrowdMasterCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CrowdMasterTreeType'

node_categories = [
    CrowdMasterCategory("INPUT", "Input", items=[
        NodeItem("IntegerNode"),
        NodeItem("FloatNode"),
        ]),
    CrowdMasterCategory("LOCATION", "Location", items=[
        NodeItem("PositionNode"),
        ]),
    CrowdMasterCategory("OUTPUT", "Output", items=[
        NodeItem("CrowdDataOutputNode"),
        NodeItem("SimulateNode"),
        ]),
    ]


def register_cnode():
    bpy.utils.register_class(CrowdMasterTree)
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)

def unregister_cnode():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")
    bpy.utils.unregister_class(CrowdMasterTree)

if __name__ == "__main__":
    register()
