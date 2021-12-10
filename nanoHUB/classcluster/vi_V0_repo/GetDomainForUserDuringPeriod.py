import MySQLdb
import GetDomainForIPAddress
import sys

class GetDomainForUserDuringPeriod:
	def __init__(self, dbhost, thedb, dbuser, dbport, password, thetable):
		self.connection = MySQLdb.connect(host = dbhost, user = dbuser, passwd = password, db = thedb, port = dbport)
		self.ipToDomainTranslator = GetDomainForIPAddress.GetDomainForIPAddress()

		self.table = thetable
	
	
	def getDomainForUserDuringPeriod(self, user, start, end):
		cursor = self.connection.cursor()
		sql = ""
		if self.table == 'sessionlog':
			sql = "select remoteip from sessionlog where username = %s and start > %s and start < %s;"
		elif self.table == 'toolstart':
			sql = "select ip from toolstart where user = %s and datetime > %s and datetime < %s;"
		cursor.execute(sql, (user, start, end))
		row = cursor.fetchone()
		domainCounts = {}
		lookedUpIPs = {}
		nSessions = 0
		while row != None:
			#print row
			nSessions += 1
			domain = lookedUpIPs.get(row[0])
			if domain == None:
				domain = self.ipToDomainTranslator.getDomainForIP(row[0])
				lookedUpIPs[row[0]] = domain
			count = domainCounts.get(domain)
			if count == None:
				domainCounts[domain] = 1
			else:
				domainCounts[domain] = count + 1
			row = cursor.fetchone()
		maxDomainCount = 0
		maxDomain = None
		for domain in domainCounts:
			curCount = domainCounts[domain]
			if curCount > maxDomainCount:
				maxDomainCount = curCount
				maxDomain = domain
		#print domainCounts
		return maxDomain


class GetDomainForUserGroupDuringPeriod:
	def __init__(self, dbhost, thedb, dbuser, dbport, password, thetable):
		self.domainForUserGetter = GetDomainForUserDuringPeriod(dbhost, thedb, dbuser, dbport, password, thetable)
	
	
	def getDomainForUserGroupDuringPeriod(self, users, start, end):
		domainCounts = {}
		for user in users:
			udomain = self.domainForUserGetter.getDomainForUserDuringPeriod(user, start, end)
			count = domainCounts.get(udomain)
			if count == None:
				domainCounts[udomain] = 1
			else:
				domainCounts[udomain] = count + 1
		maxDomainCount = 0
		maxDomain = None
		domainPercentages = []
		for domain in domainCounts:
			curCount = domainCounts[domain]
			domainPercentages.append((domain, float(curCount) / float(len(users))))
			if curCount > maxDomainCount:
				maxDomainCount = curCount
				maxDomain = domain
		#print domainCounts
		domainPercentages.sort(key = lambda x: -x[1])
		return maxDomain, domainPercentages
	

#dg = GetDomainForUserGroupDuringPeriod('localhost','narwhal_22022011','root','')
#thedom = dg.getDomainForUserGroupDuringPeriod(sys.argv[1].split(','), sys.argv[2], sys.argv[3])
#print thedom

