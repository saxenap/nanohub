import os
import csv
import sys

class GetDomainForIPAddress:
	def __init__(self):
		self.theFile = open(os.path.expanduser('~/.nanoHUBGlobalData/ipXdomain.csv'),'rb')
		self.firstByte = 0
		self.reader = csv.reader(self.theFile)
		self.firstIP = None
		for row in self.reader:
			self.firstIP = row[0]
			break

		self.lastByte = self.theFile.seek(0, os.SEEK_END)
		self.theFile.seek(-2, os.SEEK_END)
		self.seekBeginningOfLine()
		self.lastByte = self.theFile.tell()

	def seekBeginningOfLine(self):
		while self.theFile.read(1) != '\n':
			self.theFile.seek(-2, os.SEEK_CUR)

	def getDomainForIP(self, ip):
		rv = None
		currentStartByte = self.firstByte
		currentEndByte = self.lastByte
		candidateByte = currentStartByte + (currentEndByte - currentStartByte)/2
		self.theFile.seek(candidateByte)
		self.seekBeginningOfLine()
		candidateByte = self.theFile.tell()
		candidateIPRow = self.reader.next()
		candidateIP = candidateIPRow[0]
		lastCurrentStartByte = None
		lastCurrentEndByte = None
		stuckRepeating = False
		while candidateIP != ip and currentEndByte > currentStartByte and not stuckRepeating:
			#print currentStartByte, candidateByte, currentEndByte
			if ip < candidateIP:
				currentEndByte = candidateByte
			else:
				currentStartByte = candidateByte
			candidateByte = currentStartByte + (currentEndByte - currentStartByte)/2
			#print "AJT",currentStartByte, candidateByte, currentEndByte
			self.theFile.seek(candidateByte)
			self.seekBeginningOfLine()
			candidateByte = self.theFile.tell()
			candidateIPRow = self.reader.next()
			#candidateByte = self.theFile.tell()
			#print "AJT LINE START",currentStartByte, candidateByte, currentEndByte
			candidateIP = candidateIPRow[0]
			if lastCurrentStartByte == currentStartByte and lastCurrentEndByte == currentEndByte:
				stuckRepeating = True
			else:
				lastCurrentStartByte = currentStartByte
				lastCurrentEndByte = currentEndByte
		if candidateIP == ip:
			if candidateIPRow == None:
				print candidateIP, ip
			if len(candidateIPRow) <= 1: print candidateIPRow
			rv = candidateIPRow[1]
		return rv
			

#dg = GetDomainForIPAddress()
#x = dg.getDomainForIP(sys.argv[1])
#print "THIS is IT",x

