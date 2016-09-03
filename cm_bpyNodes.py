import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty


class CrowdMasterTree(NodeTree):
    """The node tree that contains the CrowdMaster nodes"""
    bl_idname = 'CrowdMasterTreeType'
    bl_label = 'CrowdMaster Agent Simulation'
    bl_icon = 'OUTLINER_OB_ARMATURE'

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


class StateSocket(NodeSocket):
    """Socket used for state tree transitions"""
    bl_idname = 'StateSocketType'
    bl_label = 'CrowdMaster State Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.0, 0.0, 0.5, 1.0)


class DependanceSocket(NodeSocket):
    """Socket used for state tree transitions"""
    bl_idname = 'DependanceSocketType'
    bl_label = 'CrowdMaster Dependance Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.8, 0.5, 0.0, 0.9)


class CrowdMasterNode(Node):
    """CrowdMaster node superclass"""
    bl_label = 'Super class'

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

    Input = StringProperty(name="Input", default="Noise.random")

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

    Multiply = FloatProperty(name="Multiply", description="Multiply the outputted value by this number", default=1.0)
    
    CurveType = EnumProperty(name="Curve Type", 
                             items=[("RBF", "RBF", "", 1),
                                    ("RANGE", "Range", "", 2)])

    LowerZero = FloatProperty(name="Lower Zero", default=-1.0, update=update_properties)
    LowerOne = FloatProperty(name="Lower One", default=-0.5, update=update_properties)
    UpperOne = FloatProperty(name="Upper One", default=0.5, update=update_properties)
    UpperZero = FloatProperty(name="Upper Zero", default=1.0, update=update_properties)

    RBFMiddle = FloatProperty(default=0.0)
    RBFTenPP = FloatProperty(default=0.25)  # Ten percent point

    def draw_buttons(self, context, layout):
        layout.prop(self, "Multiply")
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
        node.settings["Multiply"] = self.Multiply
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

    Method = EnumProperty(name="Method",
                          items=[("MUL", "Mul", "", 1),
                                 ("MIN", "Min", "", 2)])
    SingleOutput = BoolProperty(name="Single Output", default=False)
    IncludeAll = BoolProperty(name="Include All", default=True)

    def draw_buttons(self, context, layout):
        layout.prop(self, "Method", expand=True)
        layout.prop(self, "SingleOutput")
        layout.prop(self, "IncludeAll")

    def getSettings(self, node):
        node.settings["Method"] = self.Method
        node.settings["SingleOutput"] = self.SingleOutput
        node.settings["IncludeAll"] = self.IncludeAll


class OrNode(LogicNode):
    """CrowdMaster or node"""
    bl_label = "Or"

    Method = EnumProperty(name="Method",
                          items=[("MUL", "Mul", "", 1),
                                 ("MAX", "Max", "", 2)])
    SingleOutput = BoolProperty(name="Single Output", default=True)
    IncludeAll = BoolProperty(name="Include All", default=True)

    def draw_buttons(self, context, layout):
        layout.prop(self, "Method", expand=True)
        layout.prop(self, "SingleOutput")
        layout.prop(self, "IncludeAll")

    def getSettings(self, node):
        node.settings["Method"] = self.Method
        node.settings["SingleOutput"] = self.SingleOutput
        node.settings["IncludeAll"] = self.IncludeAll


class StrongNode(LogicNode):
    """CrowdMaster Strong node. Makes 1's and 0's stronger"""
    bl_label = "Strong"


class WeakNode(LogicNode):
    """CrowdMaster Weak node. Relaxes 1's and 0's"""
    bl_label = "Weak"


class QueryTagNode(LogicNode):
    """CrowdMaster Query Tag node"""
    bl_label = "Query Tag"

    Tag = StringProperty(name="Tag", default="default")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Tag")

    def getSettings(self, node):
        node.settings["Tag"] = self.Tag


class SetTagNode(LogicNode):
    """CrowdMaster Set Tag node"""
    bl_label = "Set Tag"

    Tag = StringProperty(name="Tag", default="default")
    UseThreshold = BoolProperty(name="Use Threshold", default=True)
    Threshold = FloatProperty(name="Threshold", default=0.5)
    Action = EnumProperty(name="Action",
                          items=[("ADD", "Add", "", 1),
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

    Variable = StringProperty(name="Variable", default="None")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Variable")

    def getSettings(self, node):
        node.settings["Variable"] = self.Variable


class FilterNode(LogicNode):
    """CrowdMaster Filter node"""
    bl_label = "Filter"

    Operation = EnumProperty(name="Operation",
                             items=[("EQUAL", "Equal", "", 1),
                                    ("NOT EQUAL", "Not equal", "", 2),
                                    ("LESS", "Less than", "", 3),
                                    ("GREATER", "Greater than", "", 4),
                                    ("LEAST", "Least only", "", 5),
                                    ("Most", "Most only", "", 6),
                                    ("AVERAGE", "Average", "", 7)])
    Value = FloatProperty(name="Value", default=0.0)

    def draw_buttons(self, context, layout):
        layout.prop(self, "Operation")
        if (self.Operation == "EQUAL" or self.Operation == "NOT EQUAL" or
            self.Operation == "LESS" or self.Operation == "GREATER"):
            layout.prop(self, "Value")

    def getSettings(self, node):
        node.settings["Operation"] = self.Operation
        node.settings["Value"] = self.Value


class MapNode(LogicNode):
    """CrowdMaster Map node"""
    bl_label = "Map"

    LowerInput = FloatProperty(name="Lower Input", default=0.0)
    UpperInput = FloatProperty(name="Upper Input", default=1.0)
    LowerOutput = FloatProperty(name="Lower Output", default=0.0)
    UpperOutput = FloatProperty(name="Upper Output", default=2.0)

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

    Output = EnumProperty(name="Output",
                          items=[("rz", "rz", "", 3),
                                 ("rx", "rx", "", 1),
                                 ("ry", "ry", "", 2),
                                 ("px", "px", "", 4),
                                 ("py", "py", "", 5),
                                 ("pz", "pz", "", 6)
                                 ])
    MultiInputType = EnumProperty(name="Multi Input Type",
                                  items=[("AVERAGE", "Average", "", 1),
                                         ("MAX", "Max", "", 2),
                                         ("SIZEAVERAGE", "Size Average", "", 3),
                                         ("SUM", "Sum", "", 4)
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

    EventName = StringProperty(name="Event Name", default="default")

    def draw_buttons(self, context, layout):
        layout.prop(self, "EventName")

    def getSettings(self, node):
        node.settings["EventName"] = self.EventName


class PythonNode(LogicNode):
    """CrowdMaster Python node"""
    bl_label = "Python"

    Expression = StringProperty(name="Expression", default="output = Noise.random")
    # This really needs to link to a text block

    def draw_buttons(self, context, layout):
        layout.prop(self, "Expression")

    def getSettings(self, node):
        node.settings["Expression"] = self.Expression


class PrintNode(LogicNode):
    """CrowdMaster Print Node"""
    bl_label = "Print"

    Label = StringProperty(name="Label", description = "The label to append to each printed statement.", default="")
    save_to_file = BoolProperty(
        name = "Save To File",
        description = "Save the printed statements to a file for later viewing.",
        default = False,
        )

    output_filepath = StringProperty \
      (
      name = "Output Filepath",
      default = "",
      description = "Define the output file path.",
      subtype = 'DIR_PATH'
      )
    # PrintSelected = BoolProperty(name="Print Selected", default=True)  # Not implemented

    def draw_buttons(self, context, layout):
        layout.prop(self, "Label")
        layout.prop(self, "save_to_file")
        if self.save_to_file == True:
            layout.prop(self, "output_filepath")

    def getSettings(self, node):
        node.settings["Label"] = self.Label
        node.settings["save_to_file"] = self.save_to_file
        node.settings["output_filepath"] = self.output_filepath


class PriorityNode(LogicNode):
    """CrowdMaster Priority node"""
    bl_label = "Priority"

    defaultValue = FloatProperty(name="Default Value", default=0)

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

    stateLength = IntProperty(name="State Length", default=1)
    cycleState = BoolProperty(name="Cycle State", default=False)
    actionName = StringProperty(name="Action Name", default="")
    useValueOfSpeed = BoolProperty(name=" Use Value of Speed", default=True)

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


class NoteNode(CrowdMasterNode):
    """For keeping the graph well organised"""
    bl_idname = 'LogicNoteNode'
    bl_label = 'Note'

    noteText = StringProperty(name="Note Text", default="Enter text here")

    def draw_buttons(self, context, layout):
        layout.label(self.noteText)

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "noteText")


import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CrowdMasterTreeType'

node_categories = [
    MyNodeCategory("INPUT", "Input", items=[
        NodeItem("InputNode"),
        NodeItem("PythonNode")
        ]),
    MyNodeCategory("OUTPUT", "Output", items=[
        NodeItem("OutputNode"),
        NodeItem("PrintNode")
        ]),
    MyNodeCategory("BASIC", "Basic", items=[
        NodeItem("GraphNode"),
        NodeItem("MapNode"),
        NodeItem("PriorityNode")
        ]),
    MyNodeCategory("LOGIC", "Logic", items=[
        NodeItem("AndNode"),
        NodeItem("OrNode")
        ]),
    MyNodeCategory("STRENGTH", "Strength", items=[
        NodeItem("StrongNode"),
        NodeItem("WeakNode")
        ]),
    MyNodeCategory("STATE", "State", items=[
        NodeItem("StartState"),
        NodeItem("ActionState")
        ]),
    MyNodeCategory("OTHER", "Other", items=[
        NodeItem("QueryTagNode"),
        NodeItem("SetTagNode"),
        NodeItem("VariableNode"),
        NodeItem("FilterNode"),
        NodeItem("EventNode")
        ]),
    MyNodeCategory("LAYOUT", "Layout", items=[
        NodeItem("NodeFrame"),
        NodeItem("NodeReroute"),
        NodeItem("LogicNoteNode")
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
    bpy.utils.register_class(FilterNode)
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
    bpy.utils.unregister_class(FilterNode)
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
