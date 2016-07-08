import bpy, sqlite3

def ChangeOrders(team,orders,target):
	#clear and set Orders
	if not target:
		target=1
	if orders == 'March' or orders == 'StrictMarch' or orders == 'Directed' or orders == 'Target' or orders == 'Mill' or orders == 'StrictMill' or orders  == 'Rank':
		#print orders + '*' + target + '*' + str(target)
		orders += str(target)
		bpy.dbCursor.execute('UPDATE tblOrders SET Orders="' + orders + '", SpeedMultilpier = 1 WHERE team="' + team + '"')
	else:
		bpy.dbCursor.execute('UPDATE tblOrders SET Orders="' + orders + '", SpeedMultilpier = ' + str(target) + ' WHERE team="' + team + '"')
	return 'Ordered ' + team + ' to ' + orders + '.'
