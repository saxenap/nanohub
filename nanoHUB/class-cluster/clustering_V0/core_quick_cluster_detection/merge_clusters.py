import csv
import sys
import code

#import MySQLdb
#import UserToolDayPattern
#from optparse import OptionParser

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

def printClusters(clusters):
    clusters.sort(key=lambda x: -len(x))            
    writer = csv.writer(sys.stdout)
    for cluster in clusters:
        writer.writerow(list(cluster))

def writeClusterFile(clusters, clusterFileName):
    clusters.sort(key=lambda x: -len(x))            
    outfile = open(clusterFileName, 'w')
    writer = csv.writer(outfile)
    for cluster in clusters:
        writer.writerow(list(cluster))
    outfile.close()




# ---------------------------
def generateClusterIntersections(clusters):
    intersections = []
    for i in range(0, len(clusters)):
        for j in range(i + 1, len(clusters)):
            intersection = clusters[i] & clusters[j]
            intersectionSize = len(intersection)
            if intersectionSize > 0:
                intersections.append((intersection, clusters[i], clusters[j]))
    return intersections




def merge_clusters(inparams, clusters):
    '''
    Merge similar clusters together to form super clusters
    '''

    intersections = generateClusterIntersections(clusters)

    iperf = runIntersectionAffinity(clusters, intersections)

    cleanUpRemainingIntersections(clusters, intersections)
    cleanUpRemainingClusters(clusters, 5)
    

    #intersections = generateClusterIntersections(clusters)
    #print(sys.stderr, name, "is", len(intersections))
    return clusters
    
