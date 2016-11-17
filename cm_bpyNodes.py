# Copyright 2016 CrowdMaster Developer Team
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of CrowdMaster.
#
# CrowdMaster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CrowdMaster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CrowdMaster.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import FloatProperty, StringProperty, BoolProperty
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty
import textwrap
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
import random

from . icon_load import cicon


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
    randomInputValue = BoolProperty(default=False)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        preferences = context.user_preferences.addons[__package__].preferences
        if not self.is_output and isinstance(node, StateNode):
            row = layout.row(align=True)
            if node.syncState:
                if self.is_linked:
                    row.prop(self, "defaultValueProperty", text="")
                    if preferences.use_custom_icons:
                        row.prop(self, "randomInputValue",
                                 icon_value=cicon('dice'), icon_only=True)
                    else:
                        row.prop(self, "randomInputValue", icon="FILE_REFRESH",
                                 icon_only=True)
                else:
                    row.label(text)
            else:
                if self.is_linked:
                    row.prop(self, "filterProperty", text=text)
                else:
                    row.prop(self, "defaultValueProperty", text="")
                if preferences.use_custom_icons:
                    row.prop(self, "randomInputValue",
                             icon_value=cicon('dice'), icon_only=True)
                else:
                    row.prop(self, "randomInputValue", icon="FILE_REFRESH",
                             icon_only=True)
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
    bl_label = "Old Input Node !UNSTABLE!"
    bl_width_default = 200.0

    Input = StringProperty(name="Input", default="Noise.random")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Input")

    def getSettings(self, node):
        node.settings["Input"] = self.Input


class NewInputNode(LogicNode):
    """CrowdMaster input node"""
    bl_label = "Input"
    bl_width_default = 200.0

    InputSource = EnumProperty(name="Input Channel",
                               items=[("CONSTANT", "Constant", "", 1),
                                      ("CROWD", "Crowd", "", 2),
                                      ("FORMATION", "Formation", "", 3),
                                      ("GROUND", "Ground", "", 4),
                                      ("NOISE", "Noise", "", 5),
                                      ("PATH", "Path", "", 6),
                                      ("SOUND", "Sound", "", 7),
                                      ("STATE", "State", "", 8),
                                      ("WORLD", "World", "", 9)])

    Constant = FloatProperty(name="Constant")

    Flocking = EnumProperty(name="Flocking Input",
                            items=[("SEPARATE", "Separate", "", 1),
                                   ("ALIGN", "Align", "", 2),
                                   ("COHERE", "Cohere", "", 3)])
    RotationAxis = EnumProperty(name="Rotation Axis",
                                items=[("RZ", "rz", "", 1),
                                       ("RX", "rx", "", 2)])
    TranslationAxis = EnumProperty(name="Translation Axis",
                                   items=[("TX", "tx", "", 1),
                                          ("TY", "ty", "", 2),
                                          ("TZ", "tz", "", 3)])

    FormationGroup = StringProperty(name="Formation Group")
    FormationOptions = EnumProperty(name="Formation Options",
                                    items=[("RZ", "rz", "", 1),
                                           ("RX", "rx", "", 2),
                                           ("DIST", "dist", "", 3)])

    GroundGroup = StringProperty(name="Ground Group")

    NoiseOptions = EnumProperty(name="Noise Options",
                                items=[("RANDOM", "Random", "", 1),
                                       ("AGENTRANDOM", "Agent Random", "", 2)])

    PathName = StringProperty(name="Path Name")
    PathOptions = EnumProperty(name="Path Options",
                               items=[("RZ", "rz", "", 1),
                                      ("RX", "rx", "", 2)])

    SoundFrequency = StringProperty(name="Sound Frequency")
    SoundMode = EnumProperty(name="Sound mode",
                             items=[("BASIC", "Basic", "", 1),
                                    ("PREDICTION", "Prediction", "", 2),
                                    ("STEERING", "Steering", "", 3)])
    SoundOptions = EnumProperty(name="Sound Options",
                                items=[("RZ", "rz", "", 1),
                                       ("RX", "rx", "", 2),
                                       ("DIST", "dist", "", 3),
                                       ("CLOSE", "close", "", 4),
                                       ("DB", "db", "", 5),
                                       ("CERT", "cert", "", 6),
                                       ("ACC", "acc", "", 7),
                                       ("OVER", "over", "", 8)])

    StateOptions = EnumProperty(name="State Options",
                                items=[("RADIUS", "Radius", "", 1),
                                       ("SPEED", "Speed", "", 2),
                                       ("GLOBALVELX", "Global Vel X", "", 3),
                                       ("GLOBALVELY", "Global Vel Y", "", 4),
                                       ("GLOBALVELZ", "Global Vel Z", "", 5)])

    WorldOptions = EnumProperty(name="World Options",
                                items=[("TIME", "Time", "", 1),
                                       ("TARGET", "Target", "", 2)])
    TargetObject = StringProperty(name="Target Object")
    TargetOptions = EnumProperty(name="Target Options",
                                 items=[("RZ", "rz", "", 1),
                                        ("RX", "rx", "", 2),
                                        ("ARRIVED", "Arrived", "", 3)])

    def draw_buttons(self, context, layout):
        layout.prop(self, "InputSource", text="Input")
        if self.InputSource == "CONSTANT":
            layout.prop(self, "Constant")
        elif self.InputSource == "CROWD":
            layout.prop(self, "Flocking")
            if self.Flocking == "SEPARATE" or self.Flocking == "COHERE":
                layout.prop(self, "TranslationAxis")
            else:  # ie. self.Flocking == "ALIGN"
                layout.prop(self, "RotationAxis")
        elif self.InputSource == "FORMATION":
            layout.prop_search(self, "FormationGroup", bpy.data, "groups")
            # TODO  Add fixed formations
            if self.FormationGroup != "":
                layout.prop(self, "FormationOptions")
        elif self.InputSource == "GROUND":
            layout.prop_search(self, "GroundGroup", bpy.data, "groups")
        elif self.InputSource == "NOISE":
            layout.prop(self, "NoiseOptions")
        elif self.InputSource == "PATH":
            layout.prop_search(self, "PathName", context.scene.cm_paths, "coll")
            if self.PathName != "":
                layout.prop(self, "PathOptions")
        elif self.InputSource == "SOUND":
            layout.prop(self, "SoundFrequency", text="Frequency")
            layout.prop(self, "SoundMode", expand=True)
            layout.prop(self, "SoundOptions", text="Options")
        elif self.InputSource == "STATE":
            layout.prop(self, "StateOptions")
        elif self.InputSource == "WORLD":
            layout.prop(self, "WorldOptions"),
            if self.WorldOptions == "TARGET":
                layout.prop_search(self, "TargetObject", context.scene, "objects")
                if self.TargetObject != "":
                    layout.prop(self, "TargetOptions")

    def getSettings(self, node):
        node.settings["InputSource"] = self.InputSource
        if self.InputSource == "CONSTANT":
            node.settings["Constant"] = self.Constant
        elif self.InputSource == "CROWD":
            node.settings["Flocking"] = self.Flocking
            if self.Flocking == "SEPARATE" or self.Flocking == "COHERE":
                node.settings["TranslationAxis"] = self.TranslationAxis
            else:  # ie. self.Flocking == "ALIGN"
                node.settings["RotationAxis"] = self.RotationAxis
        elif self.InputSource == "FORMATION":
            node.settings["FormationGroup"] = self.FormationGroup
            # TODO  Add fixed formations
            if self.FormationGroup != "":
                node.settings["FormationOptions"] = self.FormationOptions
        elif self.InputSource == "GROUND":
            node.settings["GroundGroup"] = self.GroundGroup
        elif self.InputSource == "NOISE":
            node.settings["NoiseOptions"] = self.NoiseOptions
        elif self.InputSource == "PATH":
            node.settings["PathName"] = self.PathName
            node.settings["PathOptions"] = self.PathOptions
        elif self.InputSource == "SOUND":
            node.settings["SoundFrequency"] = self.SoundFrequency
            node.settings["SoundMode"] = self.SoundMode
            node.settings["SoundOptions"] = self.SoundOptions
        elif self.InputSource == "STATE":
            node.settings["StateOptions"] = self.StateOptions
        elif self.InputSource == "WORLD":
            node.settings["WorldOptions"] = self.WorldOptions
            if self.WorldOptions == "TARGET":
                node.settings["TargetObject"] = self.TargetObject
                if self.TargetObject != "":
                    node.settings["TargetOptions"] = self.TargetOptions


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
    bl_width_default = 200.0

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

    """Testing to see if this would work, currently it breaks the texture preview in the properties editor
    def init(self, context):
        cm_tex1Path = os.path.dirname(__file__) + "/cm_graphics/images/range_function.jpg"
        cm_tex2Path = os.path.dirname(__file__) + "/cm_graphics/images/rbf_function.jpg"
        try:
            cm_tex1Img = bpy.data.images.load(cm_tex1Path)
            cm_tex2Img = bpy.data.images.load(cm_tex2Path)
        except:
            raise NameError("Cannot load image %s" % cm_tex1Path)
            raise NameError("Cannot load image %s" % cm_tex2Path)

        cm_tex1Name = 'CrowdMaster-Graph-Range-Do-Not-Delete'
        cm_tex2Name = 'CrowdMaster-Graph-RBF-Do-Not-Delete'

        if cm_tex1Name not in bpy.data.textures:
            cm_tex1 = bpy.data.textures.new(cm_tex1Name, type='IMAGE')
            cm_tex1.image = cm_tex1Img

        if cm_tex2Name not in bpy.data.textures:
            cm_tex2 = bpy.data.textures.new(cm_tex2Name, type='IMAGE')
            cm_tex2.image = cm_tex2Img
    """

    def draw_buttons(self, context, layout):
        """if self.CurveType == "RANGE":
            row = layout.row()
            split = row.split(1000 / (context.region.width - 50))
            split.template_preview(bpy.data.textures['CrowdMaster-Graph-Range-Do-Not-Delete'], show_buttons=False)

        elif self.CurveType == "RBF":
            row = layout.row()
            split = row.split(1000 / (context.region.width - 50))
            split.template_preview(bpy.data.textures['CrowdMaster-Graph-RBF-Do-Not-Delete'], show_buttons=False)"""

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


class MathNode(LogicNode):
    """CrowdMaster math node"""
    bl_label = "Math"
    bl_width_default = 150.0

    operation = EnumProperty(name="Operation", items=[
                             ("add", "Add", "Add the two numbers together"),
                             ("sub", "Subtract", "Subtract the two numbers from each other"),
                             ("mul", "Multiply", "Multiply the two numbers"),
                             ("div", "Divide", "Divide the two numbers")], default="add")

    num1 = FloatProperty(name="Number 1", default=1.0)

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation")
        layout.prop(self, "num1")

    def getSettings(self, node):
        node.settings["operation"] = self.operation
        node.settings["num1"] = self.num1


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
    bl_width_default = 200.0

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
    bl_width_default = 200.0

    Variable = StringProperty(name="Variable", default="None")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Variable")

    def getSettings(self, node):
        node.settings["Variable"] = self.Variable


class FilterNode(LogicNode):
    """CrowdMaster Filter node"""
    bl_label = "Filter"
    bl_width_default = 250.0

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
        if self.Operation in {"EQUAL", "NOT EQUAL", "LESS", "GREATER"}:
            layout.prop(self, "Value")

    def getSettings(self, node):
        node.settings["Operation"] = self.Operation
        node.settings["Value"] = self.Value


class MapNode(LogicNode):
    """CrowdMaster Map node"""
    bl_label = "Map"
    bl_width_default = 200.0

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
    bl_width_default = 300.0

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
    bl_width_default = 250.0

    EventName = StringProperty(name="Event Name", default="default")

    def draw_buttons(self, context, layout):
        layout.prop(self, "EventName")

    def getSettings(self, node):
        node.settings["EventName"] = self.EventName


class PythonNode(LogicNode):
    """CrowdMaster Python node"""
    bl_label = "Python"
    bl_width_default = 300.0

    Expression = StringProperty(name="Expression", default="output = Noise.random")
    # This really needs to link to a text block

    def draw_buttons(self, context, layout):
        layout.prop(self, "Expression")

    def getSettings(self, node):
        node.settings["Expression"] = self.Expression


class PrintNode(LogicNode):
    """CrowdMaster Print Node"""
    bl_label = "Print"
    bl_width_default = 300.0

    Label = StringProperty(name="Label", description="The label to append to each printed statement.", default="")
    save_to_file = BoolProperty(
        name="Save To File",
        description="Save the printed statements to a file for later viewing.",
        default=False,
        )

    output_filepath = StringProperty(
      name="Output Filepath",
      default="",
      description="Define the output file path.",
      subtype='DIR_PATH'
      )
    # PrintSelected = BoolProperty(name="Print Selected", default=True)  # Not implemented

    def draw_buttons(self, context, layout):
        layout.prop(self, "Label")
        layout.prop(self, "save_to_file")
        if self.save_to_file:
            layout.prop(self, "output_filepath")

    def getSettings(self, node):
        node.settings["Label"] = self.Label
        node.settings["save_to_file"] = self.save_to_file
        node.settings["output_filepath"] = self.output_filepath


class PriorityNode(LogicNode):
    """CrowdMaster Priority node"""
    bl_label = "Priority"
    bl_width_default = 175.0

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

def updateWait(self, context):
    """Keeps the random wait values in the right order"""
    if self.minRandWait > self.maxRandWait:
        self.minRandWait = self.maxRandWait


class StartState(StateNode):
    """CrowdMaster Start State"""
    bl_label = "Start"
    bl_width_default = 225.0

    minRandWait = IntProperty(name="Minimum", default=0, min=0,
                              update=updateWait)
    maxRandWait = IntProperty(name="Maximum", default=0, min=0,
                              update=updateWait)

    def init(self, context):
        self.inputs.new("DependanceSocketType", "Dependant")
        self.inputs["Dependant"].link_limit = 4095

        self.outputs.new("StateSocketType", "To")
        self.outputs["To"].link_limit = 4095

    def getSettings(self, item):
        item.settings["minRandWait"] = self.minRandWait
        item.settings["maxRandWait"] = self.maxRandWait
        item.length = random.randint(self.minRandWait,
                                     self.maxRandWait)

    def draw_buttons(self, context, layout):
        row = layout.row()
        row.label("Random wait time:")
        row = layout.row(align=True)
        row.prop(self, "minRandWait")
        row.prop(self, "maxRandWait")


class ActionState(StateNode):
    """CrowdMaster Action State"""
    bl_label = "Action"

    stateLength = IntProperty(name="State Length", default=1)
    cycleState = BoolProperty(name="Cycle State", default=False)
    actionName = StringProperty(name="Action Name", default="")
    useValueOfSpeed = BoolProperty(name=" Use Value of Speed", default=True)
    syncState = BoolProperty(name="Sync State", default=False)

    def init(self, context):
        StateNode.init(self, context)

    def getSettings(self, item):
        val = self.inputs['Value']
        item.settings["ValueFilter"] = val.filterProperty
        item.settings["ValueDefault"] = val.defaultValueProperty
        item.settings["RandomInput"] = val.randomInputValue
        item.length = self.stateLength
        item.cycleState = self.cycleState
        item.actionName = self.actionName
        item.useValueOfSpeed = self.useValueOfSpeed
        item.syncState = self.syncState

    def draw_buttons(self, context, layout):
        if self.actionName == "":
            layout.prop(self, "stateLength")
        layout.prop(self, "cycleState")
        row = layout.row()
        row.prop(self, "actionName", text="")
        layout.prop(self, "syncState")
        # row.prop(self, "useValueOfSpeed", text="")


class ActionGroupState(StateNode):
    """CrowdMaster Action Group State"""
    bl_label = "Action Group"

    cycleState = BoolProperty(name="Cycle State", default=False)
    groupName = StringProperty(name="Action Group Name", default="")
    useValueOfSpeed = BoolProperty(name=" Use Value of Speed", default=True)

    def init(self, context):
        StateNode.init(self, context)

    def getSettings(self, item):
        val = self.inputs['Value']
        item.settings["ValueFilter"] = val.filterProperty
        item.settings["ValueDefault"] = val.defaultValueProperty
        item.settings["RandomInput"] = val.randomInputValue
        item.settings["GroupName"] = self.groupName
        item.cycleState = self.cycleState
        item.useValueOfSpeed = self.useValueOfSpeed

    def draw_buttons(self, context, layout):
        layout.prop(self, "cycleState")
        row = layout.row()
        row.prop(self, "groupName", text="")
        # row.prop(self, "useValueOfSpeed", text="")

TEXT_WIDTH = 6
TW = textwrap.TextWrapper()


def get_lines(text_file):
    for line in text_file.lines:
        yield line.body


class NoteNode(CrowdMasterNode):
    """For keeping the graph well organised"""
    bl_idname = 'LogicNoteNode'
    bl_label = 'Note'

    text = StringProperty(name='Note Text', description="Text to show, if set will overide file")

    text_file = StringProperty(description="Textfile to show")

    def format_text(self):
        global TW
        out = []
        if self.text:
            lines = self.text.splitlines()
        elif self.text_file:
            text_file = bpy.data.texts.get(self.text_file)
            if text_file:
                lines = get_lines(text_file)
            else:
                return []
        else:
            return []
        width = self.width
        TW.width = int(width) // TEXT_WIDTH
        for t in lines:
            out.extend(TW.wrap(t))
            out.append("")
        return out

    def init(self, context):
        self.width = 400
        self.color = (0.5, 0.5, 0.5)
        self.use_custom_color = True

    def draw_buttons(self, context, layout):
        has_text = self.text or self.text_file
        if has_text:
            col = layout.column(align=True)
            text_lines = self.format_text()
            for l in text_lines:
                if l:
                    col.label(text=l)
            col = layout.column()
            col.operator("node.sim_note_clear", icon="X_VEC")

        else:
            col = layout.column()
            col.prop(self, "text")

            col = layout.column(align=True)
            col.operator("node.sim_note_from_clipboard", icon="TEXT")
            col.operator("node.sim_note_clear", icon="X_VEC")

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "text", text="Text")
        layout.operator("node.sim_note_from_clipboard", icon="TEXT")
        layout.operator("node.sim_note_clear", icon="X_VEC")

    def clear(self):
        self.text = ""
        self.text_file = ""

    def to_text(self):
        text_name = "Note Text"
        text = bpy.data.texts.get(text_name)
        if not text:
            text = bpy.data.texts.new(text_name)
        text.clear()
        text.write(self.text)


class SimNoteTextFromClipboard(bpy.types.Operator):
    """Grab whatever text is in the clipboard"""
    bl_idname = "node.sim_note_from_clipboard"
    bl_label = "Grab Text From Clipboard"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        text = bpy.context.window_manager.clipboard
        if not text:
            self.report({"INFO"}, "No text selected")
            return {'CANCELLED'}
        node = context.node
        node.text = text
        return {'FINISHED'}


class SimNoteClear(bpy.types.Operator):
    """Clear Note Node"""
    bl_idname = "node.sim_note_clear"
    bl_label = "Clear Text"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        node = context.node
        node.clear()
        return {'FINISHED'}

class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CrowdMasterTreeType'

node_categories = [
    MyNodeCategory("INPUT", "Input", items=[
        NodeItem("NewInputNode"),
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
        NodeItem("ActionState"),
        NodeItem("ActionGroupState")
        ]),
    MyNodeCategory("OTHER", "Other", items=[
        NodeItem("QueryTagNode"),
        NodeItem("SetTagNode"),
        NodeItem("MathNode"),
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
    bpy.utils.register_class(ActionGroupState)

    bpy.utils.register_class(InputNode)
    bpy.utils.register_class(NewInputNode)
    bpy.utils.register_class(GraphNode)
    bpy.utils.register_class(MathNode)
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
    bpy.utils.register_class(SimNoteTextFromClipboard)
    bpy.utils.register_class(SimNoteClear)

    nodeitems_utils.register_node_categories("CrowdMaster_NODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("CrowdMaster_NODES")

    bpy.utils.unregister_class(CrowdMasterTree)
    bpy.utils.unregister_class(DefaultSocket)
    bpy.utils.unregister_class(StateSocket)
    bpy.utils.unregister_class(DependanceSocket)
    bpy.utils.unregister_class(LogicNode)
    bpy.utils.unregister_class(StateNode)
    bpy.utils.unregister_class(ActionGroupState)

    bpy.utils.unregister_class(InputNode)
    bpy.utils.unregister_class(NewInputNode)
    bpy.utils.unregister_class(GraphNode)
    bpy.utils.unregister_class(MathNode)
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
    bpy.utils.unregister_class(SimNoteTextFromClipboard)
    bpy.utils.unregister_class(SimNoteClear)

if __name__ == "__main__":
    register()
