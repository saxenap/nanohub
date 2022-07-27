import mysql.connector
from PIL import Image
from PIL import ImageDraw
# import MySQLdb
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

utdpl = UserToolDayPattern.UserToolDayPatternList('2008-07-01', '2008-12-31', showCohort=False)

utdpl.grabAllFromDatabase(conn)
# geocache = {}
# userToGeo = {}
# geoReader = csv.reader(open(sys.argv[2]))
# for row in geoReader:
#     user = row[0]
#     location = row[1] + "," + row[2] + "," + row[3]
#     if location not in geocache:
#         geocache[location] = []
#     geocache[location].append(user)
#     userToGeo[user] = (location, (row[1], row[2], row[3]))
#
# print(userToGeo)
# clusters = []

# for cluster in order[1:]:
#     clusters.append(cluster)
#     clusterAnchor = None
#     clusterUserPatternList = UserToolDayPattern.UserToolDayPatternList('2008-07-01', '2008-12-31', showCohort=False)
#     for user in cluster[7][1:-1].split(', '):
#         username = user[1:-1]
#         if clusterAnchor is None:
#             clusterAnchor = username
#         clusterUserPatternList.add(utdpl.getUserPattern(username))

for cluster in order[1:]:
    # clusters.append(cluster)
    clusterAnchor = None
    clusterUserPatternList = UserToolDayPattern.UserToolDayPatternList('2008-07-01', '2008-12-31', showCohort=False)
    if clusterAnchor is None:
        clusterAnchor = cluster[1]
    clusterUserPatternList.add(utdpl.getUserPattern(cluster[1]))

    # im = clusterUserPatternList.makeImage(cluster, geocache, userToGeo, True, (0,0,0))
    im = clusterUserPatternList.makeImage(None)

    im.save('/Users/sdy/Desktop/raindrop' + '/' + clusterAnchor + '.png', 'PNG') # enter file path
    print('/Users/sdy/Desktop/raindrop' + '/' + clusterAnchor + '.png', 'PNG')

conn.close()