import csv
import sys

#this program takes stuff from a file that has each line as
#user, user, distance, user, distance...
#where the first user is the "center" of a cluster
#and turns it into a file that has each line being a cluster
#user, user, user, user
#
#it also eliminates all subsets of other clusters so that you have
#fewer clusters than in the input file.

if len(sys.argv) != 4:
	print "Usage: ",sys.argv[0]," inputfile outputfile tolerance"
	sys.exit(1)
	
clusterReader = csv.reader(open(sys.argv[1]))

tolerance = float(sys.argv[3])
print sys.argv[3], tolerance
clusterCenter = None
clusteredUser = None

clusters = {}

#Read the clusters in.  Stepping over the elements of a row, this loop
#finds the "clusterCenter" (the initial user) and then finds a user
#followed by a distance, until the line is fully read.
for row in clusterReader:
	clusterCenter = None
	if len(row) > 1:
		for rowElement in row:
			if clusterCenter == None:
				clusterCenter = rowElement
				clusters[clusterCenter] = set()
				clusters[clusterCenter].add(rowElement)
			elif clusteredUser == None:
				clusteredUser = rowElement
				#find a user, then let the loop go again to get the distance for that user
			elif clusteredUser != None and float(rowElement) <= tolerance:
				clusters[clusterCenter].add(clusteredUser)
				clusteredUser = None
			else:
				clusteredUser = None
		if len(clusters[clusterCenter]) == 1:
			del clusters[clusterCenter]

eliminatedClusters = 0

removeClusters = set()

clusterList = clusters.items()

clusterSizeMinimum = 4

#Generate a set of clusters to remove based on one being a superset of another,
#or also if a cluster size does not meat the minimum requirement.
for i in xrange(len(clusterList)):
	if i % 500 == 0: print i
	if len(clusterList[i][1]) <= clusterSizeMinimum:
		removeClusters.add(clusterList[i][0])
	elif clusterList[i][0] not in removeClusters:
		for j in xrange(i+1, len(clusterList)):
			if clusterList[j][0] not in removeClusters:
				if len(clusterList[j][1]) <= clusterSizeMinimum:
					removeClusters.add(clusterList[j][0])
				elif clusterList[i][1] == clusterList[j][1]:
					removeClusters.add(clusterList[j][0])
				elif clusterList[i][1] >= clusterList[j][1]:
					removeClusters.add(clusterList[j][0])
				elif clusterList[i][1] <= clusterList[j][1]:
					removeClusters.add(clusterList[i][0])
					break #if you are going to remove the cluster in the outer loop, then might as well stop and not do any more
					#print "removing cluster ", clusterList[j][0], " because ", clusterList[i][1], " >= ", clusterList[j][1]

#Now actually remove the clusters - couldn't do this before
#because you don't want to change a set while iterating over it.
print "Initially ",len(clusters)," clusters"
for i in removeClusters:
	del clusters[i]

print "Finally ",len(clusters)," clusters"

clusterWriter = csv.writer(open(sys.argv[2], 'w'));

for key in clusters:
	clusterWriter.writerow(list(clusters[key]))
	
