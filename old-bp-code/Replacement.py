import bpy, sqlite3

def ReplaceSelectedwithArmature():
	selected = Blender.Object.GetSelected()
	for Actor in selected:
		Actor.select(0)
	for Actor in selected:
		SQL = 'SELECT tblTypes.Armature FROM tblTypes,tblActors WHERE tblTypes.TypeID=tblActors.Type AND tblActors.ObjectName = "' + Actor.name + '";'
		bpy.dbCursor.execute(SQL)
		ArmatureName = bpy.dbCursor.fetchall()
		totalresults = len(ArmatureName)
		
		if (totalresults>0):
			#create new armature object, using old Actor proxy's Ipo...
			#arm=Blender.Armature.Get(ArmatureName[0])
			obs=Blender.Object.Get(ArmatureName[0])
			arm=obs[0]
			if (arm):
				arm.select(1)
				ipo = Actor.getIpo()
				scene = Blender.Scene.getCurrent()
				#ob = Blender.Object.New('Armature')
				#ob.link(arm)
				#scene.link(ob)
				Blender.Object.Duplicate(0,0,0,0,0,0,0,0,0,1)
				ob=Blender.Object.GetSelected()
				scene.unlink(Actor)
				newob=ob[0]
				newob.clearIpo()
				newob.setIpo(ipo)
				newob.select(0)
				Actor.clearIpo()
				transname=Actor.name
				Actor.name='proxy'
				newob.name=transname

def LinkSelectedwithMesh():
	selected=Blender.Object.GetSelected()
	for Actor in selected:
		Actor.select(0)
	for Actor in selected:
		baseMesh=bpy.data.objects['body']
		baseMesh.select(1)
		Blender.Object.Duplicate()
		newMesh=Blender.Object.GetSelected()
		for singleMesh in newMesh:
			singleMesh.setMatrix(Actor.getMatrix())
			Actor.makeParentDeform([singleMesh])
		fordeselect=Blender.Object.GetSelected()
		for des in fordeselect:
			des.select(0)
	print 'Meshes placed and linked.'
	return 'Meshes linked.'
			
#LinkSelectedwithMesh()

#ReplaceSelectedwithArmature()

