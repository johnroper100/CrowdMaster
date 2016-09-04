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
        return (0.125, 0.125, 0.575, 1.0)

class TemplateSocket(NodeSocket):
    '''Template node socket type'''
    bl_idname = 'TemplateSocketType'
    bl_label = 'Template Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.125, 0.575, 0.125, 1.0)


class CrowdMasterAGenTreeNode(Node):
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CrowdMasterAGenTreeType'


class GenerateNode(CrowdMasterAGenTreeNode):
    '''The generate node'''
    bl_idname = 'GenerateNodeType'
    bl_label = 'Generate'
    bl_icon = 'SOUND'

    def init(self, context):
        self.inputs.new('TemplateSocketType', "Templates")
        self.inputs[0].link_limit = 4095

    def draw_buttons(self, context, layout):
        layout.scale_y = 1.5
        oper = layout.operator("scene.cm_agent_nodes_generate",
                               icon_value=cicon('add_agents'))
        oper.nodeName = self.name
        oper.nodeTreeName = self.id_data.name

class AddToGroupNode(CrowdMasterAGenTreeNode):
    '''The addToGroup node'''
    bl_idname = 'AddToGroupNodeType'
    bl_label = 'Add To Group'
    bl_icon = 'SOUND'

    groupName = StringProperty()

    def init(self, context):
        self.inputs.new('TemplateSocketType', "Template")
        self.inputs[0].link_limit = 1

        self.outputs.new("TemplateSocketType", "Template")

    def draw_buttons(self, context, layout):
        layout.label("Group name:")
        layout.prop(self, "groupName", text="cm_")

    def getSettings(self):
        return {"groupName": "cm_" + self.groupName}

class ObjectInputNode(CrowdMasterAGenTreeNode):
    '''The object input node'''
    bl_idname = 'ObjectInputNodeType'
    bl_label = 'Object'
    bl_icon = 'SOUND'

    inputObject = StringProperty(name="Object")

    def init(self, context):
        self.outputs.new('GeoSocketType', "Geometry")
        # self.outputs.new('VectorSocketType', "Location")

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "inputObject", context.scene, "objects")

    def getSettings(self):
        return {"inputObject": self.inputObject}

class GroupInputNode(CrowdMasterAGenTreeNode):
    '''The group input node'''
    bl_idname = 'GroupInputNodeType'
    bl_label = 'Group'
    bl_icon = 'SOUND'

    inputGroup = StringProperty(name="Group")

    def init(self, context):
        self.outputs.new('GeoSocketType', "Geometry")

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "inputGroup", bpy.data, "groups")

    def getSettings(self):
        return {"inputGroup": self.inputGroup}

class GeoSwitchNode(CrowdMasterAGenTreeNode):
    '''The geo switch node'''
    bl_idname = 'GeoSwitchNodeType'
    bl_label = 'Geo Switch'
    bl_icon = 'SOUND'

    switchAmount = FloatProperty(name="Amount", default = 0.5, min=0.0, max=1.0, precision=0)

    def init(self, context):
        self.inputs.new('GeoSocketType', "Object 1")
        self.inputs.new('GeoSocketType', "Object 2")
        self.inputs[0].link_limit = 1
        self.inputs[1].link_limit = 1

        self.outputs.new('GeoSocketType', "Objects")

    def draw_buttons(self, context, layout):
        layout.prop(self, "switchAmount")

    def getSettings(self):
        return {"switchAmout": self.switchAmount}

class TemplateSwitchNode(CrowdMasterAGenTreeNode):
    '''The template switch node'''
    bl_idname = 'TemplateSwitchNodeType'
    bl_label = 'Template Switch'
    bl_icon = 'SOUND'

    switchAmount = FloatProperty(name="Amount", default = 0.5, min=0.0, max=1.0, precision=0)

    def init(self, context):
        self.inputs.new('TemplateSocketType', "Template 1")
        self.inputs.new('TemplateSocketType', "Template 2")
        self.inputs[0].link_limit = 1
        self.inputs[1].link_limit = 1

        self.outputs.new('TemplateSocketType', "Templates")

    def draw_buttons(self, context, layout):
        layout.prop(self, "switchAmount")

    def getSettings(self):
        return {"switchAmout": self.switchAmount}

class ParentNode(CrowdMasterAGenTreeNode):
    '''The parent node'''
    bl_idname = 'ParentNodeType'
    bl_label = 'Parent'
    bl_icon = 'SOUND'

    parentTo = StringProperty(name="Parent To (Bone)", description="The bone you want to parent to")

    def init(self, context):
        self.inputs.new('GeoSocketType', "Parent Group")
        self.inputs.new('GeoSocketType', "Child Object")
        self.inputs[0].link_limit = 1
        self.inputs[1].link_limit = 1

        self.outputs.new('GeoSocketType', "Objects")

    def draw_buttons(self, context, layout):
        layout.prop(self, "parentTo")

    def getSettings(self):
        return {"parentTo": self.parentTo}

class TemplateNode(CrowdMasterAGenTreeNode):
    '''The template node'''
    bl_idname = 'TemplateNodeType'
    bl_label = 'Template'
    bl_icon = 'SOUND'

    brainType = StringProperty(name="Brain Type")

    def init(self, context):
        self.inputs.new('GeoSocketType', "Objects")
        self.inputs[0].link_limit = 1

        self.outputs.new('TemplateSocketType', "Template")

    def draw_buttons(self, context, layout):
        layout.prop(self, "brainType")

    def getSettings(self):
        return {"brainType": self.brainType}


def updateRandomNode(self, context):
    if self.minRandRot > self.maxRandRot:
        self.maxRandRot = self.minRandRot
    if self.minRandSz > self.maxRandSz:
        self.maxRandSz = self.minRandSz

class OffsetNode(CrowdMasterAGenTreeNode):
    '''The offset node'''
    bl_idname = 'OffsetNodeType'
    bl_label = 'Offset'
    bl_icon = 'SOUND'

    offset = BoolProperty(name="Overwrite",
                          description="Should the given location be added to the position requested or simply overwrite it?",
                          default=True)
    referenceObject = StringProperty(name="Location Object",
                                     description="An object in the scene from which to get the location")
    locationOffset = FloatVectorProperty(name="Location Offset",
                                         description="Also add this to the location",
                                         default = [0, 0, 0], subtype = "XYZ")
    rotationOffset = FloatVectorProperty(name="Rotation Offset",
                                         description="Also add this to the rotation",
                                         default = [0, 0, 0], subtype = "XYZ")

    def init(self, context):
        self.inputs.new("TemplateSocketType", "Template")
        self.inputs[0].link_limit = 1

        self.outputs.new("TemplateSocketType", "Template")

    def draw_buttons(self, context, layout):
        layout.prop(self, "offset")
        layout.prop_search(self, "referenceObject", context.scene, "objects")
        layout.prop(self, "locationOffset")
        layout.prop(self, "rotationOffset")

    def getSettings(self):
        return {"offset": self.offset,
                "referenceObject": self.referenceObject,
                "locationOffset": self.locationOffset,
                "rotationOffset": self.rotationOffset}

class RandomNode(CrowdMasterAGenTreeNode):
    '''The random node'''
    bl_idname = 'RandomNodeType'
    bl_label = 'Random'
    bl_icon = 'SOUND'

    minRandRot = FloatProperty(name="Min Rand Rotation",
                               description="The minimum random rotation in the Z axis for each agent.",
                               default = -10, min=-360.0, max=360,
                               update=updateRandomNode)
    maxRandRot = FloatProperty(name="Max Rand Rotation",
                               description="The maximum random rotation in the Z axis for each agent.",
                               default = 10, min=-360, max=360.0,
                               update=updateRandomNode)

    minRandSz = FloatProperty(name="Min Rand Scale",
                              description="The minimum random scale for each agent.",
                              default = 1.0, min=0, precision=3,
                              update=updateRandomNode)
    maxRandSz = FloatProperty(name="Max Rand Scale",
                              description="The maximum random scale for each agent.",
                              default = 1.0, min=0, precision=3,
                              update=updateRandomNode)

    def init(self, context):
        self.inputs.new("TemplateSocketType", "Template")
        self.inputs[0].link_limit = 1

        self.outputs.new('TemplateSocketType', "Template")

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(self, "minRandRot")
        row.prop(self, "maxRandRot")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(self, "minRandSz")
        row.prop(self, "maxRandSz")

    def getSettings(self):
        return {"maxRandRot": self.maxRandRot,
                "minRandRot": self.minRandRot,
                "maxRandSz": self.maxRandSz,
                "minRandSz": self.minRandSz}

class RandomPositionNode(CrowdMasterAGenTreeNode):
    '''The random positioing node'''
    bl_idname = 'RandomPositionNodeType'
    bl_label = 'Random Positioning'
    bl_icon = 'SOUND'

    noToPlace = IntProperty(name="Number Of Agents",
                            description="The number of agents to place",
                            default=1)

    locationType = EnumProperty(
        items = [("radius", "Radius", "Within radius of requested")],
        name = "Location Type",
        description = "Which location type to use",
        default = "radius"
    )

    radius = FloatProperty(name="Radius",
                           description="The distance from the requested position to place",
                           default=5, min=0)

    MaxX = FloatProperty(name="Max X",
                         description="The maximum distance in the X direction around the center point where the agents will be randomly spawned.",
                         default = 50.0)
    MaxY = FloatProperty(name="Max Y",
                         description="The maximum distance in the Y direction around the center point where the agents will be randomly spawned.",
                         default = 50.0)
    MinX = FloatProperty(name="Min X",
                         description="The minimum distance in the X direction around the center point where the agents will be randomly spawned.",
                         default = -50.0)
    MinY = FloatProperty(name="Min Y",
                         description="The minimum distance in the Y direction around the center point where the agents will be randomly spawned.",
                         default = -50.0)

    def init(self, context):
        self.inputs.new('TemplateSocketType', "Template")
        self.inputs[0].link_limit = 1

        self.outputs.new('TemplateSocketType', "Template")

    def draw_buttons(self, context, layout):
        layout.prop(self, "noToPlace")
        layout.prop(self, "locationType")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        if self.locationType == "radius":
            row.prop(self, "radius")
        elif self.locationType == "vector":
            row.prop(self, "MaxX")
            row.prop(self, "MaxY")
        elif self.locationType == "scene":
            row.prop(self, "MinX")
            row.prop(self, "MaxX")
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.prop(self, "MinY")
            row.prop(self, "MaxY")

    def getSettings(self):
        return {"locationType": self.locationType,
                "MaxX": self.MaxX,
                "MaxY": self.MaxY,
                "MinX": self.MinX,
                "MinY": self.MinY,
                "noToPlace": self.noToPlace,
                "radius": self.radius}

class FormationPositionNode(CrowdMasterAGenTreeNode):
    '''The formation positioing node'''
    bl_idname = 'FormationPositionNodeType'
    bl_label = 'Formation Positioning'
    bl_icon = 'SOUND'

    noToPlace = IntProperty(name="Number Of Agents",
                            description="The number of agents to place",
                            default=1, min=1)
    ArrayRows = IntProperty(name="Rows",
                            description="The number of rows in the array.",
                            default=1, min=1)
    ArrayRowMargin = FloatProperty(name="Row Margin",
                                   description="The margin between each row.")
    ArrayColumnMargin = FloatProperty(name="Column Margin",
                                      description="The margin between each column.")

    def init(self, context):
        self.inputs.new('TemplateSocketType', "Template")
        self.inputs[0].link_limit = 1

        self.outputs.new('TemplateSocketType', "Template")

    def draw_buttons(self, context, layout):
        layout.prop(self, "noToPlace")
        row = layout.row()
        row.prop(self, "ArrayRows")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(self, "ArrayRowMargin")
        row.prop(self, "ArrayColumnMargin")

    def getSettings(self):
        return {"noToPlace": self.noToPlace,
                "ArrayRows": self.ArrayRows,
                "ArrayRowMargin": self.ArrayRowMargin,
                "ArrayColumnMargin": self.ArrayColumnMargin}

class TargetPositionNode(CrowdMasterAGenTreeNode):
    '''The target positioing node'''
    bl_idname = 'TargetPositionNodeType'
    bl_label = 'Target Positioning'
    bl_icon = 'SOUND'

    targetType = EnumProperty(
        items = [("object", "Object", "Use the locations of each object in a group"),
                 ("vertex", "Vertex", "Use the location of each vertex on an object")],
        name = "Target Type",
        description = "Which target type to use",
        default = "object"
    )

    targetObject = StringProperty(name="Target Object",
                                  description="Placement will be on the vertices of this object")
    targetGroups = StringProperty(name="Target Objects",
                                  description="Placement will be at the location of each object")
    overwritePosition = BoolProperty(name="Overwrite position",
                                     description="Should this node use the global position of the vertices or the position of the vertices relative to the origin",
                                     default=True)

    def init(self, context):
        self.inputs.new('TemplateSocketType', "Template")
        self.inputs[0].link_limit = 1

        self.outputs.new('TemplateSocketType', "Template")

    def draw_buttons(self, context, layout):
        layout.prop(self, "targetType")
        if self.targetType == "object":
            layout.prop_search(self, "targetGroups", bpy.data, "groups")
        elif self.targetType == "vertex":
            layout.prop_search(self, "targetObject", context.scene, "objects")
        layout.prop(self, "overwritePosition")

    def getSettings(self):
        return {"targetType": self.targetType,
                "targetObject": self.targetObject,
                "targetGroups": self.targetGroups,
                "overwritePosition": self.overwritePosition}

class ObstacleNode(CrowdMasterAGenTreeNode):
    '''The obstacle node'''
    bl_idname = 'ObstacleNodeType'
    bl_label = 'Obstacle'
    bl_icon = 'SOUND'

    obstacleGroup = StringProperty(name="Obstacles")
    margin = FloatProperty(name="Margin", precision=3)

    def init(self, context):
        self.inputs.new('TemplateSocketType', "Template")
        self.inputs[0].link_limit = 1

        self.outputs.new('TemplateSocketType', "Template")

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "obstacleGroup", bpy.data, "groups")
        layout.prop(self, "margin")

    def getSettings(self):
        return {"obstacleGroup": self.obstacleGroup,
                "margin": self.margin}


class NoteNode(CrowdMasterAGenTreeNode):
    """For keeping the graph well organised"""
    bl_label = 'Note'

    noteText = StringProperty(default="Enter text here")

    def draw_buttons(self, context, layout):
        layout.label(self.noteText)

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "noteText")


import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class CrowdMasterAGenCategories(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CrowdMasterAGenTreeType'

agen_node_categories = [
    CrowdMasterAGenCategories("geometry", "Geometry", items=[
        NodeItem("ObjectInputNodeType"),
        NodeItem("GroupInputNodeType"),
        NodeItem("GeoSwitchNodeType", label="Switch"),
        NodeItem("ParentNodeType")
        ]),
    CrowdMasterAGenCategories("template", "Template", items=[
        NodeItem("TemplateNodeType"),
        NodeItem("TemplateSwitchNodeType", label="Switch"),
        NodeItem("RandomNodeType"),
        ]),
    CrowdMasterAGenCategories("position", "Positioning", items=[
        NodeItem("RandomPositionNodeType", label="Random"),
        NodeItem("FormationPositionNodeType", label="Formation"),
        NodeItem("TargetPositionNodeType", label="Target"),
        NodeItem("ObstacleNodeType"),
        NodeItem("OffsetNodeType"),
        ]),
    CrowdMasterAGenCategories("other", "Other", items=[
        NodeItem("GenerateNodeType"),
        NodeItem("AddToGroupNodeType")
        ]),
    CrowdMasterAGenCategories("layout", "Layout", items=[
        NodeItem("NodeFrame"),
        NodeItem("NodeReroute"),
        NodeItem("NoteNode")
    ])
    ]

def register():
    bpy.utils.register_class(CrowdMasterAGenTree)
    bpy.utils.register_class(GeoSocket)
    bpy.utils.register_class(TemplateSocket)

    bpy.utils.register_class(GenerateNode)
    bpy.utils.register_class(AddToGroupNode)

    bpy.utils.register_class(ObjectInputNode)
    bpy.utils.register_class(GroupInputNode)
    bpy.utils.register_class(GeoSwitchNode)
    bpy.utils.register_class(TemplateSwitchNode)
    bpy.utils.register_class(ParentNode)
    bpy.utils.register_class(TemplateNode)
    bpy.utils.register_class(OffsetNode)
    bpy.utils.register_class(RandomNode)
    bpy.utils.register_class(RandomPositionNode)
    bpy.utils.register_class(FormationPositionNode)
    bpy.utils.register_class(TargetPositionNode)
    bpy.utils.register_class(ObstacleNode)

    bpy.utils.register_class(NoteNode)

    nodeitems_utils.register_node_categories("AGEN_CUSTOM_NODES", agen_node_categories)

def unregister():
    nodeitems_utils.unregister_node_categories("AGEN_CUSTOM_NODES")

    bpy.utils.unregister_class(CrowdMasterAGenTree)
    bpy.utils.unregister_class(GeoSocket)
    bpy.utils.unregister_class(TemplateSocket)

    bpy.utils.unregister_class(GenerateNode)
    bpy.utils.unregister_class(AddToGroupNode)

    bpy.utils.unregister_class(ObjectInputNode)
    bpy.utils.unregister_class(GroupInputNode)
    bpy.utils.unregister_class(GeoSwitchNode)
    bpy.utils.unregister_class(TemplateSwitchNode)
    bpy.utils.unregister_class(ParentNode)
    bpy.utils.unregister_class(TemplateNode)
    bpy.utils.unregister_class(OffsetNode)
    bpy.utils.unregister_class(RandomNode)
    bpy.utils.unregister_class(RandomPositionNode)
    bpy.utils.unregister_class(FormationPositionNode)
    bpy.utils.unregister_class(TargetPositionNode)
    bpy.utils.unregister_class(ObstacleNode)

    bpy.utils.unregister_class(NoteNode)

if __name__ == "__main__":
    register()
