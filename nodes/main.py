import bpy
from bpy.types import NodeTree, Node, NodeSocket

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

    @classmethod
    def getDefaultValue(cls):
        return None

    @classmethod
    def getDefaultValueCode(cls):
        return "None"

    @classmethod
    def correctValue(cls, value):
        return value, 0

    # Socket color
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

class CrowdOutputNode(Node, CrowdMasterTreeNode):
    '''The crowd output node'''
    bl_idname = 'CrowdOutputNode'
    bl_label = 'Output'
    bl_icon = 'SOUND'

    myStringProperty = bpy.props.StringProperty()
    myFloatProperty = bpy.props.FloatProperty(default=3.1415926)

    def init(self, context):
        self.inputs.new('CrowdSocketType', "Hello")

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
        layout.prop(self, "myStringProperty")

    def draw_label(self):
        return "Output"

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
        NodeItem("CrowdOutputNode"),
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
    bpy.utils.register_class(MyCustomSocket)
    bpy.utils.register_class(CrowdSocket)
    bpy.utils.register_class(MyCustomNode)

    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)


def unregister_cnode():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")

    bpy.utils.unregister_class(CrowdMasterTree)
    bpy.utils.unregister_class(MyCustomSocket)
    bpy.utils.unregister_class(CrowdSocket)
    bpy.utils.unregister_class(MyCustomNode)


if __name__ == "__main__":
    register()