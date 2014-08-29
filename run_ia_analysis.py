# -*- coding: utf-8 -*-
"""
Created on Wed Apr 02 08:23:20 2014

@author: a8243587

********
Version 2_4_0 - replaces the lists of metrics with dicts - integrates with 
v5_4_0 of main resilince module.

Last good version - run_ia_analysis or run_ia_analysis v2_0_0
********



"""
#import python modules
import networkx as nx
import ogr, sys

#import resilience module
import interdependency_analysis_v5_4_0 as ia

#import nx_pgnet module
sys.path.append("C:/a8243587_DATA/Dropbox/GitRepo/nx_pgnet")
import nx_pgnet

#import subsidiary resilience modules
sys.path.append("C:/a8243587_DATA/Dropbox/resilience_module/resilience_modules")
import tools, error_classes

def analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath):
    ''''''
    #unpack varaibles
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, results_file, a_to_b_edges = parameters
    #if performing analysis on one network only    
    if STAND_ALONE == True:
        count = 0
        #loop through the listed networks
        for nets in NETWORK_NAME:
            if db=='theoretic_networks_tree' or db=='theoretic_networks_hc' or db=='theoretic_networks_hr' or db=='theoretic_networks_ahr' or db=='theoretic_networks_ba'or db=='theoretic_networks_ws' or db=='theoretic_networks_gnm' or db=='theoretic_networks_er':
                nets = str(nets)+'_'+str(count)
                count += 1
            iterations = 0
            #while noia(the number of simulation to perform) is greater then the number performed
            while iterations < noioa:
                #if the network is to be got from the database
                if use_db == True: 
                    #connect to the database and get the network
                    conn = ogr.Open(conn)
                    G = nx_pgnet.read(conn).pgnet(nets)
                #the network must come from a csv
                else:
                    #get the text file
                    # maybe replace file_path with fileName1
                    filepath = str(file_path)+'%s/%s.txt' %(db, nets)
                    nodelist, edgelist = tools.get_nodes_edges_csv(filepath)
                    #build the network from the lists returned from the function
                    G = nx.Graph()
                    G.add_nodes_from(nodelist)
                    G.add_edges_from(edgelist)
                #set the name of the results text file
                fileName = str(results_file)+'%s/%s%s.txt'%(db,nets,failuretype)
                #package the parameters together
                parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges
                #need a value for network B (G2)
                G2 = None
                #perform the analusis
                ia.main(G, G2, parameters, logfilepath)
                iterations += 1
                
    #if dependency or intersedpendcy
    elif STAND_ALONE == False:
        if use_db == True:
            conn = ogr.Open(conn)
            G = nx_pgnet.read(conn).pgnet(nets)
            raise error_classes.GeneralError('Error. This function does not work as yet.')
        elif use_db == False:
            #get both networks from csv
            filepath = str(file_path)+'%s/%s.txt' %(db, NETWORK_NAME[0])
            nodelist, edgelist = tools.get_nodes_edges_csv(filepath)
            G1 = nx.Graph()
            G1.add_nodes_from(nodelist)
            G1.add_edges_from(edgelist)
            filepath = str(file_path)+'%s/%s.txt' %(db, NETWORK_NAME[1])
            nodelist, edgelist = tools.get_nodes_edges_csv(filepath)
            G2 = nx.Graph()
            G2.add_nodes_from(nodelist)
            G2.add_edges_from(edgelist)
        ia.main(G1, G2, parameters,logfilepath)
    else:
        raise error_classes.GeneralError('Error. The STAND_ALONE variable must have a boolean value')



#------------------type of failure-----------------------------------------
STAND_ALONE = True; DEPENDENCY = False; INTERDEPENDENCY = False 

#------------------method of failure---------------------------------------
SINGLE = False; SEQUENTIAL = True; CASCADING = False

#------------------node selection method-----------------------------------
RANDOM = False; DEGREE = False; BETWEENNESS = True

#------------------analysis parameters-------------------------------------
REMOVE_SUBGRAPHS = False; REMOVE_ISOLATES = True; NO_ISOLATES = True
#REMOVE_SUBGRAPHS: When subgraphs appear, delete from network
#REMOVE_ISOLATES: When isolated nodes appear, delete from network
#NO_ISOLATES: Allow isolated nodes to be removed in the selection methods    

#------------------setting of data input type------------------------------
use_db = False
use_csv = False
mass = False
if mass == True:
    import network_data_v_0_2 as network_data #does not currently work as no file path for it yet

#------------------use lof file--------------------------------------------
#logfilepath = False    
#logfilepath = 'C:/a8243587_DATA/Dropbox/'
logfilepath = 'C:/a8243587_DATA/logfile.txt'

#------------------path name for the result files--------------------------
"when using analysing exisiting networks dont need name of outputfile here, just the location"
#result_file = 'H:/robustness/results/' #for desktop
result_file = 'C:/a8243587_DATA/Dropbox/result.txt'
#result_file = 'C:/Users/Craig/Dropbox/robustness/results/' #for laptop

#------------------path name for the input files---------------------------
file_path = 'H:/robustness/csv_network_data/'
#file_path = 'C:/Users/Craig/Dropbox/robustness/csv_network_data/'

#------------------auto generate text for failure model--------------------
failuretype = tools.failure_type(SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS)

#------------------single quick analysis-----------------------------------
GA = nx.gnm_random_graph(50,369)
#edges = [(1,3),(2,4),(1,2),(1,4),(3,4),(4,5)]
#GA = nx.Graph()
#GA.add_edges_from(edges)

if STAND_ALONE == True: GB = None
else: 
    GB = nx.gnm_random_graph(34,145)
    #edges = [(1,2),(1,3),(1,4),(2,4),(4,3)]     
    #GB = nx.Graph()
    #GB.add_edges_from(edges)

#------------------setting of dependency edges-----------------------------
if DEPENDENCY == True or INTERDEPENDENCY == True:
    a_to_b_edges = [(3,1),(3,2),(5,3)]
    if INTERDEPENDENCY == True:
        b_to_a_edges = []
else:
    a_to_b_edges = None       

#--------------parameters for the database connection----------------------
host = 'localhost'
user = 'postgres'
password = 'aaSD2011'
port = '5433'

#---------------------sql for dependency edges-----------------------------
#interdependency code does not work yet
#fromSQL='SELECT "p" FROM "Inter_Lines"'
#toSQL='SELECT "t" FROM "Inter_Lines"'


#-----------------------weight field for path length-----------------------
length = 'shape_leng'

#------------------declaration of basic metrics for analysis---------------
nodes_removed_A = True #nodes removed from network A
node_count_removed_A = True #count of ndoes removed from network A   
count_nodes_left_A = True #the number of nodes left in network A
number_of_edges_A = True #number of edges in the network
number_of_components_A = True #number of subgraphs/isolated nodes
  
if STAND_ALONE == False:      
      nodes_removed_B = True #nodes removed from network B
      node_count_removed_B = True #count of ndoes removed from network B   
      count_nodes_left_B = True #the number of nodes left in network B
      number_of_edges_B = True #number of edges in the network
      number_of_components_B = True #number of subgraphs/isolated nodes

#------------------declaration of optional metrics-------------------------
size_of_components_A = False
giant_component_size_A = False
av_nodes_in_components_A = False
isolated_nodes_A = True #THIS NEEDS TO BE IN THE BASIC SET
isolated_n_count_A = True #THIS NEEDS TO BE IN THE BASIC SET
isolated_n_count_removed_A = False
subnodes_A = False
subnodes_count_A = False   
path_length_A = False
av_path_length_components_A = False
av_path_length_geo_A = False
giant_component_av_path_length_A = False
average_degree_A = False
inter_removed_count_A = False #THIS IS ONLY NEEDED IF INTERDEPENDENCY

if STAND_ALONE == False:        
    size_of_components_B = False
    giant_component_size_B = False
    av_nodes_in_components_B = False
    isolated_nodes_B = True #THIS NEEDS TO BE IN THE BASIC SET
    isolated_n_count_B = True #THIS NEEDS TO BE IN THE BASIC SET
    isolated_n_count_removed_B = False
    subnodes_B = False
    subnodes_count_B = False   
    path_length_B = False
    av_path_length_components_B = False
    av_path_length_geo_B = False
    giant_component_av_path_length_B = False
    average_degree_B = False
    inter_removed_count_B = True #THIS IS NEEDED IF NOT STAND ALONE

#------------------metrics needed for cascading analysis - overrides above
if CASCADING == True:
    pass #for the moment anyway

#------------------option to set the attribute which contins the length of the edges
if av_path_length_geo_A <> False: length = 'length'
if STAND_ALONE == False:
    if av_path_length_geo_B <> False: length = 'length'
        
#------------------compile metrics into variables--------------------------
basic_metrics_a = {'nodes_removed':nodes_removed_A,'no_of_nodes_removed':node_count_removed_A,
                   'no_of_nodes_left':count_nodes_left_A,'number_of_edges':number_of_edges_A,
                   'number_of_components':number_of_components_A}
option_metrics_a = {'size_of_components':size_of_components_A,'size_of_giant_component':giant_component_size_A,
                    'avg_no_of_nodes_in_components':av_nodes_in_components_A,
                    'isolated_nodes':isolated_nodes_A,'no_of_isolated_nodes':isolated_n_count_A,
                    'no_of_isolated_nodes_removed':isolated_n_count_removed_A,
                    'subnodes':subnodes_A,'no_of_subnodes':subnodes_count_A,
                    'avg_path_length':path_length_A,'avg_path_length_of_components':av_path_length_components_A,
                    'giant_components_avg_path_length':giant_component_av_path_length_A,
                    'avg_geo_path_length':av_path_length_geo_A,'avg_degree':average_degree_A,
                    'interdependency_nodes_removed':inter_removed_count_A}

if STAND_ALONE == False:
    basic_metrics_B =  nodes_removed_B,node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B
    option_metrics_B = size_of_components_B,giant_component_size_B,av_nodes_in_components_B,isolated_nodes_B,isolated_n_count_B,isolated_n_count_removed_B,subnodes_B,subnodes_count_B,path_length_B,av_path_length_components_B,giant_component_av_path_length_B,av_path_length_geo_B,average_degree_B,inter_removed_count_B
else: basic_metrics_B = None; option_metrics_B = None
metrics = basic_metrics_A, basic_metrics_B, option_metrics_A, option_metrics_B  

#------------------not sure what this is doing-----------------------------
file_1_name = 'dependencey_test_n1'
file_2_name = 'dependencey_test_n2'
db = 'testing'
          
#------------------analysis methods----------------------------------------
if DEPENDENCY == True and mass == False and use_csv == True: #for csv only #for dependency analysis
    parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, result_file, a_to_b_edges
    NETWORK_NAME = file_1_name, file_2_name #list the name of the two networks for the analysis
    conn = None; noia = 1
    ia.analyse_existing_networks(NETWORK_NAME,conn,db,parameters,noia,use_db,use_csv)
elif DEPENDENCY == True and mass == False:
    parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, result_file, a_to_b_edges
    complete = ia.main(GA, GB, parameters,logfilepath)
    print complete
elif mass == False and STAND_ALONE == True: #for single network analysis
    parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, result_file, a_to_b_edges
    complete = ia.main(GA, GB, parameters,logfilepath)
    print 'complete:', complete
elif INTERDEPENDENCY == True and mass == False: #for interdependendency analysis
    pass
elif mass == True and STAND_ALONE == True: #for mass single analysis
    print 'where mass = True and Stand_alone = true'
    '''select which network types to analyse'''
    lightrail = False; roads_national = False; roads_regional = False
    air = False; other = False; infrastructure = False
    er = False; gnm = False; ws = False; ba = False
    hra = False; hr = False; hc = False; tree = True
    
    noioa = 5   #number_of_iterations_of_analysis
    parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, result_file, a_to_b_edges

    if air== True:
        db = 'air'
        NETWORK_NAME, conn = network_data.air_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if lightrail == True:
        db = 'lightrail'
        NETWORK_NAME, conn = network_data.lightrail_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if roads_national == True:
        db = 'roads_national'
        NETWORK_NAME, conn = network_data.road_national_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)       
    if roads_regional== True:
        db = 'roads_regional'
        NETWORK_NAME, conn = network_data.road_regional_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if other== True:
        db = 'other'
        NETWORK_NAME, conn = network_data.other_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if infrastructure== True:
        db = 'infrastructure'
        NETWORK_NAME, conn = network_data.infra_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)            
    if er == True:
        db = 'er'
        NETWORK_NAME,conn = network_data.er_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if gnm == True:
        db = 'gnm'
        NETWORK_NAME, conn = network_data.gnm_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if ws == True:
        db = 'ws'
        NETWORK_NAME, conn = network_data.ws_networks()        
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if ba == True:
        db = 'ba'
        NETWORK_NAME, conn = network_data.ba_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if hra == True:
        db = 'hra'
        NETWORK_NAME, conn = network_data.hra_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if hr == True:
        db = 'hr'
        NETWORK_NAME, conn = network_data.hr_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if hc == True:
        db = 'hc'
        NETWORK_NAME, conn = network_data.hc_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if tree == True:
        db = 'theoretic_networks_tree'
        NETWORK_NAME, conn = network_data.tree_networks()
        ia.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    else:
        print 'no networks selected'
else:
    print 'combination of parameters is not correct'        
    print 'check analysis parameters'