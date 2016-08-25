import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty
from .. icon_load import cicon

class CrowdMasterAGenTree(NodeTree):
    '''CrowdMaster agent generation node tree'''
    bl_idname = 'CrowdMasterAGenTreeType'
    bl_label = 'CrowdMaster Agent Generation'
    bl_icon = 'MOD_ARRAY'

class GeoSocket(NodeSocket):
    '''Geo node socket type'''
    bl_idname = 'GeoSocketType'
    bl_label = 'Geo Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.0, 0.0, 0.2, 0.5)

class TemplateSocket(NodeSocket):
    '''Template node socket type'''
    bl_idname = 'TemplateSocketType'
    bl_label = 'Template Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.8, 0.5, 0.0, 0.9)

class ObjectSocket(NodeSocket):
    '''Object node socket type'''
    bl_idname = 'ObjectSocketType'
    bl_label = 'Object Node Socket'

    inputObject = StringProperty(name="Object")

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.prop_search(self, "inputObject", context.scene, "objects", text=text)

    def draw_color(self, context, node):
        return (1.0, 0.5, 0.2, 0.5)

class GroupSocket(NodeSocket):
    '''Group node socket type'''
    bl_idname = 'GroupSocketType'
    bl_label = 'Group Node Socket'

    inputGroup = StringProperty(name="Group")

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.prop_search(self, "inputGroup", bpy.data, "groups", text=text)

    def draw_color(self, context, node):
        return (1.0, 0.5, 0.2, 0.5)

class CrowdMasterAGenTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CrowdMasterAGenTreeType'

class MyCustomNode(Node, CrowdMasterAGenTreeNode):
    # === Basics ===
    # Description string
    '''A custom node'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'CustomNodeType'
    # Label for nice name display
    bl_label = 'Custom Node'
    # Icon identifier
    bl_icon = 'SOUND'

    # === Custom Properties ===
    # These work just like custom properties in ID data blocks
    # Extensive information can be found under
    # http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
    myStringProperty = bpy.props.StringProperty()
    myFloatProperty = bpy.props.FloatProperty(default=3.1415926)

    # === Optional Functions ===
    # Initialization function, called when a new node is created.
    # This is the most common place to create the sockets for a node, as shown below.
    # NOTE: this is not the same as the standard __init__ function in Python, which is
    #       a purely internal Python method and unknown to the node system!
    def init(self, context):
        self.inputs.new('ObjectSocketType', "Hello")
        self.inputs.new('NodeSocketFloat', "World")
        self.inputs.new('NodeSocketVector', "!")

        self.outputs.new('NodeSocketColor', "How")
        self.outputs.new('NodeSocketColor', "are")
        self.outputs.new('GroupSocketType', "are")
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

class GenerateNode(Node, CrowdMasterAGenTreeNode):
    '''The generate node'''
    bl_idname = 'GenerateNodeType'
    bl_label = 'Generate'
    bl_icon = 'SOUND'

    def init(self, context):
        self.inputs.new('TemplateSocketType', "Template")

    def draw_buttons(self, context, layout):
        layout.scale_y = 1.5
        layout.operator("scene.cm_gen_agents", icon_value=cicon('plus_yellow'))

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class CrowdMasterAGenCategories(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CrowdMasterAGenTreeType'

agen_node_categories = [
    CrowdMasterAGenCategories("SOMENODES", "Some Nodes", items=[
        NodeItem("GenerateNodeType"),
        ]),
    ]

def register():
    bpy.utils.register_class(CrowdMasterAGenTree)
    bpy.utils.register_class(GeoSocket)
    bpy.utils.register_class(TemplateSocket)
    bpy.utils.register_class(ObjectSocket)
    bpy.utils.register_class(GroupSocket)
    bpy.utils.register_class(GenerateNode)

    nodeitems_utils.register_node_categories("AGEN_CUSTOM_NODES", agen_node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("AGEN_CUSTOM_NODES")

    bpy.utils.unregister_class(CrowdMasterAGenTree)
    bpy.utils.unregister_class(GeoSocket)
    bpy.utils.unregister_class(TemplateSocket)
    bpy.utils.unregister_class(ObjectSocket)
    bpy.utils.unregister_class(GroupSocket)
    bpy.utils.unregister_class(GenerateNode)


if __name__ == "__main__":
    register()
