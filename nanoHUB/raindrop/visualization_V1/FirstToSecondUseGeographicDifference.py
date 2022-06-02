import csv
import sys
from operator import itemgetter

def getLocationFromCluster(cluster):
	l = cluster.split('|')
	return l[1]+l[2]+l[3]

def updateToolUseEvolutions(row, tue):
	cluster = row[0]
	location = getLocationFromCluster(cluster)
	tool = row[2]
	day = int(row[3])
	city = row[5]
	state = row[6]
	country = row[7]
	institution = ''
	if len(row) == 11:
		institution = row[10]
	signature = ''
	if len(institution) > 0 and institution != 'UNKNOWN' and not institution.endswith('.net') and not institution.endswith('.com'):
		signature = institution
	elif not location.startswith('UNKNOWN'):
		signature = location
	if len(signature) > 0:
		siglist = tue.get(tool)
		if siglist == None:
			siglist = {}
			tue[tool] = siglist
		sigday = siglist.get(signature)
		if sigday == None or sigday > day:
			siglist[signature] = day
	
		

clusterReader = csv.reader(open(sys.argv[1],'r'))

row = clusterReader.next()

expectedHeader = ['cluster','user','tool','day','clustersize','city','state','country','clusterStart','clusterEnd','institution']

if row != expectedHeader:
	print >> sys.stderr, 'Header row is not as expected!'
	sys.exit(1)


toolUseEvolutions = {}
for row in clusterReader:
	if row[1] != 'dummy':
		updateToolUseEvolutions(row, toolUseEvolutions)

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
