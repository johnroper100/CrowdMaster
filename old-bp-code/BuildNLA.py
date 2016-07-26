import bpy, sqlite3, random, math

def setNLAforLoD(ob):
	obName=ob.getName()
	if (ob):
		ob.enableNLAOverride=1
		obGroup=ob.DupGroup
		if (obGroup):
			obGroupName=obGroup.name
			SQL='SELECT ArmatureObject FROM tblCharacters WHERE GroupName="' + obGroupName + '" AND TypeID="'+obName[3]+'";'
			bpy.dbCursor.execute(SQL)
			result=bpy.dbCursor.fetchone()
			if result:
				nlastrips=ob.actionStrips
				if nlastrips:
					for nlastrip in nlastrips:
						nlastrip.groupTarget=result[0]

def refreshMatchBone(ob):
	if (ob):
		nlastrips=ob.actionStrips
		if (nlastrips):
			nlastrips.refreshMatch()
			
def sortonColumn(column,list):
	try:
		decorated = [(listitem[column], listitem) for listitem in list]
		decorated.sort()
		result = [listitem for (key, listitem) in decorated]
		result.reverse()
		return result
	except:
		return None

def filterbyRange(target, list):
	resultlist = []
	for listitem in list:
		if target>=listitem[3]:
			resultlist.append(listitem)
	if resultlist==[]:
		return None
	else:
		return resultlist
	
def fitActionsToFrames(actionlinkstuple,startframe,endframe):
	actionlinks=[]
	for actions in actionlinkstuple:
		actionlinks.append(list(actions))
	finalActionList=[]
	resultActionList=[]
	tofill=endframe-startframe
	expand=0
	while expand==0:
		workinglist=filterbyRange(tofill,actionlinks)
		if workinglist is None:
			#no actions will fit in remaining space. dump out of loop
			expand=1
		else:
			if len(workinglist)>1:
				for item in workinglist:
					item[1]*=random.random()
				workinglist=sortonColumn(1,workinglist)
			finalActionList.append(workinglist[0])
			tofill-=workinglist[0][2]
	if finalActionList==[]: #no actions were found at all. use smallest and crunch
		workinglist=sortonColumn(3,actionlinks)
		workinglist.reverse()
		resultActionList=[[workinglist[0][0],startframe,endframe]]
	else:
		for item in finalActionList:	
			item[1]=random.random()
		finalActionList=sortonColumn(1,finalActionList)
		expandfactor=(endframe-startframe)/((endframe-startframe)-tofill)
		curframe=startframe
		for item in finalActionList:
			resultActionList.append([item[0],curframe,curframe+(item[2]*expandfactor)+2])
			curframe+=(item[2]*expandfactor)
	return resultActionList

def buildNLA(object,actionlinks):
	print ('Building NLA for ' + object.getName())
	
	curframe=bpy.context.scene.frame_current
	bpy.ops.anim.change_frame(frame = 1)
	
	#get all actions from the database
	SQL='SELECT tblActors.ObjectName,tblActors.ID,tblActors.Type,tblActions.ActorID,tblActions.Frame,tblActions.Orders,tblActions.Action FROM tblActors,tblActions '
	SQL+='WHERE tblActors.ObjectName="'+object.getName()+'" AND tblActors.ID=tblActions.ActorID ORDER BY tblActions.Frame;'
	bpy.dbCursor.execute(SQL)
	
	actionList=bpy.dbCursor.fetchall()
	actionsinBlender=obj.animation_data.nla_tracks
	
	if (actionList is not None):
		actionQueue=[]
		baseframe=actionList[0][4]
		for i in range(len(actionList)):
			type=actionList[i][2]
			frame=actionList[i][4]
			orders=actionList[i][5]
			action=actionList[i][6]
		
			if (i+2)<=len(actionList):
				if actionList[i+1][6]<>action:
					actionQueue.append([type,baseframe,actionList[i+1][4]+1,orders,action])
					baseframe=actionList[i+1][4]
				else:
					pass
			else: #last item in list
				actionQueue.append([type,baseframe,baseframe+12,orders,action])
		
		dead=0
		for actionitem in actionQueue:
			type=actionitem[0]
			startframe=actionitem[1]
			endframe=actionitem[2]
			orders=actionitem[3]
			action=actionitem[4]
			if action=="Die":
				SQL='SELECT ActionName,Likelihood,OptimumFrames,MinFrames,MaxFrames FROM tblActionLinks WHERE TypeID="'+type+'" AND Action="'+action+'" ORDER BY 1-(Likelihood*RAND()) LIMIT 1;'
			else:	
				SQL='SELECT ActionName,Likelihood,OptimumFrames,MinFrames,MaxFrames FROM tblActionLinks WHERE TypeID="'+type+'" AND Action="'+action+'";'
			bpy.dbCursor.execute(SQL)
			linkResult=bpy.dbCursor.fetchall()
			if len(linkResult)==0:
				pass
				#print ("There are no Action Links built for Actor type "+type+" and Action "+action+".")
			elif dead==0:
				if action=="Die":
					listforNLA=[[linkResult[0][0],startframe,startframe+linkResult[0][2]]]
				else:
					listforNLA=fitActionsToFrames(linkResult,startframe,endframe)
				#print (listforNLA)
				for NLAitem in listforNLA:
					actionname=NLAitem[0]
					acendframe=NLAitem[2]
					acstartframe=NLAitem[1]
						
					# add new strip to NLA and set accordingly...
					nlastrips=object.actionStrips
					actiontoadd=actionsinBlender[actionname]
					nlastrips.append(actiontoadd)
					totalstrips=len(nlastrips)
					laststrip=nlastrips[totalstrips-1]
					laststrip.stripEnd=acendframe
					laststrip.stripStart=acstartframe
					if action=="Die":
						laststrip.flag=(laststrip.flag | 8)
						dead=1
					laststrip.blendIn=5
					laststrip.matchBone='foot.base.l'
					laststrip.flag=(laststrip.flag | 64)
				nlastrips.refreshMatch()
				
		#clean action strips to remove bad blendins
		nlastrips=object.actionStrips
		totalstrips=len(nlastrips)
		for i in range(totalstrips):
			thisstrip=nlastrips[i]
			thisstrip.groupTarget="soldier"
			lastframe=thisstrip.stripEnd
			extension=0
			blendout=0
			for j in range(len(nlastrips)-(i+1)):
				tempstrip=nlastrips[j+i+1]
				if (tempstrip.stripStart>lastframe-5) and (tempstrip.stripStart<lastframe):
					extension=max(extension,(5-(lastframe-tempstrip.stripStart)))
			if extension>0:
				thisstrip.stripEnd+=extension
			elif not (thisstrip.flag & 8):
				thisstrip.blendOut=3
				
		nlastrips[len(nlastrips)-1].blendOut=0
		nlastrips[len(nlastrips)-1].flag|=8
	
	scene.frame_set(curframe)

def setLoDforselected():
	selected=context.selected_objects
	if (selected is not None):
		#find if a camera object is included in the list
		camOb=None
		for object in selected:
			if (object.getType()=='Camera'):
				camOb=object
		if (camOb):
			camMat=camOb.getMatrix()
			camLoc=camMat.translationPart()
			for object in selected:
				if (object<>camOb):
					obMat=object.getMatrix()
					obLoc=obMat.translationPart()
					distance=math.sqrt(((obLoc[0]-camLoc[0])**2)+((obLoc[1]-camLoc[1])**2)+((obLoc[2]-camLoc[2])**2))
					SQL='SELECT GroupName FROM tblCharacters WHERE MinDist<='+str(distance)+' AND TypeID="'+object.name[2]+'" ORDER BY -MinDist LIMIT 1'
					bpy.dbCursor.execute(SQL)
					result=bpy.dbCursor.fetchone()
					if (result):
						obGroup=object.DupGroup
						if obGroup.name<>result[0]:
							newGroup=bpy.data.groups[result[0]]
							if (newGroup):
								object.DupGroup=newGroup
								setNLAforLoD(object)
								
					
		else:
			return "No Camera object in selection."
	
def buildnlaforselected():
	selected=context.selected_objects
	if (selected is not None):
		Blender.Window.DrawProgressBar(0,'Building NLA...')
		totalselected=len(selected)
		thisactor=0
		actionlinks={}
		for actor in selected:
			buildNLA(actor,actionlinks)
			setNLAforLoD(actor)
			thisactor+=1
			Blender.Window.DrawProgressBar(float(thisactor)/totalselected,'Building NLA...')
			refreshMatchBone(actor)
	return 'Done building NLA.'

def fixNLAforselected():
	selected=context.selected_objects
	if (selected is not None):
		Blender.Window.DrawProgressBar(0,'Setting Level of Detail...')
		totalselected=len(selected)
		thisactor=0
		actionlinks={}
		for actor in selected:
			setNLAforLoD(actor)
			thisactor+=1
			Blender.Window.DrawProgressBar(float(thisactor)/totalselected,'Setting Level of Detail...')
	return 'Level of Detail Set.'
	
