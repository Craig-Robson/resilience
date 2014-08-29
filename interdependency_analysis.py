 # -*- coding: utf-8 -*-
""" Previuosly was v14, the most up to date and working code
Created on Mon Jul 23 14:26:27 2012

@author: Craig Robson
"""
'''

**********
Version 5_4_0 - integrates the use of dicts rather than lists for the
storage of the graph metrics.

Version 5_4_1 - will start to tidy up parameters and the two sets of containers

Last good version - 5_3_3
**********

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
        
'''
__author__ = "Craig Robson"
__created__ = ""
__year__ = "2014"
__version__ = "5.3.2"

#standard modules
import sys, random
import networkx as nx

#custom modules
sys.path.append("C:/Users/Craig/Dropbox/resilience_module/resilience_modules")
sys.path.append("C:/a8243587_DATA/Dropbox/resilience_module/resilience_modules")
import tools, error_classes, failure_methods
import network_handling_v1_4_0 as network_handling
import outputs_v1_4_0 as outputs


def main(GA, GB, parameters, logfilepath, viewfailure=False):
    '''
    This is the main control function when the analysis is run directly from 
    the script. This reads in the data provided and processes it as such to run 
    the desired analysis.
    Input: up to two networks, parameters and a logfile path.
    Returns: a boolean varalible stating if the analysis has been completed.
    '''
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges, write_step_to_db, db_parameters, length = parameters

    #creates the containers for the selected varaibles and calc the initial values
    #graphparameters = create_containers(GA, GB, parameters)
    graphparameters = metrics_initial(GA,GB,parameters)

    iterate = True    
    #run the analysis if seuquential or cascading == true
    if SEQUENTIAL == True or CASCADING == True:
        #while iterate is still true- network still has edges eleft
        while iterate == True:
            #update log file - only works if file path is set
            tools.write_to_log_file(logfilepath,'initiating step')
            #run the time step
            graphparameters,iterate = step(graphparameters, parameters, iterate,logfilepath)
            #update logfile - only works if file path is set
            tools.write_to_log_file(logfilepath,'step completed')
        if iterate == False:
            #no edges left so output results
            outputs.outputresults(graphparameters,parameters,logfilepath=None)
    complete = True
    #update log file - only works if file path is set
    tools.write_to_log_file(logfilepath,'completed analysis')
    return complete

def step(graphparameters, parameters, iterate, logfilepath):
    '''
    Performs one time step of analysis when called.
    Inputs: graphparameters, parameters iterate 
    Returns: graphparameters, iterate
    '''
    #----------------unpack all the data containers----------------------------
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges, write_step_to_db, db_parameters, length = parameters    
    networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics = graphparameters
    GA, GB, GtempA, GtempB = networks
    
    #----------------perform the analsis---------------------------------------
    #----------------for sequential analysis only------------------------------
    if SEQUENTIAL == True and SINGLE == False and CASCADING == False:
        if DEGREE == True:
            #find node based on highest degree and remove it
            GtempA,node = failure_methods.sequential_degree(GtempA,INTERDEPENDENCY)
        elif BETWEENNESS == True:
            #find node with highest betweenness value and remove it           
            GtempA,node = failure_methods.sequential_betweenness(GtempA,INTERDEPENDENCY)
        elif RANDOM == True:
            #randomly select the next node and remove it
            GtempA,node = failure_methods.sequential_random(GtempA, NO_ISOLATES,INTERDEPENDENCY)
        #update the counter
        basic_metrics_A['no_of_nodes_removed'].append(len(basic_metrics_A['no_of_nodes_removed']))
    
    #----------------for cascading analysis------------------------------------
    elif CASCADING == True and SINGLE == False and SEQUENTIAL == False: 
        #unpack the cascading metrics and create some blank containers
        dead, dlist, removed_nodes, deadlist = cascading_metrics
        #------------identify subnodes and isolated nodes--------------------
        for g in nx.connected_component_subgraphs(GtempA):
            if g.number_of_nodes == 1:
                option_metrics_A['isolated_nodes'].append(g.nodes())
            elif g.number_of_nodes <> 0:
                option_metrics_A['subnodes'].append(g.nodes())
            else:
                raise error_classes.GeneralError('Error. Component has zero nodes.')
        #------------on the first time step only-----------------------------
        #need to initaite the failure through remoiving a node to begin with
        if i == 0:
            if DEGREE == True and BETWEENNESS == False and RANDOM == False:
                ma, dead = tools.max_val_random(nx.degree(GtempA))
            elif BETWEENNESS == True and RANDOM == False and DEGREE == False:
                ma, dead = tools.max_val_random(nx.betweenness_centrality(GtempA))
            elif RANDOM == True and DEGREE == False and BETWEENNESS == False:
                dead = dead
            #update the network and find the next set of nodes to remove
            GtempA,dlist,removed_nodes,deadlist = failure_methods.cascading_failure(GtempA,dlist,dead,i,basic_metrics_A['subnodes'], basic_metrics_A['isolated_nodes'],basic_metrics_A['nodes_removed'],INTERDEPENDENCY)
            node = deadlist
            
        #------------on all but first time step------------------------------
        else:
            #update the network and find the next set of nodes to remove
            GtempA,dlist,removed_nodes,deadlist = failure_methods.cascading_failure(GtempA,dlist,dead,i,option_metrics_A['subnodes'],option_metrics_A['isolated_nodes'],basic_metrics_A['nodes_removed'],INTERDEPENDENCY)         
            node = deadlist
        
        #update metric
        basic_metrics_A['no_of_nodes_removed'].append(basic_metrics_A['no_of_nodes_removed'][i] + len(deadlist))

        #------------package cascading metrics together----------------------
        cascading_metrics = dead, dlist, removed_nodes, deadlist

    #----------------for single analysis---------------------------------------
    elif SINGLE == True and SEQUENTIAL == False and CASCADING == False:
        #create a copy of the original network - will be complete
        GtempA = GA.copy()
        #select and remove a node from the network
        GtempA,node = failure_methods.single_random(GtempA, node_list, INTERDEPENDENCY)
        #------------when node list is empty change iterate------------------
        if node_list == []:
            iterate = False
        #update the metric
        basic_metrics_A['no_of_nodes_removed'].append(len(basic_metrics_A['no_of_nodes_removed']))
        #node_count_removed_A.append(len(node_count_removed_A))
        
    #----------------update the list of removed nodes--------------------------
    basic_metrics_A['nodes_removed'].append(node)
    
    #----------------re-package networks and metrics which have been changed---   
    networks = GA, GB , GtempA, GtempB

    #----------------functions for analysis methods----------------------------
    if INTERDEPENDENCY == True:
        pass
        #this in case in future we start removing nodes from both networks

    '''Run the post node removal analysis''' #biggest area which needs updating
    if INTERDEPENDENCY == True and STAND_ALONE == False and DEPENDENCY == False :
        '''Needs to be developed'''
        
    elif DEPENDENCY == True and STAND_ALONE == False and INTERDEPENDENCY == False :
        '''
        Needs to be updated. Uses A and B. Not sure on state of A or why A is needed at all
        need to find out what the main metrics are which are NEEDED for dependency analysis
        a_to_b_edges holds the connecting edges between the networks
        '''
        #special one for cascading as loop needed to handle multiple network A nodes being removed in one iteration
        #to store all nodes for intire iteration which are removed from networkB due to broken dependence link
        temp = []
        #------------if cascading analysis-----------------------------------
        #this needs checking
        if CASCADING == True: 
            x = 0
            while x < len(deadlist):
                node = deadlist[x]
                GtempA, GtempB, to_b_nodes, from_a_nodes, temp = network_handling.check_dependency_edges(GtempA, GtempB, node, to_b_nodes, from_a_nodes, temp)
                x += 1
        #------------run for all other analysis scenarios--------------------
        else:
            args = network_handling.check_dependency_edges(networks,node,basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B,to_b_nodes,from_a_nodes,temp)
            if args == 0001:
                raise error_classes.SearchError('Error. Could not find chosen node to remove it.')
                tools.write_to_log_file(logfilepath, 'ERROR %s; Could not find chosen node ro remove (check_dependency_edges).' %(args))
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
        raise error.classes.GeneralError('Error. No analysis type has been selected.')

    #----------------re-package all data into respective containers------------
    networks = GA, GB, GtempA, GtempB
    graphparameters = networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics   
    if write_step_to_db:
        done = outputs.write_to_db(graphparameters,parameters)
    
    write_results_table=True    
    if write_results_table:
        outputs.write_results_table(basic_metrics_A,option_metrics_A,basic_metrics_B,option_metrics_B,i,STAND_ALONE,db_parameters) #network a
    networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics= graphparameters
    GA,GB,GtempA,GtempB = networks
    return graphparameters, iterate
 
'''calcualte values at end of step'''       
def analysis_B(parameters,iterate,Gtemp,i,to_a_nodes,from_b_nodes,node_list,basic_metrics,option_metrics,to_b_nodes, from_a_nodes):
        '''
        Run some analaysis.....
        '''
        #------------unpack the holding variables------------------------------
        metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges, write_step_to_db, db_parameters, length = parameters
    
        basic_metrics['no_of_isolated_nodes'].append(len(nx.isolates(Gtemp)))
        #------------check the variables and run appropriate analysis----------
        #after removing a node, there might be node edges left, need to check before sending to check for isolates
        if REMOVE_ISOLATES == True:
            if Gtemp.number_of_edges() <> 0:            
                Gtemp,node_list,option_metrics['isolated_nodes'],option_metrics['no_of_isolated_nodes_removed'],basic_metrics['no_of_nodes_removed'],to_b_nodes,from_a_nodes = network_handling.remove_isolates(Gtemp,node_list,option_metrics['isolated_nodes'],option_metrics['no_of_isolated_nodes_removed'],basic_metrics['no_of_nodes_removed'],to_b_nodes,from_a_nodes)
        elif REMOVE_ISOLATES == False:
            if option_metrics['no_of_isolated_nodes_removed'] <> False: option_metrics['no_of_isolated_nodes_removed'].append(0)
            if option_metrics['isolated_nodes_removed']<>False: option_metrics['isolated_nodes_removed'].append([])
            if option_metrics['isolated_nodes']<>False:option_metrics['isolated_nodes'].append([nx.isolates(Gtemp)])
        else:
            raise error_classes.GeneralError('Error. REMOVE_ISOLATES variable has become corrupt.')
        #------------run some analysis/metric calcs----------------------------
        num_edges = Gtemp.number_of_edges()        
        if num_edges <> 0: #if the graph is not dissconnected                      
            nodelists = Gtemp.nodes()
            edgelists = Gtemp.edges()
            #if subgraphs are to be removed for the analysis ie. for infrastructure modelling
            if REMOVE_SUBGRAPHS == True:     
                #put the network through the handle-subgraphs function - will remove any nodes part of subgraphs
                Gtemp, subn, nsubnodes, nodelists, edgelists = network_handling.handle_sub_graphs(nodelists, edgelists) 
                #where needed, add the removed nodes/info to the respective lists
                if option_metrics['subnodes'] <> False: option_metrics['subnodes'].append(subn)
                #add onto the current value for nodes removed those removed as part of subgraphs
                basic_metrics['no_of_nodes_removed'].append(basic_metrics['no_of_nodes_removed'].pop()+nsubnodes)
                if basic_metrics['no_of_subnodes'] <> False: basic_metrics['no_of_subnodes'].append(nsubnodes)
                #clean the node list of nodes removed as part of subgraphs
                node_list, to_b_nodes, from_a_nodes =  network_handling.clean_node_lists(subn,node_list,to_b_nodes,from_a_nodes)
            #if subgraphs are to be left as part of the network 
            elif REMOVE_SUBGRAPHS == False:
                #get a list of all connected components
                temp = nx.connected_component_subgraphs(Gtemp)
                #add the number components to the respective list
                basic_metrics['number_of_components'].append(len(temp))
                
                temp=[]
                if option_metrics['subnodes']<>False:
                    for g in nx.connected_component_subgraphs(Gtemp):
                        temp.append(g.nodes()) #list of subgraphs
                    count = 1 #ignore the first one
                    no_of_subnodes = 0
                    temp2 = []
                    while count < len(temp):
                        temp2.append(temp[count])
                        no_of_subnodes+=(len(temp[count]))
                        count+=1
                    option_metrics['subnodes'].append(temp2)
                    if option_metrics['no_of_subnodes']<>False:option_metrics['no_of_subnodes'].append(no_of_subnodes)
                #calcualte the averge path length if needed
                if option_metrics['path_length'] <> False:
                    option_metrics['avg_path_length_of_components'].append(network_handling.whole_graph_av_path_length(Gtemp))
                 
            else:
                #there is an error with the variable
                raise error_classes.GeneralError('Error. Variable REMOVE_SUBGRAPHS must be set as True or False only.')
                
        #------------run if no edges left--------------------------------------
        elif num_edges == 0:
            #at the last removal of a node, all remaining edges were consequently removed
            #update the metrics
            if option_metrics['subnodes'] <> False: option_metrics['subnodes'].append([])
            if option_metrics['no_of_subnodes'] <> False: option_metrics['no_of_subnodes'].append(0)
        #------------re-calc the number of edges-------------------------------
        #this is needed if subgraphs were removed
        numofedges = Gtemp.number_of_edges()
        #------------if there are no edges left--------------------------------
        if numofedges == 0: 
            #set i really high so iteraion stops at the end of this step
            i = -100
            #add values for the metrics which are not set as False
            if option_metrics['path_length'] <> False: option_metrics['path_length'].append(00000.000000)
            if option_metrics['path_length_of_giant_component']<> False: option_metrics['path_length_of_giant_component'].append(0.0)
            if option_metrics['giant_component_size'] <> False: option_metrics['giant_component_size'].append(0)
            if option_metrics['avg_degree'] <> False: option_metrics['avg_degree'].append(0)
            basic_metrics['number_of_components'].append(nx.number_connected_components(Gtemp))
            basic_metrics['number_of_edges'].append(0)
            #set iterate as False so it stops after this time step
            iterate = False
            
        #------------if the number of edge is greater than zero----------------
        elif numofedges <> 0:
            if option_metrics['path_length'] <> False:
                #claculates the average path length of the whole network if not dissconnected
                average = network_handling.whole_graph_av_path_length(Gtemp)
                option_metrics['path_length'].append(average)
                Gtemp.graph['apl']=average
            if option_metrics['path_length_geo']<>False:
                option_metrics['path_length_geo'].append(network_handling.whole_graph_av_path_length(Gtemp,length))
            if option_metrics['path_length_of_giant_component'] <> False:
                #gets a lists of the connected components
                gbig = nx.connected_component_subgraphs(Gtemp)
                #gets the average path length in the largest connected component
                av_len = nx.average_shortest_path_length(gbig[0])
                option_metrics['path_length_of_giant_component'].append(av_len)
            if option_metrics['giant_component_size'] <> False: 
                #gets the size of the largest connected component
                option_metrics['giant_component_size'].append((nx.connected_component_subgraphs(Gtemp)[0]).number_of_nodes()) #get the number of ndoes in the largest component
            if option_metrics['avg_nodes_in_components'] <> False: option_metrics['avg_nodes_in_components'].append(Gtemp.number_of_nodes()/len(nx.connected_component_subgraphs(Gtemp)))  
            #add the number of edges to the respective list

            basic_metrics['number_of_edges'].append(Gtemp.number_of_edges())
                            
            if option_metrics['avg_degree'] <> False:       
                degree_list = Gtemp.degree()
                sumh = 0.0
                for d in degree_list:    
                    sumh += degree_list[d]
                option_metrics['avg_degree'].append(sumh/(Gtemp.number_of_nodes()))
                Gtemp.graph['average_degree']=sumh/Gtemp.number_of_nodes()
            if option_metrics['density']<>False:option_metrics['density'].append(nx.density(Gtemp))
                
            #metrics added as attributes of nodes
            Gtemp = tools.add_node_field(Gtemp,'degree',Gtemp.degree())
            Gtemp = tools.add_node_field(Gtemp,'betweenness',nx.betweenness_centrality(Gtemp))
            Gtemp = tools.add_node_field(Gtemp,'clustering',nx.clustering(Gtemp))
            Gtemp = tools.add_node_field(Gtemp,'square_clustering', nx.square_clustering(Gtemp))
            Gtemp = tools.add_node_field(Gtemp,'avg_neighbour_degree',nx.average_neighbor_degree(Gtemp))
            
            #metrics added as attributes of edges
            Gtemp = tools.add_edge_field(Gtemp,'betweenness',nx.edge_betweenness_centrality(Gtemp))
        
        #add the number of nodes left to the respective list
        basic_metrics['no_of_nodes'].append(Gtemp.number_of_nodes())

        return iterate,Gtemp,i,to_b_nodes,from_a_nodes,node_list,basic_metrics,option_metrics 


def calc_initial_values(Gtemp, basic_metrics, option_metrics, length = None):
    '''
    Calculates all the initial values for the metrics selected to record 
    the performance of the network.
    '''
    print '**********************'
    print basic_metrics.keys()
    print option_metrics.keys()
    print '**********************'
    #calcualte the number of isolates - this is required
    basic_metrics['no_of_isolated_nodes'] = []
    basic_metrics['no_of_isolated_nodes'].append(len(nx.isolates(Gtemp)))
    #calculate the average degree of the nodes if not set as False    
    if option_metrics['avg_degree']<> False:
        #get the list of node degrees
        degreelist = Gtemp.degree()
        #get the sum of the list of values
        av_degree = sum(degreelist)
        option_metrics['avg_degree'].append(av_degree/nx.number_of_nodes(Gtemp))
    #calculate the average path length of the components ro for the whole network
    if option_metrics['avg_path_length_of_components'] <> False or option_metrics['path_length'] <> False:    
        geo_total = 0.0  
        sumtotal = 0.0      
        #go through the connected components and calcualte the average path length
        for g in nx.connected_component_subgraphs(Gtemp):
            av_path_length = nx.average_shortest_path_length(g)
            
            #if geo length metric has also been selected, calculate that as well
            if option_metrics['path_length_geo'] <> False:
                geo_sum_total = nx.average_shortest_path_length(g, length)
            #if wanted for the components, add to the respective list
            if option_metrics['avg_path_length_of_components'] <> False:
                option_metrics['avg_path_length_of_components'].append(av_path_length)
            
            sumtotal += av_path_length
            geo_total += geo_sum_total
            av_path_length = None
    
        #calculate the averages if requried
        if option_metrics['path_length_geo'] <> False:
            option_metrics['path_length_geo'].append(geo_total/nx.number_connected_components(Gtemp))
        
        if option_metrics['path_length'] <> False:
            option_metrics['path_length'] = []
            option_metrics['path_length'].append(sumtotal/nx.number_connected_components(Gtemp))
        sumtotal = None
    
    #if need the number of components, calcualte and append to the list
    if basic_metrics['number_of_components'] <> False:
        basic_metrics['number_of_components'].append(nx.number_connected_components(Gtemp))
    
    #if need the size of components, calcaulte and add to the list
    if option_metrics['size_of_components'] <> False:
        temp = []
        for g in nx.connected_component_subgraphs(Gtemp):
            temp.append(g.number_of_nodes())
        option_metrics['size_of_components'].append(temp)
        temp = None
         
    #if need the a list of isolates
    if option_metrics['isolated_nodes'] <> False:
        option_metrics['isolated_nodes'].append(nx.isolates(Gtemp))
    
    #if need count of number of nodes removed due to interdependent edges        
    if option_metrics['no_of_inter_removed'] <> False: 
        option_metrics['no_of_inter_removed'] = []
        option_metrics['no_of_inter_removed'].append(0)

    return basic_metrics, option_metrics
        

def create_containers(GnetA, GnetB, parameters):   
    '''
    Creates all the data containers and packages them all
    up into one varaible which can be used for the analysis.
    Inputs: network A, network B, parameters
    Outputs: graphparameters
    '''
    #unpack the paarameters
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges, write_step_to_db, db_parameters = parameters      
    #----------------unpack the metrics----------------------------------------
    basic_metrics_A, basic_metrics_B, option_metrics_A, option_metrics_B = metrics    
    #----------------sort a_to_b edges-----------------------------------------
    #when doing dependency and interdependency analysis, need to create lists 
    #of the nodes in each network affected by the links 
    from_a_nodes = []
    to_b_nodes = []
    if STAND_ALONE == False:
        for item in a_to_b_edges:
            from_a_nodes.append(item[0])
            to_b_nodes.append(item[1])
        if INTERDEPENDENCY == True:pass        
    #----------------sort the networks out-------------------------------------
    #make copies of the networks
    GA = GnetA.copy()
    if GnetB <> None:GB = GnetB.copy()
    else: GB = GnetB
    #----------------length attribute - if using geo lengths-------------------
    length = 'length' #None
    #-----------------------------############---------------------------------
    i = 0
    #----------------create data containers------------------------------------   
    # create a template blank list
    blnklist=[]
    #----------------for basic metrics-----------------------------------------
    #need to create all the data containers for the metrics which are set as True
    basic_metrics_A['nodes_removed'] = [[]] #nodes removed from network A
    basic_metrics_A['no_of_nodes'] = [GA.number_of_nodes()] #the number of nodes left in network A
    basic_metrics_A['number_of_edges'] = [GA.number_of_edges()] #number of edges in the network
    basic_metrics_A['number_of_components'] = [] #number of subgraphs/isolated nodes
    basic_metrics_A['no_of_nodes_removed'] = [0]
    
    if STAND_ALONE == False:
        basic_metrics_B['nodes_removed'] = [[]] #nodes removed from network A
        basic_metrics_B['no_of_nodes'] = [GA.number_of_nodes()] #the number of nodes left in network A
        basic_metrics_B['number_of_edges'] = [] #number of edges in the network
        basic_metrics_B['number_of_components'] = [] #number of subgraphs/isolated nodes
        basic_metrics_B['no_of_nodes_removed'] = [0]

    #----------------for optional metrics--------------------------------------
    if option_metrics_A['size_of_components']== True: option_metrics_A['size_of_components']=[]
    if option_metrics_A['giant_component_size']==True: option_metrics_A['giant_component_size']=[]
    if option_metrics_A['avg_nodes_in_components']==True: option_metrics_A['avg_nodes_in_components']=[]
    if option_metrics_A['isolated_nodes']==True: option_metrics_A['isolated_nodes']=[blnklist]#list of isolated nodes
    if option_metrics_A['no_of_isolated_nodes']==True: option_metrics_A['no_of_isolated_nodes']=[0]
    
    if REMOVE_ISOLATES == True or option_metrics_A['no_of_isolated_nodes']<>False:
        option_metrics_A['isolated_nodes_removed']=[0] #count the number of isolated nodes removed in the handle isolates function each step    
    if REMOVE_SUBGRAPHS == True or option_metrics_A['subnodes']==True or option_metrics_A['subnodes_count']==True:
        option_metrics_A['subnodes']=[blnklist] #nodes removed as part of isolated graphs
        option_metrics_A['no_of_subnodes']=[0] #count of nodes removed as part of subgraphs

    if STAND_ALONE == False:
        print option_metrics_B
        if option_metrics_B['size_of_components']== True: option_metrics_B['size_of_components']=[]
        if option_metrics_B['giant_component_size']==True: option_metrics_B['giant_component_size']=[]
        if option_metrics_B['avg_nodes_in_components']==True: option_metrics_B['avg_nodes_in_components']=[]
        if option_metrics_B['isolated_nodes']==True: option_metrics_B['isolated_nodes']=[blnklist]#list of isolated nodes
        if option_metrics_B['no_of_isolated_nodes']==True: option_metrics_B['no_of_isolated_nodes']=[0]
        if REMOVE_ISOLATES == True or option_metrics_B['no_of_isolated_nodes']<>False:
            option_metrics_B['isolated_nodes_removed']=[0] #count the number of isolated nodes removed in the handle isolates function each step    
            if REMOVE_SUBGRAPHS == True or option_metrics_B['subnodes']==True or option_metrics_B['subnodes_count']==True:
                option_metrics_B['subnodes']=[blnklist] #nodes removed as part of isolated graphs
                option_metrics_B['no_of_subnodes']=[0] #count of nodes removed as part of subgraphs
            
    if option_metrics_A['path_length']==True:option_metrics_A['path_length']=[] 
    if option_metrics_A['avg_path_length_of_components']==True:option_metrics_A['avg_path_length_of_components']=[]
    if option_metrics_A['path_length_of_giant_component']==True:option_metrics_A['path_length_of_giant_component']= []
    if option_metrics_A['avg_degree']==True:option_metrics_A['avg_degree']=[]
    
    if STAND_ALONE == False:
         if option_metrics_B['path_length']==True:option_metrics_B['path_length']=[] 
         if option_metrics_B['avg_path_length_of_components']==True:option_metrics_B['avg_path_length_of_components']=[]
         if option_metrics_B['path_length_of_giant_component']==True:option_metrics_B['path_length_of_giant_component']= []
         if option_metrics_B['avg_degree']==True:option_metrics_B['avg_degree']=[]
         if option_metrics_B['inter_removed_count']==True: option_metrics_B['inter_removed_count']= [0]
     
    #----------------specific metrics for interdependency----------------------
    if INTERDEPENDENCY == True:
        interdependency_metrics = {'inter_removed_nodes':[blnklist], 'inter_removed_count':[0]}
    else: interdependency_metrics = None
    
    #----------------specific metrics for cascading analysis-------------------
    if CASCADING == True:
        dead = random.choice(GA.nodes()) #set the initial node to be removed for the neighbour analysis
        dlist = [] #list to store nodes between iterations during nieghbour analysis
        removed_nodes=[] #list to store nodes during the nieghbor analysis
        deadlist = [] #neighbor analysis only: the nodes removed in the last iteration  
        cascading_metrics = dead, dlist, removed_nodes, deadlist
    else: cascading_metrics = None
        
    #----------------sort initial networks out again---------------------------
    #create a temp version of network to be used for all analysis
    GtempA = GA.copy() 
    if GB == None: GB = nx.Graph()
    GtempB = GB.copy()
    
    #generate a node list as need for some simulations    
    node_list = GA.nodes() #for single random analysis only
    
    #----------------calculate the initial values for network A----------------
    basic_metrics_A, option_metrics_A = calc_initial_values(GtempA,basic_metrics_A,option_metrics_A,length)
    
    #----------------calculate the initial values for network B----------------
    if STAND_ALONE == False:
        basic_metrics_B, option_metrics_B = calc_initial_values(GtempB,basic_metrics_B,option_metrics_B,length)
    
    #----------------package stuff up------------------------------------------
    networks = GA, GB, GtempA, GtempB
    graphparameters = networks,i,node_list, to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics
    return graphparameters

def metrics_initial(GnetA, GnetB, parameters):
    
    #unpack the paarameters
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges, write_step_to_db, db_parameters,length = parameters      
    #----------------unpack the metrics----------------------------------------
    basic_metrics_A, basic_metrics_B, option_metrics_A, option_metrics_B = metrics    
    #----------------sort a_to_b edges-----------------------------------------
    #when doing dependency and interdependency analysis, need to create lists 
    #of the nodes in each network affected by the links 
    from_a_nodes = []; to_b_nodes = []
    if STAND_ALONE == False:
        for item in a_to_b_edges:
            from_a_nodes.append(item[0]);to_b_nodes.append(item[1])
        if INTERDEPENDENCY == True:pass        
    #----------------sort the networks out-------------------------------------
    GA = GnetA.copy()
    if GnetB <> None:GB = GnetB.copy()
    else: GB = GnetB
    #---------------------------set counter to---------------------------------
    i = 0
    #-------------------------basic metrics------------------------------------
    basic_metrics_A['nodes_removed'] = [[]] #nodes removed from network A
    basic_metrics_A['no_of_nodes'] = [GA.number_of_nodes()] #the number of nodes left in network A
    basic_metrics_A['number_of_edges'] = [GA.number_of_edges()] #number of edges in the network
    basic_metrics_A['number_of_components'] = [nx.number_connected_components(GA)] #number of subgraphs
    basic_metrics_A['no_of_nodes_removed'] = [0]
    basic_metrics_A['no_of_isolated_nodes'] = [len(nx.isolates(GA))]
    
    if STAND_ALONE <> True:    
        basic_metrics_B['nodes_removed'] = [[]] #nodes removed from network A
        basic_metrics_B['no_of_nodes'] = [GB.number_of_nodes()] #the number of nodes left in network A
        basic_metrics_B['number_of_edges'] = [GB.number_of_edges()] #number of edges in the network
        basic_metrics_B['number_of_components'] = [nx.number_connected_components(GB)] #number of subgraphs
        basic_metrics_B['no_of_nodes_removed'] = [0]
        basic_metrics_B['no_of_isolated_nodes'] = [len(nx.isolates(GB))]  
        
    if option_metrics_A['giant_component_size']==True:
        option_metrics_A['giant_component_size']=[(nx.connected_component_subgraphs(GA)[0]).number_of_nodes()]
    if option_metrics_A['avg_nodes_in_components']==True:
        option_metrics_A['avg_nodes_in_components']=[(GA.number_of_nodes()/len(nx.connected_component_subgraphs(GA)))]
    if option_metrics_A['isolated_nodes']==True:
        option_metrics_A['isolated_nodes']=[[nx.isolates(GA)]]
    if REMOVE_ISOLATES == True or option_metrics_A['isolated_nodes_removed'] == True:
        option_metrics_A['isolated_nodes_removed']=[[]] #count the number of isolated nodes removed in the handle isolates function each step
    if REMOVE_ISOLATES == True or option_metrics_A['no_of_isolated_nodes_removed'] == True:
        option_metrics_A['no_of_isolated_nodes_removed']=[0]
    if REMOVE_SUBGRAPHS == True or option_metrics_A['subnodes']==True or option_metrics_A['subnodes_count']==True:
        option_metrics_A['subnodes']=[[]] #nodes removed as part of isolated graphs
        option_metrics_A['no_of_subnodes']=[0] #count of nodes removed as part of subgraphs

    if option_metrics_A['path_length']==True:option_metrics_A['path_length']=[nx.average_shortest_path_length(GA)] 
    if option_metrics_A['avg_path_length_of_components']==True:
        temp = []
        for g in nx.connected_component_subgraphs(GA):
            temp.append(nx.average_shortest_path_length(GA))
        option_metrics_A['avg_path_length_of_components']=[temp]
    if option_metrics_A['path_length_of_giant_component']==True:option_metrics_A['path_length_of_giant_component']=[temp[0]]
    if option_metrics_A['path_length_geo']==True:option_metrics_A['path_length_geo']=[nx.average_shortest_path_length(GA,'length')]
    if option_metrics_A['avg_degree']==True:
        temp=0
        for node in GA:
            temp+=GA.degree(node)
        option_metrics_A['avg_degree']=[temp/GA.number_of_nodes()]
    if option_metrics_A['no_of_inter_removed']==True:option_metrics_A['no_of_inter_removed']=[0]
    
    if option_metrics_A['density']==True:option_metrics_A['density']=[nx.density(GA)]
        
    if STAND_ALONE == False:
        if option_metrics_B['giant_component_size']==True:
            option_metrics_B['giant_component_size']=[(nx.connected_component_subgraphs(GB)[0]).number_of_nodes()]
        if option_metrics_B['avg_nodes_in_components']==True: 
            option_metrics_B['avg_nodes_in_components']=[(GB.number_of_nodes()/len(nx.connected_component_subgraphs(GB)))]
        if option_metrics_B['isolated_nodes']==True:
            option_metrics_B['isolated_nodes']=[[nx.isolates(GB)]]
        if REMOVE_ISOLATES == True or option_metrics_B['isolated_nodes_removed']==True:
            option_metrics_B['isolated_nodes_removed']=[[]] #count the number of isolated nodes removed in the handle isolates function each step    
        if REMOVE_ISOLATES == True or option_metrics_B['no_of_isolated_nodes_removed']==True:
            option_metrics_B['no_of_isolated_nodes_removed']=[0]
        if REMOVE_SUBGRAPHS == True or option_metrics_B['subnodes']==True or option_metrics_B['subnodes_count']==True:
            option_metrics_B['subnodes']=[[]] #nodes removed as part of isolated graphs
            option_metrics_B['no_of_subnodes']=[0] #count of nodes removed as part of subgraphs
        
        if option_metrics_B['density']==True:option_metrics_B['density']=[nx.density(GB)]
        

    if STAND_ALONE == False:
        if option_metrics_B['path_length']==True:option_metrics_B['path_length']=[nx.average_shortest_path_length(GB)] 
        if option_metrics_B['avg_path_length_of_components']==True:
            temp = []
            for g in nx.connected_component_subgraphs(GB):
                temp.append(nx.average_shortest_path_length(GB))   
            option_metrics_B['avg_path_length_of_components']=[temp]
        if option_metrics_B['path_length_of_giant_component']==True:option_metrics_B['path_length_of_giant_component']=[temp[0]]
        if option_metrics_B['path_length_geo']==True:option_metrics_B['path_length_geo']=[nx.average_shortest_path_length(GB,'length')]
        if option_metrics_B['avg_degree']==True:
             temp=0
             for node in GB:
                 temp+=GB.degree(node)
             option_metrics_B['avg_degree']=[temp/GB.number_of_nodes()]
        if option_metrics_B['no_of_inter_removed']==True:option_metrics_B['no_of_inter_removed']=[0]

    #----------------specific metrics for interdependency----------------------
    if INTERDEPENDENCY == True:
        interdependency_metrics = {'inter_removed_nodes':[[]], 'inter_removed_count':[0]}
    else: interdependency_metrics = None
    
    #----------------specific metrics for cascading analysis-------------------
    if CASCADING == True:
        dead = random.choice(GA.nodes()) #set the initial node to be removed for the neighbour analysis
        dlist = [] #list to store nodes between iterations during nieghbour analysis
        removed_nodes=[] #list to store nodes during the nieghbor analysis
        deadlist = [] #neighbor analysis only: the nodes removed in the last iteration  
        cascading_metrics = dead, dlist, removed_nodes, deadlist
    else: cascading_metrics = None
    
    ''' need to check the relevance of the lines below'''
    #----------------sort initial networks out again---------------------------
    #create a temp version of network to be used for all analysis
    GtempA = GA.copy() 
    if GB == None: GB = nx.Graph()
    GtempB = GB.copy()

    #-----------generate a node list for single random analysis----------------
    node_list = GA.nodes()
       
    #----------------package stuff up------------------------------------------
    networks = GA, GB, GtempA, GtempB
    graphparameters = networks,i,node_list, to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics
    
    return graphparameters
    
    
def default_parameters(fileName, failure_1 = None, failure_2 = None, failure_3 = None, basic_A = None, option_A = None, basic_B = None, option_B = None):
    #metrics
    if basic_A <> None:
        pass
    else:
        nodes_removed_A = True #nodes removed from network A
        node_count_removed_A = True #count of ndoes removed from network A   
        count_nodes_left_A = True #the number of nodes left in network A
        number_of_edges_A = True #number of edges in the network
        number_of_components_A = True #number of subgraphs/isolated nodes
        basic_A = nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A
    if option_A <> None:
        pass
    else:
        size_of_components_A=False;giant_component_size_A=False;av_nodes_in_components_A=False;isolated_nodes_A=False;isolated_n_count_removed_A=False;subnodes_A=False;subnodes_count_A=False;path_length_A=False;av_path_length_components_A=False;giant_component_av_path_length_A=False;av_path_length_geo_A=False;average_degree_A=False;inter_removed_count_A=False
        option_A = size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,inter_removed_count_A
    if basic_B <> None:
        pass
    else:
        basic_B = None
    if option_B <> None:
        pass
    else:
        option_B = None
    
    metrics = basic_A,basic_B,option_A,option_B

    if failure_1 <> None:
        STAND_ALONE,DEPENDENCY,INTERDEPENDENCY = failure_1
    else:
        STAND_ALONE = True;DEPENDENCY = False;INTERDEPENDENCY = False
    if failure_2 <> None:
        SINGLE,SEQUENTIAL,CASCADING = failure_2
    else:
        SINGLE = False;SEQUENTIAL = True;CASCADING = False
    if failure_3 <> None:
        RANDOM,DEGREE,BETWEENNESS = failure_3
    else:   
        RANDOM=True;DEGREE = False;BETWEENNESS = False
        
    REMOVE_SUBGRAPHS = False
    REMOVE_ISOLATES = False
    NO_ISOLATES = False
    a_to_b_edges = None
    parameters=metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName, a_to_b_edges
    return parameters
    
def outputresults(graphparameters, parameters,logfilepath=None,multiterations=False):
    values,error = outputs.outputresults(graphparameters, parameters,logfilepath,multiterations)
    return values