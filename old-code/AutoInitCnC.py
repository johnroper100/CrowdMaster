import bpy, sqlite3

def AutoInitCnC():
	#Start from lowest level, work up
	CnCTypes=['a','b','c','d','e','f']
	CnCLoop=['a','b','c','d','e']
	for cncLevel in CnCLoop:
		cncUp = CnCTypes[CnCTypes.index(cncLevel)+1]
		SQLCheck='SELECT ID, ObjectName FROM tblActors WHERE MID(ObjectName,5,1)="' + cncUp + '"'
		bpy.dbCursor.execute(SQLCheck)
		SQLResult=bpy.dbCursor.fetchall()
		if SQLResult is ():
			#done processing - we've run out of C&C levels
			#AttachInsert='UPDATE tblActors SET CommanderID=ID WHERE MID(ObjectName,5,1)="' + cncLevel + '"'
			#bpy.dbCursor.execute(AttachInsert)
			pass
		else:
			#There are C&C levels above the current one - populate based on nearest CnC unit algorithm
			SQLCheck='SELECT ID, Team, ObjectName, x, y FROM tblActors WHERE Mid(ObjectName,5,1)="' + cncLevel + '"'
			bpy.dbCursor.execute(SQLCheck)
			cncList=bpy.dbCursor.fetchall() #get list of all actors at the current cnc level
			for cncActor in cncList:
				#print cncActor
				NearCheck='SELECT ID, Team, ObjectName, sqrt(((x - ' + str(cncActor[3]) + ') * (x - ' + str(cncActor[3]) + ')) + ((y - ' + str(cncActor[4]) + ') * (y - ' + str(cncActor[4]) + '))) as Distance FROM tblActors WHERE Team="' + cncActor[1] + '" AND MID(ObjectName,5,1)="' + cncUp + '" ORDER BY Distance'
				bpy.dbCursor.execute(NearCheck)
				NearestCnC=bpy.dbCursor.fetchone()
				AttachInsert='UPDATE tblActors SET CommanderID=' + str(NearestCnC[0]) + ', Orders="Defend" WHERE ID=' + str(cncActor[0])
				bpy.dbCursor.execute(AttachInsert)

	outMessage = 'CnC Initialized to nearest Commanders.'
	print (outMessage)
	return outMessage
