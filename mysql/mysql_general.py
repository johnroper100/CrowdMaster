import bpy
import sys
sys.path.append('C:\Python35\Lib\site-packages')
sys.path.append('C:\Python35\DLLs')
import pymysql

def dbConnect(databaseName, databaseHost, databaseUsername, databasePassword):
    conn = pymysql.connect(host=databaseHost, port=3306, user=databaseUsername, passwd=databasePassword, db=databaseName)
    cursor = conn.cursor()
    
    return conn, cursor

def dbClose(conn, cursor):
    cursor.close()
    conn.close()

def dbVersion(conn, cursor):
    cursor.execute("SELECT VERSION()")
    data = cursor.fetchone()
    print ("Database version : %s " % data)
