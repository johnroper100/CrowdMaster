import bpy, sqlite3

def MakeConnection():
	#initialize sqlite3 connection and cursor
	dbConn = sqlite3.connect("dbactors")
	dbCursor = dbConn.cursor()

	#register the sqlite3 cursor in the Blender object for other scripts to use
	bpy.dbCursor = dbCursor
