import csv
import sys
from operator import itemgetter


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
	if len(signature) > 0:
		toollist = ce.get(period)
		if toollist == None:
			toollist = {}
			ce[period] = toollist
		toolsigset = toollist.get(tool)
		if toolsigset == None:
			toolsigset = set()
			toollist[tool] = toolsigset
		toolsigset.add(signature)
	

def getCumulativeStudentEvolutions(studentEvolutions, toolList):
	rv = {}
	semesters = sorted(studentEvolutions.keys(), key=itemgetter(0,2))
	for i in xrange(0, len(semesters)):
		semester = semesters[i]
		rv[semester] = {}
		for t in toolList:
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
toolSet = set()
for row in clusterReader:
	if row[1] != 'dummy':
		updateStudentEvolutions(row, studentEvolutions)
		toolSet.add(row[2])

toolList = []
toolList.extend(toolSet)
cumulativeStudentEvolutions = getCumulativeStudentEvolutions(studentEvolutions, toolList)


writeStudentEvolutions(studentEvolutions, toolList)
writeStudentEvolutions(cumulativeStudentEvolutions, toolList)

#print cumulativeClusterEvolutions[('2011','Spring',0)]['bandstrlab']

		



sys.exit(1)

