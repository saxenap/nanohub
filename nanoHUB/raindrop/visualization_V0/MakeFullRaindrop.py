from PIL import Image
from PIL import ImageDraw
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
(opts,args) = parser.parse_args()
if not opts.clusterfilename:
	parser.error('Cluster file not provided')
elif not opts.geofilename:
	parser.error('Geographical file not provided')
elif not opts.rawfilename and (not opts.startdate or not opts.enddate):
	parser.error('Start and end dates must both be given when not supplying a rawfilename')
print>>sys.stderr, opts

sys.stdout = open(opts.clusterfilename.replace(".csv","sequence.txt"),'wb')

clusters = []

geocache = {}
userToGeo = {}

#if len(sys.argv) != 8:
	#print>>sys.stderr, "Usage: ",sys.argv[0]," clusterfile geolocationfile startdate enddate showCohort bgcolor plopwords"
	#print>>sys.stderr, "NOTE: dates are in YYYY-MM-DD format, showCohort and plopwords are a \"Y\" or \"N\" field, bgcolor is either \"B\" or \"W\" "
	#sys.exit(1)
	
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
		


#print "hello"
#sys.exit(1)

#showCohort = (sys.argv[5] == "Y")
showCohort = opts.showcohort
print>>sys.stderr, "SC", showCohort
#showPlopwords = (sys.argv[7] == "Y")
showPlopwords = opts.showplopwords

bgcolor = (0,0,0)
#if sys.argv[6] == "W": bgcolor = (255,255,255)
if opts.white: bgcolor = (255,255,255)

utdpl = UserToolDayPattern.UserToolDayPatternList(opts.startdate, opts.enddate, showCohort)

if opts.rawfilename == None:
	import MySQLdb
	conn = MySQLdb.connect(host = "localhost",
						user = "root",
						passwd = "",
						db = "narwhal_22022011")

	utdpl.grabAllFromDatabase(conn)
	conn.close()
else:
	utdpl.grabAllFromFile(opts.rawfilename)

im = utdpl.makeImage(clusters, geocache, userToGeo, showPlopwords, bgcolor)

im.save(opts.clusterfilename.replace('csv','png'), 'PNG')

