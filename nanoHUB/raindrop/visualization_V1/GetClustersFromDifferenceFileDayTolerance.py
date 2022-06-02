import csv
import sys

abacuscluster = set(['jcooper2008','jmgaines','ssaeedas','wjbennet88','eschmidgall','theagape','bbommai','jpurao','akiran','banatoski','jyeoh','daryoosh','souvikmatsc','smarjeet','xie0','vedpragyan','ankithatalkar','aabraham','nomissimon','thenu_cc','owensec','hugooj2004','tanoue','avalluru','naidu123','indigoclay','msalah','marabharahap','rjbl','mohabey','mathsislife','kakashow','hankh825','wittawat','3ksnn64','alas82','nextork25','moni3004','whoang88','soocax','dandan','greggroth','amirmirzaei','arnoob','faraz_25','sumittbrl','anisha','mmakowsk','tejaspandit','ganapatigmb','enginakin','dk12','jsaiprakashreddy','dsjin','nbutt','michaeldt','tiagovilela','sneharuby','jmlopezg','sunlin','ivaniske','skalag80','clau_perez','raisavec','amalpradeep','jainfantep','moisoro','carolina_amaya','duskie','alichaparro','rgnanadavid','kanungo','mattg2k4','mahar','neddy','forerca','slaakso','dagutierrezp','carlosparra','gahoi','heisenberg','emieritz','lpatters','einstruments','quantumisme','bgallowa','ug_user','durangotang','cavewyrm','dabernalm','a_ebn','rohanchaukulkar','rcrisp','marcuslay','aallende','rain2air','stahel','jecortesc','jaacevedo','carlospolitte','fazal','nayab','christopherborsa','kevin00002','rock28','sjmoore987'])

#this program takes stuff from a file that has each line as
#user, user, distance, user, distance...
#where the first user is the "center" of a cluster
#and turns it into a file that has each line being a cluster
#user, user, user, user
#
#it also eliminates all subsets of other clusters so that you have
#fewer clusters than in the input file.

if len(sys.argv) != 5:
	print "Usage: ",sys.argv[0]," inputfile outputfile semester diff-tolerance userxtoolxday-file"
	sys.exit(1)
	
userDaySpans = {}
udsReader = csv.reader(open(sys.argv[4]), delimiter='\t')
rowsRead = 0
for row in udsReader:
	rowsRead +=1
	#the first 3 rows are just header material
	if rowsRead > 3:
		user = row[0]
		dayOfActivity = int(row[2])
		if user in userDaySpans:
			minActivity,maxActivity = userDaySpans[user]
			if dayOfActivity > maxActivity: maxActivity=dayOfActivity
			if dayOfActivity < minActivity: minActivity=dayOfActivity
			userDaySpans[user] = (minActivity, maxActivity)
		else: userDaySpans[user] = (dayOfActivity,dayOfActivity)
		
	
clusterReader = csv.reader(open(sys.argv[1],'rb'))

tolerance = float(sys.argv[3])
print sys.argv[3], tolerance
clusterCenter = None
clusteredUser = None

clusters = {}

#Read the clusters in.  Stepping over the elements of a row, this loop
#finds the "clusterCenter" (the initial user) and then finds a user
#followed by a distance, until the line is fully read.
for row in clusterReader:
	clusterCenter = None
	clusterCandidates = set()
	clusterDaySpan = (0,0)
	clusterCenter = row[0]
	if len(row) > 1 and (True or clusterCenter in abacuscluster):
		clusters[clusterCenter] = set()
		clusters[clusterCenter].add(clusterCenter)
		clusterDaySpan = userDaySpans[clusterCenter]
		for i in xrange(1, len(row), 2):
			clusteredUser = row[i]
			clusteredUserDistance = row[i + 1]
			if float(clusteredUserDistance) <= tolerance:
				clusterCandidates.add(clusteredUser)
		for candidate in clusterCandidates:
			if clusterDaySpan[0] == clusterDaySpan[1] and (True or candidate in abacuscluster):
				clusterDay = clusterDaySpan[0]
				candidateDaySpan = userDaySpans[candidate]
				if candidateDaySpan[0] <= clusterDay and candidateDaySpan[1] >= clusterDay:
					clusters[clusterCenter].add(candidate)
				elif abs(candidateDaySpan[0] - clusterDay) == 1 or abs(candidateDaySpan[1] - clusterDay) == 1:
					clusters[clusterCenter].add(candidate)
			elif True or candidate in abacuscluster:
				clusters[clusterCenter].add(candidate)
			
		"""
		candidatesToRemove = set()
		for candidate in clusterCandidates:
			candmin,candmax = userDaySpans[candidate]
			clusmin,clusmax = clusterDaySpan
			if candmin >= clusmin and candmax <= clusmax and float(candmax - candmin + 1) > 0.7 * float(clusmax - clusmin + 1):
				print clusterCenter," Adding ",candidate, candmax, candmin, clusmax, clusmin, clusters[clusterCenter]
				clusters[clusterCenter].add(candidate)
				candidatesToRemove.add(candidate)
			#clusters[clusterCenter] = set()
			#clusters[clusterCenter].add(rowElement)
		for remover in candidatesToRemove:
			clusterCandidates.remove(remover)
		
		while len(clusterCandidates) > 0:
			minExpansionDays = 100000
			bestCandidate = None
			clusmin,clusmax = clusterDaySpan
			for candidate in clusterCandidates:
				candmin,candmax = userDaySpans[candidate]
				expansionDays = max(0, clusmin - candmin) + max(0, candmax - clusmax)
				if expansionDays < minExpansionDays: 
					bestCandidate = candidate
					minExpansionDays = expansionDays
			if minExpansionDays > 0 and minExpansionDays <= 1:
				clusterCandidates.remove(bestCandidate)
				candmin,candmax = userDaySpans[bestCandidate]
				print clusterCenter," adding ", bestCandidate, candmax, candmin, clusmax, clusmin, " size=",len(clusters[clusterCenter])," c= ", clusters[clusterCenter]
				clusters[clusterCenter].add(bestCandidate)
			else: clusterCandidates.remove(bestCandidate)
		while len(clusterCandidates) > 0:
			bestOverlapFraction = -0.01
			bestCandidate = None
			clusmin,clusmax = clusterDaySpan
			for candidate in clusterCandidates:
				candmin,candmax = userDaySpans[candidate]
				totalSpan = float(max(candmax, clusmax) - min(candmin, clusmin)) + 1.0
				overlap = float(max(0, min(candmax, clusmax) - max(candmin, clusmin))) + 1.0
				overlapFraction = overlap / totalSpan
				if overlapFraction > bestOverlapFraction: 
					bestCandidate = candidate
					bestOverlapFraction = overlapFraction
			if bestOverlapFraction > 0.5:
				clusterCandidates.remove(bestCandidate)
				candmin,candmax = userDaySpans[bestCandidate]
				#print clusterCenter," adding ", bestCandidate, candmax, candmin, clusmax, clusmin, " size=",len(clusters[clusterCenter])," c= ", clusters[clusterCenter]
				clusters[clusterCenter].add(bestCandidate)
			else: clusterCandidates.remove(bestCandidate)
		"""
		if len(clusters[clusterCenter]) == 1:
			del clusters[clusterCenter]


eliminatedClusters = 0

removeClusters = set()

clusterList = clusters.items()

clusterSizeMinimum = 4

#Generate a set of clusters to remove based on one being a superset of another,
#or also if a cluster size does not meat the minimum requirement.
for i in xrange(len(clusterList)):
	if i % 500 == 0: print i
	if len(clusterList[i][1]) <= clusterSizeMinimum:
		removeClusters.add(clusterList[i][0])
	elif clusterList[i][0] not in removeClusters:
		for j in xrange(i+1, len(clusterList)):
			if clusterList[j][0] not in removeClusters:
				if len(clusterList[j][1]) <= clusterSizeMinimum:
					removeClusters.add(clusterList[j][0])
				elif clusterList[i][1] == clusterList[j][1]:
					removeClusters.add(clusterList[j][0])
				elif clusterList[i][1] >= clusterList[j][1]:
					removeClusters.add(clusterList[j][0])
				elif clusterList[i][1] <= clusterList[j][1]:
					removeClusters.add(clusterList[i][0])
					break #if you are going to remove the cluster in the outer loop, then might as well stop and not do any more
					#print "removing cluster ", clusterList[j][0], " because ", clusterList[i][1], " >= ", clusterList[j][1]

#Now actually remove the clusters - couldn't do this before
#because you don't want to change a set while iterating over it.
print "Initially ",len(clusters)," clusters"
for i in removeClusters:
	del clusters[i]

print "Finally ",len(clusters)," clusters"

clusterWriter = csv.writer(open('_'.join((sys.argv[2],'extractedClusters',"%d" % (int(tolerance)),'DT.csv')), 'w'));

for key in clusters:
	clusterWriter.writerow(list(clusters[key]))
	
