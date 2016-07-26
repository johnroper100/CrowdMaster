import bpy, string, random, time
from math import *
from array import array
random.seed()

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

def FindZCoords(A,B,C,tx,ty,tz,px,py):
	D=-((A*tx)+(B*ty)+(C*tz))
	return -((A*px)+(B*py)+D)/C

def InverseTranslate(InCoords,DeltaVec):
	return [InCoords[0]+DeltaVec[0],InCoords[1]+DeltaVec[1],InCoords[2]+DeltaVec[2]]

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

def EulerHeading(startloc,targetloc): #Given two points, find the Euler heading to those points.
	return (atan2(targetloc[1]-startloc[1],targetloc[0]-startloc[0]))

def getColFaceList(facelist,x,y):
	averageColor = 0
	for GroundVerts in facelist:
		#check for quad faces
		#print 'quad face'
		[x1,y1,z1] = [GroundVerts[0],GroundVerts[1],GroundVerts[2]]
		[x2,y2,z2] = [GroundVerts[3],GroundVerts[4],GroundVerts[5]]
		[x3,y3,z3] = [GroundVerts[6],GroundVerts[7],GroundVerts[8]]
		[x4,y4,z4] = [GroundVerts[9],GroundVerts[10],GroundVerts[11]]
		p0=[x,y,0]
		p1=[x1,y1,0]
		p2=[x2,y2,0]
		p3=[x3,y3,0]
		p4=[x4,y4,0]
		if InsideQuad(p0,p1,p2,p3,p4):		
			dist1 = sqrt(((x-x1)**2) + ((y-y1)**2))
			dist2 = sqrt(((x-x2)**2) + ((y-y2)**2))
			dist3 = sqrt(((x-x3)**2) + ((y-y3)**2))
			dist4 = sqrt(((x-x4)**2) + ((y-y4)**2))
			totaldist = dist1 + dist2 + dist3 + dist4
			averageColor = (GroundVerts[15] * (dist1/totaldist)) + (GroundVerts[16] * (dist2/totaldist)) + (GroundVerts[17] * (dist3/totaldist)) + (GroundVerts[18] * (dist4/totaldist))
			return averageColor
	return averageColor

def getColfromTree(x,y): #obtain the weighted vertex color of the coordinates from the Ground tree
	global globalGround
	qx=array('i')
	qy=array('i')
	#firstsubdiv
	gb0=Blender.GB0
	gb1=Blender.GB1
	gb2=Blender.GB2
	gb3=Blender.GB3
	for counter in [0,1,2,3]:
		centerpointx=(gb0+gb1)/2
		centerpointy=(gb2+gb3)/2
		#print centerpointx,centerpointy
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
	colorlist=Blender.globalGround[str(qx[0])+str(qy[0])+str(qx[1])+str(qy[1])+str(qx[2])+str(qy[2])+str(qx[3])+str(qy[3])]
	averageColor = getColFaceList(colorlist,x,y)
	return averageColor


def moveTowardLocation(startloc,targetloc,localspeed,pathmode): # Given start and end coords and max distance to travel, gives new coords
	#startTime=time.time()
	totaldist = sqrt(((targetloc[0]-startloc[0])**2) + ((targetloc[1]-startloc[1])**2))
	if (pathmode=='none'):
		movedistx = ((localspeed*targetloc[0])-(localspeed*startloc[0]))/totaldist
		movedisty = ((localspeed*targetloc[1])-(localspeed*startloc[1]))/totaldist
	elif (pathmode=='terrain') or (totaldist<(localspeed*3)): #use short distance terrain based look-ahead for fake pathfinding
		#determine normalized vector
		lowdist = totaldist * totaldist
		startvec = atan2((targetloc[1]-startloc[1]),(targetloc[0]-startloc[0]))
		lowvec = startvec
		currentcol = getColfromTree(startloc[0],startloc[1])
		for testval in [4,3,5,2,6,1,7,0,8,-1,9,-2,10,-3,11,-4,12]: #test in 9 steps within 180 degrees of optimum vector
			testvec = startvec+((testval-4)*.35)
			#test each vector end for ground color, balanced against distance from target
			pointcol = getColfromTree(startloc[0]+(localspeed*cos(testvec)),startloc[1]+(localspeed*sin(testvec)))
			if (currentcol < (pointcol * 1.03)) and (pointcol > 20):
				#ground color is close enough to current value - break and move out
				lowvec = testvec
				#print 'Early breakout: heading ', (lowvec*57.29), '; color ', currentcol, 'to ',pointcol
				break
			actualdist = sqrt(((targetloc[0]-(localspeed*cos(testvec)))**2) + ((targetloc[1]-(localspeed*sin(testvec)))**2))
			if pointcol <= 20:
				testdist = actualdist * 2
			else:
				testdist = actualdist * (((255 - pointcol) / 255) / (1 - ((abs(1 - (testval/4))**2) / 100)))
			if testdist < lowdist:
				lowvec = testvec
				lowdist = testdist
			if (testval == 8) and (lowdist<(actualdist * 1.5)):
				#we've found an acceptable path forward - stop the loop.
				break
		movedistx = localspeed*cos(lowvec)
		movedisty = localspeed*sin(lowvec)
	else: #pathmode is full A Star pathfinding - should only be used for commanders and solitary actors
		cx=0 #initialize search variables - 'c' is current, 't' is target
		cy=0
		tx=int((targetloc[0]-startloc[0])/localspeed) #create local integer coord system for searches - find target in new coords
		ty=int((targetloc[1]-startloc[1])/localspeed)
		ch=abs(tx-cx)+abs(ty-cy)
		cg=0
		cf=cg+ch
		target=0
		astaropen = {'0,0':[0,0,cf,0,ch,0,0,250]}
		astarf = [[cf,"0,0"]]
		astarclosed = {'null':[0,0,0,0,0,0,0,250]}
						
		while (target==0): #run this loop until the target block is accquired
			# find best square for this iteration of search loop
			astarf.sort
			currentkey=astarf.pop(0)
			keyresult=astaropen[currentkey[1]]
			cx=keyresult[0]
			cy=keyresult[1]
			cf=keyresult[2]
			cg=keyresult[3]
			ch=keyresult[4]	
			for lx in [-1,0,1]:
				for ly in [-1,0,1]:
					if ((cx+lx)==tx) and ((cy+ly)==ty): #have we accquired the target?
						target=1
					elif (target==0): #not the target - keep looking
						if (lx<>0) or (ly<>0): #skip testing of the current block
							testkey=str(cx+lx) + ',' + str(cy+ly)
							testresult=(astaropen.has_key(testkey) or astarclosed.has_key(testkey))
							if not testresult: #This is a new block to our search - add it to the list as open
								pointcol = int(getColfromTree(startloc[0]+((cx+lx)*localspeed),startloc[1]+((cy+ly)*localspeed))) #get terrain color from center of block, mapped back to main coords
								if pointcol>20: #terrain is passable - continue; otherwise, ditch on this block
									h_diagonal = min(abs(tx-(cx+lx)), abs(ty-(cy+ly)))
									h_straight = abs(tx-(cx+lx)) + abs(ty-(cy+ly))
									sh = (14 * h_diagonal) + 10 * (h_straight - (2 * h_diagonal)) #Manhattan with weighted diagonals
									if (lx==0) or (ly==0): #using simple 10 for vert/horiz, 14 for diagonal
										sg=cg+int(10+((250-pointcol)/8.5))
									else:
										sg=cg+int(14+((250-pointcol)/8.5))
									sf=sg+sh
									astarf.append([sf,testkey])
									astaropen[testkey]=[(cx+lx),(cy+ly),sf,sg,sh,cx,cy,pointcol]#adds new listing to db for this block
							else: #This block is already in the db - check for open/closed and stats
								if (astaropen.has_key(testkey)):
									already=astaropen[testkey]
									pickupcolor=already[7]
									if (lx==0) or (ly==0): #using simple 10 for vert/horiz, 14 for diagonal
										sg=cg+int(10+((250-pickupcolor)/8.5))
									/indices.htmlelse:
										sg=cg+int(14+((250-pickupcolor)/8.5))
									if (sg<already[3]): #new path is better than stored path - change the listing
										astaropen[testkey]=[already[0],already[1],already[2],sg,already[4],cx,cy,pickupcolor]
						else: #section to work on the current block
							testkey=str(cx)+','+str(cy)
							astarclosed[testkey]=astaropen[testkey]
							del astaropen[testkey]
					
		# found the target square - now backtrack the path and take the one that points to the origin				
		ox=tx
		oy=ty
		done=0

		while (done==0): #until we hit the origin...
			testkey=str(cx)+','+str(cy)
			if (astarclosed.has_key(testkey)):
				astar=astarclosed[testkey]
			else:
				astar=astaropen[testkey]

			ox=astar[5]
			oy=astar[6]
			if ((ox==0) and (oy==0)): #origin, baby!
				done=1
			else:
				cx=ox
				cy=oy
		
		targetloc[0]=startloc[0]+(cx*localspeed)
		targetloc[1]=startloc[1]+(cy*localspeed)
		[movedistx, movedisty] = moveTowardLocation(startloc,targetloc,localspeed,"none")			
						
	#print 'Move Time: ' + str(Blender.Get('curframe')) + ' in ' + str(time.time()-startTime) + ' seconds'
	return [movedistx, movedisty]

def findDistance(startloc,endloc): # Find distance between two points in 2d space
	return sqrt(((startloc[0]-endloc[0])*(startloc[0]-endloc[0]))+((startloc[1]-endloc[1])*(startloc[1]-endloc[1])))

def findOpponent(actorloc,team,heading,fov): # Find nearest actor on an opposing team - return x,y of opponent and distance
	heading = - heading #adjust for different rotation directions in Python and mySQL
	if ((heading>pi) or (heading<-pi)):
		heading=fmod(heading,pi)
	if ((heading-fov)<-pi):
		heading+=pi
	if ((heading+fov)>pi):
		heading-=pi
	SQLQuery='SELECT ObjectName, Team, x, y, ((x - ' + str(actorloc[0]) + ') * (x - ' + str(actorloc[0]) + ')) + ((y - ' + str(actorloc[1]) + ') * (y - ' + str(actorloc[1]) + ')) as Distance, Health, Defense, ActorRadius, ID '
	SQLQuery = SQLQuery + 'FROM tblActors WHERE(Team<>"' + team + '" AND Health>0 and (atan2(y-' + str(actorloc[1]) + ',x-' + str(actorloc[0]) + ') BETWEEN ' + str(heading-fov) + ' AND ' + str(heading+fov) + ')) ORDER BY Distance LIMIT 1'
	bpy.dbCursor.execute(SQLQuery)
	sqlResult=bpy.dbCursor.fetchone()
	if sqlResult is None:
		#print "Heading was " + str(heading) + " and FOV " + str(fov)
		#print SQLQuery
		return ["None",0,0,-1,0,0,0,0]
	else:
		return [sqlResult[0],sqlResult[2],sqlResult[3],sqrt(sqlResult[4]),sqlResult[5],sqlResult[6],sqlResult[7],sqlResult[8]]

def findDirectedOp(actorloc,team,targetObject): # Find nearest actor on an opposing team within target area
	[targetLocx,targetLocy,targetLocz] = targetObject.getLocation()
	[targetScalex,targetScaley,targetScalez] = targetObject.getSize()
	targetScale = (targetScalex + targetScaley + targetScalez) / 3
	SQLQuery='SELECT ObjectName, Team, x, y, ((x - ' + str(actorloc[0]) + ') * (x - ' + str(actorloc[0]) + ')) + ((y - ' + str(actorloc[1]) + ') * (y - ' + str(actorloc[1]) + ')) as Distance, Health, Defense, ActorRadius, ID '
	SQLQuery = SQLQuery + 'FROM tblActors WHERE(Team<>"' + team + '" AND Health>0 AND (((x - ' + str(targetLocx) + ') * (x - ' + str(targetLocx) + ')) + ((y - ' + str(targetLocy) + ') * (y - ' + str(targetLocy) + '))) < (' + str(targetScale) + ' * ' + str(targetScale) + ')) ORDER BY Distance LIMIT 1'
	bpy.dbCursor.execute(SQLQuery)
	sqlResult=bpy.dbCursor.fetchone()
	if sqlResult is None:
		return ["None",0,0,-1,0,0,0,0]
	else:
		return [sqlResult[0],sqlResult[2],sqlResult[3],sqrt(sqlResult[4]),sqlResult[5],sqlResult[6],sqlResult[7],sqlResult[8]]

def findOpponentAudial(actorloc,team,hearing): # Find nearest actor on an opposing team - return x,y of opponent and distance
	SQLQuery='SELECT ObjectName, Team, x, y, ((x - ' + str(actorloc[0]) + ') * (x - ' + str(actorloc[0]) + ')) + ((y - ' + str(actorloc[1]) + ') * (y - ' + str(actorloc[1]) + ')) as Distance, Health, Defense, ActorRadius, ID '
	SQLQuery = SQLQuery + 'FROM tblActors WHERE(Team<>"' + team + '" AND Health>0) ORDER BY Distance LIMIT 1'
	bpy.dbCursor.execute(SQLQuery)
	sqlResult=bpy.dbCursor.fetchone()
	if sqlResult is None:
		return ["None",0,0,-1,0,0,0,0]
	elif sqrt(sqlResult[4])<hearing:
		return [sqlResult[0],sqlResult[2],sqlResult[3],sqrt(sqlResult[4]),sqlResult[5],sqlResult[6],sqlResult[7],sqlResult[8]]
	else:
		return ["None",0,0,-1,0,0,0,0]

def findAlly(actorloc,team,actorName): # Find x,y of nearest living ally
	SQLQuery='SELECT ObjectName, Team, x, y, ((x - ' + str(actorloc[0]) + ') * (x - ' + str(actorloc[0]) + ')) + ((y - ' + str(actorloc[1]) + ') * (y - ' + str(actorloc[1]) + ')) as Distance, Health '
	SQLQuery = SQLQuery + 'FROM tblActors WHERE(Team="' + team + '" AND Health>0 AND ObjectName<>"' + actorName + '") ORDER BY Distance LIMIT 1'
	bpy.dbCursor.execute(SQLQuery)
	sqlResult=bpy.dbCursor.fetchone()
	if sqlResult is None:
		return [0,0,-1]
	else:
		return [sqlResult[2],sqlResult[3],sqrt(abs(sqlResult[4]))]
	
def ISeeDeadPeople(actorloc,actorName): # Find x,y of nearest living ally
	SQLQuery='SELECT ObjectName, x, y, ((x - ' + str(actorloc[0]) + ') * (x - ' + str(actorloc[0]) + ')) + ((y - ' + str(actorloc[1]) + ') * (y - ' + str(actorloc[1]) + ')) as Distance, Health, ActorRadius '
	SQLQuery = SQLQuery + 'FROM tblActors WHERE(Health<=0 AND ObjectName<>"' + actorName + '") ORDER BY Distance LIMIT 1'
	bpy.dbCursor.execute(SQLQuery)
	sqlResult=bpy.dbCursor.fetchone()
	if sqlResult is None:
		return [0,0,0,-1]
	else:
		return [sqlResult[1],sqlResult[2],sqlResult[5],sqrt(abs(sqlResult[3]))]

def findOpCenter(team): # Find x,y center of forces opposing the passed team
	#startTime=time.time()
	AVGQuery='SELECT AVG(x), AVG(y) FROM tblActors WHERE (Team<>"' + team + '" and Health > 0)'
	bpy.dbCursor.execute(AVGQuery)
	avgResult=bpy.dbCursor.fetchone()
	#print 'Opponent Center Find: ' + str(Blender.Get('curframe')) + ' in ' + str(time.time()-startTime) + ' seconds'
	if avgResult is None: # There are no opponents
		return [0,0]
	else:
		return [avgResult[0],avgResult[1]]

def findAlCenter(team): # Find x,y center of allied forces
	AVGQuery='SELECT AVG(x), AVG(y) FROM tblActors WHERE (Team="' + team + '" and Health > 0)'
	bpy.dbCursor.execute(AVGQuery)
	avgResult=bpy.dbCursor.fetchone()
	if avgResult is None: # There are no opponents
		return [0,0]
	else:
		return [avgResult[0],avgResult[1]]

def dPointLine(actorx,actory,dlx1,dly1,dlx2,dly2): #find distance between a point and a line, given three coords
	try:
		A = -((dly2-dly1)/(dlx2-dlx1))
	except:
		A = 0
	B = 1
	C = -(dly1+ (A * dlx1))
	return abs(((A*B)+(actorx*actory)+C)/sqrt((A**2)+(B**2)))

def zOnLine(actorx,actory,flx1,fly1,flz1,flx2,fly2,flz2): #find nearest point on a line
	#print actorx,actory,flx1,fly1,flz1,flx2,fly2,flz2
	intx1=((((flx2-flx1)/(fly2-fly1))*actorx)+(((fly2-fly1)/(flx2-flx1))*flx1)+actory-fly1)
	intx2=(((fly2-fly1)/(flx2-flx1)) + ((flx2-flx1)/(fly2-fly1)))
	intx=intx1/intx2
	inty=(((fly2-fly1)/(flx2-flx1))*intx)+fly1-(((fly2-fly1)/(flx2-flx1))*flx1)
	return (sqrt((intx-flx1)**2+(inty-fly1)**2)*(flz2-flz1))/sqrt((flx2-flx1)**2+(fly2-fly1)**2)

def getZFaceList(facelist,actorx,actory):
	MeshZ = -200.0
	#find which face the object is over - if the
	#object isn't over a ground face, do nothing
	#print 'Faces:',len(facelist)
	for GroundVerts in facelist:
		#check for quad faces
		#print 'quad face'
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
		#print 'no face found'
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
		#print centerpointx,centerpointy
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
	facelist=Blender.globalGround[str(qx[0])+str(qy[0])+str(qx[1])+str(qy[1])+str(qx[2])+str(qy[2])+str(qx[3])+str(qy[3])]
	#print 'ZLookup: ' + str(Blender.Get('curframe')) + ' in ' + str(time.time()-startTime) + ' seconds'
	return getZFaceList(facelist,x,y)

#############################
### MAIN BLENDERPEOPLE ROUTINE - THIS IS WHERE MOTION IS GENERATED
#############################
			
def Main():
	startTime=time.time()
	thisFrame=bpy.context.scene.frame_current
	#import psyco
	#psyco.full()

	# Get list of all living Actors
	SQLQuery = 'SELECT ObjectName, Team, Speed, AttackRadius, ChargeRadius, BuddyRadius, CowardRadius, ID, Attack, Health, CommanderID, Intellect, ActorRadius, Orders, Heading, Turn, MaxTurn, FieldofView, Pathmode, Type, OrderSpeed FROM tblActors WHERE Health>0 ORDER BY Turn, Speed'
	bpy.dbCursor.execute(SQLQuery)
	actorList = bpy.dbCursor.fetchall()
	totalActors = len(actorList)

	# Initialize objects for dropping to ground
	Ground = Blender.Object.Get ('Ground')
	InvVec = Ground.getLocation ()

	#determine min and max bounding values of the ground object	
	#so we can ignore objects not even over the ground
	GroundBounds = Ground.getBoundBox ()
	GB = [0.0,0.0,0.0,0.0]
	GB[0] = min(GroundBounds[0][0],GroundBounds[1][0],GroundBounds[2][0],GroundBounds[3][0],GroundBounds[4][0],GroundBounds[5][0],GroundBounds[6][0],GroundBounds[7][0])
	GB[1] = max(GroundBounds[0][0],GroundBounds[1][0],GroundBounds[2][0],GroundBounds[3][0],GroundBounds[4][0],GroundBounds[5][0],GroundBounds[6][0],GroundBounds[7][0])
	GB[2] = min(GroundBounds[0][1],GroundBounds[1][1],GroundBounds[2][1],GroundBounds[3][1],GroundBounds[4][1],GroundBounds[5][1],GroundBounds[6][1],GroundBounds[7][1])
	GB[3] = max(GroundBounds[0][1],GroundBounds[1][1],GroundBounds[2][1],GroundBounds[3][1],GroundBounds[4][1],GroundBounds[5][1],GroundBounds[6][1],GroundBounds[7][1])
	Blender.GB0 = GB[0]
	Blender.GB1 = GB[1]
	Blender.GB2 = GB[2]
	Blender.GB3 = GB[3]
	
	#create dictionary for Effector<->variable translations
	EffectorStats = {'Health':'actorHealth','Speed':'speed','Attack':'attackStrength','Defense':'defense','Intellect':'intellect','CommanderID':'commander','FieldofView':'FieldofView','MaxTurn':'maxTurn','AttackRadius':'attackRadius','ChargeRadius':'chargeRadius','CowardRadius':'cowardRadius','BuddyRadius':'buddyRadius'}

	actorCount=0.0
	Blender.Window.DrawProgressBar(0,"Working")
	for actorLink in actorList: # main loop - page through all actors, generating behaviors
		#actorTime=time.time()
		actorCount = actorCount + 1
		# Assign information about the current Actor to named variables for clarity
		actorName = actorLink[0]
		try:
			actorObject = bpy.data.objects[actorName]
		except:
			print "No long a Blender object named "+ actorName
			continue
		actorLoc = actorObject.getLocation()
		actorRot = actorObject.getEuler()
		team = actorLink[1]
		speed = actorLink[2]
		attackRadius = actorLink[3]
		chargeRadius = actorLink[4]
		buddyRadius = actorLink[5]
		cowardRadius = actorLink[6]
		dbID = actorLink[7]
		attackStrength = actorLink[8]
		actorHealth = actorLink[9]
		commander = actorLink[10]
		intellect = actorLink[11]
		actorRadius = actorLink[12]
		oldOrders = actorLink[13]
		actorHeading = actorLink[14]
		newHeading = actorHeading
		headingAdjustor = (float(int(actorHeading/6.2831853))*6.2831853) # create a "normalized" heading for use in tests	
		testHeading = actorHeading - headingAdjustor
		sqlHeading = testHeading
		if sqlHeading>3.1415928:
			sqlHeading-=6.2831853
		if testHeading<0:
			testHeading+=6.2831853
			headingAdjustor-=6.2831853
		actorTurn = actorLink[15]
		maxTurn = actorLink[16]
		FieldofView = actorLink[17]
		Pathmode = actorLink[18]
		defense = 0
		actorType = actorLink[19]
		oldOrderSpeed = actorLink[20]

		# Set initial values on some variables
		attack,movex,movey = 0,0,0
		marchDirection = -1
		currentAction=''

		# Check orders, perform initial evaluation
		# heirarchy of orders is: commander's published orders->your own old orders->master orders from orders table->Defend
		orders=None
		if commander<>0: # If the Actor has no assigned commander, get orders directly from tblOrders
			SQLQuery = 'SELECT ID, Orders, OrderSpeed, PassOrder FROM tblActors WHERE (ID=' + str(commander) + ')'
			bpy.dbCursor.execute(SQLQuery)
			incomingOrders = bpy.dbCursor.fetchone()
			if (incomingOrders is not None) and (incomingOrders[3] is None):
				orders = oldOrders
				speedMultiplier = oldOrderSpeed
			elif (incomingOrders is not None):
				orders = incomingOrders[3]
				speedMultiplier = incomingOrders[2]	
		if orders is None:
			SQLQuery = 'SELECT Team, Orders, SpeedMultilpier FROM tblOrders WHERE (Team="' + team + '")'
			bpy.dbCursor.execute(SQLQuery)
			incomingOrders = bpy.dbCursor.fetchone()
			if incomingOrders is None:
				orders='Defend'
				speedMultiplier=0.5
			else:
				orders = incomingOrders[1]
				speedMultiplier = incomingOrders[2]

		originalOrders = orders
		
		#Check for any active temporary Effectors and apply them to Actor stats
		EffSQL='SELECT Attribute,Operator,Value,x,y,Size FROM tblEffectors WHERE Active=1 AND Duration="Temporary" AND '
		EffSQL+=' sqrt(((x-' + str(actorLoc[0]) + ')*(x-' + str(actorLoc[0]) + '))+((y-' + str(actorLoc[1]) + ')*(y-' + str(actorLoc[1]) + '))) <= Size AND ((Affects="All") OR (Affects="Team" AND AffectsValue="'
		EffSQL+=team + '") OR (Affects="Type" AND AffectsValue="' + actorType + '"))'
		bpy.dbCursor.execute(EffSQL)
		Effectors = bpy.dbCursor.fetchall()
		if (Effectors):
			for Effector in Effectors:
				execString=EffectorStats[Effector[0]] + '=' + EffectorStats[Effector[0]] + Effector[1] + str(Effector[2])
				exec(execString)

		# If this is a marching order, strip out the marching direction
		if string.find(orders,'March') == 0: 
			marchDirection = float(orders[5:])*.01745327
			orders = 'March'

		if string.find(orders,'StrictMarch') == 0:
			marchDirection = float(string.lstrip(orders,'StrictMarch'))*.01745327
			orders = 'StrictMarch'

		# If the order is target, accquire the object. If this fails, default to Defend
		if string.find(orders,'Target') == 0:
			targetName = orders[6:]
			try:
				targetObject = bpy.data.objects[targetName]
			except:
				orders = 'Defend'
			else:
				orders = 'Target'

		# If the order is for a Directed attack, strip out the name of the target empty
		if string.find(orders,'Directed') == 0:
			targetName = orders[8:]
			#print orders, targetName
			try:
				targetObject = bpy.data.objects[targetName]
			except:
				orders = 'Defend'
			else:
				orders = 'Directed'


		# If the order is for Milling, strip out the name of the target object
		if string.find(orders,'Mill') == 0:
			targetName = orders[4:]
			#print orders, targetName
			try:
				targetObject = bpy.data.objects[targetName]
			except:
				orders = 'Defend'
			else:
				orders = 'Mill'

		# If the order is for Strict Milling, strip out the name of the target object
		if string.find(orders,'StrictMill') == 0:
			targetName = orders[10:]
			try:
				targetObject = bpy.data.objects[targetName]
			except:
				orders = 'StrictDefend'
			else:
				orders = 'StrictMill'

		# If order is Rank, parse out heading and separation distance
		if string.find(orders,'Rank') == 0:
			rankNumbers = orders[4:]
			rankList = string.split(rankNumbers,'d')
			marchDirection = float(rankList[0]) * .01745327
			rankDist = float(rankList[1])
			#print marchDirection, rankDist
			orders = 'Rank'		
	
		# Perturb Orders based on Intellect - the dumber you are the less well you will follow your orders
		if sqrt(intellect) < random.random():
			if orders == 'RegroupMain':
				orders = 'Retreat'
			elif orders =='Retreat':
				orders = 'Regroup'
			elif orders =='March':
				marchError = random.uniform((2*intellect)+1,1)
				marchDirection = marchDirection*(1+marchError)
			elif orders == 'Attack':
				orders = 'Defend'
			elif orders == 'Defend':
				orders = 'RegroupMain'
			elif orders == 'Target':
				orders = 'RegroupMain'
			elif orders == 'StrictMarch':
				orders = 'March'
				marchError = random.uniform((2*intellect)+1,1)
				marchDirection = marchDirection*(1+marchError)
			elif orders == 'StrictDefend':
				orders = 'Defend'
			elif orders == 'RegroupCommander':
				orders = 'Retreat'

		# find nearest opponent - if you cannot see one, listen for one.
		if orders<>'Directed':
			[opName,opX,opY,opDist,opHealth,opDefense,opRadius,opID] = findOpponent(actorLoc,team,sqlHeading,FieldofView) 	
			#print actorName + "opDist: " + str(opDist) + " opX: " + str(opX) + " opY: " + str(opY)
			if opDist == -1: #no opponent in view, check within the sound radius
				[opName,opX,opY,opDist,opHealth,opDefense,opRadius,opID] = findOpponentAudial(actorLoc,team,chargeRadius*3)
		else:
			[opName,opX,opY,opDist,opHealth,opDefense,opRadius,opID] = findDirectedOp(actorLoc,team,targetObject)

		#print orders

		# Evaluate situation, determine base action, respecting orders
		if orders == 'Retreat': # Move at ordered speed away from both nearest opponent and center of enemy force, do not engage opponents
			currentAction = 'Retreat'
			[opCX,opCY] = findOpCenter(team)
			if opDist == -1:
				if opCX == 0 and opCY == 0:
					#all enemies are dead.
					orders = 'Defend'
				else:
					[movex,movey] = moveTowardLocation(actorLoc,[opCX,opCY],(-speed)*speedMultiplier,Pathmode)
			else:
				[movex,movey] = moveTowardLocation(actorLoc,[(opCX+opX)/2,(opCY+opY)/2],(-speed)*speedMultiplier,Pathmode)
			newHeading = EulerHeading(actorLoc,[actorLoc[0]+movex,actorLoc[1]+movey])

		if orders == 'StrictMill' or orders == 'Mill':
			if opDist <= chargeRadius and opDist > -1 and orders == 'Mill':
				orders = 'Attack'
			elif opDist <= attackRadius and opDist > -1 and orders == 'StrictMill':
				orders = 'Attack'
			else:
				currentAction = 'Mill'
				targetLoc = targetObject.getLocation()
				targetScale = targetObject.getSize()
				avgSize = (targetScale[0] + targetScale[1] + targetScale[2]) / 3
				if findDistance(actorLoc,targetLoc) > avgSize: # outside the mill area? get inside
					#print 'Outside area'
					orders = 'Target'
				else: # mill around
					pickNew = random.random()
					if pickNew >= 0.05: #pick an angle to offset the current heading, then test it for boundries
						#print 'Pick Angle'
						testAngle = random.gauss(0,0.7)
						[movex,movey]=moveTowardLocation(actorLoc,[actorLoc[0]+(speed*10*cos(testHeading + testAngle)),actorLoc[1]+(speed*10*sin(testHeading + testAngle))],speed/2,Pathmode)
						if (actorLoc[0]+movex)>(targetLoc[0]+avgSize) or (actorLoc[0]+movex)<(targetLoc[0]-avgSize) or (actorLoc[1]+movey)>(targetLoc[1]+avgSize) or (actorLoc[1]+movey)<(targetLoc[1]-avgSize):
							pickNew = 0.01
					if pickNew < 0.05: #pick a new target location to mill to
						#print 'Pick New'
						targetx = random.uniform(avgSize,-avgSize) + targetLoc[0]
						targety = random.uniform(avgSize,-avgSize) + targetLoc[1]
						[movex,movey] = moveTowardLocation(actorLoc,[targetx,targety],speed/2,Pathmode)
					newHeading = EulerHeading(actorLoc,[actorLoc[0]+movex,actorLoc[1]+movey])
					
		if orders == 'Target': # Advance toward the specified Blender object, charging and attacking as needed
			if opDist <= chargeRadius and opDist > -1:
				orders = 'Attack'
			else:
				currentAction = 'March'
				targetLoc = targetObject.getLocation()
				if findDistance(actorLoc,targetLoc) > (chargeRadius + attackRadius)/2:
					[movex,movey] = moveTowardLocation(actorLoc,[targetLoc[0],targetLoc[1]],speed*speedMultiplier,Pathmode)
					newHeading = EulerHeading(actorLoc,[actorLoc[0]+movex,actorLoc[1]+movey])
				else:
					orders = 'Defend'

		if orders == 'March' or orders == 'Rank': # March along the given heading at the ordered speed, attack anything within charging distance
			currentAction = 'March'
			if opDist <= chargeRadius and opDist > -1:
				orders = 'Attack'
			else:
				[movex,movey] = moveTowardLocation(actorLoc,[actorLoc[0]+(speed*10*cos(marchDirection)),actorLoc[1]+(speed*10*sin(marchDirection))],speed*speedMultiplier,Pathmode)
				newHeading = EulerHeading(actorLoc,[actorLoc[0]+movex,actorLoc[1]+movey])

		elif orders == 'Defend': # Maintain formation, attack anything within charging distance
			currentAction = 'Defend'
			if opDist > -1:
				newHeading = EulerHeading(actorLoc,[opX,opY])
				if opDist <= chargeRadius:
					orders = 'Attack'
			else:
				newHeading = testHeading

		elif orders == 'StrictMarch': # March along the given heading at the ordered speed, do not charge, but attack anything within attack range
			currentAction = 'March'
			if opDist <= attackRadius and opDist > -1:
				orders = 'Attack'
			else:
				[movex,movey] = moveTowardLocation(actorLoc,[actorLoc[0]+(speed*cos(marchDirection)),actorLoc[1]+(speed*sin(marchDirection))],speed*speedMultiplier,Pathmode)
				newHeading = EulerHeading(actorLoc,[actorLoc[0]+movex,actorLoc[1]+movey])

		elif orders == 'Directed': # Attack nearest opponent within the Target object
			if opDist > -1:
				attack = 1
				newHeading = EulerHeading(actorLoc,[opX,opY])
				currentAction = 'Attack'
				if (opDefense*random.random())<(attackStrength*random.random()): # A Hit!
					currentAction = 'Attack'
					HitInsert = 'UPDATE tblActors SET Health=' + str(opHealth-attackStrength) + ' WHERE ObjectName="' + opName + '"'
					bpy.dbCursor.execute(HitInsert)
					#if (opHealth-attackStrength)<0:
						#deadEnemy=bpy.data.objects[opName]
						#deadEnemy.setEuler(0,3.14159,0)
			else:
				orders = 'StrictDefend'

		elif orders == 'RegroupCommander': # Close into your coward radius around your commander; if no commander is present perform a full Regroup
			if opDist <= attackRadius and opDist > -1:
				orders = 'Attack'
			elif commander == 0: # No Commander
				orders = 'RegroupMain'
			else:
				SQLQuery = 'SELECT x, y, sqrt(((x - ' + str(actorLoc[0]) + ') * (x - ' + str(actorLoc[0]) + ')) + ((y - ' + str(actorLoc[1]) + ') * (y - ' + str(actorLoc[1]) + '))) as Distance FROM tblActors WHERE (ID = ' + str(commander) + ' AND Health > 0)'
				bpy.dbCursor.execute(SQLQuery)
				SQLResult = bpy.dbCursor.fetchone()
				if SQLResult is None: # Commander is nonexistent or dead. Perform full regroup
					orders = 'RegroupMain'
				else: # Move toward Commander, if too far away
					[cmdX,cmdY,cmdDist] = SQLResult
					if cmdDist > cowardRadius:
						currentAction = 'Regroup'
						[movex,movey] = moveTowardLocation(actorLoc,[cmdX,cmdY],speed*speedMultiplier,Pathmode)
						newHeading = EulerHeading(actorLoc,[actorLoc[0]+movex,actorLoc[1]+movey])
					else:
						currentAction = 'Defend'

		if orders == 'StrictDefend': # Maintain formation, do not charge, but attack anything within attack range
			currentAction = 'Defend'
			newHeading = testHeading
			if opDist <= attackRadius and opDist > -1:
				orders = 'Attack'

		if orders == 'RegroupMain': # Regroup to center of allied forces
			if opDist <= attackRadius and opDist > -1:
				orders = 'Attack'
			else:
				[allX,allY]=findAlCenter(team)
				if findDistance(actorLoc,[allX,allY]) > cowardRadius:
					currentAction = 'Regroup'
					[movex,movey] = moveTowardLocation(actorLoc,[allX,allY],speed*speedMultiplier,Pathmode)
					newHeading = EulerHeading(actorLoc,[actorLoc[0]+movex,actorLoc[1]+movey])
				else:
					currentAction = 'Defend'

		if orders == 'Attack': # Find closest Opponent, attack it.
			if opDist > -1: # -1 indicates there are no opponents, look around
				if opDist > (chargeRadius+(actorRadius*2)+opRadius): # Too far to charge, so march toward enemy force, third of way between nearest op and center of enemy force
					[opCX,opCY] = findOpCenter(team)
					currentAction = 'March'
					[movex,movey] = moveTowardLocation(actorLoc,[(opCX+opX+opX)/3,(opCY+opY+opY)/3],(speed/2)*speedMultiplier,Pathmode)
					newHeading = EulerHeading(actorLoc,[actorLoc[0]+movex,actorLoc[1]+movey])
				elif opDist > (attackRadius+(actorRadius*2)+opRadius): # Charge!
					currentAction = 'Charge'
					[movex,movey] = moveTowardLocation(actorLoc,[opX,opY],speed*speedMultiplier,Pathmode)
					distancetospot = sqrt((movex*movex)+(movey*movey)) #adjust charges for offset due to actor radii
					if distancetospot<(actorRadius+opRadius):
						movex=movex-((actorRadius+actorRadius+opRadius)*(movex/distancetospot))
						movey=movey-((actorRadius+actorRadius+opRadius)*(movey/distancetospot))
					newHeading = EulerHeading(actorLoc,[actorLoc[0]+movex,actorLoc[1]+movey])
				else: # Attack!
					attack = 1
					newHeading = EulerHeading(actorLoc,[opX,opY])
					currentAction = 'Attack'
					if (opDefense*random.random())<(attackStrength*random.random()): # A Hit!
						currentAction = 'Attack'
						HitInsert = 'UPDATE tblActors SET Health=' + str(opHealth-attackStrength) + ' WHERE ObjectName="' + opName + '"'
						bpy.dbCursor.execute(HitInsert)
						if (opHealth-attackStrength)>0:
							#logInsert='INSERT INTO tblActions (ActorID,Frame,Orders,Action) SELECT '
							#logInsert+=str(opID) + ', ' + str(thisFrame+actorTurn) + ', "None", "Struck"'
							#bpy.dbCursor.execute(logInsert)
							pass
						else:
							logInsert='INSERT INTO tblActions (ActorID,Frame,Orders,Action) SELECT '
							logInsert+=str(opID) + ', ' + str(thisFrame+actorTurn) + ', "None", "Die"'
							bpy.dbCursor.execute(logInsert)
				#print opDist,chargeRadius,attackRadius,actorRadius,opRadius,currentAction
			else:
				newHeading = testHeading + ((FieldofView * 0.8) * random.choice([-1,1]))
				#print actorName, "cannot see opponents"
				currentAction = 'Search'

		# Orders are evaluated. Make sure that formations and distances are respected
		if (orders=='March' or orders=='StrictMarch' or orders=='Attack' or orders=='Target') and opDist>chargeRadius: #check to see if you're too far from your commander
			if commander <> 0:
				SQLQuery = 'SELECT x, y, sqrt(((x - ' + str(actorLoc[0]+movex) + ') * (x - ' + str(actorLoc[0]+movex) + ')) + ((y - ' + str(actorLoc[1]+movey) + ') * (y - ' + str(actorLoc[1]+movey) + '))) as Distance FROM tblActors WHERE (ID = ' + str(commander) + ' AND Health > 0)'
				bpy.dbCursor.execute(SQLQuery)
				SQLResult = bpy.dbCursor.fetchone()
				if SQLResult is None: # Commander is nonexistent or dead. Ignore this constraint
					pass
				else: # Cheat toward Commander, if too far away
					[cmdX,cmdY,cmdDist] = SQLResult
					if cmdDist > cowardRadius:
						[Dmovex,Dmovey] = moveTowardLocation(actorLoc,[cmdX,cmdY],speed*speedMultiplier,Pathmode)
						movex=(movex+movex+Dmovex)/3
						movey=(movey+movey+Dmovey)/3

		[alX,alY,alDist] = findAlly([actorLoc[0]+movex,actorLoc[1]+movey],team,actorName) # Find nearest Ally

		if orders == 'Rank':
			buddyRadius = rankDist
			actorRadius = rankDist
	
		if alDist > -1:
			if alDist > buddyRadius: # Too far awar from closest ally, cheat towards it.
				[Dmovex,Dmovey] = moveTowardLocation(actorLoc,[alX,alY],(speed/2)*speedMultiplier,Pathmode)
				movex=(movex+movex+Dmovex)/3
				movey=(movey+movey+Dmovey)/3
			if alDist < ((buddyRadius + actorRadius)/2): # Too close to an ally, cheat away.
				[Dmovex,Dmovey] = moveTowardLocation(actorLoc,[alX,alY],-(speed/2)*speedMultiplier,Pathmode)
				movex=(movex+Dmovex)/2
				movey=(movey+Dmovey)/2
		
		[deadX,deadY,deadRadius,deadDist] = ISeeDeadPeople([actorLoc[0]+movex,actorLoc[1]+movey],actorName)
		if deadDist > -1:
			if deadDist < (actorRadius + deadRadius): # Too close to a dead body, cheat away.
				[Dmovex,Dmovey] = moveTowardLocation(actorLoc,[deadX,deadY],-(speed/2)*speedMultiplier,Pathmode)
				movex=(movex+Dmovey)/2 #swapping x and y to generate oblique movement
				movey=(movey+Dmovex)/2

		# make sure new heading is within turning capacity of Actor, if not, reduce the move and turn max distance
		maxHeading = testHeading + maxTurn
		minHeading = testHeading - maxTurn
		# adjust newHeading so you take the shortest way around the circle
		if (newHeading<=0) and (newHeading<(testHeading-3.14159)):
			newHeading+=6.2831853
		elif (newHeading>=0) and (newHeading<(testHeading-3.14159)):
			newHeading+=6.2831853
		if newHeading>maxHeading: # turning too fast, slow down and turn the max amount
			newHeading=maxHeading
			movex=movex/3
			movey=movey/3
		if newHeading<minHeading: # turning too fast, slow down and turn the max amount
			newHeading=minHeading
			movex=movex/3
			movey=movey/3

		#print actorName + ' pre z-check moves: ' + str(movex) + ',' + str(movey)
		xyDistance = findDistance(actorLoc,[actorLoc[0]+movex,actorLoc[1]+movey])
		if xyDistance <> 0:
			#newZ = getZFromMesh(GroundMesh,actorLoc[0]+movex,actorLoc[1]+movey,GB)
			newZ = getZFromTree([actorLoc[0]+movex,actorLoc[1]+movey,0],GB[0],GB[1],GB[2],GB[3])
			#print 'First pass newZ:' + str(newZ)
			if newZ <> -200:
				zSlope = (newZ - actorLoc[2])/xyDistance
				# if slope is < 10 degrees, do nothing; above 60 dg. stop movement; between, adjust movement speed
				zMultiplier = (1-min((abs(zSlope)-.176)/1.556,1)) 
				movex = movex * zMultiplier
				movey = movey * zMultiplier
				#newZ = getZFromMesh(GroundMesh,actorLoc[0]+movex,actorLoc[1]+movey,GB)
				newZ = getZFromTree([actorLoc[0]+movex,actorLoc[1]+movey,0],GB[0],GB[1],GB[2],GB[3])
			if newZ==-200:
				newZ=actorLoc[2]
		else:
			newZ = getZFromTree([actorLoc[0],actorLoc[1],0],GB[0],GB[1],GB[2],GB[3])

		# update object location in Blender and in database
		newX = actorLoc[0]+movex
		newY = actorLoc[1]+movey
		newHeading = newHeading + headingAdjustor #recalc heading for values <> +-360 degrees

		moveQuery='UPDATE tblActors SET x=' + str(newX) + ',y=' + str(newY) + ', Orders="' + originalOrders + '", OrderSpeed=' + str(speedMultiplier) + ', Heading=' + str(newHeading) + ' WHERE ID=' + str(dbID)
		bpy.dbCursor.execute(moveQuery)

		# add this characters action to the log
		logInsert='INSERT INTO tblActions (ActorID,Frame,Orders,Action) SELECT '
		logInsert+=str(dbID) + ', ' + str(thisFrame+actorTurn) + ', "' + orders + '", "' + currentAction + '"'
		bpy.dbCursor.execute(logInsert)

		actorObject.setLocation(newX,newY,newZ)
		actorObject.setEuler([actorRot[0],actorRot[1],newHeading])
	
		#add a point to the IPOs
		actorIpo=actorObject.getIpo()
		actorIpoX=actorIpo.getCurve('LocX')
		actorIpoY=actorIpo.getCurve('LocY')
		actorIpoZ=actorIpo.getCurve('LocZ')
		actorIpoRZ=actorIpo.getCurve('RotZ')
		actorIpoX.addBezier((thisFrame+actorTurn,newX))
		actorIpoY.addBezier((thisFrame+actorTurn,newY))
		actorIpoZ.addBezier((thisFrame+actorTurn,newZ))
		actorIpoRZ.addBezier((thisFrame+actorTurn,(newHeading*5.72957795)))
		actorIpoRZ.Recalc()
		actorIpoX.Recalc()
		actorIpoY.Recalc()
		actorIpoZ.Recalc()
		if (actorCount/100 == int(actorCount/100)):
			print '*',
			Blender.Window.DrawProgressBar(actorCount/totalActors,"Working")

	outMessage = str(Blender.Get('curframe')) + ' in ' + str(time.time()-startTime) + ' seconds'
	Blender.Window.DrawProgressBar(1,"Done")
	print outMessage
	Blender.Set('curframe',thisFrame+Blender.resolution)
	return outMessage
