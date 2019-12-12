import code
from pprint import pprint


import csv
'''
def form_cluster(name, tolerance, usages, differences, outputfile, createIntermediateFiles):
    
    #this program takes stuff from a file that has each line as
    #user, user, distance, user, distance...
    #where the first user is the "center" of a cluster
    #and turns it into a file that has each line being a cluster
    #user, user, user, user
    #
    #it also eliminates all subsets of other clusters so that you have
    #fewer clusters than in the input file.
    
    # rvForKey = []
    # differences[user1] = rvForKey
    # rvForKey.append((user2, diff))
                
    userDaySpans = {}
    for user in usages:
        toolUsagePattern = usages[user].usages
        userDaySpans[user] = (min(toolUsagePattern), max(toolUsagePattern)) # tuple. User's activity span in days
            
        
    #print >> sys.stderr, name, 'Clustering tolerance', tolerance
    
    clusters = {}
    
    #Read the clusters in.  Stepping over the elements of a row, this loop
    #finds the "clusterCenter" (the initial user) and then finds a user
    #followed by a distance, until the line is fully read.
    sortedKeys = sorted(differences.keys())

    for clusterCenter in sortedKeys:
      # for each username (clusterCenter is a username)
        clusterCandidates = set()
        clusterDaySpan = (0,0)
        others = differences[clusterCenter] # list of tuples containing (other username, cost)
        if len(others) > 0:
            clusters[clusterCenter] = set()
            clusters[clusterCenter].add(clusterCenter) # add username into its own set
            clusterDaySpan = userDaySpans[clusterCenter]
            
            for clusteredUser, clusteredUserDistance in others:
                if clusteredUserDistance <= tolerance:
                  # add all other usernames whose cost is lower than tolerance
                    clusterCandidates.add(clusteredUser)
                    
            for candidate in clusterCandidates:
              # iterate through all candidates that are closely associated with username #1
                if clusterDaySpan[0] == clusterDaySpan[1]:
                  # username #1 only has a single-day activity
                    clusterDay = clusterDaySpan[0]
                    candidateDaySpan = userDaySpans[candidate]
                    
                    if candidateDaySpan[0] <= clusterDay and candidateDaySpan[1] >= clusterDay:
                      # single-day is within candidate activity span
                        clusters[clusterCenter].add(candidate)
                    elif abs(candidateDaySpan[0] - clusterDay) == 1 or abs(candidateDaySpan[1] - clusterDay) == 1:
                      # single-day is within 1-day of candidate acitivity span
                        clusters[clusterCenter].add(candidate)
                
                else:
                  # add candidates into username #1 cluster
                    clusters[clusterCenter].add(candidate)
                
            if len(clusters[clusterCenter]) == 1:
                del clusters[clusterCenter]



    
    eliminatedClusters = 0
    
    removeClusters = set()
    
    clusterList = list(clusters.items())
    
    clusterSizeMinimum = 4
    
    #Generate a set of clusters to remove based on one being a superset of another,
    #or also if a cluster size does not meet the minimum requirement.
    
    # clusterList[i] = (username #i, set(username_A, username_B, .....))

    for i in range(0,len(clusterList)):
        #if i % 500 == 0: print i
        if len(clusterList[i][1]) <= clusterSizeMinimum:
          # remove clusters that are smaller than minimum size
            removeClusters.add(clusterList[i][0])
            
        elif clusterList[i][0] not in removeClusters:
          # username #i is not in removal list
            for j in range(i+1, len(clusterList)):
              # for each username after #i
                if clusterList[j][0] not in removeClusters:
                  # username #j is not in removal list
                  
                    if len(clusterList[j][1]) <= clusterSizeMinimum:
                      # remove clusters that are smaller than minimum size
                        removeClusters.add(clusterList[j][0])
                        
                    elif clusterList[i][1] == clusterList[j][1]:
                      # if cluster #i and #j are identical
                        removeClusters.add(clusterList[j][0])
                        
                    elif clusterList[i][1] >= clusterList[j][1]:
            # remove the smaller cluster, if bigger cluster includes the smaller one
                        removeClusters.add(clusterList[j][0])
                        
                    elif clusterList[i][1] <= clusterList[j][1]:
                        removeClusters.add(clusterList[i][0])
                        break #if you are going to remove the cluster in the outer loop, then might as well stop and not do any more
                        #print "removing cluster ", clusterList[j][0], " because ", clusterList[i][1], " >= ", clusterList[j][1]
    
    #Now actually remove the clusters - couldn't do this before
    #because you don't want to change a set while iterating over it.
    print(name+"Initially "+str(len(clusters))+" clusters")

    for i in removeClusters:
        del clusters[i]
    
    #print >> sys.stderr, name, "Finally ",len(clusters)," clusters"
    
    if outputfile != None and createIntermediateFiles == True:
        outfile = open(outputfile, 'w')
        clusterWriter = csv.writer(outfile);
    
        for key in clusters:
            clusterWriter.writerow(list(clusters[key]))
        outfile.close()

    #convert a dictionary of clusters into a list of sets for return
    rvclusters = []
    for key in clusters:
        rvclusters.append(clusters[key])
    return rvclusters
'''    
    
def user_cluster_formation(user_usage_row, user_usage_indexed_df, tolerance):
    '''
    sortedKeys = sorted(differences.keys())
    for clusterCenter in sortedKeys:
      # for each username (clusterCenter is a username)
        clusterCandidates = set()
        clusterDaySpan = (0,0)
        others = differences[clusterCenter] # list of tuples containing (other username, cost)
        if len(others) > 0:
            clusters[clusterCenter] = set()
            clusters[clusterCenter].add(clusterCenter) # add username into its own set
            #clusterDaySpan = userDaySpans[clusterCenter]
            clusterDaySpan = user_usage_indexed_df.loc[user_usage_df].userDaySpans
            
            for clusteredUser, clusteredUserDistance in others:
                if clusteredUserDistance <= tolerance:
                  # add all other usernames whose cost is lower than tolerance
                    clusterCandidates.add(clusteredUser)
                    
            for candidate in clusterCandidates:
              # iterate through all candidates that are closely associated with username #1
                if clusterDaySpan[0] == clusterDaySpan[1]:
                  # username #1 only has a single-day activity
                    clusterDay = clusterDaySpan[0]
                    #candidateDaySpan = userDaySpans[candidate]
                    candidateDaySpan = user_usage_indexed_df.loc[candidate].userDaySpans
                                        
                    if candidateDaySpan[0] <= clusterDay and candidateDaySpan[1] >= clusterDay:
                      # single-day is within candidate activity span
                        clusters[clusterCenter].add(candidate)
                    elif abs(candidateDaySpan[0] - clusterDay) == 1 or abs(candidateDaySpan[1] - clusterDay) == 1:
                      # single-day is within 1-day of candidate acitivity span
                        clusters[clusterCenter].add(candidate)
                
                else:
                  # add candidates into username #1 cluster
                    clusters[clusterCenter].add(candidate)
                
            if len(clusters[clusterCenter]) == 1:
                del clusters[clusterCenter]
    '''
    
    others = user_usage_row.usages
    clusters = set()
    
    if len(others) == 0:
        # empty list
        return clusters
    
    clusterCandidates = set([user_usage_row.name])
    clusterDaySpan = user_usage_row.userDaySpans
    
    for clusteredUser, clusteredUserDistance in others:
        if clusteredUserDistance <= tolerance:
            # add all other usernames whose cost is lower than tolerance
            clusterCandidates.add(clusteredUser)
            
    for candidate in clusterCandidates:
        # iterate through all candidates that are closely associated with username #1
        if clusterDaySpan[0] == clusterDaySpan[1]:
            # username #1 only has a single-day activity
            clusterDay = clusterDaySpan[0]
            #candidateDaySpan = userDaySpans[candidate]

            candidateDaySpan = user_usage_indexed_df.loc[candidate].userDaySpans
                        
            if candidateDaySpan[0] <= clusterDay and candidateDaySpan[1] >= clusterDay:
                # single-day is within candidate activity span
                clusters.add(candidate)
                
            elif abs(candidateDaySpan[0] - clusterDay) == 1 or abs(candidateDaySpan[1] - clusterDay) == 1:
                # single-day is within 1-day of candidate acitivity span
                clusters.add(candidate)

        else:
            # add candidates into username #1 cluster
            clusters.add(candidate)

    if len(clusters) == 1:
        clusters = set()
                    
    return clusters
    
    
    
    
def form_cluster_new(tolerance, user_usage_df, outputfile):
    #this program takes stuff from a file that has each line as
    #user, user, distance, user, distance...
    #where the first user is the "center" of a cluster
    #and turns it into a file that has each line being a cluster
    #user, user, user, user
    #
    #it also eliminates all subsets of other clusters so that you have
    #fewer clusters than in the input file.
    
    # rvForKey = []
    # differences[user1] = rvForKey
    # rvForKey.append((user2, diff))
    
    user_usage_indexed_df = user_usage_df.set_index('user')
    user_usage_indexed_df['userDaySpans'] = user_usage_indexed_df.apply(lambda x: (min(x.ToolUsagePattern.usages), max(x.ToolUsagePattern.usages)), axis=1)
    
    
    
                
    #userDaySpans = {}
    #for user in usages:
    #    toolUsagePattern = usages[user].usages
    #    userDaySpans[user] = (min(toolUsagePattern), max(toolUsagePattern)) # tuple. User's activity span in days
            
        
    #print >> sys.stderr, name, 'Clustering tolerance', tolerance
    
    clusters = {}
    
    #Read the clusters in.  Stepping over the elements of a row, this loop
    #finds the "clusterCenter" (the initial user) and then finds a user
    #followed by a distance, until the line is fully read.


    '''
    sortedKeys = sorted(differences.keys())
    for clusterCenter in sortedKeys:
      # for each username (clusterCenter is a username)
        clusterCandidates = set()
        clusterDaySpan = (0,0)
        others = differences[clusterCenter] # list of tuples containing (other username, cost)
        if len(others) > 0:
            clusters[clusterCenter] = set()
            clusters[clusterCenter].add(clusterCenter) # add username into its own set
            #clusterDaySpan = userDaySpans[clusterCenter]
            clusterDaySpan = user_usage_indexed_df.loc[user_usage_df].userDaySpans
            
            for clusteredUser, clusteredUserDistance in others:
                if clusteredUserDistance <= tolerance:
                  # add all other usernames whose cost is lower than tolerance
                    clusterCandidates.add(clusteredUser)
                    
            for candidate in clusterCandidates:
              # iterate through all candidates that are closely associated with username #1
                if clusterDaySpan[0] == clusterDaySpan[1]:
                  # username #1 only has a single-day activity
                    clusterDay = clusterDaySpan[0]
                    #candidateDaySpan = userDaySpans[candidate]
                    candidateDaySpan = user_usage_indexed_df.loc[candidate].userDaySpans
                                        
                    if candidateDaySpan[0] <= clusterDay and candidateDaySpan[1] >= clusterDay:
                      # single-day is within candidate activity span
                        clusters[clusterCenter].add(candidate)
                    elif abs(candidateDaySpan[0] - clusterDay) == 1 or abs(candidateDaySpan[1] - clusterDay) == 1:
                      # single-day is within 1-day of candidate acitivity span
                        clusters[clusterCenter].add(candidate)
                
                else:
                  # add candidates into username #1 cluster
                    clusters[clusterCenter].add(candidate)
                
            if len(clusters[clusterCenter]) == 1:
                del clusters[clusterCenter]
    '''
    
    # Pandas implementation
    result = user_usage_indexed_df.apply(user_cluster_formation, user_usage_indexed_df = user_usage_indexed_df, tolerance = tolerance, axis=1)

    # END of Pandas implementation
    
    '''
    user
    fabien                          {shigeyasu, fabien, kennyxue, gsun}
    gbu                                   {aamjad, bashir, gbu, agupta}
    manolo_sperini                                                   {}
    marchi                                                           {}
    sbahl             {fervorviolinist, boz, singhd, dlsherma, tbig,...
    '''
    
    eliminatedClusters = 0
    
    removeClusters = set()
    
    clusterList = list(clusters.items())
    
    clusterSizeMinimum = 4
    
    #Generate a set of clusters to remove based on one being a superset of another,
    #or also if a cluster size does not meet the minimum requirement.
    
    # clusterList[i] = (username #i, set(username_A, username_B, .....))

    for i in range(0,len(clusterList)):
        #if i % 500 == 0: print i
        if len(clusterList[i][1]) <= clusterSizeMinimum:
          # remove clusters that are smaller than minimum size
            removeClusters.add(clusterList[i][0])
            
        elif clusterList[i][0] not in removeClusters:
          # username #i is not in removal list
            for j in range(i+1, len(clusterList)):
              # for each username after #i
                if clusterList[j][0] not in removeClusters:
                  # username #j is not in removal list
                  
                    if len(clusterList[j][1]) <= clusterSizeMinimum:
                      # remove clusters that are smaller than minimum size
                        removeClusters.add(clusterList[j][0])
                        
                    elif clusterList[i][1] == clusterList[j][1]:
                      # if cluster #i and #j are identical
                        removeClusters.add(clusterList[j][0])
                        
                    elif clusterList[i][1] >= clusterList[j][1]:
            # remove the smaller cluster, if bigger cluster includes the smaller one
                        removeClusters.add(clusterList[j][0])
                        
                    elif clusterList[i][1] <= clusterList[j][1]:
                        removeClusters.add(clusterList[i][0])
                        break #if you are going to remove the cluster in the outer loop, then might as well stop and not do any more
                        #print "removing cluster ", clusterList[j][0], " because ", clusterList[i][1], " >= ", clusterList[j][1]
    
    #Now actually remove the clusters - couldn't do this before
    #because you don't want to change a set while iterating over it.
    print(name+"Initially "+str(len(clusters))+" clusters")

    for i in removeClusters:
        del clusters[i]
    
    #print >> sys.stderr, name, "Finally ",len(clusters)," clusters"

    # Pandas implementation
    
    #

    
    if outputfile != None:
        outfile = open(outputfile, 'w')
        clusterWriter = csv.writer(outfile);
    
        for key in clusters:
            clusterWriter.writerow(list(clusters[key]))
        outfile.close()

    #convert a dictionary of clusters into a list of sets for return
    rvclusters = []
    for key in clusters:
        rvclusters.append(clusters[key])
    return rvclusters
