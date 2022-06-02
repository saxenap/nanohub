import sqlite3
import csv
import os

class FileField:
	def __init__(self, shortname, dbtype):
		self.dbtype = dbtype
		self.shortname = shortname


def createDatabase(dbname, fileFields):
	if os.path.exists(dbname):
		os.remove(dbname)
	conn = sqlite3.connect(dbname)
	createTables(conn, fileFields)
	conn.commit()
	return conn



def createTables(conn, fileFields):
	qry = 'create table clusterelement ('
	qry += 'record int,'
	qry += 'filename varchar,'
	comma = ''
	for field in fileFields:
		qry += comma
		qry += field.shortname
		qry += ' '
		qry += field.dbtype
		comma = ','
	qry += ');'
	c = conn.cursor()
	c.execute(qry)

def insertRecord(data, fileFields, conn):
	if data[1] != 'dummy':
		qry = 'insert into clusterelement ('
		comma = ''
		for element in fileFields:
			qry += comma
			qry += element.shortname
			comma = ','
		qry += ') values ('
		comma = ''
		for v in zip(data, fileFields):
			qry += comma
			quote = ''
			if v[1].dbtype in ['varchar','timestamp']:
				quote = "'"
			qry += quote
			qry += v[0].replace("'","''")
			qry += quote
			comma = ','
		qry += ');'
		print qry
		c = conn.cursor()
		c.execute(qry)
		
		



fileFields = [
	FileField('cluster','varchar'),
	FileField('user','varchar'),
	FileField('tool','varchar'),
	FileField('day','int'),
	FileField('clustersize','int'),
	FileField('city','varchar'),
	FileField('state','varchar'),
	FileField('country','varchar'),
	FileField('clusterStart','timestamp'),
	FileField('clusterEnd','timestamp'),
	FileField('institution','varchar')
]




clusterFile = open('CLUSTERSBYSEMESTER_TOOLSTART/all_aubiceClusters.csv','r')
clusterReader = csv.reader(clusterFile)

header = clusterReader.next()
if header != ['cluster','user','tool','day','clustersize','city','state','country','clusterStart','clusterEnd','institution']:
	print >> sys.stderr, 'ERROR - header does not match expected header'
	exit(1)

conn = createDatabase('clusters.db', fileFields)

for row in clusterReader:
	insertRecord(row, fileFields, conn)



conn.commit()
clusterFile.close()
