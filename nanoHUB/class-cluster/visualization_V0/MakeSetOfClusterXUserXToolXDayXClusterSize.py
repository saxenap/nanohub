from PIL import Image
from PIL import ImageDraw
import MySQLdb
import UserToolDayPattern
import csv
import sys
import os
import GetDomainForUserDuringPeriod


databasehost = 'fdb.nanohub.org'
databasehost = '127.0.0.1'
databaseport = 4406
database = 'nanohub_metrics'
databaseuser = 'hub_read'
databasepassword = 'XXXXXX'
databasesessiontable = 'toolstart'


#This requires two input files
#The first argument is a directory which contains a bunch of directories, each of which has a set of clusters in it.
#	The cluster file in this directory is expected to be named orderList##.csv
#The second argument is the number that fills in ## in the filename above
#the third argument is a geolocation file that maps a user to a geolocation.  This file was generated by Nathan Denny.
#The output of this program is a list of rows that contain:
#clustername, username, toolname, day, clusterSize, city, state, country

domaingetter = GetDomainForUserDuringPeriod.GetDomainForUserGroupDuringPeriod(databasehost,database,databaseuser,databaseport,databasepassword,databasesessiontable)

def doDummyCluster(clusterName, clusterStart, clusterEnd, conn, clusterWriter):
	sql = "select to_days('" + clusterStart + "'), to_days('" + clusterEnd + "') from " + databasesessiontable + ";"
	cursor = conn.cursor()
	cursor.execute(sql)
	row = cursor.fetchone()
	for i in xrange(row[0], row[1] + 1):
		crow = (clusterName, 'dummy', 'dummy', i, 1,'*','*','*')
		clusterWriter.writerow(crow)
		

"""

reader = csv.reader(open(sys.argv[1], 'r'))

for row in reader:
	geoName = geo.getGeographicNameForUserGroup(row)
	domain, domainPercentages = domaingetter.getDomainForUserGroupDuringPeriod(row, sys.argv[2], sys.argv[3])
	print len(row), geoName, domain, domainPercentages
"""


def doClustersFromFile(fileName, clusterNamePrefix, conn, clusterWriter, clusterNameWriter, geocache, userToGeo):

	clusters = []
	clusterReader = csv.reader(open(fileName))
	print >> sys.stderr, "opening", fileName
	userToCluster = {}
	for row in clusterReader:
		cluster = list(row)
		clusters.append(cluster)
		for user in cluster:
			if user in userToCluster:
				print >> sys.stderr, 'User',user,'is already in a cluster.'
			userToCluster[user] = cluster

	###Get the names for the Year, Season, Start and End from the Prefix (something like "Fall2006")
	clusterYear = clusterNamePrefix.replace('Fall','').replace('Spring','')
	clusterSeason = clusterNamePrefix.replace(clusterYear,'')
	clusterStart = ''
	clusterEnd = ''
	if clusterSeason == 'Fall':
		clusterStart = clusterYear + '-07-01'
		clusterEnd = str(int(clusterYear)+1) + '-01-01'
	elif clusterSeason == 'Spring':
		clusterStart = clusterYear + '-01-01'
		clusterEnd = clusterYear + '-07-01'
	else:
		print "Cannot discern the cluster time period - looking for Fall or Spring in file name"
		sys.exit(1)


	print clusterNamePrefix, clusterStart, clusterEnd
	utdpl = UserToolDayPattern.UserToolDayPatternList(clusterStart, clusterEnd, 'N')

	utdpl.grabAllFromDatabaseUsingToolstartTable(conn)

	rows = utdpl.makeClusterUserToolDayClustersizeList(clusters, geocache, userToGeo)

	currentCluster = 'dummy'
	clusterDomains = {}
	for row in rows:
		row[0] = clusterNamePrefix + "|" + row[0].replace("'",'')
		row.append(clusterStart)
		row.append(clusterEnd)
		domain = None
		domainPercentages = None
		if row[0] not in clusterDomains:
			domain, domainPercentages = domaingetter.getDomainForUserGroupDuringPeriod(userToCluster[row[1]], clusterStart, clusterEnd)
			clusterDomains[row[0]] = (domain, domainPercentages)
			print domain, domainPercentages
		domain, domainPercentages = clusterDomains.get(row[0])
		if domain != '?' and (len(domainPercentages) <= 1 or domainPercentages[0][1] > domainPercentages[1][1]):
			row.append(domain)
		else:
			row.append('UNKNOWN')
		clusterWriter.writerow(row)
		if row[0] != currentCluster:
			clusterNameWriter.write(row[0] + '\n')
			currentCluster = row[0]

	doDummyCluster(clusterNamePrefix + "|dummy", clusterStart, clusterEnd, conn, clusterWriter)

def doMain():
	
	geocache = {}
	userToGeo = {}
	
	conn = MySQLdb.connect(host = databasehost,
							user = databaseuser,
							passwd = databasepassword,
							db = database,
							port = databaseport)
	geoReader = csv.reader(open(sys.argv[3]))
	for row in geoReader:
		user = row[0]
		location = row[1].strip() + "," + row[2].strip() + "," + row[3].strip()
		if location not in geocache:
			geocache[location] = []
		geocache[location].append(user)
		userToGeo[user] = (location, (row[1].strip(), row[2].strip(), row[3].strip()))
	
	
	
	clusterNameWriter = open(sys.argv[1] + '/all_aubiceClusterNamesOnly.csv', 'wb')
	
	clusterWriter = csv.writer(open(sys.argv[1] + '/all_aubiceClusters.csv', 'wb'))
	clusterWriter.writerow(['cluster','user','tool','day','clustersize','city','state','country','clusterStart','clusterEnd', 'institution'])
	
	for root, dirs, files in os.walk(sys.argv[1]):
		print >> sys.stderr, "ENTERING OS LOOP with" , root, dirs, files
		candidateFile = 'orderList' + sys.argv[2] + '.csv'
		print >> sys.stderr, "Seeking Candidate File", candidateFile
		if candidateFile in files:
			clusterName = root.replace(sys.argv[1] + '/', '')
			print "TRUE", clusterName
			if True or clusterName == '2007Spring':
				doClustersFromFile(root + '/' + candidateFile, clusterName, conn, clusterWriter, clusterNameWriter, geocache, userToGeo)

				#break
	
	conn.close()
	


doMain()