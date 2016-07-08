bl_info = {
	"name": "BlenderPeople",
	"author": "John Roper",
	"version": (1, 0, 0),
	"blender": (2, 76, 0),
	"location": "Node Editor > Toolbar > Compositor's Dream",
	"description": "Create cool crowd simulation",
	"warning": "",
	"wiki_url": "",
	"category": "Animation",
	}

from bpy import *
import bpy
import sqlite3
import CheckDB,Initialization,BuildTree,Main,AutoInitCnC,ManualCnC,ChangeOrders,ActorQueries,Effectors,Locomotion,BuildNLA,Replacement
reload(Main)

host = Draw.Create('127.0.0.1')
password = Draw.Create('')
user = Draw.Create('root')
message = Draw.Create('')

msgWindow01    = Draw.Create("> Connected to Database")
msgWindow02    = Draw.Create(">")
msgWindow03    = Draw.Create(">")
msgWindow04    = Draw.Create("> Blender People 0.8")
msgWindow05    = Draw.Create(">     (c) Roland Hess 2006")
Blender.resolution = 12

orderlist=['Attack','Directed','StrictDefend','Defend','StrictMarch','March','StrictMill','Mill','Target','Rank','RegroupMain','RegroupCommander','Retreat']
teamlist=['a','b']
orders = Draw.Create(0)
number = Draw.Create(1)
toggle = Draw.Create(0)
team = Draw.Create(0)
target = Draw.Create("")
general = Draw.Create(1)
obstacle = Draw.Create(1)
information = Draw.Create(0)
simtools = Draw.Create(0)

# character stat variables
globalID = 0
dbID = Draw.Create(0)
dbType = Draw.Create('Type')
dbTeam = Draw.Create('Team')
dbObjectName = Draw.Create('Name')
dbOrderSpeed = Draw.Create(1.0)
dbOrders = Draw.Create(0)
dbOrderParam = Draw.Create('')
dbCommanderID = Draw.Create(0)
dbSpeed = Draw.Create(0.0)
dbAttack = Draw.Create(0.0)
dbDefense = Draw.Create(0.0)
dbIntellect = Draw.Create(0.0)
dbHealth = Draw.Create(0.0)
dbFieldofView = Draw.Create(0.0)
dbMaxTurn = Draw.Create(0.0)
dbWeapon = Draw.Create('Weapon')
dbAttackRadius = Draw.Create(0.0)
dbChargeRadius = Draw.Create(0.0)
dbCowardRadius = Draw.Create(0.0)
dbBuddyRadius = Draw.Create(0.0)
dbLoyalty = Draw.Create(0.0)
dbActorRadius = Draw.Create(0.0)
defaultpathmode = 'terrain'
pathmodes={'terrain':1,'astar':2,'none':3}
reversepathmodes={1:'terrain',2:'astar',3:'none'}

# character type variables
originalType = ""
TypeMenuList = []
TypeMenu = Draw.Create(0)
tpTypeID = Draw.Create('a')
tpTypeName = Draw.Create('Name')
tpSpeed = Draw.Create(0.0)
tpSpeedV = Draw.Create(0.0)
tpAttackRadius = Draw.Create(0.0)
tpAttackRadiusV = Draw.Create(0.0)
tpChargeRadius = Draw.Create(0.0)
tpChargeRadiusV = Draw.Create(0.0)
tpCowardRadius = Draw.Create(0.0)
tpCowardRadiusV = Draw.Create(0.0)
tpBuddyRadius = Draw.Create(0.0)
tpBuddyRadiusV = Draw.Create(0.0)
tpHealth = Draw.Create(0.0)
tpHealthV = Draw.Create(0.0)
tpAttack = Draw.Create(0.0)
tpAttackV = Draw.Create(0.0)
tpDefense = Draw.Create(0.0)
tpDefenseV = Draw.Create(0.0)
tpIntellect = Draw.Create(0.0)
tpIntellectV = Draw.Create(0.0)
tpFieldofView = Draw.Create(0.0)
tpFieldofViewV = Draw.Create(0.0)
tpMaxTurn = Draw.Create(0.0)
tpMaxTurnV = Draw.Create(0.0)
tpActorRadius = Draw.Create(0.0)

#simulation tools
AffectsList = ['All','Team','Type']
AttributeList = ['Health','Speed','Attack','Defense','Intellect','CommanderID','FieldofView','MaxTurn','AttackRadius','ChargeRadius','CowardRadius','BuddyRadius']
OperatorList = ['=','*','/','+','-']
DurationList = ['Permanent','Temporary']
EffectorName = 'None'
efAffects = Draw.Create(1)
efAffectsValue = Draw.Create('')
efAttributeMenu = Draw.Create(1)
efOperatorMenu = Draw.Create(1)
efValue = Draw.Create(0.0)
efAction = Draw.Create('None')
efActive = Draw.Create(1)
efDuration = Draw.Create(1)

def main():
	CheckDB.CheckDB()
	
	#register the sqlite3 cursor in the Blender object for other scripts to use
	Blender.barriers = 1
	
	Blender.globalGround = {}

	BuildTree.loadTree()
	
	print
	print 'Connection to DB Successfully established'
	
	Draw.Register(drawGUI, event, buttonEvents) # refresh all windows

def drawMySQL():
	global testbutton, host, password, user, message

	BGL.glClearColor(0.753, 0.753, 0.753, 0.0)
	BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)


	BGL.glColor3f(0.000, 0.000, 0.000)
	BGL.glRasterPos2i(24, 252)
	Draw.Text('Password:')
	BGL.glRasterPos2i(24, 276)
	Draw.Text('User:')
	BGL.glRasterPos2i(24, 300)
	Draw.Text('Host:')
	BGL.glRasterPos2i(24, 380)
	Draw.Text('Enter your configuration here for your')
	BGL.glRasterPos2i(24, 360)
	Draw.Text("MySQL setup. If you've done the default")
	BGL.glRasterPos2i(24, 340)
	Draw.Text('install of MySQL, you should only need')
	BGL.glRasterPos2i(24, 320)
	Draw.Text('to enter the correct password.')
	BGL.glRasterPos2i(24, 428)
	Draw.Text('BlenderPeople MySQL Configuration')

	Draw.Button('Test Connection', 1, 24, 208, 120, 23, '')
	Draw.Button('Quit',6,150,208,80,23, '')

	host = Draw.String('', 2, 88, 290, 151, 23, host.val, 200, '')
	password = Draw.String('', 3, 88, 242, 151, 23, password.val, 200, '')
	user = Draw.String('', 4, 88, 266, 151, 23, user.val, 200, '')
	message = Draw.String('', 5, 56, 160, 151, 23, message.val, 200, '')

def MySQLevent(evt, val):
	if (evt== Draw.QKEY or evt== Draw.ESCKEY and not val): Draw.Exit()
def MySQLbevent(evt):
	if evt==1:
		try:
			dbConn = sqlite3.connect(host.val, user.val, password.val)
		except:
			message.val='Connection failed.'
		else: #connection successful
			newtxt=Blender.Text.New("MySQLInfo")
			newtxt.write(host.val+"\n"+user.val+"\n"+password.val+"\n")
			message.val = 'Connection Succeeded!'
			main()
		Blender.Redraw()
	elif evt==6:
		Draw.Exit()

def drawGUI():

    global number, toggle, orders, team, target, general, information, simtools
    global msgWindow01,msgWindow02,msgWindow03,msgWindow04,msgWindow05,pathmodes
    global dbID,dbType,dbTeam,dbObjectName,dbCommanderID,dbOrderSpeed,dbSpeed,dbAttack,dbActorRadius,dbOrderParam
    global dbDefense,dbIntellect,dbHealth,dbFieldofView,dbMaxTurn,dbPathmode,dbOrders,defaultpathmode
    global dbAttackRadius,dbChargeRadius,dbCowardRadius,dbBuddyRadius,dbLoyalty,globalID
    global tpTypeID,tpTypeName,tpSpeed,tpSpeedV,tpAttackRadius,tpAttackRadiusV,tpChargeRadius
    global tpChargeRadiusV,tpCowardRadius,tpCowardRadiusV,tpBuddyRadius,tpBuddyRadiusV,originalType
    global tpHealth,tpHealthV,tpAttack,tpAttackV,tpDefense,tpDefenseV,tpIntellect,tpIntellectV
    global tpFieldofView,tpFieldofViewV,tpMaxTurn,tpMaxTurnV,tpActorRadius,TypeMenuList,TypeMenu,EffectorName,efDuration,DurationList
    global AffectsList,AttributeList,OperatorList,efAffects,efAffectsValue,efAttributeMenu,efOperatorMenu,efValue,efAction,efActive

    BGL.glClearColor(0.5, 0.5, 0.5, 0.0)
    BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)

    Draw.Button("Exit", 10, 12, 12, 56, 18)
    #Draw.Toggle("Obstacles", 30, 270, 12, 70, 18, obstacle.val, 'Turn vert paint obstacles on and off')
   
	#Info Window

    msgWindow05 = Draw.String("", 81, 4, 478, 361, 18, msgWindow05.val, 45)
    msgWindow04 = Draw.String("", 81, 4, 496, 361, 18, msgWindow04.val, 45)
    msgWindow03 = Draw.String("", 81, 4, 514, 361, 18, msgWindow03.val, 45)
    msgWindow02 = Draw.String("", 81, 4, 532, 361, 18, msgWindow02.val, 45)
    msgWindow01 = Draw.String("", 81, 4, 550, 361, 18, msgWindow01.val, 45)

    general = Draw.Toggle('General', 99, 4, 450, 110, 18, general.val, 'Setup, orders and simulation.')
    information = Draw.Toggle('Information', 98, 124, 450, 110, 18, information.val, 'Info about actors.')
    simtools = Draw.Toggle('Sim. Tools', 97, 244, 450, 110, 18, simtools.val, 'Simulation Tools - Effectors.')

    if general.val == 1:
        #Setup widgets

        BGL.glColor3ub(219, 134, 134)
        BGL.glRectf(4, 320, 365, 430)
   
        BGL.glColor3ub(0, 0, 0)
        BGL.glRasterPos2d(12, 410)
        Draw.Text("Setup")
        BGL.glRasterPos2d(140, 385)
        Draw.Text("Clear database and create actors")
        BGL.glRasterPos2d(140, 360)
        Draw.Text("Create search tree for ground")
        BGL.glRasterPos2d(140, 335)
        Draw.Text("Reset Actor health and location")
   
        Draw.Button("Initialize Actors", 2, 12, 380, 120, 20)
        Draw.Button("Initialize Ground", 3, 12, 355, 120, 20)
        Draw.Button("Reset Actors", 16, 12, 330, 120, 20)
   
        #Command and Control widgets
   
        BGL.glColor3ub(254, 255, 184)
        BGL.glRectf(4, 225, 365, 310)
   
        BGL.glColor3ub(0, 0, 0)
        BGL.glRasterPos2d(12, 290)
        Draw.Text("Command and Control")
        BGL.glRasterPos2d(140, 265)
        Draw.Text("Do CnC by proximity and name")
        BGL.glRasterPos2d(140, 240)
        Draw.Text("Assign selected Actors to active object")
   
        Draw.Button("Automatic CnC", 5, 12, 260, 120, 20)
        Draw.Button("Manual CnC", 6, 12, 235, 120, 20)
   
        #Orders widgets

        BGL.glColor3ub(220,220,255)
        BGL.glRectf(4, 145, 365, 215)

        BGL.glColor3ub(0, 0, 0)
        BGL.glRasterPos2d(12, 185)
        Draw.Text("Change Orders")
        orderkinds = 'Orders %t'
        for order in orderlist:
            orderkinds += '|' + order
        orders = Draw.Menu(orderkinds, 90, 70, 155, 150, 20, 1)
        team = Draw.Menu('Teams %t|a|b', 92, 12, 155, 50, 20, 1)
        Draw.Button('Order', 12, 230, 155, 50, 20)
        target = Draw.String("",91,290,155,50,20,"",30)

        #Simulate widgets
   
        BGL.glColor3ub(184, 255, 191)
        BGL.glRectf(4, 50, 365, 135)
   
        BGL.glColor3ub(0, 0, 0)
        BGL.glRasterPos2d(12, 115)
        Draw.Text("Simulate")
        #BGL.glRasterPos2d(140, 90)
        #Draw.Text("Run simulation until toggle is released")
        BGL.glRasterPos2d(140, 65)
        Draw.Text("Run simulation for                     turns")
        #toggle = Draw.Toggle("Run", 7, 12, 85, 120, 20, toggle.val)
        Draw.Button("Run", 1, 12, 60, 120, 20)
        number = Draw.Slider("", 4, 245, 60, 70, 20, number.val, 1, 100)

    elif information.val == 1:
        BGL.glRasterPos2d(12,432)
        Draw.Text('Select an Actor and press Get Stats.')

        BGL.glRasterPos2d(12,414)
        Draw.Text('ID#')
        dbID = Draw.Number("", 81, 12, 396, 60, 15, dbID.val, 0, 500000)

        BGL.glRasterPos2d(80,414)
        Draw.Text('Name')
        dbObjectName = Draw.String("", 81, 80, 396, 120, 15, dbObjectName.val, 64)

        BGL.glRasterPos2d(208,414)
        Draw.Text('Type')
        dbType = Draw.String("", 81, 208, 396, 40, 15, dbType.val, 1)

        BGL.glRasterPos2d(256,414)
        Draw.Text('Team')
        dbTeam = Draw.String("", 81, 256, 396, 40, 15, dbTeam.val, 1)

        Draw.Button("Self", 74, 306, 396, 30, 15)

        BGL.glRasterPos2d(288,383)
        Draw.Text('Commander ID')
        dbCommanderID = Draw.Number("", 81, 288, 363, 60, 15, dbCommanderID.val, 0, 500000)

        BGL.glRasterPos2d(80,383)
        Draw.Text('Orders')
        ordermenustring = ''
        for singleOrder in orderlist:
            ordermenustring+=singleOrder+'|'
        ordermenustring=ordermenustring[:-1]
        dbOrders = Draw.Menu(ordermenustring, 81, 80, 363, 120, 15, dbOrders.val)

        BGL.glRasterPos2d(210,383)
        Draw.Text('Params')
        dbOrderParam = Draw.String("", 81, 210, 363, 70, 15, dbOrderParam.val, 30)

        BGL.glRasterPos2d(12,383)
        Draw.Text('xSpeed')
        dbOrderSpeed = Draw.Number("", 81, 12, 363, 60, 15, dbOrderSpeed.val, 0, 5)

        BGL.glRasterPos2d(284,350)
        Draw.Text('Intellect')
        dbIntellect = Draw.Number("", 81, 284, 330, 60, 15, dbIntellect.val, 0, 1)

        BGL.glRasterPos2d(12,350)
        Draw.Text('Speed')
        dbSpeed = Draw.Number("", 81, 12, 330, 60, 15, dbSpeed.val, 0, 20)

        BGL.glRasterPos2d(80,350)
        Draw.Text('Attack')
        dbAttack = Draw.Number("", 81, 80, 330, 60, 15, dbAttack.val, 0, 50)

        BGL.glRasterPos2d(148,350)
        Draw.Text('Defense')
        dbDefense = Draw.Number("", 81, 148, 330, 60, 15, dbDefense.val, 0, 50)

        BGL.glRasterPos2d(216,350)
        Draw.Text('Health')
        dbHealth = Draw.Number("", 81, 216, 330, 60, 15, dbHealth.val, 0, 50)

        BGL.glRasterPos2d(12,318)
        Draw.Text('R-Attack')
        dbAttackRadius = Draw.Number("", 81, 12, 298, 60, 15, dbAttackRadius.val, 0, 100)

        BGL.glRasterPos2d(80,318)
        Draw.Text('R-Charge')
        dbChargeRadius = Draw.Number("", 81, 80, 298, 60, 15, dbChargeRadius.val, 0, 500)

        BGL.glRasterPos2d(148,318)
        Draw.Text('R-Coward')
        dbCowardRadius = Draw.Number("", 81, 148, 298, 60, 15, dbCowardRadius.val, 0, 1000)

        BGL.glRasterPos2d(216,318)
        Draw.Text('R-Buddy')
        dbBuddyRadius = Draw.Number("", 81, 216, 298, 60, 15, dbBuddyRadius.val, 0, 50)

        BGL.glRasterPos2d(284,318)
        Draw.Text('R-Actor')
        dbActorRadius = Draw.Number("", 81, 284, 298, 60, 15, dbActorRadius.val, 0, 10)

        BGL.glRasterPos2d(12,286)
        Draw.Text('View')
        dbFieldofView = Draw.Number("", 81, 12, 266, 60, 15, dbFieldofView.val, 0, 6.28)

        BGL.glRasterPos2d(80,286)
        Draw.Text('MaxTurn')
        dbMaxTurn = Draw.Number("", 81, 80, 266, 60, 15, dbMaxTurn.val, 0, 6.28)

        BGL.glRasterPos2d(148,286)
        Draw.Text('Loyalty')
        dbLoyalty = Draw.Number("", 81, 148, 266, 60, 15, dbLoyalty.val, 0, 1)

        BGL.glRasterPos2d(216,286)
        Draw.Text('Pathfinding')
        dbPathmode = Draw.Menu('Types %t|terrain|astar|none', 81, 216, 266, 130, 15, pathmodes[defaultpathmode])

        Draw.Button('Get Stats', 13, 12, 236, 70, 20)
        Draw.Button('Select Cmndr', 14, 90, 236, 90, 20)
        Draw.Button('Select Subs', 15, 188, 236, 90, 20)
        Draw.Button('Set Stats', 17, 286, 236, 70, 20)

        bpy.dbCursor.execute('SELECT TypeID, TypeName FROM tblTypes')
        TypeMenuList = []
        typeList = bpy.dbCursor.fetchall()
        typeNames = 'Types %t'
        for order in typeList:
            TypeMenuList.append(order[0])
            typeNames += '|' + order[0] + ', ' + order[1]
        TypeMenu = Draw.Menu(typeNames, 18, 12, 35, 150, 20, 1)

        BGL.glRasterPos2d(12,216)
        Draw.Text('Speed')
        tpSpeed = Draw.Number("",81,80,212,60,15,tpSpeed.val, 0, 20)
        tpSpeedV = Draw.Number("",81,140,212,60,15,tpSpeedV.val, 0, 1)

        BGL.glRasterPos2d(12,200)
        Draw.Text('Attack Rad.')
        tpAttackRadius = Draw.Number("",81,80,196,60,15,tpAttackRadius.val, 0, 50)
        tpAttackRadiusV = Draw.Number("",81,140,196,60,15,tpAttackRadiusV.val, 0, 1)

        BGL.glRasterPos2d(12,184)
        Draw.Text('Charge Rad.')
        tpChargeRadius = Draw.Number("",81,80,180,60,15,tpChargeRadius.val, 0, 50)
        tpChargeRadiusV = Draw.Number("",81,140,180,60,15,tpChargeRadiusV.val, 0, 1)

        BGL.glRasterPos2d(12,168)
        Draw.Text('Coward Rad.')
        tpCowardRadius = Draw.Number("",81,80,164,60,15,tpCowardRadius.val, 0, 50)
        tpCowardRadiusV = Draw.Number("",81,140,164,60,15,tpCowardRadiusV.val, 0, 1)

        BGL.glRasterPos2d(12,152)
        Draw.Text('Buddy Rad.')
        tpBuddyRadius = Draw.Number("",81,80,148,60,15,tpBuddyRadius.val, 0, 50)
        tpBuddyRadiusV = Draw.Number("",81,140,148,60,15,tpBuddyRadiusV.val, 0, 1)

        BGL.glRasterPos2d(12,136)
        Draw.Text('Health')
        tpHealth = Draw.Number("",81,80,132,60,15,tpHealth.val, 0, 50)
        tpHealthV = Draw.Number("",81,140,132,60,15,tpHealthV.val, 0, 1)

        BGL.glRasterPos2d(12,120)
        Draw.Text('Attack')
        tpAttack = Draw.Number("",81,80,116,60,15,tpAttack.val, 0, 50)
        tpAttackV = Draw.Number("",81,140,116,60,15,tpAttackV.val, 0, 1)

        BGL.glRasterPos2d(12,104)
        Draw.Text('Defense')
        tpDefense = Draw.Number("",81,80,100,60,15,tpDefense.val, 0, 50)
        tpDefenseV = Draw.Number("",81,140,100,60,15,tpDefenseV.val, 0, 1)

        BGL.glRasterPos2d(12,88)
        Draw.Text('Intellect')
        tpIntellect = Draw.Number("",81,80,84,60,15,tpIntellect.val, 0, 1)
        tpIntellectV = Draw.Number("",81,140,84,60,15,tpIntellectV.val, 0, 1)

        BGL.glRasterPos2d(205,216)
        Draw.Text('Field of View')
        tpFieldofView = Draw.Number("",81,285,212,60,15,tpFieldofView.val, 0, 180)
        tpFieldofViewV = Draw.Number("",81,285,197,60,15,tpFieldofViewV.val, 0, 1)

        BGL.glRasterPos2d(205,177)
        Draw.Text('MaxTurn')
        tpMaxTurn = Draw.Number("",81,285,173,60,15,tpMaxTurn.val, 0, 180)
        tpMaxTurnV = Draw.Number("",81,285,158,60,15,tpMaxTurnV.val, 0, 1)

        BGL.glRasterPos2d(205,138)
        Draw.Text('Name')
        tpTypeName = Draw.String("", 81, 205, 118, 150, 15, tpTypeName.val, 60)

        BGL.glRasterPos2d(205,104)
        Draw.Text('Type Identifier')

        tpTypeID = Draw.String("", 81, 205, 84, 150, 15, tpTypeID.val, 1)

        Draw.Button('Get Type', 19, 170, 35, 60, 20)
        Draw.Button('Set Type', 20, 238, 35, 60, 20)
        Draw.Button('New', 21, 304, 35, 50, 20)

    elif simtools.val == 1:
        #Effectors and Simulation widgets

        BGL.glRasterPos2d(12,220)
        Draw.Text('Effector Name:')
        BGL.glRasterPos2d(12,205)
        Draw.Text(EffectorName)

        BGL.glRasterPos2d(170,220)
        Draw.Text('Duration')
        efDuration = Draw.Menu('Duration %t|Permanent|Temporary', 81, 170, 200, 100, 15, efDuration.val)

        BGL.glRasterPos2d(12,180)
        Draw.Text('Works on these Actors')
        efAffects = Draw.Menu('Affects %t|All|Team|Type', 81, 12, 160, 150, 15, efAffects.val)

        BGL.glRasterPos2d(170,180)
        Draw.Text('Team or Type')
        efAffectsValue = Draw.String("", 81, 170, 160, 60, 15, efAffectsValue.val, 5)

        BGL.glRasterPos2d(12,140)
        Draw.Text('Attribute Affected')
        eam = 'Attributes %t'
        for listitem in AttributeList:
            eam+='|' + listitem
        efAttributeMenu = Draw.Menu(eam, 81, 12, 120, 80, 15, efAttributeMenu.val)

        BGL.glRasterPos2d(120,140)
        Draw.Text('Operator')
        eom = 'Operators %t'
        for listitem in OperatorList:
            eom+='|' + listitem
        efOperatorMenu = Draw.Menu(eom, 81, 120, 120, 40, 15, efOperatorMenu.val)

        BGL.glRasterPos2d(175,140)
        Draw.Text('Value')
        efValue = Draw.Number("", 81, 175, 120, 60, 15, efValue.val, 0, 1000)

        BGL.glRasterPos2d(12,105)Node Editor > Toolbar > Compositor's Dream
        Draw.Text('Associated Action')
        efAction = Draw.String("", 81, 12, 85, 120, 15, efAction.val, 30)

        efActive = Draw.Toggle("Active", 81, 150, 85, 60, 15, efActive.val)

        Draw.Button("Create/Set", 70, 12, 40, 90, 20)
        Draw.Button("Retrieve", 71, 115, 40, 90, 20)
			
        Draw.Button("Generate Locomtion",72,12,360,180,20)
        Draw.Button("Set Level of Detail",73,12,330,180,20)
        Draw.Button("Generate NLA",75,12,300,180,20)

def event(evt, val):
   if ((evt == Draw.QKEY or evt == Draw.ESCKEY) and not val):
      #bpy.dbCursor.disconnect
      #print 'Connection to DB closed.'
      Draw.Exit()
   if (evt == Draw.XKEY and not val):
      toggle.val = 0
   
def buttonEvents(evt):
   
    global toggle, number, obstacle, reversepathmodes, orderlist
    global dbID,dbType,dbTeam,dbObjectName,dbCommanderID,dbOrderSpeed,dbSpeed,dbAttack,dbActorRadius
    global dbDefense,dbIntellect,dbHealth,dbFieldofView,dbMaxTurn,dbPathmode,dbOrders,defaultpathmode
    global dbAttackRadius,dbChargeRadius,dbCowardRadius,dbBuddyRadius,dbLoyalty,globalID,dbOrderParam
   
    global TypeMenu,tpTypeID,tpTypeName,tpSpeed,tpSpeedV,tpAttackRadius,tpAttackRadiusV,tpChargeRadius
    global tpChargeRadiusV,tpCowardRadius,tpCowardRadiusV,tpBuddyRadius,tpBuddyRadiusV
    global tpHealth,tpHealthV,tpAttack,tpAttackV,tpDefense,tpDefenseV,tpIntellect,tpIntellectV
    global tpFieldofView,tpFieldofViewV,tpMaxTurn,tpMaxTurnV,tpActorRadius,TypeMenuList,originalType

    global AffectsList,AttributeList,OperatorList,efAffects,efAffectsValue,efAttributeMenu,efOperatorMenu,efValue,efAction,efActive
    global EffectorName,efDuration,DurationList

    if evt == 1:
        for counter in range(number.val):
            scrollMessage(Effectors.CheckEffectors())
            scrollMessage(Main.Main())
            #Window.DrawProgressBar(float(counter)/number.val,'Moving')
            Draw.Draw()
            Blender.Redraw()
        #Window.DrawProgressBar(1,'Done')
    elif evt == 10:
        Draw.Exit()
    elif evt == 14:
        subObject = Blender.Object.GetSelected()
        if subObject == []:
            scrollMessage('Please select an object.')
            Draw.Draw()
        else:
            subList = ActorQueries.getActor(subObject[0])
            if subList == -1:
                scrollMessage('Please select a registered Actor.')
            else:
                commanderid=subList[6]
                if commanderid > 0:
                    SQLQuery='SELECT ObjectName FROM tblActors WHERE ID=' + str(commanderid)
                    bpy.dbCursor.execute(SQLQuery)
                    SQLResult=bpy.dbCursor.fetchone()
                    if SQLResult:
                        CommanderObject=Blender.Object.Get(SQLResult[0])
                        subObject[0].select(0)
                        CommanderObject.select(1)
                        Blender.Window.RedrawAll()
    elif evt == 15:
        comObject = Blender.Object.GetSelected()
        if comObject == []:
            scrollMessage('Please select an object.')
        else:
            comList = ActorQueries.getActor(comObject[0])
            if comList == -1:
                scrollMessage('Please select a registered Actor.')
            else:
                commanderid=comList[0]
                SQLQuery='SELECT ObjectName FROM tblActors WHERE CommanderID=' + str(commanderid)
                bpy.dbCursor.execute(SQLQuery)
                SQLResult=bpy.dbCursor.fetchall()
                print SQLResult
                for subActor in SQLResult:
                    tempObject = Blender.Object.Get(subActor[0])
                    tempObject.select(1)
                comObject[0].select(1)
                Blender.Window.RedrawAll()
    elif evt == 30:
        if obstacle.val == 0:
            Blender.barriers = 0
        else:
            Blender.barriers = 1
        Draw.Draw()
    elif evt == 2:
        scrollMessage('Initializing...')
        scrollMessage(Initialization.Initialize(bpy.dbCursor))
    elif evt == 3:
        scrollMessage('Building Search Tree...')
        scrollMessage(BuildTree.BuildTree())
        BuildTree.loadTree()
        Draw.Draw()
    elif evt == 16:
        scrollMessage('Resetting...')
        scrollMessage(Initialization.ResetActors(bpy.dbCursor))
    elif evt == 5:
        scrollMessage(AutoInitCnC.AutoInitCnC())
    elif evt == 6:
        ManualCnC.ManualCnC()
    elif evt == 7:
        #while toggle.val == 1:
        #    scrollMessage(Main.Main())
        #    Draw.Draw()
        pass
    elif evt == 12:
        scrollMessage(ChangeOrders.ChangeOrders(teamlist[team.val-1],orderlist[orders.val-1],target.val))
        Draw.Draw()
    elif evt == 99:
        general.val = 1
        information.val = 0
        simtools.val = 0
        Draw.Draw()
    elif evt == 98:
        general.val = 0
        information.val = 1
        simtools.val = 0
        Draw.Draw()
    elif evt == 97:
        general.val = 0
        information.val = 0
        simtools.val = 1
        Draw.Draw()
    elif evt == 13: # Get Actor stats from database and display
        statObject = Blender.Object.GetSelected()
        if statObject == []:
            scrollMessage('Please select an object.')
            Draw.Draw()
        else:
            statList = ActorQueries.getActor(statObject[0])
            if statList == -1:
                scrollMessage('Please select a registered Actor.')
                Draw.Draw()
            else:
                dbID.val = statList[0]
                globalID = dbID.val
                dbType.val = statList[1]
                dbTeam.val = statList[2]
                dbObjectName.val = statList[3]
                dbOrderSpeed.val = statList[4]
                actualorder=statList[5]
                if actualorder == None:
                    actualorder = ''
                    dbOrders.val=0
                    dbOrderParam.val = ''
                else:
                    orderindex=0
                    orderfound=False
                    while (orderfound==False):
                        orderindex+=1
                        orderfound = actualorder.startswith(orderlist[orderindex-1])
                    dbOrders.val = orderindex
                    dbOrderParam.val = actualorder[len(orderlist[orderindex-1]):]
                dbCommanderID.val = statList[6]
                dbSpeed.val = statList[7]
                dbAttack.val = statList[8]
                dbDefense.val = statList[9]
                dbIntellect.val = statList[10]
                dbHealth.val = statList[11]
                dbFieldofView.val = statList[12]
                dbMaxTurn.val = statList[13]
                if statList[14] == None:
                  dbWeapon.val = ''
                else:
                  dbWeapon.val = statList[14]
                dbAttackRadius.val = statList[15]
                dbChargeRadius.val = statList[16]
                dbCowardRadius.val = statList[17]
                dbBuddyRadius.val = statList[18]
                dbLoyalty.val = statList[19]
                dbActorRadius.val = statList[20]
                defaultpathmode = statList[21]
                Draw.Draw()
    elif evt == 17:
        actualorder = orderlist[dbOrders.val-1] + dbOrderParam.val
        statList = [globalID,dbType.val,dbTeam.val,dbObjectName.val,dbOrderSpeed.val,actualorder,dbCommanderID.val,dbSpeed.val,dbAttack.val,dbDefense.val,dbIntellect.val,dbHealth.val,dbFieldofView.val,dbMaxTurn.val,dbWeapon.val,dbAttackRadius.val,dbChargeRadius.val,dbCowardRadius.val,dbBuddyRadius.val,dbLoyalty.val,dbActorRadius,reversepathmodes[dbPathmode.val]]
        scrollMessage(ActorQueries.setActor(statList))
        defaultpathmode=reversepathmodes[dbPathmode.val]
        Draw.Draw()
    elif evt == 74: # Set Actor to be it's own Commander
        dbCommanderID.val = dbID.val
        scrollMessage(ActorQueries.selfCommander(dbID.val))
        Draw.Draw()
    elif evt == 19: # Get Actor Type from database and display
        statList = ActorQueries.getType(TypeMenuList[TypeMenu.val - 1])
        if statList == -1:
            scrollMessage('That Type is not in the database.')
            Draw.Draw()
        else:
            tpTypeID.val = statList[0]
            originalType = tpTypeID.val
            tpTypeName.val = statList[1]
            tpSpeed.val = statList[2]
            tpSpeedV.val = statList[3]
            tpAttackRadius.val = statList[4]
            tpAttackRadiusV.val = statList[5]
            tpChargeRadius.val = statList[6]
            tpChargeRadiusV.val = statList[7]
            tpCowardRadius.val = statList[8]
            tpCowardRadiusV.val = statList[9]
            tpBuddyRadius.val = statList[10]
            tpBuddyRadiusV.val = statList[11]
            tpHealth.val = statList[12]
            tpHealthV.val = statList[13]
            tpAttack.val = statList[14]
            tpAttackV.val = statList[15]
            tpDefense.val = statList[16]
            tpDefenseV.val = statList[17]
            tpIntellect.val = statList[18]
            tpIntellectV.val = statList[19]
            tpFieldofView.val = statList[20]
            tpFieldofViewV.val = statList[21]
            tpMaxTurn.val = statList[22]
            tpMaxTurnV.val = statList[23]
            tpActorRadius.val = statList[24]
            Draw.Draw()
    elif evt == 20: #Set values into display Type
        statList = [tpTypeID.val,tpTypeName.val,tpSpeed.val,tpSpeedV.val,tpAttackRadius.val,tpAttackRadiusV.val]
        statList.extend([tpChargeRadius.val,tpChargeRadiusV.val,tpCowardRadius.val,tpCowardRadiusV.val])
        statList.extend([tpBuddyRadius.val,tpBuddyRadiusV.val,tpHealth.val,tpHealthV.val,tpAttack.val,tpAttackV.val])
        statList.extend([tpDefense.val,tpDefenseV.val,tpIntellect.val,tpIntellectV.val,tpFieldofView.val,tpFieldofViewV.val])
        statList.extend([tpMaxTurn.val,tpMaxTurnV.val,tpActorRadius.val])
        scrollMessage(ActorQueries.setType(statList,originalType))
        Draw.Draw()
    elif evt == 72: #Generate locomotion
        animreturn=Locomotion.locomoteselected()
        scrollMessage(animreturn)
        Draw.Draw()
    elif evt == 73: # Set Level of Detail
        animreturn=BuildNLA.setLoDforselected()
        scrollMessage(animreturn)
        Draw.Draw()	
    elif evt == 75: # Build NLA
        animreturn=BuildNLA.buildnlaforselected()
        scrollMessage(animreturn)
        Draw.Draw()
    elif evt == 71: #Retrieve and Display Effector
        effObject = Blender.Object.GetSelected()
        SQLEffector = ActorQueries.getEffector(effObject[0])
        if SQLEffector==-1:
            scrollMessage('Please select a registered Effector.')
        else:
            EffectorName = SQLEffector[0]
            efAffects.val = AffectsList.index(SQLEffector[1])+1
            efAffectsValue.val = SQLEffector[2]
            efAttributeMenu.val = AttributeList.index(SQLEffector[3])+1
            efOperatorMenu.val = OperatorList.index(SQLEffector[4])+1
            efValue.val = SQLEffector[5]
            efAction.val = SQLEffector[6]
            efActive.val = SQLEffector[7]
            efDuration.val = DurationList.index(SQLEffector[8])+1
            Draw.Draw()        
    elif evt == 70: #Create or Set stats for Effectors
        effObject = Blender.Object.GetSelected()
        SQLEffector = ActorQueries.getEffector(effObject[0])
        if SQLEffector==-1: # Register a new effector
            SQLReturn=ActorQueries.createEffector(effObject[0].getName(),AffectsList[efAffects.val-1],efAffectsValue.val,AttributeList[efAttributeMenu.val-1],OperatorList[efOperatorMenu.val-1],efValue.val,efAction.val,efActive.val,DurationList[efDuration.val-1])
        else: #Effector already exists - reset it
            print AttributeList[efAttributeMenu.val-1],OperatorList[efOperatorMenu.val-1],AffectsList[efAffects.val-1]
            SQLReturn=ActorQueries.setEffector(effObject[0].getName(),AffectsList[efAffects.val-1],efAffectsValue.val,AttributeList[efAttributeMenu.val-1],OperatorList[efOperatorMenu.val-1],efValue.val,efAction.val,efActive.val,DurationList[efDuration.val-1])
        scrollMessage(SQLReturn)
        Draw.Draw()
    elif evt == 21: #Create and display new Type
        newType = ActorQueries.newType()
        if newType <> -1:
            scrollMessage('New type Created.')
            statList = ActorQueries.getType(newType)
            tpTypeID.val = statList[0]
            originalType = tpTypeID.val
            tpTypeName.val = statList[1]
            tpSpeed.val = statList[2]
            tpSpeedV.val = statList[3]
            tpAttackRadius.val = statList[4]
            tpAttackRadiusV.val = statList[5]
            tpChargeRadius.val = statList[6]
            tpChargeRadiusV.val = statList[7]
            tpCowardRadius.val = statList[8]
            tpCowardRadiusV.val = statList[9]
            tpBuddyRadius.val = statList[10]
            tpBuddyRadiusV.val = statList[11]
            tpHealth.val = statList[12]
            tpHealthV.val = statList[13]
            tpAttack.val = statList[14]
            tpAttackV.val = statList[15]
            tpDefense.val = statList[16]
            tpDefenseV.val = statList[17]
            tpIntellect.val = statList[18]
            tpIntellectV.val = statList[19]
            tpFieldofView.val = statList[20]
            tpFieldofViewV.val = statList[21]
            tpMaxTurn.val = statList[22]
            tpMaxTurnV.val = statList[23]
            tpActorRadius.val = statList[24]
            Draw.Draw()
    else:
        return

def scrollMessage(newMessage):
	if newMessage:
		msgWindow01.val = msgWindow02.val
		msgWindow02.val = msgWindow03.val
		msgWindow03.val = msgWindow04.val
		msgWindow04.val = msgWindow05.val
		msgWindow05.val = newMessage
	Draw.Draw()
	
txtnames=[txt2.name for txt2 in Blender.Text.Get()]
try:
	itxt=txtnames.index("MySQLInfo")
	print "MySQLInfo file found...testing."
	try:
		cnctInfoOb=Blender.Text.Get('MySQLInfo')
		connectInfo=cnctInfoOb.asLines()
		dbConn = sqlite3.connect(connectInfo[0], connectInfo[1], connectInfo[2])
	except:
		host.val=connectInfo[0]
		user.val=connectInfo[1]
		password.val=connectInfo[2]
		Blender.Text.unlink(cnctInfoOb)
		Draw.Register(drawMySQL, MySQLevent, MySQLbevent)
		Blender.Redraw()
	else: #connection successful
		#newtxt=Blender.Text.New("MySQLInfo")
		#newtxt.write(host.val+"\n"+user.val+"\n"+password.val+"\n")
		message.val = 'Connection Succeeded!'
		main()
except ValueError:
	#BlenderPeople has never been successfully run...
	#ask for connection info and test the connection
	print "MySQLInfo does not exist."
	Draw.Register(drawMySQL, MySQLevent, MySQLbevent)
	Blender.Redraw()
