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