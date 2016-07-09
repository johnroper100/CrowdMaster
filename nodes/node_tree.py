import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .. import icon_load
from . import node_register

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
        NodeItem("CMTimeInfoNode"),
        ]),
    ]

def register():
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)
    bpy.utils.register_module(__name__)

def unregister():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
