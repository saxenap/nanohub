    
class ZDSatisfaction:
  def __init__(self, cost, missingToolName):
    self.cost = cost
    self.missingToolName = missingToolName
  
  def sortKey(self):
    return self.cost
  

class ZDSlideBackSatisfaction (ZDSatisfaction):
  def __init__(self, missingToolName, targetToolsOnDay, targetDay, sourceToolsOnDay, sourceDay, daysWithUsage, daySpanForPenalties):
    # s1m:                           missingToolName:     User #1 did not use this tool on day k with user #2
    # s1:                            targetToolsOnDay:    User #1's tools on day k
    # k:                             targetDay:           day #
    # self.tup1[kj]:                 sourceToolsOnDay:    however, User #1 used tool on day kj
    # kj:                            sourceDay:           the day User #1 used the tool (different day with user #2 however)
    # tup1DaysWithUsage:             daysWithUsage:       total number of days the user has used any tool
    # self.tup1DaySpanForPenalities: daySpanForPenalties: total number of days scanned for this user (latestDay - earliestDay + 1)
            
    ZDSatisfaction.__init__(self, 0.0, missingToolName)
    self.targetToolsOnDay = targetToolsOnDay
    self.sourceToolsOnDay = sourceToolsOnDay
    self.targetDay = targetDay
    self.sourceDay = sourceDay

    superLinearity = float(max(1, 4 - daysWithUsage)) # between 1 and 4
    if daysWithUsage <= 1 and sourceDay - targetDay > 5:
      # seems to only apply for users who only used tool for 1 day, and the day different exceeds 5 between user 1 and 2? so rare occurance....
      # high cost for single tool, single day users
 
      #superLinearity = float(daySpanForPenalties) / 6.0 NOTE THAT THIS IS INAPPROPRIATE AS THE ROUNDING HAD AN EFFECT ON THE ORIGINAL METHOD
      superLinearity = float(daySpanForPenalties / 6)

    self.cost = superLinearity * float(sourceDay - targetDay) # higher cost if 1. user #1 and #2 used the tool far apart in days; 2. fewer days of usage (less than 4)
    # cost function: time lag between User #1 and User #2's usage of a certain tool

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

