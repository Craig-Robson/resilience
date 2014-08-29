# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 14:15:46 2014

@author: a8243587
"""

import networkx as nx
import sys

sys.path.append('C:/a8243587_DATA/Dropbox/GUI')
import interdependency_analysis_v5_3_1 as ia

#create a network using networkx
G = nx.gnm_random_graph(34,154)
#create a second, but make it equal to none so is ignored
GB = None

#specifiy the location and name of output file
fileName = 'C:/a8243587_DATA/Dropbox/results.txt'
#sepcify the location and name for a log file, or make = to None or False
logfilepath = None

#get default set of parameters
parameters = ia.default_parameters(fileName)

#create metric containers
#graph_parameters = ia.core_analysis(G, GB, parameters) 

#run analysis
completed = ia.main(G, GB, parameters, logfilepath)
print 'Did the simultion complete (True/False): ', completed
