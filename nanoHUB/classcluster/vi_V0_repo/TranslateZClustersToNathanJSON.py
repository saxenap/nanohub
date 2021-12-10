import sys
import csv
import datalib
import json

if len(sys.argv) != 4:
	print "Usage: ",sys.argv[0]," clustersAndMatricesFile.csv tolerance minimumCorrelationValue"

tolerance = float(sys.argv[2])
minimumCorrelationValue = float(sys.argv[3])
clusterReader = csv.reader(open(sys.argv[1]))	

rowList = []
colList = []
intdict = {}

rowsRead = 0
for row in clusterReader:
	rowList.append(row[0])
	colList.append(row[0])
	intdict[row[0]] = rowsRead
	rowsRead+=1

del clusterReader

clusterReader = csv.reader(open(sys.argv[1]))	

differences = []

clusterReader = csv.reader(open(sys.argv[1]))

rowsRead = 0;
for row in clusterReader:
	rowsRead += 1
	#if rowsRead == 2: break
	anchorUser = None
	nextUser = None
	for user in row:
		if anchorUser == None:
			anchorUser = user
			differences.append([intdict[anchorUser], intdict[anchorUser], 1.0])
		elif nextUser == None:
			nextUser = user
		else:
			distance = float(user)
			if distance <= tolerance:
				normalizedDistance =  1.0 - (1.0 - minimumCorrelationValue) * distance / tolerance
				differences.append([intdict[anchorUser], intdict[nextUser], normalizedDistance])
			nextUser = None
			
print "Saving JSON"
json.dump([rowList, colList, differences], open('zd.json','wb'), sort_keys=True, indent=4)