from PIL import Image
from PIL import ImageDraw
import MySQLdb
import UserToolDayPattern
import csv
import sys


order = []

if len(sys.argv) != 3:
	print "Usage:", sys.argv[0], "<clusterfile> <rootdirforclusterPNGfiles>"
	sys.exit(1)
	
clusterReader = csv.reader(open(sys.argv[1]))
for row in clusterReader:
	cluster = []
	order.append(cluster)
	for elem in row:
		cluster.append(elem)


print "hello"

conn = MySQLdb.connect(host = "localhost",
						user = "root",
						passwd = "",
						db = "narwhal")

utdpl = UserToolDayPattern.UserToolDayPatternList()

utdpl.grabAllFromDatabase(conn)

for cluster in order:
	clusterAnchor = None
	clusterUserPatternList = UserToolDayPattern.UserToolDayPatternList()
	for user in cluster:
		if clusterAnchor == None: clusterAnchor = user
		clusterUserPatternList.add(utdpl.getUserPattern(user))
		

	im = clusterUserPatternList.makeImage(None)

	im.save(sys.argv[2] + '/' + clusterAnchor + '.png', 'PNG')

conn.close()
