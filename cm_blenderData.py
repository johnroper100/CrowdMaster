import bpy
from bpy.props import IntProperty, EnumProperty, CollectionProperty
from bpy.props import PointerProperty, BoolProperty, StringProperty
from bpy.types import PropertyGroup, UIList, Panel, Operator

# =============== DATA START===============#

d = [('NONE', """{'edges': [], 'nodes': {}}"""),
     ('GROUND', """{'edges': [{'source': 0, 'dest': 1}], 'nodes': {0:
      {'frameparent': (None,), 'posx': 0.0, 'category': ('SETTAG', ['INPUT',
      'GRAPH', 'AND', 'OR', 'QUERYTAG', 'SETTAG', 'VARIABLE', 'MAP', 'OUTPUT',
      'EVENT', 'PYTHON', 'PRINT']), 'posy': 0.0, 'settings':
      OrderedDict([('Tag', 'Ground'), ('Use threshold', True), ('Threshold',
      0.0), ('Action', ('Add', ('Add', 'Remove'))), ('Value', 1)]),
      'UID': 0, 'displayname': 'settag Ground', 'type': 'LogicNode'},
      1: {'frameparent': (None,), 'posx': -192.0, 'category': ('INPUT',
      ['INPUT', 'GRAPH', 'AND', 'OR', 'QUERYTAG', 'SETTAG', 'VARIABLE',
      'MAP', 'OUTPUT', 'EVENT', 'PYTHON', 'PRINT']), 'posy': -0.9, 'settings':
      OrderedDict([('Input', '1')]), 'UID': 1, 'displayname': '1',
      'type': 'LogicNode'}}}""".replace("/n", ""))]

default_slots = d


class brain_entry(PropertyGroup):
    """The data that is saved for each of the brain types"""
    identify = StringProperty(default="")
    dispname = StringProperty(default="")
    brain = StringProperty(default="")


def setcmBrains():
    """loads the brains from the .blend or creates them if they don't already
    exist"""
    for b in default_slots:
        if b[0] not in [br.dispname for br in bpy.context.scene.cm_brains]:
            item = bpy.context.scene.cm_brains.add()
            item.identify = b[0]
            item.dispname = b[0]
            item.brain = b[1]
    cm_brains = bpy.context.scene.cm_brains
    print("Loaded brains", cm_brains)


def updateagents(self, context):
    bpy.ops.scene.cm_groups_populate()
    bpy.ops.scene.cm_selected_populate()


class agent_entry(PropertyGroup):
    """The data structure for the agent entries"""
    type = StringProperty(update=updateagents)
    group = IntProperty(update=updateagents)


class agents_collection(PropertyGroup):
    """cm_agents, cm_agents_selected"""
    coll = CollectionProperty(type=agent_entry)
    index = IntProperty()


class default_agents_type(PropertyGroup):
    """Properties that define how new objects will be assigned groups"""
    startType = EnumProperty(
        items=(
            ('Next', 'Next Free', ''),
            ('Set', 'Set to', '')
        )
    )
    contType = EnumProperty(
        items=(
            ('Same', 'All the same', ''),
            ('Inc', 'Increment next available', '')
        )
    )
    setno = IntProperty(min=1)


def setcmAgents():
    """register cm_agents type with blender"""
    PP = PointerProperty
    bpy.types.Scene.cm_agents = PP(type=agents_collection)
    bpy.types.Scene.cm_agents_selected = PP(type=agents_collection)
    bpy.types.Scene.cm_agents_default = PP(type=default_agents_type)


def GroupChange(self, context):
    """callback for changing the type of one of the groups"""
    for agent in bpy.context.scene.cm_agents.coll:
        if str(agent.group) == self.name:
            agent.type = self.type


class group_entry(PropertyGroup):
    """The data structure for the group entries"""
    type = StringProperty()
    group = IntProperty(min=0)
    # TODO the group isn't actually used... it's the name that is used


class groups_collection(PropertyGroup):
    coll = CollectionProperty(type=group_entry)
    index = IntProperty()


def setcmGroups():
    """register cm_groups type with blender"""
    bpy.types.Scene.cm_groups = PointerProperty(type=groups_collection)


def update_cm_brains(brains):
    # TODO not used anymore?
    """passed to the GUI so that it can update the brain types"""
    cm_brains = bpy.context.scene.cm_brains
    idents = {}
    for x in cm_brains:
        idents[x.identify] = x
    # print("brains", brains)
    for bb in brains:
        if bb[0] in idents:
            # print("Brain", bb[0], "modified")
            idents[bb[1].upper()].identify = bb[1].upper()
            idents[bb[1].upper()].dispname = bb[1]
            idents[bb[1].upper()].brain = bb[2]
        else:
            # print("New brain", bb[0], "added")
            item = cm_brains.add()
            item.identify = bb[1].upper()
            item.dispname = bb[1]
            item.brain = bb[2]
    setcmBrains()
    for g in bpy.context.scene.cm_groups.coll:
        if g.type not in [x.identify for x in cm_brains]:
            g.type = cm_brains[0][1].upper()
            # print(g, g.type)

registered = False


def registerTypes():
    """register all types"""
    global registered
    if not registered:
        # bpy.utils.register_module(__name__)
        # I think this registers the SCENE_PT_CrowdMaster class...
        # ...or maybe all the classes in the file?
        bpy.utils.register_class(brain_entry)
        bpy.utils.register_class(agent_entry)
        bpy.utils.register_class(agents_collection)
        bpy.utils.register_class(default_agents_type)
        bpy.utils.register_class(group_entry)
        bpy.utils.register_class(groups_collection)
        registered = True
        setcmGroups()
        setcmAgents()
        bpy.types.Scene.cm_brains = CollectionProperty(type=brain_entry)


def unregisterAllTypes():
    # bpy.utils.unregister_module(__name__)
    # ...and this one unregisters the SCENE_PT_CrowdMaster
    bpy.utils.unregister_class(brain_entry)
    bpy.utils.unregister_class(agent_entry)
    bpy.utils.unregister_class(agents_collection)
    bpy.utils.unregister_class(default_agents_type)
    bpy.utils.unregister_class(group_entry)
    bpy.utils.unregister_class(groups_collection)
    del bpy.types.Scene.cm_agents
    del bpy.types.Scene.cm_groups
    del bpy.types.Scene.cm_agents_selected
    del bpy.types.Scene.cm_agents_default
    del bpy.types.Scene.cm_brains

# =============== DATA END ===============#
