import sys
import csv
from multiprocessing import Process, Queue

verbose = False

class ToolUsagePattern:
	def __init__(self, user, daySpanForPenalties):
		self.user = user;
		self.daySpanForPenalties = daySpanForPenalties;
		self.usages = dict()
		self.numberOfDaysWithUsage = 0
	
	def addUsage(self, tool, day):
		toolsOnDay = self.usages.get(day)
		if toolsOnDay == None:
			toolsOnDay = set()
			toolsOnDay.add(tool);
			self.usages[day] = toolsOnDay
			self.numberOfDaysWithUsage += 1
		else:
			toolsOnDay.add(tool);
	
	def size(self):
		return len(self.usages)


class ZDSatisfaction:
	def __init__(self, cost, missingToolName):
		self.cost = cost
		self.missingToolName = missingToolName
	
	def sortKey(self):
		return self.cost
	

class ZDSlideBackSatisfaction (ZDSatisfaction):
	def __init__(self, missingToolName, targetToolsOnDay, targetDay, sourceToolsOnDay, sourceDay, daysWithUsage, daySpanForPenalties):
		ZDSatisfaction.__init__(self, 0.0, missingToolName)
		self.targetToolsOnDay = targetToolsOnDay
		self.sourceToolsOnDay = sourceToolsOnDay
		self.targetDay = targetDay
		self.sourceDay = sourceDay

		superLinearity = float(max(1, 4 - daysWithUsage))
		if daysWithUsage <= 1 and sourceDay - targetDay > 5:
			#superLinearity = float(daySpanForPenalties) / 6.0 NOTE THAT THIS IS INAPPROPRIATE AS THE ROUNDING HAD AN EFFECT ON THE ORIGINAL METHOD
			superLinearity = float(daySpanForPenalties / 6)
		self.cost = superLinearity * float(sourceDay - targetDay)

	def prettyPrint(self, target):
		print >> target, 'SlideBack',self.missingToolName, 'from', self.sourceDay, 'to', self.targetDay, '(', str(self.sourceDay - self.targetDay), 'days', ')', 'at cost', self.cost

	def execute(self):
		self.sourceToolsOnDay.remove(self.missingToolName);
		self.targetToolsOnDay.add(self.missingToolName);
		return self.cost
	

class ZDNeighborSpawnSatisfaction (ZDSatisfaction):
	def __init__(self, missingToolName, targetToolsOnDay, targetDay, sourceDay, daysDifference, daysWithUsage, daySpanForPenalties):
		ZDSatisfaction.__init__(self, 0.0, missingToolName)
		self.targetToolsOnDay = targetToolsOnDay

		#the following two members are only for pretty printing
		self.daysDifference = daysDifference
		self.sourceDay = sourceDay
		self.targetDay = targetDay


		superLinearity = float(max(1, 4 - daysWithUsage))
		if daysWithUsage <= 1 and daysDifference > 5:
			superLinearity = float(daySpanForPenalties / 6)
		self.cost = superLinearity * float(daysDifference)

	def prettyPrint(self, target):
		print >> target, 'NeighborSpawn',self.missingToolName, 'from', self.sourceDay, 'to', self.targetDay, '(', self.daysDifference, 'days', ')', 'at cost', self.cost

	def execute(self):
		self.targetToolsOnDay.add(self.missingToolName);
		return self.cost
	

class ZDImmaculateSpawnSatisfaction (ZDSatisfaction):
	def __init__(self, missingToolName, targetToolsOnDay, targetDay, daysWithUsage, daySpanForPenalties):
		ZDSatisfaction.__init__(self, 0.0, missingToolName)
		self.cost = float(daySpanForPenalties) / float(daysWithUsage)
		self.targetToolsOnDay = targetToolsOnDay
		self.targetDay = targetDay

	def prettyPrint(self, target):
		print >> target, 'ImmaculateSpawn', self.missingToolName, 'on', self.targetDay, 'at cost', self.cost

	def execute(self):
		self.targetToolsOnDay.add(self.missingToolName);
		return self.cost


# a toolUsagePattern is a dict of days->sets of tools on the given day.
def getNumberOfDaysWithUsage(toolUsagePattern):
	rv = 0
	for v in toolUsagePattern.values():
		if len(v) > 0:
			rv += 1
	return rv

class CommonToolUsagePair:
	def __init__(self, toolUsagePattern1, toolUsagePattern2):
		#print >> sys.stderr, toolUsagePattern1.usages, toolUsagePattern2.usages
		self.tup1DaySpanForPenalties = toolUsagePattern1.daySpanForPenalties
		self.tup2DaySpanForPenalties = toolUsagePattern2.daySpanForPenalties
		self.tup1NumberOfDaysWithUsage = toolUsagePattern1.numberOfDaysWithUsage
		self.tup2NumberOfDaysWithUsage = toolUsagePattern2.numberOfDaysWithUsage
		self.tup1 = dict()
		self.tup2 = dict()
		self.toolNameMap = dict()  #make a list of single letter mappings for printing purposes
		curChar = 65    #start with the letter 'A'
		for (k,v) in toolUsagePattern1.usages.items():
			toolsOnDay1 = set()
			for t in v:
				toolsOnDay1.add(t)
				if t not in self.toolNameMap:
					self.toolNameMap[t] = chr(curChar)
					curChar += 1
			self.tup1[k] = toolsOnDay1
			self.tup2[k] = set()
		for (k,v) in toolUsagePattern2.usages.items():
			toolsOnDay2 = self.tup2.get(k)
			if toolsOnDay2 == None:
				toolsOnDay2 = set()
			toolsOnDay1 = self.tup1.get(k)
			if toolsOnDay1 == None:
				toolsOnDay1 = set()
				self.tup1[k] = toolsOnDay1
			for t in v:
				toolsOnDay2.add(t)
				if t not in self.toolNameMap:
					self.toolNameMap[t] = chr(curChar)
					curChar += 1
			self.tup2[k] = toolsOnDay2
		#print >> sys.stderr, self.tup1, self.tup2

	def printAlignedPair(self, target):
		keys = self.tup1.keys()
		minDay = min(keys)
		maxDay = max(keys)
		for tup in [self.tup1, self.tup2]:
			for tool in self.toolNameMap:
				for d in xrange(minDay, maxDay + 1):
					toolsOnDay = tup.get(d)
					if toolsOnDay == None or tool not in toolsOnDay:
						target.write('-')
					else:
						target.write(self.toolNameMap[tool])
				target.write('\n')
			for d in xrange(minDay, maxDay + 1):
				target.write('=')
			target.write('\n')
		joinerString = ''
		for (k,v) in self.toolNameMap.items():
			target.write(joinerString + ' ' + k + '=' + v)
			joinerString = ', '
		print >> target, ''


	def addSatisfaction(self, s, sdict):
		slist = sdict.get(s.missingToolName)
		if slist == None:
			slist = []
			sdict[s.missingToolName] = slist
		slist.append(s)


	def addSpawnSatisfactions(self, missingTools, toolUsagePattern, currentDay, pastDays, futureDays, satisfactions, daySpanForPenalties, numberOfDaysWithUsage):
		#past days is ordered such that the nearest day to current day is first in the list, same with future days
		#for example, if day is 250, past days might be [230,221,200]
		#and future days might be [256, 275, 299]
		addedAnything = False
		timeDifferences = []
		allDays = []
		allDays.extend(pastDays)
		allDays.extend(futureDays) #WE MAY NOT NEED FUTURE DAYS since the penalty for future slidebacks is identical.
		for d in allDays:
			timeDifferences.append((abs(d-currentDay), d))
		timeDifferences.sort()

		daysWithUsage = getNumberOfDaysWithUsage(toolUsagePattern)
		#HERE remove this after making sure I can duplicate results from previous work
		daysWithUsage = numberOfDaysWithUsage
		#HERE end remove if
		for mt in missingTools:
			addedASatisfaction = False
			for td,d in timeDifferences:
				if mt in toolUsagePattern[d]:
					satisfaction = ZDNeighborSpawnSatisfaction(mt, toolUsagePattern[currentDay], currentDay, d, td, daysWithUsage, daySpanForPenalties)
					if verbose == True:
						satisfaction.prettyPrint(sys.stderr)
					self.addSatisfaction(satisfaction, satisfactions)
					addedASatisfaction = True
					break
			if addedASatisfaction == False:
				satisfaction = ZDImmaculateSpawnSatisfaction(mt, toolUsagePattern[currentDay], currentDay, daysWithUsage, daySpanForPenalties)
				if verbose == True:
					satisfaction.prettyPrint(sys.stderr)
				self.addSatisfaction(satisfaction, satisfactions)
			

	def applySatisfactions(self, satisfactions):
		cost = 0.0
		for missingTool in satisfactions:
			missingToolSatisfactions = satisfactions[missingTool]
			missingToolSatisfactions.sort(key=ZDSatisfaction.sortKey)
			s = missingToolSatisfactions[0]
			if verbose == True:
				print >> sys.stderr, "Applying---------------"
				s.prettyPrint(sys.stderr)
			cost += s.execute()
		return cost
			
	def getDifference(self, verbose, forceAllDifferencesLevel):
		keys = self.tup1.keys()
		keys.sort()
		alreadyExaminedKeys = []
		daysRepresented = keys[len(keys) - 1] - keys[0] + 1
		tup1DaysWithUsage = getNumberOfDaysWithUsage(self.tup1)
		tup2DaysWithUsage = getNumberOfDaysWithUsage(self.tup2)
		# HERE get rid of the following two lines after verifying we can product the same results
		tup1DaysWithUsage = self.tup1NumberOfDaysWithUsage
		tup2DaysWithUsage = self.tup2NumberOfDaysWithUsage
		# HERE end of get rid of
		cost = 0.0
		while len(keys) > 0:
			k = keys.pop(0)
			if verbose == True:
				print >> sys.stderr, "doing day",k
			s1 = self.tup1[k]
			s2 = self.tup2[k]
			set1Missing = s2 - s1
			set2Missing = s1 - s2

			set1Satisfactions = dict()
			set2Satisfactions = dict()

			#first look for all "shift back" opportunities
			#because python lists and sorting is "stable" this means that since spawns are added after slidebacks
			#even with sorting, a slideback that has the same value as a neighbor spawn will always be first in
			#the sorted list, and therefore chosen preferentially over the spawns.
			for kj in keys:
				for s1m in set1Missing:
					if s1m in self.tup1[kj]:
						satisfaction = ZDSlideBackSatisfaction(s1m, s1, k, self.tup1[kj], kj, tup1DaysWithUsage, self.tup1DaySpanForPenalties)
						if verbose == True:
							satisfaction.prettyPrint(sys.stderr)
						self.addSatisfaction(satisfaction, set1Satisfactions)
				for s2m in set2Missing:
					if s2m in self.tup2[kj]:
						satisfaction = ZDSlideBackSatisfaction(s2m, s2, k, self.tup2[kj], kj, tup2DaysWithUsage, self.tup2DaySpanForPenalties)
						if verbose == True:
							satisfaction.prettyPrint(sys.stderr)
						self.addSatisfaction(satisfaction, set2Satisfactions)

			#next look for spawing a creation based on the existence of at least one other execution of the same tool
			#HERE the last argument in these two calls can be removed if I can validate that I get the same results as with Java
			#as this should really be calculated dynamically and not be a static value from tehbeginning of the process
			self.addSpawnSatisfactions(set1Missing, self.tup1, k, alreadyExaminedKeys, keys, set1Satisfactions, self.tup1DaySpanForPenalties, tup1DaysWithUsage)
			self.addSpawnSatisfactions(set2Missing, self.tup2, k, alreadyExaminedKeys, keys, set2Satisfactions, self.tup2DaySpanForPenalties, tup2DaysWithUsage)

			cost += self.applySatisfactions(set1Satisfactions)
			cost += self.applySatisfactions(set2Satisfactions)
			if verbose == True:
				self.printAlignedPair(sys.stderr)

			alreadyExaminedKeys.insert(0, k)
			if cost > forceAllDifferencesLevel:
				break
		return cost


def readInput(userXtoolXdayFile):
	rv = dict()
	with open(userXtoolXdayFile, 'rb') as fp:
		r = csv.reader(fp, delimiter = '	')
		line = r.next() #header of date boundaries
		line = r.next() #date boundaries
		earliestDay = int(line[0])
		latestDay = int(line[1])
		line = r.next()  #header row for usages
		for line in r:
			user = line[0]
			tool = line[1]
			day = int(line[2])
			toolUsagePattern = rv.get(user)
			if toolUsagePattern == None:
				toolUsagePattern = ToolUsagePattern(user, latestDay - earliestDay + 1)
				rv[user] = toolUsagePattern
			toolUsagePattern.addUsage(tool, day)
	return rv

def stripThresholdUsages(usages, threshold):
	rv = usages
	removers = []
	for k in usages:
		toolUsagePattern = usages[k]
		if toolUsagePattern.size() <= threshold:
			removers.append(k)
	for i in removers:
		del usages[i]
	return rv



def getDifference(toolUsagePattern1, toolUsagePattern2, verbose, forceAllDifferencesLevel):
	"""
	HERE GET RID of these as we are forcing hte passing of this parameter now
	fadl = 501.0           #threshold beyone which we needn't continue computing differences
	if forceAllDifferencesLevel >= 0.0:
		fadl = forceAllDifferencesLevel
	"""
	fadl = forceAllDifferencesLevel
	pair = CommonToolUsagePair(toolUsagePattern1, toolUsagePattern2)
	if verbose == True:
		pair.printAlignedPair(sys.stderr)
	return pair.getDifference(verbose, fadl)


	
	


def fillQueue(n, usages, workQueue):
	keys = usages.keys()
	entries = 0
	for i in xrange(0, len(keys)):
		toolUsagePattern1 = usages[keys[i]]
		for j in xrange(i+1, len(keys)):
			toolUsagePattern2 = usages[keys[j]]
			workQueue.put((toolUsagePattern1, toolUsagePattern2))
			entries += 1
	for i in xrange(0, n):
		workQueue.put('STOP')

def computeDifference(workQueue, doneQueue, forceAllDifferencesLevel):
	for p in iter(workQueue.get, 'STOP'):
		tup1, tup2 = p
		diff = getDifference(tup1, tup2, verbose, forceAllDifferencesLevel);
		if verbose == True:
			print >> sys.stderr, "Difference", diff
		doneQueue.put((tup1.user, tup2.user, diff))
	doneQueue.put('STOP')


def drainDoneQueue(n, doneQueue, usages, forceAllDifferencesLevel):
	#compute total number of comparisons so we can print percentge done
	total = float(len(usages))
	total = total * (total - 1.0) / 2.0
	currentPercent = 0
	differencesAppended = 0

	differences = dict()
	nStops = 0
	while nStops < n:
		dv = doneQueue.get()
		if type(dv) == str and dv == 'STOP':
			nStops += 1
		else:
			user1, user2, diff = dv
			if diff < forceAllDifferencesLevel:
				u1diffs = differences.get(user1)
				u2diffs = differences.get(user2)
				if u1diffs == None:
					u1diffs = []
					differences[user1] = u1diffs
				u1diffs.append((user2, diff))

				if u2diffs == None:
					u2diffs = []
					differences[user2] = u2diffs
				u2diffs.append((user1, diff))
			differencesAppended += 1

		if float(differencesAppended) / total > float(currentPercent) / 100.0:
			print >> sys.stderr, "Doing", differencesAppended, "out of", total, currentPercent, '%'
			currentPercent += 1
	return differences

def createProcesses(n, workQueue, doneQueue, usages, forceAllDifferencesLevel):
	processes = []
	pQueueFiller = Process(target = fillQueue, args = (n, usages, workQueue))
	pQueueFiller.start()
	processes.append(pQueueFiller)
	for i in xrange(0, n):
		p = Process(target = computeDifference, args = (workQueue, doneQueue, forceAllDifferencesLevel))
		p.start()
		processes.append(p)

	return processes

def joinProcesses(processes, wq, dq):
	#print 'joining', len(processes), wq.empty(), dq.empty()
	for p in processes:
		print >> sys.stderr, 'joining a proces'
		p.join()

def printDifferences(differences, target):
	for key in differences:
		target.write(key)
		others = differences[key]
		for other,diff in others:
			target.write(',')
			target.write(other)
			target.write(',')
			target.write(str(diff))
		target.write('\n')

def filterDifferences(differences, target):
	for key in differences:
		others = differences[key]
		others.sort(key = lambda d : d[1])
		deletePosition = -1
		currentPosition = -1
		previousDiff = None
		for o in others:
			currentPosition += 1
			if previousDiff != None:
				if 1.15 * previousDiff[1] < o[1] and o[1] > 100.0:
					deletePosition = currentPosition
					break
			previousDiff = o
		if deletePosition > -1:
			differences[key] = others[0:deletePosition]


userXtoolXdayFile = sys.argv[1]
semester = sys.argv[2]
clustersAndMatricesFile = '_'.join((semester,"clustersAndMatrices.csv"))
pcount = int(sys.argv[3])

#pcount = 4
forceAllDifferencesLevel = 501.0
usages = readInput(userXtoolXdayFile)
usages = stripThresholdUsages(usages, 0)
workQueue = Queue()
doneQueue = Queue()
processes = createProcesses(pcount, workQueue, doneQueue, usages, forceAllDifferencesLevel)
differences = drainDoneQueue(pcount, doneQueue, usages, forceAllDifferencesLevel)
joinProcesses(processes, workQueue, doneQueue)
filterDifferences(differences, forceAllDifferencesLevel)
with open(clustersAndMatricesFile,'wb') as fp:
	printDifferences(differences, fp)

