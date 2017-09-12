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
from bpy.types import Panel, UIList
from bpy.props import StringProperty, CollectionProperty, EnumProperty
from bpy.props import IntProperty, BoolProperty
import random
from . import cm_bpyNodes

def groupInSocketUpdate(self, context):
    group = context.space_data.path[-1].node_tree
    for n, gi in enumerate(group.groupIn):
        if gi == self:
            index = n
    def dup(coll, name):
        one = False
        for i in coll:
            if i.name == name:
                if one:
                    return True
                else:
                    one = True
    while dup(group.groupIn, self.name):
        self.name += "*"
        # TODO append ".001", ".002" etc... instead of "*"
    for node in group.nodes:
        if node.bl_idname in "GroupInputs":
            if node.outputs[index].name != self.name:
                node.outputs[index].name = self.name
    group.updateInstances()

def groupOutSocketUpdate(self, context):
    group = context.space_data.path[-1].node_tree
    for n, gi in enumerate(group.groupOut):
        if gi == self:
            index = n
    def dup(coll, name):
        one = False
        for i in coll:
            if i.name == name:
                if one:
                    return True
                else:
                    one = True
    while dup(group.groupOut, self.name):
        self.name += "*"
        # TODO append ".001", ".002" etc... instead of "*"
    for node in group.nodes:
        if node.bl_idname in "GroupOutputs":
            if node.inputs[index].name != self.name:
                node.inputs[index].name = self.name
    group.updateInstances()


class GroupInListing(PropertyGroup):
    name = StringProperty(name="Name", update=groupInSocketUpdate)
    # TODO socket type


class GroupOutListing(PropertyGroup):
    name = StringProperty(name="Name", update=groupOutSocketUpdate)
    # TODO socket type


updatingGroup = False


class CrowdMasterGroupTree(NodeTree):
    bl_idname = 'CrowdMasterGroupTreeType'
    bl_label = 'CrowdMaster Group Node Tree'
    bl_icon = 'NONE'

    groupIn = CollectionProperty(type=GroupInListing)
    groupInIndex = IntProperty()
    groupOut = CollectionProperty(type=GroupOutListing)
    groupOutIndex = IntProperty()

    def update(self):
        global updatingGroup
        if updatingGroup:
            return
        updatingGroup = True
        for node in self.nodes:
            inConnections = {}
            for inputSocket in node.inputs:
                if inputSocket.name == "":
                    continue
                inConnections[inputSocket.name] = []
                for inputLink in inputSocket.links:
                    inConnections[inputSocket.name].append(inputLink.from_socket)
            outConnections = {}
            for outputSocket in node.outputs:
                if outputSocket.name == "":
                    continue
                outConnections[outputSocket.name] = []
                for outputLink in outputSocket.links:
                    outConnections[outputSocket.name].append(outputLink.to_socket)

            changedConnected = False
            groupIONode = False
            if node.bl_idname == "GroupInputs":
                groupIONode = True
                if len(node.outputs) > 0:
                    if node.outputs[-1].is_linked:
                        n = len(node.outputs)
                        node.outputs[-1].name = "Input {}".format(n)
                        node.outputs.new("EmptySocketType", "")
                        changedConnected = True

                if changedConnected:
                    for inp in node.outputs[len(self.groupIn):-1]:
                        i = self.groupIn.add()
                        i.name = inp.name

                count = 0
                while count < len(self.groupIn) and count < len(node.outputs):
                    if self.groupIn[count].name != node.outputs[count].name:
                        break
                    count += 1

                newInputs = count != len(self.groupIn)
                while count < len(node.outputs):
                    if newInputs:
                        node.outputs.remove(node.outputs[count])
                    elif len(node.outputs) - 1 <= count:
                        break
                    else:
                        node.outputs.remove(node.outputs[count])

                if newInputs:
                    while count < len(self.groupIn):
                        socketName = self.groupIn[count].name
                        node.outputs.new("EmptySocketType", socketName)
                        count += 1

                    node.outputs.new("EmptySocketType", "")

            elif node.bl_idname == "GroupOutputs":
                groupIONode = True
                if node.inputs[-1].is_linked:
                    n = len(node.inputs)
                    node.inputs[-1].name = "Output {}".format(n)
                    node.inputs.new("EmptySocketType", "")
                    changedConnected = True

                if changedConnected:
                    self.groupOut.clear()
                    for out in node.inputs[:-1]:
                        i = node.id_data.groupOut.add()
                        i.name = out.name

                count = 0
                while count < len(self.groupOut) and count < len(node.inputs):
                    if self.groupOut[count].name != node.inputs[count].name:
                        break
                    count += 1
                while count < len(node.inputs):
                    node.inputs.remove(node.inputs[count])

                while count < len(self.groupOut):
                    socketName = self.groupOut[count].name
                    node.inputs.new("EmptySocketType", socketName)
                    count += 1
                node.inputs.new("EmptySocketType", "")

            if groupIONode:
                for inputSocketName in inConnections:
                    inputSocket = node.inputs.get(inputSocketName)
                    if inputSocket is not None:
                        connections = inConnections[inputSocketName]
                        if len(inputSocket.links) == 0:
                            for inputLink in inConnections[inputSocketName]:
                                self.links.new(inputLink, inputSocket)
                for outputSocketName in outConnections:
                    outputSocket = node.outputs.get(outputSocketName)
                    if outputSocket is not None:
                        connections = outConnections[outputSocketName]
                        if len(outputSocket.links) == 0:
                            for outputLink in outConnections[outputSocketName]:
                                self.links.new(outputSocket, outputLink)

            if changedConnected:
                updatingGroup = False
                self.update()
                updatingGroup = True

        self.updateInstances()
        updatingGroup = False

    def updateInstances(self):
        for groupNodeInstance in self.instances():
            groupNodeInstance.update()

    @classmethod
    def poll(cls, context):
        return False

    def instances(self):
        res = []
        for nodeGroup in bpy.data.node_groups:
            if nodeGroup.bl_idname in {"CrowdMasterTreeType", "CrowdMasterGroupTreeType"}:
                for node in nodeGroup.nodes:
                    if node.bl_idname == "GroupNode":
                        if node.groupName == self.name:
                            res.append(node)
        return res


class remove_group_input_socket(Operator):
    """Remove the seleted group input socket"""
    bl_idname = "scene.cm_group_remove_input"
    bl_label = "Remove socket"

    groupName = StringProperty()

    @classmethod
    def poll(cls, context):
        if len(context.space_data.path) > 0:
            group = context.space_data.path[-1].node_tree
            if group.bl_idname == "CrowdMasterGroupTreeType":
                if 0 <= group.groupInIndex < len(group.groupIn):
                    return True


    def invoke(self, context, event):
        group = bpy.data.node_groups[self.groupName]

        group.groupIn.remove(group.groupInIndex)

        group.update()
        return {"FINISHED"}


class remove_group_output_socket(Operator):
    """Remove the seleted group output socket"""
    bl_idname = "scene.cm_group_remove_output"
    bl_label = "Remove socket"

    groupName = StringProperty()

    @classmethod
    def poll(cls, context):
        if len(context.space_data.path) > 0:
            group = context.space_data.path[-1].node_tree
            if group.bl_idname == "CrowdMasterGroupTreeType":
                if 0 <= group.groupOutIndex < len(group.groupOut):
                    return True


    def invoke(self, context, event):
        group = bpy.data.node_groups[self.groupName]

        group.groupOut.remove(group.groupOutIndex)

        group.update()
        return {"FINISHED"}


class SOCKET_UL_CrowdMaster_GroupIO(UIList):
    def draw_item(self, context, layout, data, item, icom, active_data, active_propname):
        layout.prop(item, "name")


class GroupIOPanel(Panel):
    """Creates CrowdMaster group input/output editor panel in the node editor."""
    bl_label = "Group IO"
    bl_idname = "SCENE_PT_CrowdMaster_GroupIO"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        path = context.space_data.path
        if len(path) > 0:
            if path[-1].node_tree.bl_idname == "CrowdMasterGroupTreeType":
                return True

    def draw(self, context):
        layout = self.layout

        group = context.space_data.path[-1].node_tree

        row = layout.row()
        row.label("Inputs:")
        i = row.operator("scene.cm_group_remove_input", text="", icon="X")
        i.groupName = group.name
        row.label("Output:")
        o = row.operator("scene.cm_group_remove_output", text="", icon="X")
        o.groupName = group.name

        row = layout.row()
        row.template_list("SOCKET_UL_CrowdMaster_GroupIO", "", group, "groupIn", group, "groupInIndex")
        row.template_list("SOCKET_UL_CrowdMaster_GroupIO", "", group, "groupOut", group, "groupOutIndex")


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

        parent_node = ng.nodes.new("GroupNode")
        parent_node.select = False
        parent_node.groupName = newGroup.name
        # parent_node.location = average_of_selected(nodes)

        # remove nodes from parent_tree
        for n in nodes:
            ng.nodes.remove(n)

        # TODO link the new nodes sockets

        # to make it pretty we pop and then append with the node
        path.pop()
        path.append(newGroup, node=parent_node)

        bpy.ops.node.view_all()

        availableGroups = getCMGroups(self, context)

        for nodeGroup in bpy.data.node_groups:
            if nodeGroup.bl_idname in {"CrowdMasterTreeType", "CrowdMasterGroupTreeType"}:
                for node in nodeGroup.nodes:
                    if node.bl_idname == "GroupNode":
                        if node.editGroupName != node.groupName:
                            if node.editGroupName in availableGroups:
                                node.groupName = node.editGroupName
                            else:
                                node.editGroupName = node.groupName
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

        if node and node.select and node.bl_idname == "GroupNode":
            if node.groupName != "":
                parentTree = node.id_data
                group = bpy.data.node_groups[node.groupName]

                path = context.space_data.path
                if len(path) == 1:
                    path.start(parentTree)
                path.append(group, node=node)
            return {'FINISHED'}
        else:
            if len(context.space_data.path) > 1:
                space = context.space_data
                space.path.pop()
                return {'FINISHED'}

        return {'CANCELLED'}


def getCMGroups(self, context):
    res = []
    for group in context.blend_data.node_groups:
        if group.bl_idname == "CrowdMasterGroupTreeType":
            res.append((group.name,)*3)
    return res

def updateGroupName(self, context):
    if self.editGroupName != self.groupName:
        self.editGroupName = self.groupName
    self.update()

def updateEditGroupName(self, context):
    if self.groupName != self.editGroupName:
        group = bpy.data.node_groups[self.groupName]
        group.name = self.editGroupName
        if group.name != self.editGroupName:
            self.editGroupName = group.name
        self.groupName = group.name


class GroupNode(cm_bpyNodes.CrowdMasterNode):
    """CrowdMaster Group Node"""
    bl_idname = "GroupNode"
    bl_label = "Group"

    groupName = EnumProperty(items=getCMGroups, update=updateGroupName)
    editGroupName = StringProperty(update=updateEditGroupName)

    @classmethod
    def poll(cls, ntree):
        if ntree.bl_idname in {"CrowdMasterTreeType", "CrowdMasterGroupTreeType"}:
            return True

    def init(self, context):
        pass

    @property
    def cm_groupTree(self):
        if self.groupName in bpy.data.node_groups:
            return bpy.data.node_groups[self.groupName]

    def update(self):
        if self.editGroupName != self.groupName:
            ng = bpy.data.node_groups
            if self.editGroupName == "":
                self.editGroupName = self.groupName
            elif self.editGroupName in ng and ng[self.editGroupName].bl_idname == "CrowdMasterGroupTreeType":
                self.groupName = self.editGroupName
            else:
                self.editGroupName = self.groupName
        self.updateSockets()

    def draw_buttons(self, context, layout):
        layout.prop(self, "groupName")
        if self.groupName in bpy.data.node_groups:
            layout.prop(self, "editGroupName")

    def updateSockets(self):
        group = self.cm_groupTree
        if group is None:
            self.inputs.clear()
            self.outputs.clear()
        else:
            count = 0
            while count < len(group.groupIn) and count < len(self.inputs):
                if group.groupIn[count].name != self.inputs[count].name:
                    break
                count += 1
            while count < len(self.inputs):
                if count < len(group.groupIn):
                    socketName = group.groupIn[count].name
                    if self.inputs[count].name == socketName:
                        count += 1
                    else:
                        self.inputs.remove(self.inputs[count])
                else:
                    self.inputs.remove(self.inputs[count])

            while count < len(group.groupIn):
                socketName = group.groupIn[count].name
                self.inputs.new("EmptySocketType", socketName)
                count += 1

            count = 0
            while count < len(group.groupOut) and count < len(self.outputs):
                if group.groupOut[count].name != self.outputs[count].name:
                    break
                count += 1
            while count < len(self.outputs):
                if count < len(group.groupOut):
                    socketName = group.groupOut[count].name
                    if self.outputs[count].name == socketName:
                        count += 1
                    else:
                        self.outputs.remove(self.outputs[count])
                else:
                    self.outputs.remove(self.outputs[count])

            while count < len(group.groupOut):
                socketName = group.groupOut[count].name
                self.outputs.new("EmptySocketType", socketName)
                count += 1


class GroupInputs(cm_bpyNodes.CrowdMasterNode):
    """CrowdMaster Inputs Group Node"""
    bl_idname = "GroupInputs"
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

    def update(self):
        pass


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

    def update(self):
        pass


keyMap = None
keyMapItems = []

def register():
    bpy.utils.register_class(GroupInListing)
    bpy.utils.register_class(GroupOutListing)
    bpy.utils.register_class(CrowdMasterGroupTree)
    bpy.utils.register_class(CrowdMasterCreateFromSelected)
    bpy.utils.register_class(CrowdMasterGroupToggle)
    bpy.utils.register_class(EmptySocket)

    bpy.utils.register_class(GroupNode)
    bpy.utils.register_class(GroupInputs)
    bpy.utils.register_class(GroupOutputs)

    bpy.utils.register_class(remove_group_input_socket)
    bpy.utils.register_class(remove_group_output_socket)
    bpy.utils.register_class(SOCKET_UL_CrowdMaster_GroupIO)
    bpy.utils.register_class(GroupIOPanel)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        global keyMap
        keyMap = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')

        # ctrl+G
        kmi = keyMap.keymap_items.new('node.cm_node_group_from_selected', 'G', 'PRESS', ctrl=True)
        keyMapItems.append(kmi)

        # TAB
        kmi = keyMap.keymap_items.new('node.cm_group_enter_exit', 'TAB', 'PRESS')
        keyMapItems.append(kmi)

def unregister():
    global keyMap
    if keyMap:
        for kmi in keyMapItems:
            try:
                keyMap.keymap_items.remove(kmi)
            except Exception:
                pass
    keyMapItems.clear()

    bpy.utils.unregister_class(GroupInListing)
    bpy.utils.unregister_class(GroupOutListing)
    bpy.utils.unregister_class(CrowdMasterGroupTree)
    bpy.utils.unregister_class(CrowdMasterCreateFromSelected)
    bpy.utils.unregister_class(CrowdMasterGroupToggle)
    bpy.utils.unregister_class(EmptySocket)

    bpy.utils.unregister_class(GroupNode)
    bpy.utils.unregister_class(GroupInputs)
    bpy.utils.unregister_class(GroupOutputs)

    bpy.utils.unregister_class(remove_group_input_socket)
    bpy.utils.unregister_class(remove_group_output_socket)
    bpy.utils.unregister_class(SOCKET_UL_CrowdMaster_GroupIO)
    bpy.utils.unregister_class(GroupIOPanel)
