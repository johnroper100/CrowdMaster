import bpy, BuildNLA
import math
from bpy import Armature

def bestframe(distance,distList):
	for i in distList:
		if i[1]<=distance:
			lowdist=i
	distList.reverse()
	for i in distList:
		if i[1]>=distance:
			hidist=i
	distList.reverse()
	if distance==lowdist[1]:
		return lowdist[0]
	else:
		return (((hidist[0]-lowdist[0])*(distance-lowdist[1]))/(hidist[1]-lowdist[1]))+lowdist[0]
	
def bestvel(distance,distList):
	for i in distList:
		if i[1]<=distance:
			lowdist=i
	distList.reverse()
	for i in distList:
		if i[1]>=distance:
			hidist=i
	distList.reverse()
	if distance==lowdist[1]:
		return lowdist[0]
	else:
		return (((distance-lowdist[1])/(hidist[0]-lowdist[0]))*(hidist[2]-lowdist[2]))+lowdist[2]

def locomote(armname):
	#grab walking info for this actor from the db
	arm=bpy.data.objects[armname]
	ob=arm
	
	SQL='SELECT tbllocomotion.ActionName FROM tbllocomotion,tblactors WHERE tblactors.ObjectName="' + arm.name + '" AND tblactors.Type=tbllocomotion.TypeID ORDER BY 1-(tbllocomotion.Likelihood*RAND());'
	bpy.dbCursor.execute(SQL)
	SQLResult=bpy.dbCursor.fetchone()
	SQL='SELECT WalkName,leftstart,leftend,rightstart,rightend,length,height,leftname,rightname FROM tblwalkcycles WHERE WalkName="' + SQLResult[0] + '";'
	bpy.dbCursor.execute(SQL)
	SQLResult=bpy.dbCursor.fetchone()
	#get the correct Ipos
	lfbone=SQLResult[7]
	rfbone=SQLResult[8]
	actionname=SQLResult[0]
	runname=SQLResult[0]
	lfrunplant=[SQLResult[1],SQLResult[2]]
	rfrunplant=[SQLResult[3],SQLResult[4]]
	lfplant=[SQLResult[1],SQLResult[2]]
	rfplant=[SQLResult[3],SQLResult[4]]
	
	stridelength = SQLResult[5] #single step length
	stepheight = SQLResult[6]
	runheight = SQLResult[5]
	runlength = SQLResult[6]
	
	#get the walk action, grab its channels and remove the foot channels
	walkactions=Blender.Armature.NLA.GetActions()
	walkaction=walkactions[actionname]
	runaction=walkactions[runname]
	walkactionipos=walkaction.getAllChannelIpos()
	runactionipos=runaction.getAllChannelIpos()
	del runactionipos[lfbone]
	del runactionipos[rfbone]
	del walkactionipos[lfbone]
	del walkactionipos[rfbone]
	
	#create secondary motion action, remove all curves
	builtwalk = Blender.Armature.NLA.CopyAction(walkaction)
	#add bones that are in runaction as well
	builtwalk.removeChannel(lfbone)
	builtwalk.removeChannel(rfbone)
	builtwalk.setName("secondary")
	schannelipos=builtwalk.getAllChannelIpos()
	curves = ['LocX','LocY','LocZ','QuatW','QuatX','QuatY','QuatZ']
	for name, channel in schannelipos.iteritems():
		for curve in curves:
			try:
				channel.delCurve(curve)
			except:
				pass
			channel.addCurve(curve)
	
	checkSQL='SELECT ID, Turn FROM tblActors WHERE ObjectName = "' + armname + '"'
	bpy.dbCursor.execute(checkSQL)
	SQLResult=bpy.dbCursor.fetchone()
	if SQLResult is None:
		return
	checkSQL='SELECT Frame FROM tblActions WHERE ActorID=' + str(SQLResult[0]) + ' ORDER BY Frame DESC LIMIT 1'
	bpy.dbCursor.execute(checkSQL)
	FrameResult=bpy.dbCursor.fetchone()
	if (FrameResult):
		startframe = 1 + SQLResult[1]
		samplestep = 10
		endframe = FrameResult[0] + samplestep

		
		# 1. Make dict of Actor location via matrix at regular time intervals, and cache starting orientation
		
		Blender.Set('curframe',1)
		originalMat = ob.getMatrix()
		
		locDict = {}
		
		for i in range(startframe, endframe+1, samplestep):
			Blender.Set('curframe',i)
			obMat = ob.getMatrix()
			locDict[i]=[obMat[3][0],obMat[3][1],obMat[3][2]]
			
		Blender.Set('curframe',startframe)
			
		# 2. Make a list of frames, distance travelled to date, and velocities in BU/Frame
		
		distList = []
		
		prevelem = []
		prevdist = 0
		distance = 0
		
		for i in range(startframe, endframe+1, samplestep):
			if prevelem==[]:
				distList.append([i,0,0])
				prevelem=locDict[i]
			else:
				matLoc=locDict[i]
				distance=math.sqrt(((matLoc[0]-prevelem[0])**2)+((matLoc[1]-prevelem[1])**2)+((matLoc[2]-prevelem[2])**2))
				distList.append([i,prevdist+distance,distance/samplestep])
				prevdist+=distance
				prevelem=matLoc
				
		# 3. Bake object-level to Action
		
		action=arm.bake_to_action(1)
		
		# 4. Create final list with key positions for each limb
		
		lfipoob = action.getChannelIpo(lfbone)
		lfipo=lfipoob.getName()
		
		lflocX = lfipoob.getCurve('LocX')
		lflocY = lfipoob.getCurve('LocY')
		lflocZ = lfipoob.getCurve('LocZ')
		
		lfquatW = lfipoob.getCurve('QuatW')
		lfquatX = lfipoob.getCurve('QuatX')
		lfquatY = lfipoob.getCurve('QuatY')
		lfquatZ = lfipoob.getCurve('QuatZ')
		
		rfipoob = action.getChannelIpo(rfbone)
		rfipo=rfipoob.getName()
		
		rflocX = rfipoob.getCurve('LocX')
		rflocY = rfipoob.getCurve('LocY')
		rflocZ = rfipoob.getCurve('LocZ')
		
		rfquatW = rfipoob.getCurve('QuatW')
		rfquatX = rfipoob.getCurve('QuatX')
		rfquatY = rfipoob.getCurve('QuatY')
		rfquatZ = rfipoob.getCurve('QuatZ')
		
		maxframesinair=30
		maxwalkvelocity=.4
		minwalkvelocity=.1
		framerate=24 #frames per second
		
		stepcount = 0
		lastlong = 0
		lastrun = 0
		
		currentdist = 0
		evenodd = 0
		lastframe = 0
		
		rfResult=[]
		lfResult=[]
		
		#add starting positions to lists
		rfResult.append([startframe,rfipo,rflocX.evaluate(startframe),rflocY.evaluate(startframe),rflocZ.evaluate(startframe),rfquatW.evaluate(startframe),rfquatX.evaluate(startframe),rfquatY.evaluate(startframe),rfquatZ.evaluate(startframe)])
		lfResult.append([startframe,lfipo,lflocX.evaluate(startframe),lflocY.evaluate(startframe),lflocZ.evaluate(startframe),lfquatW.evaluate(startframe),lfquatX.evaluate(startframe),lfquatY.evaluate(startframe),lfquatZ.evaluate(startframe)])
	
		#make list of distances from start upon which footsteps will fall
		footsteps={}
		listdone=0
		footsteps[0]=[0,"walk"]
		while (listdone==0):
			stepcount += 1
			nextdist = currentdist + stridelength # when walking, stride is uniform in distance
			steptype="walk"
			if (nextdist>distList[-1][1]):
				nextdist=distList[-1][1]
			velocity=bestvel(nextdist,distList) # try a standard walking stride first
			if (velocity>maxwalkvelocity):
				# generate a running distance footstep, based on 2.5 strides per second (a good average)
				steptype="run"
				if (footsteps[stepcount-1][1]=="walk"):
					#nextdist = currentdist + (runlength - stridelength)
					nextdist = currentdist + (((framerate/2.5)*velocity) - stridelength)
				else:
					#nextdist =  currentdist + runlength
					nextdist = currentdist + ((framerate/2.5)*velocity)
			elif (velocity<minwalkvelocity):
				# generate a ministep
				steptype = "mini"
				nextdist = currentdist + (stridelength * 0.5)
			if nextdist>=distList[-1][1]:
				nextdist=distList[-1][1]
				listdone=1
			#print steptype,velocity,(nextdist-currentdist)
			currentdist=nextdist
			footsteps[stepcount]=[nextdist,steptype]
			
		currentdist = 0
		prevstep = 1
		
		#loop through dictionary of footsteps
		for step in range(1,stepcount-1):
			curframe = bestframe(footsteps[step][0],distList) #get the frame number and type info for this step
			curtype = footsteps[step][1]
			if curtype=="mini":
				heightmod=stepheight/2
			elif curtype=="run":
				heightmod=runheight
			else:
				heightmod=stepheight
			if (step+2)<=stepcount: #calculate frame numbers various distances from current
				farframe=bestframe((footsteps[step+1][0]+footsteps[step+2][0])/2,distList) 
				farthird=bestframe(((footsteps[step+1][0]*2)+footsteps[step][0])/3,distList)
			else:
				farframe=bestframe(distList[-1][1],distList)
				farthird=farframe
			prevframe=bestframe((footsteps[step][0]+footsteps[step-1][0])/2,distList)
			nextframe=bestframe((footsteps[step][0]+footsteps[step+1][0])/2,distList)
			frameafter=bestframe(footsteps[step+1][0],distList)
			if (frameafter-curframe)>(maxframesinair*2): #check if the next step has the foot in the air too long
				longstep=1
			else:
				longstep=0
			if nextdist==stridelength:
				prevframe=startframe	
			if evenodd==0: #evenodd alternates between left and right footsteps
				if curtype!="run":
					rfResult.append([curframe,rfipo,rflocX.evaluate(prevframe),rflocY.evaluate(prevframe),rflocZ.evaluate(prevframe),rfquatW.evaluate(prevframe),rfquatX.evaluate(prevframe),rfquatY.evaluate(prevframe),rfquatZ.evaluate(prevframe)])
					if (footsteps[step+1][1]=="run"):
						qfore=(nextframe+curframe)/2
						lfResult.append([curframe,lfipo,lflocX.evaluate(qfore),lflocY.evaluate(qfore),lflocZ.evaluate(qfore),lfquatW.evaluate(qfore),lfquatX.evaluate(qfore),lfquatY.evaluate(qfore),lfquatZ.evaluate(qfore)])				
					else:
						lfResult.append([curframe,lfipo,lflocX.evaluate(nextframe),lflocY.evaluate(nextframe),lflocZ.evaluate(nextframe),lfquatW.evaluate(nextframe),lfquatX.evaluate(nextframe),lfquatY.evaluate(nextframe),lfquatZ.evaluate(nextframe)])
					if longstep==1:
						rfResult.append([curframe+(maxframesinair/2),rfipo,rflocX.evaluate(nextframe),rflocY.evaluate(nextframe),rflocZ.evaluate(nextframe)+heightmod,rfquatW.evaluate(nextframe),rfquatX.evaluate(nextframe),rfquatY.evaluate(nextframe),rfquatZ.evaluate(nextframe)])
						rfResult.append([curframe+maxframesinair,rfipo,rflocX.evaluate(farframe),rflocY.evaluate(farframe),rflocZ.evaluate(farframe),rfquatW.evaluate(farframe),rfquatX.evaluate(farframe),rfquatY.evaluate(farframe),rfquatZ.evaluate(farframe)])
					else:
						rfResult.append([nextframe,rfipo,rflocX.evaluate(nextframe),rflocY.evaluate(nextframe),rflocZ.evaluate(nextframe)+heightmod,rfquatW.evaluate(nextframe),rfquatX.evaluate(nextframe),rfquatY.evaluate(nextframe),rfquatZ.evaluate(nextframe)])
					plant1=lfplant[1]
					plant0=lfplant[0]
					actionipos=walkactionipos
					lastrun=0
				else:
					qfore=(nextframe+curframe)/2
					qback=(prevframe+curframe)/2
					if (lastrun==0):
						qback3=(prevframe+prevstep)/2
						rfResult.append([prevframe,rfipo,rflocX.evaluate(qback3),rflocY.evaluate(qback3),rflocZ.evaluate(qback3),rfquatW.evaluate(qback3),rfquatX.evaluate(qback3),rfquatY.evaluate(qback3),rfquatZ.evaluate(qback3)])
						rfResult.append([qback,rfipo,rflocX.evaluate(qback3),rflocY.evaluate(qback3),rflocZ.evaluate(qback3),rfquatW.evaluate(qback3),rfquatX.evaluate(qback3),rfquatY.evaluate(qback3),rfquatZ.evaluate(qback3)])
					rfResult.append([curframe,rfipo,rflocX.evaluate(qback),rflocY.evaluate(qback),rflocZ.evaluate(qback)+(heightmod*0.6667),rfquatW.evaluate(qback),rfquatX.evaluate(qback),rfquatY.evaluate(qback),rfquatZ.evaluate(qback)])			
					lfResult.append([curframe,lfipo,lflocX.evaluate(qfore),lflocY.evaluate(qfore),lflocZ.evaluate(qfore)+heightmod,lfquatW.evaluate(qfore),lfquatX.evaluate(qfore),lfquatY.evaluate(qfore),lfquatZ.evaluate(qfore)])
					rfResult.append([nextframe,rfipo,rflocX.evaluate(nextframe),rflocY.evaluate(nextframe),rflocZ.evaluate(nextframe)+(heightmod*0.3333),rfquatW.evaluate(nextframe),rfquatX.evaluate(nextframe),rfquatY.evaluate(nextframe),rfquatZ.evaluate(nextframe)])			
					lfResult.append([nextframe,lfipo,lflocX.evaluate(nextframe),lflocY.evaluate(nextframe),lflocZ.evaluate(nextframe),lfquatW.evaluate(nextframe),lfquatX.evaluate(nextframe),lfquatY.evaluate(nextframe),lfquatZ.evaluate(nextframe)])
					lfResult.append([(nextframe+frameafter)/2,lfipo,lflocX.evaluate(nextframe),lflocY.evaluate(nextframe),lflocZ.evaluate(nextframe),lfquatW.evaluate(nextframe),lfquatX.evaluate(nextframe),lfquatY.evaluate(nextframe),lfquatZ.evaluate(nextframe)])
					plant1=lfrunplant[1]
					plant0=lfrunplant[0]
					actionipos=runactionipos
					lastrun=1
				evenodd=1
			else: #other side of evenodd switch
				if curtype!="run":
					if (footsteps[step+1][1]=="run"):
						qfore=(nextframe+curframe)/2
						rfResult.append([curframe,rfipo,rflocX.evaluate(qfore),rflocY.evaluate(qfore),rflocZ.evaluate(qfore),rfquatW.evaluate(qfore),rfquatX.evaluate(qfore),rfquatY.evaluate(qfore),rfquatZ.evaluate(qfore)])
					else:
						rfResult.append([curframe,rfipo,rflocX.evaluate(nextframe),rflocY.evaluate(nextframe),rflocZ.evaluate(nextframe),rfquatW.evaluate(nextframe),rfquatX.evaluate(nextframe),rfquatY.evaluate(nextframe),rfquatZ.evaluate(nextframe)])
					lfResult.append([curframe,lfipo,lflocX.evaluate(prevframe),lflocY.evaluate(prevframe),lflocZ.evaluate(prevframe),lfquatW.evaluate(prevframe),lfquatX.evaluate(prevframe),lfquatY.evaluate(prevframe),lfquatZ.evaluate(prevframe)])
					if longstep==1:
						lfResult.append([curframe+(maxframesinair/2),lfipo,lflocX.evaluate(nextframe),lflocY.evaluate(nextframe),lflocZ.evaluate(nextframe)+heightmod,lfquatW.evaluate(nextframe),lfquatX.evaluate(nextframe),lfquatY.evaluate(nextframe),lfquatZ.evaluate(nextframe)])
						lfResult.append([curframe+maxframesinair,lfipo,lflocX.evaluate(farframe),lflocY.evaluate(farframe),lflocZ.evaluate(farframe),lfquatW.evaluate(farframe),lfquatX.evaluate(farframe),lfquatY.evaluate(farframe),lfquatZ.evaluate(farframe)])
					else:
						lfResult.append([nextframe,lfipo,lflocX.evaluate(nextframe),lflocY.evaluate(nextframe),lflocZ.evaluate(nextframe)+heightmod,lfquatW.evaluate(nextframe),lfquatX.evaluate(nextframe),lfquatY.evaluate(nextframe),lfquatZ.evaluate(nextframe)])
					plant1=rfplant[1]
					plant0=rfplant[0]
					actionipos=walkactionipos
					lastrun=0
				else:
					qfore=(nextframe+curframe)/2
					qback=(prevframe+curframe)/2
					if (lastrun==0):
						qback3=(prevframe+prevstep)/2
						lfResult.append([prevframe,lfipo,lflocX.evaluate(qback3),lflocY.evaluate(qback3),lflocZ.evaluate(qback3),lfquatW.evaluate(qback3),lfquatX.evaluate(qback3),lfquatY.evaluate(qback3),lfquatZ.evaluate(qback3)])
						lfResult.append([qback,lfipo,lflocX.evaluate(qback3),lflocY.evaluate(qback3),lflocZ.evaluate(qback3),lfquatW.evaluate(qback3),lfquatX.evaluate(qback3),lfquatY.evaluate(qback3),lfquatZ.evaluate(qback3)])
					rfResult.append([curframe,rfipo,rflocX.evaluate(qfore),rflocY.evaluate(qfore),rflocZ.evaluate(qfore)+heightmod,rfquatW.evaluate(qfore),rfquatX.evaluate(qfore),rfquatY.evaluate(qfore),rfquatZ.evaluate(qfore)])
					lfResult.append([curframe,lfipo,lflocX.evaluate(qback),lflocY.evaluate(qback),lflocZ.evaluate(qback)+(heightmod*0.6667),lfquatW.evaluate(qback),lfquatX.evaluate(qback),lfquatY.evaluate(qback),lfquatZ.evaluate(qback)])			
					rfResult.append([nextframe,rfipo,rflocX.evaluate(nextframe),rflocY.evaluate(nextframe),rflocZ.evaluate(nextframe),rfquatW.evaluate(nextframe),rfquatX.evaluate(nextframe),rfquatY.evaluate(nextframe),rfquatZ.evaluate(nextframe)])
					lfResult.append([nextframe,lfipo,lflocX.evaluate(nextframe),lflocY.evaluate(nextframe),lflocZ.evaluate(nextframe)+(heightmod*0.3333),lfquatW.evaluate(nextframe),lfquatX.evaluate(nextframe),lfquatY.evaluate(nextframe),lfquatZ.evaluate(nextframe)])			
					rfResult.append([(nextframe+frameafter)/2,rfipo,rflocX.evaluate(nextframe),rflocY.evaluate(nextframe),rflocZ.evaluate(nextframe),rfquatW.evaluate(nextframe),rfquatX.evaluate(nextframe),rfquatY.evaluate(nextframe),rfquatZ.evaluate(nextframe)])
					plant1=rfrunplant[1]
					plant0=rfrunplant[0]
					actionipos=runactionipos
					lastrun=1
				evenodd=0
			#make secondary action keys
			divfactor=(plant1-plant0)/(nextframe-prevframe)
			for channel, ipo in actionipos.iteritems():
				for curve in curves:
					targetipo=schannelipos[channel]
					sourcecurve=ipo.getCurve(curve)
					if (sourcecurve):
						targetcurve=targetipo.getCurve(curve)
						for point in sourcecurve.bezierPoints:
							pointlist=point.getPoints()
							if (plant0<=pointlist[0]) and (pointlist[0]<=plant1):
								targetcurve.addBezier((((pointlist[0]-plant0)/divfactor)+prevframe,pointlist[1]))
			nextdist+=stridelength
			lastlong=longstep
			prevstep=curframe
		
		#add finish position to list
		if evenodd==1:
			lfResult.append([endframe,lfipo,lflocX.evaluate(endframe),lflocY.evaluate(endframe),lflocZ.evaluate(endframe),lfquatW.evaluate(endframe),lfquatX.evaluate(endframe),lfquatY.evaluate(endframe),lfquatZ.evaluate(endframe)])
			rfResult.append([farframe,rfipo,rflocX.evaluate(endframe),rflocY.evaluate(endframe),rflocZ.evaluate(endframe),rfquatW.evaluate(endframe),rfquatX.evaluate(endframe),rfquatY.evaluate(endframe),rfquatZ.evaluate(endframe)])
		else:
			lfResult.append([farframe,lfipo,lflocX.evaluate(endframe),lflocY.evaluate(endframe),lflocZ.evaluate(endframe),lfquatW.evaluate(endframe),lfquatX.evaluate(endframe),lfquatY.evaluate(endframe),lfquatZ.evaluate(endframe)])
			rfResult.append([endframe,rfipo,rflocX.evaluate(endframe),rflocY.evaluate(endframe),rflocZ.evaluate(endframe),rfquatW.evaluate(endframe),rfquatX.evaluate(endframe),rfquatY.evaluate(endframe),rfquatZ.evaluate(endframe)])
		
		# set interpolation and fix curves for secondary motion
		for channel, ipo in walkactionipos.iteritems():
			for curve in curves:
				targetipo=schannelipos[channel]
				targetcurve=targetipo.getCurve(curve)
				targetcurve.setInterpolation("Bezier")
				targetcurve.recalc()
		
		# 5. Replace current Ipo curve values with ones in the lists
		#print "Generating new curves."
		results = [rfResult,lfResult]
		curves = ['LocX','LocY','LocZ','QuatW','QuatX','QuatY','QuatZ']
		
		for result in results:
			ipoob = Blender.Ipo.Get(result[0][1])
			for curve in curves:
				ipoob.delCurve(curve)
				ipoob.addCurve(curve)
			for keypos in result:
				for i in range(0,7):
					currentcurve=ipoob.getCurve(curves[i])
					currentcurve.addBezier((keypos[0],keypos[i+2]))
					currentcurve.recalc()
			for curve in curves:
				currentcurve=ipoob.getCurve(curve)
				currentcurve.setInterpolation("Bezier")
				currentcurve.recalc()
				
		# add new strip to NLA and set accordingly...
		nlastrips=arm.actionStrips
		nlastrips.append(builtwalk)
		totalstrips=len(nlastrips)
		secondstrip=nlastrips[totalstrips-1]
		nlastrips.moveUp(secondstrip)
		secondstrip.actionStart=secondstrip.stripStart
		secondstrip.stripEnd=secondstrip.actionEnd
		secondstrip.flag=(secondstrip.flag | 8)
		ob.setMatrix(originalMat)
	BuildNLA.setNLAforLoD(ob)

def locomoteselected():
	selected = Blender.Object.GetSelected()
	Blender.Window.DrawProgressBar(0,'Walking...')
	totalselected=len(selected)
	thisactor=0
	for Actor in selected:
		locomote(Actor.name)
		thisactor+=1
		Blender.Window.DrawProgressBar(float(thisactor)/totalselected,'Walking...')
		print ('Locomotion Finished for '+Actor.name+'.')
	return 'Locomotion Finished.'
