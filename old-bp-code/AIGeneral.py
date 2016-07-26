import bpy, sqlite3, string

def parseTokens(inString):
	return inString.split(' ')

def setStrategy(inString, team):
	subjectList = ['overall','allied','enemy','actor','object','commandedby','commanderof']
	expressionList = ['average','total','distance','count']
	attributeList = ['Health','Attack','Defense','Loyalty','Speed']
	objectList = ['object','actor','enemycenter','alliedcenter','nearalliedcmd','nearenemycmd']
	operatorList = ['=','<','>','<=','>=','<>','within']
	changeList = ['Orders','Team','OrderSpeed','CommanderID','Speed','Attack','Defense','Intellect','Health','Loyalty','MaxTurn','FieldofView']

	stratList = parseTokens(inString)
	
	#####
	# parse commands for first SQL statement
	#####

	 #check that first statement is a subject and assign
	stratSubjectA = stratList.pop(0)
	if subjectList.count(stratSubjectA) == 0:
		return 'Expected a valid subject.'
	
	#if subject has an argument (object, actor, commandedby, commanderof) assign it to stratRef
	if stratSubjectA <> 'overall' and stratSubjectA<>'allied' and stratSubjectA<>'enemy':
		stratRefA = stratList.pop(0)

	#check the next statement is an expression and assign
	stratExpressionA = stratList.pop(0)
	if expressionList.count(stratExpressionA) == 0:
		return 'Expected a valid expression.'

	#if expression is distance, assign a distance object and reference	
	if stratExpressionA == 'distance':
		stratDistObA = stratList.pop(0)		
		if objectList.count(stratDistObA) == 0:
			return 'Expected an object for Distance.'
		if stratDistObA == 'object' or stratDistObA == 'actor':
			stratDistObAName = stratList.pop(0)
	elif stratExpressionA <> 'count':
		stratAttributeA = stratList.pop(0)
		if attributeList.count(stratAttributeA) == 0:
			return 'Expected a valid Attribute.'

	# Assemble first SQL statement

	Statement01 = 'SELECT '

	if stratExpressionA == 'distance':
		# Build distance SQL statement
		# Build statement for subject location
		if stratSubjectA == 'overall':
			subSQL = 'SELECT avg(x), avg(y) FROM tblActors WHERE Health > 0'
		elif stratSubjectA == 'enemy':
			subSQL = 'SELECT avg(x), avg(y) FROM tblActors WHERE Health > 0 AND Team <> "' + team + '"'
		elif stratSubjectA == 'allied':
			subSQL = 'SELECT avg(x), avg(y) FROM tblActors WHERE Health > 0 AND Team = "' + team + '"'
		elif stratSubjectA == 'actor':
			subSQL = 'SELECT x, y FROM tblActors WHERE ObjectName = "' + stratRefA + '"'
		elif stratSubjectA == 'commandedby':
			subSQL = 'SELECT avg(x), avg(y) FROM tblActors WHERE CommanderID = ' + str(stratRefA)
		elif stratSubjectA == 'commanderof':
			subSQL = 'SELECT x, y FROM tblActors WHERE ID = ' + str(stratRefA)
		elif stratSubjectA == 'object':
			subSQL = stratSubjectA + ' ' + stratRefA

		# Build statement for object location
		if stratDistObA == 'actor':
			obSQL = 'SELECT x, y FROM tblActors WHERE ObjectName = "' + stratDistObAName + '"'
		elif stratDistObA == 'object':
			obSQL = stratDistObA + ' ' + stratDistObAName
		elif stratDistObA == 'enemycenter':
			obSQL = 'SELECT avg(x), avg(y) FROM tblActors WHERE Team <> "' + team + '"'
		elif stratDistObA == 'alliedcenter':
			obSQL = 'SELECT avg(x), avg(y) FROM tblActors WHERE Team = "' + team + '"'
		objectList = ['object','actor','enemycenter','alliedcenter','nearalliedcmd','nearenemycmd']
		
	else:
		# Build tabulated SQL statement
		if stratExpressionA == 'average':
			Statement01 += 'avg('
			deadAlive = ''
		elif stratExpressionA == 'total':
			Statement01 += 'sum('
			deadAlive = ' AND Health > 0'
		else: # Count
			Statement01 += 'count('
			deadAlive = ' AND Health > 0'
			stratAttributeA = 'Health'
		Statement01 += stratAttributeA + '), Team, ID, CommanderID, ObjectName, Health FROM tblActors GROUP BY '
		if stratSubjectA <> 'overall':
			if stratSubjectA == 'enemy':
				Statement01 += 'Team HAVING (Team <> "' + team + '"' + deadAlive + ')'
			elif stratSubjectA == 'allied':
				Statement01 += 'Team HAVING (Team = "' + team + '"' + deadAlive + ')'
			elif stratSubjectA == 'actor':
				Statement01 += 'ObjectName HAVING (ObjectName = "' + stratRefA + '")'
			elif stratSubjectA == 'commandedby':
				Statement01 += 'CommanderID HAVING (CommanderID = ' + str(stratRefA) + deadAlive + ')'
			elif stratSubjectA == 'commanderof':
				Statement01 += 'ID HAVING (ID = ' + str(stratRefA) + ')'
			else:
				return 'Invalid Subject for Expression.'

	return Statement01
	# Statement assembled

testing = setStrategy('allied average Health','b')
print (testing)
