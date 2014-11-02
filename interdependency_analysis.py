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
        
'''
__author__ = "Craig Robson"
__created__ = ""
__year__ = "2014"
__version__ = "5.3.2"

#standard modules

import sys, random
import networkx as nx
'''
#custom modules
sys.path.append("C:/a8243587_DATA/GitRepo/resilience/modules")
sys.path.append("C:/Users/Craig/GitRepo/resilience/modules")
import tools,error_classes,failure_methods,network_handling,outputs
'''


def import_modules(resil_mod_loc):
    sys.path.append(resil_mod_loc)
    global tools, error_classes, failure_methods, network_handling, outputs
    import tools,error_classes,failure_methods,network_handling,outputs


def main(GA, GB, parameters, logfilepath, viewfailure=False):
    '''
    This is the main control function when the analysis is run directly from 
    the script. This reads in the data provided and processes it as such to run 
    the desired analysis.
    Input: up to two networks, parameters and a logfile path.
    Returns: a boolean varalible stating if the analysis has been completed.
    '''
    import_modules("C:/a8243587_DATA/GitRepo/resilience/modules")
        
    metrics,failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length,source_nodes_A,source_nodes_B=parameters
    
    #------set up the metrics for the analysis being asked for-----------------
    networks,metrics,graphparameters = metrics_initial(GA,GB,metrics,failure,handling_variables,store_n_e_atts,length,a_to_b_edges,source_nodes_A,source_nodes_B)
    networks,i,node_list,to_b_nodes,from_a_nodes = graphparameters
    basicA,basicB,optionA,optionB,interdependency_metrics,cascading_metrics = metrics
    parameters=failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length
    i = 0;iterate = True  
    print 'i is:', i
    #--------------------node and edge attributes------------------------------
    if store_n_e_atts:
        '''
        this will be done in the metric computation sections as this results 
        in less repitition in computations.
        Once complete, will remove this from code.
        '''
        pass
    #-----------------write networks to database t = 0-------------------------
    #GA,GB,GA,GB=networks
    if write_step_to_db:outputs.write_to_db(networks,a_to_b_edges,failure,db_parameters,i)
    #-----------------write metrics to database table t = 0--------------------  
    if write_results_table:outputs.write_results_table(metrics,i,failure,db_parameters,k=0)
    i +=1
    
    graphparameters=networks,i,node_list,to_b_nodes,from_a_nodes,source_nodes_A,source_nodes_B
    #run the analysis if seuquential or cascading == true
    if failure['sequential']==True or failure['cascading']== True:
        #while iterate is still true- network still has edges eleft
        while iterate == True:
            print '----------------------------------------------'
            print 'i is:', i
            #-------------update log file (if file path set)-------------------
            tools.write_to_log_file(logfilepath,'initiating step')
            #-------------run the step-----------------------------------------
            graphparameters,parameters,metrics,iterate = step(graphparameters,parameters,metrics,iterate,logfilepath)
            #-------------unpack variables-------------------------------------
            basicA,basicB,optionA,optionB,interdependency,cascading = metrics
            networks,k,node_list,to_b_nodes,from_a_nodes,source_nodes_A, source_nodes_B = graphparameters
            #-------------write networks to database---------------------------
            if write_step_to_db:outputs.write_to_db(networks,a_to_b_edges,failure,db_parameters,i)    
            #-------------write metrics to database table----------------------  
            if write_results_table:outputs.write_results_table(metrics,i,failure,db_parameters,k)
            #-------------update log file (if file path set)-------------------
            tools.write_to_log_file(logfilepath,'step completed')
            #-------------update i as iteration finished-----------------------
            i+=1
        if iterate == False:
            #no edges left so output results
            outputs.outputresults(graphparameters,parameters,metrics,logfilepath=None)
            
    complete = True
    print "Completed simulation"
    #update log file - only works if file path is set
    tools.write_to_log_file(logfilepath,'completed analysis')
    return complete

def step(graphparameters, parameters, metrics, iterate, logfilepath):
    '''
    Performs one time step of analysis when called.
    Inputs: graphparameters, parameters iterate 
    Returns: graphparameters, iterate
    '''
    #----------------unpack all the data containers----------------------------
    failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length = parameters
    basicA,basicB,optionA,optionB,dependency,cascading = metrics
    networks,i,node_list,to_b_nodes,from_a_nodes,source_nodes_A,source_nodes_B = graphparameters
    GA, GB, GtempA, GtempB = networks
    print "in step"
    #----------------perform the analsis---------------------------------------
    #----------------for sequential analysis only------------------------------
    #look at adding ability to remove nodes from both A and B
    if failure['sequential'] and failure['single']==False and failure['cascading']==False:
        if failure['degree']:
            #find node based on highest degree and remove it
            GtempA,node = failure_methods.sequential_degree(GtempA,failure['interdependency'])
        elif failure['betweenness']:
            #find node with highest betweenness value and remove it           
            GtempA,node = failure_methods.sequential_betweenness(GtempA,failure['interdependency'])
        elif failure['from_list']<>False:
            print 'THIS METHOD HAS NOT BEEN FINISHED OR TESTED'
            fail_list = []
            GtempA,node = failure_methods.sequential_from_list(GtempA,failure['interdependency'],fail_list,i)
        elif failure['random']:
            #randomly select the next node and remove it
            GtempA,node = failure_methods.sequential_random(GtempA, handling_variables['no_isolates'],failure['interdependency'])
        #update the counter
        #basicA['no_of_nodes_removed'].append(len(basicA['no_of_nodes_removed']))
        basicA['no_of_nodes_removed'].append(basicA['no_of_nodes_removed'][len(basicA['no_of_nodes_removed'])-1]+1)

        #-----removes source node from list if it is the selected node
        if source_nodes_A != None:
            for nd in source_nodes_A:
                if node == nd:
                    source_nodes_A.remove(node)
                    break
        
    #----------------for cascading analysis------------------------------------
    elif failure['cascading'] and failure['single']==False and failure['sequential']==False: 
        #unpack the cascading metrics and create some blank containers
        dead, dlist, removed_nodes, deadlist = cascading
        #------------identify subnodes and isolated nodes--------------------
        for g in nx.connected_component_subgraphs(GtempA):
            if g.number_of_nodes == 1:
                optionA['isolated_nodes'].append(g.nodes())
            elif g.number_of_nodes <> 0:
                optionA['subnodes'].append(g.nodes())
            else:
                raise error_classes.GeneralError('Error. Component has zero nodes.')
                #------------on the first time step only-----------------------
        #need to initaite the failure through remoiving a node to begin with
        if i == 1:
            if failure['degree'] and failure['betweenness']==False and failure['random']==False:
                ma, dead = tools.max_val_random(nx.degree(GtempA))
            elif failure['betweenness']==True and failure['random']==False and failure['degree']==False:
                ma, dead = tools.max_val_random(nx.betweenness_centrality(GtempA))
            elif failure['random']==True and failure['degree']==False and failure['betweeness']==False:
                dead = dead
            #update the network and find the next set of nodes to remove
            GtempA,dlist,removed_nodes,deadlist = failure_methods.cascading_failure(GtempA,dlist,dead,i,basicA['subnodes'], basicA['isolated_nodes'],basicA['nodes_removed'],failure['interdependency'])
            node = deadlist
            
            #------------on all but first time step----------------------------
        else:
            #update the network and find the next set of nodes to remove
            GtempA,dlist,removed_nodes,deadlist = failure_methods.cascading_failure(GtempA,dlist,dead,i,optionA['subnodes'],optionA['isolated_nodes'],basicA['nodes_removed'],failure['interdependency'])         
            node = deadlist
        
        #update metric
        basicA['no_of_nodes_removed'].append(basicA['no_of_nodes_removed'][len(basicA['no_of_nodes_removed'])-1]+len(deadlist))


        #-----removes source node from list if it is the selected node
        if source_nodes_A != None:
            for nd in source_nodes_A:
                for nde in deadlist:
                    if nde == nd:
                        source_nodes_A.remove(nde)
                        break
                    
        #------------package cascading metrics together----------------------
        cascading = dead, dlist, removed_nodes, deadlist

    #----------------for single analysis---------------------------------------
    elif failure['single']==True and failure['sequential']==False and failure['cascading']==False:
        #create a copy of the original network - will be complete
        GtempA = GA.copy()
        #select and remove a node from the network
        GtempA,node = failure_methods.single_random(GtempA, node_list, failure['interdependency'])
        #------------when node list is empty change iterate------------------
        if node_list == []:
            iterate = False
        #update the metric
        basicA['no_of_nodes_removed'].append(len(node))

        #-----removes source node from list if it is the selected node
        if source_nodes_A != None:
            for nd in source_nodes_A:
                if node == nd:
                    source_nodes_A.remove(node)
                    break
                
    #----------------update the list of removed nodes--------------------------
    basicA['nodes_removed'].append([node])
    basicA['nodes_selected_to_fail'].append([node])
    
    #----------------re-package networks and metrics which have been changed---   
    networks = GA, GB , GtempA, GtempB

    #----------------functions for analysis methods----------------------------
    if failure['interdependency'] and failure['stand_alone']==False and failure['dependency']==False:
        '''Needs to be developed'''
        #basicB['nodes_selected_to_fail'].append([])
        pass
        
    elif failure['dependency'] and failure['stand_alone']==False and failure['interdependency']==False:
        '''
        '''
        #special one for cascading as loop needed to handle multiple network A nodes being removed in one iteration
        #to store all nodes for intire iteration which are removed from networkB due to broken dependence link
        temp = []
        #------------if cascading analysis-----------------------------------
        #this needs checking
        if failure['cascading']==True: 
            x = 0
            while x < len(deadlist):
                node = deadlist[x]
                GtempA, GtempB, to_b_nodes, from_a_nodes, temp = network_handling.check_dependency_edges(GtempA, GtempB, node, to_b_nodes, from_a_nodes, temp)
                x += 1
        #------------run for all other analysis scenarios--------------------
        else:
            if GtempA.number_of_edges() != 0:
                nodes_removed=[]
                #are we using source nodes
                if source_nodes_A != None:
                    GtempA,nodes_removed = network_handling.check_connected_to_source_nodes(GtempA,source_nodes_A,nodes_removed)
                    #write changes out to metrics
                    if optionA['failed_no_con_to_a_source']!=False:
                        optionA['failed_no_con_to_a_source'].append(nodes_removed)
                    if optionA['source_nodes']!=False:
                        temp=[]
                        for nd in source_nodes_A: temp.append(nd)
                        optionA['source_nodes'].append(temp)
                        
                #add the selected node to remove to the list
                nodes_removed.append(node)
                               
                #checking dependency edges
                args = network_handling.check_dependency_edges(networks,nodes_removed,basicA,basicB,optionA,optionB,to_b_nodes,from_a_nodes,a_to_b_edges,temp,failure['interdependency'])
                if args == 0001:
                    raise error_classes.SearchError('Error. Could not find chosen node to remove it.')
                    tools.write_to_log_file(logfilepath, 'ERROR %s; Could not find chosen node ro remove (check_dependency_edges).' %(args))
                    return args
                else:
                    #un-pack variables returned                  
                    networks,nodes_removed_from_b,basicA,basicB,optionA,optionB,to_b_nodes,from_a_nodes,a_to_b_edges = args
                    GA, GB, GtempA, GtempB = networks
                    basicB['no_of_nodes_removed'].append(basicB['no_of_nodes_removed'][len(basicB['no_of_nodes_removed'])-1]+len(nodes_removed_from_b))  
                    basicB['nodes_removed'].append(nodes_removed_from_b)
                    dependency['no_of_nodes_removed_from_B'].append(len(nodes_removed_from_b))
                    dependency['nodes_removed_from_B'].append(nodes_removed_from_b)
                    #check if any of the failed nodes are source nodes in B - remove from list if they are
                    if source_nodes_B != None:
                        for nd in nodes_removed_from_b:
                            try: source_nodes_B.remove(nd)
                            except:pass
            else:
                basicB['nodes_removed'].append([])
                dependency['nodes_removed_from_B'].append([])
                dependency['no_of_nodes_removed_from_B'].append(0)
                if optionA['source_nodes'] != False: optionA['source_nodes'].append([])
                if optionA['failed_no_con_to_a_source'] != False: optionA['failed_no_con_to_a_source'].append([])
            
            if GtempB.number_of_edges() != 0:
                if source_nodes_B != None:
                    nodes_removed=[]
                    GtempB,nodes_removed = network_handling.check_connected_to_source_nodes(GtempB,source_nodes_B,nodes_removed)                   
                    #write out to some metrics
                    if optionB['failed_no_con_to_a_source'] != False:
                        optionB['failed_no_con_to_a_source'].append(nodes_removed)
                    if optionB['source_nodes'] != False:
                        temp=[]
                        for nd in source_nodes_B: temp.append(nd)
                        optionB['source_nodes'].append(temp)
            else:
                if optionB['source_nodes'] != False: optionB.append([])
                if optionB['failed_no_con_to_a_source'] != False: optionB.append([])
        
        #------------run the actual analysis---------------------------------
        #analyse network B
        iterate,GtempB,i,to_a_nodes,from_b_nodes,a_to_b_edges,node_list,basicB,optionB,source_nodes_B = analysis_B(parameters,iterate,GtempB,i,to_b_nodes,from_a_nodes,node_list,basicB,optionB,to_b_nodes,from_a_nodes,source_nodes_B,net='B')
        #analyse network A
        iterate,GtempA,i,to_a_nodes,from_b_nodes,a_to_b_edges,node_list,basicA,optionA,source_nodes_A = analysis_B(parameters,iterate,GtempA,i,to_b_nodes,from_a_nodes,node_list,basicA,optionA,to_b_nodes,from_a_nodes,source_nodes_A,net='A')  
        
        if i <> -100: basicA['nodes_removed'].append(basicA['nodes_removed'].pop()+basicA['isolated_nodes_removed'][i])
        if optionA['failed_no_con_to_a_source'] != None:
            basicA['no_of_nodes_removed'].append(basicA['no_of_nodes_removed'].pop()+len(optionA['failed_no_con_to_a_source'][len(optionA['failed_no_con_to_a_source'])-1]))
        if optionB['failed_no_con_to_a_source'] != None:
            basicB['no_of_nodes_removed'].append(basicB['no_of_nodes_removed'].pop()+len(optionB['failed_no_con_to_a_source'][len(optionB['failed_no_con_to_a_source'])-1]))

        #------------move counter on-----------------------------------------
        i += 1   
        
    elif failure['stand_alone'] and failure['dependency']==False and failure['interdependency']==False :
        if GtempA.number_of_edges() != 0:
            #check all nodes still contected to a source node if set
            if source_nodes_A != None:
                nodes_removed=[]
                GtempA,nodes_removed = network_handling.check_connected_to_source_nodes(GtempA,source_nodes_A,nodes_removed)
                #write out to some metrics
                if optionA['failed_no_con_to_a_source'] != False:
                    optionA['failed_no_con_to_a_source'].append(nodes_removed)
                if optionA['source_nodes'] != False:
                    temp=[]
                    for nd in source_nodes_A: temp.append(nd)
                    optionA['source_nodes'].append(temp)
        else:
            if optionA['source_nodes'] != False: optionA['source_nodes'].append([])
            if optionA['failed_no_con_to_a_source'] != False: optionA['failed_no_con_to_a_source'].append([])
        #run the analysis
        iterate,GtempA,i,to_a_nodes,from_b_nodes,a_to_b_edges,node_list,basicA,optionA,source_nodes_A = analysis_B(parameters,iterate,GtempA,i,to_b_nodes,from_a_nodes,node_list,basicA,optionA,to_b_nodes, from_a_nodes,source_nodes_A,net='A') #run the analysis
        if i <> -100:
            print "I is: %s. Length of basicA no_of_nodes_removed is: %s." %(i,len(basicA['no_of_nodes_removed']))
            basicA['nodes_removed'].append(basicA['nodes_removed'].pop()+basicA['isolated_nodes_removed'][i])
            basicA['nodes_removed'].append(basicA['nodes_removed'].pop()+optionA['failed_no_con_to_a_source'][i])
        if optionA['failed_no_con_to_a_source'] != None:
            basicA['no_of_nodes_removed'].append(basicA['no_of_nodes_removed'].pop()+len(optionA['failed_no_con_to_a_source'][len(optionA['failed_no_con_to_a_source'])-1]))

        i += 1  
    else:
        raise error_classes.GeneralError('Error. No analysis type has been selected.')
    
    #----------------re-package all data into respective containers------------
    networks = GA, GB, GtempA, GtempB
    metrics = basicA,basicB,optionA, optionB,dependency,cascading
    graphparameters = networks,i,node_list,to_b_nodes,from_a_nodes,source_nodes_A,source_nodes_B
    parameters =  failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length
    
    return graphparameters,parameters,metrics,iterate
 
'''calcualte values at end of step'''       
def analysis_B(parameters,iterate,Gtemp,i,to_a_nodes,from_b_nodes,node_list,basic_metrics,option_metrics,to_b_nodes,from_a_nodes,source_nodes,net):
        '''
        Failure method has already been run. This checks for isolated nodes and
        subgraphs (goes throught the handling avraibles, then calculates metrics 
        required.)
        '''
        #------------unpack the holding variables------------------------------
        failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length=parameters    
        basic_metrics['no_of_isolated_nodes'].append(len(nx.isolates(Gtemp)))

        #------------check for isoalted nodes---------------------------------
        
        if handling_variables['remove_isolates']==True:
            if Gtemp.number_of_edges() <> 0:
                Gtemp,node_list,basic_metrics,option_metrics,isolated_nodes,to_b_nodes,from_a_nodes,a_to_b_edges = network_handling.remove_isolates(Gtemp,node_list,option_metrics,basic_metrics,to_b_nodes,from_a_nodes,a_to_b_edges,net)
                #not too sure why I need separate things for net a and b??S
                if net == 'B':         
                    if option_metrics['isolated_nodes']<>False:option_metrics['isolated_nodes'].append(isolated_nodes)
                    if option_metrics['no_of_isolated_nodes_removed']<>False:option_metrics['no_of_isolated_nodes_removed'].append(len(isolated_nodes))
                    basic_metrics['isolated_nodes_removed'].append(isolated_nodes)
                    basic_metrics['no_of_nodes_removed'].append(basic_metrics['no_of_nodes_removed'].pop()+len(isolated_nodes))
                    basic_metrics['nodes_removed'].append(basic_metrics['nodes_removed'].pop()+basic_metrics['isolated_nodes_removed'][i])
                if net == 'A':
                    basic_metrics['isolated_nodes_removed'].append(isolated_nodes)
                    if option_metrics['isolated_nodes']<>False:option_metrics['isolated_nodes'].append(isolated_nodes)
                    if option_metrics['no_of_isolated_nodes_removed']<>False:option_metrics['no_of_isolated_nodes_removed'].append(len(isolated_nodes))
                if source_nodes != None:
                    for nd in isolated_nodes:
                        try: source_nodes.remove(nd)
                        except: pass
            else:
                if option_metrics['isolated_nodes']<>False:option_metrics['isolated_nodes'].append([])
                if option_metrics['no_of_isolated_nodes_removed']<>False:option_metrics['no_of_isolated_nodes_removed'].append(0)
                basic_metrics['isolated_nodes_removed'].append([])
                                    
        elif handling_variables['remove_isolates']==False:
            if option_metrics['no_of_isolated_nodes_removed'] <> False: option_metrics['no_of_isolated_nodes_removed'].append(0)
            basic_metrics['isolated_nodes_removed'].append([])
            if option_metrics['isolated_nodes']<>False:option_metrics['isolated_nodes'].append([nx.isolates(Gtemp)])
            
        #----------------if the graph is still connected-----------------------
        num_edges = Gtemp.number_of_edges()        
        if num_edges <> 0:
            #the graph is not dissconnected                      
            nodelists = Gtemp.nodes()
            edgelists = Gtemp.edges()
            #if subgraphs are to be removed for the analysis ie. for infrastructure modelling
            if handling_variables['remove_subgraphs']==True:
                #remove subgraphs and record the details of them
                Gtemp, subnodes, nsubnodes, nodelists, edgelists = network_handling.handle_sub_graphs(Gtemp) 
                if option_metrics['subnodes'] <> False: option_metrics['subnodes'].append(subnodes)
                basic_metrics['no_of_nodes_removed'].append(basic_metrics['no_of_nodes_removed'].pop()+nsubnodes)
                if option_metrics['no_of_subnodes'] <> False: option_metrics['no_of_subnodes'].append(nsubnodes)
                
                nodes_removed = basic_metrics['nodes_removed'].pop()
                for subgraph in subnodes: 
                    for nd in subgraph: 
                        nodes_removed.append(nd)
                basic_metrics['nodes_removed'].append(nodes_removed)
                if source_nodes != None:
                    for nd in nodes_removed:
                        try: source_nodes.remove(nd)
                        except: pass
                
                node_list, to_b_nodes, from_a_nodes =  network_handling.clean_node_lists(subnodes,node_list,to_b_nodes,from_a_nodes)
                
                temp = nx.connected_component_subgraphs(Gtemp)
                basic_metrics['no_of_components'].append(len(temp))
                
            #if subgraphs are to be left as part of the network 
            elif handling_variables['remove_subgraphs']==False:
                #get a list of all connected components
                temp = nx.connected_component_subgraphs(Gtemp)
                #add the number components to the respective list
                basic_metrics['no_of_components'].append(len(temp))
                
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
            else:
                #there is an error with the variable
                raise error_classes.GeneralError('Error. Variable REMOVE_SUBGRAPHS must be set as True or False only.')
                        
        #------------run if no edges left--------------------------------------
        elif num_edges == 0:
            #at the last removal of a node, all remaining edges were consequently removed
            #update the metrics
            if option_metrics['subnodes'] <> False: option_metrics['subnodes'].append([])
            if option_metrics['no_of_subnodes'] <> False: option_metrics['no_of_subnodes'].append(0)
        
        #-------metric calcs which work no matter the state of the network-----
        if option_metrics['size_of_components']<>False:
            temp = []
            for g in nx.connected_component_subgraphs(Gtemp):
                temp.append(g.number_of_nodes())
            option_metrics['size_of_components'].append(temp)
        
        if option_metrics['maximum_betweenness_centrality']<>False or option_metrics['avg_betweenness_centrality']<>False:
            temp = nx.betweenness_centrality(Gtemp)
            if option_metrics['maximum_betweenness_centrality']<>False:
                option_metrics['maximum_betweenness_centrality'].append(max(temp.values()))
            if option_metrics['avg_betweenness_centrality']<>False:
                avg=0.0
                for val in temp.values():
                    avg+=val
                option_metrics['avg_betweenness_centrality'].append(avg/len(temp))
                if store_n_e_atts == True:
                    for key in temp: Gtemp.node[key]['betweenness_centrality'] = temp[key]                
                
        if option_metrics['clustering_coefficient']<>False:
            option_metrics['clustering_coefficient'].append(nx.average_clustering(Gtemp))
            temp = nx.clustering(Gtemp)
            if store_n_e_atts == True:
                    for key in temp: Gtemp.node[key]['clustering_coefficient'] = temp[key]
        if option_metrics['transitivity']<>False:
            option_metrics['transitivity'].append(nx.transitivity(Gtemp))
        if option_metrics['square_clustering']<>False:
            temp = nx.square_clustering(Gtemp)
            avg=0.0
            for val in temp.values():
                avg+=val
            option_metrics['square_clustering'].append(avg/len(temp))
            if store_n_e_atts == True:
                    for key in temp: Gtemp.node[key]['square_clustering'] = temp[key]
        if option_metrics['avg_degree_connectivity'] <> False:
            temp = nx.average_degree_connectivity(Gtemp)
            option_metrics['avg_degree_connectivity'].append(temp.values())
        if option_metrics['avg_closeness_centrality'] <> False:
            temp = nx.closeness_centrality(Gtemp)
            avg=0.0
            for val in temp.values():
                avg+=val
            option_metrics['avg_closeness_centrality'].append(avg/len(temp))
            if store_n_e_atts == True:
                    for key in temp: Gtemp.node[key]['avg_closeness_centrality'] = temp[key]
        if option_metrics['avg_neighbor_degree'] <> False:
            temp = nx.average_neighbor_degree(Gtemp)
            avg=0.0
            for val in temp.values():
                avg+=val
            option_metrics['avg_neighbor_degree'].append(avg/len(temp))
            if store_n_e_atts == True:
                    for key in temp: Gtemp.node[key]['avg_neighbor_degree'] = temp[key]
        #------------re-calc the number of edges-------------------------------
        #this is needed if subgraphs were removed
        numofedges = Gtemp.number_of_edges()                      
        #------------if there are no edges left--------------------------------
        
        if numofedges == 0: 
            #set i really high so iteraion stops at the end of this step
            i = -100
            #add values for the metrics which are not set as False
            if option_metrics['avg_path_length'] <> False: option_metrics['avg_path_length'].append(0.0)
            if option_metrics['avg_path_length_of_components']<>False: option_metrics['avg_path_length_of_components'].append([0.0])
            if option_metrics['avg_path_length_of_giant_component']<> False: option_metrics['avg_path_length_of_giant_component'].append(0.0)
            if option_metrics['avg_geo_path_length'] <> False: option_metrics['avg_geo_path_length'].append(0.0)
            if option_metrics['avg_geo_path_length_of_components']<>False:option_metrics['avg_geo_path_length_of_components'].append([0.0])
            if option_metrics['avg_geo_path_length_of_giant_component']<>False:option_metrics['avg_geo_path_length_of_giant_component'].append(0.0)
            if option_metrics['giant_component_size'] <> False: option_metrics['giant_component_size'].append(0)
            if option_metrics['avg_degree'] <> False: option_metrics['avg_degree'].append(0)
            if option_metrics['density']<>False:option_metrics['density'].append(0.0)
            if option_metrics['assortativity_coefficient']<>False:option_metrics['assortativity_coefficient'].append(0.0)
            if option_metrics['avg_degree_centrality']<>False:option_metrics['avg_degree_centrality'].append(0.0)
            if option_metrics['diameter']<>False:option_metrics['diameter'].append(0.0)
            #if option_metrics['avg_size_of_components']<>False: option_metrics['avg_size_of_components']=0
            basic_metrics['no_of_components'].append(nx.number_connected_components(Gtemp))
            basic_metrics['no_of_edges'].append(0)
            #set iterate as False so it stops after this time step
            iterate = False

        #------------if the number of edge is greater than zero----------------
        elif numofedges <> 0:
            #---------------average path length calculations-------------------
            if option_metrics['avg_path_length'] <> False or option_metrics['avg_path_length_of_components']<>False:
                #claculates the average path length of the whole network if not dissconnected
                #average = network_handling.whole_graph_av_path_length(Gtemp)
                temp=[]
                for g in nx.connected_component_subgraphs(Gtemp):
                    temp.append(nx.average_shortest_path_length(g))
                if option_metrics['avg_path_length']<>False:
                    avg = 0
                    for dist in temp:
                        avg+= dist
                    option_metrics['avg_path_length'].append(avg/len(temp))
                if option_metrics['avg_path_length_of_components']<>False:
                    option_metrics['avg_path_length_of_components'].append(temp)
            
            if option_metrics['avg_path_length_of_giant_component'] <> False and option_metrics['avg_path_length']<>False:
                option_metrics['avg_path_length_of_giant_component'].append(temp[0])
            elif option_metrics['avg_path_length_of_giant_component']<>False:
                av_len = nx.average_shortest_path_length(nx.connected_component_subgraphs(Gtemp)[0])
                option_metrics['avg_path_length_of_giant_component'].append(av_len)        
            
            length_att = False
            if option_metrics['avg_geo_path_length']<>False or option_metrics['avg_geo_path_length_of_components']<>False:
                for edge in Gtemp.edges(data=True):
                    for key in edge[2].keys():
                        if key == str(length):
                            length_att = True
                            break
                if length_att == True:
                    temp=[]
                    for g in nx.connected_component_subgraphs(Gtemp):
                        temp.append(nx.average_shortest_path_length(g,length_att))
                    if option_metrics['avg_geo_path_length']<>False:
                        avg = 0
                        for dist in temp:
                            avg+= dist
                        option_metrics['avg_geo_path_length'].append(avg/len(temp))
                    if option_metrics['avg_geo_path_length_of_components']<>False:
                        option_metrics['avg_geo_path_length_of_components'].append(temp)
                else:
                    if option_metrics['avg_geo_path_length']<>False:
                        option_metrics['avg_geo_path_length'].append(None)
                    if option_metrics['avg_geo_path_length_of_components']<>False:
                        option_metrics['avg_geo_path_length_of_components'].append(None)
            
            if option_metrics['avg_geo_path_length_of_giant_component'] <> False and option_metrics['avg_geo_path_length']<>False:
                option_metrics['avg_geo_path_length_of_giant_component'].append(temp[0])
            elif option_metrics['avg_geo_path_length_of_giant_component']<>False and length_att == True:
                av_len = nx.average_shortest_path_length(nx.connected_component_subgraphs(Gtemp)[0],length_att)
                option_metrics['avg_geo_path_length_of_giant_component'].append(av_len)
            elif option_metrics['avg_geo_path_length_of_giant_component']<>False and length_att == False:
                option_metrics['avg_geo_path_length_of_giant_component'].append(None)
                
            if option_metrics['diameter'] <> False:
                if len(nx.connected_component_subgraphs(Gtemp)) > 1:
                    option_metrics['diameter'].append('ERROR')
                else:
                    option_metrics['diameter'].append(nx.diameter(Gtemp))                
                
            #-------------------other calculations-----------------------------
            if option_metrics['giant_component_size'] <> False: 
                #gets the size of the largest connected component
                option_metrics['giant_component_size'].append((nx.connected_component_subgraphs(Gtemp)[0]).number_of_nodes()) #get the number of ndoes in the largest component
            
            if option_metrics['avg_size_of_components'] <> False:
                option_metrics['avg_size_of_components'].append(Gtemp.number_of_nodes()/float(len(nx.connected_component_subgraphs(Gtemp))))
            
            #add the number of edges to the respective list
            basic_metrics['no_of_edges'].append(Gtemp.number_of_edges())
                            
            if option_metrics['avg_degree'] <> False:       
                degree_list = Gtemp.degree()
                sumh = 0.0
                for d in degree_list:    
                    sumh += degree_list[d]
                option_metrics['avg_degree'].append(sumh/(Gtemp.number_of_nodes()))
                Gtemp.graph['average_degree']=sumh/Gtemp.number_of_nodes()
            if option_metrics['density']<>False:option_metrics['density'].append(nx.density(Gtemp))

            if option_metrics['assortativity_coefficient']<>False:
                temp = nx.degree_assortativity_coefficient(Gtemp)
                if str(temp) == 'nan': temp = 0.0
                option_metrics['assortativity_coefficient'].append(temp)
            
            if option_metrics['avg_degree_centrality']<>False:
                temp = nx.degree_centrality(Gtemp)
                avg=0
                for val in temp.values():
                    avg+=val
                option_metrics['avg_degree_centrality'].append(avg/len(temp))
        
        #add the number of nodes left to the respective list
        basic_metrics['no_of_nodes'].append(Gtemp.number_of_nodes())

        return iterate,Gtemp,i,to_b_nodes,from_a_nodes,a_to_b_edges,node_list,basic_metrics,option_metrics,source_nodes 

def metrics_initial(GnetA, GnetB, metrics, failure, handling_variables, store_n_e_atts, length, a_to_b_edges, source_nodes_A, source_nodes_B):
    
    #unpack the paarameter
    #----------------unpack the metrics----------------------------------------
    basicA, basicB, optionA, optionB, dependency, cascading = metrics    
    #----------------sort a_to_b edges-----------------------------------------
    #when doing dependency and interdependency analysis, need to create lists 
    #of the nodes in each network affected by the links 
    from_a_nodes = []; to_b_nodes = []
    if failure['stand_alone'] == False:
        for item in a_to_b_edges:
            from_a_nodes.append(item[0]);to_b_nodes.append(item[1])
        if failure['interdependency']== True:pass        
    #----------------sort the networks out-------------------------------------
    GA = GnetA.copy()
    if GnetB <> None:GB = GnetB.copy()
    else: GB = GnetB
    #---------------------------set counter to---------------------------------
    i = 0
    #-------------------------basic metrics------------------------------------
    basicA['nodes_removed'] = [[]] #nodes removed from network A for any reason (fails, isolated, subgraphs)
    basicA['no_of_nodes_removed'] = [0]
    basicA['no_of_nodes'] = [GA.number_of_nodes()] #the number of nodes left in network A
    basicA['no_of_edges'] = [GA.number_of_edges()] #number of edges in the network
    basicA['no_of_components'] = [nx.number_connected_components(GA)] #number of subgraphs
    basicA['no_of_isolated_nodes'] = [len(nx.isolates(GA))]
    basicA['isolated_nodes_removed'] = [[]]
    basicA['nodes_selected_to_fail'] = [[]] #only those nodes which are selected to fail
        
    if failure['stand_alone'] <> True:
        basicB['nodes_removed'] = [[]] #nodes removed from network A for any reason (fails, isolated, subgraphs)
        basicB['no_of_nodes_removed'] = [0]
        basicB['no_of_nodes'] = [GB.number_of_nodes()] #the number of nodes left in network A
        basicB['no_of_edges'] = [GB.number_of_edges()] #number of edges in the network
        basicB['no_of_components'] = [nx.number_connected_components(GB)] #number of subgraphs
        basicB['no_of_isolated_nodes'] = [len(nx.isolates(GB))]
        basicB['isolated_nodes_removed'] = [[]]
    
    if store_n_e_atts == True:
        temp = nx.degree(GA)
        for key in temp:GA.node[key]['degree']=temp[key]
        temp = nx.degree(GB)
        for key in temp:GB.node[key]['degree']=temp[key]

        GA.graph['no_of_nodes']=nx.number_of_nodes(GA)
        
    if optionA['size_of_components']==True:
        temp = []
        for g in nx.connected_component_subgraphs(GA):
            temp.append(g.number_of_nodes())
        optionA['size_of_components']=[temp]
    if optionA['giant_component_size']==True:
        optionA['giant_component_size']=[(nx.connected_component_subgraphs(GA)[0]).number_of_nodes()]
    if optionA['avg_size_of_components']==True:
        optionA['avg_size_of_components']=[(GA.number_of_nodes()/len(nx.connected_component_subgraphs(GA)))]
    if optionA['isolated_nodes']==True:
        optionA['isolated_nodes']=[nx.isolates(GA)]
    if handling_variables['remove_isolates'] == True or optionA['no_of_isolated_nodes_removed'] == True:
        optionA['no_of_isolated_nodes_removed']=[0]
    if handling_variables['remove_subgraphs']== True or optionA['subnodes']==True or optionA['no_of_subnodes']==True:
        optionA['subnodes']=[[]] #nodes removed as part of isolated graphs
        optionA['no_of_subnodes']=[0] #count of nodes removed as part of subgraphs

    if optionA['source_nodes']==True and source_nodes_A != None:
        temp = []
        for val in source_nodes_A: temp.append(val)
        optionA['source_nodes']=[temp]
    else: optionA['source_nodes']=False
    if optionA['failed_no_con_to_a_source']==True and source_nodes_A != None:
        optionA['failed_no_con_to_a_source']=[[]]
    else: optionA['failed_no_con_to_a_source']=False
    
    if optionA['avg_path_length']==True:optionA['avg_path_length']=[nx.average_shortest_path_length(GA)] 
    if optionA['avg_path_length_of_components']==True or optionA['avg_path_length_of_giant_component']==True:
        temp = []
        for g in nx.connected_component_subgraphs(GA):
            temp.append(nx.average_shortest_path_length(GA))
        if optionA['avg_path_length_of_components']== True:optionA['avg_path_length_of_components']=[temp]
        if optionA['avg_path_length_of_giant_component']==True:optionA['avg_path_length_of_giant_component']=[temp[0]]
    if optionA['avg_geo_path_length']==True or optionA['avg_geo_path_length_of_components']==True or optionA['avg_geo_path_length_of_giant_component']==True:
        #need to check that the edges have an attribute 'length'
        for edge in GA.edges(data=True):
            for edge in GA.edges(data=True):
                if len(edge[2].keys()) > 0:
                    for key in edge[2].keys():
                        if key == str(length):
                            temp = []
                            for g in nx.connected_component_subgraphs(GA):
                                temp.append(nx.average_shortest_path_length(g,length))
                            if optionA['avg_geo_path_length']==True:
                                avg=0
                                for val in temp:
                                    avg+=val
                                optionA['avg_geo_path_length']=[avg/len(temp)]
                            if optionA['avg_geo_path_length_of_components']==True:
                                optionA['avg_geo_path_length_of_components']=[temp]
                            if optionA['avg_geo_path_length_of_giant_component']==True:
                                optionA['avg_geo_path_length_of_giant_component']=[temp[0]]
                            break
                if optionA['avg_geo_path_length']== True:optionA['avg_geo_path_length']=[None]
                if optionA['avg_geo_path_length_of_components']==True: optionA['avg_geo_path_length_of_components']=[None]
                if optionA['avg_geo_path_length_of_giant_component']==True: optionA['avg_geo_path_length_of_giant_component']=[None]
                break
            break
            
    if optionA['avg_degree']==True:
        avg=0.0
        for node in GA:
            avg+=GA.degree(node)
        optionA['avg_degree']=[avg/GA.number_of_nodes()]
    if optionA['density']==True:optionA['density']=[nx.density(GA)]
        
    if optionA['maximum_betweenness_centrality']==True or optionA['avg_betweenness_centrality']==True:
        temp = nx.betweenness_centrality(GA)
        if optionA['maximum_betweenness_centrality']<>False:
            optionA['maximum_betweenness_centrality']=[max(temp.values())]
        if optionA['avg_betweenness_centrality']<>False:
            avg=0.0
            for val in temp.values():
                avg+=val
            optionA['avg_betweenness_centrality']=[avg/len(temp)]
        if store_n_e_atts == True:
            for key in temp: GA.node[key]['betweenness_centrality'] = temp[key]            
    if optionA['assortativity_coefficient']==True:
        optionA['assortativity_coefficient']=[nx.degree_assortativity_coefficient(GA)]
    if optionA['clustering_coefficient']==True:
        optionA['clustering_coefficient']=[nx.average_clustering(GA)]
        temp = nx.clustering(GA)
        if store_n_e_atts == True:
            for key in temp: GA.node[key]['clustering'] = temp[key]
    if optionA['transitivity']==True:
        optionA['transitivity']=[nx.transitivity(GA)]
    if optionA['square_clustering']==True:
        temp = nx.square_clustering(GA)
        avg=0.0
        for val in temp.values():
            avg+=val
        optionA['square_clustering']=[avg/len(temp)]
        if store_n_e_atts == True:
            for key in temp: GA.node[key]['square_clustering'] = temp[key]
    if optionA['avg_neighbor_degree']==True:
        temp = nx.average_neighbor_degree(GA)
        avg=0.0
        for val in temp.values():
            avg+=val
        optionA['avg_neighbor_degree']=[avg/len(temp)]
        if store_n_e_atts == True:
            for key in temp: GA.node[key]['avg_neighbor_degree'] = temp[key]
    if optionA['avg_degree_connectivity']==True:
        temp = nx.average_degree_connectivity(GA)
        optionA['avg_degree_connectivity']=[temp.values()]
    if optionA['avg_degree_centrality']==True:
        temp = nx.degree_centrality(GA)
        avg=0.0
        for val in temp.values():
            avg+=val
        optionA['avg_degree_centrality']=[avg/len(temp)]
        if store_n_e_atts == True:
            for key in temp: GA.node[key]['avg_degree_centrality'] = temp[key]
    if optionA['avg_closeness_centrality']==True:
        temp = nx.closeness_centrality(GA)
        avg=0.0
        for val in temp.values():
            avg+=val
        optionA['avg_closeness_centrality']=[avg/len(temp)]
        if store_n_e_atts == True:
            for key in temp: GA.node[key]['avg_closeness_centrality'] = temp[key]
    if optionA['diameter']==True:
        optionA['diameter']=[nx.diameter(GA)]
    
    if failure['stand_alone'] == False:
        if optionB['size_of_components']==True:
            temp = []
            for g in nx.connected_component_subgraphs(GB):
                temp.append(g.number_of_nodes())
            optionB['size_of_components']=[temp]
        if optionB['giant_component_size']==True:
            optionB['giant_component_size']=[(nx.connected_component_subgraphs(GB)[0]).number_of_nodes()]
        if optionB['avg_size_of_components']==True: 
            optionB['avg_size_of_components']=[(GB.number_of_nodes()/len(nx.connected_component_subgraphs(GB)))]
        if optionB['isolated_nodes']==True:
            optionB['isolated_nodes']=[nx.isolates(GB)]
        if handling_variables['remove_isolates']==True or basicB['isolated_nodes_removed']==True:
            basicB['isolated_nodes_removed']=[[]] #count the number of isolated nodes removed in the handle isolates function each step
        if handling_variables['remove_isolates']== True or optionB['no_of_isolated_nodes_removed']==True:
            optionB['no_of_isolated_nodes_removed']=[0]
        if handling_variables['remove_subgraphs']== True or optionB['subnodes']==True or optionB['no_of_subnodes']==True:
            optionB['subnodes']=[[]] #nodes removed as part of isolated graphs
            optionB['no_of_subnodes']=[0] #count of nodes removed as part of subgraphs
        
        if optionB['source_nodes']==True and source_nodes_B != None:
            temp = []
            for val in source_nodes_B: temp.append(val)
            optionB['source_nodes']=[temp]
        else: optionB['source_nodes']=False
        if optionB['failed_no_con_to_a_source']==True:
            optionB['failed_no_con_to_a_source']=[[]]
        else: optionB['failed_no_con_to_a_source']=False
                
        if optionB['density']==True:optionB['density']=[nx.density(GB)]
        
        if optionB['avg_path_length']==True:optionB['avg_path_length']=[nx.average_shortest_path_length(GB)] 
        if optionB['avg_path_length_of_components']==True or optionB['avg_path_length_of_giant_component']==True:
            temp = []
            for g in nx.connected_component_subgraphs(GB):
                temp.append(nx.average_shortest_path_length(GB))   
            if optionB['avg_path_length_of_components']==True:optionB['avg_path_length_of_components']=[temp]
            if optionB['avg_path_length_of_giant_component']==True:optionB['avg_path_length_of_giant_component']=[temp[0]]
        if optionB['avg_geo_path_length']==True or optionB['avg_geo_path_length_of_components']==True or optionB['avg_geo_path_length_of_giant_component']==True:
            #need to check that the edges have an attribute 'length'
            for edge in GB.edges(data=True):
                for edge in GB.edges(data=True):
                    if len(edge[2].keys()) > 0:
                        for key in edge[2].keys():
                            if key == str(length):
                                temp = []
                                for g in nx.connected_component_subgraphs(GB):
                                    temp.append(nx.average_shortest_path_length(g,length))
                                if optionB['avg_geo_path_length']==True:
                                    avg=0
                                    for val in temp:
                                        avg+=val
                                    optionB['avg_geo_path_length']=[avg/len(temp)]
                                if optionB['avg_geo_path_length_of_components']==True:
                                    optionB['avg_geo_path_length_of_components']=[temp]
                                if optionB['avg_geo_path_length_of_giant_component']==True:
                                    optionB['avg_geo_path_length_of_giant_component']=[temp[0]]
                                break
                    
                    if optionB['avg_geo_path_length']==True:optionB['avg_geo_path_length']=[None]
                    if optionB['avg_geo_path_length_of_components']==True:optionB['avg_geo_path_length_of_components']=[None]
                    if optionB['avg_geo_path_length_of_giant_component']==True:optionB['avg_geo_path_length_of_giant_component']=[None]
                    break
                break
            
        if optionB['avg_degree']==True:
             temp=0
             for node in GB:
                 temp+=GB.degree(node)
             optionB['avg_degree']=[temp/GB.number_of_nodes()]
             
        if optionB['density']==True:optionA['density']=[nx.density(GB)]
        
        if optionB['maximum_betweenness_centrality']==True or optionB['avg_betweenness_centrality']==True:
            temp = nx.betweenness_centrality(GB)
            if optionB['maximum_betweenness_centrality']<>False:
                optionB['maximum_betweenness_centrality']=[max(temp.values())]
            if optionB['avg_betweenness_centrality']<>False:
                avg=0.0
                for val in temp.values():
                    avg+=val
                optionB['avg_betweenness_centrality']=[avg/len(temp)]
            if store_n_e_atts == True:
                for key in temp: GB.node[key]['betweenness_centrality'] = temp[key]
        if optionB['assortativity_coefficient']==True:
            optionB['assortativity_coefficient']=[nx.degree_assortativity_coefficient(GB)]
        if optionB['clustering_coefficient']==True:
            optionB['clustering_coefficient']=[nx.average_clustering(GB)]
            temp = nx.clustering(GB)
            if store_n_e_atts == True:
                for key in temp: GB.node[key]['betweenness_centrality'] = temp[key]
        if optionB['transitivity']==True:
            optionB['transitivity']=[nx.transitivity(GB)]
        if optionB['square_clustering']==True:
            temp = nx.square_clustering(GB)
            avg=0.0
            for val in temp.values():
                avg+=val
            optionB['square_clustering']=[avg/len(temp)]            
            if store_n_e_atts == True:
                for key in temp: GB.node[key]['square_clustering'] = temp[key]
        if optionB['avg_neighbor_degree']==True:
            temp = nx.average_neighbor_degree(GB)
            avg=0.0
            for val in temp.values():
                avg+=val
            optionB['avg_neighbor_degree']=[avg/len(temp)]            
            if store_n_e_atts == True:
                for key in temp: GB.node[key]['avg_neighbor_degree'] = temp[key]
        if optionB['avg_degree_connectivity']==True:
            temp = nx.average_degree_connectivity(GB)
            optionB['avg_degree_connectivity']=[temp.values()]
        if optionB['avg_degree_centrality']==True:
            temp = nx.degree_centrality(GB)
            avg=0.0
            for val in temp.values():
                avg+=val
            optionB['avg_degree_centrality']=[avg/len(temp)]            
            if store_n_e_atts == True:
                for key in temp: GB.node[key]['avg_degree_centrality'] = temp[key]
        if optionB['avg_closeness_centrality']==True:
            temp = nx.closeness_centrality(GB)
            avg=0.0
            for val in temp.values():
                avg+=val
            optionB['avg_closeness_centrality']=[avg/len(temp)]            
            if store_n_e_atts == True:
                for key in temp: GB.node[key]['avg_closeness_centrality'] = temp[key]
        if optionB['diameter']==True:
            optionB['diameter']=[nx.diameter(GB)]
            
    #----------------specific metrics for dependency failures------------------
    if failure['dependency']==True or failure['interdependency']== True:
        if failure['dependency']==True:
            dependency_metrics = {'nodes_removed_from_A':False, 'no_of_nodes_removed_from_A':False,
                              'nodes_removed_from_B':[[]], 'no_of_nodes_removed_from_B':[0]}
        else: dependency_metrics = {'nodes_removed_from_A':[[]], 'no_of_nodes_removed_from_A':[0],
                              'nodes_removed_from_B':[[]], 'no_of_nodes_removed_from_B':[0]}
    else: dependency_metrics = None
    
    #----------------specific metrics for cascading analysis-------------------
    if failure['cascading']== True:
        cascading_metrics = {'dead':random.choice(GA.nodes()),'dlist':[],'removed_nodes':[],'deadlist':[]}
    else: cascading_metrics = None
    
    #-----------generate a node list for single random analysis----------------
    node_list = GA.nodes()
    
    ''' need to check the relevance of the lines below'''
    #----------------sort initial networks out again---------------------------
    #create a temp version of network to be used for all analysis
    GtempA = GA.copy() 
    if GB == None: GB = nx.Graph()
    GtempB = GB.copy()
       
    #----------------package stuff up------------------------------------------
    metrics = basicA,basicB,optionA,optionB,dependency_metrics,cascading_metrics
    networks = GA, GB, GtempA, GtempB
    graphparameters = networks,i,node_list,to_b_nodes,from_a_nodes 
    return networks,metrics,graphparameters
    
    
def default_parameters(fileName, failure, basicA=None, optionA=None, basicB=None, optionB=None):
    #metrics
    if basicA <> None: pass
    else: basicA = {'nodes_removed':True,'no_of_nodes_removed':True,'no_of_nodes':True,'no_of_edges':True,'no_of_components':True,'no_of_isolated_nodes':True,'isolated_nodes_removed':True,'nodes_selected_to_fail':True}
    if optionA <> None: pass
    else: optionA = {'size_of_components':False,'giant_component_size':False,'avg_size_of_components':False,'isolated_nodes':False,'no_of_isolated_nodes_removed':False,'subnodes':False,'no_of_subnodes':False,'avg_path_length':False,'avg_path_length_of_components':False,'avg_path_length_of_giant_component':False,'avg_geo_path_length':False,'avg_geo_path_length_of_components':False,'avg_geo_path_length_of_giant_component':False,'avg_degree':False,'density':False,'maximum_betweenness_centrality':False,'avg_betweenness_centrality':False,'assortativity_coefficient':False,'clustering_coefficient':False,'transitivity':False,'square_clustering':False,'avg_neighbor_degree':False,'avg_degree_connectivity':False,'avg_degree_centrality':False,'avg_closeness_centrality':False,'diameter':False}
    if basicB <> None:pass
    else: basicB = None
    if optionB <> None:pass
    else: optionB = None
    
    dependency = None
    cascading = None
    metrics = basicA,basicB,optionA,optionB,dependency,cascading
    failure = {'stand_alone':True, 'dependency':False, 'interdependency':False,
        'single':False, 'sequential':True, 'cascading':False,
        'random':True, 'degree':False, 'betweenness':False}

    handling_variables={'remove_subgraphs':False,'remove_isolates':False,'no_isolates':False}
    a_to_b_edges = None
    parameters=metrics, failure, handling_variables, fileName, a_to_b_edges
    return parameters
    
def outputresults(graphparameters, parameters, metrics, logfilepath=None,multiterations=False):
    values,error = outputs.outputresults(graphparameters, parameters, metrics, logfilepath,multiterations)
    return values
