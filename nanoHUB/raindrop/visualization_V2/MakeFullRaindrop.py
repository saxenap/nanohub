from PIL import Image
from PIL import ImageDraw
import mysql.connector
from optparse import OptionParser
from . import UserToolDayPattern     # user defined function
import csv
import sys
import os

def call_func(path, m_id, startdate, enddate, geofilename, clusters, showcohort=True, showplopwords=True, white=False, rawfilename=None):
    # sys.stdout = open(options.clusterfilename.replace(".csv", "_sequence.txt"), 'w')

    geocache = {}
    userToGeo = {}

    if len(sys.argv) >= 3:
        geoReader = csv.reader(open(geofilename))
        for row in geoReader:
            user = row[0]
            location = row[1] + "," + row[2] + "," + row[3]
            if location not in geocache:
                geocache[location] = []
            geocache[location].append(user)
            userToGeo[user] = (location, (row[1], row[2], row[3]))

    showCohort = showcohort
    print("SC", showCohort, file=sys.stderr)
    showPlopwords = showplopwords

    bgcolor = (0, 0, 0)
    if white: bgcolor = (255, 255, 255)

    utdpl = UserToolDayPattern.UserToolDayPatternList(startdate, enddate, showCohort)

    if rawfilename is None:
        conn = mysql.connector.connect(host="127.0.0.1",
                                       user="shang26_ro",
                                       passwd="PNY0fvkqHQfx49ry",
                                       db="nanohub", port=3307)

        utdpl.grabAllFromDatabase(conn)
        conn.close()
    else:
        utdpl.grabAllFromFile(rawfilename)

    im = utdpl.makeImage(clusters, geocache, userToGeo, showPlopwords, bgcolor)

    # im.save(options.clusterfilename.replace('.csv', '.png'), 'PNG')
    # print(options.clusterfilename.replace('.csv', '.png'), 'PNG')
    # im.save('black.png')
    im.save(os.path.join(path, "M_" + "{:03d}".format(m_id) + ".png"))


if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--clusterfile", action="store", dest="clusterfilename",
                      help="A file listing clusters, one per line")
    parser.add_option("-f", "--rawfile", action="store", dest="rawfilename",
                      help="Use a file rather than a database for source data")
    parser.add_option("-g", "--geofile", action="store", dest="geofilename",
                      help="Name of file linking users to geographic clusters")
    parser.add_option("-s", "--startdate", action="store", dest="startdate",
                      help="Start date of cluster analysis (not needed if using a rawfile)")
    parser.add_option("-e", "--enddate", action="store", dest="enddate",
                      help="End date of cluster analysis (not needed if using a rawfile)")
    parser.add_option("-k", "--showcohort", action="store_true", dest="showcohort", default=False,
                      help="Show the entire cohort, not just the clusters")
    parser.add_option("-w", "--white", action="store_true", dest="white", default=False,
                      help="Use a white background")
    parser.add_option("-p", "--plopwords", action="store_false", dest="showplopwords", default=True,
                      help="Put geographics in pixelized font")
    (opts, args) = parser.parse_args()
    if not opts.clusterfilename:
        parser.error('Cluster file not provided')
    elif not opts.geofilename:
        parser.error('Geographical file not provided')
    elif not opts.rawfilename and (not opts.startdate or not opts.enddate):
        parser.error('Start and end dates must both be given when not supplying a rawfilename')
    print(opts, file=sys.stderr)

    clusters = []

    if len(sys.argv) >= 2:
        clusterReader = csv.reader(open(opts.clusterfilename))
        for row in clusterReader:
            cluster = []
            clusters.append(cluster)
            for elem in row:
                cluster.append(elem)

    call_func(opts, clusters)
