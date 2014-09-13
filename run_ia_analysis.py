# -*- coding: utf-8 -*-
"""
Created on Wed Apr 02 08:23:20 2014

@author: a8243587

"""
#import python modules
import networkx as nx
import ogr, sys

#import resilience module
import interdependency_analysis as ia

#import nx_pgnet module
sys.path.append("C:/a8243587_DATA/GitRepo/nx_pgnet")
sys.path.append("C:/Users/Craig/GitRepo/nx_pgnet")
import nx_pgnet

#import subsidiary resilience modules
sys.path.append("C:/a8243587_DATA/GitRepo/resilience/resilience_modules")
import tools, error_classes

def analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath):
    ''''''
    #unpack varaibles
    metrics,failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length = parameters

    #if performing analysis on one network only    
    if failure['stand_alone'] == True:
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
                fileName = str(fileName)+'%s/%s%s.txt'%(db,nets,failuretype)
                #package the parameters together
                parameters = metrics,failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length = parameters
                #need a value for network B (G2)
                G2 = None
                #perform the analusis
                ia.main(G, G2, parameters, logfilepath)
                iterations += 1
                
    #if dependency or intersedpendcy
    elif failure['stand_alone'] == False:
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


failure = {'stand_alone':True, 'dependency':False, 'interdependency':False,
        'single':False, 'sequential':True, 'cascading':False,
        'random':False, 'degree':False, 'betweenness':True}

#------------------analysis parameters-------------------------------------
#REMOVE_SUBGRAPHS: When subgraphs appear, delete from network
#REMOVE_ISOLATES: When isolated nodes appear, delete from network
#NO_ISOLATES: Allow isolated nodes to be removed in the selection methods
handling_variables = {'remove_subgraphs':False,'remove_isolates':True,'no_isolates':False}  

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
dbname = 'testing'

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
    a_to_b_edges = [(3,1),(3,2),(5,3)]
    #fromSQL='SELECT "p" FROM "Inter_Lines"
    #toSQL='SELECT "t" FROM "Inter_Lines"
    if failure['interdependency'] == True:
        b_to_a_edges = []
else:
    a_to_b_edges = None  

#------------------compile metrics into variables--------------------------
basic_metrics_A = {'nodes_removed':True,'no_of_nodes_removed':True,'no_of_nodes':True,
                   'no_of_edges':True,'no_of_components':True,
                   'no_of_isolated_nodes':True,'isolated_nodes_removed':True,}
option_metrics_A = {'size_of_components':           False,
                    'giant_component_size':         False,
                    'avg_size_of_components':       False,
                    'isolated_nodes':               False,
                    'no_of_isolated_nodes_removed': False,
                    'subnodes':                     False,
                    'no_of_subnodes':               False,
                    'avg_path_length':              False,
                    'avg_path_length_of_components':False,
                    'avg_path_length_of_giant_component':   False,
                    'avg_geo_path_length':                  False,
                    'avg_geo_path_length_of_components':    False,
                    'avg_geo_path_length_of_giant_component':False,
                    'avg_degree':                   False,
                    'no_of_inter_removed':          False,
                    'density':                      False,
                    'maximum_betweenness_centrality':False,
                    'avg_betweenness_centrality':   False,
                    'assortativity_coefficient':    False,
                    'clustering_coefficient':       True,
                    'transitivity':                 True,
                    'square_clustering':            True,
                    'avg_neighbor_connectivity':    False,
                    'avg_degree_connectivity':      False,
                    'avg_degree_centrality':        False,
                    'avg_closeness_centrality':     False,
                    'diameter':                     False
                    }

if failure['stand_alone'] == False:
    basic_metrics_B = basic_metrics_A.copy()
    option_metrics_B = option_metrics_A.copy()
else: basic_metrics_B = None; option_metrics_B = None
metrics = basic_metrics_A, basic_metrics_B, option_metrics_A, option_metrics_B  

#------------------option to set the attribute which contins the length of the edges
if option_metrics_A['avg_geo_path_length'] <> False: length = 'shape_leng'
else: length = None

#------------------file names for csv based analysis-------------------------
file_1_name = 'dependencey_test_n1'
file_2_name = 'dependencey_test_n2'   

#------------------run some checks-----------------------------------------
if failure['interdependency']==True: print 'This functionality is not currently available.'; exit()
if failure['cascading']==True: print 'WARNING! This functionality has not been tested fully yet.'

#------------------analysis methods----------------------------------------
if use_nx_single == True:
    write_results_table=False;store_n_e_atts=False;write_step_to_db=False
    parameters = metrics,failure,handling_variables,result_file,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length
    complete = ia.main(GA, GB, parameters,logfilepath)
elif use_csv == True:
    write_results_table=False;store_n_e_atts=False;write_step_to_db=False
    parameters = metrics,failure,handling_variables,result_file,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length
    NETWORK_NAME = file_1_name, file_2_name #list the name of the two networks for the analysis
    conn = None; noia = 1
    ia.analyse_existing_networks(NETWORK_NAME,conn,dbname,parameters,noia,use_db,use_csv)
elif use_db == True:
    parameters = metrics,failure,handling_variables,result_file,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length
    complete = ia.main(GA, GB, parameters,logfilepath)
elif mass == True and failure['stand_alone'] == True: #for mass single analysis
    print 'where mass = True and Stand_alone = true'
    write_results_table=False;store_n_e_atts=False;write_step_to_db=False
    '''select which network types to analyse'''
    lightrail = False; roads_national = False; roads_regional = False
    air = False; other = False; infrastructure = False
    er = False; gnm = False; ws = False; ba = False
    hra = False; hr = False; hc = False; tree = True
    
    noioa = 5   #number_of_iterations_of_analysis
    parameters = metrics,failure,handling_variables,result_file,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length

    if air== True:
        db = 'air'
        NETWORK_NAME, conn = network_data.air_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if lightrail == True:
        db = 'lightrail'
        NETWORK_NAME, conn = network_data.lightrail_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if roads_national == True:
        db = 'roads_national'
        NETWORK_NAME, conn = network_data.road_national_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)       
    if roads_regional== True:
        db = 'roads_regional'
        NETWORK_NAME, conn = network_data.road_regional_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if other== True:
        db = 'other'
        NETWORK_NAME, conn = network_data.other_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if infrastructure== True:
        db = 'infrastructure'
        NETWORK_NAME, conn = network_data.infra_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)            
    if er == True:
        db = 'er'
        NETWORK_NAME,conn = network_data.er_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if gnm == True:
        db = 'gnm'
        NETWORK_NAME, conn = network_data.gnm_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if ws == True:
        db = 'ws'
        NETWORK_NAME, conn = network_data.ws_networks()        
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if ba == True:
        db = 'ba'
        NETWORK_NAME, conn = network_data.ba_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if hra == True:
        db = 'hra'
        NETWORK_NAME, conn = network_data.hra_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if hr == True:
        db = 'hr'
        NETWORK_NAME, conn = network_data.hr_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if hc == True:
        db = 'hc'
        NETWORK_NAME, conn = network_data.hc_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    if tree == True:
        db = 'theoretic_networks_tree'
        NETWORK_NAME, conn = network_data.tree_networks()
        analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath)
    else:
        print 'no networks selected'
else:
    print 'combination of parameters is not correct'