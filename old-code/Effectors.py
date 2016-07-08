import bpy, string, random, time
from math import *

def CheckEffectors(): #check permanent effectors
	startTime=time.time()
	EffCount=0
	thisFrame=bpy.context.scene.frame_current
	
	SQLQuery='SELECT EffectorName,Affects,AffectsValue,Attribute,Operator,Action,Value,Duration FROM tblEffectors WHERE Active=1 AND Duration="Permanent"'
	bpy.dbCursor.execute(SQLQuery)
	SQLResult=bpy.dbCursor.fetchall()
	
	if (SQLResult): #Go through each relevant Effector in the db
		for Effector in SQLResult:
			EffCount+=1
			Name=Effector[0]
			Affects=Effector[1]
			AffectsValue=Effector[2]
			Attribute=Effector[3]
			Operator=Effector[4]
			Action=Effector[5]
			Value=Effector[6]
			
			#Find the Effectors current location and size
			try:
				EffObject=bpy.data.objects[Name]
			except:
				print ("Please remove Effector '" + Name + "' from the database.")
				continue
			EffMatrix=EffObject.getMatrix('worldspace')
			EffLoc=EffMatrix[3]
			EffScale=EffObject.getSize()
			EffSize=(EffScale[0]+EffScale[1]+EffScale[2])/3
			
			#build the query string to find out which Actors to affect
			if (Affects=='All'):
				AffectString = ''
			else:
				AffectString = 'tblActors.' + Affects + ' = "' + AffectsValue + '" AND '
			
			WhereString = AffectString + 'SQRT(POWER(tblActors.x-' + str(EffLoc[0]) + ',2) + POWER(tblActors.y-' + str(EffLoc[1]) + ',2)) < ' + str(EffSize)
				
			if (Operator=='SetTo'):
				EffSQL='UPDATE tblActors SET ' + Attribute + '=' + str(Value) + ' WHERE ' + WhereString
			else:
				EffSQL='UPDATE tblActors SET ' + Attribute + '=' + Attribute + Operator + str(Value) + ' WHERE ' + WhereString
			bpy.dbCursor.execute(EffSQL)
		
			#write to the actions log if necessary
			if (Action) and (Action!='None'):
				logInsert='INSERT INTO tblActions (ActorID,Frame,Action,Orders) SELECT '
				logInsert+='ID, ' + str(thisFrame) + ', "' + Action + '","Effector" FROM tblactors WHERE (' + WhereString + ')'
				bpy.dbCursor.execute(logInsert)
			
			#update the effector location in the db for use with temporary effectors
			EffSQL='UPDATE tblEffectors SET x=' + str(EffLoc[0]) + ', y=' + str(EffLoc[1]) + ' WHERE EffectorName="' + Name + '"'
			bpy.dbCursor.execute(EffSQL)
			
	EffSQL='SELECT EffectorName, Duration, Active FROM tblEffectors WHERE Duration="Temporary" and Active=1'
	bpy.dbCursor.execute(EffSQL)
	TempEffectors=bpy.dbCursor.fetchall()
	
	#update locations of temporary effectors in the db
	if (TempEffectors):
		for Effector in TempEffectors:
			EffObject=bpy.data.objects[Effector[0]]
			EffMatrix=EffObject.getMatrix('worldspace')
			EffLoc=EffMatrix[3]
			EffScale=EffObject.getSize()
			EffSize=(EffScale[0]+EffScale[1]+EffScale[2])/3
			EffSQL='UPDATE tblEffectors SET x=' + str(EffLoc[0]) + ', y=' + str(EffLoc[1]) + ', Size=' + str(EffSize) + ' WHERE EffectorName="' + Effector[0] + '"'
			bpy.dbCursor.execute(EffSQL)

	if (EffCount==0):
		outMessage=None
	else:
		outMessage=str(EffCount) + ' Effectors in ' + str(time.time()-startTime) + ' secs.'
		print (outMessage)
	return outMessage
