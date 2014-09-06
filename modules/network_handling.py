# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 12:11:59 2014

@author: a8243587

"""

#standard libraries
import networkx as nx

#specific modules
import error_classes


def check_node_removed(node, subnodes, isolated_nodes):
    '''Identify if a node has been removed from the network already, or if it is 
    still part of the network. Used by cascading failure model and 
    check_dependency_edges function'''
    #create required variables
    REMOVED = False    
    h = 0   
    #for all isoalted nodes, check if node is part of the list
    while h < len(isolated_nodes):
        p = 0
        while p < len(isolated_nodes[h]):
             if node == isolated_nodes[h][p]:
                    REMOVED = True
             p += 1
        h += 1
    return REMOVED
              
def remove_isolates(G,node_list,option,basic,to_b_nodes,from_a_nodes,a_to_b_edges,net):
    '''Removed any isolated nodes in the given network and any associated 
    edges. Retruns the eddited network and a number of lists which require 
    updating due to the removal.
    Input: 
    Return: '''
   
    #remove any isolated nodes and assocaited edges      
    isolatednodes = nx.isolates(G)
    if G.number_of_edges() == 0: 
        #print 'The number of nodes left is:', G.number_of_nodes()
        raise error_classes.GraphError('Error. The network is dissconnected, there are no edges left in the network.')
    else:
        #remove all nodes which are in the isolated list
        G.remove_nodes_from(isolatednodes) 
       
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
    
    tot = 0
    if net == 'B':
        for nd in isolatednodes:
            v = 0
            found = False
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
    #print 'RUNNING REMOVE_ISOLATES FROM',net,'. Number of ISOLATES removed:',len(isolatednodes),'(',isolatednodes,');','Dependency edges removed:', tot
    return G,node_list,basic,option,isolatednodes,to_b_nodes,from_a_nodes,a_to_b_edges
    
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
                REMOVED = check_node_removed(edge[1], optionB['subnodes'], optionB['isolated_nodes']) #check node in B is still there - it should be
                if not REMOVED: 
                    GtempB.remove_node(edge[1])
                    #print 'removing dependency edge (',a_to_b_edges[z],')'
                    #print 'removing node from B (',edge[1],')'
                    a_to_b_edges.pop(z)
                    nodes_removed_from_b.append(edge[1])
                    z-=1
                else: raise error_classes.SearchError('Error. Node has already been removed.')
            z += 1                
                 
    networks =  GA, GB, GtempA, GtempB
    args = networks,nodes_removed_from_b,basicA,basicB,optionA,optionB,to_b_nodes,from_a_nodes,a_to_b_edges
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

def whole_graph_av_path_length(Gtemp,length=''):
    'Calcualte the average path length the whole network when it is made up of many subgraphs. *This is outdated by easier methods within the code blocks themeselves.'
    #create the required varaibles
    number_of_components_used = 0 
    average = 0
    #calcualte the average path legnth for all subgraphs with more than one node
    for g in nx.connected_component_subgraphs(Gtemp):
        if nx.number_of_nodes(g) <= 1:
            pass
        else:
            average += nx.average_shortest_path_length(g,length)     
            number_of_components_used += 1            
    #calcualte the average if the average is greater than zero
    if average == 0:
        pass
    else:            
        average = average/number_of_components_used
    return average

