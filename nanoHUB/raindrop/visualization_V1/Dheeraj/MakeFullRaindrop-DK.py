from PIL import Image
from PIL import ImageDraw
import mysql.connector
from optparse import OptionParser
import UserToolDayPattern
import csv
import sys

usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("-c", "--clusterfile", action="store", dest="clusterfilename",
                  help="A file listing clusters, one per line")
parser.add_option("-f", "--rawfile", action="store", dest="rawfilename",
                  help="Use a file rather than a database for source data")
parser.add_option("-g", "--geofile", action="store", dest="geofilename",
                  help="Name of file linking users to geographic clusters")
parser.add_option("-s", "--startdate", action="store", dest="startdate",
                  help="Start date of cluster analysis (not needed if using a rawfile)")
parser.add_option("-e", "--enddate", action="store", dest="enddate",
                  help="End date of cluster analysis (not needed if using a rawfile)")
parser.add_option("-k", "--showcohort", action="store_true", dest="showcohort", default=False,
                  help="Show the entire cohort, not just the clusters")
parser.add_option("-w", "--white", action="store_true", dest="white", default=False,
                  help="Use a white background")
parser.add_option("-p", "--plopwords", action="store_false", dest="showplopwords", default=True,
                  help="Put geographics in pixelized font")
(opts, args) = parser.parse_args()
if not opts.clusterfilename:
    parser.error('Cluster file not provided')
elif not opts.geofilename:
    parser.error('Geographical file not provided')
elif not opts.rawfilename and (not opts.startdate or not opts.enddate):
    parser.error('Start and end dates must both be given when not supplying a rawfilename')
print(opts, file=sys.stderr)

sys.stdout = open(opts.clusterfilename.replace(".csv", "_sequence.txt"), 'w')

clusters = []
geocache = {}
userToGeo = {}

if len(sys.argv) >= 2:
    clusterReader = csv.reader(open(opts.clusterfilename))
    for row in clusterReader:
        cluster = []
        clusters.append(cluster)
        for elem in row:
            cluster.append(elem)

if len(sys.argv) >= 3:
    geoReader = csv.reader(open(opts.geofilename))
    for row in geoReader:
        user = row[0]
        location = row[1] + "," + row[2] + "," + row[3]
        if location not in geocache:
            geocache[location] = []
        geocache[location].append(user)
        userToGeo[user] = (location, (row[1], row[2], row[3]))

showCohort = opts.showcohort
print("SC", showCohort, file=sys.stderr)
showPlopwords = opts.showplopwords

bgcolor = (0, 0, 0)
if opts.white: bgcolor = (255, 255, 255)

utdpl = UserToolDayPattern.UserToolDayPatternList(opts.startdate, opts.enddate, showCohort)

if opts.rawfilename is None:
    #conn = mysql.connector.connect(host="127.0.0.1",
    #                               user="shang26_ro",
    #                               passwd="PNY0fvkqHQfx49ry",
    #                               db="nanohub", port=3307)
    conn = application.new_db_engine('nanohub')

    utdpl.grabAllFromDatabase(conn)
    #conn.close()
else:
    utdpl.grabAllFromFile(opts.rawfilename)

im = utdpl.makeImage(clusters, geocache, userToGeo, showPlopwords, bgcolor)

im.save(opts.clusterfilename.replace('csv', 'png'), 'PNG')
print(opts.clusterfilename.replace('csv', 'png'), 'PNG')
