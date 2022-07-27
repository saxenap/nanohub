import sys
import csv
import UserToGeo
import GetDomainForUserDuringPeriod

geo = UserToGeo.UserToGeo()
domaingetter = GetDomainForUserDuringPeriod.GetDomainForUserGroupDuringPeriod('localhost','narwhal_22022011','root','')

reader = csv.reader(open(sys.argv[1], 'r'))

for row in reader:
	geoName = geo.getGeographicNameForUserGroup(row)
	domain, domainPercentages = domaingetter.getDomainForUserGroupDuringPeriod(row, sys.argv[2], sys.argv[3])
	print len(row), geoName, domain, domainPercentages
