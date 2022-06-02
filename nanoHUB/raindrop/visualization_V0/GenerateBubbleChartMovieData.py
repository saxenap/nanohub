import MySQLdb
import csv
import os
import json
import sys
import copy
from datetime import datetime
#from visual import *


def getSetOfAuthors():
	rv = set()
	theUser = 'hub_read'
	theHost = 'db.nanohub.org'
	thePasswd = 'XXXXXX'
	theDb = 'nanohub'
	conn = MySQLdb.connect(host = theHost, user = theUser, passwd = thePasswd, db = theDb)
	sql =  """
		select jxp.username from jos_citations as jc, jos_citations_authors as jca, jos_xprofiles as jxp
			where jca.cid = jc.id and jxp.uidNumber = jca.uidNumber and jca.uidNumber <> 0 and exp_data = 1 and published = 1;
		"""
	cursor = conn.cursor()
	cursor.execute(sql)
	row = cursor.fetchone()
	while row != None:
		rv.add(row[0])
		row = cursor.fetchone()
	conn.close()
	return rv

#############################
# return a list, first element is a map of day (integer) to a list.  The second element is a list.
# Each of these lists is itself a list.  The first element is first valid day.  The second element is last valid day.
# The third element is a set of students.  Overall it looks like this:
# [map(day, studentlist),[[firstDay, lastDay, set(students)],...,[firstDay, lastDay, set(students)]]]
#############################
def getStudentUsers():
	rv = []
	rv.append({})
	rv.append([])
	theUser = 'hub_read'
	theHost = 'db.nanohub.org'
	thePasswd = 'XXXXXX'
	theDb = 'nanohub'
	theDirectory = 'CLUSTERSBYSEMESTER_TOOLSTART'
	theFile = 'orderList57DT.csv'
	conn = MySQLdb.connect(host = theHost, user = theUser, passwd = thePasswd, db = theDb)
	cursor = conn.cursor()
	for root, dirs, files in os.walk(theDirectory):
		candidateFile = theFile
		if candidateFile in files:
			clusterName = root.replace(theDirectory + '/', '')
			###Get the names for the Year, Season, Start and End from the Prefix (something like "Fall2006")
			clusterYear = clusterName.replace('Fall','').replace('Spring','')
			clusterSeason = clusterName.replace(clusterYear,'')
			clusterStart = ''
			clusterEnd = ''
			if clusterSeason == 'Fall':
				clusterStart = clusterYear + '-07-01'
				clusterEnd = clusterYear + '-12-31'
			elif clusterSeason == 'Spring':
				clusterStart = clusterYear + '-01-01'
				clusterEnd = clusterYear + '-06-30'
			else:
				print "Cannot discern the cluster time period - looking for Fall or Spring in file name"
				sys.exit(1)
			sql = "select to_days(%s), to_days(%s);"
			cursor.execute(sql, [clusterStart, clusterEnd])
			row = cursor.fetchone()
			sublist = [row[0], row[1], set()]
			rv[1].append(sublist)
			reader = csv.reader(open(root + '/' + candidateFile, 'rb'))
			for row in reader:
				for field in row:
					sublist[2].add(field)
	conn.close()
	return rv


def isUserStudent(studentXdayrange, dayInt, user):
	studentList = studentXdayrange[0].get(dayInt)
	if studentList == None:
		for x in studentXdayrange[1]:
			#print dayInt ,x[0], x[1]
			if dayInt >= x[0] and dayInt <= x[1]:
				studentList = x[2]
				studentXdayrange[0][dayInt] = studentList
				break
	return user in studentList
	
def updatePopularities(dayInt, tool, user, authors, studentsXdayrange, popularities):
	dayPopularities = popularities.get(dayInt)
	if dayPopularities == None:
		dayPopularities = {}
		popularities[dayInt] = dayPopularities
	dayXtoolPopularities = dayPopularities.get(tool)
	if dayXtoolPopularities == None:
		dayXtoolPopularities = {}
		dayXtoolPopularities['student'] = 0
		dayXtoolPopularities['researcher'] = 0
		dayXtoolPopularities['other'] = 0
		dayPopularities[tool] = dayXtoolPopularities
	if user in authors:
		dayXtoolPopularities['researcher'] = dayXtoolPopularities['researcher'] + 1
	elif isUserStudent(studentsXdayrange, dayInt, user):
		dayXtoolPopularities['student'] = dayXtoolPopularities['student'] + 1
	else:
		dayXtoolPopularities['other'] = dayXtoolPopularities['other'] + 1


			
	
def accumulatePopularities(popularities, minday, maxday):
	theUser = 'hub_read'
	theHost = 'db.nanohub.org'
	thePasswd = 'XXXXXX'
	theDb = 'nanohub_metrics'
	conn = MySQLdb.connect(host = theHost, user = theUser, passwd = thePasswd, db = theDb)
	cursor = conn.cursor()
	sql = "select from_days(%s)"

	accumulatedPopularities = []
	for i in xrange(minday, maxday + 1):
		cursor.execute(sql, i)
		row = cursor.fetchone()
		dateString = row[0].isoformat()
		lastPopularities = {}
		lengthOfAccumulatedPopularities = len(accumulatedPopularities)
		if lengthOfAccumulatedPopularities > 0:
			lastPopularities = accumulatedPopularities[lengthOfAccumulatedPopularities - 1][2]
		dayPopularities = popularities.get(i)
		if dayPopularities != None:
			nextPopularities = {}
			for tool in dayPopularities:
				nextPopularities[tool] = {}
				for j in ['researcher','student','other']:
					newToolUse = dayPopularities[tool][j]
					nextPopularities[tool][j] = newToolUse
			for tool in lastPopularities:
				newToolUse = nextPopularities.get(tool)
				if newToolUse == None:
					newToolUse = {}
					newToolUse['researcher'] = 0
					newToolUse['student'] = 0
					newToolUse['other'] = 0
					nextPopularities[tool] = newToolUse
				for j in ['researcher','student','other']:
					lastToolUse = lastPopularities[tool][j]
					nextPopularities[tool][j] = newToolUse[j] + lastToolUse

			accumulatedPopularities.append([i, dateString, nextPopularities])
		else:
			accumulatedPopularities.append([i, dateString, copy.deepcopy(lastPopularities)])
	return accumulatedPopularities


def getRunsOfAllTools(toolXrunXgroupMap):
	rv = {}
	rv['researcher'] = 0
	rv['student'] = 0
	rv['other'] = 0
	for tool in toolXrunXgroupMap:
		runXgroupMap = toolXrunXgroupMap[tool]
		for i in ['researcher','student','other']:
			rv[i] = rv[i] + runXgroupMap[i]
	return rv

def normalizeAccumulatedPopularities(accumulatedPopularities):
	#first generate the popularity of the tool within a class of users
	for dailyData in accumulatedPopularities:
		#print dailyData
		runsOfAllTools = getRunsOfAllTools(dailyData[2])
		for tool in dailyData[2]:
			toolUses = dailyData[2][tool]
			totalToolRuns = 0
			for i in ['researcher','student','other']:
				normalizedUses = 0.0
				totalToolRuns += toolUses[i]
				if runsOfAllTools[i] != 0:
					normalizedUses = float(toolUses[i])/float(runsOfAllTools[i])
				toolUses[i] = normalizedUses
			toolUses['totalUseCount'] = totalToolRuns
		#print dailyData
	#next generate normalized popularity among the three groups
	#print "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
	for dailyData in accumulatedPopularities:
		#print dailyData
		for tool in dailyData[2]:
			toolUses = dailyData[2][tool]
			totalPopularity = 0.0
			for i in ['researcher','student','other']:
				totalPopularity += toolUses[i]
			for i in ['researcher','student','other']:
				toolUses[i] = toolUses[i]/totalPopularity
		#print dailyData






authors = getSetOfAuthors()
studentsXdayrange = getStudentUsers()

theUser = 'hub_read'
theHost = 'db.nanohub.org'
thePasswd = 'XXXXXX'
theDb = 'nanohub_metrics'
conn = MySQLdb.connect(host = theHost, user = theUser, passwd = thePasswd, db = theDb)
sql = """
	select jtv.toolname, to_days(datetime) as tds, date(datetime) as thedate, user
		from toolstart as sl, metrics_tool_version as jtv
		where jtv.instance = sl.tool and protocol in (5,6,7) and user <> ''  and datetime < '2012-01-01' order by datetime;
	"""
conn.query(sql)
r = conn.use_result()
row = r.fetch_row()
popularities = {}
minday = 1000000000000
maxday = -1
while len(row) > 0:
	tool = row[0][0]
	dayInt = row[0][1]
	user = row[0][3]
	if dayInt != None:
		minday = min(minday, dayInt)
		maxday = max(maxday, dayInt)
		updatePopularities(dayInt, tool, user, authors, studentsXdayrange, popularities)
	row = r.fetch_row()


accumulatedPopularities = accumulatePopularities(popularities, minday, maxday)
normalizeAccumulatedPopularities(accumulatedPopularities)

#print authors
#print studentsXdayrange
json.dump(accumulatedPopularities, sys.stdout)
