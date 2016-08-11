import bpy
import sys
from .. import icon_load
from . import options
from .generation import generate_agents_random, generate_agents_array

class CrowdMaster_generate_agents(bpy.types.Operator):
    bl_idname = "scene.cm_gen_agents"
    bl_label = "Generate Agents"

    def execute(self, context):
        scene = context.scene
        if scene.use_agent_generation == True:
            if scene.positionMode == "vector":
                vector = [scene.positionVector[0], scene.positionVector[1]]
            elif scene.positionMode == "object":
                objStart = bpy.data.objects[scene.positionObject]
                vector = [objStart.location.x, objStart.location.y]
            elif scene.positionMode == "scene":
                vector = 0

            if scene.positionType == "random":
                generate_agents_random(vector)

            if scene.positionType == "formation":
                if scene.formationPositionType == "array":
                    generate_agents_array(vector)
                    
            if scene.add_to_agent_list == True:
                bpy.ops.scene.cm_agents_populate()
            
            if scene.group_all_agents == True:
                bpy.ops.group.create(name="CrowdMaster Agents")
                bpy.ops.object.group_link(group="CrowdMaster Agents") 

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600)
    
    def check(self, context):
        scene = context.scene
        if scene.use_rand_rot is True:
            return True
        if scene.use_rand_scale is True:
            return True
        if scene.use_rand_rot is False:
            return True
        if scene.use_rand_scale is False:
            return True
        if scene.use_rand_animation is True:
            return True
        if scene.use_rand_animation is False:
            return True
        if scene.positionMode != scene.positionMode:
            return True
        if scene.positionType != scene.positionType:
            return True
        if scene.formationPositionType != scene.formationPositionType:
            return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        box = layout.box()
        
        pcoll = icon_load.icon_collection["main"]
        def cicon(name):
            return pcoll[name].icon_id

        row = box.row()
        row.label("General:", icon='FILE_TICK')

        row = box.row()
        row.prop(scene, "agentNumber")
        
        row = box.row()
        row.prop(scene, "add_to_agent_list")
        row.prop(scene, "group_all_agents")

        if scene.positionMode == "vector":
            row = box.row()
            row.prop(scene, "positionVector")

        elif scene.positionMode == "object":
            row = box.row()
            row.prop_search(scene, "positionObject", scene, "objects")
        
        box = layout.box()
        
        row = box.row()
        row.label("Obstacles:", icon='MESH_ICOSPHERE')
        
        row = box.row()
        row.prop(scene, "obstacleGroup")
        
        box = layout.box()
        
        row = box.row()
        row.label("Positioning:", icon='MANIPUL')
        
        row = box.row()
        row.prop(scene, "positionMode")

        row = box.row()
        row.prop(scene, "positionType")

        #if scene.positionType == "formation":
            #row = box.row()
            #row.prop(scene, "formationPositionType")
        
        box = layout.box()
        
        row = box.row()
        row.label("Randomization:", icon='FILE_REFRESH')

        row = box.row()
        row.prop(scene, "use_rand_rot")

        row = box.row(align=True)
        row.alignment = 'EXPAND'
        if scene.use_rand_rot == False:
            row.enabled = False
        row.prop(scene, "minRandRot")
        row.prop(scene, "maxRandRot")
        
        row = box.row()
        row.prop(scene, "use_rand_scale")

        row = box.row(align=True)
        row.alignment = 'EXPAND'
        if scene.use_rand_scale == False:
            row.enabled = False
        row.prop(scene, "minRandSz")
        row.prop(scene, "maxRandSz")
        
        row = box.row()
        row.prop(scene, "use_rand_animation")

        row = box.row()
        if scene.use_rand_animation == False:
            row.enabled = False
        row.prop_search(scene, "agentAction1", bpy.data, "actions")

        row = box.row()
        if scene.use_rand_animation == False:
            row.enabled = False
        row.prop_search(scene, "agentAction2", bpy.data, "actions")

        row = box.row()
        if scene.use_rand_animation == False:
            row.enabled = False
        row.prop_search(scene, "agentAction3", bpy.data, "actions")
        
        row = box.row()
        if scene.use_rand_animation == False:
            row.enabled = False
        row.prop_search(scene, "agentAction4", bpy.data, "actions")
        
        row = box.row()
        if scene.use_rand_animation == False:
            row.enabled = False
        row.prop_search(scene, "agentAction5", bpy.data, "actions")

        if scene.positionType == "random":
            box = layout.box()
            
            row = box.row()
            row.label("Random Positioning:", icon='FCURVE')
    
            if scene.positionMode == "scene":
                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(scene, "randomPositionMinX")
                row.prop(scene, "randomPositionMaxX")

                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(scene, "randomPositionMinY")
                row.prop(scene, "randomPositionMaxY")
            
            else:
                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(scene, "randomPositionMaxX")
                row.prop(scene, "randomPositionMaxY")
        
        if scene.positionType == "formation":
            box = layout.box()
            
            row = box.row()
            row.label("Formation Positioning:", icon='FCURVE')

            if scene.formationPositionType == "array":
                row = box.row()
                row.prop(scene, "formationArrayRows")
                
                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.prop(scene, "formationArrayRowMargin")
                row.prop(scene, "formationArrayColumnMargin")
