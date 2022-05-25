import sys
import csv
from PIL import Image
from PIL import ImageDraw
import ContrastingColors
import PlopWord

wPixelsPerUse = 2
hPixelsPerUse = 3

wLPixelBufferPerEvent = 1
wRPixelBufferPerEvent = 0
hTPixelBufferPerEvent = 1
hBPixelBufferPerEvent = 0


# wPixelsPerUse = 3
# hPixelsPerUse = 3

# wPixelBufferPerEvent = 0
# hPixelBufferPerEvent = 0

class UserToolDayPattern:
    def __init__(self, user):
        self.patterns = {}
        self.user = user
        self._minDay = -1
        self._maxDay = -1

    def getNumberOfActiveDays(self):
        return len(self.patterns)

    def addUsage(self, tool, day):
        if day not in self.patterns:
            self.patterns[day] = [];
        self.patterns[day].append(tool)
        self._maxDay = max(self._maxDay, day)
        if self._minDay == -1:
            self._minDay = day
        self._minDay = min(self._minDay, day)

    def setToStart(self, newStart):
        if newStart != self._minDay:
            difference = self._minDay - newStart
            newPatterns = {}
            for day in self.patterns:
                newPatterns[day - difference] = self.patterns[day]
            self.patterns = newPatterns
            self._minDay = newStart
            self._maxDay = self._maxDay - difference

    def getEarliestDayRepresented(self):
        return self._minDay

    def grabFromDatabase(self, connection):

        sql = """
			select distinct lower(user), jtv.toolname, to_days(start) as tds from nanohub_metrics.sessionlog_metrics as sl, nanohub.jos_tool_version as jtv
				where
			(jtv.instance = sl.appname or jtv.toolname = sl.appname) and date(start) between %s and %s and user <> ''
			order by user, tds;
			"""
        cursor = connection.cursor()
        cursor.execute(sql, self.user)
        row = cursor.fetchone()
        while row != None:
            print(row)
            self.addUsage(row[1], row[2])
            row = cursor.fetchone()

        sql = """
			select jxp.username, jca.author, jca.author_uid, to_days(jc.date_submit), to_days(jc.date_accept), to_days(jc.date_publish)
			from nanohub_22022011.jos_citations as jc, nanohub_22022011.jos_citations_authors as jca, nanohub_22022011.jos_xprofiles as jxp 
			where jxp.uidNumber = jca.author_uid and jxp.username = %s and jca.cid = jc.id and jca.author_uid <> 0 and published = 1;
			"""
        cursor.execute(sql, self.user)
        row = cursor.fetchone()
        while row != None:
            print(row)
            days = row[3]
            event = 'PUBLICATION SUBMITTED'
            if (days == None):
                days = row[4]
                event = 'PUBLICATION ACCEPTED'
            if (days == None):
                days = row[5]
                event = 'PUBLICATION PUBLISHED'
            if (days != None):
                self.addUsage(event, days)
            row = cursor.fetchone()

        cursor.close()


class UserToolDayPatternList:
    # start date and enddate below are in YYYY-MM-DD string format
    # this init is used when you will be reading the data from a db
    def __init__(self, startdate, enddate, showCohort):
        # startdate and enddate are only important when using a db.
        # If reading from a file, they are unimportant.
        self._startdate = startdate
        self._enddate = enddate
        self._showCohort = showCohort
        self._minDay = -1
        self._maxDay = -1
        self._userPatterns = {}

    # this init will be used if you are reading the data from a file
    # the file is tab separated.  Line 1 is two "to days" statements.
    # Line 2 is the start and end date of the file
    # line 3 is the "username toolname tds" header
    # the rest of the lines are data

    # def __init__(self, showCohort):
    # 	#startdate and enddate are only important when using a db.
    # 	#If reading from a file, they are unimportant.
    # 	self._startdate = '2008-07-01'
    # 	self._enddate = '2008-12-31'
    # 	self._showCohort = showCohort
    # 	self._minDay = -1
    # 	self._maxDay = -1
    # 	self._userPatterns = {}

    def getUserPattern(self, username):
        return self._userPatterns[username.lower()]

    def getSize(self):
        return len(self._userPatterns)

    def add(self, userPattern):
        if len(userPattern.patterns) > 0:
            self._maxDay = max(self._maxDay, userPattern._maxDay)
            if self._minDay == -1:
                self._minDay = userPattern._minDay
            self._minDay = min(self._minDay, userPattern._minDay)
            self._userPatterns[userPattern.user] = userPattern

    def putAllToSameStartDate(self):
        self._maxDay = -1
        for key in self._userPatterns:
            up = self._userPatterns[key]
            up.setToStart(self._minDay)
            self._maxDay = max(self._maxDay, up._maxDay)

    def grabAllFromFile(self, fileName):
        reader = csv.reader(open(fileName, 'r'), delimiter='	')
        row = next(reader)
        row = next(reader)
        row = next(reader)
        currentUser = "nobodysldkjlfdkjgerrjflk"
        currentUserPattern = None
        for row in reader:
            if row[0] != currentUser:
                if currentUserPattern != None and currentUserPattern.getNumberOfActiveDays() >= 1:
                    self.add(currentUserPattern)
                currentUserPattern = UserToolDayPattern(row[0])
                currentUser = row[0]
            currentUserPattern.addUsage(row[1], int(row[2]))
        # add the last user pattern
        if currentUserPattern != None and currentUserPattern.getNumberOfActiveDays() >= 1:
            self.add(currentUserPattern)

    def grabAllFromDatabase(self, connection):
        sql = """
			select distinct lower(user), jtv.toolname, to_days(start) as tds from nanohub_metrics.sessionlog_metrics as sl, nanohub.jos_tool_version as jtv
				where
			(jtv.instance = sl.appname or jtv.toolname = sl.appname) and date(start) between %s and %s and user <> ''
			order by user, tds;
			"""
        cursor = connection.cursor()
        cursor.execute(sql, (self._startdate, self._enddate))
        row = cursor.fetchone()
        currentUser = "nobodysldkjlfdkjgerrjflk"
        currentUserPattern = None
        while row != None:
            if row[0] != currentUser:
                if currentUserPattern != None and currentUserPattern.getNumberOfActiveDays() >= 1:
                    self.add(currentUserPattern)
                currentUserPattern = UserToolDayPattern(row[0])
                currentUser = row[0]
            currentUserPattern.addUsage(row[1], row[2])
            row = cursor.fetchone()
        # add the last user pattern
        if currentUserPattern != None and currentUserPattern.getNumberOfActiveDays() >= 1:
            self.add(currentUserPattern)
        cursor.close()

    def grabAllFromDatabaseUsingToolstartTable(self, connection):
        sql = """
			select distinct user, jtv.toolname, to_days(start) as tds from nanohub_metrics.sessionlog_metrics as sl, nanohub.jos_tool_version as jtv
				where
			jtv.instance = sl.appname and date(start) between %s and %s and user <> ''
			order by user, tds;
			"""
        cursor = connection.cursor()
        cursor.execute(sql, (self._startdate, self._enddate))
        row = cursor.fetchone()
        currentUser = "nobodysldkjlfdkjgerrjflk"
        currentUserPattern = None
        while row != None:
            if row[0] != currentUser:
                if currentUserPattern != None and currentUserPattern.getNumberOfActiveDays() >= 1:
                    self.add(currentUserPattern)
                currentUserPattern = UserToolDayPattern(row[0])
                currentUser = row[0]
            currentUserPattern.addUsage(row[1], row[2])
            row = cursor.fetchone()
        # add the last user pattern
        if currentUserPattern != None and currentUserPattern.getNumberOfActiveDays() >= 1:
            self.add(currentUserPattern)
        cursor.close()

    def incorporatePlopWord(self, word, separatorUser, rv):
        locArray = PlopWord.getPlopLetterArray(word)
        if len(locArray) > 0:
            for i in range(0, len(locArray[0])):
                dummy = UserToolDayPattern(separatorUser)
                currentPixelPosition = self._minDay
                for letter in locArray:
                    for raster in letter[i]:
                        if (raster != ' '): dummy.addUsage(separatorUser, currentPixelPosition)
                        currentPixelPosition += 1
                rv.append((separatorUser, dummy))

    def getGeoLabelForCluster(self, cluster, userToGeo):
        userToGeoCounts = {}
        userCountInThisCluster = 0
        geoTriplets = {}
        for user in cluster:
            userCountInThisCluster += 1
            userGeo = 'UNKNOWN'
            if user in userToGeo: userGeo = userToGeo[user][0]
            if (userGeo not in userToGeoCounts):
                userToGeoCounts[userGeo] = 0
            userToGeoCounts[userGeo] = userToGeoCounts[userGeo] + 1
            if userGeo not in geoTriplets:
                if user in userToGeo:
                    geoTriplets[userGeo] = userToGeo[user][1]
                else:
                    geoTriplets[userGeo] = ('UNKNOWN', 'UNKNOWN', 'UNKNOWN')
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
        rv = "%s" % userCountInThisCluster + " " + "%.1f" % (
                maximalGeo * 100.0 / userCountInThisCluster) + "% " + maximalGeoName + "  " + "%.1f" % (
                     secondMaximalGeo * 100.0 / userCountInThisCluster) + "% " + secondMaximalGeoName
        return (rv, maximalGeoName, geoTriplets[maximalGeoName])

    def getDummyPattern(self):
        dummy = UserToolDayPattern("dummy")
        for i in range(self._minDay, self._maxDay + 1):
            dummy.addUsage("dummy", i)
        return dummy

    def getOrderedUserList(self, clusters, geographicClusters, userToGeo, plopWords):

        rv = []

        for cluster in clusters:
            clusterGeoLabel, primaryGeography, geoTriplet = self.getGeoLabelForCluster(cluster, userToGeo)
            if geoTriplet[0] == "WEST LAFAYETTE" or geoTriplet[0] == "URBANA" or geoTriplet[0] == "EVANSTON" or True:
                rv.append(("RESET", self.getDummyPattern()))
                if plopWords:
                    self.incorporatePlopWord(clusterGeoLabel, "RESET", rv)
                print(clusterGeoLabel)
                for user in cluster:
                    if user in self._userPatterns:
                        rv.append((user, self._userPatterns[user]))
                        print(user)
        if self._showCohort:
            for cluster in geographicClusters:
                # clusterGeoLabel, primaryGeography, geoTriplet = self.getGeoLabelForCluster(cluster, userToGeo)
                if cluster[0].startswith("WEST LAFAYETTE") or cluster[0].startswith("URBANA") or cluster[0].startswith(
                        "EVANSTON") or True:
                    rv.append(("GEO", self.getDummyPattern()))
                    if plopWords: self.incorporatePlopWord(cluster[0], "GEO", rv)
                    print(cluster[0])
                    cluster[1].sort(key=lambda usr: self._userPatterns[
                        usr].getEarliestDayRepresented() if usr in self._userPatterns else 0)
                    for user in cluster[1]:
                        if user in self._userPatterns:
                            rv.append((user, self._userPatterns[user]))
                            print(user)
        return rv

    def removeExtraneousUsersFromGeoInfo(self, clusters, geographicClusters, geocache, userToGeo):
        # Get the users for which we have usage patterns
        representedUsers = set(self._userPatterns.keys())
        # A non represented user is one that is in our geography table but for which we do not have a usage pattern
        # we want to remove these so that the number of users in a given geography is accurate when it is a denominator
        nonRepresentedUsers = set(userToGeo.keys()) - representedUsers
        # We want to remove the clustered users as well, since they are not part of the remianing "cruft" that must
        # be sorted by geographic region
        for cluster in clusters:
            nonRepresentedUsers.update(cluster)
        for user in nonRepresentedUsers:
            if user in userToGeo:
                # print userToGeo[user]
                location = userToGeo[user][0]

                locationUserList = geocache[location]
                locationUserList.remove(user)
                del userToGeo[user]
        geosorted = list(geocache.items())
        geosorted.sort(key=lambda x: -len(x[1]))
        for key, value in geosorted:
            if len(value) > 0:
                geographicCluster = (key, [])
                geographicClusters.append(geographicCluster)
                for user in value:
                    geographicCluster[1].append(user)

    def makeImage(self, clusters, geocache, userToGeo, plopWords, bgcolor):

        rawUserToGeo = userToGeo.copy()

        geographicClusters = []
        self.removeExtraneousUsersFromGeoInfo(clusters, geographicClusters, geocache, userToGeo)

        ups = self.getOrderedUserList(clusters, geographicClusters, rawUserToGeo, plopWords)
        print((self._maxDay - self._minDay + 1) * (wPixelsPerUse + wLPixelBufferPerEvent + wRPixelBufferPerEvent),
              len(ups) * (hPixelsPerUse + hTPixelBufferPerEvent + hBPixelBufferPerEvent))
        # set image size
        im = Image.new("RGB", (
            (self._maxDay - self._minDay + 1) * (wPixelsPerUse + wLPixelBufferPerEvent + wRPixelBufferPerEvent),
            len(ups) * (hPixelsPerUse + hTPixelBufferPerEvent + hBPixelBufferPerEvent)), bgcolor)
        # im = Image.new("RGB", (1050, len(ups) * (hPixelsPerUse + hTPixelBufferPerEvent + hBPixelBufferPerEvent)), bgcolor)

        cm = ContrastingColors.ContrastingColors(bgcolor)
        cm.getContrastingColors(['PUBLICATION SUBMITTED', 'PUBLICATION ACCEPTED', 'PUBLICATION PUBLISHED'])

        draw = ImageDraw.Draw(im)

        userCount = 0
        for key, value in ups:
            userPattern = value
            # print "imaging user ", key
            for day in userPattern.patterns:
                toolsUsed = userPattern.patterns[day]
                colors = cm.getContrastingColors(toolsUsed)
                upperRight = ((day - self._minDay) * (wPixelsPerUse + wLPixelBufferPerEvent + wRPixelBufferPerEvent),
                              userCount * (hPixelsPerUse + hTPixelBufferPerEvent + hBPixelBufferPerEvent))
                height = hPixelsPerUse + hTPixelBufferPerEvent + hBPixelBufferPerEvent
                width = wPixelsPerUse + wLPixelBufferPerEvent + wRPixelBufferPerEvent
                # if ('PUBLISH' not in toolsUsed):
                if ('PUBLICATION SUBMITTED' not in toolsUsed and
                        'PUBLICATION ACCEPTED' not in toolsUsed and
                        'PUBLICATION PUBLISHED' not in toolsUsed):
                    if 'dummy' not in toolsUsed:
                        upperRight = (upperRight[0] + wLPixelBufferPerEvent, upperRight[1] + hTPixelBufferPerEvent)
                        height = hPixelsPerUse
                        width = wPixelsPerUse
                    else:
                        upperRight = (upperRight[0], upperRight[1] + hTPixelBufferPerEvent)
                        height = hPixelsPerUse
                curColor = 0
                for h in range(upperRight[1], upperRight[1] + height):
                    for w in range(upperRight[0], upperRight[0] + width):
                        if w < 0 or h < 0: print("plotting ", w, " ", h, " ", key)
                        draw.point([(w, h)], fill=colors[curColor])
                        curColor += 1
                        if curColor == len(colors): curColor = 0
            userCount = userCount + 1
        del draw
        return im

    def getGeographicClusterName(self, geoTriplet, usedNames):
        city = geoTriplet[0].strip()
        state = geoTriplet[1].strip()
        country = geoTriplet[2].strip()
        rv = city + '|' + state + '|' + country + '|'
        if rv not in usedNames:
            usedNames[rv] = 0
        usedNames[rv] = usedNames[rv] + 1
        return rv + '(' + str(usedNames[rv]) + ')'

    def makeClusterUserToolDayClustersizeList(self, clusters, geocache, userToGeo):
        rows = []
        takenGeoclusterNames = {}
        for cluster in clusters:
            clusterGeoLabel, primaryGeography, geoTriplet = self.getGeoLabelForCluster(cluster, userToGeo)
            clusterName = self.getGeographicClusterName(geoTriplet, takenGeoclusterNames)
            for user in cluster:
                city = 'UNKNOWN'
                state = 'UNKNOWN'
                country = 'UNKNOWN'
                if user in userToGeo:
                    city, state, country = userToGeo[user][1]
                userPattern = self._userPatterns[user.lower()]
                for key in userPattern.patterns:  # key here is a day
                    for tool in userPattern.patterns[key]:
                        rows.append([clusterName, user, tool, key, len(cluster), city, state, country])
        return rows
