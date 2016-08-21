import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty

class CrowdMasterGenTree(NodeTree):
    """The node tree that contains the CrowdMaster agent gen nodes"""
    bl_idname = 'CrowdMasterGenTreeType'
    bl_label = 'CrowdMaster Agent Generation'
    bl_icon = 'MOD_ARRAY'

class DefaultSocket(NodeSocket):
    # Description string
    """Default socket"""
    # If not explicitly defined, the python class name is used.
    bl_idname = 'DefaultSocketType'
    # Label for nice name display
    bl_label = 'Default CrowdMaster Node Socket'

    filterProperty = EnumProperty(items=[("AVERAGE", "Average", "", 1),
                                         ("MAX", "Max", "", 2),
                                         ("MIN", "Min", "", 3)
                                         ])
    defaultValueProperty = FloatProperty(default=1.0)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if not self.is_output and node.bl_idname == "ActionState":
            if self.is_linked:
                layout.prop(self, "filterProperty", text=text)
            else:
                layout.prop(self, "defaultValueProperty", text=text)
        else:
            layout.label(text)

    # Socket color
    def draw_color(self, context, node):
        if self.is_linked:
            return (0.0, 0.0, 0.0, 0.7)
        else:
            return (0.0, 0.0, 0.0, 0.4)

class CrowdMasterGenNode(Node):
    """CrowdMaster generate node superclass"""
    bl_label = 'Super class'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CrowdMasterGenTreeType'

class DataInputNode(CrowdMasterGenNode):
    bl_label = 'Data input super class'

    def init(self, context):
        self.inputs.new("DefaultSocketType", "Input")
        self.inputs[0].link_limit = 4095

    def getSettings(self, node):
        pass

class DataOutputNode(CrowdMasterGenNode):
    bl_label = 'Data output super class'

    def init(self, context):
        self.outputs.new('DefaultSocketType', "Output")

    def getSettings(self, node):
        pass

# ============ End of super classes ============

class GroupInputNode(DataOutputNode):
    """CrowdMaster group input node"""
    bl_label = "Group"

    Group = StringProperty()

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "Group", bpy.data, "groups")

    def getSettings(self, node):
        node.settings["Group"] = self.Group

class ObjectInputNode(DataOutputNode):
    """CrowdMaster group input node"""
    bl_label = "Object"

    Object = StringProperty()

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "Object", context.scene, "objects")

    def getSettings(self, node):
        node.settings["Object"] = self.Object

class NumberInputNode(DataOutputNode):
    """CrowdMaster number input node"""
    bl_label = "Number"

    Int = IntProperty(name="Integer", default=1)
    Float = FloatProperty(name="Float", default=1.0)
    Vector = FloatVectorProperty(name="Vector", default = [0, 0, 0], subtype = "XYZ")
    
    numType = EnumProperty(
        items = [('int', 'Integer', 'An integer type number.'), 
                 ('float', 'Float', 'A float type number.'),
                 ('vector', 'Vector', 'A vector type number.')],
        name = "Number Type",
        description = "Which type of number to input",
        default = "int")

    def draw_buttons(self, context, layout):
        layout.prop(self, "numType")
        if self.numType == "int":
            layout.prop(self, "Int")
        elif self.numType == "float":
            layout.prop(self, "Float")
        elif self.numType == "vector":
            layout.prop(self, "Vector")

    def getSettings(self, node):
        node.settings["numType"] = self.numType
        node.settings["Int"] = self.Int
        node.settings["Float"] = self.Float
        node.settings["Vector"] = self.Vector

class GenNoteNode(Node):
    """For keeping the graph well organised"""
    bl_label = 'Note'

    noteText = StringProperty(name="Note Text", default="Enter text here")

    def draw_buttons(self, context, layout):
        layout.label(self.noteText)

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "noteText")

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CrowdMasterGenTreeType'


import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class MyNodeCategory2(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CrowdMasterGenTreeType'

node_categories2 = [
    MyNodeCategory2("input", "Input", items=[
        NodeItem("GroupInputNode"),
        NodeItem("ObjectInputNode"),
        NodeItem("NumberInputNode")
        ]),
    MyNodeCategory2("layout", "Layout", items=[
        NodeItem("GenNoteNode")
        ])
    ]

def register():
    bpy.utils.register_class(CrowdMasterGenTree)
    bpy.utils.register_class(DefaultSocket)
    bpy.utils.register_class(DataInputNode)
    bpy.utils.register_class(DataOutputNode)

    bpy.utils.register_class(GroupInputNode)
    bpy.utils.register_class(ObjectInputNode)
    bpy.utils.register_class(NumberInputNode)
    bpy.utils.register_class(GenNoteNode)

    nodeitems_utils.register_node_categories("CrowdMasterGen_NODES", node_categories2)


def unregister():
    nodeitems_utils.unregister_node_categories("CrowdMasterGen_NODES")

    bpy.utils.unregister_class(CrowdMasterGenTree)
    bpy.utils.unregister_class(DefaultSocket)
    bpy.utils.unregister_class(DataInputNode)
    bpy.utils.unregister_class(DataOutputNode)

    bpy.utils.unregister_class(GroupInputNode)
    bpy.utils.unregister_class(ObjectInputNode)
    bpy.utils.unregister_class(NumberInputNode)
    bpy.utils.unregister_class(GenNoteNode)

if __name__ == "__main__":
    register()
