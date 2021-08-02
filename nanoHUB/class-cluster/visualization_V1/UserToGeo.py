import os
import csv

class UserToGeo:
	def __init__(self):
		self.theFile = open(os.path.expanduser('~/.nanoHUBGlobalData/usergeoclustered-all50KMClustering.csv'),'rb')
		self.geocache = {}
		self.userToGeo = {}

		geoReader = csv.reader(self.theFile)
		for row in geoReader:
			user = row[0]
			location = row[1].strip() + "," + row[2].strip() + "," + row[3].strip()
			if location not in self.geocache:
				self.geocache[location] = []
			self.geocache[location].append(user)
			self.userToGeo[user] = (location, (row[1].strip(), row[2].strip(), row[3].strip()))
		self.usedNames = {}
		self.theFile.close()

	def getGeoLabelForUserGroup(self, cluster):
		userToGeoCounts = {}
		userCountInThisCluster = 0
		geoTriplets = {}
		for user in cluster:
			userCountInThisCluster += 1
			userGeo = 'UNKNOWN'
			if user in self.userToGeo: userGeo = self.userToGeo[user][0]
			if (userGeo not in userToGeoCounts):
				userToGeoCounts[userGeo] = 0
			userToGeoCounts[userGeo] = userToGeoCounts[userGeo] + 1
			if userGeo not in geoTriplets:
				if user in self.userToGeo: geoTriplets[userGeo] = self.userToGeo[user][1]
				else: geoTriplets[userGeo] = ('UNKNOWN','UNKNOWN','UNKNOWN')
		maximalGeo = 0
		maximalGeoName = ""
		secondMaximalGeoName = ""
		secondMaximalGeo = 0
		for key in userToGeoCounts:
			if userToGeoCounts[key] > maximalGeo:
				secondMaximalGeo = maximalGeo
				secondMaximalGeoName = maximalGeoName
				maximalGeo = userToGeoCounts[key]
				maximalGeoName = key
			elif userToGeoCounts[key] > secondMaximalGeo:
				secondMaximalGeo = userToGeoCounts[key]
				secondMaximalGeoName = key
		rv = "%s" % userCountInThisCluster + " " + "%.1f" % (maximalGeo * 100.0 / userCountInThisCluster) + "% " + maximalGeoName + "  " + "%.1f" % (secondMaximalGeo * 100.0 / userCountInThisCluster) + "% " + secondMaximalGeoName
		return (rv, maximalGeoName, geoTriplets[maximalGeoName])
			
	
	def getGeographicNameForUserGroup(self, cluster):
		junk, junk2, geoTriplet = self.getGeoLabelForUserGroup(cluster)
		city = geoTriplet[0].strip()
		state = geoTriplet[1].strip()
		country = geoTriplet[2].strip()
		rv = city + '|' + state + '|' + country + '|'
		if rv not in self.usedNames:
			self.usedNames[rv] = 0
		self.usedNames[rv] = self.usedNames[rv] + 1
		return rv + '(' + str(self.usedNames[rv]) + ')'
