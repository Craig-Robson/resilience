#import networkx
import networkx as nx
import sys

#specify location of module and import
sys.path.append('C:/a8243587_DATA/Dropbox/GUI')
import interdependency_analysis_v5_3_1 as ia
#import interdependency_analysis_v5_3_3 as ia

#create a network using networkx - can use any of the networkx generators or 
#node and edge lists
G = nx.gnm_random_graph(34,154)

#create a second, but make it equal to none so is ignored
GB = None

#specifiy the location and name of output file
fileName = 'C:/a8243587_DATA/Dropbox/results.txt'
#sepcify the location and name for a log file, or make = to None if not wanted
logfilepath = None

#stand_alone, dependency, interdependency
failure_1 = True, False, False
#single, sequential, cascading
failure_2 = False, True, False
#random, degree, betweenness
failure_3 = False, True, False

#get default set of parameters
parameters = ia.default_parameters(fileName, failure_1, failure_2, failure_3)

#run analysis
completed = ia.main(G, GB, parameters, logfilepath)
print 'Did the simultion complete (True/False): ', completed
