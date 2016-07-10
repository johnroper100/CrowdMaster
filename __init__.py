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
from . mysql import mysql_general as cmDB
from . nodes.node_register import register_nodes, unregister_nodes
from . icon_load import register_icons, unregister_icons

if bpy.app.version < (2, 76, 0):
    message = ("\n\n"
        "CrowdMaster requires at least Blender 2.77.\n"
        "Please download the latest official release.")
    raise Exception(message)

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

################
# Registration #
################
def register():
    register_icons()
    register_nodes()
    bpy.utils.register_module(__name__)

def unregister():
    unregister_icons()
    unregister_nodes()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
