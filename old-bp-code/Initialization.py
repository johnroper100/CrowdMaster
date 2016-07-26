import bpy, sqlite3, string, random, time
from math import *
from bpy import NMesh, Window, Draw
from array import array
import BuildTree

def sgn(value):
	if value>0:
		return 1
	elif value<0:
		return -1
	else:
		return 0

def sgn2(value):
	if value>0:
		return 1
	else:
		return -1

def sideofline(PA,PB,PP):
	return ((PA[0]-PP[0])*(PB[1]-PP[1]))-((PB[0]-PP[0])*(PA[1]-PP[1]))

def InsideQuad(p0,p1,p2,p3,p4):
	if (sideofline(p1,p3,p0)>=0):
		return (sideofline(p1,p4,p0)<=0) and (sideofline(p4,p3,p0)<=0)
	else:
		return (sideofline(p1,p2,p0)>=0) and (sideofline(p2,p3,p0)>=0)

def InsideTri(p0,p1,p2,p3):
	return (sideofline(p1,p2,p0)>=0) and (sideofline(p2,p3,p0)>=0) and (sideofline(p3,p1,p0)>=0)

def FindZ(TriangleFace,tx,ty,tz,px,py):
	[A,B,C]=TriangleFace.no
	D=-((A*tx)+(B*ty)+(C*tz))
	return -((A*px)+(B*py)+D)/C

def InverseTranslate(InCoords,DeltaVec):
	return [InCoords[0]+DeltaVec[0],InCoords[1]+DeltaVec[1],InCoords[2]+DeltaVec[2]]

def FindZCoords(A,B,C,tx,ty,tz,px,py):
	D=-((A*tx)+(B*ty)+(C*tz))
	return -((A*px)+(B*py)+D)/C
	
def getZFaceList(facelist,actorx,actory):
	MeshZ = -200.0
	#find which face the object is over - if the
	#object isn't over a ground face, do nothing
	#print ('Faces:',len(facelist))
	for GroundVerts in facelist:
		#check for quad faces
		#print ('quad face')
		[x1,y1,z1] = [GroundVerts[0],GroundVerts[1],GroundVerts[2]]
		[x2,y2,z2] = [GroundVerts[3],GroundVerts[4],GroundVerts[5]]
		[x3,y3,z3] = [GroundVerts[6],GroundVerts[7],GroundVerts[8]]
		[x4,y4,z4] = [GroundVerts[9],GroundVerts[10],GroundVerts[11]]
		p0=[actorx,actory,0]
		p1=[x1,y1,0]
		p2=[x2,y2,0]
		p3=[x3,y3,0]
		p4=[x4,y4,0]
		if InsideQuad(p0,p1,p2,p3,p4):
			MeshZ = FindZCoords(GroundVerts[12],GroundVerts[13],GroundVerts[14],x1,y1,z1,actorx,actory)			
	if MeshZ == -200: # No face found that matches
		#print ('no face found')
		return MeshZ
	return MeshZ

def getZFromTree(location,gb0,gb1,gb2,gb3):
	#startTime=time.time()
	[x,y,z]=location
	qx=array('i')
	qy=array('i')
	#firstsubdiv
	for counter in [0,1,2,3]:
		centerpointx=(gb0+gb1)/2
		centerpointy=(gb2+gb3)/2
		#print (centerpointx,centerpointy)
		qx.append(sgn2(x-centerpointx))
		qy.append(sgn2(y-centerpointy))
		if qx[counter]==1:
			gb0=centerpointx
		else:
			gb1=centerpointx
		if qy[counter]==1:
			gb2=centerpointy
		else:
			gb3=centerpointy
	#sqlCheck='SELECT fx1,fy1,fz1,fx2,fy2,fz2,fx3,fy3,fz3,fx4,fy4,fz4,fnx,fny,fnz FROM tblGroundTree WHERE (x1=' + str(qx[0]) + ' AND y1=' + str(qy[0]) + ' AND x2=' + str(qx[1]) + ' AND y2=' + str(qy[1]) + ' AND x3=' + str(qx[2]) + ' AND y3=' + str(qy[2]) + ' AND x4=' + str(qx[3]) + ' AND y4=' + str(qy[3]) + ')'
	#bpy.dbCursor.execute(sqlCheck)
	#facelist=bpy.dbCursor.fetchall()
	try:Blender.
		facelist=bpy.globalGround[str(qx[0])+str(qy[0])+str(qx[1])+str(qy[1])+str(qx[2])+str(qy[2])+str(qx[3])+str(qy[3])]
	except:
		BuildTree.BuildTree()
		BuildTree.loadTree()
		facelist=bpy.globalGround[str(qx[0])+str(qy[0])+str(qx[1])+str(qy[1])+str(qx[2])+str(qy[2])+str(qx[3])+str(qy[3])]
	#print ('ZLookup: ' + str(bpy.context.scene.frame_current) + ' in ' + str(time.time()-startTime) + ' seconds')
	return getZFaceList(facelist,x,y)
				
def getZFromMesh(groundmesh,actorx,actory,bounds,InvVec):
	#is the Actor above the ground's bounding box?
	MeshZ = -200
	if ((actorx <= bounds[1]) and (actorx >= bounds[0]) and (actory >=bounds[2]) and (actory <= bounds[3])):
		#find which face the object is over - if the
		#object isn't over a ground face, do nothing
		GroundFaces = groundmesh.faces
		for GroundFace in GroundFaces:
			GroundVerts = GroundFace.v
			if len(GroundVerts) == 4:
				#use on quad faces
				[x1,y1,z1] = InverseTranslate(GroundVerts[0].co,InvVec)
				[x2,y2,z2] = InverseTranslate(GroundVerts[1].co,InvVec)
				[x3,y3,z3] = InverseTranslate(GroundVerts[2].co,InvVec)
				[x4,y4,z4] = InverseTranslate(GroundVerts[3].co,InvVec)
				p0=[actorx,actory,0]
				p1=[x1,y1,0]
				p2=[x2,y2,0]
				p3=[x3,y3,0]
				p4=[x4,y4,0]
				if InsideQuad(p0,p1,p2,p3,p4):
					MeshZ = FindZ(GroundFace,x1,y1,z1,actorx,actory)			
			else:
				print ('Checking Tri Face! Ugh!')
				#use on tri faces
				[x1,y1,z1] = GroundVerts[0].co
				[x2,y2,z2] = GroundVerts[1].co
				[x3,y3,z3] = GroundVerts[2].co
				p0=[actorx,actory,0]	
				p1=[x1,y1,0]
				p2=[x2,y2,0]
				p3=[x3,y3,0]
				if InsideTri(p0,p1,p2,p3):
					MeshZ = FindZ(GroundFace,x1,y1,z1,actorx,actory)
	return MeshZ

def Initialize(dbCursor):
	#try:
		#import psyco
		#psyco.full()
	#except:
		#print ("You should download and install psyco for Python... it'll speed things up!")
	startTime=time.time()
	objectlist=bpy.data.objects[]
	objectCount=len(objectlist)	
	random.seed()
	resolution=12
	Blender.resolution=resolution
	totalActors=0

	Window.DrawProgressBar(0,'Initializing...')

	# Initialize objects for dropping to ground
	try:
		Ground = bpy.data.objects["Ground"]
	except:
		return 'PROBLEM: No object named Ground.'
	InvVec = Ground.getLocation()

	#determine min and max bounding values of the ground object	
	#so we can ignore objects not even over the ground
	GroundBounds = Ground.getBoundBox()
	GB = [0.0,0.0,0.0,0.0]
	GB[0] = min(GroundBounds[0][0],GroundBounds[1][0],GroundBounds[2][0],GroundBounds[3][0],GroundBounds[4][0],GroundBounds[5][0],GroundBounds[6][0],GroundBounds[7][0])
	GB[1] = max(GroundBounds[0][0],GroundBounds[1][0],GroundBounds[2][0],GroundBounds[3][0],GroundBounds[4][0],GroundBounds[5][0],GroundBounds[6][0],GroundBounds[7][0])
	GB[2] = min(GroundBounds[0][1],GroundBounds[1][1],GroundBoBlender.unds[2][1],GroundBounds[3][1],GroundBounds[4][1],GroundBounds[5][1],GroundBounds[6][1],GroundBounds[7][1])
	GB[3] = max(GroundBounds[0][1],GroundBounds[1][1],GroundBounds[2][1],GroundBounds[3][1],GroundBounds[4][1],GroundBounds[5][1],GroundBounds[6][1],GroundBounds[7][1])

	#clear and set Orders
	dbCursor.execute('DELETE tblOrders.* FROM tblOrders')
	dbCursor.execute('INSERT INTO tblOrders (Team,Orders,SpeedMultilpier) SELECT "a","Attack",1')
	dbCursor.execute('INSERT INTO tblOrders (Team,Orders,SpeedMultilpier) SELECT "b","Attack",1')

	#clear the actor database
	dbCursor.execute('DELETE tblActors.* FROM tblActors')

	#clear the Actions database
	dbCursor.execute('DELETE tblActions.* FROM tblActions')

	#Populate database with Actor object information
	#Naming convention:
	#WRabc - WR indicates active character, a is team, b is actor type, c is command level (a is lowest z is highest)
	for Actor in objectlist:
		actorName = Actor.getName()
		if string.find(actorName,'WR')==0: #Use this object
			totalActors = totalActors + 1
			if (totalActors/100.0)==(totalActors/100):
				print ('*'),
				Window.DrawProgressBar(totalActors/objectCount,"Initializing....")
			actorLocation = Actor.getLocation()
			actorRotation = Actor.getEuler()
			actorHeading = actorRotation[2] - (float(int(actorRotation[2]/6.2831853))*6.2831853) # normalize actor rotation
			if actorHeading<0:
				actorHeading+=6.2831853
			actorTurn = random.randrange(-int((resolution-1)/2),int((resolution-1)/2),1)
			#get the stats for this type of actor
			dbCursor.execute('SELECT TypeID,Speed,SpeedV,AttackRadius,AttackRadiusV,ChargeRadius,ChargeRadiusV,CowardRadius,CowardRadiusV,BuddyRadius,BuddyRadiusV,Health,HealthV,Attack,AttackV,Defense,DefenseV,Intellect,IntellectV,ActorRadius,FieldofView,FieldofViewV,MaxTurn,MaxTurnV FROM tblTypes WHERE (TypeID="' + actorName[3:4] + '")')
			actorType=dbCursor.fetchone()
	
			#use Type stats to generate individual characters
			SQLInsert = 'INSERT INTO tblActors (ObjectName,Team,Type,Speed,AttackRadius,ChargeRadius,CowardRadius,BuddyRadius,Health,Attack,Defense,Intellect,FieldofView,MaxTurn,x,y,ActorRadius,Heading,Turn,Pathmode) SELECT'
			SQLInsert = SQLInsert + '"' + actorName + '", "' + actorName[2:3] + '", ' #Team
			SQLInsert = SQLInsert + '"' + str(actorType[0]) + '", '
			SQLInsert = SQLInsert + str(actorType[1]*(1+random.uniform(actorType[2],-actorType[2]))) + ', ' #Speed
			SQLInsert = SQLInsert + str(actorType[3]*(1+random.uniform(actorType[4],-actorType[4]))) + ', ' #AttackRadius
			SQLInsert = SQLInsert + str(actorType[5]*(1+random.uniform(actorType[6],-actorType[6]))) + ', ' #ChargeRadius
			SQLInsert = SQLInsert + str(actorType[7]*(1+random.uniform(actorType[8],-actorType[8]))) + ', ' #CowardRadius
			SQLInsert = SQLInsert + str(actorType[9]*(1+random.uniform(actorType[10],-actorType[10]))) + ', ' #BuddyRadius
			SQLInsert = SQLInsert + str(actorType[11]*(1+random.uniform(actorType[12],-actorType[12]))) + ', ' #Health
			SQLInsert = SQLInsert + str(actorType[13]*(1+random.uniform(actorType[14],-actorType[14]))) + ', ' #Attack
			SQLInsert = SQLInsert + str(actorType[15]*(1+random.uniform(actorType[16],-actorType[16]))) + ', ' #Defense
			SQLInsert = SQLInsert + str(actorType[17]*(1+random.uniform(actorType[18],-actorType[18]))) + ', ' #Intellect
			SQLInsert = SQLInsert + str((actorType[20]*0.017453)*(1+random.uniform((actorType[21]),-(actorType[21])))) + ', ' #Field of View into Radians
			SQLInsert = SQLInsert + str((actorType[22]*0.017453)*(1+random.uniform((actorType[23]),-(actorType[23])))) + ', ' #Max Turning Radius into Radians
			SQLInsert = SQLInsert + str(actorLocation[0]) + ', ' + str(actorLocation[1]) + ', ' + str(actorType[19]) + ',' + str(actorHeading) + ', '#x,y, Actor's Physical radius, and Heading
			SQLInsert = SQLInsert + str(actorTurn) + ', "terrain"' #Turn - where the actor takes his turn during a round
			dbCursor.execute(SQLInsert)

			Actor.clearIpo() #unlink existing Ipo and create a new one
			actorIpo = Blender.Ipo.New('Object','actorIpo')
			Actor.setIpo(actorIpo)
			actorIpoX=actorIpo.addCurve('LocX')
			actorIpoY=actorIpo.addCurve('LocY')
			actorIpoZ=actorIpo.addCurve('LocZ')
			actorIpoRZ=actorIpo.addCurve('RotZ')
			thisFrame=bpy.context.scene.frame_current
			actorIpoX.addBezier((thisFrame,actorLocation[0]))
			actorIpoY.addBezier((thisFrame,actorLocation[1]))
			actorIpoZ.addBezier((thisFrame,getZFromTree(actorLocation,GB[0],GB[1],GB[2],GB[3])))
			actorIpoRZ.addBezier((thisFrame,actorHeading*5.72957795))
			actorIpoRZ.setInterpolation('Bezier')
			actorIpoZ.setInterpolation('Bezier')
			actorIpoX.setInterpolation('Bezier')
			actorIpoY.setInterpolation('Bezier')
		elif string.find(actorName,'BR')==0: #this is a Barrier Object
			actorLocation=Actor.getLocation()
			actorSize=(Actor.SizeX+Actor.SizeY+Actor.SizeZ)/3
			SQLInsert = 'INSERT INTO tblBarriers (BarrierName,x,y,BarrierSize,BarrierType) SELECT "' + actorName + '", ' + str(actorLocation[0]) + ', ' + str(actorLocation[1]) + ', '
			SQLInsert = SQLInsert + str(actorSize) + ', "Empty"'
			dbCursor.execute(SQLInsert)

	outMessage = str(totalActors) + ' Actors set: ' + str(float(int((time.time()-startTime)*100))/100) + ' secs.'
	Blender.Set('curframe',thisFrame+Blender.resolution)
	print (outMessage)
	Window.DrawProgressBar(1,'Initialized')
	return outMessage

def ResetActors(dbCursor):
	startTime=time.time()
	objectlist=bpy.data.objects[]
	objectCount=len(objectlist)	
	random.seed()
	totalActors=0
	#import psyco
	#psyco.full()
	
	# Initialize objects for dropping to ground
	try:
		Ground = bpy.data.objects["Ground"]
	except:
		return 'PROBLEM: No object named Ground.'
	InvVec = Ground.getLocation()

	#clear the Actions database
	dbCursor.execute('DELETE tblActions.* FROM tblActions')

	#determine min and max bounding values of the ground object	
	#so we can ignore objects not even over the ground
	GroundBounds = Ground.getBoundBox()
	GB = [0.0,0.0,0.0,0.0]
	GB[0] = min(GroundBounds[0][0],GroundBounds[1][0],GroundBounds[2][0],GroundBounds[3][0],GroundBounds[4][0],GroundBounds[5][0],GroundBounds[6][0],GroundBounds[7][0])
	GB[1] = max(GroundBounds[0][0],GroundBounds[1][0],GroundBounds[2][0],GroundBounds[3][0],GroundBounds[4][0],GroundBounds[5][0],GroundBounds[6][0],GroundBounds[7][0])
	GB[2] = min(GroundBounds[0][1],GroundBounds[1][1],GroundBounds[2][1],GroundBounds[3][1],GroundBounds[4][1],GroundBounds[5][1],GroundBounds[6][1],GroundBounds[7][1])
	GB[3] = max(GroundBounds[0][1],GroundBounds[1][1],GroundBounds[2][1],GroundBounds[3][1],GroundBounds[4][1],GroundBounds[5][1],GroundBounds[6][1],GroundBounds[7][1])

	#get the face list of the ground object
	GroundMesh = Blender.NMesh.GetRawFromObject('Ground')

	#Go through list of objects, reseting info
	for Actor in objectlist:
		actorName = Actor.getName()
		if string.find(actorName,'WR')==0: #Update this object
			totalActors = totalActors + 1
			if (totalActors/100)==(totalActors/100.0):
				print ('*'),
			actorLocation = Actor.getLocation()
			actorRotation = Actor.getEuler()
			actorHeading = actorRotation[2] - (float(int(actorRotation[2]/6.2831853))*6.2831853) # normalize actor rotation
			if actorHeading<0:
				actorHeading += 6.2831853

			#get the stats for this type of actor
			dbCursor.execute('SELECT TypeID,Health,HealthV FROM tblTypes WHERE (TypeID="' + actorName[3:4] + '")')
			actorType=dbCursor.fetchone()
	
			#use Type stats to generate individual characters
			SQLUpdate = 'UPDATE tblActors SET Health = ' + str(actorType[1]*(1+random.uniform(actorType[2],-actorType[2]))) + ', '
			SQLUpdate = SQLUpdate + 'x = ' + str(actorLocation[0]) + ', y = ' + str(actorLocation[1]) + ', Heading = ' + str(actorHeading)
			SQLUpdate = SQLUpdate + ' WHERE ObjectName = "' + actorName + '"'
			dbCursor.execute(SQLUpdate)

			Actor.clearIpo() #unlink existing Ipo and create a new one
			actorIpo = Blender.Ipo.New('Object','actorIpo')
			Actor.setIpo(actorIpo)
			actorIpoX=actorIpo.addCurve('LocX')
			actorIpoY=actorIpo.addCurve('LocY')
			actorIpoZ=actorIpo.addCurve('LocZ')
			actorIpoRZ=actorIpo.addCurve('RotZ')
			thisFrame=bpy.context.scene.frame_current
			actorIpoX.addBezier((thisFrame,actorLocation[0]))
			actorIpoY.addBezier((thisFrame,actorLocation[1]))
			ActorZ=getZFromTree(actorLocation,GB[0],GB[1],GB[2],GB[3])
			Actor.setLocation(actorLocation[0],actorLocation[1],ActorZ)
			actorIpoZ.addBezier((thisFrame,ActorZ))
			actorIpoRZ.addBezier((thisFrame,actorHeading*5.72957795))
			actorIpoRZ.setInterpolation('Bezier')
			actorIpoZ.setInterpolation('Bezier')
			actorIpoX.setInterpolation('Bezier')
			actorIpoY.setInterpolation('Bezier')

	outMessage = str(totalActors) + ' Actors reset: ' + str(float(int((time.time()-startTime)*100))/100) + ' secs.'
	Blender.Set('curframe',thisFrame+Blender.resolution)
	print (outMessage)
	return outMessage
