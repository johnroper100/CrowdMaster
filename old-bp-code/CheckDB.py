import bpy, sqlite3

def CheckDB(): #See if database and tables have been created
	
	cnctInfoOb=Blender.Text.Get('MySQLInfo')
	connectInfo=cnctInfoOb.asLines()
		
	#initialize sqlite3 connection and cursor
	
	dbConn = sqlite3.connect(connectInfo[0], connectInfo[1], connectInfo[2])
	dbCursor = dbConn.cursor()
	bpy.dbCursor=dbCursor

	SQL='SHOW DATABASES;'
	dbCursor.execute(SQL)
	dbCheck = bpy.dbCursor.fetchall()

	DBexists = 0
	for thisDB in dbCheck:
		if thisDB[0] == 'dbactors' or thisDB[0] == 'dbActors':
			DBexists = 1
			dbConn.close()
			dbConn = sqlite3.connect(connectInfo[0], connectInfo[1], connectInfo[2], 'dbActors')
			dbCursor = dbConn.cursor()
			bpy.dbCursor=dbCursor
			
	if DBexists == 0:
		SQL = 'CREATE DATABASE dbActors;' #Create database
		dbCursor.execute(SQL)

		SQL = 'USE dbActors;' #Set mySQL to use dbActors
		dbCursor.execute(SQL)
		
		SQL = 'SET AUTOCOMMIT=1;'
		dbCursor.execute(SQL)

		SQL='CREATE TABLE tblActors (ID int(11) NOT NULL auto_increment,Type text NOT NULL,Team text NOT NULL,ObjectName tinytext NOT NULL,'
		SQL=SQL+'OrderSpeed float NOT NULL default 0,Orders tinytext,CommanderID int(11) NOT NULL default 0,'
		SQL=SQL+'Speed float NOT NULL default 0,Attack float NOT NULL default 0,Defense float NOT NULL default 0,'
		SQL=SQL+'Intellect float NOT NULL default 0,Health float NOT NULL default 0,FieldofView float NOT NULL default 0,'
		SQL=SQL+'MaxTurn float NOT NULL default 0,Weapon text,AttackRadius float NOT NULL default 0,'
		SQL=SQL+'ChargeRadius float NOT NULL default 0,CowardRadius float NOT NULL default 0,BuddyRadius float NOT NULL default 0,'
		SQL=SQL+'Loyalty float NOT NULL default 0,x float NOT NULL default 0,y float NOT NULL default 0,'
		SQL=SQL+'ActorRadius float NOT NULL default 0,Heading float NOT NULL default 0,Turn int(11) NOT NULL default 0,'
		SQL=SQL+'CurrentState text,OldState text,Pathmode text,PassOrder tinytext,PRIMARY KEY (ID),KEY Team (Team(255)),'
		SQL=SQL+'KEY Name (ObjectName(255))) ENGINE=MYISAM;'
		dbCursor.execute(SQL)

		#SQL='CREATE TABLE tblBarriers (ID int(11) NOT NULL auto_increment,BarrierName tinytext,x float default 0,'
		#SQL=SQL+'y float default 0,BarrierSize varchar(100),BarrierType tinytext,PRIMARY KEY (ID)) ENGINE=MYISAM; '
		#dbCursor.execute(SQL)

		SQL='CREATE TABLE tblEffectors (ID int(11) NOT NULL auto_increment,EffectorName text,Affects tinytext,AffectsValue tinytext,Attribute tinytext,'
		SQL+='Operator tinytext,Action tinytext,Value float default 0,Active tinyint default 1,Duration tinytext,x float,y float,Size float,PRIMARY KEY (ID),Key EffectorName (EffectorName(255))) ENGINE=MYISAM;'
		dbCursor.execute(SQL)
		
		SQL='CREATE TABLE tblGroundtree (ID int(11) NOT NULL auto_increment,x1 tinyint(4) NOT NULL default 0,'
		SQL=SQL+'y1 tinyint(4) NOT NULL default 0,x2 tinyint(4) NOT NULL default 0,y2 tinyint(4) NOT NULL default 0,'
		SQL=SQL+'x3 tinyint(4) NOT NULL default 0,y3 tinyint(4) NOT NULL default 0,x4 tinyint(4) NOT NULL default 0,'
		SQL=SQL+'y4 tinyint(4) NOT NULL default 0,fx1 float NOT NULL default 0,fy1 float NOT NULL default 0,'
		SQL=SQL+'fz1 float NOT NULL default 0,fx2 float NOT NULL default 0,fy2 float NOT NULL default 0,fz2 float NOT NULL default 0,'
		SQL=SQL+'fx3 float NOT NULL default 0,fy3 float NOT NULL default 0,fz3 float NOT NULL default 0,fx4 float NOT NULL default 0,'
		SQL=SQL+'fy4 float NOT NULL default 0,fz4 float NOT NULL default 0,fnx float NOT NULL default 0,fny float NOT NULL default 0,'
		SQL=SQL+'fnz float NOT NULL default 0,r1 smallint(4) NOT NULL default 0,r2 smallint(4) NOT NULL default 0,r3 smallint(4) NOT NULL default 0,'
		SQL=SQL+'r4 smallint(4) NOT NULL default 0,PRIMARY KEY  (ID),KEY Quadrant (x1,y1,x2,y2,x3,y3,x4,y4)) ENGINE=MYISAM; '
		dbCursor.execute(SQL)

		SQL='CREATE TABLE tblAstar (x int(11) NOT NULL default 0,y int(11) NOT NULL default 0,f float,g float,h float,ox int,oy int,list text,color int,'
		SQL=SQL+'PRIMARY KEY (x,y),KEY list (list(255))) ENGINE=MYISAM; '
		dbCursor.execute(SQL)

		SQL='CREATE TABLE tblOrders (ID int(11) NOT NULL auto_increment,Team text,Orders tinytext,'
		SQL=SQL+'SpeedMultilpier float NOT NULL default 0,PRIMARY KEY  (ID),KEY Team (Team(255))) ENGINE=MYISAM; '
		dbCursor.execute(SQL)

		SQL='CREATE TABLE tblActions (ID int(11) NOT NULL auto_increment, ActorID int(11) NOT NULL default 0,'
		SQL+='Frame int(11) NOT NULL default 0, Orders tinytext NOT NULL, Action tinytext NOT NULL, PRIMARY KEY (ID),'
		SQL+='KEY Frame (Frame), KEY ActorID (ActorID)) ENGINE=MYISAM;'
		dbCursor.execute(SQL) 

		SQL='CREATE TABLE tblTypes (ID int(11) NOT NULL auto_increment,TypeID tinytext NOT NULL,TypeName tinytext NOT NULL,'
		SQL=SQL+'Speed float NOT NULL default 0,SpeedV float NOT NULL default 0,AttackRadius float NOT NULL default 0,AttackRadiusV float NOT NULL default 0,'
		SQL=SQL+'ChargeRadius float NOT NULL default 0,ChargeRadiusV float NOT NULL default 0,CowardRadius float NOT NULL default 0,CowardRadiusV float NOT NULL default 0,'
		SQL=SQL+'BuddyRadius float NOT NULL default 0,BuddyRadiusV float NOT NULL default 0,Health float NOT NULL default 0,HealthV float NOT NULL default 0,'
		SQL=SQL+'Attack float NOT NULL default 0,AttackV float NOT NULL default 0,Defense float NOT NULL default 0,DefenseV float NOT NULL default 0,'
		SQL=SQL+'Intellect float NOT NULL default 0,IntellectV float NOT NULL default 0,FieldofView float NOT NULL default 0,FieldofViewV float NOT NULL default 0,'
		SQL=SQL+'MaxTurn float NOT NULL default 0,MaxTurnV float NOT NULL default 0,ActorRadius float NOT NULL default 0,'
		SQL=SQL+'Armature tinytext, PRIMARY KEY (ID),KEY TypeID (TypeID(255))) ENGINE=MYISAM;'
		dbCursor.execute(SQL)
		
		SQL='CREATE TABLE tblCharacters (ID int(11) NOT NULL auto_increment,TypeID tinytext NOT NULL,GroupName tinytext NOT NULL,'
		SQL+='MaxDist float,MinDist float,ArmatureObject tinytext NOT NULL,PRIMARY KEY (ID), KEY TypeID (TypeID(255))) ENGINE=MYISAM;'
		dbCursor.execute(SQL)
		
		linkDataOb=Blender.Text.Get("CharacterData")
		linkData=linkDataOb.asLines()
		for linkLine in linkData:
			SQL='INSERT INTO tblCharacters (TypeID,GroupName,MaxDist,MinDist,ArmatureObject) VALUES '
			SQL+=linkLine
			bpy.dbCursor.execute(SQL)
		
		SQL='CREATE TABLE tblActionLinks (ID int(11) NOT NULL auto_increment,TypeID tinytext NOT NULL,Orders tinytext,Action tinytext,'
		SQL+='Likelihood float,OptimumFrames float,MinFrames float,MaxFrames float, ActionName tinytext NOT NULL,PRIMARY KEY (ID), KEY TypeID (TypeID(255))) ENGINE=MYISAM;'
		dbCursor.execute(SQL)
		
		linkDataOb=Blender.Text.Get("ActionLinksData")
		linkData=linkDataOb.asLines()
		for linkLine in linkData:
			SQL='INSERT INTO tblActionLinks (TypeID,Orders,Action,Likelihood,OptimumFrames,MinFrames,MaxFrames,ActionName) VALUES '
			SQL+=linkLine
			bpy.dbCursor.execute(SQL)
	
		SQL='CREATE TABLE tblWalkCycles (ID int(11) NOT NULL auto_increment,WalkName tinytext NOT NULL,leftstart float,leftend float,rightstart float,'
		SQL+='rightend float,length float,height float,leftname tinytext,rightname tinytext,likelihood float, PRIMARY KEY (ID),KEY WalkName (WalkName(255))) ENGINE=MYISAM;'
		dbCursor.execute(SQL)
		
		SQL='INSERT INTO tblWalkCycles (WalkName,leftstart,leftend,rightstart,rightend,length,height,leftname,rightname,likelihood) '
		SQL+='VALUES ("finalwalk",1,21,21,41,1.4,0.35,"foot.base.l","foot.base.r",1);'
		dbCursor.execute(SQL)
		
		SQL='CREATE TABLE tblRunCycles (ID int(11) NOT NULL auto_increment,RunName tinytext NOT NULL,leftstart float,leftend float,rightstart float,'
		SQL+='rightend float,length float,height float,leftname tinytext,rightname tinytext, likelihood float,PRIMARY KEY (ID),KEY RunName (RunName(255))) ENGINE=MYISAM;'		 
		dbCursor.execute(SQL)
		
		SQL='INSERT INTO tblRunCycles (RunName,leftstart,leftend,rightstart,rightend,length,height,leftname,rightname,likelihood) '
		SQL+='VALUES ("finalwalk",1,21,21,41,8,2,"foot.base.l","foot.base.r",1);'
		dbCursor.execute(SQL)
		
		SQL='CREATE TABLE tblLocomotion (ID int(11) NOT NULL auto_increment,TypeID tinytext NOT NULL,MoveType tinytext NOT NULL,'
		SQL+='ActionName tinytext NOT NULL,Likelihood float, PRIMARY KEY (ID), Key TypeID (TypeID(255))) ENGINE=MYISAM;'
		dbCursor.execute(SQL)
		
		SQL='INSERT INTO tblLocomotion (TypeID,MoveType,ActionName,Likelihood) VALUES ("a","walk","finalwalk",1);'
		dbCursor.execute(SQL)

		SQL='INSERT INTO tblTypes (TypeID,TypeName,Speed,SpeedV,AttackRadius,AttackRadiusV,ChargeRadius,ChargeRadiusV,CowardRadius,CowardRadiusV,BuddyRadius,BuddyRadiusV,Health,HealthV,Attack,AttackV,Defense,DefenseV,Intellect,IntellectV,FieldofView,FieldofViewV,MaxTurn,MaxTurnV,ActorRadius,Armature)'
		SQL+=' VALUES ("a","Swordsman",3,0.05,2,0.15,30,0.25,60,0.1,10,0.1,5,0.4,3,0.2,3,0.2,0.95,0,150,0.1,60,0.1,.6,"soldier");'
		dbCursor.execute(SQL)

		SQL='INSERT INTO tblTypes (TypeID,TypeName,Speed,SpeedV,AttackRadius,AttackRadiusV,ChargeRadius,ChargeRadiusV,CowardRadius,CowardRadiusV,BuddyRadius,BuddyRadiusV,Health,HealthV,Attack,AttackV,Defense,DefenseV,Intellect,IntellectV,FieldofView,FieldofViewV,MaxTurn,MaxTurnV,ActorRadius,Armature)'
		SQL+=' VALUES ("b","Horseman",12,0.05,6,0.15,90,0.2,90,0.15,30,0.3,10,0.2,7,0.2,4,0.2,0.98,0,170,0.1,70,0.1,3,"soldier");'
		dbCursor.execute(SQL)

		print ('Database and tables created.')
	else:
		print ('Database and tables already exist.')
