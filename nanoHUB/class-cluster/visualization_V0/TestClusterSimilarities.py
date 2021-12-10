import csv
import sys

#This program combines overlapping clusters into super-clusters
#You run it like:
#python TestClusterSimilarities.py clusterfile > outputlist
#
#clusterfile has lines that are a comma separated list of users all belonging to a cluster
#outputlist will list out the clustered users, one per line, with the word "RESET" on a line
#   when the end of the cluster is reached.  This format is only because I used the file to
#   generate dotplots in MakeFullRaindrop.py


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
		
		

clusterReader = csv.reader(open(sys.argv[1]))

clusters = []

#Could have just created the set from each row rather than marching through all elements in the row, but didn't
#know that at the time
for row in clusterReader:
	rowset = set()
	clusters.append(rowset)
	for elem in row:
		rowset.add(elem);


nSetPairs = 0

setsWithIntersections = []

#determine the list of clusters that intersect with at least one other cluster
#this was only done as a debugging step to see how many clusters did intersect.
for i in xrange(0,len(clusters)):
	for j in xrange(i + 1, len(clusters)):
		intersection = clusters[i] & clusters[j]
		intersectionSize = len(intersection)
		if intersectionSize > 0:
			nSetPairs+=1
			#print "SET1", clusters[i]
			#print "SET2", clusters[j]
			#print "INTERSECTION",intersection
			#print "S1=",len(clusters[i])," S2=",len(clusters[j])," INT=",len(intersection)
			appendIntersectingSetIfNotPresent(setsWithIntersections, clusters[i])
			appendIntersectingSetIfNotPresent(setsWithIntersections, clusters[j])
			
			

#print i, " intersecting pairs "
#print "total sets=", len(clusters)
#print "intersecting sets=", len(setsWithIntersections)




#firstlist will be a list of lists of users, one list for each cluster.
firstList = []
#As clusters are added to "firstlist" they will be taken away from the clusters set.  Continue until there are no
#more clusters left.
first = None
while len(clusters) > 0:
	#if there is a first list from the previous iteration, take all those members away from the remaining clusters so they
	#dont get added to more than one cluster
	#HERE
	#if first != None or 1==2:
	if first != None:
		for remainingCluster in clusters:
			for justClusteredMember in first:
				remainingCluster.discard(justClusteredMember)
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
				first = first | biggestIntersector
				foundIntersector = True


firstList.sort(key=lambda x: -len(x))			
for cluster in firstList:
	clusterString = ""
	for user in cluster:
		if len(clusterString) > 0:
			clusterString += ","
		clusterString += user
	print clusterString
