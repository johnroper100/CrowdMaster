import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.props import EnumProperty, IntProperty


class CrowdMasterTree(NodeTree):
    """New type of node tree to contain the CrowdMaster nodes"""
    bl_idname = 'CrowdMasterTreeType'
    bl_label = 'CrowdMaster'
    bl_icon = 'MOD_REMESH'


class DefaultSocket(NodeSocket):
    # Description string
    """Default socket"""
    # If not explicitly defined, the python class name is used.
    bl_idname = 'DefaultSocketType'
    # Label for nice name display
    bl_label = 'Default Node Socket'

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
        return (0.0, 0.0, 0.0, 0.4)


class StateSocket(NodeSocket):
    """Socket used for state tree transitions"""
    bl_idname = 'StateSocketType'
    bl_label = 'State Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.0, 0.0, 0.5, 1.0)


class DependanceSocket(NodeSocket):
    """Socket used for state tree transitions"""
    bl_idname = 'DependanceSocketType'
    bl_label = 'Dependance Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.5, 0.0, 0.0, 1.0)


class CrowdMasterNode(Node):
    """CrowdMaster nodes superclass"""
    # bl_idname = 'CustomNodeType'  # Class name used if not defined
    # Label for nice name display
    bl_label = 'Super class'
    # bl_icon = 'SOUND'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CrowdMasterTreeType'


class LogicNode(CrowdMasterNode):
    bl_label = 'Logic super class'

    def init(self, context):
        self.inputs.new("DefaultSocketType", "Input")
        self.inputs[0].link_limit = 4095

        self.outputs.new('DefaultSocketType', "Output")
        self.outputs.new("DependanceSocketType", "Dependant")

    def getSettings(self, node):
        pass


# ============ End of super classes ============


class InputNode(LogicNode):
    """CrowdMaster input node"""
    bl_label = "Input"

    Input = StringProperty(default="Noise.random")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Input")
        # layout.prop(self, "fillOutput")

    def getSettings(self, node):
        node.settings["Input"] = self.Input


def update_properties(self, context):
    """Keeps the values in the graph node in the correct order"""
    if self.UpperZero < self.UpperOne:
        self.UpperOne = self.UpperZero
    if self.UpperOne < self.LowerOne:
        self.LowerOne = self.UpperOne
    if self.LowerOne < self.LowerZero:
        self.LowerZero = self.LowerOne


class GraphNode(LogicNode):
    """CrowdMaster graph node"""
    bl_label = "Graph"

    CurveType = EnumProperty(items=[("RBF", "RBF", "", 1),
                                    ("RANGE", "Range", "", 2)
                                    ])

    LowerZero = FloatProperty(default=-1.0, update=update_properties)
    LowerOne = FloatProperty(default=-0.5, update=update_properties)
    UpperOne = FloatProperty(default=0.5, update=update_properties)
    UpperZero = FloatProperty(default=1.0, update=update_properties)

    RBFMiddle = FloatProperty(default=0.0)
    RBFTenPP = FloatProperty(default=0.25)  # Ten percent point

    def draw_buttons(self, context, layout):
        layout.prop(self, "CurveType", expand=True)
        if self.CurveType == "RBF":
            layout.prop(self, "RBFMiddle")
            layout.prop(self, "RBFTenPP")
        elif self.CurveType == "RANGE":
            layout.prop(self, "LowerZero")
            layout.prop(self, "LowerOne")
            layout.prop(self, "UpperOne")
            layout.prop(self, "UpperZero")

    def getSettings(self, node):
        node.settings["CurveType"] = self.CurveType
        node.settings["LowerZero"] = self.LowerZero
        node.settings["LowerOne"] = self.LowerOne
        node.settings["UpperOne"] = self.UpperOne
        node.settings["UpperZero"] = self.UpperZero
        node.settings["RBFMiddle"] = self.RBFMiddle
        node.settings["RBFTenPP"] = self.RBFTenPP


class AndNode(LogicNode):
    """CrowdMaster and node"""
    bl_label = "And"

    SingleOutput = BoolProperty(default=False)
    IncludeAll = BoolProperty(default=True)

    def draw_buttons(self, context, layout):
        layout.prop(self, "SingleOutput")
        layout.prop(self, "IncludeAll")

    def getSettings(self, node):
        node.settings["SingleOutput"] = self.SingleOutput
        node.settings["IncludeAll"] = self.IncludeAll


class OrNode(LogicNode):
    """CrowdMaster or node"""
    bl_label = "Or"

    SingleOutput = BoolProperty(default=True)

    def draw_buttons(self, context, layout):
        layout.prop(self, "SingleOutput")

    def getSettings(self, node):
        node.settings["SingleOutput"] = self.SingleOutput


class StrongNode(LogicNode):
    """CrowdMaster Strong node. Makes 1's and 0's stronger"""
    bl_label = "Strong"


class WeakNode(LogicNode):
    """CrowdMaster Weak node. Relaxes 1's and 0's"""
    bl_label = "Weak"


class QueryTagNode(LogicNode):
    """CrowdMaster Query Tag node"""
    bl_label = "Query Tag"

    Tag = StringProperty(default="default")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Tag")

    def getSettings(self, node):
        node.settings["Tag"] = self.Tag


class SetTagNode(LogicNode):
    """CrowdMaster Set Tag node"""
    bl_label = "Set Tag"

    Tag = StringProperty(default="default")
    UseThreshold = BoolProperty(default=True)
    Threshold = FloatProperty(default=0.5)
    Action = EnumProperty(items=[("ADD", "Add", "", 1),
                                 ("REMOVE", "Remove", "", 2)
                                 ])

    def draw_buttons(self, context, layout):
        layout.prop(self, "Tag")
        layout.prop(self, "UseThreshold")
        if self.UseThreshold:
            layout.prop(self, "Threshold")
        layout.prop(self, "Action")

    def getSettings(self, node):
        node.settings["Tag"] = self.Tag
        node.settings["UseThreshold"] = self.UseThreshold
        node.settings["Threshold"] = self.Threshold
        node.settings["Action"] = self.Action


class VariableNode(LogicNode):
    """CrowdMaster Variable node"""
    bl_label = "Variable"

    Variable = StringProperty(default="None")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Variable")

    def getSettings(self, node):
        node.settings["Variable"] = self.Variable


class MapNode(LogicNode):
    """CrowdMaster Map node"""
    bl_label = "Map"

    LowerInput = FloatProperty(default=0.0)
    UpperInput = FloatProperty(default=1.0)
    LowerOutput = FloatProperty(default=0.0)
    UpperOutput = FloatProperty(default=2.0)

    def draw_buttons(self, context, layout):
        layout.prop(self, "LowerInput")
        layout.prop(self, "UpperInput")
        layout.prop(self, "LowerOutput")
        layout.prop(self, "UpperOutput")

    def getSettings(self, node):
        node.settings["LowerInput"] = self.LowerInput
        node.settings["UpperInput"] = self.UpperInput
        node.settings["LowerOutput"] = self.LowerOutput
        node.settings["UpperOutput"] = self.UpperOutput


class OutputNode(LogicNode):
    """CrowdMaster Output node"""
    bl_label = "Output"

    Output = EnumProperty(items=[("rz", "rz", "", 3),
                                 ("rx", "rx", "", 1),
                                 ("ry", "ry", "", 2),
                                 ("px", "px", "", 4),
                                 ("py", "py", "", 5),
                                 ("pz", "pz", "", 6)
                                 ])
    MultiInputType = EnumProperty(items=[("AVERAGE", "Average", "", 1),
                                         ("MAX", "Max", "", 2),
                                         ("SIZEAVERAGE", "Size Average", "", 3)
                                         ])

    def draw_buttons(self, context, layout):
        layout.prop(self, "Output")
        layout.prop(self, "MultiInputType")

    def getSettings(self, node):
        node.settings["Output"] = self.Output
        node.settings["MultiInputType"] = self.MultiInputType


class EventNode(LogicNode):
    """CrowdMaster Event node"""
    bl_label = "Event"

    EventName = bpy.props.StringProperty(default="default")

    def draw_buttons(self, context, layout):
        layout.prop(self, "EventName")

    def getSettings(self, node):
        node.settings["EventName"] = self.EventName


class PythonNode(LogicNode):
    """CrowdMaster Python node"""
    bl_label = "Python"

    Expression = bpy.props.StringProperty(default="output = Noise.random")
    # This really needs to link to a text block

    def draw_buttons(self, context, layout):
        layout.prop(self, "Expression")

    def getSettings(self, node):
        node.settings["Expression"] = self.Expression


class PrintNode(LogicNode):
    """CrowdMaster Print Node"""
    bl_label = "Print"

    Label = bpy.props.StringProperty(default="")
    # PrintSelected = bpy.props.BoolProperty(default=True)  # Not implemented

    def draw_buttons(self, context, layout):
        layout.prop(self, "Label")

    def getSettings(self, node):
        node.settings["Label"] = self.Label


class PriorityNode(LogicNode):
    """CrowdMaster Priority node"""
    bl_label = "Priority"

    defaultValue = bpy.props.FloatProperty(default=0)

    def init(self, context):
        self.inputs.new("DefaultSocketType", "Values0")
        self.inputs.new("DefaultSocketType", "Priority0")

        self.outputs.new('DefaultSocketType', "Output")
        self.outputs.new("DependanceSocketType", "Dependant")

    def update(self):
        if self.inputs[-1].is_linked and self.inputs[-2].is_linked:
            n = len(self.inputs)//2
            self.inputs.new("DefaultSocketType", "Values{}".format(n))
            self.inputs.new("DefaultSocketType", "Priority{}".format(n))

            self.inputs[-1].link_limit = 1
            self.inputs[-2].link_limit = 1
        elif len(self.inputs) > 2 and not (self.inputs[-1].is_linked or
                                           self.inputs[-2].is_linked):
            while (not self.inputs[-4].is_linked and
                   not self.inputs[-3].is_linked and len(self.inputs) > 2):
                self.inputs.remove(self.inputs[-1])
                self.inputs.remove(self.inputs[-1])

    def draw_buttons(self, context, layout):
        layout.prop(self, "defaultValue")

    def getSettings(self, node):
        node.settings["defaultValue"] = self.defaultValue

# ============ Start of state nodes ============


class StateNode(CrowdMasterNode):
    bl_label = 'State super class'

    def init(self, context):
        self.inputs.new("StateSocketType", "From")
        self.inputs["From"].link_limit = 4095
        self.inputs.new("DefaultSocketType", "Value")
        self.inputs["Value"].link_limit = 4095
        self.inputs.new("DependanceSocketType", "Dependant")
        self.inputs["Dependant"].link_limit = 4095

        self.outputs.new("StateSocketType", "To")
        self.outputs["To"].link_limit = 4095


# ====== End of Super class ======


class StartState(StateNode):
    """CrowdMaster Start State"""
    bl_label = "Start"

    def init(self, context):
        self.inputs.new("DependanceSocketType", "Dependant")
        self.inputs["Dependant"].link_limit = 4095

        self.outputs.new("StateSocketType", "To")
        self.outputs["To"].link_limit = 4095

    def getSettings(self, item):
        return


class ActionState(StateNode):
    """CrowdMaster Action State"""
    bl_label = "Action"

    stateLength = IntProperty(default=1)
    cycleState = BoolProperty(default=False)
    actionName = StringProperty(default="")
    useValueOfSpeed = BoolProperty(default=True)

    def init(self, context):
        StateNode.init(self, context)

    def getSettings(self, item):
        val = self.inputs['Value']
        item.settings["ValueFilter"] = val.filterProperty
        item.settings["ValueDefault"] = val.defaultValueProperty
        item.length = self.stateLength
        item.cycleState = self.cycleState
        item.actionName = self.actionName
        item.useValueOfSpeed = self.useValueOfSpeed

    def draw_buttons(self, context, layout):
        layout.prop(self, "stateLength")
        layout.prop(self, "cycleState")
        row = layout.row()
        row.prop(self, "actionName", text="")
        row.prop(self, "useValueOfSpeed", text="")


class NoteNode(Node):
    """For keeping the graph well organised"""
    bl_label = 'Note Node'

    noteText = StringProperty(default="Enter text here")

    def draw_buttons(self, context, layout):
        layout.label(self.noteText)

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "noteText")

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CrowdMasterTreeType'


import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CrowdMasterTreeType'

# all categories in a list
node_categories = [
    MyNodeCategory("INPUT", "Input", items=[
        NodeItem("InputNode")
        ]),
    MyNodeCategory("OUTPUT", "Output", items=[
        NodeItem("OutputNode")
        ]),
    MyNodeCategory("BASIC", "Basic", items=[
        NodeItem("GraphNode"),
        NodeItem("AndNode"),
        NodeItem("OrNode"),
        NodeItem("StrongNode"),
        NodeItem("WeakNode"),
        NodeItem("MapNode"),
        NodeItem("PriorityNode")
        ]),
    MyNodeCategory("STATE", "State", items=[
        NodeItem("StartState"),
        NodeItem("ActionState")
        ]),
    MyNodeCategory("OTHER", "Other", items=[
        NodeItem("QueryTagNode"),
        NodeItem("SetTagNode"),
        NodeItem("VariableNode"),
        NodeItem("EventNode")
        ]),
    MyNodeCategory("DEVELOPER", "Developer", items=[
        NodeItem("PythonNode"),
        NodeItem("PrintNode")
        ]),
    MyNodeCategory("LAYOUT", "Layout", items=[
        NodeItem("NodeFrame"),
        NodeItem("NodeReroute"),
        NodeItem("NoteNode")
        ])
    ]


def register():
    bpy.utils.register_class(CrowdMasterTree)
    bpy.utils.register_class(DefaultSocket)
    bpy.utils.register_class(StateSocket)
    bpy.utils.register_class(DependanceSocket)
    bpy.utils.register_class(LogicNode)
    bpy.utils.register_class(StateNode)

    bpy.utils.register_class(InputNode)
    bpy.utils.register_class(GraphNode)
    bpy.utils.register_class(AndNode)
    bpy.utils.register_class(OrNode)
    bpy.utils.register_class(StrongNode)
    bpy.utils.register_class(WeakNode)
    bpy.utils.register_class(QueryTagNode)
    bpy.utils.register_class(SetTagNode)
    bpy.utils.register_class(VariableNode)
    bpy.utils.register_class(MapNode)
    bpy.utils.register_class(OutputNode)
    bpy.utils.register_class(PriorityNode)
    bpy.utils.register_class(EventNode)
    bpy.utils.register_class(PythonNode)
    bpy.utils.register_class(PrintNode)

    bpy.utils.register_class(StartState)
    bpy.utils.register_class(ActionState)

    bpy.utils.register_class(NoteNode)

    nodeitems_utils.register_node_categories("CrowdMaster_NODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("CrowdMaster_NODES")

    bpy.utils.unregister_class(CrowdMasterTree)
    bpy.utils.unregister_class(DefaultSocket)
    bpy.utils.unregister_class(StateSocket)
    bpy.utils.unregister_class(DependanceSocket)
    bpy.utils.unregister_class(LogicNode)
    bpy.utils.unregister_class(StateNode)

    bpy.utils.unregister_class(InputNode)
    bpy.utils.unregister_class(GraphNode)
    bpy.utils.unregister_class(AndNode)
    bpy.utils.unregister_class(OrNode)
    bpy.utils.unregister_class(StrongNode)
    bpy.utils.unregister_class(WeakNode)
    bpy.utils.unregister_class(QueryTagNode)
    bpy.utils.unregister_class(SetTagNode)
    bpy.utils.unregister_class(VariableNode)
    bpy.utils.unregister_class(MapNode)
    bpy.utils.unregister_class(OutputNode)
    bpy.utils.unregister_class(PriorityNode)
    bpy.utils.unregister_class(EventNode)
    bpy.utils.unregister_class(PythonNode)
    bpy.utils.unregister_class(PrintNode)

    bpy.utils.unregister_class(StartState)
    bpy.utils.unregister_class(ActionState)

    bpy.utils.unregister_class(NoteNode)

if __name__ == "__main__":
    register()
