import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .. icon_load import cicon

class CrowdMasterTree(NodeTree):
    '''The CrowdMaster node tree'''
    bl_idname = 'CrowdMasterTreeType'
    bl_label = 'CrowdMaster'
    bl_icon = 'MOD_REMESH'

class MyCustomSocket(NodeSocket):
    '''Custom node socket type'''
    bl_idname = 'CustomSocketType'
    bl_label = 'Custom Node Socket'

    my_items = [
        ("DOWN", "Down", "Where your feet are"),
        ("UP", "Up", "Where your head should be"),
        ("LEFT", "Left", "Not right"),
        ("RIGHT", "Right", "Not left")
    ]

    myEnumProperty = bpy.props.EnumProperty(name="Direction", description="Just an example", items=my_items, default='UP')

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "myEnumProperty", text=text)

    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)

class CrowdSocket(NodeSocket):
    '''Crowd socket used for transferring crowd data'''
    bl_idname = 'CrowdSocketType'
    bl_label = 'Crowd'
    
    def draw(self, context, layout, node, text):
        layout.label("Crowd")

    def draw_color(self, context, node):
        return (0.8, 0.514, 0.0, 1.0)


# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class CrowdMasterTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CrowdMasterTreeType'

class MyCustomNode(Node, CrowdMasterTreeNode):
    '''A custom node'''
    bl_idname = 'CustomNodeType'
    bl_label = 'Custom Node'
    bl_icon = 'SOUND'


    myStringProperty = bpy.props.StringProperty()
    myFloatProperty = bpy.props.FloatProperty(default=3.1415926)

    # === Optional Functions ===
    # Initialization function, called when a new node is created.
    # This is the most common place to create the sockets for a node, as shown below.
    # NOTE: this is not the same as the standard __init__ function in Python, which is
    #       a purely internal Python method and unknown to the node system!
    def init(self, context):
        self.inputs.new('CrowdSocketType', "Hello")
        self.inputs.new('CustomSocketType', "Hello")
        self.inputs.new('NodeSocketFloat', "World")
        self.inputs.new('NodeSocketVector', "!")

        self.outputs.new('NodeSocketColor', "How")
        self.outputs.new('NodeSocketColor', "are")
        self.outputs.new('NodeSocketFloat', "you")

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.label("Node settings")
        layout.prop(self, "myFloatProperty")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "myFloatProperty")
        # myStringProperty button will only be visible in the sidebar
        layout.prop(self, "myStringProperty")

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "I am a custom node"

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

# all categories in a list
node_categories = [
    CrowdMasterCategory("INPUT", "Input", items=[
        NodeItem("CustomNodeType"),
        ]),
    CrowdMasterCategory("OUTPUT", "Output", items=[
        NodeItem("CrowdDataOutputNode"),
        NodeItem("SimulateNode"),
        ]),
    CrowdMasterCategory("OTHERNODES", "Other Nodes", items=[
        NodeItem("CustomNodeType", label="Node A", settings={
            "myStringProperty": repr("Lorem ipsum dolor sit amet"),
            "myFloatProperty": repr(1.0),
            }),
        NodeItem("CustomNodeType", label="Node B", settings={
            "myStringProperty": repr("consectetur adipisicing elit"),
            "myFloatProperty": repr(2.0),
            }),
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
