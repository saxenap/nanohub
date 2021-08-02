import MySQLdb
import csv
import sys

class MultipleUserMatch(Exception):
	def __init(self,value):
		self.value = value
	def __str__(self):
		return repr(value)


conn = MySQLdb.connect(host = "db.nanohub.org",
                        user = "hub_read",
                        passwd = "XXXXXX", 
                        db = "nanohub")
cursor = conn.cursor()

clusterReader = csv.reader(open(sys.argv[1], 'rb'))
clusterWriter = csv.writer(open(sys.argv[1].replace(".csv","_userdata.csv"), 'wb'))

rowsRead = 0
for row in clusterReader:
	rowsRead += 1
	for user in row:
		sql = "select * from jos_xprofiles where username = %s;"
		cursor.execute(sql, user)
		row2 = cursor.fetchone()
		row3 = cursor.fetchone()
		if row3 != None:
			raise MultipleUserMatch(user)
		outrow = ["Cluster" + str(rowsRead)]
		for useratt in row2:
			outrow.append(useratt)
		clusterWriter.writerow(outrow)

