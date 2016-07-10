import bpy
from bpy.props import *
from bpy.types import NodeTree, Node, NodeSocket

class MyCustomSocket(NodeSocket):
    # Description string
    '''Custom node socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'CustomSocketType'
    # Label for nice name display
    bl_label = 'Custom Node Socket'

    # Enum items list
    my_items = [
        ("DOWN", "Down", "Where your feet are"),
        ("UP", "Up", "Where your head should be"),
        ("LEFT", "Left", "Not right"),
        ("RIGHT", "Right", "Not left")
    ]

    myEnumProperty = bpy.props.EnumProperty(name="Direction", description="Just an example", items=my_items, default='UP')

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "myEnumProperty", text=text)

    # Socket color
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)