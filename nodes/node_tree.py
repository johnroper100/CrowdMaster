import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .. import icon_load

class CMNodeTree(NodeTree):
    '''The CrowdMaster node tree'''
    bl_idname = 'CMNodeTree'
    bl_label = 'CrowdMaster'
    bl_icon = 'MOD_REMESH'

class CMNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CMNodeTree'

    import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class CMNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CMNodeTree'

node_categories = [
    # identifier, label, items list
    CMNodeCategory("SOMENODES", "Some Nodes", items=[
        # our basic node
        NodeItem("CMTimeInfoNode"),
        ]),CMNodeCategory
    ]

def register():
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)

def unregister():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")

if __name__ == "__main__":
    register()
