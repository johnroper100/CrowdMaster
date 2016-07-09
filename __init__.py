bl_info = {
    "name": "CrowdMaster",
    "author": "John Roper",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "Toobar > CrowdMaster",
    "description": "Blender crowd simulation",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Simulation"
}

import bpy
import sys
sys.path.append('C:\Python35\Lib\site-packages')
sys.path.append('C:\Python35\DLLs')
import pymysql

from . import cm_prefs
from . import mysql
from . import nodes
from . mysql import mysql_general as cmDB
from . nodes import node_tree as nTree

class CMInitDatabase(bpy.types.Operator):
    """Init the CrowdMaster mysql database"""
    bl_idname = "scene.cm_init_database"
    bl_label = "Init Database"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.user_preferences.addons[__package__].preferences

        conn, cursor = cmDB.dbConnect(preferences.databaseName, preferences.databaseHost, preferences.databaseUsername, preferences.databasePassword)
        
        cmDB.dbVersion(conn, cursor)
        
        # Sample SQL to make sure everything works
        cursor.execute("DROP TABLE IF EXISTS ACTORS")
        actorSql = """CREATE TABLE ACTORS (
         FIRST_NAME  CHAR(20) NOT NULL,
         LAST_NAME  CHAR(20),
         AGE INT,  
         SEX CHAR(1),
         INCOME FLOAT )"""
        cursor.execute(actorSql)
        
        cmDB.dbClose(conn, cursor)

        return {'FINISHED'}

class CMPanelMain(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "CrowdMaster"
    bl_label = "Main"
    def draw(self, context):
        layout = self.layout
        preferences = context.user_preferences.addons[__package__].preferences
        
        if (preferences.databaseName == "") or (preferences.databaseHost == "") or (preferences.databaseUsername == "") or (preferences.databasePassword == ""):
            layout.enabled = False
        
        row = layout.row()
        row.operator("scene.cm_init_database")

################
# Registration #
################
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
