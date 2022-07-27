import csv
import sys
from operator import itemgetter


def getLocationFromCluster(cluster):
	l = cluster.split('|')
	return l[1]+l[2]+l[3]

def getLocationSignature(row):
	cluster = row[0]
	location = getLocationFromCluster(cluster)
	institution = ''
	if len(row) == 11:
		institution = row[10]
	signature = ''
	if len(institution) > 0 and institution != 'UNKNOWN' and not institution.endswith('.net') and not institution.endswith('.com'):
		signature = institution
	elif not location.startswith('UNKNOWN'):
		signature = location
	return signature

def getYearSemesterFromCluster(cluster):
	semesterseasonsorter = 1
	if cluster.startswith('Fall'):
		semester = 'Fall'
		semesterseasonsorter = 1
	else:
		semester = 'Spring'
		semesterseasonsorter = 0
	l = cluster.split('|')
	l2 = l[0].split(semester)
	year = l2[1]
	return (year,semester,semesterseasonsorter)


def updateStudentEvolutions(row, ce):
	cluster = row[0]
	period = getYearSemesterFromCluster(cluster)
	tool = row[2]
	signature = row[1] #user
	locationSignature = getLocationSignature(row)
	if len(signature) > 0:
		clusterlist = ce.get(period)
		if clusterlist == None:
			clusterlist = {}
			ce[period] = clusterlist
		clustersigset = clusterlist.get(locationSignature)
		if clustersigset == None:
			clustersigset = set()
			clusterlist[locationSignature] = clustersigset
		clustersigset.add(signature)
	

def getCumulativeStudentEvolutions(studentEvolutions, clusterList):
	rv = {}
	semesters = sorted(studentEvolutions.keys(), key=itemgetter(0,2))
	for i in xrange(0, len(semesters)):
		semester = semesters[i]
		rv[semester] = {}
		for t in clusterList:
			rv[semester][t] = set()
			for j in xrange(0, i+1):
				oldset = studentEvolutions[semesters[j]].get(t)
				if oldset != None:
					rv[semester][t] |= oldset
	return rv


def writeStudentEvolutions(studentEvolutions, toolList):
	writer = csv.writer(sys.stdout)
	outHeaderRow = ['']
	for t in toolList:
		outHeaderRow.append(t)
	writer.writerow(outHeaderRow)
	semesters = sorted(studentEvolutions.keys(), key=itemgetter(0,2))
	for s in semesters:
		outrow =[s]
		semesterToolStudents = studentEvolutions[s]
		for t in toolList:
			toolStudents = semesterToolStudents.get(t)
			tlc = 0
			if toolStudents != None:
				tlc = len(toolStudents)
			outrow.append(str(tlc))
		writer.writerow(outrow)
		

clusterReader = csv.reader(open(sys.argv[1],'r'))

row = clusterReader.next()

expectedHeader = ['cluster','user','tool','day','clustersize','city','state','country','clusterStart','clusterEnd','institution']

if row != expectedHeader:
	print >> sys.stderr, 'Header row is not as expected!'
	sys.exit(1)


studentEvolutions = {}
clusterSet = set()
for row in clusterReader:
	if row[1] != 'dummy':
		updateStudentEvolutions(row, studentEvolutions)
		clusterSet.add(getLocationSignature(row))

clusterList = []
clusterList.extend(clusterSet)
cumulativeStudentEvolutions = getCumulativeStudentEvolutions(studentEvolutions, clusterList)


writeStudentEvolutions(studentEvolutions, clusterList)
writeStudentEvolutions(cumulativeStudentEvolutions, clusterList)

#print cumulativeClusterEvolutions[('2011','Spring',0)]['bandstrlab']

		



sys.exit(1)

