import csv
import sys
from operator import itemgetter

# ToolToFirstUsePlot <clusterfile> <swaroopsfirstusefile>


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


def updateFirstUses(row, ce):
	cluster = row[0]
	location = getLocationFromCluster(cluster)
	if location.startswith('UNKNOWN'):
		location = ''
	period = getYearSemesterFromCluster(cluster)
	tool = row[2]
	earliestUse = ce.get(tool)
	day = int(row[3])
	institution = ''
	if len(row) == 11 and row[10] != 'UNKNOWN':
		institution = row[10]
	if earliestUse == None or earliestUse[0] > day:
		institutionSet = set()
		if institution != '':
			institutionSet.add(institution)
		ce[tool] = (day,institutionSet, location)
	elif institution != '':
		ce[tool][1].add(institution)

	


clusterReader = csv.reader(open(sys.argv[1],'r'))

row = clusterReader.next()

expectedHeader = ['cluster','user','tool','day','clustersize','city','state','country','clusterStart','clusterEnd','institution']

if row != expectedHeader:
	print >> sys.stderr, 'Header row is not as expected!'
	sys.exit(1)


firstUses = {}
for row in clusterReader:
	if row[1] != 'dummy':
		updateFirstUses(row, firstUses)

#print firstUses
#sys.exit(1)

timeAvailableReader = csv.reader(open(sys.argv[2],'rU'))
row = timeAvailableReader.next()
expectedHeader = ['Tool','URL','toolname','Date Available','Date Available (to_days)','Versions','Total Users','Date First Used in Classroom','Date first used in Classroom (to_day)','Total Classroom Users','Total Classrooms','Institutions','Total Citations','Date First Cited','Date First cited (to_days)','Author Institutions']
if row != expectedHeader:
	print >> sys.stderr, 'Header row is not as expected!'
	sys.exit(1)

writer = csv.writer(sys.stdout)
writer.writerow(['tool','day_available','first_use','first_use_institution','first_use_location','author_institutions','first_use_and_author_institute_same'])

for row in timeAvailableReader:
	tool = row[2].strip()
	dayAvailable = int(row[4].strip())
	authorInstitutions = ''
	if len(row) == 16:
		authorInstitutions = row[15]
	firstUse = firstUses.get(tool)

				
		

	if firstUse != None:
		institutionSet = firstUse[1]
		first_use_and_author_institute_same = 'U'
		if authorInstitutions != '' and len(institutionSet) > 0:
			first_use_and_author_institute_same = 'N'
			for i in institutionSet:
				if authorInstitutions.count(i) > 0:
					first_use_and_author_institute_same = 'Y'
					break
		outrow = [tool, str(dayAvailable), str(firstUse[0]), firstUse[1], firstUse[2], authorInstitutions, first_use_and_author_institute_same]
		writer.writerow(outrow)


sys.exit(1)
