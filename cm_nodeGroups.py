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

import bpy
from bpy.types import Node, NodeTree, Operator, NodeSocket, PropertyGroup
from bpy.props import StringProperty, CollectionProperty
import random
from . import cm_bpyNodes

class GroupIOListing(PropertyGroup):
    name = StringProperty(name="Name")
    # TODO socket type


class CrowdMasterGroupTree(NodeTree):
    bl_idname = 'CrowdMasterGroupTreeType'
    bl_label = 'CrowdMaster Group Node Tree'
    bl_icon = 'NONE'

    # unique and non changing identifier set upon first creation
    cm_groupUID = StringProperty()

    groupIn = CollectionProperty(type=GroupIOListing)
    groupOut = CollectionProperty(type=GroupIOListing)

    def update(self):
        for node in self.nodes:
            if node.bl_idname in {"GroupInputs", "GroupOutputs"}:
                node.updateSockets()
        affected_trees = {instance.id_data for instance in self.instances()}
        for tree in affected_trees:
            tree.update()

    @classmethod
    def poll(cls, context):
        return False

    def instances(self):
        res = []
        for nodeGroup in bpy.data.node_groups:
            if nodeGroup.bl_idname in {"CrowdMasterTreeType", "CrowdMasterGroupTreeType"}:
                for node in nodeGroup.nodes:
                    if node.bl_idname == self.cm_groupUID:
                        res.append(node)
                    if hasattr(node, "cm_groupUID") and node.cm_groupUID == self.cm_groupUID:
                        res.append(node)
        return res

    def update_group_UID(self):
        """
        create or update the corresponding class reference
        """

        # TODO check that input and output node are present

        cls_dict = {}

        if not self.cm_groupUID:

            # cm_groupUID needs to be unique and cannot change

            name = self.name
            while name and not name[0].isalpha():
                name = name[1:]
            if name:
                baseName = "".join(ch for ch in name if ch.isalnum() or ch == "_")
            else:
                baseName = "generic"

            identifier = id(self) ^ random.randint(0, 4294967296)

            groupUID = "CrowdMasterGroupTree_{}_{}".format(baseName, identifier)
            self.cm_groupUID = groupUID
        else:
            groupUID = self.cm_groupUID

        cls_dict["bl_idname"] = groupUID
        cls_dict["bl_label"] = self.name

        #cls_dict["input_template"] = self.generate_inputs()
        #cls_dict["output_template"] = self.generate_outputs()

        # self.make_props(cls_dict)

        # done with setup

        old_cls_ref = getattr(bpy.types, groupUID, None)

        bases = (CrowdMasterGroupNode, CrowdMasterGroupTree)

        cls_ref = type(groupUID, bases, cls_dict)

        if old_cls_ref:
            bpy.utils.unregister_class(old_cls_ref)
        bpy.utils.register_class(cls_ref)

        return cls_ref


class CrowdMasterGroupNode(Node):
    @property
    def cm_groupTree(self):
        for tree in bpy.data.node_groups:
            if tree.bl_idname == 'CrowdMasterGroupTreeType' and self.bl_idname == tree.cm_groupUID:
               return tree

    def update(self):
        pass


class EmptySocket(NodeSocket):
    """Socket type used for unassigned group sockets."""
    bl_idname = 'EmptySocketType'
    bl_label = 'CrowdMaster Empty Node Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return 1.0, 1.0, 1.0, 0.0


class CrowdMasterCreateFromSelected(Operator):
    """Makes node group"""
    bl_idname = "node.cm_node_group_from_selected"
    bl_label = "Create node group from selected nodes"

    @classmethod
    def poll(cls, context):
        tree_type = context.space_data.tree_type
        if tree_type == 'CrowdMasterTreeType':
            return True

    def execute(self, context):

        ng = context.space_data.edit_tree
        nodes = [n for n in ng.nodes if n.select]

        if not nodes:
            self.report({"ERROR_INVALID_INPUT"}, "No nodes selected")
            return {'CANCELLED'}

        # TODO achieve this without using the clipboard
        bpy.ops.node.clipboard_copy()

        # TODO Use proper group name
        newGroup = bpy.data.node_groups.new("New group name", "CrowdMasterGroupTreeType")
        newGroup.use_fake_user = True

        # TODO create group input and output nodes here

        # by appending, space_data is now different
        path = context.space_data.path
        path.append(newGroup)

        bpy.ops.node.clipboard_paste()

        # TODO set positions of group input and output nodes and link sockets

        cls_ref = newGroup.update_group_UID()
        parent_node = ng.nodes.new(cls_ref.bl_idname)
        parent_node.select = False
        # parent_node.location = average_of_selected(nodes)

        # remove nodes from parent_tree
        for n in nodes:
            ng.nodes.remove(n)

        # TODO link the new nodes sockets

        # to make it pretty we pop and then append with the node
        path.pop()
        path.append(newGroup, node=parent_node)

        bpy.ops.node.view_all()
        return {'FINISHED'}


class CrowdMasterGroupToggle(Operator):
    bl_idname = "node.cm_group_enter_exit"
    bl_label = "Enter/exit group"

    @classmethod
    def poll(cls, context):
        tree_type = context.space_data.tree_type
        if tree_type in {"CrowdMasterTreeType", "CrowdMasterGroupTreeType"}:
            return True

    def execute(self, context):
        node = context.active_node

        if node and hasattr(node, 'cm_groupUID'):
            parentTree = node.id_data
            group = node.cm_groupTree

            path = context.space_data.path
            #space_data = context.space_data
            if len(path) == 1:
                path.start(parentTree)
                path.append(group, node=node)
            else:
                path.append(group, node=node)
            return {'FINISHED'}

        else:
            if len(context.space_data.path) > 1:
                space = context.space_data
                space.path.pop()
                return {'FINISHED'}

        return {'CANCELLED'}


class GroupInputs(cm_bpyNodes.CrowdMasterNode):
    """CrowdMaster Inputs Group Node"""
    bl_label = "Group Inputs"

    @classmethod
    def poll(cls, ntree):
        if ntree.bl_idname in {'CrowdMasterGroupTreeType'}:
            return True

    def init(self, context):
        # Input and self.outputs not a typo! Think about what this node is!
        self.outputs.new('EmptySocketType', "Input 0")

    def getSettings(self, item):
        pass

    def draw_buttons(self, context, layout):
        pass

    def updateSockets(self):
        count = 0
        while count < len(self.id_data.groupIn) and count < len(self.outputs):
            if self.id_data.groupIn[count].name != self.outputs[count].name:
                break
            count += 1
        while count < len(self.outputs):
            self.outputs.remove(self.outputs[count])
        while count < len(self.id_data.groupIn):
            socketName = self.id_data.groupIn[count].name
            self.outputs.new("EmptySocketType", "Input {}".format(socketName))

    def update(self):
        # TODO multiple group input nodes
        changedConnected = False
        if self.outputs[-1].is_linked:
            n = len(self.outputs)
            self.outputs.new("EmptySocketType", "Input {}".format(n))
            changedConnected = True
        elif len(self.outputs) > 1 and not self.outputs[-1].is_linked:
            while len(self.outputs) > 1 and not self.outputs[-2].is_linked:
                self.outputs.remove(self.outputs[-1])
                changedConnected = True

        if changedConnected:
            self.id_data.groupIn.clear()
            for inp in self.outputs[:-1]:
                i = self.id_data.groupIn.add()
                i.name = inp.name
            self.id_data.update()


class GroupOutputs(cm_bpyNodes.CrowdMasterNode):
    """CrowdMaster Output Group Node"""
    bl_label = "Group Outputs"

    @classmethod
    def poll(cls, ntree):
        if ntree.bl_idname in {'CrowdMasterGroupTreeType'}:
            return True

    def init(self, context):
        # Output and self.inputs not a typo! Think about what this node is!
        self.inputs.new('EmptySocketType', "Output 0")

    def getSettings(self, item):
        pass

    def draw_buttons(self, context, layout):
        pass

    def updateSockets(self):
        count = 0
        while count < len(self.id_data.groupOut) and count < len(self.inputs):
            if self.id_data.groupOut[count].name != self.inputs[count].name:
                break
            count += 1
        while count < len(self.inputs):
            self.inputs.remove(self.inputs[count])
        while count < len(self.id_data.groupOut):
            socketName = self.id_data.groupOut[count].name
            self.inputs.new("EmptySocketType", "Input {}".format(socketName))

    def update(self):
        # TODO multiple group output nodes
        changedConnected = False
        if self.inputs[-1].is_linked:
            n = len(self.inputs)
            self.inputs.new("EmptySocketType", "Output {}".format(n))
            changedConnected = True
        elif len(self.inputs) > 1 and not self.inputs[-1].is_linked:
            while len(self.inputs) > 1 and not self.inputs[-2].is_linked:
                self.inputs.remove(self.inputs[-1])
                changedConnected = True

        if changedConnected:
            self.id_data.groupOut.clear()
            for out in self.inputs[:-1]:
                i = self.id_data.groupOut.add()
                i.name = out.name
            self.id_data.update()


def register():
    bpy.utils.register_class(GroupIOListing)
    bpy.utils.register_class(CrowdMasterGroupTree)
    bpy.utils.register_class(CrowdMasterCreateFromSelected)
    bpy.utils.register_class(CrowdMasterGroupToggle)
    bpy.utils.register_class(EmptySocket)

    bpy.utils.register_class(GroupInputs)
    bpy.utils.register_class(GroupOutputs)

def unregister():
    bpy.utils.unregister_class(GroupIOListing)
    bpy.utils.unregister_class(CrowdMasterGroupTree)
    bpy.utils.unregister_class(CrowdMasterCreateFromSelected)
    bpy.utils.unregister_class(CrowdMasterGroupToggle)
    bpy.utils.unregister_class(EmptySocket)

    bpy.utils.unregister_class(GroupInputs)
    bpy.utils.unregister_class(GroupOutputs)
