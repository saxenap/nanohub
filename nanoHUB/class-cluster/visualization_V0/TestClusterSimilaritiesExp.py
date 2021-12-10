import csv
import sys
import UserToolDayPattern
from optparse import OptionParser

#This program combines overlapping clusters into super-clusters
#You run it like:
#python TestClusterSimilarities.py clusterfile geoclusterfile startdate enddate > outputlist
#
#clusterfile has lines that are a comma separated list of users all belonging to a cluster
#outputlist will list out the clustered users, one per line, with the word "RESET" on a line
#   when the end of the cluster is reached.  This format is only because I used the file to
#   generate dotplots in MakeFullRaindrop.py

#####################################
#The below are only needed for making the incremental raindrops as the algorithm proceeds

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
(opts,args) = parser.parse_args()
if not opts.clusterfilename:
	parser.error('Cluster file not provided')
elif not opts.geofilename:
	parser.error('Geographical file not provided')
elif not opts.rawfilename and (not opts.startdate or not opts.enddate):
	parser.error('Start and end dates must both be given when not supplying a rawfilename')
#print opts
#sys.exit(1)

clusters = []

geocache = {}
userToGeo = {}

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

showCohort = False
showPlopwords = True

bgcolor = (0,0,0)


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

	
def geocacheDeepCopy():
	c = {}
	for location in geocache:
		c[location] = list(geocache[location])
	return c

def makeIncrementalRaindrop(step, clusters):
	im = utdpl.makeImage(clusters, geocacheDeepCopy(), userToGeo.copy(), showPlopwords, bgcolor)

	im.save(opts.clusterfilename.replace('.csv', step + '.png'), 'PNG')

#this is the end of the stuff for making incremental raindrop plots
##########################################



#This function maintains a list of clusters that are known to intersect
#with other clusters.  This simply checks if the candidate cluster is already
#a member of the list and if not, adds it.  There are no cluster-cluster
#relationships contained in this list...it is simply a list where the cluster
#in the list is known to intersect with some other cluster.
def appendIntersectingSetIfNotPresent(setsWithIntersections, cluster):
	foundSet = False
	for theSet in setsWithIntersections:
		if theSet == cluster:
			foundSet = True;
			break
	if not foundSet:
		setsWithIntersections.append(cluster)
		
		

def readClusters(filename):
	cfile = open(filename, 'rb')
	clusterReader = csv.reader(cfile)
	clusters = []
	for row in clusterReader:
		rowset = set(row)
		clusters.append(rowset)
	cfile.close()
	return clusters


def generateClusterIntersections(clusters):
	intersections = []
	for i in xrange(0, len(clusters)):
		for j in xrange(i + 1, len(clusters)):
			intersection = clusters[i] & clusters[j]
			intersectionSize = len(intersection)
			if intersectionSize > 0:
				intersections.append((intersection, clusters[i], clusters[j]))
	return intersections

def getIntersectionMeasureForTuple(intersectionTuple):
	return getIntersectionMeasure(intersectionTuple[0], intersectionTuple[1], intersectionTuple[2])

def getIntersectionMeasure(intersection, s1, s2):
	lenInt = float(len(intersection))
	lenS1 = float(len(s1))
	lenS2 = float(len(s2))
	return max(lenInt/lenS1, lenInt/lenS2)

"""
The best intersection is the one with the fewest outside members in one of the sets
"""
def findBestIntersection(intersections):
	intersections.sort(key = lambda x: -getIntersectionMeasure(x[0], x[1], x[2]))
	rv = None
	if len(intersections) > 0: rv = intersections[0]
	return rv


def executeIntersection(intersection, intersections, clusters):
	s1 = intersection[1]
	s2 = intersection[2]
	newSet = s1 | s2
	clusters.remove(s1)
	clusters.remove(s2)
	#it is possible to create a merged set that we already have (not likely)
	if newSet not in clusters:
		removers = []
		for i in intersections:
			if i[1] == s1 or i[2] == s1 or i[1] == s2 or i[2] == s2:
				removers.append(i)
		for i in removers:
			intersections.remove(i)
		for c in clusters:
			i = newSet & c
			intersectionSize = len(i)
			if intersectionSize > 0:
				intersections.append((i, newSet, c))
		clusters.append(newSet)
			

def executeIntersectionCleanup(intersection, intersections, clusters):
	s1 = intersection[1]
	s2 = intersection[2]
	r1 = float(len(intersection[0]))/float(len(s1))
	r2 = float(len(intersection[0]))/float(len(s2))
	removeFrom = s1
	if r1 > r2:
		removeFrom = s2
	removeFrom-=intersection[0]
	intersections.remove(intersection)
	zeroIntersections = []
	#above we removed users from a set, thus potentially invalidating some intersections
	#here we remove those users we just grabbed from all remaining intersections
	for i in intersections:
		x = i[0]
		ibefore = x.copy()
		"""
		"""
		x-=intersection[0]
		x = i[1]
		x-=intersection[0]
		x = i[2]
		x-=intersection[0]
		if len(i[0]) == 0:
			zeroIntersections.append(i)
		if i[0] != i[1] & i[2]:
			print >> sys.stderr, "ERROR"
			print >> sys.stderr, i[0]
			print >> sys.stderr, i[1]
			print >> sys.stderr, i[2]
			print >> sys.stderr, i[1] & i[2]
			print >> sys.stderr, ibefore
			print >> sys.stderr, intersection[0]
		"""
		"""
	for i in zeroIntersections:
		intersections.remove(i)

			

def runIntersectionAffinity(clusters, intersections):
	iperformed = 0
	bi = findBestIntersection(intersections)
	while len(intersections) > 0 and getIntersectionMeasureForTuple(bi) > 0.4:
		executeIntersection(bi, intersections, clusters)
		iperformed += 1
		bi = findBestIntersection(intersections)
	return iperformed

def cleanUpRemainingIntersections(clusters, intersections):
	iperformed = 0
	bi = findBestIntersection(intersections)
	while len(intersections) > 0:
		executeIntersectionCleanup(bi, intersections, clusters)
		iperformed += 1
		bi = findBestIntersection(intersections)
	return iperformed


def cleanUpRemainingClusters(clusters, tolerance):
	clusters.sort(key = lambda x: -len(x))
	while len(clusters) > 0 and len(clusters[len(clusters) - 1]) < tolerance:
		clusters.pop()

def printClusters(clusters,orderListFilename):
	clusters.sort(key=lambda x: -len(x))			
	with open(orderListFilename,'wb') as fp:
		writer = csv.writer(fp)
		for cluster in clusters:
			writer.writerow(list(cluster))


clusters = readClusters(opts.clusterfilename)
intersections = generateClusterIntersections(clusters)
print >> sys.stderr, "cs", len(clusters), "is", len(intersections)
iperf = runIntersectionAffinity(clusters, intersections)
print >> sys.stderr, "iperf",iperf, "cs", len(clusters), "is", len(intersections)
cleanUpRemainingIntersections(clusters, intersections)
cleanUpRemainingClusters(clusters, 5)
orderListFilename = opts.clusterfilename.replace("extractedClusters","orderList")
printClusters(clusters,orderListFilename)
intersections = generateClusterIntersections(clusters)
print >> sys.stderr, "is", len(intersections)

sys.exit(0)


#firstlist will be a list of lists of users, one list for each cluster.
firstList = []
#As clusters are added to "firstlist" they will be taken away from the clusters set.  Continue until there are no
#more clusters left.
first = None
step = 0
while len(clusters) > 0:
	#if there is a first list from the previous iteration, take all those members away from the remaining clusters so they
	#dont get added to more than one cluster
	#HERE
	#if first != None or 1==2:
	if first != None:
		for remainingCluster in clusters:
			nDiscarded = 0
			remainingClusterCopy = remainingCluster.copy()
			for justClusteredMember in first:
				remainingCluster.discard(justClusteredMember)
				nDiscarded += 1
			if nDiscarded > 0:
				#######stuff to make incremental raindrops
				step += 1
				if step <= 250:
					makeIncrementalRaindrop('STEP' + str(step) + '_discard', [remainingClusterCopy, remainingCluster])
				#######end of stuff for incremental raindrops
	#sort to get largest cluster on top of the cluster list
	clusters.sort(key=lambda x: -len(x))
	#We're about to pop off a new cluster to work with, so RESET if we have already processed a cluster
	#if len(firstList) > 0: firstList.append("RESET")
	first = clusters.pop(0)
	if len(first) > 0:
		currentCluster = list(first)
		firstList.append(currentCluster)


		foundIntersector = True
		#Now search through the remaining clusters to find intersecting clusters.  For as long as we find one, we 
		#will keep repeating this loop before RESETing again as done above.
		while foundIntersector:
			foundIntersector = False
			biggestIntersector = None
			bisize = -1
			#find the remaining cluster with the biggest intersection.  In order to be considered, the candidate cluster
			#must intersect with at least 20% of its members...otherwise, we are getting divergent behavior.
			for cluster in clusters:
				isize = len(first & cluster)
				if biggestIntersector == None and isize > 0 and isize > 0.2 * len(cluster) and isize > 2:
					biggestIntersector = cluster
					bisize = len(cluster & first)
				elif biggestIntersector != None and isize > 0 and isize > bisize and isize > 0.2 * len(cluster) and isize > 2:
					bisize = isize
					biggestIntersector = cluster
		
			#now take the biggest intersecting set and add it to the current cluster called "first" and add its
			#members to the global list of clusters.
			if biggestIntersector != None:
				clusters.remove(biggestIntersector)
				#if len(firstList) > 0: firstList.append("NEWMEMBERS")
				#HERE
				#currentCluster = currentCluster + list(biggestIntersector - first)
				for newmember in biggestIntersector - first:
					currentCluster.append(newmember)
				#######stuff to make incremental raindrops
				step += 1
				if step <= 250:
					makeIncrementalRaindrop('STEP' + str(step) + '_merge', [list(first), list(first&biggestIntersector), list(biggestIntersector), currentCluster])
				#######end of stuff for incremental raindrops
				first = first | biggestIntersector
				foundIntersector = True
		#######stuff to make incremental raindrops
		step += 1
		if step <= 250:
			makeIncrementalRaindrop('STEP' + str(step) + '_finish', [currentCluster])
		#######end of stuff for incremental raindrops


firstList.sort(key=lambda x: -len(x))			
for cluster in firstList:
	clusterString = ""
	for user in cluster:
		if len(clusterString) > 0:
			clusterString += ","
		clusterString += user
	print clusterString


