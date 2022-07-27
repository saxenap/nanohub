import csv
import sys
from operator import itemgetter

def getLocationFromCluster(cluster):
	l = cluster.split('|')
	return l[1]+l[2]+l[3]

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

def updateToolUseEvolutions(row, tue):
	cluster = row[0]
	period = getYearSemesterFromCluster(cluster)
	tool = row[2]
	signature = getLocationSignature(row)
	if len(signature) > 0:
		toollist = tue.get(period)
		if toollist == None:
			toollist = {}
			tue[period] = toollist
		toolsigset = toollist.get(tool)
		if toolsigset == None:
			toolsigset = set()
			toollist[tool] = toolsigset
		toolsigset.add(signature)
	

def getCumulativeToolUseEvolutions(toolUseEvolutions, toolList):
	rv = {}
	semesters = sorted(toolUseEvolutions.keys(), key=itemgetter(0,2))
	for i in xrange(0, len(semesters)):
		semester = semesters[i]
		rv[semester] = {}
		for t in toolList:
			rv[semester][t] = set()
			for j in xrange(0, i+1):
				oldset = toolUseEvolutions[semesters[j]].get(t)
				if oldset != None:
					rv[semester][t] |= oldset
	return rv


def writeToolUseEvolutions(toolUseEvolutions, toolList):
	writer = csv.writer(sys.stdout)
	outHeaderRow = ['']
	for t in toolList:
		outHeaderRow.append(t)
	writer.writerow(outHeaderRow)
	semesters = sorted(toolUseEvolutions.keys(), key=itemgetter(0,2))
	for s in semesters:
		outrow =[s]
		semesterToolLocations = toolUseEvolutions[s]
		for t in toolList:
			toolLocations = semesterToolLocations.get(t)
			tlc = 0
			if toolLocations != None:
				tlc = len(toolLocations)
			outrow.append(str(tlc))
		writer.writerow(outrow)


def writeInstitutionEvolutions(toolUseEvolutions, toolsubset):
	institutionEvolutions = {}
	for period in toolUseEvolutions:
		tools = toolUseEvolutions[period]
		institutions = set()
		for tool in tools:
			if toolsubset == None or tool in toolsubset:
				toolinstitutions = tools[tool]
				institutions = institutions | toolinstitutions
		institutionEvolutions[period] = institutions
	semesters = sorted(institutionEvolutions.keys(), key=itemgetter(0,2))
	writer = csv.writer(sys.stdout)
	cumulativeSet = set()
	for s in semesters:
		cumulativeSet = cumulativeSet | institutionEvolutions[s]
		writer.writerow([s, str(len(cumulativeSet))])


		

clusterReader = csv.reader(open(sys.argv[1],'r'))

row = clusterReader.next()

expectedHeader = ['cluster','user','tool','day','clustersize','city','state','country','clusterStart','clusterEnd','institution']

if row != expectedHeader:
	print >> sys.stderr, 'Header row is not as expected!'
	sys.exit(1)


toolUseEvolutions = {}
toolSet = set()
for row in clusterReader:
	if row[1] != 'dummy':
		updateToolUseEvolutions(row, toolUseEvolutions)
		toolSet.add(row[2])

toolList = []
toolList.extend(toolSet)
cumulativeToolUseEvolutions = getCumulativeToolUseEvolutions(toolUseEvolutions, toolList)


writeToolUseEvolutions(toolUseEvolutions, toolList)
writeToolUseEvolutions(cumulativeToolUseEvolutions, toolList)

writeInstitutionEvolutions(toolUseEvolutions, None)
writeInstitutionEvolutions(toolUseEvolutions, ['crystal_viewer', 'qdot', 'abacus', 'mosfet', 'pntoy', 'bandstrlab'])

#print cumulativeToolUseEvolutions[('2011','Spring',0)]['bandstrlab']

		



sys.exit(1)

singleSigs = 0
multiSigs = 0
toolsEncountered = 0
#want to sort these from smallest to largest first, secondarily from latest to earliest
x = []

for key in toolUseEvolutions:
	uses = toolUseEvolutions[key]
	sortedUses = sorted(uses.values())
	x.append((key, sortedUses, -sortedUses[0], len(sortedUses)))
	if len(uses) == 1:
		singleSigs += 1
	else:
		multiSigs += 1

writer = csv.writer(sys.stdout)
y = sorted(x, key=itemgetter(3,2)) 
toolsEncountered = 0
outHeaderRow = ['Day']
for r in y:
	outHeaderRow.append(r[0])
#writer.writerow(outHeaderRow)
outmatrix = []
for r in y:
	toolsEncountered += 1
	locCount = 0
	for q in r[1]:
		outrow = []
		locCount += 1
		outrow.append(q)
		for i in xrange(1, toolsEncountered):
			outrow.append('')
		outrow.append(str(locCount))

		outmatrix.append(outrow)
		#writer.writerow(outrow)
sortedOutmatrix = sorted(outmatrix, key=itemgetter(0)) 
previousRow = None
for row in sortedOutmatrix:
	itemsCounted = 0
	for item in row:
		if previousRow == None:
			break
		elif itemsCounted != 0:
			if row[itemsCounted] == '':
				row[itemsCounted] = previousRow[itemsCounted]
		itemsCounted += 1

writer.writerow(outHeaderRow)
for i in sortedOutmatrix:
	writer.writerow(i)
			



#print >> sys.stderr, y
#print 'Singles', singleSigs, 'Multis', multiSigs
#print toolUseEvolutions['nsoptics']
#print toolUseEvolutions['bandstrlab']
#print toolUseEvolutions
