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

def create_dict_of_removals(G,failures_to_occur,node_to_fail_list,method):
    '''
    Creates a dict of nodes which are the x highest with the value left in the network. Can use a number of methods which must be entered in the function.
    '''

    if method == 'betweenness':
        blist = nx.betweenness_centrality(G)
    elif method == 'degree':
        blist = nx.degree(G)
    elif method == 'clustering':
        blist = nx.clustering(G)

    for key in blist.keys():
        if len(node_to_fail_list) > 0:
            min_val = min(node_to_fail_list.values())

        if len(node_to_fail_list) < failures_to_occur:
            node_to_fail_list[key] = blist[key]
        elif blist[key] > min_val:

            #remove min val
            for key1 in blist.keys():
                if blist[key1] == min_val:
                    del node_to_fail_list[key1]
                    break
            #add new val
            node_to_fail_list[key] = blist[key]

    return node_to_fail_list

def sequential_by_list(G,failures_to_occur,node_to_fail_list,method):
    '''
    Runs the sequential by list method. Takes parameters and method for node selection and uses/generates a list of nodes to remove. Removes the node with the greatest value.
    '''
    #if fewer nodes in the network than wanted for list reduce request
    if G.number_of_nodes() < failures_to_occur:
        failures_to_occur = G.number_of_nodes()

    #if list has no nodes in, build list
    if len(node_to_fail_list) == 0 or node_to_fail_list == {}:
        node_to_fail_list = create_dict_of_removals(G,failures_to_occur,node_to_fail_list,method)
    node = -99999

    if len(node_to_fail_list) != 0:
        use_next = True
        while use_next == True:
            # if the list becomes zero while trying to remove a node
            if len(node_to_fail_list) == 0:
                node_to_fail_list = create_dict_of_removals(G,failures_to_occur,node_to_fail_list,method)
            #get node with the max value and delete from the list
            max_val = max(node_to_fail_list.values())
            for key in node_to_fail_list.keys():
                if node_to_fail_list[key] == max_val:
                    node = key
                    break
            if node == -99999:
                print('Did not find node to remove')
                exit()
            del node_to_fail_list[key]
            # check node still in network - it may have been removed eg. isolated
            try:
                G.node[node]
                use_next = False
            except:
                use_next = True

    #if the node has the value of an error
    if node == -99999:

        raise error_classes.GeneralError('Error. An error occured when calculating the node to remove.')
        return 3011
    else:
        #remove all edges and the node
        try:
            G.remove_node(node)
        except:
            return 3012

    #return the eddited network and the node remvoed
    var = G, node, node_to_fail_list
    return var

'''sequential failures'''
def sequential_degree(G,INTERDEPENDENCY): #formally cascading
    '''Code to perform the sequential analysis where the node to be removed is
    selected via that with the highest degree.
    Input: a network, INTERDEPENDENCY variable
    Return: a network, the node removed '''
    #get the node and with the maximum value from the network
    var = tools.max_val_random(nx.degree(G))
    if type(var) == int:
        return 3000
    else: degree, node = var

    #if the returned node is -99999, then there is an error
    if node == -99999:
        #check to see if the number of edges in the network is greater than 0
        if G.number_of_edges() > 0:
            raise error_classes.GeneralError('There are %s edge on the network. An unknown error has occred.' %(G.number_of_edges()))
            return 3001

        else:
            raise error_classes.CalculationError('There are no edges in the network, thus no values could be computed.')
            return 3002
    else:
        #remove the edges connected to the node - networkx does this automatically
        #remove the node from the network
        try:
            G.remove_node(node) #remove the node
        except:
            return 3003

    #return the editied network and the node removed
    var = G, node
    return var

def sequential_degree_by_list(G,INTERDEPENDENCY,failures_to_occur,node_to_fail_list):
    '''
    Allows for a list of the nodes to be removed to be calculated and saved allowing these to then be removed without re-calcualting those nodes to be removed. Uses node degree.
    '''
    method = 'degree'
    var = sequential_by_list(G,failures_to_occur,node_to_fail_list,method)

    return var

def sequential_betweenness(G,INTERDEPENDENCY):
    '''Sequential analysis where the node to be removed on each iteration is
    that with the highest betweenness centrality value.
    Input: a network, INTERDEPENDENCY variable
    Return: a network, the node removed'''
    #find the node with the max betweenness value in the network
    var = tools.max_val_random(nx.betweenness_centrality(G))
    if type(var) == int:
        return 3010
    else: betweenness_value, node = var

    #if the node has the value of an error
    if node == -99999:
        raise error_classes.GeneralError('Error. An error occured when calcualting the node to remove.')
        return 3011
    else:
        #remove all edges which feature the node and then the node
        try:
            G.remove_node(node)
        except:
            return 3012
    #return the eddited network and the node remvoed
    var = G, node
    return var

def sequential_betweenness_by_list(G,INTERDEPENDENCY,failures_to_occur,node_to_fail_list):
    '''
    Allows a list of nodes to be created and used to remove the nodes.
    '''
    method = 'betweenness'
    var = sequential_by_list(G,failures_to_occur,node_to_fail_list,method)
    return var

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
    try:
        G.remove_node(node)
    except:
        return 3020
    #return the network and the node which was removed
    var = G, node
    return var

def sequential_clustering_by_list(G,INTERDEPENDENCY,failures_to_occur,node_to_fail_list):
    '''
    Allows a list of nodes to be created and used to remove the nodes.
    '''
    method = 'clustering'
    var = sequential_by_list(G,failures_to_occur,node_to_fail_list,method)
    return var

def sequential_flow(G, NO_ISOLATES, INTERDEPENDENCY):
    '''Sequential anlysis method where the node to be removed is selcted
    via having the highest flow value.
    Input: a network, NO_ISOLATES varaible, INTERDEPENDENCY variable
    Return: a network, the node removed'''

    flow_dict = {}
    for nd in G.nodes():
        flow_dict[nd]=G.node[nd]['flow']

    var = tools.max_val_random(flow_dict)
    if type(var) == int:
        return 3030
    else: betweenness_value, node = var

    #if the node has the value of an error
    if node == -99999:
        raise error_classes.GeneralError('Error. An error occured when calcualting the node to remove.')
        return 3031
    else:
        #remove all edges which feature the node and then the node
        try:
            G.remove_node(node)
        except:
            return 3032
    #return the eddited network and the node removed
    var = G, node
    return var

def sequential_from_list(G,INTERDEPENDENCY,fail_list,i):
    '''
    '''
    try:
        node = fail_list[i]
    except:
        return 3040
    try:
        G.remove_node(node)
    except:
        return 3041
    var = G, node
    return var

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
    try:
        i = 0
        while i < len(deadlist):
            node = deadlist[i]
            #to avoid errors, check if the node has been removed yet due to being in a subgraph or an isolated node
            REMOVED = network_handling.check_node_removed(node, subnodes_A, isolated_nodes_A)
            if type(REMOVED) == int:
                return REMOVED
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
                    try:
                        neighbours_list = G.neighbors(node)
                    except: return 3051
                    y = 0
                    while y<len(neighbours_list):
                        fnode = neighbours_list[y]
                        nlist.append(fnode)
                        y += 1
                    #remove the edges and the node
                    try:
                        G.remove_node(node)
                    except: return 3053
                    removed_nodes.append(node) #
            i += 1
    except:
        return 3052
    #update the lists for the next iteration
    dlist = nlist
    node = deadlist
    var = G,dlist,removed_nodes,node
    return var

'''flow cascading failure'''
def flow_cascading_failure(G,NO_ISOLATES, INTERDEPENDENCY,flow_key,cap_key):
    '''
    Removes any nodes where the flow value exceeds the capacity value.
    Inputs:
    Returns:
    '''
    removed_edges = []
    removed_nodes = []

    #check for keys in networks
    for edge in G.edges(data=True):
        try:
            edge[2][flow_key]
        except:
            print('Could not find %s attribute in an edge.' %flow_key)
            raise
        try:
            edge[2][cap_key]
        except:
            print('Could not find %s attribute in an edge.' %cap_key)
            raise

    for node in G.nodes(data=True):
        try:
            node[1][flow_key]
        except:
            print('Could not find %s attribute in a node.' %flow_key)
            raise
        try:
            node[1][cap_key]
        except:
            print('Could not find %s attribute in a node.' %cap_key)
            raise

    #remove any edge where flow is greater than capacity
    for edge in G.edges(data=True):
        if edge[2][flow_key] > edge[2][cap_key]:
            removed_edges.append(edge)
    #remove any node where flow is greater then capacity
    for node in G.nodes(data=True):
        if node[1][flow_key] > node[1][cap_key]:
            removed_nodes.append(node)

    return G,removed_nodes,removed_edges


'''single isolaterd failures'''
def single_random(G,node_list, INTERDEPENDENCY):
    '''Analysis by removeing only one node for each iteration, where the nodes
    are selected at random.
    Input: network, list of nodes, INTERDEPENDENCY variable
    Return: network, node removed '''
    #if there are no nodes in the network
    if len(node_list) < 1:
        raise error_classes.GraphError('Error. No nodes to choose from for the node to remove.')
        return 3060

    #choose a node at random from the graph node list
    node = random.choice(node_list)
    #use Gtemp as need to reset G to its original state for the next iteration
    Gtemp = G
    try:
        Gtemp.remove_node(node)
    except: return 3061
    #need to keep track of the nodes removed, hence a list
    node_list.remove(node)
    var = Gtemp,node
    return var

'''Failure via shapefile'''
def geo_failure(G,shp_file):
    '''
    Given a shapefile, identifies those nodes within the failure zone.
    '''

    print('THIS NEEDS UPDATING')
    import shapefile
    coords = []
    try:
        sf = shapefile.Reader(shp_file)
    except: return 3070

    shapes = sf.shapes()
    for shape in shapes:
        for p in  shape.points:
            coords.append(p)
    polygon = coords
    #get list of node
    list_of_nodes = G.nodes()
    nodes_removed = []

    #loop through list of nodes
    Gtemp = G
    for nde in list_of_nodes:
        #see if node inside polygon
        inside = point_in_poly(nde,polygon)
        if type(inside) == int:
            return inside

        #if inside polygon
        if inside == True:
            #remove node and edges from network
            try:
                Gtemp = network_handling.remove_edges(Gtemp, nde, INTERDEPENDENCY=False)
            except: return 3071
            try:
                Gtemp.remove_node(nde)
            except: return 3072

            nodes_removed.append(nde)

    var = Gtemp, nodes_removed
    return var

def point_in_poly(coord,poly):
    '''Point in polygon.'''
    x,y = coord
    n = len(poly)
    inside = False

    try:
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
    except:
        return 3080

    return inside
