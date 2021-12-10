from PIL import Image
from PIL import ImageDraw
import mysql.connector
import UserToolDayPattern
import csv
import sys

order = []

if len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "<clusterfile> <rootdirforclusterPNGfiles>")
    sys.exit(1)

clusterReader = csv.reader(open(sys.argv[1]))
for row in clusterReader:
    cluster = []
    order.append(cluster)
    for elem in row:
        cluster.append(elem)

print("hello")

conn = mysql.connector.connect(host="127.0.0.1",
                               user="shang26_ro",
                               passwd="PNY0fvkqHQfx49ry",
                               db="nanohub", port=3307)

utdpl = UserToolDayPattern.UserToolDayPatternList('2008-07-01', '2008-12-31', True)

utdpl.grabAllFromDatabase(conn)

for cluster in order:
    clusterAnchor = None
    clusterUserPatternList = UserToolDayPattern.UserToolDayPatternList('2008-07-01', '2008-12-31', True)
    for user in cluster:
        if clusterAnchor == None: clusterAnchor = user
        clusterUserPatternList.add(utdpl.getUserPattern(user))

    im = clusterUserPatternList.makeImage(None)

    im.save(sys.argv[2] + '/' + clusterAnchor + '.png', 'PNG')

conn.close()
