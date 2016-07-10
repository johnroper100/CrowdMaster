import bpy
from bpy.types import NodeTree, Node, NodeSocket
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
        return (0.8, 0.514, 0.0, 1.0)

class CrowdMasterTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CrowdMasterTreeType'

class CrowdDataOutputNode(Node, CrowdMasterTreeNode):
    '''The crowd data output node'''
    bl_idname = 'CrowdDataOutputNode'
    bl_label = 'Data Output'
    bl_icon = 'SOUND'
    
    outputPath = bpy.props.StringProperty \
      (
      name = "Output Path",
      default = "",
      description = "Define the output path",
      subtype = 'DIR_PATH'
      )

    def init(self, context):
        self.inputs.new('CrowdSocketType', "Crowd")

    def copy(self, node):
        print("Copying from node ", node)

    def free(self):
        print("Removing node ", self, ", Goodbye!")

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
    bl_icon = 'SOUND'

    def init(self, context):
        self.inputs.new('CrowdSocketType', "Crowd")

    def copy(self, node):
        print("Copying from node ", node)

    def free(self):
        print("Removing node ", self, ", Goodbye!")

    def draw_buttons(self, context, layout):
        layout.scale_y = 1.5
        layout.operator("scene.cm_init_database", icon_value=cicon('setup_plug'))

    def draw_buttons_ext(self, context, layout):
        layout.operator("scene.cm_init_database", icon_value=cicon('setup_plug'))

    def draw_label(self):
        return "Simulate"

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class CrowdMasterCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CrowdMasterTreeType'

node_categories = [
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
