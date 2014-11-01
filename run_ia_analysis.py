# -*- coding: utf-8 -*-
"""
Created on Wed Apr 02 08:23:20 2014

@author: a8243587

"""
#import python modules
import networkx as nx
import sys


#read in config file to get file paths
f = open("config.txt")
for line in f.readlines():
    if line[0:8]=="nx_pgnet":
        line = line.split('\t')
        nx_pgnet_location = line[1].strip()
    elif line[0:10]=="resilience":
        line = line.split("\t")
        resil_mod_loc = line[1].strip()
        resil_mod_loc = resil_mod_loc + str("/modules")
                
#import resilience module
import interdependency_analysis as ia

sys.path.append(nx_pgnet_location)
import nx_pgnet

#import subsidiary resilience modules
sys.path.append(resil_mod_loc)
import tools

#make modules accessable in ia module
ia.import_modules(resil_mod_loc)

#-------------------------------------------------------------------------

failure = {'stand_alone':True, 'dependency':False, 'interdependency':False,
        'single':False, 'sequential':True, 'cascading':False,
        'random':False, 'degree':True, 'betweenness':False, 'from_list':False}

#------------------analysis parameters-------------------------------------
#REMOVE_SUBGRAPHS: When subgraphs appear, delete from network
#REMOVE_ISOLATES: When isolated nodes appear, delete from network
#NO_ISOLATES: Allow isolated nodes to be removed in the selection methods
handling_variables = {'remove_subgraphs':True,'remove_isolates':True,'no_isolates':False}  

#------------------setting of data input type------------------------------
use_nx_single = True
use_db = False
use_csv = False
mass = False

if mass == True:
    import network_data as network_data #does not currently work as no file path for it yet

#------------------use lof file--------------------------------------------
logfilepath = 'C:/a8243587_DATA/GitRepo/_res_testing/logfile.txt'
#logfilepath = 'C:/Users/Craig/GitRepo/_res_testing/logfile.txt'

#------------------path name for the result files--------------------------
"when using analysing exisiting networks dont need name of outputfile here, just the location"
result_file = 'C:/a8243587_DATA/GitRepo/_res_testing/result.txt'
#result_file = 'C:/Users/Craig/GitRepo/_res_testing/result.txt' #for laptop

#------------------path name for the input files---------------------------
file_path = 'H:/robustness/csv_network_data/'
#file_path = 'C:/Users/Craig/Dropbox/robustness/csv_network_data/'

#------------------auto generate text for failure model--------------------
failuretype = tools.failure_type(failure)

#--------------for single quick analysis-----------------------------------
GA = nx.gnm_random_graph(50,369)
#edges = [(1,3),(2,4),(1,2),(1,4),(3,4),(4,5)]
#GA = nx.Graph()
#GA.add_edges_from(edges)

if failure['stand_alone'] == True: GB = None
else: 
    GB = nx.gnm_random_graph(34,145)
    #edges = [(1,2),(1,3),(1,4),(2,4),(4,3)]     
    #GB = nx.Graph()
    #GB.add_edges_from(edges)  

#--------------parameters for the database connection----------------------
host = 'localhost'
user = 'postgres'
password = 'aaSD2011'
port = '5433'
dbname = 'tetsting_res'

net_name_a = 'power_lines'; net_name_b = 'tube_lines'
con = {'host':host,'dbname':dbname,'user':user,'password':password,'port':port}
conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
srid_a = 27700; srid_b = 27700;spatial_a=True;spatial_b=True
save_a = True; save_b = True
db_parameters = conn, net_name_a, net_name_b, save_a, save_b, srid_a, srid_b, spatial_a, spatial_b

#------------------option when analysis from db------------------------------
#to save the metrics at end of each time step to db
write_results_table=True
#to wirte metrics to the attributes of the nodes and edges
store_n_e_atts=True
#to save network(s) at each time step to the database
write_step_to_db = True

#------------------setting of dependency edges-----------------------------
if failure['dependency'] == True or failure['interdependency'] == True:
    #a_to_b_edges = [(3,1),(3,2),(5,3),(34,45),(24,89),(35,245),(54,345),(54,101),(78,254),(65,289),(32,198),(92,312)]
    a_to_b_edges = [(3,1),(3,2),(5,3),(34,12)]#,(24,36),(35,245),(54,345),(54,101),(78,254),(65,289),(32,198),(92,312)]
    #fromSQL='SELECT "p" FROM "Inter_Lines"
    #toSQL='SELECT "t" FROM "Inter_Lines"
    if failure['interdependency'] == True:
        b_to_a_edges = []
else:
    a_to_b_edges = None  
#------------------source nodes for networks--------------------------------
#set as None if not using these - functions will ignore them
#if wanted eg. [2,56,34]
source_nodes_A = [2,5,34]
source_nodes_B = [12,1,2]

#------------------compile metrics into variables--------------------------
basic_metrics_A = {'nodes_removed':True,'no_of_nodes_removed':True,'no_of_nodes':True,
                   'no_of_edges':True,'no_of_components':True,
                   'no_of_isolated_nodes':True,'isolated_nodes_removed':True,
                   'nodes_selected_to_fail':True}
option_metrics_A = {'size_of_components':           True,
                    'giant_component_size':         True,
                    'avg_size_of_components':       True,
                    'isolated_nodes':               True,
                    'no_of_isolated_nodes_removed': True,
                    'subnodes':                     False,
                    'no_of_subnodes':               False,
                    'source_nodes':                 True,
                    'failed_no_con_to_a_source':    True,
                    'avg_path_length':              False,
                    'avg_path_length_of_components':False,
                    'avg_path_length_of_giant_component':   False,
                    'avg_geo_path_length':                  False,
                    'avg_geo_path_length_of_components':    False,
                    'avg_geo_path_length_of_giant_component':False,
                    'avg_degree':                   False,
                    'density':                      False,
                    'maximum_betweenness_centrality':False,
                    'avg_betweenness_centrality':   False,
                    'assortativity_coefficient':    False,
                    'clustering_coefficient':       False,
                    'transitivity':                 False,
                    'square_clustering':            False,
                    'avg_neighbor_degree':          False,
                    'avg_degree_connectivity':      False,
                    'avg_degree_centrality':        False,
                    'avg_closeness_centrality':     False,
                    'diameter':                     False
                    }

if failure['stand_alone'] == False:
    basic_metrics_B = basic_metrics_A.copy()
    option_metrics_B = option_metrics_A.copy()
    basic_metrics_B['nodes_selected_to_fail']=False
else: basic_metrics_B = None; option_metrics_B = None

dependency = None
cascading = None
metrics = basic_metrics_A, basic_metrics_B, option_metrics_A, option_metrics_B, dependency, cascading  

#------------------option to set the attribute which contins the length of the edges
if option_metrics_A['avg_geo_path_length'] <> False: length = 'shape_leng'
else: length = None

#------------------file names for csv based analysis-------------------------
file_1_name = 'dependencey_test_n1'
file_2_name = 'dependencey_test_n2'

#-----------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------run some checks-----------------------------------------
if failure['interdependency']==True: print 'This functionality is not currently available.'; exit()
if failure['cascading']==True: print 'WARNING! This functionality has not been tested fully yet.'

#------------------analysis methods----------------------------------------
if use_nx_single == True:
    write_results_table=False;store_n_e_atts=False;write_step_to_db=False
    parameters = metrics,failure,handling_variables,result_file,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length,source_nodes_A,source_nodes_B
    complete = ia.main(GA, GB, parameters,logfilepath)
elif use_csv == True:
    write_results_table=False;store_n_e_atts=False;write_step_to_db=False
    parameters = metrics,failure,handling_variables,result_file,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length,source_nodes_A,source_nodes_B
    NETWORK_NAME = file_1_name, file_2_name #list the name of the two networks for the analysis
    conn = None; noia = 1
    ia.analyse_existing_networks(NETWORK_NAME,conn,dbname,parameters,noia,use_db,use_csv)
elif use_db == True:
    parameters = metrics,failure,handling_variables,result_file,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length,source_nodes_A,source_nodes_B
    conn, net_name_a, net_name_b, save_a, save_b, srid_a, srid_b, spatial_a, spatial_b = db_parameters
    import ogr
    conn = ogr.Open(conn)
    GA = nx_pgnet.read(conn).pgnet(net_name_a)
    GB = nx_pgnet.read(conn).pgnet(net_name_b)
    for nd in GA.nodes(data=True): del nd[1]['id']
    for nd in GB.nodes(data=True): del nd[1]['id']
    complete = ia.main(GA, GB, parameters,logfilepath)
elif mass == True and failure['stand_alone'] == True: #for mass single analysis
    write_results_table=False;store_n_e_atts=False;write_step_to_db=False
    '''select which network types to analyse'''
    lightrail = False; roads_national = False; roads_regional = False
    air = False; other = False; infrastructure = False
    er = False; gnm = False; ws = False; ba = False
    hra = False; hr = False; hc = False; tree = True
    noioa = 5   #number_of_iterations_of_analysis
    parameters = metrics,failure,handling_variables,result_file,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length,source_nodes_A,source_nodes_B

    if air== True:
        db = 'air'
        NETWORK_NAME, conn = network_data.air_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if lightrail == True:
        db = 'lightrail'
        NETWORK_NAME, conn = network_data.lightrail_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if roads_national == True:
        db = 'roads_national'
        NETWORK_NAME, conn = network_data.road_national_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)  
    if roads_regional== True:
        db = 'roads_regional'
        NETWORK_NAME, conn = network_data.road_regional_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if other== True:
        db = 'other'
        NETWORK_NAME, conn = network_data.other_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if infrastructure== True:
        db = 'infrastructure'
        NETWORK_NAME, conn = network_data.infra_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)            
    if er == True:
        db = 'er'
        NETWORK_NAME,conn = network_data.er_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if gnm == True:
        db = 'gnm'
        NETWORK_NAME, conn = network_data.gnm_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if ws == True:
        db = 'ws'
        NETWORK_NAME, conn = network_data.ws_networks()        
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if ba == True:
        db = 'ba'
        NETWORK_NAME, conn = network_data.ba_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if hra == True:
        db = 'hra'
        NETWORK_NAME, conn = network_data.hra_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if hr == True:
        db = 'hr'
        NETWORK_NAME, conn = network_data.hr_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if hc == True:
        db = 'hc'
        NETWORK_NAME, conn = network_data.hc_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    if tree == True:
        db = 'theoretic_networks_tree'
        NETWORK_NAME, conn = network_data.tree_networks()
        tools.analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_pgnet_location)
    else:
        print 'no networks selected'
else:
    print 'combination of parameters is not correct'