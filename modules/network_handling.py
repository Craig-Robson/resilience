# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 12:11:59 2014

@author: a8243587

"""

#standard libraries
import networkx as nx

#specific modules
import error_classes


def check_node_removed(node, isolated_nodes):
    '''Identify if a node has been removed from the network already, or if it is 
    still part of the network. Used by cascading failure model and 
    check_dependency_edges function'''
    #create required variables
    REMOVED = False
    h = 0   
    #for all isoalted nodes, check if node is part of the list
    try:
        while h < len(isolated_nodes):
            if type(isolated_nodes[h]) == int:
                if node == isolated_nodes[h]:
                        REMOVED = True
            else:
                p = 0
                print isolated_nodes[h]
                print type(isolated_nodes[h])
                while p < len(isolated_nodes[h]):
                     if node == isolated_nodes[h][p]:
                            REMOVED = True
                     p += 1
            h += 1
    except:
        return 4001
    return REMOVED
              
def remove_isolates(G,node_list,option,basic,to_b_nodes,from_a_nodes,a_to_b_edges,net):
    '''Removed any isolated nodes in the given network and any associated 
    edges. Retruns the eddited network and a number of lists which require 
    updating due to the removal.
    Input: 
    Return: '''
   
    #remove any isolated nodes and assocaited edges      
    try:
        isolatednodes = nx.isolates(G)
    except:
        return 4010
    if G.number_of_edges() == 0: 
        #print 'The number of nodes left is:', G.number_of_nodes()
        raise error_classes.GraphError('Error. The network is dissconnected, there are no edges left in the network.')
    else:
        #remove all nodes which are in the isolated list
        G.remove_nodes_from(isolatednodes) 
       
    j = 0
    #loop through the isolated nodes and remove from the node list
    try:
        while j < len(isolatednodes):
            k = 0 
            while k < len(node_list):
                if isolatednodes[j] == node_list[k]:
                    node_list.remove(node_list[k])
                    k -= 1
                k += 1
            j += 1
    except:
        return 4012

    #update some of the lists to record the simulation process
    
    tot = 0
    if net == 'B':
        for nd in isolatednodes:
            v = 0
            found = False
            try:
                while v < len(a_to_b_edges):
                    if int(nd) == int(a_to_b_edges[v][1]):
                        
                        a_to_b_edges.pop(v)
                        found = True
                        tot += 1
                        v -= 1
                        if found==False:
                            print 'node is:', nd
                            for item in a_to_b_edges:
                                print item[1]
                            exit()
                    v += 1
            except:
                return 4013
                
    var = G,node_list,basic,option,isolatednodes,to_b_nodes,from_a_nodes,a_to_b_edges
    return var 
    
def handle_sub_graphs(G):
    ''''Used for removing subgraphs from a network, but converting them to 
    node and edge lists so can be re-built for analysis purposes. Called from 
    analysis_B'''
    U_G = None
    if G.is_directed() == True:
        U_G = G.to_undirected()
    else: U_G = G
    
    try:
        subgraphlist = nx.connected_component_subgraphs(U_G) #create a list of subgraphs
    except:
        return 4020

    subnodes = [] #list of subnodes
    numofsubnodes = 0 #to store the number of subnodes in total at each iteration

    i = 0
    for g in subgraphlist:
        if i <> 0:
            subnodes.append(g.nodes())
            numofsubnodes+=g.number_of_nodes()
        i+=1
    G = subgraphlist[0]
    
    var = G, subnodes, numofsubnodes, G.nodes(),G.edges()
    return var

'''interdependency function'''
def check_dependency_edges(networks,nodes_to_check,basicA,basicB,optionA,optionB,to_b_nodes,from_a_nodes,a_to_b_edges,temp,INTERDEPENDENCY): 
    ''' 
    check to see if any interdependency edges have a to or from node which is 
    one of the nodes to be removed(damaged) 
    -if so, find the node at other end of the edge in network B
    -remove all edges connected to that node so that node can be removed and 
        full effect in network B modelled
    -remove that node
    -in analysis section need to check both networks for isolted nodes and sub graphs - why???
         -which produce more interdependency failures - when to stop checking????
         -could this be another method of analysis    
    ''' 
    GA, GB, GtempA, GtempB = networks   
    nodes_removed_from_b=[]
    #print 'Nodes in network A being removed:', nodes_to_check
    for node in nodes_to_check:
        z = 0
        while z < len(a_to_b_edges):
        #for edge in a_to_b_edges:
            edge = a_to_b_edges[z]
            if node == edge[0]:
                REMOVED = check_node_removed(edge[1], nx.isolates(GtempB)) #check node in B is still there - it should be                
                #REMOVED = check_node_removed(edge[1], optionB['subnodes'], optionB['isolated_nodes']) #check node in B is still there - it should be
                if type(REMOVED) == int:
                    return REMOVED
                elif not REMOVED: 
                    try:
                        GtempB.remove_node(edge[1])
                        a_to_b_edges.pop(z)
                        nodes_removed_from_b.append(edge[1])
                    except:
                        return 4030
                    z-=1
                else:
                    pass
                    #raise error_classes.SearchError('Error. Node has already been removed.')
            z += 1                
                 
    networks =  GA, GB, GtempA, GtempB
    var = networks,nodes_removed_from_b,basicA,basicB,optionA,optionB,to_b_nodes,from_a_nodes,a_to_b_edges
    return var

def clean_node_lists(subn,node_list, to_b_nodes, from_a_nodes):
        '''Clean the node lists which are needed for some forms of analysis. 
        Need to remove any nodes which have been removed from the network 
        already e.g. remove subgraphs. Called from analysis B only.
        Input: 
        Output:  '''
        j = 0
        #loop through all nodes in subgraphs and remove from the node list
        try:
            while j < len(subn):
                k = 0
                while k < len(node_list):
                    if subn[j] == node_list[k]:
                        try:
                            node_list.remove(node_list[k])
                        except:
                            return 4040
                        k -= 1
                    k += 1
                j += 1
        except:
            return 4042
            
        #remove from to and from lists where the dependency is broken as the to node has been removed as part of a subgraph
        try:
            v = 0
            while v < len(subn):
                vd = 0
                while vd < len(subn[v]): #double set of brackets for the subnodes, so double loop required
                    vf = 0
                    while vf < len(to_b_nodes):
                        if subn[v][vd] == to_b_nodes[vf]:
                            try:
                                to_b_nodes.pop(vf) #remove from the to list
                                from_a_nodes.pop(vf) #remove from the from list
                            except:
                                return 4041
                            vf-=1 #adjust vf so no value in list is missed
                        vf += 1
                    vd += 1
                v += 1
        except:
            return 4043
            
        var = node_list, to_b_nodes, from_a_nodes
        return var

def check_connected_to_source_nodes(Gtemp, source_nodes,nodes_removed):
    """
    Given a network and a list of source nodes, checks they are still connected
    to a source. If not they are removed from the network and recorded.
    """
    
    #check if any nodes are no longer connected to source nodes
    #loop through all nodes:origins
    for nd in Gtemp.nodes():
        connected = False
        for sn in source_nodes:
            #for each check path to a source
            try:
                if nx.has_path(Gtemp,nd,sn) == True:
                    #break if has_path returns True
                    connected = True
                    break
            except:
                return 4050
        #if false for all, then remove from network and add to removed list
        if connected == False:
            try:
                Gtemp.remove_node(nd) 
            except:
                return 4051
            nodes_removed.append(nd)
    var = Gtemp, nodes_removed
    return var


def whole_graph_av_path_length(Gtemp,length=''):
    'Calcualte the average path length the whole network when it is made up of many subgraphs. *This is outdated by easier methods within the code blocks themeselves.'
    #create the required varaibles
    number_of_components_used = 0 
    average = 0
    
    #calcualte the average path legnth for all subgraphs with more than one node
    try:
        for g in nx.connected_component_subgraphs(Gtemp):
            if nx.number_of_nodes(g) <= 1:
                pass
            else:
                try:
                    average += nx.average_shortest_path_length(g,length)     
                except:
                    return 4060
                number_of_components_used += 1
    except:
        return 4061
        
    #calcualte the average if the average is greater than zero
    if average == 0:
        pass
    else:            
        average = float(average)/number_of_components_used
    return average

