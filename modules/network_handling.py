# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 12:11:59 2014

@author: a8243587
"""

#standard libraries
import networkx as nx

#specific modules
import error_classes


def remove_edges(G,nde,INTERDEPENDENCY):
    '''Removes the edges from the input network where they involve the input 
    node.
    Input: network, the node removed, INTERDEPENDENCY variable
    Return: network '''
    #if perforing single of dependency analysis
    if INTERDEPENDENCY == False:    
        i = 0
        edgelist = G.edges()
        #loop throught he edge list, and if an edge using the removed node is found, remove it
        while i < len(edgelist):
            origin,dest = edgelist[i]
            if origin == nde and origin <> dest:
                G.remove_edge(origin,dest)
            if dest == nde and origin <> dest:
                G.remove_edge(origin,dest)
            i += 1
    #if performing interdependcy analysis
    elif INTERDEPENDENCY == True:
        #get the edges belonging to the node
        nde_edges = G.edges(nde)
        i = 0  
        #remoce all edge which involve the node
        while i < len(nde_edges):
            origin,dest = nde_edges[i] 
            G.remove_edge(origin,dest)      
            i += 1
    return G

def check_node_removed(node, subnodes, isolated_nodes):
    '''Identify if a node has been removed from the network already, or if it is 
    still part of the network. Used by cascading failure model and 
    check_dependency_edges function'''
    #create required variables
    REMOVED = False    
    h = 0
    print 'errors here'
    print isolated_nodes    
    #for all isoalted nodes, check if node is part of the list
    while h < len(isolated_nodes):
        p = 0
        while p < len(isolated_nodes[h]):
             if node == isolated_nodes[h][p]:
                    REMOVED = True
             p += 1
        h += 1
    return REMOVED
        
#do not want to remove isolates at the moment    
def handle_isolates(G): #remove isolated nodes 
    '''Removes any isolated nodes. Returns the adjusted network and 
    the list of nodes removed.
    Input: network
    Return: network, isolated nodes''' 
    #create list of isolated nodes
    isolatednodes = nx.isolates(G)
    #if there are no edges in the network, then all nodes are isolates
    if G.number_of_edges() == 0: 
        raise error_classes.GraphError('Error. The network is dissconnected, there are no edges left in the network.')
    else:
        #remove all nodes which are in the isolated list
        G.remove_nodes_from(isolatednodes) 
    return G,isolatednodes
        
def remove_isolates(Gtemp,node_list,isolated_nodes,isolated_n_count_removed,node_count_removed,to_b_nodes,from_a_nodes):
    '''Removed any isolated nodes in the given network and any associated 
    edges. Retruns the eddited network and a number of lists which require 
    updating due to the removal.
    Input: 
    Return: '''
    #remove any isolated nodes and assocaited edges
    Gtemp, isolatednodes = handle_isolates(Gtemp)       
        
    j = 0
    #loop through the isolated nodes and remove from the node list
    while j < len(isolatednodes):
        k = 0 
        while k < len(node_list):
            if isolatednodes[j] == node_list[k]:
                node_list.remove(node_list[k])
                k -= 1
            k += 1
        j += 1
    
    #update some of the lists to record the simulation process
    isolated_nodes.append(isolatednodes)  
    isolated_n_count_removed.append(len(isolatednodes))
    node_count_removed.append(node_count_removed.pop()+len(isolatednodes))
    
    #remove from to and from lists where the dependence link is now invalid as to node removed as isolated
    v = 0
    while v < len(isolatednodes):
        vf = 0
        while vf < len(to_b_nodes):
            if isolatednodes[v] == to_b_nodes[vf]:
                to_b_nodes.pop(vf) #remove from the to list
                from_a_nodes.pop(vf) #remove from the from list
                vf -= 1
            vf += 1
        v += 1       
             
    return Gtemp,node_list,isolated_nodes,isolated_n_count_removed,node_count_removed,to_b_nodes,from_a_nodes

def handle_sub_graphs(nodelists, edgelists):
    ''''Used for removing subgraphs from a network, but converting them to 
    node and edge lists so can be re-built for analysis purposes. Called from 
    analysis_B'''
    #build network from node and edge lists,identify any new subgraphs, and store all graphs as node and edge lists
    G = nx.Graph()
    G.add_nodes_from(nodelists)    
    G.add_edges_from(edgelists)
    subgraphlist = nx.connected_component_subgraphs(G) #create a list of subgraphs

    subnodesinA = [] #list of subnodes
    numofsubnodes = 0 #to store the number of subnodes in total at each iteration
    newedgelist = [] #new list to store the edges for each subgraph
    newnodelist = [] #new list to store the nodes for each subgraph

    i = 0    
    #for all nodes in the subgraph list, update the output lists
    while i < len(subgraphlist): 
        subgraph = subgraphlist[i]
        newnodelist.append(subgraph.nodes()) 
        newedgelist.append(subgraph.edges()) 
        subnodesinA.append(subgraph.nodes())
        numofsubnodes += subgraph.number_of_nodes() #add up the number of nodes in the subgrahs during this wider iteration
        i += 1
    
    return G, subnodesinA, numofsubnodes,newnodelist,newedgelist

#to change the handling of subgraphs:
#use lists to store node and edge lists, then build each network as required- means it will run much slower I believe
#for the sub graph function - identify sub graphs and add the node and egde lists to two new lists - list must be re-created on each analysis iteration to keep everything up to date
#instead of passing the single network(G), need to pass the two lists to all functions
#for all other functions loop thorugh them to go thrugh the lists of graphs - easier than trying to create and handle multiple networks at once
#also need to add the new outputs - average across all subgraphs,average for each subgraph, size of each subgraph - to be confirmed by Stuart


'''interdependency function'''
def check_dependency_edges(networks,node,basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B,to_b_nodes,from_a_nodes,temp): 
    ''' 
    check to see if any interdependency edges have a to or from node which is 
    one of the nods to be removed(damaged) 
    -if so, find the node at other end of the edge in network B
    -remove all edges connected to that node so that node can be removed and 
        full effect in network B modelled
    -remove that node
    -in analysis section need to check both networks for isolted nodes and sub graphs - why???
         -which produce more interdependency failures - when to stop checking????
         -could this be another method of analysis    
    ''' 
    GA, GB, GtempA, GtempB = networks
    nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A,isolated_n_count_A = basic_metrics_A
    nodes_removed_B,node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B,isolated_n_count_B = basic_metrics_B
    size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,inter_removed_count_A = option_metrics_A
    size_of_components_B,giant_component_size_B,av_nodes_in_components_B,isolated_nodes_B,isolated_n_count_removed_B,subnodes_B,subnodes_count_B,path_length_B,av_path_length_components_B,giant_component_av_path_length_B,av_path_length_geo_B,average_degree_B,inter_removed_count_B = option_metrics_B
    print 'before B is affected:'    
    print 'node of interest is:', node
    INTERDEPENDENCY = False   
    print 'A nodes:'
    print GtempA.nodes()
    print 'B ndoes:'
    print GtempB.nodes()
    print GB.nodes()
    print 'FROM A nodes:'
    print from_a_nodes
    print to_b_nodes
    
    i=0
    while i < len(from_a_nodes): #for the length of a node list
        if node == from_a_nodes[i]: #if the removed value coresponds to a from node in the interdependency edges
            tnode = to_b_nodes[i] #get the to node at the other end of the dependency edge                                                     
            #check node has not been removed through being isolated or member of a subgraph            
            REMOVED = check_node_removed(tnode, subnodes_B, isolated_nodes_B) 
            #if node still in network
            if REMOVED == False:
                #remove all edges which feature the to node
                GtempB = remove_edges(GtempB,tnode,INTERDEPENDENCY) 
                try:                
                    GtempB.remove_node(tnode) #remove the to node
                except:
                    raise error_classes.SearchError('Error. Could not find the node in the network.')
                    error = 0001
                    return error
                #add node to required metrics/counts
                node_count_removed_B.append(node_count_removed_B.pop()+1)             
                inter_removed_count_B.append(inter_removed_count_B.pop()+1)
                temp.append(tnode) 
                to_b_nodes.pop(i) 
                from_a_nodes.pop(i) 
                #edit i so no list items are mised 
                i -= 1  
            elif REMOVED == True: 
                #if node has already been removed in another process
                raise error_classes.SearchError('Error. Node has already been removed.')
        i += 1
    networks =  GA, GB, GtempA, GtempB
    basic_metrics_A = nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A,isolated_n_count_A
    basic_metrics_B = nodes_removed_B,node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B,isolated_n_count_B
    option_metrics_A = size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,inter_removed_count_A
    option_metrics_B = size_of_components_B,giant_component_size_B,av_nodes_in_components_B,isolated_nodes_B,isolated_n_count_removed_B,subnodes_B,subnodes_count_B,path_length_B,av_path_length_components_B,giant_component_av_path_length_B,av_path_length_geo_B,average_degree_B,inter_removed_count_B
    args = networks,node,basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B,to_b_nodes,from_a_nodes,temp    
    return args

def clean_node_lists(subn,node_list, to_b_nodes, from_a_nodes):
        '''Clean the node lists which are needed for some forms of analysis. 
        Need to remove any nodes which have been removed from the network 
        already e.g. remove subgraphs. Called from analysis B only.
        Input: 
        Output:  '''
        j = 0
        #loop through all nodes in subgraphs and remove from the node list
        while j < len(subn):
            k = 0
            while k < len(node_list):
                if subn[j] == node_list[k]:
                    node_list.remove(node_list[k])
                    k -= 1
                k += 1
            j += 1
            
        #remove from to and from lists where the dependency is broken as the to node has been removed as part of a subgraph
        v = 0
        while v < len(subn):
            vd = 0
            while vd < len(subn[v]): #double set of brackets for the subnodes, so double loop required
                vf = 0
                while vf < len(to_b_nodes):
                    if subn[v][vd] == to_b_nodes[vf]:
                        to_b_nodes.pop(vf) #remove from the to list
                        from_a_nodes.pop(vf) #remove from the from list
                        vf-=1 #adjust vf so no value in list is missed
                    vf += 1
                vd += 1
            v += 1
        return node_list, to_b_nodes, from_a_nodes

def whole_graph_av_path_length(Gtemp):
    'Calcualte the average path length the whole network when it is made up of many subgraphs. *This is outdated by easier methods within the code blocks themeselves.'
    #create the required varaibles
    number_of_components_used = 0 
    average = 0
    #calcualte the average path legnth for all subgraphs with more than one node
    for g in nx.connected_component_subgraphs(Gtemp):
        if nx.number_of_nodes(g) <= 1:
            pass
        else:
            average += nx.average_shortest_path_length(g)                 
            number_of_components_used += 1            
    #calcualte the average if the average is greater than zero
    if average == 0:
        pass
    else:            
        average = average/number_of_components_used
    return average

