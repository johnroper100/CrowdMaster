import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty
from .. icon_load import cicon

class CrowdMasterGenTree(NodeTree):
    """The node tree that contains the CrowdMaster agent gen nodes"""
    bl_idname = 'CrowdMasterGenTreeType'
    bl_label = 'CrowdMaster Agent Generation'
    bl_icon = 'MOD_ARRAY'

class TemplateSocket(NodeSocket):
    """Template socket"""
    bl_idname = 'TemplateSocketType'
    bl_label = 'Template CrowdMaster Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        if self.is_linked:
            return (0.8, 0.515, 0.0, 0.7)
        else:
            return (0.8, 0.515, 0.0, 0.5)

class GeoTemplateSocket(NodeSocket):
    """GeoTemplate socket"""
    bl_idname = 'GeoTemplateSocketType'
    bl_label = 'GeoTemplate CrowdMaster Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

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
        self.inputs.new('GroupInputSocket', "Input")
        self.inputs[0].link_limit = 4095

    def getSettings(self, node):
        pass

class DataOutputNode(CrowdMasterGenNode):
    bl_label = 'Data output super class'

    def init(self, context):
        self.outputs.new('GeoTemplateSocket', "Output")

    def getSettings(self, node):
        pass

class DataThroughNode(CrowdMasterGenNode):
    bl_label = 'Data through super class'

    def init(self, context):
        self.inputs.new('GroupInputSocket', "Input")
        self.inputs[0].link_limit = 4095

        self.outputs.new('GeoTemplateSocket', "Output")

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

class TemplateNode(DataThroughNode):
    """CrowdMaster template node"""
    bl_label = "Template"

    brainType = EnumProperty(
        items = [('int', 'Integer', 'An integer type number.'), 
                 ('float', 'Float', 'A float type number.'),
                 ('vector', 'Vector', 'A vector type number.')],
        name = "Number Type",
        description = "Which type of number to input",
        default = "int")

    def draw_buttons(self, context, layout):
        layout.prop(self, "brainType")

    def getSettings(self, node):
        node.settings["brainType"] = self.brainType

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

class GenOutputNode(DataInputNode):
    """CrowdMaster generation output node"""
    bl_label = "Generate"

    def draw_buttons(self, context, layout):
        layout.scale_y = 1.5		
        layout.operator("scene.cm_gen_agents", icon_value=cicon('plus_yellow'))

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
    MyNodeCategory2("output", "Output", items=[
        NodeItem("GenOutputNode")
        ]),
    MyNodeCategory2("through", "Through", items=[
        NodeItem("TemplateNode")
        ]),
    MyNodeCategory2("layout", "Layout", items=[
        NodeItem("GenNoteNode")
        ])
    ]

def register():
    bpy.utils.register_class(CrowdMasterGenTree)
    bpy.utils.register_class(TemplateSocket)
    bpy.utils.register_class(GeoTemplateSocket)
    bpy.utils.register_class(DataInputNode)
    bpy.utils.register_class(DataOutputNode)
    bpy.utils.register_class(DataThroughNode)

    bpy.utils.register_class(GroupInputNode)
    bpy.utils.register_class(ObjectInputNode)
    bpy.utils.register_class(TemplateNode)
    bpy.utils.register_class(NumberInputNode)
    bpy.utils.register_class(GenNoteNode)
    bpy.utils.register_class(GenOutputNode)

    nodeitems_utils.register_node_categories("CrowdMasterGen_NODES", node_categories2)


def unregister():
    nodeitems_utils.unregister_node_categories("CrowdMasterGen_NODES")

    bpy.utils.unregister_class(CrowdMasterGenTree)
    bpy.utils.unregister_class(TemplateSocket)
    bpy.utils.unregister_class(GeoTemplateSocket)
    bpy.utils.unregister_class(DataInputNode)
    bpy.utils.unregister_class(DataOutputNode)
    bpy.utils.unregister_class(DataThroughNode)

    bpy.utils.unregister_class(GroupInputNode)
    bpy.utils.unregister_class(ObjectInputNode)
    bpy.utils.unregister_class(TemplateNode)
    bpy.utils.unregister_class(NumberInputNode)
    bpy.utils.unregister_class(GenNoteNode)
    bpy.utils.unregister_class(GenOutputNode)

if __name__ == "__main__":
    register()