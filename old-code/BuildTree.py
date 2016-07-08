import bpy, math, sqlite3, time
from bpy import NMesh, Window
from array import array

#The script builds a queriable quad tree in a mysql database to speed up droptoGround calculations

def sgn2(value):
	if value>0:
		return 1
	else:
		return -1

def InverseTranslate(InCoords,DeltaVec):
	return [InCoords[0]+DeltaVec[0],InCoords[1]+DeltaVec[1],InCoords[2]+DeltaVec[2]]

def loadTree():
	SQL='Select * from tblGroundTree'
	bpy.dbCursor.execute(SQL)
	fulltree = bpy.dbCursor.fetchall()
	
	if fulltree == None:
		return
	else:
		globalGround = {}
		
		for entry in fulltree:
			entrykey = str(entry[1]) + str(entry[2]) + str(entry[3]) + str(entry[4]) + str(entry[5]) + str(entry[6]) + str(entry[7]) + str(entry[8])
			if bpy.globalGround.has_key(entrykey): #add entry to list of lists associated with this key
				bpy.globalGround[entrykey].append([entry[9],entry[10],entry[11],entry[12],entry[13],entry[14],entry[15],entry[16],entry[17],entry[18],entry[19],entry[20],entry[21],entry[22],entry[23],entry[24],entry[25],entry[26],entry[27]])
			else: #new key
				bpy.globalGround[entrykey]=[[entry[9],entry[10],entry[11],entry[12],entry[13],entry[14],entry[15],entry[16],entry[17],entry[18],entry[19],entry[20],entry[21],entry[22],entry[23],entry[24],entry[25],entry[26],entry[27]]]
	return globalGround
	
def searchTreeBuild(location,gf,gb0,gb1,gb2,gb3,InvVec):
	[x,y,z]=location
	qx=array('f')
	qy=array('f')
	for counter in [0,1,2,3]:
		centerpointx=(gb0+gb1)/2
		centerpointy=(gb2+gb3)/2
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
	gv=gf.v
	gc=gf.col
	if len(gc) > 0:
		return {(qx[0],qy[0],qx[1],qy[1],qx[2],qy[2],qx[3],qy[3]):[InverseTranslate(gv[0].co,InvVec),InverseTranslate(gv[1].co,InvVec),InverseTranslate(gv[2].co,InvVec),InverseTranslate(gv[3].co,InvVec),[gc[0].r,gc[1].r,gc[2].r,gc[3].r],gf.no]}
	else:
		return {(qx[0],qy[0],qx[1],qy[1],qx[2],qy[2],qx[3],qy[3]):[InverseTranslate(gv[0].co,InvVec),InverseTranslate(gv[1].co,InvVec),InverseTranslate(gv[2].co,InvVec),InverseTranslate(gv[3].co,InvVec),[255,255,255,255],gf.no]}

def BuildTree():
	startTime=time.time()
	Window.DrawProgressBar(0,'Building...')
	try:
		Ground=bpy.data.objects["Ground"]
	except:
		return 'PROBLEM: No object named Ground.'
	bpy.dbCursor.execute('DELETE tblGroundTree.* FROM tblGroundTree')

	
	InvVec = Ground.location

	GroundBounds = Ground.dimensions
	GB = [0.0,0.0,0.0,0.0]
	GB[0] = min(GroundBounds[0][0],GroundBounds[1][0],GroundBounds[2][0],GroundBounds[3][0],GroundBounds[4][0],GroundBounds[5][0],GroundBounds[6][0],GroundBounds[7][0])
	GB[1] = max(GroundBounds[0][0],GroundBounds[1][0],GroundBounds[2][0],GroundBounds[3][0],GroundBounds[4][0],GroundBounds[5][0],GroundBounds[6][0],GroundBounds[7][0])
	GB[2] = min(GroundBounds[0][1],GroundBounds[1][1],GroundBounds[2][1],GroundBounds[3][1],GroundBounds[4][1],GroundBounds[5][1],GroundBounds[6][1],GroundBounds[7][1])
        GB[3] = max(GroundBounds[0][1],GroundBounds[1][1],GroundBounds[2][1],GroundBounds[3][1],GroundBounds[4][1],GroundBounds[5][1],GroundBounds[6][1],GroundBounds[7][1])
	#get the face list of the ground object
        ob = bpy.data.objects['Ground']
        GroundMesh =  ob.to_mesh(scene, True, 'PREVIEW')

	GroundFaces = GroundMesh.faces
	faceCount = len(GroundFaces)
	faceNo = 0

	# for each face, add an SQL entry for each unique tree node a vertex resides in
	for GroundFace in GroundFaces:
		GroundVerts = GroundFace.v
		faceNo += 1
		if ((faceNo/100.0)==(faceNo/100)):
			Window.DrawProgressBar(float(faceNo)/faceCount,'Building...')
		treeCoordsDist={}
		for GroundVert in GroundVerts:
			treeCoordsDistTemp = searchTreeBuild(InverseTranslate(GroundVert,InvVec),GroundFace,GB[0],GB[1],GB[2],GB[3],InvVec)
			tempKey = treeCoordsDistTemp.keys()
			tempValue = treeCoordsDistTemp.values()
			treeCoordsDist[tempKey[0]] = tempValue[0]
		for GroundCoords,GroundVals in treeCoordsDist.items():
			SQLInsert = 'INSERT INTO tblGroundTree (x1,y1,x2,y2,x3,y3,x4,y4,fx1,fy1,fz1,fx2,fy2,fz2,fx3,fy3,fz3,fx4,fy4,fz4,r1,r2,r3,r4,fnx,fny,fnz) SELECT '
			SQLInsert = SQLInsert + str(GroundCoords[0]) + ',' + str(GroundCoords[1]) + ',' #x1, y1
			SQLInsert = SQLInsert + str(GroundCoords[2]) + ',' + str(GroundCoords[3]) + ',' #x2, y2
			SQLInsert = SQLInsert + str(GroundCoords[4]) + ',' + str(GroundCoords[5]) + ',' #x3, y3
			SQLInsert = SQLInsert + str(GroundCoords[6]) + ',' + str(GroundCoords[7]) + ',' #x4, y4
			SQLInsert = SQLInsert + str(GroundVals[0][0]) + ',' + str(GroundVals[0][1]) + ',' + str(GroundVals[0][2]) + ',' #fx1,fy1,fz1
			SQLInsert = SQLInsert + str(GroundVals[1][0]) + ',' + str(GroundVals[1][1]) + ',' + str(GroundVals[1][2]) + ',' #fx2,fy2,fz2
			SQLInsert = SQLInsert + str(GroundVals[2][0]) + ',' + str(GroundVals[2][1]) + ',' + str(GroundVals[2][2]) + ',' #fx3,fy3,fz3
			SQLInsert = SQLInsert + str(GroundVals[3][0]) + ',' + str(GroundVals[3][1]) + ',' + str(GroundVals[3][2]) + ',' #fx4,fy4,fz4
			SQLInsert = SQLInsert + str(GroundVals[4][0]) + ',' + str(GroundVals[4][1]) + ',' + str(GroundVals[4][2]) + ',' + str(GroundVals[4][3]) + ','#vertex colors for red
			SQLInsert = SQLInsert + str(GroundVals[5][0]) + ',' + str(GroundVals[5][1]) + ',' + str(GroundVals[5][2]) #fnx,fny,fnz
			bpy.dbCursor.execute(SQLInsert)

	outMessage = 'Ground search tree built: ' + str(float(int((time.time()-startTime)*100))/100) + ' secs.'
	print (outMessage)
	Window.DrawProgressBar(1,'Built.')
	return outMessage
