import csv
import sys

import MySQLdb



def getUsersThatHaveSessions(users):
	rv = set()
	conn = MySQLdb.connect(host = "db.nanohub.org",
						   user = "hub_read",
						   passwd = "XXXXXX",
						   db = "narwhal")
	cursor = conn.cursor()
	cursor.execute("""
				   select distinct username from sessionlog;
				   """)
	row = cursor.fetchone()
	while row != None:
		if row[0] in users:
			print row[0]
			rv.add(row[0])
		row = cursor.fetchone()
	cursor.close()
	conn.close()
	return rv

def getExpListExpDataOnlyUsers():
	rv = set()
	conn = MySQLdb.connect(host = "db.nanohub.org",
						   user = "hub_read",
						   passwd = "XXXXXX",
						   db = "nanohub")
	cursor = conn.cursor()
	cursor.execute("""
				   select distinct jxp.username from jos_citations as jc, jos_citations_authors as jca, jos_xprofiles as jxp
					where jca.cid = jc.id and jca.author_uid <> 0 and exp_list_exp_data = 1 and published = 1 and jca.author_uid = jxp.uidNumber and jca.author_uid not in 
					(select distinct jca.author_uid from jos_citations as jc, jos_citations_authors as jca where jca.cid = jc.id and jca.author_uid <> 0 and exp_data = 1 and published = 1);
				   """)
	row = cursor.fetchone()
	while row != None:
		print row[0]
		rv.add(row[0])
		row = cursor.fetchone()
	cursor.close()
	conn.close()
	return rv

def getExpDataOnlyUsers():
	rv = set()
	conn = MySQLdb.connect(host = "db.nanohub.org",
						   user = "hub_read",
						   passwd = "XXXXXX",
						   db = "nanohub")
	cursor = conn.cursor()
	cursor.execute("""
				   select distinct jxp.username from jos_citations as jc, jos_citations_authors as jca, jos_xprofiles as jxp
					where jca.cid = jc.id and jca.author_uid <> 0 and exp_data = 1 and published = 1 and jca.author_uid = jxp.uidNumber and jca.author_uid not in 
					(select distinct jca.author_uid from jos_citations as jc, jos_citations_authors as jca where jca.cid = jc.id and jca.author_uid <> 0 and exp_list_exp_data = 1 and published = 1);
				   """)
	row = cursor.fetchone()
	while row != None:
		print row[0]
		rv.add(row[0])
		row = cursor.fetchone()
	cursor.close()
	conn.close()
	return rv


def getPureExperimentalistUsers():
	rv = set()
	conn = MySQLdb.connect(host = "db.nanohub.org",
						   user = "hub_read",
						   passwd = "XXXXXX",
						   db = "nanohub")
	cursor = conn.cursor()
	cursor.execute("""
					select distinct jxp.username from jos_citations as jc, jos_citations_authors as jca, jos_xprofiles as jxp
					where jca.cid = jc.id and jca.author_uid <> 0 and exp_list_exp_data = 1 and published = 1 and jca.author_uid = jxp.uidNumber and
					jca.author_uid not in (select jca.author_uid from jos_citations as jc, jos_citations_authors as jca where jca.cid = jc.id and jca.author_uid <> 0 and exp_list_exp_data <> 1 and published = 1);
				   """)
	row = cursor.fetchone()
	while row != None:
		print row[0]
		rv.add(row[0])
		row = cursor.fetchone()
	cursor.close()
	conn.close()
	return rv



	
	
if len(sys.argv) != 1:
	print "Usage: ",sys.argv[0]," inputfile outputfile"
	sys.exit(1)
	
print "#######ExpListExpDataOnlyUsers######"
expListExpDataOnlyUsers = getExpListExpDataOnlyUsers()
print "#######Length ",len(expListExpDataOnlyUsers),"######"
print "#######Those who have sessions######"
sessionUsers = getUsersThatHaveSessions(expListExpDataOnlyUsers)
print "#######Length ",len(sessionUsers),"######"
print "#######ExpDataOnlyUsers######"
expDataOnlyUsers = getExpDataOnlyUsers()
print "#######Length ",len(expDataOnlyUsers),"######"
print "#######Those who have sessions######"
sessionUsers = getUsersThatHaveSessions(expDataOnlyUsers)
print "#######Length ",len(sessionUsers),"######"
print "#######pureExperimentalistUsers######"
pureExperimentalistUsers = getPureExperimentalistUsers()
print "#######Length ",len(pureExperimentalistUsers),"######"
print "#######Those who have sessions######"
sessionUsers = getUsersThatHaveSessions(pureExperimentalistUsers)
print "#######Length ",len(sessionUsers),"######"

#for user in expListExpDataOnlyUsers:
#	print user
	
