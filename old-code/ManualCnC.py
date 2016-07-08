import bpy, sqlite3

def ManualCnC():
	actors=Blender.Object.GetSelected()

	if actors==[]:
		print 'You must make a selection.'
	else:
		commandObject=actors.pop(0)
		commandName=commandObject.getName()
		SQLCommander='SELECT ID, ObjectName FROM tblActors WHERE ObjectName="' + commandName + '"'
		bpy.dbCursor.execute(SQLCommander)
		[CommanderID, ReturnName]=bpy.dbCursor.fetchone()
		for actor in actors:
			actorName=actor.getName()
			SQLAssign='UPDATE tblActors SET CommanderID=' + str(CommanderID) + ' WHERE ObjectName="' + actorName + '"'
			bpy.dbCursor.execute(SQLAssign)

		print
		print 'Actors assigned to Commander ' + commandName + '.'
