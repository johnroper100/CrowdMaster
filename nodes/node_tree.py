import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .. import icon_load
from .. icon_load import cicon

class CMNodeTree(NodeTree):
    '''The CrowdMaster node tree'''
    bl_idname = 'CMNodeTree'
    bl_label = 'CrowdMaster'
    bl_icon = cicon('node_tree_logo')

def register():
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)

def unregister():
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")

if __name__ == "__main__":
    register()
