import MySQLdb
import csv
import sys

class MultipleUserMatch(Exception):
	def __init(self,value):
		self.value = value
	def __str__(self):
		return repr(value)


# conn = MySQLdb.connect(host = "db.nanohub.org",
#                         user = "hub_read",
#                         passwd = "XXXXXX",
#                         db = "nanohub")
conn = mysql.connector.connect(host="127.0.0.1",
                               user="shang26_ro",
                               passwd="PNY0fvkqHQfx49ry",
                               db="nanohub", port=3307)
cursor = conn.cursor()

clusterReader = csv.reader(open(sys.argv[1], 'r'))
clusterWriter = csv.writer(open(sys.argv[1].replace(".csv","_userdata.csv"), 'w'))

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

