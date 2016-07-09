import bpy
from bpy.types import NodeTree, Node, NodeSocket

class CMNodeTree(NodeTree):
    '''The CrowdMaster node tree'''
    bl_idname = 'CMNodeTree'
    bl_label = 'CrowdMaster'
    bl_icon = 'NODETREE'

def register():
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)

def unregister():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")

if __name__ == "__main__":
    register()
