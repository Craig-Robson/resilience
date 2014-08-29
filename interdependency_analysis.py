 # -*- coding: utf-8 -*-
""" Previuosly was v14, the most up to date and working code
Created on Mon Jul 23 14:26:27 2012

@author: Craig Robson
"""
'''
Code layout

The mian function is used to define the analysis type and the networks involved in the analysis.
    First choice is single or cascading analysis
    If cascading selected, must also choice a type of node selection
        degree, betweenness, random, cascading
        This is done by changing the relevant false statement to true
        Only one method can be selected(True) at a time
From the main function a following funtion is called based upon the first selection (single or cascading)
    These functions then call other functions which combined performed the requested analysis
For the average path length calcualtion, use a edge length field, which must be the same in both tables (in this version anyway)

For the developer:
    From the cascading_analysis function the node selection function is called
        Returns the graph with relevant node and edges removed(used remove_edges function)
    Then calls the analysis function which performs the majority of the analysis (from within a loop in the cascading analysis function)
        This takes the node removed and the graph and 'cleans' the graph so suitable for analysis        
            Removes isolated nodes and dissconnected edges (uses clean_graph function)
            Then removes any subgraphs, using handle_sub_graphs function
    Finally the results module is called and the results printed and wrote to file
        File path defined at top of code
        

5_1_5+:
to make the failure models easier to run with external data as a stand alone script

5_1_7+:
changes to make the metric selection policy more user friendly and flexable
        
5_2_??:
changes again to make the metric selection even more user firendly after the failure of the 5_1_ methods


'''

__author__ = "Craig Robson"
__created__ = "Wed Jul 23 14:26:27 2012"
__year__ = "2012"
__version__ = "1.0"


import sys
import networkx as nx
import random as r
import time
import datetime

sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet');

#parameters for the database connection
host = 'localhost'
user = 'postgres'
password = 'aaSD2011'
port = '5433'

'''sql to create interdependency lists'''
#interdependency code does not work yet
#fromSQL='SELECT "p" FROM "Inter_Lines"'
#toSQL='SELECT "t" FROM "Inter_Lines"'

'''weight field for path length'''
length = 'shape_leng'

'''Advanced options'''
#NO_ISOLATES = False


def write_to_log_file(logfilepath,text):
    '''Writes to a file given a file path and a string of text. Also adds the 
    time to the output. Opens and closes the file to avoid the file being 
    locked during complex iteractions.
    Input: logfilepath, string of text
    Return: Nothing  '''
    print 'log file path is: ', logfilepath
    #if a logfile is being used and the filepath has been specified
    if logfilepath <> False or logfilepath <> None:
        try:
            #open the logfile, print the time and the string sent
            logfile = open(logfilepath,'a')
            logfile.write(str(datetime.time) + ',\t' + str(text))
            logfile.close()
        except:
            #if the logfile could not be opened, exit
            print 'COULD NOT WRITE TO LOG FILE'
            print logfilepath
            print text
            exit()
    
def max_val_random(alist):
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
    i = 0
    #loop through the whole list
    while i<len(alist):
            try:
                if alist[i] == 0:
                    #if there is a value of zero, ignore it
                    pass
                elif alist[i] > ma:
                    #if the value is higher than the max value already
                    #reset the tie list
                    tie_list = []
                    #add the value to the tie_list in case another one with the same value is found
                    tie_list.append(i)
                    ma = alist[i]
                    node = i
                elif alist[i] == ma:
                    #if the value is the same as the current max value, add to the tie list
                    tie_list.append(i)
                else:
                    pass
            except:
                pass
            i += 1
    #if there is more than one node in the tie list, pick one at random            
    if len(tie_list)>0:
        node = r.choice(tie_list)
        return ma, node
    #this should really eb idne in the betweenness function
    else: 
        #list can be zero if using betweenness as nodes can be in pairs, thus non have a betweenness value
        #therefore, as graph stil has active components, still have to remove a node
        #thus pick one at random to remove
        templist=[]
        for node in alist:
            templist.append(node)
        node = r.choice(templist)
        return ma, node 
        
'''sequential failures'''
def sequential_degree(G,INTERDEPENDENCY): #formally cascading
    '''Code to perform the sequential analysis where the node to be removed is 
    selected via that with the highest degree.
    Input: a network, INTERDEPENDENCY variable
    Return: a network, the node removed '''
    #get the node and with the maximum value from the network
    degree, node = max_val_random(nx.degree(G))
    #if the returned node is -99999, then there is an error
    if node == -99999:
        #check to see if the number of edges in the network is greater than 0
        if G.number_of_edges() > 0: 
            print 'There are', G.number_of_edges(), 'edge on the network. An unknown error has occred.'
        else: print 'There are no edges in the network, thus no values could be computed.'
        exit()
    else: #graph still connected
        #remove the edges realted to the node - networkx does this automatically when you remove the node I think
        G = remove_edges(G,node,INTERDEPENDENCY) 
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
    degree, node = max_val_random(nx.betweenness_centrality(G)) 
    #if the node has the value of an error
    if node == -99999:
        print 'An error occured when calcualting the node to remove.'
        exit()
    else:
        #remove all edges which feature the node and then the node
        G = remove_edges(G, node,INTERDEPENDENCY) 
        G.remove_node(node) 
    #return the eddited network and the node remvoed
    return G,node
    
def sequential_random(G, NO_ISOLATES, INTERDEPENDENCY):
    '''Sequential anlysis method where the node to be removed is selcted 
    randomly from those still in the network.
    Input: a network, NO_ISOLATES varaible, INTERDEPENDENCY variable
    Return: a network, the node removed'''
    #choose a node at random from the network node list
    node = r.choice(G.nodes()) 
    #if isolates are not to be removed as a selected node
    if NO_ISOLATES==True:
        #randomly select a node until one is found with a degree of one at least
        while nx.degree(G, node) == 0: 
            node = r.choice(G.nodes())
    #remove the edge assocaiated with the node and then the node
    G = remove_edges(G, node, INTERDEPENDENCY)
    G.remove_node(node)
    #return the network and the node which was removed
    return G,node    
    
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
        REMOVED = check_node_removed(node, subnodes_A, isolated_nodes_A) 
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
                G = remove_edges(G, node,INTERDEPENDENCY)
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
    if len(node_list)< 1:
        print 'MAJOR ERROR. TERMINATING. NO NODES TO CHOOSE FROM FOR SINGLE_RANDOM PROCESS.'
        exit()
    #choose a node at random from the graph node list
    node = r.choice(node_list) 
    #use Gtemp as need to reset G to its original state for the next iteration
    Gtemp = G
    Gtemp = remove_edges(Gtemp, node, INTERDEPENDENCY)
    Gtemp.remove_node(node)
    #need to keep track of the nodes removed, hence a list
    node_list.remove(node)
    return Gtemp,node      

'''cleaning the graph(s)'''  
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
        print 'Graph dissconnected, there are no edges and the number of nodes in the graph is ', G.number_of_nodes(), '(handle_isolated function).'
        exit()
    else:
        #remove all nodes which are in the isolated list
        G.remove_nodes_from(isolatednodes) 
    return G,isolatednodes
        
def remove_isolates(Gtemp,node_list,isolated_nodes,isolated_n_count_removed,node_count_removed,to_nodes,from_nodes):
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
                k-=1
            k+=1
        j+=1
    
    #update some of the lists to record the simulation process
    isolated_nodes.append(isolatednodes)  
    isolated_n_count_removed.append(len(isolatednodes))
    node_count_removed.append(node_count_removed.pop()+len(isolatednodes))
    
    #remove from to and from lists where the dependence link is now invalid as to node removed as isolated
    v = 0
    while v<len(isolatednodes):
        vf = 0
        while vf<len(to_nodes):
            if isolatednodes[v]==to_nodes[vf]:
                to_b_nodes.pop(vf) #remove from the to list
                from_a_nodes.pop(vf) #remove from the from list
                vf -= 1
            vf += 1
        v += 1       
             
    return Gtemp,node_list,isolated_nodes,isolated_n_count_removed,node_count_removed,to_nodes,from_nodes

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
 
def clean_node_lists(subn,node_list, to_b_nodes, from_a_nodes):
        '''Clean the node lists which are needed for some forms of analyiss of 
        any nodes which have been removed from the network already.
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
                while vf < len(to_nodes):
                    if subn[v][vd] == to_b_nodes[vf]:
                        to_b_nodes.pop(vf) #remove from the to list
                        from_a_nodes.pop(vf) #remove from the from list
                        vf-=1 #adjust vf so no value in list is missed
                    vf += 1
                vd += 1
            v += 1 

def handle_sub_graphs(nodelists, edgelists):
    'Used for removing subgraphs from a network, but converting them to node and edge lists so can be re-built for analysis purposes.'
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
    nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A = basic_metrics_A
    nodes_removed_B,node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B = basic_metrics_B
    size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,inter_removed_count_A = option_metrics_A
    size_of_components_B,giant_component_size_B,av_nodes_in_components_B,isolated_nodes_B,isolated_n_count_B,isolated_n_count_removed_B,subnodes_B,subnodes_count_B,path_length_B,av_path_length_components_B,giant_component_av_path_length_B,av_path_length_geo_B,average_degree_B,inter_removed_count_B = option_metrics_B
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
            print 'found node in net A'
            tnode = to_b_nodes[i] #get the to node at the other end of the dependency edge                                                     
            #print 'node dependent on node ', node, ' is (tnode) ', tnode
            REMOVED = check_node_removed(tnode, subnodes_B, isolated_nodes_B) #check node has not been removed through being isolated or member of a subgraph
            if REMOVED == False: #if node still in network
                print 'node still in B - ', tnode, ' - ', GtempB.nodes()
                GtempB = remove_edges(GtempB,tnode,INTERDEPENDENCY) #remove all edges which feature the to node
                try:                
                    GtempB.remove_node(tnode) #remove the to node
                except:
                    print 'MAJOR ERROR - NODE COULD NOT BE REMOVED/DOES NOT EXIST'
                    error = 0001
                    return error
                print 'node removed from B'
                node_count_removed_B.append(node_count_removed_B.pop()+1) #add to the total count of nodes removed               
                inter_removed_count_B.append(inter_removed_count_B.pop()+1) #add to the count of nodes removed through interdependency
                temp.append(tnode) #add removed node to the temp list to be added to be main list at the end of iteration process
                to_b_nodes.pop(i) #remove node from the to list
                from_a_nodes.pop(i) #remove node from the from list
                i-=1 #edit i so no list items are mised  
                #print 'Interdependency analysis, node found in graph and removed successfully.'
            elif REMOVED == True: #if node has already been removed in another process - not sure this is still needed
                print 'REMOVED was true, see above for reason'
            else:
                print 'Node has already been removed. Should never see this!!!!' #means the ndoe is missing - been removed and not recorded why
        i += 1
    networks =  GA, GB, GtempA, GtempB
    basic_metrics_A = nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A
    basic_metrics_B = nodes_removed_B,node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B
    option_metrics_A = size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,inter_removed_count_A
    option_metrics_B = size_of_components_B,giant_component_size_B,av_nodes_in_components_B,isolated_nodes_B,isolated_n_count_B,isolated_n_count_removed_B,subnodes_B,subnodes_count_B,path_length_B,av_path_length_components_B,giant_component_av_path_length_B,av_path_length_geo_B,average_degree_B,inter_removed_count_B
    args = networks,node,basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B,to_b_nodes,from_a_nodes,temp    
    return args

def check_node_removed(node, subnodes, isolated_nodes):
    'Identify if a node has been removed from the network already, or if it is still part of the network.'
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

'''analysis functions'''  

def calc_initial_values(Gtemp, basic_metrics, option_metrics):
    '''Calculates all the initial values for the metrics selected to record 
    the performance of the network.'''
    nodes_removed,node_count_removed,count_nodes_left,number_of_edges,number_of_components = basic_metrics
    size_of_components,giant_component_size,av_nodes_in_components,isolated_nodes,isolated_n_count,isolated_n_count_removed,subnodes,subnodes_count,path_length,av_path_length_components,giant_component_av_path_length,av_path_length_geo,average_degree,inter_removed_count = option_metrics
    #calculate the average degree of the nodes if not set as False    
    if average_degree <> False:
        #get the list of node degrees
        degreelist = Gtemp.degree()
        #get the sum of the list of values
        average_degree = sum(degreelist)
        average_degree.append(average_degree/nx.number_of_nodes(Gtemp))
    #calculate the average path length of the components ro for the whole network
    if av_path_length_components <> False or path_length <> False:    
        geo_total = 0.0  
        sumtotal = 0.0      
        #go through the connected components and calcualte the average path length
        for g in nx.connected_component_subgraphs(Gtemp):
            av_path_length = nx.average_shortest_path_length(g)
            #if geo length metric has also been selected, calculate that as well
            if av_path_length_geo <> False:
                av_geo_path_length = nx.average_shortest_path_length(g, length)
            #if wanted for the components, add to the respective list
            if av_path_length_components <> False:
                av_path_length_components.append(av_path_length)
            
            geo_total += av_geo_path_length    
            sumtotal += av_path_length
            av_path_length = None
        
        #calculate the averages if requried
        if av_path_length_geo <> False:
            av_path_length_geo = []
            av_path_length_geo.append(geo_total/nx.number_connected_components(Gtemp))
        
        if path_length <> False:
            path_length = []
            path_length.append(sumtotal/nx.number_connected_components(Gtemp))
        sumtotal = None
        
    #if need the number of components, calcualte and append to the list
    if number_of_components <> False:
        number_of_components = []
        number_of_components.append(nx.number_connected_components(Gtemp))
    
    #if need the size of components, calcaulte and add to the list
    if size_of_components <> False:
        temp = []
        size_of_components = []
        for g in nx.connected_component_subgraphs(Gtemp):
            temp.append(g.number_of_nodes())
        size_of_components.append(temp)
        temp = None
        
    #if need the number of edges, calculate and add to the list
    if number_of_edges <> False:
        number_of_edges = []
        number_of_edges.append(nx.number_of_edges(Gtemp))
        
    #if need the a list of isolates
    if isolated_nodes <> False:
        isolated_nodes = []
        isolated_nodes.append(nx.isolates(Gtemp))
    #if need count of the number of isolates
    if isolated_n_count <> False:
        isolated_n_count = []
        isolated_n_count.append(len(nx.isolates(Gtemp)))
    #if need count of number of nodes removed due to interdependent edges        
    if inter_removed_count <> False: 
        inter_removed_count = []        
        inter_removed_count.append(0)
    #group of metric (containers) into their respective varaibles and return
    basic_metrics = nodes_removed,node_count_removed,count_nodes_left,number_of_edges,number_of_components
    option_metrics = size_of_components,giant_component_size,av_nodes_in_components,isolated_nodes,isolated_n_count,isolated_n_count_removed,subnodes,subnodes_count,path_length,av_path_length_components,giant_component_av_path_length,av_path_length_geo,average_degree,inter_removed_count
    return basic_metrics, option_metrics
        
def core_analysis(G, GnetB, parameters):   
    '''Creates all the data containers and packages them all
    up into one varaible which can be used for the analysis.
    Inputs: network A, network B, parameters
    Outputs: graphparameters '''
    #unpack the paarameters
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges = parameters  
    
    #----------------unpack the metrics----------------------------------------
    basic_metrics_A, basic_metrics_B, option_metrics_A, option_metrics_B = metrics
    nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A=basic_metrics_A
    if basic_metrics_B <> None:    
        nodes_removed_B,node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B=basic_metrics_B
    size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,inter_removed_count_A=option_metrics_A
    if option_metrics_B <> None:    
        size_of_components_B,giant_component_size_B,av_nodes_in_components_B,isolated_nodes_B,isolated_n_count_B,isolated_n_count_removed_B,subnodes_B,subnodes_count_B,path_length_B,av_path_length_components_B,giant_component_av_path_length_B,av_path_length_geo_B,average_degree_B,inter_removed_count_B=option_metrics_B
    
    #----------------sort a_to_b edges-----------------------------------------
    #when doing dependency and interdependency analysis, need to create lists 
    #of the nodes in each network affected by the links 
    from_a_nodes = []
    to_b_nodes = []
    if STAND_ALONE == False:
        for item in a_to_b_edges:
            a,b = item
            from_a_nodes.append(a)
            to_b_nodes.append(b)
        if INTERDEPENDENCY == True:
            pass
        
    #----------------sort the networks out-------------------------------------
    #make copies of the networks
    GA = G.copy()
    GB = GnetB.copy()
      
    i = 0
    #----------------create data containers------------------------------------   
    # create a template blank list
    blnklist=[]
    #----------------for basic metrics-----------------------------------------
    #need to create all the data containers for the metrics which are set as True
    nodes_removed_A = [0] #nodes removed from network A
    node_count_removed_A = [0] #count of ndoes removed from network A   
    count_nodes_left_A = [GA.number_of_nodes()] #the number of nodes left in network A
    number_of_edges_A = [] #number of edges in the network
    number_of_components_A = [] #number of subgraphs/isolated nodes
    if STAND_ALONE == False:
        nodes_removed_B = [blnklist] #nodes removed from network B
        node_count_removed_B = [0]  #count of ndoes removed from network B  
        count_nodes_left_B = [GB.number_of_nodes()] #the number of nodes left in network B
        number_of_edges_B = [] #number of edges in the network
        number_of_components_B = [] #number of subgraphs/isolated nodes
    
    #----------------for optional metrics--------------------------------------
    if size_of_components_A == True: size_of_components_A = []
    if giant_component_size_A == True: giant_component_size_A = []
    if av_nodes_in_components_A == True: av_nodes_in_components_A = []
    if isolated_nodes_A == True: isolated_nodes_A = [blnklist]#list of isolated nodes
    if isolated_n_count_A == True: isolated_n_count_A = [0] #count of isolated nodes in network at each node removal
    if REMOVE_ISOLATES == True or isolated_n_count_removed_A == True:
        isolated_n_count_removed_A = [0] #count the number of isolated nodes removed in the handle isolates function each step    
    if REMOVE_SUBGRAPHS == True or subnodes_A == True or subnodes_count_A == True:
        subnodes_A = [blnklist] #nodes removed as part of isolated graphs
        subnodes_count_A = [0] #count of nodes removed as part of subgraphs
        
    if STAND_ALONE == False:
        if size_of_components_B == True: size_of_components_B = []
        if giant_component_size_B == True: giant_component_size_B = []
        if av_nodes_in_components_B == True: av_nodes_in_components_B = []
        if isolated_nodes_B == True: isolated_nodes_B = [blnklist]#list of isolated nodeS
        if isolated_n_count_B == True: isolated_n_count_B = [0] #count of isolated nodes in network at each node removal
        if REMOVE_ISOLATES == True or isolated_n_count_removed_B == True:
            isolated_n_count_removed_B = [0] #count the number of isolated nodes removed in the handle isolates function each step    
        if REMOVE_SUBGRAPHS == True or subnodes_B == True or subnodes_count_B == True:
            subnodes_B = [blnklist] #nodes removed as part of isolated graphs
            subnodes_count_B = [0] #count of nodes removed as part of subgraphs
            
    if path_length_A == True: path_length_A = [] #path length container for network A 
    if av_path_length_components_A == True: av_path_length_components_A = []
    if giant_component_av_path_length_A == True: giant_component_av_path_length_A = []
    if average_degree_A == True: average_degree_A = []
    
    if STAND_ALONE == False:
         if path_length_B == True: path_length_B = [] #path length container for network A
         if av_path_length_components_B == True: av_path_length_components_B = []
         if giant_component_av_path_length_B == True: giant_component_av_path_length_B = []
         if average_degree_B == True: average_degree_B = []
         if inter_removed_count_B == True: inter_removed_count_B = [0]
         
    #----------------specific metrics for interdependency----------------------
    if INTERDEPENDENCY == True:
        inter_removed_nodes = [blnklist] #list of nodes removed as thier dependent node has been removed
        inter_removed_count = [0] #count of nodes removed due to failure of dependent node 
        interdependency_metrics = inter_removed_nodes, inter_removed_count
    else: interdependency_metrics = None
    
    #----------------specific metrics for cascading analysis-------------------
    if CASCADING == True:
        dead = r.choice(GA.nodes()) #set the initial node to be removed for the neighbour analysis
        dlist = [] #list to store nodes between iterations during nieghbour analysis
        removed_nodes=[] #list to store nodes during the nieghbor analysis
        deadlist = [] #neighbor analysis only: the nodes removed in the last iteration  
        cascading_metrics = dead, dlist, removed_nodes, deadlist
    else: cascading_metrics = None
     
    #----------------store all data containers into a single variable - graph parameters
    #for ease of transferability, package up all metric containers into respective variables
    basic_metrics_A = nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A
    option_metrics_A = size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,inter_removed_count_A
    if STAND_ALONE == False:
        basic_metrics_B = nodes_removed_B,node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B     
        option_metrics_B = size_of_components_B,giant_component_size_B,av_nodes_in_components_B,isolated_nodes_B,isolated_n_count_B,isolated_n_count_removed_B,subnodes_B,subnodes_count_B,path_length_B,av_path_length_components_B,giant_component_av_path_length_B,av_path_length_geo_B,average_degree_B,inter_removed_count_B
    else: basic_metrics_B = None; option_metrics_B = None
    
    #----------------sort initial networks out again---------------------------
    GtempA = GA.copy() #create a temp version of network to be used for all analysis
    if GB == None:
        GB = nx.Graph()
    GtempB = GB.copy() #create a temp version of network to be used for all analysis
    
    #generate a node list as need for some simulations    
    node_list = GA.nodes() #for single random analysis only
    #
    figureModel = None
    
    #----------------calculate the initial values for network A----------------
    basic_metrics_A, option_metrics_A = calc_initial_values(GtempA,basic_metrics_A, option_metrics_A)
   
    #----------------calculate the initial values for network B----------------
    if STAND_ALONE == False:
        basic_metrics_B, option_metrics_B = calc_initial_values(GtempB,basic_metrics_B, option_metrics_B)
    
    #----------------package stuff up------------------------------------------
    networks = GA, GB, GtempA, GtempB    
    graphparameters = networks,i,node_list, to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics  
    return graphparameters
       
def step(graphparameters,parameters,iterate,logfilepath):
    '''Performs one time step of analysis when called.
    Inputs: graphparameters, parameters iterate 
    Returns: graphparameters, iterate '''
    #----------------unpack all the data containers----------------------------
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges = parameters    
    networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics = graphparameters
    GA, GB, GtempA, GtempB = networks
    nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A = basic_metrics_A

    #----------------perform the analsis---------------------------------------
    #----------------for sequential analysis only------------------------------
    if SEQUENTIAL == True and SINGLE == False and CASCADING == False:
        if DEGREE == True:
            #find node based on highest degree and remove it
            GtempA,node = sequential_degree(GtempA,INTERDEPENDENCY)
        elif BETWEENNESS == True:
            #find node with highest betweenness value and remove it           
            GtempA,node = sequential_betweenness(GtempA,INTERDEPENDENCY)
        elif RANDOM == True:
            #randomly select the next node and remove it
            GtempA,node = sequential_random(GtempA, NO_ISOLATES,INTERDEPENDENCY)
        #update the counter
        node_count_removed_A.append(len(node_count_removed_A))
    
    #----------------for cascading analysis------------------------------------
    elif CASCADING == True and SINGLE == False and SEQUENTIAL == False: 
        #unpack the cascading metrics and create some blank containers
        dead, dlist, removed_nodes, deadlist = cascading_metrics
        isolated_nodes_A = []
        subnodes_A = []
        #------------identify subnodes and isolated nodes--------------------
        for g in nx.connected_component_subgraphs(GtempA):
            if g.number_of_nodes == 1:
                isolated_nodes_A.append(g.nodes())
            elif g.number_of_nodes <> 0:
                subnodes_A = subnodes_A.append(g.nodes())
            else:
                print 'Component has zero nodes.'
                exit()
        #------------on the first time step only-----------------------------
        #need to initaite the failure through remoiving a node to begin with
        if i == 0:
            if DEGREE == True and BETWEENNESS == False and RANDOM == False:
                ma, dead = max_val_random(nx.degree(GtempA))
            elif BETWEENNESS == True and RANDOM == False and DEGREE == False:
                ma, dead = max_val_random(nx.betweenness_centrality(GtempA))
            elif RANDOM == True and DEGREE == False and BETWEENNESS == False:
                dead = dead
            #update the network and find the next set of nodes to remove
            GtempA,dlist,removed_nodes,deadlist = cascading_failure(GtempA,dlist,dead,i,subnodes_A, isolated_nodes_A,nodes_removed_A,INTERDEPENDENCY)
            node = deadlist
            
        #------------on all but first time step------------------------------
        else:
            #update the network and find the next set of nodes to remove
            GtempA,dlist,removed_nodes,deadlist = cascading_failure(GtempA,dlist,dead,i,subnodes_A, isolated_nodes_A,nodes_removed_A,INTERDEPENDENCY)         
            node = deadlist
        
        #update the metric
        #this method below needs checking
        node_count_removed_A.append(node_count_removed_A[i]+len(deadlist))

        #------------package cascading metrics together----------------------
        cascading_metrics = dead, dlist, removed_nodes, deadlist

    #----------------for single analysis---------------------------------------
    elif SINGLE == True and SEQUENTIAL == False and CASCADING == False:
        #create a copy of the original network - will be complete
        GtempA = GA.copy()
        #select and remove a node from the network
        GtempA,node = single_random(GtempA, node_list, INTERDEPENDENCY)
        #------------when node list is empty change iterate------------------
        if node_list == []:
            iterate = False
        #update the metric
        node_count_removed_A.append(len(node_count_removed_A))
        
    #----------------update the list of removed nodes--------------------------
    nodes_removed_A.append(node)
    
    #----------------re-package networks and metrics which have been changed---
    basic_metrics_A = nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A       
    networks = GA, GB , GtempA, GtempB
    
    #----------------functions for analysis methods----------------------------
    if INTERDEPENDENCY == True:
        pass
        #this in case in future we start removing nodes from both networks
        #nodes_removed_B.append(nodeB)

    '''Run the post node removal analysis''' #biggest area which needs updating
    if INTERDEPENDENCY == True and STAND_ALONE == False and DEPENDENCY == False :
        '''Needs to be developed'''
        
    elif DEPENDENCY == True and STAND_ALONE == False and INTERDEPENDENCY == False :
        '''Needs to be updated. Uses A and B. Not sure on state of A or why A is needed at all'''        
        '''need to find out what the main metrics are which are NEEDED for dependency analysis'''
        '''a_to_b_edges holds the connecting edges between the networks'''
        #special one for cascading as loop needed to handle multiple network A nodes being removed in one iteration
        #to store all nodes for intire iteration which are removed from networkB due to broken dependence link
        temp = []
        #------------if cascading analysis-----------------------------------
        #this needs checking
        if CASCADING == True: 
            x = 0
            while x < len(deadlist):
                node = deadlist[x]
                GtempA, GtempB, to_b_nodes, from_a_nodes, temp = check_dependency_edges(GtempA, GtempB, node, to_b_nodes, from_a_nodes, temp)
                x += 1
        #------------run for all other analysis scenarios--------------------
        else:
            args = check_dependency_edges(networks,node,basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B,to_b_nodes,from_a_nodes,temp)
            if args == 0001:
                print 'ERROR', args, ' Could not find chosen node to remove it'
                write_to_log_file(logfilepath, 'ERROR %s; Could not find chosen node ro remove (check_dependency_edges).' %(args))
                error = 0001
                return error
            else:
                #un-pack variables returned                  
                networks,node,basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B,to_b_nodes,from_a_nodes,temp = args
        #------------re-package networks-------------------------------------
        GA, GB, GtempA, GtempB = networks
        #ANALYSE NETWORK A   
        #what is the differnece between a and b?
        #B only does stand alone network
        #A has the extra checks for dependency networks in theory, though I can't see any differences
        #GtempA,GtempB,to_b_nodes,from_a_nodes,temp,i,basic_metrics_A,option_metrics_A = analysis_A(GtempA,GtempB,to_b_nodes,from_a_nodes,temp,i,basic_metrics_A,option_metrics_A) #run the analysis        
        
        #------------run the actual analysis---------------------------------
        #analyse network B        
        iterate,GtempB,i,to_b_nodes,from_a_nodes,node_list,basic_metrics_B,option_metrics_B = analysis_B(parameters,iterate,GB,i,to_b_nodes,from_a_nodes,node_list,basic_metrics_B,option_metrics_B,to_b_nodes, from_a_nodes)
        #analyse A
        iterate,GtempA,i,to_b_nodes,from_a_nodes,node_list,basic_metrics_A,option_metrics_A = analysis_B(parameters,iterate,GtempA,i,to_b_nodes,from_a_nodes,node_list,basic_metrics_A,option_metrics_A,to_b_nodes, from_a_nodes) #run the analysis        
        
        #------------move counter on-----------------------------------------
        i += 1   
        
    elif STAND_ALONE == True and DEPENDENCY == False and INTERDEPENDENCY == False :
        #run the analysis
        iterate,GtempA,i,to_b_nodes,from_a_nodes,node_list,basic_metrics_A,option_metrics_A = analysis_B(parameters,iterate,GtempA,i,to_b_nodes,from_a_nodes,node_list,basic_metrics_A,option_metrics_A,to_b_nodes, from_a_nodes) #run the analysis
        i += 1  
    else:
        print 'TERMINAL ERRROR\nNO ANALYSIS TYPE SELECTED'
        sys.exit()
    
    #----------------re-package all data into respective containers------------
    networks = GA, GB, GtempA, GtempB    
    graphparameters = networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics   
    return graphparameters, iterate
    
def analysis_A(networks, basic_metrcs_A, basic_metrics_B, optional_metrics_A, optional_metrics_B,i,node,to_b_nodes, from_a_nodes,temp,): #perform the analysis of the graph 
        '''The analysis function is for the network which is dependent on 
        another, thus some extra checks after to be run'''        

        GA, GB, GtempA, GtempB = networks
        #run function to check interdependency stuff  - has to go here after checking for isolted nodes and subnodes, so can then remove any network b nodes which are dependent on these 
        if REMOVE_ISOLATES == True:        
            GtempA, isolatednodes = handle_isolates(GtempA) #remove any isolated nodes and assocaited edges
            isolated_nodes.append(isolatednodes)  #add to the list the issolated nodes removed
            isolated_n_count_removed.append(len(isolatednodes)) #record the count of islated nodes removed
            node_count_removed.append(node_count_removed.pop()+len(isolatednodes))#first extra nodes removed from graph
        #run the interdependence analysis on any nodes removed due to being isalted as they be the supply node for nodes in other network    
        #print 'isolated nodes are ', isolatednodes
        x=0
        while x<len(isolatednodes):        
            node=isolatednodes[x]
            #print 'checking isolated node ', node, 'is not part of a dependency'
            GtempA, GtempB, node_count_removed_B, to_b_nodes, from_a_nodes, inter_removed_count, temp = check_inter_edges(GtempA, GtempB, node, node_count_removed_B, to_b_nodes, from_a_nodes, subnodes_A, subnodes_B, isolated_nodes_A, isolated_nodes_B, inter_removed_count, temp)
            x += 1
        num_edges = GtempA.number_of_edges() 
        
        #from here just calcs the metrics
        if num_edges <> 0: #if the graph is not dissconnected

            nodelists=GtempA.nodes()
            edgelists=GtempA.edges()
            subn,nsubnodes, nodelists, edgelists = handle_sub_graphs(nodelists, edgelists) #send the current lists of edges and nodes for graphs.retireive the vairables and the new edge and node lists
            #old function call GtempA, subn,nsubnodes = handle_sub_graphs(GtempA) remove any sub graphs                     
            
            subnodes.append(subn)  #add all the nodes removed as part of subgraphs to the master list
            node_count_removed.append(node_count_removed.pop() + nsubnodes) #sum the current total(from isolated nodes) and the count from nodes in sub graphs
            subnodes_count.append(nsubnodes)
            
            #run interdependency analysis using the list of subnodes removed from network, as some nodes in B may be dependent on them      
            #print 'subnodes are ', subn
            x=0
            while x<len(subn):
                xd = 0
                while xd<len(subn[x]):
                    node=subn[x][xd]
                    #print 'checking node ', node, 'is not part of a dependency'
                    GtempA, GtempB, node_count_removed_B, to_b_nodes, from_a_nodes, inter_removed_count, temp_store = check_inter_edges(GtempA, GtempB, node, node_count_removed_B, to_b_nodes, from_a_nodes, subnodes_A, subnodes_B, isolated_nodes_A, isolated_nodes_B, inter_removed_count, temp)
                    xd += 1
                x += 1 
            inter_removed_nodes.append(temp) #append all nodes removed due to broken depende link no matter what the cause for that break
        elif num_edges == 0:
            subnodes.append([])
            subnodes_count.append(0)            
        num_edges = GtempA.number_of_edges()  #recalc 
        if num_edges == 0: #if the graph is now dissconnceted, stop iterative process, leading to the results 
            #print 'the number of edges is ', num_edges, ' this should be the end!!'       
            i = 999999999 #set i really high so stops process 
            path_length.append(00000.000000) #append a path length of zero as no edges left in network
        elif num_edges <> 0:
            path_length.append(nx.average_shortest_path_length(GtempA,length)) #as not dissconnected, calc average path length 
        count_nodes_left.append(GtempA.number_of_nodes())
        return GtempA, GtempB, isolated_nodes,subnodes,path_length,i,node_count_removed,subnodes_count,isolated_n_count_removed, to_b_nodes, from_a_nodes, count_nodes_left,node_count_removed_B,inter_removed_count, inter_removed_nodes,numofcomponents

def analysis_B(parameters,iterate,Gtemp,i,to_a_nodes,from_b_nodes,node_list,basic_metrics,option_metrics,to_b_nodes, from_a_nodes):                
        '''Run some analaysis.....'''
        #------------unpack the holding variables------------------------------
        metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges = parameters
        nodes_removed,node_count_removed,count_nodes_left,number_of_edges,number_of_components = basic_metrics
        size_of_components,giant_component_size,av_nodes_in_components,isolated_nodes,isolated_n_count,isolated_n_count_removed,subnodes,subnodes_count,path_length,av_path_length_components,giant_component_av_path_length,av_path_length_geo,average_degree,inter_removed_count= option_metrics
        isolated_n_count.append(len(nx.isolates(Gtemp)))
        #------------check the variables and run appropriate analysis----------
        if REMOVE_ISOLATES == True:
            Gtemp,node_list,isolated_nodes,isolated_n_count_removed,node_count_removed,to_b_nodes,from_a_nodes = remove_isolates(Gtemp,node_list,isolated_nodes,isolated_n_count_removed,node_count_removed,to_b_nodes,from_a_nodes)
        elif REMOVE_ISOLATES <> False:
            sys.exit()
        #------------run some analysis/metric calcs----------------------------
        num_edges = Gtemp.number_of_edges()        
        if num_edges <> 0: #if the graph is not dissconnected                      
            nodelists = Gtemp.nodes()
            edgelists = Gtemp.edges()
            #if subgraphs are to be removed for the analysis ie. for infrastructure modelling
            if REMOVE_SUBGRAPHS == True:     
                #put the network through the handle-subgraphs function - will remove any nodes part of subgraphs
                Gtemp, subn, nsubnodes, nodelists, edgelists = handle_sub_graphs(nodelists, edgelists) 
                #where needed, add the removed nodes/info to the respective lists
                if subnodes <> False: subnodes.append(subn)
                #add onto the current value for nodes removed those removed as part of subgraphs
                node_count_removed.append(node_count_removed.pop() + nsubnodes)
                if subnodes_count <> False: subnodes_count.append(nsubnodes)
                #clean the node list of nodes removed as part of subgraphs
                clean_node_lists(subn,node_list,to_b_nodes,from_a_nodes)
            #if subgraphs are to be left as part of the network 
            elif REMOVE_SUBGRAPHS == False:
                #get a list of all connected components
                temp = nx.connected_component_subgraphs(Gtemp)
                #add the number components to the respective list
                number_of_components.append(len(temp))
                #calcualte the averge path length if needed
                if path_length <> False:     
                    av_path_length_components.append(whole_graph_av_path_length(Gtemp))
                #add the size of components to the respective list
                if size_of_components <> False: size_of_components.append(temp)   
            else:
                #there is an error with the variable
                print 'ERROR! Variable REMOVE_SUBGRAPHS must be set as True or False only.'
                sys.exit()
                
        #------------run if no edges left--------------------------------------
        elif num_edges == 0:
            #at the last removal of a node, all remaining edges were consequently removed
            #update the metrics
            if subnodes <> False: subnodes.append([])
            if subnodes_count <> False: subnodes_count.append(0)
        #------------re-calc the number of edges-------------------------------
        #this is needed if subgraphs were removed
        numofedges = Gtemp.number_of_edges()
        #------------if there are no edges left--------------------------------
        if numofedges == 0: 
            #set i really high so iteraion stops at the end of this step
            i = 999999999
            #add values for the metrics which are not set as False
            if path_length <> False: path_length.append(00000.000000)
            if giant_component_av_path_length <> False: giant_component_av_path_length.append(0.0)
            if giant_component_size <> False: giant_component_size.append(0)
            if average_degree <> False: average_degree.append(0)
            if number_of_components <> False: number_of_components.append(nx.number_connected_components(Gtemp))
            number_of_edges.append(0)
            #set iterate as False so it stops after this time step
            iterate = False
            
        #------------if the number of edge is greater than zero----------------
        elif numofedges <> 0:
            if path_length <> False:
                #claculates the average path length of the whole network if not dissconnected
                average = whole_graph_av_path_length(Gtemp)
                path_length.append(average)
            if giant_component_av_path_length <> False:
                #gets a lists of the connected components
                gbig = nx.connected_component_subgraphs(Gtemp)
                #gets the average path length in the largest connected component
                av_len = nx.average_shortest_path_length(gbig[0])
                giant_component_av_path_length.append(av_len)
            if giant_component_size <> False: 
                #gets the size of the largest connected component
                giant_component_size.append((nx.connected_component_subgraphs(Gtemp)[0]).number_of_nodes()) #get the number of ndoes in the largest component
            if av_nodes_in_components <> False: av_nodes_in_components.append(Gtemp.number_of_nodes()/len(nx.connected_component_subgraphs(Gtemp)))  
            #add the number of edges to the respective list
            number_of_edges.append(Gtemp.number_of_edges())
            
            if average_degree <> False:            
                degree_list = Gtemp.degree()
                sumh = 0.0
                for d in degree_list:    
                    sumh += degree_list[d]
                average_degree.append(sumh/(Gtemp.number_of_nodes()))
        #------------run final calculation-------------------------------------
        #add thenumber of nodes left to the respective list
        count_nodes_left.append(Gtemp.number_of_nodes())
        #------------package metric into containers----------------------------
        basic_metrics = nodes_removed,node_count_removed,count_nodes_left,number_of_edges,number_of_components
        option_metrics = size_of_components,giant_component_size,av_nodes_in_components,isolated_nodes,isolated_n_count,isolated_n_count_removed,subnodes,subnodes_count,path_length,av_path_length_components,giant_component_av_path_length,av_path_length_geo,average_degree,inter_removed_count
        return iterate,Gtemp,i,to_b_nodes,from_a_nodes,node_list,basic_metrics,option_metrics 

def outputresults(graphparameters, parameters,logfilepath=None,multiiterations=None):
    '''Controls how the results are output.
    Inputs: graphparametes and parameters containers
    Returns: all sets of metrics in a single container '''
    error = None
    #unpacking the variables
    networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics = graphparameters    
    #if more than one simualtion has been run over the same network
    if multiiterations <> None:
        #send to the method for calculating the averages and writing the results out
        basic_metrics_A, basic_metrics_B, option_metrics_A, option_metrics_B, error = average_txtresults(graphparameters, parameters,error)
        #if an error occurs
        if error <> None:
            print 'Error in calculating the averages for the output.'
            exit()
    else:
        #unpack the parameters
        metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges = parameters
        try:
            #open output file
            outputfile = open(fileName,'a')
        except:
            print 'Error. Could not open text file to write results to. File attempted was:', fileName,
            exit()
        #send to the textout function to write the results out
        txtout(outputfile,graphparameters, parameters)
    #pack the metric values together again
    values = basic_metrics_A, basic_metrics_B, option_metrics_A, option_metrics_B  
    return values,error       
    
def average_txtresults(graphparameters, parameters,error):
    '''Reads a txt file with results in and produces an average set and writes 
    back to the same text file.'''
    #unpack the graphparameters and parameters
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges = parameters
    networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics = graphparameters
    #open file which contains all the results form the simulations
    fread = open(fileName, 'r')
    #list of metrics - these are then added to a list for network A and B
    line_index = ['took this many steps','nodes removed','count removed nodes',
                  'number of nodes left','number of edges','number of components',
                  'size of each component','number of ndoes in giant component',
                  'average size of components','isolated nodes','isolated nodes count',
                  'numer of isolates removed','subnodes','number of subnodes',     
                  'average path length for network','average path length per component',
                  'average path length in giant', 'average path length for network geo',
                  'average degree','inter removed count']

    #create variables required
    network_is = 'A'
    dependency = False
    temp_metrics_A = []
    temp_metrics_B = []
    #append the names of the metrics to the two lists
    j = 0
    while j < len(line_index):
        temp_metrics_A.append([])
        temp_metrics_B.append([])
        j+=1
    #read each line of the text file
    for line in fread:
        #if the line starts with the network, identify if A or B
        if line.startswith('NETWORK'):
            network_is = line[8:]
            network_is = network_is.strip()
        #need to work out what this does or if I need it
        elif line.startswith('The analysis') or line.startswith('Start size'):
            pass
        else:
            i = 0
            #loop through the list of metric names
            while i < len(line_index):
                #check if the line starts with the meric name in the list at position i
                if line.startswith(line_index[i]):
                    #if found, split the line
                    try:
                        a,b = line.split(',[')
                    except:
                        #if can't split the line, there must be an error in the text file
                        print 'Error. Could not read in the text file for the average results.'
                        error = 0045
                        return basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B,error
                    #once split, edit the string to make it readable
                    b = b.replace('[','');b=b.replace(']','')
                    b = b.split(',')
                    #loop through the items, adding them to the 'temp' list
                    temp = []
                    for items in b:
                        items = items.strip()
                        if items <> "['\n']":
                            try:
                                temp.append(float(items))
                            except:
                                #if cant convert to a float, exit.
                                print 'Error. Could not convert what should be a numerical value to a float when calcautig the average of the results.'
                                exit()
                    #if more than one value read
                    if len(temp) <> 0:
                        #find out for which network the result is for and append to the respective list
                        if network_is == 'A':
                            temp_metrics_A[i].append(temp)
                        elif network_is == 'B':
                            dependency = True
                            temp_metrics_B[i].append(temp)
                        else:
                            print 'Error. The network the values are assoicated with was not found when calcualting the averages for the output.'
                            exit()
                    #stop looping through once found the metric and move on
                    break
                i += 1
    #close the resuls file
    fread.close()
    #open the file for writing the results to
    fwrite = open(fileName, 'a')    
    #loop through the teo network metric lists
    y = 0; r = 0    
    while r < 2:
        #get the metrics for the respective network
        if r == 0:
            temp_metrics = temp_metrics_A        
        elif r == 1: 
            temp_metrics = temp_metrics_B
        else: 
            print 'Error. Major error in average results.'
            exit()
        
        #go through each of the metrics in the list
        metriclist = []
        while y < len(temp_metrics):
            temp_metric = temp_metrics[y]
            #calc average for each of metrics
            #find the length of the longest list for the metric
            if len(temp_metric) <> 0:
                max_len = 0                
                for items in temp_metric:
                    if len(items) > max_len:
                        max_len = len(items)
                #calculate the average at each time step across each set of results for the metric
                p = 0
                temp = []
                #the number of simulations performed
                num_of_iterations = len(temp_metric)
                while p < max_len:
                    k = 0
                    mean = 0
                    #get the value at the time step foe each simulation and sum them together
                    while k < num_of_iterations:
                        try:
                            mean += float(temp_metric[k][p])
                        except: 
                            #if can't get a value as for the specific simualtion finished quicker then one of the others
                            pass
                        k += 1
                    #get the average value
                    temp.append(mean/num_of_iterations)
                    p += 1
                #append the average value
                metriclist.append(temp)
            else:
                #if the metric was not used, thus append False instead
                metriclist.append(False)
            y+=1
            
        p = 0
        #write which network this set of results are for
        if r == 0: 
            fwrite.write('NETWORK A\n')
        elif r ==1:
            fwrite.write('NETWORK B\n')
        #for each metric that might have been calculated, write the results out
        while p < len(line_index):
            if metriclist[p]==False:
                fwrite.write(str(line_index[p])+', NA\n')
            else:
                fwrite.write(str(line_index[p]) + ',' + str(metriclist[p]) + '\n')
            p += 1
        
        if r == 0: metriclist_A = metriclist
        elif r == 1: metriclist_B = metriclist
        #if only single analysis has been perfomed, change r so loop stops
        if dependency == False: r = 100
        r += 1
        
    #close the connection to the text file
    fwrite.close()
    #create blnk lists for A to staore the average results
    basic_metrics_A = [];option_metrics_A = []
    #create blank lists for network B if needed
    if dependency == True: basic_metrics_B = [];option_metrics_B = []
    #iterate through the possible mettrics used    
    i = 1
    while i < len(line_index):
        #while i is less than six, these are regarded as the basic metrics
        if i < 6:
            basic_metrics_A.append(metriclist_A[i])
            if dependency == True: basic_metrics_B.append(metriclist_B[i])
        #for all other metics, add to the optional lists
        elif i > 5 and i < len(line_index):
            option_metrics_A.append(metriclist_A[i])
            if dependency == True: option_metrics_B.append(metriclist_B[i])
        i += 1
  
    return basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B,error
    
def results(basic_metrics_A, basic_metrics_B): #pritn out and write out the results
    '''Prints some results to the console.
    Inputs: basic metrics set for network A and B
    Returns: Nothing '''
    nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A = basic_metrics_A
    nodes_removed_B,node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B = basic_metrics_B
    print 'NETWORK A'    
    print 'nodes_removed_A: ', nodes_removed_A
    print 'number_of_edges_A: ', number_of_edges_A
    print 'node_count_removed_A: ', node_count_removed_A
    print 'count_nodes_left_A: ', count_nodes_left_A
    print 'number_of_components_A: ', number_of_components_A
    if STAND_ALONE == False:  
        print 'NETWORK B'    
        print 'nodes_removed_B: ', nodes_removed_B
        print 'number_of_edges_B: ', number_of_edges_B    
        print 'node_count_removed_B: ', node_count_removed_B
        print 'count_nodes_left_B: ', count_nodes_left_B
        print 'number_of_components_B: ', number_of_components_B 

def write_text_file(outputfile,CASCADING,basic_metrics,option_metrics):
    '''Writes the metrics to the text file.
    Inputs: file operand, CASCADING variable, basic_metrics set and option_metrics set
    Returns: Nothing'''
    #unpack the variables
    nodes_removed,node_count_removed,count_nodes_left,number_of_edges,number_of_components = basic_metrics
    size_of_components,giant_component_size,av_nodes_in_components,isolated_nodes,isolated_n_count,isolated_n_count_removed,subnodes,subnodes_count,path_length,av_path_length_components,giant_component_av_path_length,av_path_length_geo,average_degree,inter_removed_count = option_metrics

    #write the basic metrics to the text file - if not set as False
    if nodes_removed <> False:
        outputfile.write('\nnodes removed,' + str(replace_all(str(nodes_removed), {',':';','];':'],'})))
    if node_count_removed <> False:
        outputfile.write('\ncount removed nodes,' + str(node_count_removed))
    if count_nodes_left <> False:
        outputfile.write('\nnumber of nodes left,' + str(count_nodes_left))   
    if number_of_edges <> False:
        outputfile.write('\nnumber of edges,' + str(number_of_edges))        
    if number_of_components <> False:
        outputfile.write('\nnumber of components,' + str(number_of_components))    
    #write the optional metrics to the rext file - if not set as False
    if size_of_components <> False:
        outputfile.write('\nsize of each component,' + str(replace_all(str(size_of_components),{',':';','];':'],'})))
    if giant_component_size <> False:
        outputfile.write('\nnumber of nodes in giant component,' + str(giant_component_size))
    if av_nodes_in_components <> False:
        outputfile.write('\naverage size of components,' + str(av_nodes_in_components))
    if isolated_nodes <> False:
        outputfile.write('\nisolated nodes,' + str(replace_all(str(isolated_nodes), {',':';','];':'],'})))
    if isolated_n_count <> False:
        outputfile.write('\nisolated node count,' + str(str(isolated_n_count)))
    if isolated_n_count_removed <> False:
        outputfile.write('\nisolated node count,' + str(isolated_n_count_removed))
    if subnodes <> False:
        outputfile.write('\nsubnodes,' + str(replace_all(str(replace_all(str(subnodes) , {',':';',']];':']],'})),{'[];':','})))
    if subnodes_count <> False:
        outputfile.write('\nsubnodes count,' + str(subnodes_count))  
    if path_length <> False:
        outputfile.write('\naverage path length for whole graph,' + str(path_length))        
    if av_path_length_components <> False:
        outputfile.write('\naverage path length for each component,' + str(replace_all(str(av_path_length_components),{',':';','];':'],'})))
    if giant_component_av_path_length <> False:
        outputfile.write('\naverage path length of giant component,' + str(giant_component_av_path_length))
    if average_degree <> False:
        outputfile.write('\naverage degree,' + str(average_degree))
    #if cascding failure write the node removed
    if CASCADING == True:
        outputfile.write('\nnodes removed A,' + str(replace_all(str(nodes_removed_A), {',':';','];':'],'})))
    
def txtout(outputfile,graphparameters, parameters):        
    '''Writes the results to a specified text file.
    Inputs: the file operand, the graphparameters (metrics etc) and the parameters
    Returns: Nothing'''
    #unpack the variables
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges = parameters    
    networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics = graphparameters    
    GA, GB, GtempA, GtempB = networks
    nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A = basic_metrics_A     
    size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,inter_removed_count_A = option_metrics_A
    #if not just single analysis, unpack emtrics for network B as well
    if STAND_ALONE == False:
        nodes_removed_B,node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B = basic_metrics_B
        size_of_components_B,giant_component_size_B,av_nodes_in_components_B,isolated_nodes_B,isolated_n_count_B,isolated_n_count_removed_B,subnodes_B,subnodes_count_B,path_length_B,av_path_length_components_B,giant_component_av_path_length_B,av_path_length_geo_B,average_degree_B,inter_removed_count_B = option_metrics_B
    else: basic_metrics_B = None; option_metrics_B = None
    #write the parameters for the analysis out
    outputfile.write('\nThe analysis parameters were:')    
    if SINGLE == True: outputfile.write('SINGLE = True, ')
    elif SEQUENTIAL == True: outputfile.write('Sequential = True, ')
    elif CASCADING == True: outputfile.write('Cascading = True, ') 
    else: outputfile.write('Error!')
    
    if RANDOM == True: outputfile.write('RANDOM = True')
    elif DEGREE == True: outputfile.write('DEGREE = True')
    elif BETWEENNESS == True: outputfile.write('BETWEENNESS = True')
    else: outputfile.write('Error!')    
    #write the options used out
    if REMOVE_SUBGRAPHS == True: outputfile.write(', REMOVE_SUBGRAPHS = True')
    if REMOVE_ISOLATES == True: outputfile.write(', REMOVE_ISOLATES = True')
    if NO_ISOLATES == True: outputfile.write(', NO_ISOLATES = True')
    #write out the first few lines for network A
    outputfile.write('\nNETWORK A')
    outputfile.write('\nStart size, ' + str(GA.number_of_nodes()))
    outputfile.write('\nTook this manny steps: '+ str(len(count_nodes_left_A)-1))
    #use the function to write the metric results out for the network A
    write_text_file(outputfile,CASCADING,basic_metrics_A,option_metrics_A)     
    #write the results for the metrics for network B using the function
    if STAND_ALONE == False:
        outputfile.write('\nNETWORK B')
        write_text_file(outputfile,CASCADING,basic_metrics_B,option_metrics_B)
        
def replace_all(text, dic):
    ''''''
    for i,j in dic.iteritems():
        text = text.replace(i,j)
    return text
    
'''main control function''' 
'''connect to database and create networkx graph'''
'''set the analysis type and initaite that'''
def main(GA,GB,parameters,logfilepath,viewfailure = False):
    '''This is the main control function when the analysis is run directly from 
    the script. This reads in the data provided and processes it as such to run 
    the desired analysis.
    Input: two networks and the parameters
    Returns: a boolean varalible dictating if the analysis has been completed'''
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges = parameters

    #rename networks
    GnetA = GA   
    if STAND_ALONE == True: #create empyt GnetB
        GnetB = nx.Graph()    
    else:
        GnetB = GB 
    #creates the containers for the selected varaibles and calc the initial values
    graphparameters = core_analysis(GA, GB, parameters)
    iterate = True    
    #run the analysis if seuquential or cascading == true
    if SEQUENTIAL == True or CASCADING == True:
        #while iterate is still true- network still has edges eleft
        while iterate == True:
            #update log file - only works if file path is set
            write_to_log_file(logfilepath,'initiating step')
            #run the time step
            graphparameters, iterate = step(graphparameters, parameters, iterate,logfilepath)
            #update logfile - only works if file path is set
            write_to_log_file(logfilepath,'step completed')
        if iterate == False:
            #no edges left so output results
            outputresults(graphparameters, parameters,logfilepath)            
            return
    complete = True
    #update log file - only works if file path is set
    write_to_log_file(logfilepath,'completed analysis')
    return complete

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

def failure_type(SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS):
    '''Generates a string describing the analysis being run.
    Input: analysis parameters
    Returns: a single string'''
    if SINGLE == True: failure = 'Single'
    elif SEQUENTIAL == True: failure = 'Sequential'
    elif CASCADING == True: failure = 'Cascading' 
    
    if RANDOM == True: typ = 'Random'
    elif DEGREE == True: typ = 'Degree'
    elif BETWEENNESS == True: typ = 'Betweenness'
    #add togetehr to create a single string
    failuretype = '%s_%s' % (failure, typ)
    return failuretype
    
def analyse_existing_networks(NETWORK_NAME, conn, db, parameters, noioa, use_db, use_csv, logfilepath):
    ''''''
    #unpack varaibles
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName1, a_to_b_edges = parameters
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
                    filepath = str(file_path)+'%s/%s.txt' %(db, nets)
                    nodelist, edgelist = get_nodes_edges_csv(filepath)
                    #build the network from the litss returned from the function
                    G = nx.Graph()
                    G.add_nodes_from(nodelist)
                    G.add_edges_from(edgelist)
                #set the name of the results text file
                fileName = str(fileName1)+'%s/%s%s.txt'%(db,nets,failuretype)
                #package the parameters together
                parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges
                #need a value for network B (G2)
                G2 = None
                #perform the analusis
                main(G, G2, parameters, logfilepath)
                iterations += 1
    #if dependency or intersedpendcy
    elif STAND_ALONE == False:
        #get both networks from csv
        filepath = str(file_path)+'%s/%s.txt' %(db, NETWORK_NAME[0])
        nodelist, edgelist = get_nodes_edges_csv(filepath)
        G1 = nx.Graph()
        G1.add_nodes_from(nodelist)
        G1.add_edges_from(edgelist)
        filepath = str(file_path)+'%s/%s.txt' %(db, NETWORK_NAME[1])
        nodelist, edgelist = get_nodes_edges_csv(filepath)
        G2 = nx.Graph()
        G2.add_nodes_from(nodelist)
        G2.add_edges_from(edgelist)
        main(G1, G2, parameters,logfilepath)
        pass
    else:
        print 'STAND ALONE must have a status'
        sys.exit()
        
if __name__ == "__main__":
    #------------------type of failure-----------------------------------------
    STAND_ALONE = False; DEPENDENCY = True; INTERDEPENDENCY = False 
    #------------------method of failure---------------------------------------
    SINGLE = False; SEQUENTIAL = True; CASCADING = False
    #------------------node selection method-----------------------------------
    RANDOM = True; DEGREE = False; BETWEENNESS = False
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
    #fileName1 = 'H:/robustness/results/' #for desktop
    fileName1 = 'C:/a8243587_DATA/Dropbox/result.txt'
    #fileName1 = 'C:/Users/Craig/Dropbox/robustness/results/' #for laptop
    #------------------path name for the input files---------------------------
    file_path = 'H:/robustness/csv_network_data/'
    #file_path = 'C:/Users/Craig/Dropbox/robustness/csv_network_data/'
    #------------------auto generate text for failure model--------------------
    failuretype = failure_type(SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS)
    #------------------single quick analysis-----------------------------------
    #GA = nx.gnm_random_graph(50,369)
    edges = [(1,3),(2,4),(1,2),(1,4),(3,4),(4,5)]
    GA = nx.Graph()
    GA.add_edges_from(edges)
    
    if STAND_ALONE == True: GB = None
    else: 
        #GB = nx.gnm_random_graph(34,145)
        edges = [(1,2),(1,3),(1,4),(2,4),(4,3)]     
        GB = nx.Graph()
        GB.add_edges_from(edges)
    #------------------setting of dependency edges-----------------------------
    if DEPENDENCY == True or INTERDEPENDENCY == True:
        a_to_b_edges = [(3,1),(3,2),(5,3)]
        if INTERDEPENDENCY == True:
            b_to_a_edges = []
    else:
        a_to_b_edges = None       
    
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
    basic_metrics_A =  nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A
    option_metrics_A = size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,inter_removed_count_A
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
        parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName1, a_to_b_edges
        NETWORK_NAME = file_1_name, file_2_name #list the name of the two networks for the analysis
        conn = None; noia = 1
        analyse_existing_networks(NETWORK_NAME,conn,db,parameters,noia,use_db,use_csv)
    elif DEPENDENCY == True and mass == False:
        parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName1, a_to_b_edges
        complete = main(GA, GB, parameters,logfilepath)
        print complete
    elif mass == False and STAND_ALONE == True: #for single network analysis
        parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName1, a_to_b_edges
        complete = main(GA, GB, parameters,logfilepath)
        print complete
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
        parameters = metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName1, a_to_b_edges

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
        print 'check analysis parameters'
  

