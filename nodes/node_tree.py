import bpy
from bpy.props import *
from bpy.types import NodeTree, Node, NodeSocket
from .. import icon_load

class CMNodeTree(NodeTree):
    '''The CrowdMaster node tree'''
    bl_idname = 'cm_NodeTree'
    bl_label = 'CrowdMaster'
    bl_icon = 'MOD_REMESH'

class CrowdNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'cm_NodeTree'

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class CMNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'cm_NodeTree'

node_categories = [
    # identifier, label, items list
    CMNodeCategory("SOMENODES", "Some Nodes", items=[
        # our basic node
        NodeItem("CustomNodeType"),
        ]),
    CMNodeCategory("OTHERNODES", "Other Nodes", items=[
        # the node item can have additional settings,
        # which are applied to new nodes
        # NB: settings values are stored as string expressions,
        # for this reason they should be converted to strings using repr()
        NodeItem("CustomNodeType", label="Node A", settings={
            "myStringProperty": repr("Lorem ipsum dolor sit amet"),
            "myFloatProperty": repr(1.0),
            }),
        NodeItem("CustomNodeType", label="Node B", settings={
            "myStringProperty": repr("consectetur adipisicing elit"),
            "myFloatProperty": repr(2.0),
            }),
        ]),
    ]

def register():
    nodeitems_utils.register_node_categories("CM_NODES", node_categories)
    bpy.utils.register_module(__name__)

def unregister():
    nodeitems_utils.unregister_node_categories("CM_NODES")
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
