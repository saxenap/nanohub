#make a bash script file which will run the clustering work for all semesters in the list

rootdir = "CLUSTERSBYSEMESTER_TOOLSTART"
hostname = "127.0.0.1"
username = "hub_read"
password = "XXXXXX"
port = "4406"
databasename = "nanohub_metrics"

geoFileName = "data/geolocation_nathan.csv"
semesters = [
	('Fall2000', '2000-07-01 00:00:00', '2001-01-01 00:00:00'),
	('Fall2001', '2001-07-01 00:00:00', '2002-01-01 00:00:00'),
	('Fall2002', '2002-07-01 00:00:00', '2003-01-01 00:00:00'),
	('Fall2003', '2003-07-01 00:00:00', '2004-01-01 00:00:00'),
	('Fall2004', '2004-07-01 00:00:00', '2005-01-01 00:00:00'),
	('Fall2005', '2005-07-01 00:00:00', '2006-01-01 00:00:00'),
	('Fall2006', '2006-07-01 00:00:00', '2007-01-01 00:00:00'),
	('Fall2007', '2007-07-01 00:00:00', '2008-01-01 00:00:00'),
	('Fall2008', '2008-07-01 00:00:00', '2009-01-01 00:00:00'),
	('Fall2009', '2009-07-01 00:00:00', '2010-01-01 00:00:00'),
	('Fall2010', '2010-07-01 00:00:00', '2011-01-01 00:00:00'),
	('Fall2011', '2011-07-01 00:00:00', '2012-01-01 00:00:00'),
	('Fall2012', '2012-07-01 00:00:00', '2013-01-01 00:00:00'),
	('Fall2013', '2013-07-01 00:00:00', '2014-01-01 00:00:00'),
	('Spring2001', '2001-01-01 00:00:00', '2001-07-01 00:00:00'),
	('Spring2002', '2002-01-01 00:00:00', '2002-07-01 00:00:00'),
	('Spring2003', '2003-01-01 00:00:00', '2003-07-01 00:00:00'),
	('Spring2004', '2004-01-01 00:00:00', '2004-07-01 00:00:00'),
	('Spring2005', '2005-01-01 00:00:00', '2005-07-01 00:00:00'),
	('Spring2006', '2006-01-01 00:00:00', '2006-07-01 00:00:00'),
	('Spring2007', '2007-01-01 00:00:00', '2007-07-01 00:00:00'),
	('Spring2008', '2008-01-01 00:00:00', '2008-07-01 00:00:00'),
	('Spring2009', '2009-01-01 00:00:00', '2009-07-01 00:00:00'),
	('Spring2010', '2010-01-01 00:00:00', '2010-07-01 00:00:00'),
	('Spring2011', '2011-01-01 00:00:00', '2011-07-01 00:00:00'),
	('Spring2012', '2012-01-01 00:00:00', '2012-07-01 00:00:00'),
	('Spring2013', '2013-01-01 00:00:00', '2013-07-01 00:00:00')
]



comd = "rm -rf " + rootdir
print comd
comd = "mkdir " + rootdir
print comd

for name, start, end in semesters:
	startdate = start.replace(" 00:00:00","")
	enddate = end.replace(" 00:00:00","")
	comd = "mkdir " + rootdir + "/" + name
	print comd
	comd = "mysql -h " + hostname + " -P " + port + " -u " + username + " -p" + password + " --batch --execute \"select to_days('" + start + "'), to_days('" + end + "');\" " + databasename + " > " + rootdir + "/" + name + "/userXtoolXday.csv"
	print comd

	comd = "mysql -h " + hostname + " -P " + port + " -u " + username + " -p" + password + " --batch --execute \"select distinct user, jtv.toolname, to_days(datetime) as tds from toolstart as sl, metrics_tool_version as jtv where jtv.instance = sl.tool and protocol in (5,6,7) and datetime > '" + start + "' and datetime < '" + end + "' and user <> '' order by user, tds;\" " + databasename + " >> " + rootdir + "/" + name + "/userXtoolXday.csv"
	print comd

	comd = "java -Xmx2048m -Xms2048m -classpath classes ZentnerDifference 0 < " + rootdir + "/" + name + "/userXtoolXday.csv > " + rootdir + "/" + name + "/clustersAndMatrices.csv"
	print comd

	comd = "python GetClustersFromDifferenceFileDayTolerance.py " + rootdir + "/" + name + "/clustersAndMatrices.csv " + rootdir + "/" + name + "/extractedClusters57DT.csv 57 " + rootdir + "/" + name + "/userXtoolXday.csv"
	print comd

	comd = "python TestClusterSimilaritiesExp.py -c " + rootdir + "/" + name + "/extractedClusters57DT.csv -g " + geoFileName + " -s " + startdate + " -e " + enddate + " -f " + rootdir + "/" + name + "/userXtoolXday.csv" + " > " + rootdir + "/" + name + "/orderList57DT.csv"
	print comd

	comd = "python MakeFullRaindrop.py -c " + rootdir + "/" + name + "/orderList57DT.csv -g " + geoFileName + " -s " + startdate + " -e " + enddate + " -f " + rootdir + "/" + name + "/userXtoolXday.csv" + " -k Y > " + rootdir + "/" + name + "/orderList57DTsequence.txt"
	print comd

