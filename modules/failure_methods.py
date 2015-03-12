# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 12:09:21 2014

@author: a8243587

"""


#standard libraries
import random
import networkx as nx

#specific modules
import error_classes,tools,network_handling


'''sequential failures'''
def sequential_degree(G,INTERDEPENDENCY): #formally cascading
    '''Code to perform the sequential analysis where the node to be removed is 
    selected via that with the highest degree.
    Input: a network, INTERDEPENDENCY variable
    Return: a network, the node removed '''
    #get the node and with the maximum value from the network
    degree, node = tools.max_val_random(nx.degree(G))
    #if the returned node is -99999, then there is an error
    if node == -99999:
        #check to see if the number of edges in the network is greater than 0
        if G.number_of_edges() > 0: 
            raise error_classes.GeneralError('There are %s edge on the network. An unknown error has occred.' %(G.number_of_edges()))
        else:  
            raise error_classes.CalculationError('There are no edges in the network, thus no values could be computed.')
    else: 
        #remove the edges realted to the node - networkx does this automatically when you remove the node I think
        #remove the node from the network
        G.remove_node(node) #remove the node
    #return the editied network and the node removed
    return G,node

def sequential_betweenness(G,INTERDEPENDENCY): 
    '''Sequential analysis where the node to be removed on each iteration is 
    that with the highest betweenness centrality value.
    Input: a network, INTERDEPENDENCY variable
    Return: a network, the node removed'''
    #find the node with the max betweenness value in the network
    betweenness_value, node = tools.max_val_random(nx.betweenness_centrality(G))
    
    #if the node has the value of an error
    if node == -99999:
        raise error_classes.GeneralError('Error. An error occured when calcualting the node to remove.')
    else:
        #remove all edges which feature the node and then the node
        G.remove_node(node) 
    #return the eddited network and the node remvoed
    return G,node
    
def sequential_random(G, NO_ISOLATES, INTERDEPENDENCY):
    '''Sequential anlysis method where the node to be removed is selcted 
    randomly from those still in the network.
    Input: a network, NO_ISOLATES varaible, INTERDEPENDENCY variable
    Return: a network, the node removed'''
    #choose a node at random from the network node list
    node = random.choice(G.nodes()) 
    #if isolates are not to be removed as a selected node
    if NO_ISOLATES==True:
        #randomly select a node until one is found with a degree of one at least
        while nx.degree(G, node) == 0: 
            node = random.choice(G.nodes())
    #remove the edge assocaiated with the node and then the node
    G.remove_node(node)
    #return the network and the node which was removed
    return G,node

def sequential_flow(G, NO_ISOLATES, INTERDEPENDENCY):
    '''Sequential anlysis method where the node to be removed is selcted 
    via having the highest flow value.
    Input: a network, NO_ISOLATES varaible, INTERDEPENDENCY variable
    Return: a network, the node removed'''
    
    flow_dict = {}
    for nd in G.nodes():
        flow_dict[nd]=G.node[nd]['flow']
        
    value, node = tools.max_val_random(flow_dict)  
    
    #if the node has the value of an error
    if node == -99999:
        raise error_classes.GeneralError('Error. An error occured when calcualting the node to remove.')
    else:
        #remove all edges which feature the node and then the node
        G.remove_node(node) 
    #return the eddited network and the node removed

    return G, node
    
def sequential_from_list(G,INTERDEPENDENCY,fail_list,i):
    '''
    '''
    node = fail_list[i]
    G.remove_node(node)
    return G, node
    
def cascading_failure(G, dlist, dead,k,subnodes_A, isolated_nodes_A, removed_nodes,INTERDEPENDENCY): #start node chosen at random  #take out all neighbors
    '''Sequential failure code where all the neighbours of the node(s) removed
    on the previuos iteration are remvoed. This is intiated with a node 
    selected at random.
    Input: a network, deadlist, dead, k, subnodes,isolated nodes, removed nodes, INTERDEPENDENCY variable
    Return: a network, deadlist removed nodes, node removed'''
    #create empty container for nodes which have been removed  
    deadlist = []
    nlist = []
    #this only needs to happen on the first iteration
    if k ==0:
        #append the list of 'dead' nodes to create the useable list - as deifned by the user
        deadlist.append(dead) 
    else:
        #deadlist is the dlist, created on previuos iteration, containing the vulnerable nodes
        deadlist = dlist 
    #loop through the list of nodes to remove
    i = 0
    while i < len(deadlist):
        node = deadlist[i]
        #to avoid errors, check if the node has been removed yet due to being in a subgraph or an isolated node
        REMOVED =network_handling.check_node_removed(node, subnodes_A, isolated_nodes_A) 
        #if the node has been removed from the network
        if REMOVED == True:
            #remove from deadlist as not needed anynmore and may cause errors if left in
            deadlist.remove(deadlist[i])
            #list is now shorter to subtract one so i stays the same and no values are missed
            i -= 1 
        #if the node is still in the list
        elif REMOVED == False: 
            #count the number of times the node appears in the removed nodes list
            count = removed_nodes.count(node) 
            if count > 0: 
                #remove from deadlist to avoid any errors later
                deadlist.remove(deadlist[i])    
                i -= 1
            else:
                #create a list of all neigbours to the node
                neighbours_list = G.neighbors(node) 
                y = 0
                while y<len(neighbours_list):
                    fnode = neighbours_list[y] 
                    nlist.append(fnode)
                    y += 1
                #remove the edges and the node
                G.remove_node(node)
                removed_nodes.append(node) #
        i += 1
    #update the lists for the next iteration
    dlist = nlist
    node = deadlist
    return G,dlist,removed_nodes,node

'''single isolaterd failures'''    
def single_random(G,node_list, INTERDEPENDENCY):
    '''Analysis by removeing only one node for each iteration, where the nodes 
    are selected at random.
    Input: network, list of nodes, INTERDEPENDENCY variable
    Return: network, node removed '''
    #if there are no nodes in the network
    if len(node_list) < 1:
        raise error_classes.GraphError('Error. No nodes to choose from for the node to remove.')
    #choose a node at random from the graph node list
    node = random.choice(node_list) 
    #use Gtemp as need to reset G to its original state for the next iteration
    Gtemp = G
    Gtemp.remove_node(node)
    #need to keep track of the nodes removed, hence a list
    node_list.remove(node)
    return Gtemp,node      
    
'''Failure via shapefile'''
def geo_failure(G,shp_file):
    '''Given a shapefile, identifies those nodes within the failure zone.'''
    
    print 'THIS NEEDS UPDATING'
    import shapefile
    coords = []
    sf = shapefile.Reader(shp_file)
    shapes = sf.shapes()
    for shape in shapes:
        for p in  shape.points:
            coords.append(p)    
    polygon = coords  
    #get list of node        
    list_of_nodes = G.nodes()
    #loop through list of nodes
    Gtemp = G
    for nde in list_of_nodes:
        #see if node inside polygon
        inside = point_in_poly(nde,polygon)
        #if inside polygon
        if inside == True:
            #remove node and edges from network
            Gtemp = network_handling.remove_edges(Gtemp, nde, INTERDEPENDENCY=False)
            Gtemp.remove_node(nde)
            
    
def point_in_poly(coord,poly):
    '''Point in polygon.'''
    x,y = coord
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside    
    
    pass