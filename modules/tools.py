# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 11:55:05 2014

@author: a8243587
"""
#standard libraries
import random
import datetime

#specific modules
import error_classes

def replace_all(text, dic):
    ''''''
    for i,j in dic.iteritems():
        text = text.replace(i,j)
    return text
    
def write_to_log_file(logfilepath,text):
    '''Writes to a file given a file path and a string of text. Also adds the 
    time to the output. Opens and closes the file to avoid the file being 
    locked during complex iteractions.
    Input: logfilepath, string of text
    Return: Nothing  '''
    #if a logfile is being used and the filepath has been specified
    if logfilepath == False or logfilepath == None:
        pass
    else:
        try:
            #open the logfile, print the time and the string sent
            logfile = open(logfilepath,'a')
            logfile.write(str(datetime.time) + ',\t' + str(text))
            logfile.close()
        except:
            #if the logfile could not be opened
            raise error_classes.WriteError('Write Error. Could not write to log file.')

def failure_type(failure_dict):
    '''Generates a string describing the analysis being run.
    Input: analysis parameters
    Returns: a single string'''
    if failure_dict['single'] == True: failure = 'Single'
    elif failure_dict['sequential'] == True: failure = 'Sequential'
    elif failure_dict['cascading'] == True: failure = 'Cascading' 
    
    if failure_dict['random'] == True: typ = 'Random'
    elif failure_dict['degree'] == True: typ = 'Degree'
    elif failure_dict['betweenness'] == True: typ = 'Betweenness'
    #add togetehr to create a single string
    failuretype = '%s_%s' % (failure, typ)
    return failuretype

def max_val_random(value_list):
    '''Find the maximum value in a list, and if tied between two or more 
    values, randomly select one of the ties values. In the special case of 
    betweenness centrality being used, all entires may be zero as they as 
    isolated or in pairs, thus a node is also selected at random here as well.
    Input: a list
    Return: maximum value and the entry (chosen) with that value '''
    #set the necasary variables and create an empty list
    ma = -99999 #will store the maximum value
    node = -99999 #will store the node (number) with the maximum value
    tie_list = [] #use to store any nodes which shre the maximum value
    node_iterator = 0 #counts how many node have been selected
    list_iterator = 0 

    #loop through the whole list
    while node_iterator < len(value_list):
            try:
                if value_list[list_iterator] > ma:
                    #if the value is higher than the max value already
                    #reset the tie list
                    tie_list = []
                    #add the value to the tie_list in case another one with the same value is found
                    tie_list.append(list_iterator)
                    ma = value_list[list_iterator]
                    node = list_iterator
                elif value_list[list_iterator] == ma:
                    #if the value is the same as the current max value, add to the tie list
                    tie_list.append(list_iterator)
                else:
                    pass
                node_iterator += 1
            except:
                #pass as no node with this value
                pass
            list_iterator += 1
            
    #if there is more than one node in the tie list, pick one at random            
    if len(tie_list) > 0:
        node = random.choice(tie_list)
        return ma, node
    else:
        raise error_classes.GeneralError('Error. No node was found with a value greater than -99999.')

def get_nodes_edges_csv(location):
    '''This allows a network to be loaded from a csv file. 
    Input: a valid file path.
    Returns: list of nodes and a list of edges directly compatable with the 
            netwrokx graph class.'''
            
    #open the specified text file
    text = open(location).read()
    #split the text in the file on the new line
    text1, text2 = text.split('\n')
    node_list = []
    edge_list = []
    #clean the string text2
    text2 = replace_all(text2, {' ':'','[':'',']':'',')':'','(':''})
    #create a list from text2 by spliiting on the commas
    text2 = text2.split(',')
    #iterate through the list, adding each to a node list as integers
    for item in text2:
        item = int(item)
        node_list.append(item)
    #clean string text one and split on a bracket
    text1 = replace_all(text1, {')':'',']':'','[':'',' ':''})
    text1 = text1.split('(')
    #for the items in the list create a set of edges    
    for item in text1: 
        if item == "":
            item = item
        else:
            #split each item on the comma
            item = item.split(',')
            templist = []
            #iterate through each pair of nodes, convert to an integer and add to th edge list as an edge
            for each in item:
                if each == "":
                    each = each                              
                else:
                    each = int(each)
                    templist.append(each)
            edge_list.append(templist) 

    return node_list, edge_list

def add_node_field(G,field_name,data=None):
    if field_name == 'id_':
        index=0
        for node in G.nodes():
            G.node[node][field_name]=index
            index+=1
    else:
        for key in data:
            G.node[key][field_name]=data[key]
    return G

def add_edge_field(G,field_name,data=None):
    if data <> None:
        for key in data:
            G.edge[key[0]][key[1]][field_name]=data[key]
    return G

def analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath, nx_location):
    ''''''
    import ogr, sys, tools
    sys.path.append()
    import nx_pgnet
    import networkx as nx
    import interdependency_analysis as ia
    #unpack varaibles
    metrics,failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length = parameters
    failuretype = failure_type(failure)
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
                    filepath = str(fileName)+'%s/%s.txt' %(db, nets)
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
            filepath = str(fileName)+'%s/%s.txt' %(db, NETWORK_NAME[0])
            nodelist, edgelist = tools.get_nodes_edges_csv(filepath)
            G1 = nx.Graph()
            G1.add_nodes_from(nodelist)
            G1.add_edges_from(edgelist)
            filepath = str(fileName)+'%s/%s.txt' %(db, NETWORK_NAME[1])
            nodelist, edgelist = tools.get_nodes_edges_csv(filepath)
            G2 = nx.Graph()
            G2.add_nodes_from(nodelist)
            G2.add_edges_from(edgelist)
        ia.main(G1, G2, parameters,logfilepath)
    else:
        raise error_classes.GeneralError('Error. The STAND_ALONE variable must have a boolean value')
        
        
def set_basic_parameters(failure):
    #------------------compile metrics into variables--------------------------
    basic_metrics_A = {'nodes_removed':True,'no_of_nodes_removed':True,'no_of_nodes':True,
                   'no_of_edges':True,'no_of_components':True,
                   'no_of_isolated_nodes':True,'isolated_nodes_removed':True,
                   'nodes_selected_to_fail':True}
    option_metrics_A = {'size_of_components':       True,
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
    
    return metrics
    
def set_failure_dict(analysis_type,failure_type,selection_type): 
    '''
    Takes three inputs (strings):
        analysis_type: stand_alone, dependency, interdependency
        failure_type: single, sequential, cascading
        selection_type: random, degree, betweenness
    '''
    failure = {}
    if analysis_type == 'stand_alone':
        failure['stand_alone']=True
        failure['dependency']=False
        failure['interdependency']=False
    elif analysis_type == 'dependency':
        failure['stand_alone']=False
        failure['dependency']=True
        failure['interdependency']=False
    elif analysis_type == 'interdependency':
        failure['stand_alone']=False
        failure['dependency']=False
        failure['interdependency']=True
    else:
         raise error_classes.GeneralError('Error. Could not assign the analysis_type %s to one of the available methods.' %analysis_type)
    if failure_type == 'single':
        failure['single']=True
        failure['sequential']=False
        failure['cascading']=False
    elif failure_type == 'sequential':
        failure['single']=False
        failure['sequential']=True
        failure['cascading']=False
    elif failure_type == 'cascading':
        failure['single']=False
        failure['sequential']=False
        failure['cascading']=True
    else:
        raise error_classes.GeneralError('Error. Could not assign the failure_type %s to one of the available methods.' %failure_type)
    if selection_type == 'random':
        failure['random']=True
        failure['degree']=False
        failure['betweenness']=False
        failure['from_list']=False
        failure['flow']=False
    elif selection_type == 'degree':
        failure['random']=False
        failure['degree']=True
        failure['betweenness']=False
        failure['from_list']=False
        failure['flow']=False
    elif selection_type == 'betweenness':
        failure['random']=False
        failure['degree']=False
        failure['betweenness']=True
        failure['from_list']=False
        failure['flow']=False
    elif selection_type == 'from_list':
        failure['random']=False
        failure['degree']=False
        failure['betweenness']=False
        failure['from_list']=True
        failure['flow']=False
    elif selection_type == 'flow':
        failure['random']=False
        failure['degree']=False
        failure['betweenness']=False
        failure['from_list']=False
        failure['flow']=True
    else:
        raise error_classes.GeneralError('Error. Could not assign the selection_type %s to one of the available methods.' %selection_type)
    
    return failure        
        
def default_handling_variables():
    
    handling_variables = {'remove_subgraphs':True,'remove_isolates':False,'no_isolates':False}  

    return handling_variables
    
def check_inputs(failure):
    
    count = 0
    selection_types = ['flow','random','degree','betweenness','from_list']
    for key in failure.keys():
        for option in selection_types:
            if option == key and failure[key]==True: count +=1
    if count == 0:
        raise error_classes.InputError('Error. None of the selection types were set as True. At least one should be.')
    elif count > 1:
        raise error_classes.InputError('Error. Only one of the selection types should be True.')      
    
    count = 0
    failure_types = ['single','sequential','cascading']
    for key in failure.keys():
        for option in failure_types:
            if option == key and failure[key] == True: count +=1
    if count == 0:
        raise error_classes.InputError('Error. None of the failure types were set as True. At least one should be.')
    elif count > 1:
        raise error_classes.InputError('Error. Only one of the failure types should be True.')
    
    count = 0
    analysis_types = ['stand_alone','dependency','interdependency']
    for key in failure.keys():
        for option in analysis_types:
            if option == key and failure[key] == True: count +=1
    if count == 0:
        raise error_classes.InputError('Error. None of the analysis types were set as True. At least one should be.')
    elif count > 1:
        raise error_classes.InputError('Error. Only one of the analysis types should be True.')
    
    
        