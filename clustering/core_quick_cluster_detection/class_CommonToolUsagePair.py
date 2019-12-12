
from .class_Satisfaction import ZDSatisfaction, ZDSlideBackSatisfaction, ZDNeighborSpawnSatisfaction, ZDImmaculateSpawnSatisfaction

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
    self.tup1 = dict() # set of tools used by the user #1 on that day
    self.tup2 = dict() # set of tools used by the user #2 on that day
    self.toolNameMap = dict()  #make a list of single letter mappings for printing purposes
    curChar = 65    #start with the letter 'A'
    
    for (k,v) in toolUsagePattern1.usages.items():
      # (k,v) = (day #, set of tool names on that day)
      toolsOnDay1 = set()
      for t in v:
        toolsOnDay1.add(t)
        if t not in self.toolNameMap:
          self.toolNameMap[t] = chr(curChar)
          curChar += 1
      self.tup1[k] = toolsOnDay1 # set of tool names on that day
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

          self.addSatisfaction(satisfaction, satisfactions)
          addedASatisfaction = True
          break
            
      if addedASatisfaction == False:
        satisfaction = ZDImmaculateSpawnSatisfaction(mt, toolUsagePattern[currentDay], currentDay, daysWithUsage, daySpanForPenalties)
        self.addSatisfaction(satisfaction, satisfactions)
      

  def applySatisfactions(self, satisfactions):
    cost = 0.0
    for missingTool in satisfactions:
      missingToolSatisfactions = satisfactions[missingTool]
      missingToolSatisfactions.sort(key=ZDSatisfaction.sortKey)
      s = missingToolSatisfactions[0] # choose the lowest cost

      #for this_index, this_entry in enumerate(missingToolSatisfactions):
        #if this_index == 0:
        #  pprint('(Selected) COSTS:'+str(this_entry.cost)+'; ACTION: '+str(type(this_entry)))            
        #else:
        #  pprint('           COSTS:'+str(this_entry.cost)+'; ACTION: '+str(type(this_entry)))            
      
      cost += s.execute()

    return cost
      
  def getDifference(self, verbose, forceAllDifferencesLevel):
    keys = self.tup1.keys()
    #keys.sort()
    keys = sorted(keys)
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
      # each of the day (key) from tup1. The order of which does not really matter
      k = keys.pop(0)
      #pprint('-------------------------------------------')
      #pprint('Day #'+str(k))
      s1 = self.tup1[k]
      s2 = self.tup2[k]

      # if s1 = ['a','b','c','z'], s2 = ['b','c','w']
      set1Missing = s2 - s1 # ['w']
      set2Missing = s1 - s2 # ['a']

      set1Satisfactions = dict()
      set2Satisfactions = dict()

      #first look for all "shift back" opportunities
      #because python lists and sorting is "stable" this means that since spawns are added after slidebacks
      #even with sorting, a slideback that has the same value as a neighbor spawn will always be first in
      #the sorted list, and therefore chosen preferentially over the spawns.
      for kj in keys:
        # for each day (in the remaining days)
        for s1m in set1Missing:
          if s1m in self.tup1[kj]:
            satisfaction = ZDSlideBackSatisfaction(s1m, s1, k, self.tup1[kj], kj, tup1DaysWithUsage, self.tup1DaySpanForPenalties)
            # s1m:                           User #1 did not use this tool on day k with user #2
            # s1:                            User #1's tools on day k
            # k:                             day #
            # self.tup1[kj]:                 however, User #1 used tool on day kj
            # kj:                            the day User #1 used the tool (different day with user #2 however)
            # tup1DaysWithUsage:             total number of days the user has used any tool
            # self.tup1DaySpanForPenalities: total number of days scanned for this user (latestDay - earliestDay + 1)

            self.addSatisfaction(satisfaction, set1Satisfactions)

        for s2m in set2Missing:
          if s2m in self.tup2[kj]:
            satisfaction = ZDSlideBackSatisfaction(s2m, s2, k, self.tup2[kj], kj, tup2DaysWithUsage, self.tup2DaySpanForPenalties)

            self.addSatisfaction(satisfaction, set2Satisfactions)

      #next look for spawing a creation based on the existence of at least one other execution of the same tool
      #HERE the last argument in these two calls can be removed if I can validate that I get the same results as with Java
      #as this should really be calculated dynamically and not be a static value from tehbeginning of the process

      self.addSpawnSatisfactions(set1Missing, self.tup1, k, alreadyExaminedKeys, keys, set1Satisfactions, self.tup1DaySpanForPenalties, tup1DaysWithUsage)
      self.addSpawnSatisfactions(set2Missing, self.tup2, k, alreadyExaminedKeys, keys, set2Satisfactions, self.tup2DaySpanForPenalties, tup2DaysWithUsage)

      cost += self.applySatisfactions(set1Satisfactions)
      cost += self.applySatisfactions(set2Satisfactions)
      
      #pprint('>> tup1: '+pformat(self.tup1))
      #pprint('>> tup2: '+pformat(self.tup2))
      
      alreadyExaminedKeys.insert(0, k)
      if cost > forceAllDifferencesLevel:
        break
    return cost
    
    
    
    
class ToolUsagePattern:
  def __init__(self, user, daySpanForPenalties):
    self.user = user;
    self.daySpanForPenalties = daySpanForPenalties;
    self.usages = dict() # usages[day #] = set{'pntoy', 'abc'}
    self.numberOfDaysWithUsage = 0 # total user activate days
  
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
