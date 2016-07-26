import bpy

def getActor(actorObject):
	SQL='SELECT ID, Type, Team, ObjectName, OrderSpeed, Orders, CommanderID, '
	SQL+='Speed, Attack, Defense, Intellect, Health, FieldofView, MaxTurn, '
	SQL+='Weapon, AttackRadius, ChargeRadius, CowardRadius, BuddyRadius, '
	SQL+='Loyalty, ActorRadius, Pathmode FROM tblActors WHERE ObjectName = "' + actorObject.getName() + '"'
	bpy.dbCursor.execute(SQL)

	actorStats = bpy.dbCursor.fetchone()

	if actorStats == None:
		return -1
	else:
		return actorStats

def selfCommander(ID):
	SQL='UPDATE tblActors SET CommanderID=' + str(ID) + ' WHERE ID=' + str(ID)
	bpy.dbCursor.execute(SQL)
	return 'Set to self-commanding.'
	
def getEffector(effObject):
	SQL='SELECT EffectorName, Affects, AffectsValue, Attribute, Operator, Value, Action, Active, Duration FROM tblEffectors '
	SQL+='WHERE EffectorName = "' + effObject.getName() + '"'
	bpy.dbCursor.execute(SQL)
	
	effStats = bpy.dbCursor.fetchone()
	
	if effStats == None:
		return -1
	else:
		return effStats
	
def setEffector(EffectorName,Affects,AffectsValue,Attribute,Operator,Value,Action,Active,Duration):
	SQL='UPDATE tblEffectors SET Affects="' + Affects + '", AffectsValue="' + AffectsValue + '", Attribute="' + Attribute
	SQL+='", Operator="' + Operator + '", Value=' + str(Value) + ', Action="' + Action + '", Active=' + str(Active)
	SQL+=', Duration="' + Duration + '" WHERE EffectorName="' + EffectorName +'"'
	bpy.dbCursor.execute(SQL)
	return('Updated stats for ' + EffectorName + '.')

def createEffector(EffectorName,Affects,AffectsValue,Attribute,Operator,Value,Action,Active,Duration):
	SQL='INSERT INTO tblEffectors (EffectorName,Affects,AffectsValue,Attribute,Operator,Value,Action,Active,Duration) SELECT '
	SQL+='"' + EffectorName + '","' +  Affects + '","' + AffectsValue + '","' + Attribute + '","' + Operator + '",'
	SQL+=str(Value) + ',"' + Action + '",' +  str(Active) + ', "'+ Duration + '"'
	bpy.dbCursor.execute(SQL)
	return('Registered ' + EffectorName + ' as Effector.')

def setActor(actorStats):
	#print (actorStats)
	SQL='UPDATE tblActors SET Type="' + actorStats[1] + '", Team="' + actorStats[2] + '", OrderSpeed=' + str(actorStats[4]) + ', Orders="' + actorStats[5] + '", CommanderID=' + str(actorStats[6]) + ', '
	SQL+='Speed=' + str(actorStats[7]) + ', Attack=' + str(actorStats[8]) + ', Defense=' + str(actorStats[9]) + ', Intellect=' + str(actorStats[10]) + ', Health=' + str(actorStats[11]) + ', '
	SQL+='FieldofView=' + str(actorStats[12]) + ', MaxTurn=' + str(actorStats[13]) + ', Weapon="' + actorStats[14] + '", AttackRadius=' + str(actorStats[15]) + ', ChargeRadius=' + str(actorStats[16])
	SQL+=', CowardRadius=' + str(actorStats[17]) + ', BuddyRadius=' + str(actorStats[18]) + ', Loyalty=' + str(actorStats[19]) + ', '
	SQL+='ActorRadius=' + str(actorStats[20]) + ', Pathmode="' + actorStats[21] + '" WHERE ID=' + str(actorStats[0])
	bpy.dbCursor.execute(SQL)

	return 'Stats entered into database.'

def getType(actorType):
	SQL='SELECT TypeID,TypeName,Speed,SpeedV,AttackRadius,AttackRadiusV,ChargeRadius,'
	SQL+='ChargeRadiusV,CowardRadius,CowardRadiusV,BuddyRadius,BuddyRadiusV,Health,'
	SQL+='HealthV,Attack,AttackV,Defense,DefenseV,Intellect,IntellectV,FieldofView,'
	SQL+='FieldofViewV,MaxTurn,MaxTurnV,ActorRadius FROM tblTypes WHERE '
	SQL+='TypeID = "' + actorType + '"'
	bpy.dbCursor.execute(SQL)

	typeStats = bpy.dbCursor.fetchone()

	if typeStats == None:
		return -1
	else:
		return typeStats

def newType():
	SQL='SELECT TypeID FROM tblTypes ORDER BY TypeID DESC'
	bpy.dbCursor.execute(SQL)
	lastType = bpy.dbCursor.fetchone()
	if lastType is None:
		nextType = 'a'
	else:
		nextType = chr(ord(str(lastType[0]))+1)
	SQL='INSERT INTO tblTypes (TypeID,TypeName) SELECT "' + nextType + '", "Name"'
	bpy.dbCursor.execute(SQL)
	return nextType

def setType(typeStats,original):
	SQL='UPDATE tblTypes SET TypeID="' + str(typeStats[0]) + '",TypeName="' + str(typeStats[1]) + '",Speed=' + str(typeStats[2]) + ',SpeedV=' + str(typeStats[3]) + ',AttackRadius=' + str(typeStats[4]) + ',AttackRadiusV=' + str(typeStats[5]) + ','
	SQL+='ChargeRadius=' + str(typeStats[6]) + ',ChargeRadiusV=' + str(typeStats[7]) + ',CowardRadius=' + str(typeStats[8]) + ',CowardRadius=' + str(typeStats[9]) + ','
	SQL+='BuddyRadius=' + str(typeStats[10]) + ',BuddyRadiusV=' + str(typeStats[11]) + ',Health=' + str(typeStats[12]) + ',HealthV=' + str(typeStats[13]) + ',Attack=' + str(typeStats[14]) + ',AttackV=' + str(typeStats[15]) + ','
	SQL+='Defense=' + str(typeStats[16]) + ',DefenseV=' + str(typeStats[17]) + ',Intellect=' + str(typeStats[18]) + ',IntellectV=' + str(typeStats[19]) + ',FieldofView=' + str(typeStats[20]) + ',FieldofViewV=' + str(typeStats[21]) + ','
	SQL+='MaxTurn=' + str(typeStats[22]) + ',MaxTurnV=' + str(typeStats[23]) + ',ActorRadius=' + str(typeStats[24]) + ' WHERE TypeID = "' + str(original) + '"'
	print (SQL)
	bpy.dbCursor.execute(SQL)
	return ('Type "' + str(original) + '" has been set.')
