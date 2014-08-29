#import networkx
import networkx as nx
import sys

#specify location of module and import
sys.path.append('Location of module')
import interdependency_analysis_v5_3_2 as ia

#create a network using networkx - can use any of the networkx generators or 
#node and edge lists
G = nx.gnm_random_graph(34,154)

#create a second, but make it equal to none so is ignored
GB = None

#specifiy the location and name of output file
fileName = 'file location/file name.txt'
#sepcify the location and name for a log file, or make = to None if not wanted
logfilepath = None

#stand_alone, dependency, interdependency
failure_1 = True, False, False
#single, sequential, cascading
failure_2 = False, True, False
#random, degree, betweenness
failure_3 = False, True, False

#set parameters/metrics manually

#varaibles on how sub-graphs and isolated nodes are handled
REMOVE_SUBGRAPHS=False
REMOVE_ISOLATES=False
NO_ISOLATES=False

#Set as a list of edges for dependency analysis
a_to_b_edges = None

#basic metrics are: nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A
basic_A = True, True, True, True, True
basic_B = False, False, False, False, False

#option metrics are: 
size_of_components_A = True
giant_component_size_A = True
av_nodes_in_components_A = True
isolated_nodes_A = True
isolated_n_count_A = True
isolated_n_count_removed_A = True
subnodes_A = True
subnodes_count_A = True
path_length_A = True
av_path_length_components_A = True
giant_component_av_path_length_A = True
av_path_length_geo_A = False
average_degree_A = True
inter_removed_count_A = True

option_A = size_of_components_A,giant_component_size_A,av_nodes_in_components_A,
        isolated_nodes_A,isolated_n_count_A,isolated_n_count_removed_A,subnodes_A,
        subnodes_count_A,path_length_A,av_path_length_components_A,
        giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,
        inter_removed_count_A
option_B = False, False, False, False, False, False, False, False, False, False, 
        False, False, False, False

metrics = basic_A,basic_B,option_A,option_B

parameters = [metrics, failure_1[0], failure_1[1], failure_1[2], failure_2[0],
            failure_2[1], failure_2[2], failure_3[0], failure_3[1], failure_3[2], 
            REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, 
            fileName, a_to_b_edges]

#run analysis
completed = ia.main(G, GB, parameters, logfilepath)
print 'Did the simulation complete (True/False): ', completed
