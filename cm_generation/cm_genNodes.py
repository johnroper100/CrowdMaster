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
        if self.is_linked:
            return (0.0, 0.0, 0.2, 0.9)
        else:
            return (0.0, 0.0, 0.2, 0.5)

class TemplateSocket(NodeSocket):
    '''Template node socket type'''
    bl_idname = 'TemplateSocketType'
    bl_label = 'Template Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        if self.is_linked:
            return (0.8, 0.5, 0.0, 0.9)
        else:
            return (0.8, 0.5, 0.0, 0.5)
        

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

class ObjectInputNode(Node, CrowdMasterAGenTreeNode):
    '''The object input node'''
    bl_idname = 'ObjectInputNodeType'
    bl_label = 'Object'
    bl_icon = 'SOUND'

    inputObject = StringProperty(name="Object")

    def init(self, context):
        self.outputs.new('GeoSocketType', "Geometry")
    
    def draw_buttons(self, context, layout):
        layout.prop_search(self, "inputObject", context.scene, "objects")

class GroupInputNode(Node, CrowdMasterAGenTreeNode):
    '''The group input node'''
    bl_idname = 'GroupInputNodeType'
    bl_label = 'Group'
    bl_icon = 'SOUND'

    inputGroup = StringProperty(name="Group")

    def init(self, context):
        self.outputs.new('GeoSocketType', "Geometry")
    
    def draw_buttons(self, context, layout):
        layout.prop_search(self, "inputGroup", bpy.data, "groups")

class GeoSwitchNode(Node, CrowdMasterAGenTreeNode):
    '''The geo switch node'''
    bl_idname = 'GeoSwitchNodeType'
    bl_label = 'Geo Switch'
    bl_icon = 'SOUND'

    switchAmount = FloatProperty(name="Amount", default = 0.5, min=0.0, max=1.0, precision=0)

    def init(self, context):
        self.inputs.new('GeoSocketType', "Object 1")
        self.inputs.new('GeoSocketType', "Object 2")
        
        self.outputs.new('GeoSocketType', "Objects")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "switchAmount")

class TemplateSwitchNode(Node, CrowdMasterAGenTreeNode):
    '''The template switch node'''
    bl_idname = 'TemplateSwitchNodeType'
    bl_label = 'Template Switch'
    bl_icon = 'SOUND'

    switchAmount = FloatProperty(name="Amount", default = 0.5, min=0.0, max=1.0, precision=0)

    def init(self, context):
        self.inputs.new('TemplateSocketType', "Template 1")
        self.inputs.new('TemplateSocketType', "Template 2")
        
        self.outputs.new('TemplateSocketType', "Templates")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "switchAmount")

class ParentNode(Node, CrowdMasterAGenTreeNode):
    '''The parent node'''
    bl_idname = 'ParentNodeType'
    bl_label = 'Parent'
    bl_icon = 'SOUND'
    
    parentTo = StringProperty(name="Parent To")

    def init(self, context):
        self.inputs.new('GeoSocketType', "Parent Group")
        self.inputs.new('GeoSocketType', "Child Object")
        
        self.outputs.new('GeoSocketType', "Objects")
    
    def draw_buttons(self, context, layout):
        layout.prop_search(self, "parentTo", context.scene, "objects")

class TemplateNode(Node, CrowdMasterAGenTreeNode):
    '''The template node'''
    bl_idname = 'TemplateNodeType'
    bl_label = 'Template'
    bl_icon = 'SOUND'
    
    brainType = EnumProperty(
        items = [('1', '1', 'Brain type 1'),
                 ('2', '2', 'Brain type 2')],
        name = "Brain Type",
        description = "Which brain type to use",
        default = "1")

    def init(self, context):
        self.inputs.new('GeoSocketType', "Objects")
        
        self.outputs.new('TemplateSocketType', "Template")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "brainType")

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class CrowdMasterAGenCategories(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CrowdMasterAGenTreeType'

agen_node_categories = [
    CrowdMasterAGenCategories("output", "Output", items=[
        NodeItem("GenerateNodeType"),
        ]),
    CrowdMasterAGenCategories("geometry", "Geometry", items=[
        NodeItem("ObjectInputNodeType"),
        NodeItem("GroupInputNodeType"),
        NodeItem("GeoSwitchNodeType", label="Switch"),
        NodeItem("ParentNodeType"),
        ]),
    CrowdMasterAGenCategories("template", "Template", items=[
        NodeItem("TemplateNodeType"),
        NodeItem("TemplateSwitchNodeType", label="Switch"),
        ]),
    ]

def register():
    bpy.utils.register_class(CrowdMasterAGenTree)
    bpy.utils.register_class(GeoSocket)
    bpy.utils.register_class(TemplateSocket)
    bpy.utils.register_class(ObjectSocket)
    bpy.utils.register_class(GroupSocket)

    bpy.utils.register_class(GenerateNode)
    bpy.utils.register_class(ObjectInputNode)
    bpy.utils.register_class(GroupInputNode)
    bpy.utils.register_class(GeoSwitchNode)
    bpy.utils.register_class(TemplateSwitchNode)
    bpy.utils.register_class(ParentNode)
    bpy.utils.register_class(TemplateNode)

    nodeitems_utils.register_node_categories("AGEN_CUSTOM_NODES", agen_node_categories)

def unregister():
    nodeitems_utils.unregister_node_categories("AGEN_CUSTOM_NODES")

    bpy.utils.unregister_class(CrowdMasterAGenTree)
    bpy.utils.unregister_class(GeoSocket)
    bpy.utils.unregister_class(TemplateSocket)
    bpy.utils.unregister_class(ObjectSocket)
    bpy.utils.unregister_class(GroupSocket)

    bpy.utils.unregister_class(ObjectInputNode)
    bpy.utils.unregister_class(GroupInputNode)
    bpy.utils.unregister_class(GeoSwitchNode)
    bpy.utils.unregister_class(TemplateSwitchNode)
    bpy.utils.unregister_class(ParentNode)
    bpy.utils.unregister_class(TemplateNode)

if __name__ == "__main__":
    register()
