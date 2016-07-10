import bpy
from bpy.types import NodeTree, Node, NodeSocket

class CrowdMasterTree(NodeTree):
    '''The CrowdMaster node tree'''
    bl_idname = 'CrowdTreeType'
    bl_label = 'CrowdMaster'
    bl_icon = 'MOD_REMESH'
