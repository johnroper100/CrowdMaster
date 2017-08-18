# Copyright 2017 CrowdMaster Developer Team
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

import random
import textwrap

import bpy
import nodeitems_utils
from bpy.props import (BoolProperty, EnumProperty, FloatProperty,
                       FloatVectorProperty, IntProperty, StringProperty)
from bpy.types import Node, NodeSocket, NodeTree, Operator
from nodeitems_utils import NodeCategory, NodeItem

from .cm_iconLoad import cicon


class CrowdMasterTree(NodeTree):
    """The node tree that contains the CrowdMaster nodes."""
    bl_idname = 'CrowdMasterTreeType'
    bl_label = 'CrowdMaster Agent Simulation'
    bl_icon = 'OUTLINER_OB_ARMATURE'

    savedOnce = BoolProperty(default=False)


class DefaultSocket(NodeSocket):
    """Default CrowdMaster socket type"""
    bl_idname = 'DefaultSocketType'
    bl_label = 'Default CrowdMaster Node Socket'

    filterProperty = EnumProperty(items=[("AVERAGE", "Average", "", 1),
                                         ("MAX", "Max", "", 2),
                                         ("MIN", "Min", "", 3)])
    defaultValueProperty = FloatProperty(default=1.0)
    randomInputValue = BoolProperty(default=False)

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
    """Socket type used for state tree transitions."""
    bl_idname = 'StateSocketType'
    bl_label = 'CrowdMaster State Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.0, 0.0, 0.5, 1.0)


class DependanceSocket(NodeSocket):
    """Socket type used for dependance tree transitions."""
    bl_idname = 'DependanceSocketType'
    bl_label = 'CrowdMaster Dependance Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.8, 0.5, 0.0, 0.9)


class CrowdMasterNode(Node):
    """CrowdMaster node type superclass."""
    bl_label = 'Super class'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CrowdMasterTreeType'


class LogicNode(CrowdMasterNode):
    """CrowdMAster logic type node class."""
    bl_label = 'Logic super class'

    def init(self, context):
        self.inputs.new("DefaultSocketType", "Input")
        self.inputs[0].link_limit = 4095

        self.outputs.new('DefaultSocketType', "Output")
        self.outputs.new("DependanceSocketType", "Dependant")

    def getSettings(self, node):
        pass

# ============ End of super classes ============


class NewInputNode(LogicNode):
    """CrowdMaster new input node."""
    bl_label = "Input"
    bl_width_default = 350.0

    InputSource = EnumProperty(name="Input Channel",
                               items=[("AGENTINFO", "Agent Info", "Get information about other agents in the scene", 10),
                                      ("CONSTANT", "Constant",
                                       "Get a single value that does not change per frame", 1),
                                      ("FLOCK", "Flock",
                                       "Get information relating to flocking agents", 2),
                                      ("FORMATION", "Formation",
                                       "Get information relating to formation agents", 3),
                                      ("GROUND", "Ground",
                                       "Get information about ground objects", 4),
                                      ("NOISE", "Noise",
                                       "Get random values that change over time", 5),
                                      ("PATH", "Path",
                                       "Get information relating to path following", 6),
                                      ("SOUND", "Sound",
                                       "Get sound information from each agent", 7),
                                      ("STATE", "State",
                                       "Get state information from each agent", 8),
                                      ("WORLD", "World", "Get world information from the scene", 9)],
                               description="Which channel the input data should be pulled from",
                               default="CONSTANT")

    Constant = FloatProperty(name="Constant", precision=5)

    Flocking = EnumProperty(name="Flocking Input",
                            items=[("SEPARATE", "Separate", "The direction the agent needs to move to move away from other nearby agent", 1),
                                   ("ALIGN", "Align", "The rotation about the X and Z axes needed to align to the average heading of nearby agents", 2),
                                   ("COHERE", "Cohere", "The direction the agent needs to move to move towards the average position of neighbours", 3)])
    RotationAxis = EnumProperty(name="Rotation Axis",
                                items=[("RZ", "rz", "Rotate on the z axis", 1),
                                       ("RX", "rx", "Rotate on the x axis", 2)])
    TranslationAxis = EnumProperty(name="Translation Axis",
                                   items=[("TX", "tx", "Translate on the x axis", 1),
                                          ("TY", "ty", "Translate on the y axis", 2),
                                          ("TZ", "tz", "Translate on the z axis", 3)])

    FormationGroup = StringProperty(name="Formation Group")
    FormationOptions = EnumProperty(name="Formation Options",
                                    items=[("RZ", "rz", "", 1),
                                           ("RX", "rx", "", 2),
                                           ("DIST", "dist", "", 3)])

    GroundGroup = StringProperty(name="Ground Group")
    GroundOptions = EnumProperty(name="Ground Options",
                                 items=[("DH", "dh", "", 1),
                                        ("ARZ", "ahead rz", "", 2),
                                        ("ARX", "ahead rx", "", 3)])
    GroundAheadOffset = FloatVectorProperty(name="Ground Ahead Offset",
                                            description="Position relative to the agent to check the ground mesh",
                                            default=(0, 1, 0))

    NoiseOptions = EnumProperty(name="Noise Options",
                                items=[("RANDOM", "Random", "", 1),
                                       ("AGENTRANDOM", "Agent Random", "", 2),
                                       ("WAVE", "Wave", "", 3)])

    WaveLength = FloatProperty(name="Wavelength", default=24.0, min=0.0)
    WaveOffset = FloatProperty(name="Offset", default=0.0, min=0.0, max=1.0)

    PathName = StringProperty(name="Path Name")
    PathOptions = EnumProperty(name="Path Options",
                               items=[("RZ", "rz", "", 1),
                                      ("RX", "rx", "", 2),
                                      ("INLANE", "In lane", "", 3)])
    PathLaneSearchDistance = FloatProperty(name="Search Distance", min=0)

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
                                       ("DB", "db", "", 5)])
    PredictionOptions = EnumProperty(name="Sound Prediction Options",
                                     items=[("RZ", "rz", "", 1),
                                            ("RX", "rx", "", 2),
                                            ("DIST", "dist", "", 3),
                                            ("CLOSE", "close", "", 4),
                                            ("DB", "db", "", 5),
                                            ("CERT", "cert", "", 6)])
    SteeringOptions = EnumProperty(name="Sound steering Options",
                                   items=[("RZ", "rz", "", 1),
                                          ("RX", "rx", "", 2),
                                          ("DIST", "dist", "", 3),
                                          ("CLOSE", "close", "", 4),
                                          ("DB", "db", "", 5),
                                          ("CERT", "cert", "", 6),
                                          ("ACC", "acc", "", 7),
                                          ("OVER", "over", "", 8)])
    MinusRadius = BoolProperty(name="Minus Radius", default=True)

    StateOptions = EnumProperty(name="State Options",
                                items=[("RADIUS", "Radius", "", 1),
                                       ("SPEED", "Speed", "", 2),
                                       ("GLOBALVELX", "Global Vel X", "", 3),
                                       ("GLOBALVELY", "Global Vel Y", "", 4),
                                       ("GLOBALVELZ", "Global Vel Z", "", 5),
                                       ("QUERYTAG", "Query tag", "", 6)])
    StateTagName = StringProperty(name="Tag Name")

    WorldOptions = EnumProperty(name="World Options",
                                items=[("TIME", "Time", "", 1),
                                       ("TARGET", "Target", "", 2),
                                       ("EVENT", "Event", "", 3)])
    TargetObject = StringProperty(name="Target Object")
    TargetOptions = EnumProperty(name="Target Options",
                                 items=[("RZ", "rz", "", 1),
                                        ("RX", "rx", "", 2),
                                        ("ARRIVED", "Arrived", "", 3)])
    EventName = StringProperty(name="Event Name")
    EventOptions = EnumProperty(name="Event Options",
                                items=[("duration", "Duration", "", 1),
                                       ("elapsed", "Elapsed", "", 2),
                                       ("control", "Control", "", 3)],
                                default="control")

    AgentInfoOptions = EnumProperty(name="Agent Info Options",
                                    items=[("GETTAG", "Get Tag", "", 1),
                                           ("HEADRZ", "Heading rz", "", 2),
                                           ("HEADRX", "Heading rx", "", 3)])
    GetTagName = StringProperty(name="Get Tag Name")

    def draw_buttons(self, context, layout):
        layout.prop(self, "InputSource", text="Input")
        if self.InputSource == "CONSTANT":
            layout.prop(self, "Constant")
        elif self.InputSource == "FLOCK":
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
            layout.prop(self, "GroundOptions")
            if self.GroundOptions == "ARX" or self.GroundOptions == "ARZ":
                layout.prop(self, "GroundAheadOffset")
        elif self.InputSource == "NOISE":
            layout.prop(self, "NoiseOptions")
            if self.NoiseOptions == "WAVE":
                row = layout.row(align=True)
                row.prop(self, "WaveLength")
                row.prop(self, "WaveOffset")
        elif self.InputSource == "PATH":
            layout.prop_search(
                self, "PathName", context.scene.cm_paths, "coll")
            if self.PathName != "":
                layout.prop(self, "PathOptions")
                if self.PathOptions == "INLANE":
                    layout.prop(self, "PathLaneSearchDistance")
        elif self.InputSource == "SOUND":
            layout.prop(self, "SoundFrequency", text="Frequency")
            layout.prop(self, "SoundMode", expand=True)
            if self.SoundMode == "BASIC":
                layout.prop(self, "SoundOptions", text="Options")
            elif self.SoundMode == "PREDICTION":
                layout.prop(self, "PredictionOptions", text="Options")
            elif self.SoundMode == "STEERING":
                layout.prop(self, "SteeringOptions", text="Options")
            layout.prop(self, "MinusRadius")
        elif self.InputSource == "STATE":
            layout.prop(self, "StateOptions")
            if self.StateOptions == "QUERYTAG":
                layout.prop(self, "StateTagName")
        elif self.InputSource == "WORLD":
            layout.prop(self, "WorldOptions"),
            if self.WorldOptions == "TARGET":
                layout.prop_search(self, "TargetObject",
                                   context.scene, "objects")
                if self.TargetObject != "":
                    layout.prop(self, "TargetOptions")
            if self.WorldOptions == "EVENT":
                layout.prop(self, "EventName")
                layout.prop(self, "EventOptions")
        elif self.InputSource == "AGENTINFO":
            layout.prop(self, "AgentInfoOptions")
            if self.AgentInfoOptions == "GETTAG":
                layout.prop(self, "GetTagName")

    def getSettings(self, node):
        node.settings["InputSource"] = self.InputSource
        if self.InputSource == "CONSTANT":
            node.settings["Constant"] = self.Constant
        elif self.InputSource == "FLOCK":
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
            node.settings["GroundOptions"] = self.GroundOptions
            node.settings["GroundAheadOffset"] = self.GroundAheadOffset
        elif self.InputSource == "NOISE":
            node.settings["NoiseOptions"] = self.NoiseOptions
            node.settings["WaveOffset"] = self.WaveOffset
            node.settings["WaveLength"] = self.WaveLength
        elif self.InputSource == "PATH":
            node.settings["PathName"] = self.PathName
            node.settings["PathOptions"] = self.PathOptions
            if self.PathOptions == "INLANE":
                node.settings["PathLaneSearchDistance"] = self.PathLaneSearchDistance
        elif self.InputSource == "SOUND":
            node.settings["SoundFrequency"] = self.SoundFrequency
            node.settings["SoundMode"] = self.SoundMode
            if self.SoundMode == "BASIC":
                node.settings["SoundOptions"] = self.SoundOptions
            elif self.SoundMode == "PREDICTION":
                node.settings["SoundOptions"] = self.PredictionOptions
            elif self.SoundMode == "STEERING":
                node.settings["SoundOptions"] = self.SteeringOptions
            node.settings["MinusRadius"] = self.MinusRadius
        elif self.InputSource == "WORLD":
            node.settings["WorldOptions"] = self.WorldOptions
            if self.WorldOptions == "TARGET":
                node.settings["TargetObject"] = self.TargetObject
                if self.TargetObject != "":
                    node.settings["TargetOptions"] = self.TargetOptions
            if self.WorldOptions == "EVENT":
                node.settings["EventName"] = self.EventName
                node.settings["EventOptions"] = self.EventOptions
        elif self.InputSource == "AGENTINFO":
            node.settings["AgentInfoOptions"] = self.AgentInfoOptions
            node.settings["GetTagName"] = self.GetTagName
        elif self.InputSource == "STATE":
            node.settings["StateOptions"] = self.StateOptions
            node.settings["StateTagName"] = self.StateTagName


def update_properties(self, context):
    """Keeps the values in the graph node in the correct order."""
    if self.UpperZero < self.UpperOne:
        self.UpperOne = self.UpperZero
    if self.UpperOne < self.LowerOne:
        self.LowerOne = self.UpperOne
    if self.LowerOne < self.LowerZero:
        self.LowerZero = self.LowerOne


class GraphNode(LogicNode):
    """CrowdMaster graph node."""
    bl_label = "Graph"
    bl_width_default = 200.0

    Multiply = FloatProperty(
        name="Multiply", description="Multiply the outputted value by this number", default=1.0)
    Invert = BoolProperty(
        name="Invert", description="Invert the output of the graph", default=False)

    CurveType = EnumProperty(name="Curve Type",
                             items=[("RBF", "RBF", "", 1),
                                    ("RANGE", "Range", "", 2)],
                             description="Which curve function to use")

    LowerZero = FloatProperty(
        name="Lower Zero", default=-1.0, update=update_properties)
    LowerOne = FloatProperty(
        name="Lower One", default=-0.5, update=update_properties)
    UpperOne = FloatProperty(
        name="Upper One", default=0.5, update=update_properties)
    UpperZero = FloatProperty(
        name="Upper Zero", default=1.0, update=update_properties)

    RBFMiddle = FloatProperty(default=0.0)
    RBFTenPP = FloatProperty(default=0.25)  # Ten percent point

    def draw_buttons(self, context, layout):
        row = layout.row()
        row.prop(self, "Multiply")
        row.prop(self, "Invert")
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
        node.settings["Invert"] = self.Invert
        node.settings["CurveType"] = self.CurveType
        node.settings["LowerZero"] = self.LowerZero
        node.settings["LowerOne"] = self.LowerOne
        node.settings["UpperOne"] = self.UpperOne
        node.settings["UpperZero"] = self.UpperZero
        node.settings["RBFMiddle"] = self.RBFMiddle
        node.settings["RBFTenPP"] = self.RBFTenPP


class MathNode(LogicNode):
    """CrowdMaster math node."""
    bl_label = "Math"
    bl_width_default = 225.0

    operation = EnumProperty(name="Operation", items=[
                             ("add", "Add", "Add the two numbers together"),
                             ("sub", "Subtract",
                              "Subtract the two numbers from each other"),
                             ("mul", "Multiply", "Multiply the two numbers"),
                             ("div", "Divide", "Divide the two numbers"),
                             ("set", "Set To", "Set all inputs to this number")],
                             default="mul",
                             description="which mathematical operation to use.")

    num1 = FloatProperty(name="Number 1", default=1.0,
                         description="Input is added/subtracted/multiplied/divided to this number")

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


class NotNode(LogicNode):
    """CrowdMaster not node"""
    bl_label = "Not"


class StrongNode(LogicNode):
    """CrowdMaster Strong node. Makes 1's and 0's stronger"""
    bl_label = "Strong"


class WeakNode(LogicNode):
    """CrowdMaster Weak node. Relaxes 1's and 0's"""
    bl_label = "Weak"


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


class FilterNode(LogicNode):
    """CrowdMaster Filter node"""
    bl_label = "Filter"
    bl_width_default = 215.0

    Operation = EnumProperty(name="Operation",
                             items=[("EQUAL", "Equal", "", 1),
                                    ("NOT EQUAL", "Not equal", "", 2),
                                    ("LESS", "Less than", "", 3),
                                    ("GREATER", "Greater than", "", 4),
                                    ("LEAST", "Least only", "", 5),
                                    ("MOST", "Most only", "", 6),
                                    ("AVERAGE", "Average", "", 7)])
    Tag = BoolProperty(name="Tag", default=False)
    TagName = StringProperty(name="Tag Name", default="")
    Value = FloatProperty(name="Value", default=0.0)

    def draw_buttons(self, context, layout):
        layout.prop(self, "Operation")
        if self.Operation in {"EQUAL", "NOT EQUAL", "LESS", "GREATER"}:
            layout.prop(self, "Tag")
            if self.Tag:
                layout.prop(self, "TagName")
            else:
                layout.prop(self, "Value")

    def getSettings(self, node):
        node.settings["Operation"] = self.Operation
        node.settings["Tag"] = self.Tag
        node.settings["TagName"] = self.TagName
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
    bl_width_default = 350.0

    Output = EnumProperty(name="Output",
                          items=[("rx", "Rotation X", "", 1),
                                 ("ry", "Rotation Y", "", 2),
                                 ("rz", "Rotation Z", "", 3),
                                 ("px", "Position X", "", 4),
                                 ("py", "Position Y", "", 5),
                                 ("pz", "Position Z", "", 6),
                                 ("sk", "Shape Key", "", 7)
                                 ],
                          default="py")
    SKName = StringProperty(name="Shape Key Name",
                            description="The name of the shape key")
    MultiInputType = EnumProperty(name="Multi Input Type",
                                  items=[("AVERAGE", "Average", "", 1),
                                         ("MAX", "Max", "", 2),
                                         ("SIZEAVERAGE", "Size Average", "", 3),
                                         ("SUM", "Sum", "", 4)
                                         ])

    def draw_buttons(self, context, layout):
        layout.prop(self, "Output")
        if self.Output == "sk":
            layout.prop(self, "SKName")
        layout.prop(self, "MultiInputType")

    def getSettings(self, node):
        node.settings["SKName"] = self.SKName
        node.settings["Output"] = self.Output
        node.settings["MultiInputType"] = self.MultiInputType


class PrintNode(LogicNode):
    """CrowdMaster Print Node"""
    bl_label = "Print"
    bl_width_default = 310.0

    Label = StringProperty(
        name="Label", description="The label to append to each printed statement.", default="")
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
    # PrintSelected = BoolProperty(name="Print Selected", default=True)  # Not
    # implemented

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
        self.inputs.new("DefaultSocketType", "Values 0")
        self.inputs.new("DefaultSocketType", "Priority 0")

        self.outputs.new('DefaultSocketType', "Output")
        self.outputs.new("DependanceSocketType", "Dependant")

    def update(self):
        if self.inputs[-1].is_linked and self.inputs[-2].is_linked:
            n = len(self.inputs) // 2
            self.inputs.new("DefaultSocketType", "Values {}".format(n))
            self.inputs.new("DefaultSocketType", "Priority {}".format(n))

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
    bl_width_default = 275.0

    stateLength = IntProperty(name="State Length", default=1)
    cycleState = BoolProperty(name="Cycle State", default=False)
    actionName = StringProperty(name="Action Name", default="")
    overlap = IntProperty(name="Overlap", min=0, default=0)
    useValueOfSpeed = BoolProperty(name="Use Value of Speed", default=True)
    interuptState = BoolProperty(name="Interupt State", default=False)
    syncState = BoolProperty(name="Sync State", default=False)
    randomActionFromGroup = BoolProperty(
        name="Rand Group Action", default=True)

    def init(self, context):
        StateNode.init(self, context)

    def getSettings(self, item):
        val = self.inputs['Value']
        item.settings["ValueFilter"] = val.filterProperty
        item.settings["ValueDefault"] = val.defaultValueProperty
        item.settings["RandomInput"] = val.randomInputValue
        item.settings["Overlap"] = self.overlap
        item.length = self.stateLength
        item.cycleState = self.cycleState
        item.actionName = self.actionName
        item.useValueOfSpeed = self.useValueOfSpeed
        item.interuptState = self.interuptState
        item.syncState = self.syncState
        item.randomActionFromGroup = self.randomActionFromGroup

    def draw_buttons(self, context, layout):
        preferences = context.user_preferences.addons[__package__].preferences
        if self.actionName == "":
            layout.prop(self, "stateLength")
        layout.prop(self, "cycleState")
        row = layout.row(align=True)
        row.prop_search(self, "actionName", context.scene.cm_action_groups,
                        "groups")
        actName = self.actionName
        isGroup = actName != "" and actName[0] == "[" and actName[-1] == "]"
        if isGroup and (not self.interuptState or not self.syncState):
            if preferences.use_custom_icons:
                row.prop(self, "randomActionFromGroup",
                         icon_value=cicon('dice'), icon_only=True)
            else:
                row.prop(self, "randomActionFromGroup", icon="FILE_REFRESH",
                         icon_only=True)
        if self.actionName != "":
            layout.prop(self, "overlap")
        layout.prop(self, "interuptState")
        if self.interuptState:
            layout.prop(self, "syncState")


TEXT_WIDTH = 6
TW = textwrap.TextWrapper()


def get_lines(text_file):
    for line in text_file.lines:
        yield line.body


class NoteNode(CrowdMasterNode):
    """For keeping the graph well organised"""
    bl_idname = 'LogicNoteNode'
    bl_label = 'Note'

    text = StringProperty(
        name='Note Text', description="Text to show, if set will overide file")

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
        self.width = 300
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


class SimNoteTextFromClipboard(Operator):
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


class SimNoteClear(Operator):
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
        NodeItem("NewInputNode")
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
        NodeItem("OrNode"),
        NodeItem("NotNode")
    ]),
    MyNodeCategory("STRENGTH", "Strength", items=[
        NodeItem("StrongNode"),
        NodeItem("WeakNode")
    ]),
    MyNodeCategory("STATE", "State", items=[
        NodeItem("ActionState"),
        NodeItem("StartState")
    ]),
    MyNodeCategory("OTHER", "Other", items=[
        NodeItem("FilterNode"),
        NodeItem("MathNode"),
        NodeItem("SetTagNode"),
    ]),
    MyNodeCategory("LAYOUT", "Layout", items=[
        NodeItem("NodeFrame"),
        NodeItem("LogicNoteNode"),
        NodeItem("NodeReroute"),
    ])
]


def register():
    bpy.utils.register_class(CrowdMasterTree)
    bpy.utils.register_class(DefaultSocket)
    bpy.utils.register_class(StateSocket)
    bpy.utils.register_class(DependanceSocket)
    bpy.utils.register_class(LogicNode)
    bpy.utils.register_class(StateNode)

    bpy.utils.register_class(NewInputNode)
    bpy.utils.register_class(GraphNode)
    bpy.utils.register_class(MathNode)
    bpy.utils.register_class(AndNode)
    bpy.utils.register_class(OrNode)
    bpy.utils.register_class(NotNode)
    bpy.utils.register_class(StrongNode)
    bpy.utils.register_class(WeakNode)
    bpy.utils.register_class(SetTagNode)
    bpy.utils.register_class(FilterNode)
    bpy.utils.register_class(MapNode)
    bpy.utils.register_class(OutputNode)
    bpy.utils.register_class(PriorityNode)
    bpy.utils.register_class(PrintNode)

    bpy.utils.register_class(StartState)
    bpy.utils.register_class(ActionState)

    bpy.utils.register_class(NoteNode)
    bpy.utils.register_class(SimNoteTextFromClipboard)
    bpy.utils.register_class(SimNoteClear)

    nodeitems_utils.register_node_categories(
        "CrowdMaster_NODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("CrowdMaster_NODES")

    bpy.utils.unregister_class(CrowdMasterTree)
    bpy.utils.unregister_class(DefaultSocket)
    bpy.utils.unregister_class(StateSocket)
    bpy.utils.unregister_class(DependanceSocket)
    bpy.utils.unregister_class(LogicNode)
    bpy.utils.unregister_class(StateNode)

    bpy.utils.unregister_class(NewInputNode)
    bpy.utils.unregister_class(GraphNode)
    bpy.utils.unregister_class(MathNode)
    bpy.utils.unregister_class(AndNode)
    bpy.utils.unregister_class(OrNode)
    bpy.utils.unregister_class(NotNode)
    bpy.utils.unregister_class(StrongNode)
    bpy.utils.unregister_class(WeakNode)
    bpy.utils.unregister_class(SetTagNode)
    bpy.utils.unregister_class(FilterNode)
    bpy.utils.unregister_class(MapNode)
    bpy.utils.unregister_class(OutputNode)
    bpy.utils.unregister_class(PriorityNode)
    bpy.utils.unregister_class(PrintNode)

    bpy.utils.unregister_class(StartState)
    bpy.utils.unregister_class(ActionState)

    bpy.utils.unregister_class(NoteNode)
    bpy.utils.unregister_class(SimNoteTextFromClipboard)
    bpy.utils.unregister_class(SimNoteClear)


if __name__ == "__main__":
    register()
