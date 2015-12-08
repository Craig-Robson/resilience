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

import os, sys, random
import networkx as nx


#custom modules
#sys.path.append("C:\\a8243587_DATA\\GitRepo\\resilience\\modules")
#sys.path.append("C:\\Users\\Craig\\GitRepo\\resilience\\modules")
#sys.path.append("H:\\A-PHD\\resilience\\modules")
sys.path.append(os.path.dirname(__file__)+"\modules")
import tools,error_classes,failure_methods,network_handling,outputs

def import_modules(resil_mod_loc):
    sys.path.append(resil_mod_loc)
    global tools, error_classes, failure_methods, network_handling, outputs
    import tools,error_classes,failure_methods,network_handling,outputs

def main(GA, GB, parameters, logfilepath, viewfailure=False, when_to_calc_metrics=True,failures_to_occur=False):
    '''
    This is the main control function when the analysis is run directly from
    the script. This reads in the data provided and processes it as such to run
    the desired analysis.
    Input: up to two networks, parameters and a logfile path.
    Returns: a boolean varalible stating if the analysis has been completed.
    '''

    '''
    try:
        import_modules(os.path.dirname(__file__)+"\modules")
        tools.write_to_log_file(logfilepath, 'Imported modules.')
    except:
        # cant write to log file as cant access the module to do this
        return 1102
    '''
    print('in main function')
    print(GA.number_of_nodes())
    print(GA.number_of_edges())
    try:
        var = tools.write_to_log_file(logfilepath, 'In function after importing modules')
    except:
        return var

    metrics,failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length,source_nodes_A,source_nodes_B = parameters
    tools.write_to_log_file(logfilepath, 'Calculating the inital metrics.')

    #------set up the metrics for the analysis being asked for-----------------
    try:
        var = metrics_initial(GA,GB,metrics,failure,handling_variables,store_n_e_atts,length,a_to_b_edges,source_nodes_A,source_nodes_B, logfilepath)
    except:
        return 1106
    print('got this far')
    if type(var) == int:
        tools.write_to_log_file(logfilepath, 'Error code %s returned. Failure in metrics_initial function.')
        return var
    else:
        networks,metrics,graphparameters = var

    networks,i,node_list,to_b_nodes,from_a_nodes = graphparameters
    basicA,basicB,optionA,optionB,interdependency_metrics,cascading_metrics = metrics
    parameters=failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length
    node_to_fail_list = {}
    #------run some tests to check inputs are correct--------------------------
    try:
        var = tools.check_inputs(failure)
        if type(var) == int:
            tools.write_to_log_file(logfilepath, 'Error code %s returned. Incorrect input parameters were specified.')
            return var
    except:
        return 1108
    tools.write_to_log_file(logfilepath,'Checked inputs and returned as correct.')

    i = 0;iterate = True

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
    if write_step_to_db:
        var = outputs.write_to_db(networks,a_to_b_edges,failure,db_parameters,i)
        if type(var) == int:
            tools.write_to_log_file(logfilepath, 'Error code %s returned. Could not write network to database.' %(var))
            return var

    #-----------------write metrics to database table t = 0--------------------
    if write_results_table:
        var = outputs.write_results_table(metrics,i,failure,db_parameters,k=0)
        if type(var) == int:
            tools.write_to_log_file(logfilepath, 'Error code %s returned. Could not write results to table in database.' %(var))
            return var

    i +=1

    graphparameters=networks,i,node_list,to_b_nodes,from_a_nodes,source_nodes_A,source_nodes_B
    #run the analysis if seuquential or cascading == true
    if failure['sequential']==True or failure['cascading']==True or failure['stand_alone']==True:
        #while iterate is still true- network still has edges left

        while iterate == True:
            print('----------------------------------------------')
            print('i is:', i)
            #-------------update log file (if file path set)-------------------
            #tools.write_to_log_file(logfilepath,'Initiating step')
            #-------------run the step-----------------------------------------
            graphparameters = networks,i,node_list,to_b_nodes,from_a_nodes,source_nodes_A, source_nodes_B
            try:
                var = step(graphparameters,parameters,metrics,iterate,logfilepath,when_to_calc_metrics,failures_to_occur,node_to_fail_list)
                if type(var) == int:
                    tools.write_to_log_file(logfilepath,'Error code %s returned. Error running step %s.' %(var,i))
                    return var
                else:
                    gaphparameters,parameters,metrics,iterate = var
            except:
                tools.write_to_log_file(logfilepath,'Error running step %s. Failed.' %(i))
                return 1100

            #-------------unpack variables-------------------------------------
            basicA,basicB,optionA,optionB,interdependency,cascading = metrics
            networks,k,node_list,to_b_nodes,from_a_nodes,source_nodes_A, source_nodes_B = graphparameters

            #-------------write networks to database---------------------------
            if write_step_to_db:
                var = outputs.write_to_db(networks,a_to_b_edges,failure,db_parameters,i)
                if type(var) == int:
                    tools.write_to_log_file(logfilepath, 'Error code %s returned. Error when writing network for step %s to database.' %(var, i))
                    return var

            #-------------write metrics to database table----------------------
            if write_results_table:
                var = outputs.write_results_table(metrics,i,failure,db_parameters,k)
                if type(var) == int:
                    tools.write_to_log_file(logfilepath, 'Error code %s returned. Errors when writing metric values to databse for step %s.' %(var, i))
                    return var

            if i == 2000 or i == 4000 or i == 6000 or i == 8000 or i == 10000 or i == 12000 or i == 14000 or i == 16000 or i == 18000 or i == 20000 or i == 22000 or i == 24000 or i == 26000 or i == 28000 or i == 30000:
                # this is where I want to write some results our and clear the data holders
                #var = outputs.outputresults(graphparameters,parameters,metrics,logfilepath=None)
                basicA,basicB,optionA,optionB,dependency,cascading=metrics
                outfile = fileName.replace('.txt','_%s.txt'%i)
                of = open(outfile,'a')
                for key in basicA:
                    of.write('%s: %s\n' %(key,basicA[key]))
                    if type(basicA[key]) == list:
                        pass
                for key in optionA:
                    of.write('%s: %s\n' %(key,optionA[key]))
                    if type(optionA[key]) == list:
                        optionA[key] = [optionA[key][-1]]
                of.close()
                tools.write_to_log_file(logfilepath,'Written some results out')
            if i == 300: iterate = False

            #-------------update log file (if file path set)-------------------
            try:
                tools.write_to_log_file(logfilepath,'Step %s completed.(%s nodes left; %s edges left).' %(i,basicA['no_of_nodes'][-1],basicA['no_of_edges'][-1]))
            except:pass
            #-------------stop if stand alone and all nodes have been removed--
            if failure['stand_alone']==True:
                if i == nx.number_of_nodes(networks[2]): iterate = False
            #-------------update i as iteration finished-----------------------
            print('updating i:', i)
            i += 1

        if iterate == False:
            try:
                #no edges left so output results
                var = outputs.outputresults(graphparameters,parameters,metrics,logfilepath=None)
                if type(var) == int:
                    tools.write_to_log_file(logfilepath, 'Error code %s returned. Failed when trying to write the final set of results out at end of analysis.' %(var))
                    return var
                else:
                    complete = True
            except:
                tools.write_to_log_file(logfilepath, 'Failed when trying to export results. No error code returned.')
                return 1005

    elif failure['stand_alone']==True:
        pass
    else:
        #print "No analysis method selected"
        return 1101

    #complete = None
    #print "Completed simulation"
    #update log file - only works if file path is set
    tools.write_to_log_file(logfilepath,'Completed analysis!')
    return complete

def step(graphparameters, parameters, metrics, iterate, logfilepath,when_to_calc_metrics,failures_to_occur,node_to_fail_list):
    '''
    Performs one time step of analysis when called.
    Inputs: graphparameters, parameters iterate
    Returns: graphparameters, iterate
    '''
    print('Running step')
    #----------------unpack all the data containers----------------------------
    failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length = parameters
    basicA,basicB,optionA,optionB,dependency,cascading = metrics
    networks,i,node_list,to_b_nodes,from_a_nodes,source_nodes_A,source_nodes_B = graphparameters
    GA, GB, GtempA, GtempB = networks
    #calc_metrics_all_steps == True #or = 10 for example

    #----------------perform the analsis---------------------------------------
    #----------------for sequential analysis only------------------------------
    #look at adding ability to remove nodes from both A and B
    if failure['sequential'] and failure['single']==False and failure['cascading']==False:
        failures_to_occur = 3
        try:
            if failure['degree']:
                #find node based on highest degree and remove it
                var = failure_methods.sequential_degree(GtempA,failure['interdependency'])
                if type(var) == int:
                    pass
                else: GtempA,node = var

            elif failure['betweenness']:
                if failures_to_occur == False:
                    #find node with highest betweenness value and remove it
                    var = failure_methods.sequential_betweenness(GtempA,failure['interdependency'])
                    if type(var) == int:
                        pass
                    else: GtempA,node = var
                elif failures_to_occur == True:
                    tools.write_to_log_file(logfilepath,'Error in finding node to remove. Fail to calc variable incorrectly set.')
                    return 1001
                else:
                    #used to remove features using a pre-calculated list
                    print('Using listing betweenness method')
                    var = failure_methods.sequential_betweenness_by_list(GtempA,failure['interdependency'],failures_to_occur,node_to_fail_list)
                    if type(var) == int:
                        print(var)
                        pass
                    else:
                        GtempA,node,node_to_fail_list = var
                    print('Generated list:', node_to_fail_list)

            elif failure['from_list']!=False:
                print('THIS METHOD HAS NOT BEEN FINISHED OR TESTED')
                fail_list = []
                var = failure_methods.sequential_from_list(GtempA,failure['interdependency'],fail_list,i)
                if type(var) == int:
                    pass
                else: GtempA,node = var

            elif failure['random']:
                #randomly select the next node and remove it
                var = failure_methods.sequential_random(GtempA, handling_variables['no_isolates'],failure['interdependency'])
                if type(var) == int:
                    pass
                else: GtempA,node = var

            elif failure['flow']:
                #select the node with the greatest flow - uses field named 'flow'
                var = failure_methods.sequential_flow(GtempA, handling_variables['no_isolates'],failure['interdependency'])
                if type(var) == int:
                    pass
                else: GtempA,node = var

            else:
                tools.write_to_log_file(logfilepath, 'Error in failure dictionary - no component selection method chosen (set as True). Sequential process chosen.')
                return 1001
        except:
            tools.write_to_log_file(logfilepath, 'Error in finding the next node to remove given selection method. Sequential process chosen.')
            return 1002
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
            elif g.number_of_nodes != 0:
                optionA['subnodes'].append(g.nodes())
            else:
                raise error_classes.GeneralError('Error. Component has zero nodes.')
                #------------on the first time step only-----------------------
        #need to initaite the failure through remoiving a node to begin with
        if i == 1:
            if failure['degree'] and failure['betweenness']==False and failure['random']==False:
                var = tools.max_val_random(nx.degree(GtempA))
                if type(var) == int:
                    return var+1
                else: ma, dead = var
            elif failure['betweenness']==True and failure['random']==False and failure['degree']==False:
                var = tools.max_val_random(nx.betweenness_centrality(GtempA))
                if type(var) == int:
                    return var+2
                else: ma, dead = var
            elif failure['random']==True and failure['degree']==False and failure['betweeness']==False:
                dead = dead
            elif failure['flow']==True:
                ma, dead = tools.maximum_flow(GtempA)
            #update the network and find the next set of nodes to remove
            var = failure_methods.cascading_failure(GtempA,dlist,dead,i,basicA['subnodes'], basicA['isolated_nodes'],basicA['nodes_removed'],failure['interdependency'])
            if type(var) == int:
                return var
            else: GtempA,dlist,removed_nodes,deadlist = var

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
        var = failure_methods.single_random(GtempA, node_list, failure['interdependency'])
        if type(var) == int:
            return var
        else: GtempA,node = var

        #------------when node list is empty change iterate------------------
        if node_list == []:
            iterate = False
        #update the metric
        basicA['no_of_nodes_removed'].append(1)

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
                var = network_handling.check_dependency_edges(GtempA, GtempB, node, to_b_nodes, from_a_nodes, temp)
                GtempA, GtempB, to_b_nodes, from_a_nodes, temp = var
                if type(var) == int:
                    tools.write_to_log_file(logfilepath, 'Error code %s returned. Could not find chosen node ro remove (check_dependency_edges).' %(var))
                    return var
                x += 1
        #------------run for all other analysis scenarios--------------------
        else:
            if GtempA.number_of_edges() != 0:
                nodes_removed=[]
                #are we using source nodes
                if source_nodes_A != None:
                    var = network_handling.check_connected_to_source_nodes(GtempA,source_nodes_A,nodes_removed)
                    if type(var) == int:
                        tools.write_to_log_file(logfilepath, 'Error code %s returned.' %(var))
                        return var
                    else:
                        GtempA,nodes_removed = var

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
                var = network_handling.check_dependency_edges(networks,nodes_removed,basicA,basicB,optionA,optionB,to_b_nodes,from_a_nodes,a_to_b_edges,temp,failure['interdependency'])
                if type(var) == int:
                    raise error_classes.SearchError('Error. Could not find chosen node to remove it.')
                    tools.write_to_log_file(logfilepath, 'Error code %s returned. Could not find chosen node ro remove (check_dependency_edges).' %(var))
                    return var
                else:
                    #un-pack variables returned
                    networks,nodes_removed_from_b,basicA,basicB,optionA,optionB,to_b_nodes,from_a_nodes,a_to_b_edges = var
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
                    var = network_handling.check_connected_to_source_nodes(GtempB,source_nodes_B,nodes_removed)
                    if type(var) == int:
                        tools.write_to_log_file(logfilepath, 'Error code %s returned.' %(var))
                        return var
                    else:
                        GtempB,nodes_removed = var

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
        try:
            var = analysis_B(parameters,iterate,GtempB,i,to_b_nodes,from_a_nodes,node_list,basicB,optionB,to_b_nodes,from_a_nodes,source_nodes_B,when_to_calc_metrics,logfilepath,net='B')
            if type(var) == int:
                 tools.write_to_log_file(logfilepath, 'Error code %s returned. Failed running the post component removal analysis.')
                 return
            else:
                iterate,GtempB,i,to_a_nodes,from_b_nodes,a_to_b_edges,node_list,basicB,optionB,source_nodes_B = var
        except:
            tools.write_to_log_file(logfilepath, 'Failed when running analysis of network B.')
        #analyse network A
        try:
            var = analysis_B(parameters,iterate,GtempA,i,to_b_nodes,from_a_nodes,node_list,basicA,optionA,to_b_nodes,from_a_nodes,source_nodes_A,when_to_calc_metrics,logfilepath,net='A')
            if type(var) == int:
                tools.write_to_log_file(logfilepath, 'Error code %s returned. Failed running the post component removal analysis.' %(var))
                return
            else:
                iterate,GtempA,i,to_a_nodes,from_b_nodes,a_to_b_edges,node_list,basicA,optionA,source_nodes_A = var
        except:
            tools.write_to_log_file(logfilepath, 'Failed when running analysis of network A.')

        if i != -100: basicA['nodes_removed'].append(basicA['nodes_removed'].pop()+basicA['isolated_nodes_removed'][i])
        if optionA['failed_no_con_to_a_source'] != False:
            basicA['no_of_nodes_removed'].append(basicA['no_of_nodes_removed'].pop()+len(optionA['failed_no_con_to_a_source'][len(optionA['failed_no_con_to_a_source'])-1]))
        if optionB['failed_no_con_to_a_source'] != False:
            basicB['no_of_nodes_removed'].append(basicB['no_of_nodes_removed'].pop()+len(optionB['failed_no_con_to_a_source'][len(optionB['failed_no_con_to_a_source'])-1]))

        #------------move counter on-----------------------------------------
        i += 1

    elif failure['stand_alone'] and failure['dependency']==False and failure['interdependency']==False :
        try:
            if GtempA.number_of_edges() != 0:
                #check all nodes still contected to a source node if set
                if source_nodes_A != None:
                    nodes_removed=[]
                    var = network_handling.check_connected_to_source_nodes(GtempA,source_nodes_A,nodes_removed)
                    if type(var) == int:
                        tools.write_to_log_file(logfilepath, 'Error code %s returned.' %(var))
                        return var
                    else:
                        GtempA,nodes_removed = var
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
        except:
            tools.write_to_log_file(logfilepath, 'Failed running flow checks on network.')
            return 1010

        #run the analysis
        try:
            var = analysis_B(parameters,iterate,GtempA,i,to_b_nodes,from_a_nodes,node_list,basicA,optionA,to_b_nodes, from_a_nodes,source_nodes_A,when_to_calc_metrics,logfilepath,net='A') #run the analysis
            if type(var) == int:
                 tools.write_to_log_file(logfilepath, 'Error code %s returned. Failed running the post component removal analysis.')
                 return var
            else:
                iterate,GtempA,i,to_a_nodes,from_b_nodes,a_to_b_edges,node_list,basicA,optionA,source_nodes_A = var
        except:
            tools.write_to_log_file(logfilepath, 'Failed when running analysis. No error code returned.')
            return 1011

        if i != -100:
            basicA['nodes_removed'].append(basicA['nodes_removed'].pop()+basicA['isolated_nodes_removed'][i])
        if optionA['failed_no_con_to_a_source'] != False:
            basicA['nodes_removed'].append(basicA['nodes_removed'].pop()+optionA['failed_no_con_to_a_source'][i])
        if optionA['failed_no_con_to_a_source'] != False:
            basicA['no_of_nodes_removed'].append(basicA['no_of_nodes_removed'].pop()+len(optionA['failed_no_con_to_a_source'][len(optionA['failed_no_con_to_a_source'])-1]))

        i += 1
    else:
        tools.write_to_log_file(logfilepath, 'No analysis type selected.')
        raise error_classes.GeneralError('Error. No analysis type has been selected.')
        return 1003

    #----------------re-package all data into respective containers------------
    networks = GA, GB, GtempA, GtempB
    metrics = basicA,basicB,optionA, optionB,dependency,cascading
    graphparameters = networks,i,node_list,to_b_nodes,from_a_nodes,source_nodes_A,source_nodes_B
    parameters =  failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length
    var = graphparameters,parameters,metrics,iterate
    return var

'''calcualte values at end of step'''
def analysis_B(parameters,iterate,Gtemp,i,to_a_nodes,from_b_nodes,node_list,basic_metrics,option_metrics,to_b_nodes,from_a_nodes,source_nodes,when_to_calc_metrics,logfilepath,net):
        '''
        Failure method has already been run. This checks for isolated nodes and
        subgraphs (goes throught the handling avraibles, then calculates metrics
        required.)

        All errors from here bgein with 20. e.g. 2003
        '''
        '''
        try:
            tools.write_to_log_file(logfilepath, 'Entered analysis B function.')
        except:
            return 2000
        '''
        print('analysis B i is:', i)

        #------------unpack the holding variables------------------------------
        if len(parameters) == 9:
            pass
        else:
            return 2051

        try:
            failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length = parameters
        except: return 2034

        try:
            basic_metrics['no_of_isolated_nodes'].append(len(nx.isolates(Gtemp)))
        except: return 2035


        #------------check for isoalted nodes----------------------------------
        try:
            if handling_variables['remove_isolates']==True:
                if Gtemp.number_of_edges() != 0:
                    var = network_handling.remove_isolates(Gtemp,node_list,option_metrics,basic_metrics,to_b_nodes,from_a_nodes,a_to_b_edges,net)
                    if type(var) == int:
                        return var
                    else:
                        Gtemp,node_list,basic_metrics,option_metrics,isolated_nodes,to_b_nodes,from_a_nodes,a_to_b_edges = var
                    #not too sure why I need separate things for net a and b??
                    if net == 'B':
                        if option_metrics['isolated_nodes']!=False:
                            option_metrics['isolated_nodes'].append(isolated_nodes)
                        if option_metrics['no_of_isolated_nodes_removed']!=False:
                            option_metrics['no_of_isolated_nodes_removed'].append(len(isolated_nodes))
                        basic_metrics['isolated_nodes_removed'].append(isolated_nodes)
                        basic_metrics['no_of_nodes_removed'].append(basic_metrics['no_of_nodes_removed'].pop()+len(isolated_nodes))
                        basic_metrics['nodes_removed'].append(basic_metrics['nodes_removed'].pop()+basic_metrics['isolated_nodes_removed'][i])
                    if net == 'A':
                        basic_metrics['isolated_nodes_removed'].append(isolated_nodes)
                        if option_metrics['isolated_nodes']!=False:
                            option_metrics['isolated_nodes'].append(isolated_nodes)
                        if option_metrics['no_of_isolated_nodes_removed']!=False:
                            option_metrics['no_of_isolated_nodes_removed'].append(len(isolated_nodes))
                    if source_nodes != None:
                        for nd in isolated_nodes:
                            try: source_nodes.remove(nd)
                            except: pass
                else:
                    if option_metrics['isolated_nodes']!=False:
                        option_metrics['isolated_nodes'].append([])
                    if option_metrics['no_of_isolated_nodes_removed']!=False:
                        option_metrics['no_of_isolated_nodes_removed'].append(0)
                    basic_metrics['isolated_nodes_removed'].append([])

            elif handling_variables['remove_isolates']==False:
                if option_metrics['no_of_isolated_nodes_removed'] != False:
                    option_metrics['no_of_isolated_nodes_removed'].append(0)
                basic_metrics['isolated_nodes_removed'].append([])
                if option_metrics['isolated_nodes']!=False:
                    option_metrics['isolated_nodes'].append([nx.isolates(Gtemp)])
        except: return 2028
        #----------------if the graph is still connected-----------------------
        try:
            num_edges = Gtemp.number_of_edges()
        except: return 2036

        try:
            if num_edges != 0:
                try:
                    #the graph is not dissconnected
                    nodelists = Gtemp.nodes()
                    edgelists = Gtemp.edges()
                    #if subgraphs are to be removed for the analysis ie. for infrastructure modelling

                    if handling_variables['remove_subgraphs']==True:
                        #remove subgraphs and record the details of them
                        var = network_handling.handle_sub_graphs(Gtemp)

                        if type(var) == int:
                            return var
                        else:
                            Gtemp, subnodes, nsubnodes, nodelists, edgelists = var

                        if option_metrics['subnodes'] != False:
                            option_metrics['subnodes'].append(subnodes)
                        basic_metrics['no_of_nodes_removed'].append(basic_metrics['no_of_nodes_removed'].pop()+nsubnodes)
                        if option_metrics['no_of_subnodes'] != False:
                            option_metrics['no_of_subnodes'].append(nsubnodes)

                        nodes_removed = basic_metrics['nodes_removed'].pop()
                        for subgraph in subnodes:
                            for nd in subgraph:
                                nodes_removed.append(nd)
                        basic_metrics['nodes_removed'].append(nodes_removed)
                        if source_nodes != None:
                            for nd in nodes_removed:
                                try: source_nodes.remove(nd)
                                except: pass

                        var =  network_handling.clean_node_lists(subnodes,node_list,to_b_nodes,from_a_nodes)
                        if type(var) == int:
                            return var
                        else:
                            node_list, to_b_nodes, from_a_nodes = var

                        temp = nx.connected_component_subgraphs(Gtemp)
                        basic_metrics['no_of_components'].append(len(temp))

                    #if subgraphs are to be left as part of the network
                    elif handling_variables['remove_subgraphs']==False:

                        #get a list of all connected components
                        temp = nx.connected_component_subgraphs(Gtemp)
                        number_of_components = nx.number_connected_components(Gtemp)
                        #add the number components to the respective list
                        basic_metrics['no_of_components'].append(number_of_components)

                        temp=[]
                        if option_metrics['subnodes']!=False:
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
                            if option_metrics['no_of_subnodes']!=False:
                                option_metrics['no_of_subnodes'].append(no_of_subnodes)
                    else:
                        #there is an error with the variable
                        raise error_classes.GeneralError('Error. Variable REMOVE_SUBGRAPHS must be set as True or False only.')
                except: return 2050
            #------------run if no edges left--------------------------------------
            elif num_edges == 0:
                try:
                    #at the last removal of a node, all remaining edges were consequently remove
                    #update the metrics
                    if option_metrics['subnodes'] != False: option_metrics['subnodes'].append([])
                    if option_metrics['no_of_subnodes'] != False: option_metrics['no_of_subnodes'].append(0)
                except: return 2051
        except:
            return 2036

        #-------metric calcs which work no matter the state of the network-----
        try:
            if option_metrics['size_of_components']!=False:
                try:
                    temp = []
                    for g in nx.connected_component_subgraphs(Gtemp):
                        temp.append(g.number_of_nodes())
                    option_metrics['size_of_components'].append(temp)
                except: return 2027

            #when_to_calc_metrics = 5 #here for testing

            print('i:',i)
            if when_to_calc_metrics != True: # if it has been set as number
                print('Checking to calc metrics or not:', when_to_calc_metrics)
                calc_metrics = False
                calc_value = 0
                while calc_metrics == False:
                    print('in check loop')
                    print(('i:',i,' - calc value:',calc_value))
                    if i == calc_value:
                        calc_metrics = True
                        print('Record values')
                    elif calc_value > i:
                        print('Skipping')
                        break
                    else:
                        calc_value = calc_value + when_to_calc_metrics
            elif when_to_calc_metrics == True:
                calc_metrics = True

            if calc_metrics == True:

                if option_metrics['maximum_betweenness_centrality']!=False or option_metrics['avg_betweenness_centrality']!=False:
                    try:
                        temp = nx.betweenness_centrality(Gtemp)
                    except:
                        tools.write_to_log_file(logfilepath, 'Failed when calculating the betweenness centrality.')
                        return 2006
                    if option_metrics['maximum_betweenness_centrality']!=False:
                        option_metrics['maximum_betweenness_centrality'].append(max(temp.values()))
                    if option_metrics['avg_betweenness_centrality']!=False:
                        try:
                            avg=0.0
                            for val in list(temp.values()):
                                avg+=val
                            option_metrics['avg_betweenness_centrality'].append(avg/len(temp))
                        except: return 2026

                        if store_n_e_atts == True:
                            for key in temp: Gtemp.node[key]['betweenness_centrality'] = temp[key]

                if option_metrics['clustering_coefficient']!=False:

                    try:
                        temp = nx.clustering(Gtemp)
                        failed_calc = False
                    except:
                        tools.write_to_log_file(logfilepath, 'Failed when calculating the clustering coefficient.')
                        option_metrics['clustering_coefficient'].append(-9999)
                        failed_calc = True
                        pass
                        #return 2007
                    if failed_calc == False:
                        try:
                            avg = sum(temp.values())/len(temp)
                        except: return 2032

                        try:
                            option_metrics['clustering_coefficient'].append(avg)
                        except:
                            tools.write_to_log_file(logfilepath, 'Failed adding the clusteirng coefficeint value to the metric list. The list is:')
                            tools.write_to_log_file(logfilepath, option_metrics['clustering_coefficient'])
                            tools.write_to_log_file(logfilepath, avg)
                            #return 2031

                    if store_n_e_atts == True:
                            for key in temp: Gtemp.node[key]['clustering_coefficient'] = temp[key]

                if option_metrics['transitivity']!=False:
                    try:
                        option_metrics['transitivity'].append(nx.transitivity(Gtemp))
                    except:
                        tools.write_to_log_file(logfilepath, 'Failed to calculate the transitivity.')
                        return 2008
                if option_metrics['square_clustering']!=False:
                    try:
                        temp = nx.square_clustering(Gtemp)
                        avg=0.0
                        for val in list(temp.values()):
                            avg+=val
                        avg = avg/len(temp)
                    except:
                        tools.write_to_log_file(logfilepath, 'Failed to calculate the square clustering coefficient.')
                        return 2009

                    option_metrics['square_clustering'].append(avg)
                    if store_n_e_atts == True:
                            for key in temp: Gtemp.node[key]['square_clustering'] = temp[key]
                if option_metrics['avg_degree_connectivity'] != False:
                    try:
                        temp = nx.average_degree_connectivity(Gtemp)
                    except:
                        tools.write_to_log_file(logfilepath, 'Failed calculating the average degree connectivity.')
                        return 2010
                    option_metrics['avg_degree_connectivity'].append(list(temp.values()))
                if option_metrics['avg_closeness_centrality'] != False:
                    try:
                        temp = nx.closeness_centrality(Gtemp)
                        avg=0.0
                        for val in list(temp.values()):
                            avg+=val
                        avg = avg/len(temp)
                    except:
                        tools.write_to_log_file(logfilepath, 'Failed calculating the closeness centrality.')
                        return 2011

                    option_metrics['avg_closeness_centrality'].append(avg)
                    if store_n_e_atts == True:
                            for key in temp:
                                Gtemp.node[key]['avg_closeness_centrality'] = temp[key]

                if option_metrics['avg_neighbor_degree'] != False:
                    try:
                        temp = nx.average_neighbor_degree(Gtemp)
                        avg=0.0
                        for val in list(temp.values()):
                            avg+=val
                        avg = avg/len(temp)
                    except:
                        tools.write_to_log_file(logfilepath, 'Failed to calculate the average neighbor degree.')
                        return 2012

                    option_metrics['avg_neighbor_degree'].append(avg)
                    if store_n_e_atts == True:
                            for key in temp: Gtemp.node[key]['avg_neighbor_degree'] = temp[key]
            #elif calc_metrics == False:
                #return 99999999999999
                #exit()
            else:

                if option_metrics['maximum_betweenness_centrality']!=False:
                    option_metrics['maximum_betweenness_centrality'].append(-9998)
                if option_metrics['avg_betweenness_centrality']!=False:
                    option_metrics['avg_betweenness_centrality'].append(-9998)
                if option_metrics['clustering_coefficient']!=False:
                    option_metrics['clustering_coefficient'].append(-9998)
                if option_metrics['transitivity']!=False:
                    option_metrics['transitivity'].append(-9998)
                if option_metrics['square_clustering']!=False:
                    option_metrics['square_clustering'].append(-9998)
                if option_metrics['avg_degree_connectivity']!=False:
                    option_metrics['avg_degree_connectivity'].append(-9998)
                if option_metrics['avg_closeness_centrality']!=False:
                    option_metrics['avg_closeness_centrality'].append(-9998)
                if option_metrics['avg_neighbor_degree']!=False:
                    option_metrics['avg_neighbor_degree'].append(-9998)
        except:
            return 2053

        #------------re-calc the number of edges-------------------------------
        #this is needed if subgraphs were removed
        try:
            numofedges = None
            try:
                numofedges = nx.number_of_edges(Gtemp)
            except: pass
            if numofedges == None:
                try:
                    edges = Gtemp.edges()
                    numofedges = len(edges)
                except:
                    return 20376
        except:
            tools.write_to_log_file(logfilepath, 'Failed to count the number of edges in the network.')
            tools.write_to_log_file(logfilepath, 'Number of nodes in the network = %s' %(nx.number_of_nodes(Gtemp)))
            return 2037
        #------------if there are no edges left--------------------------------

        try:
            if numofedges == 0:

                #set i really high so iteraion stops at the end of this step
                i = -100
                #add values for the metrics which are not set as False
                try:
                    if option_metrics['avg_path_length'] != False:
                        option_metrics['avg_path_length'].append(0.0)
                    if option_metrics['avg_path_length_of_components']!=False:
                        option_metrics['avg_path_length_of_components'].append([0.0])
                    if option_metrics['avg_path_length_of_giant_component']!= False:
                        option_metrics['avg_path_length_of_giant_component'].append(0.0)
                    if option_metrics['avg_geo_path_length'] != False:
                        option_metrics['avg_geo_path_length'].append(0.0)
                    if option_metrics['avg_geo_path_length_of_components']!=False:
                        option_metrics['avg_geo_path_length_of_components'].append([0.0])
                    if option_metrics['avg_geo_path_length_of_giant_component']!=False:
                        option_metrics['avg_geo_path_length_of_giant_component'].append(0.0)
                    if option_metrics['giant_component_size'] != False:
                        option_metrics['giant_component_size'].append(0)
                    if option_metrics['avg_degree'] != False:
                        option_metrics['avg_degree'].append(0)
                    if option_metrics['density']!=False:
                        option_metrics['density'].append(0.0)
                    if option_metrics['assortativity_coefficient']!=False:
                        option_metrics['assortativity_coefficient'].append(0.0)
                    if option_metrics['avg_degree_centrality']!=False:
                        option_metrics['avg_degree_centrality'].append(0.0)
                    if option_metrics['diameter']!=False:
                        option_metrics['diameter'].append(0.0)
                    #if option_metrics['avg_size_of_components']<>False: option_metrics['avg_size_of_components']=0
                    basic_metrics['no_of_components'].append(nx.number_connected_components(Gtemp))
                    basic_metrics['no_of_edges'].append(0)
                except:
                    return 2021
                #set iterate as False so it stops after this time step
                iterate = False

            #------------if the number of edge is greater than zero----------------
            elif numofedges != 0:

                try:
                    #---------------average path length calculations-------------------
                    if option_metrics['avg_path_length'] != False or option_metrics['avg_path_length_of_components']!=False:
                        try:
                            #claculates the average path length of the whole network if not dissconnected
                            #average = network_handling.whole_graph_av_path_length(Gtemp)
                            temp=[]
                            for g in nx.connected_component_subgraphs(Gtemp):
                                try:
                                    temp.append(nx.average_shortest_path_length(g))
                                except:
                                    # could not calculate the averag path length
                                    tools.write_to_log_file(logfilepath, 'Escaped from calculating the average path length of a subgraph. Did not add it to the list.')
                                    pass
                            try:
                                if temp == []:
                                    tools.write_to_log_file(logfilepath, 'The path length for all components of the network could not be calculated')
                                    return 2016
                            except:
                                return 2017

                            try:
                                tools.write_to_log_file(logfilepath,'Option_metrics[avg_path_length] = %s.' %(option_metrics['avg_path_length']))
                                if option_metrics['avg_path_length']!=False:
                                    try:
                                        option_metrics['avg_path_length'].append(sum(temp)/len(temp))
                                    except:
                                        return 2019
                            except:
                                return 2018
                            try:
                                if option_metrics['avg_path_length_of_components']!=False:
                                    option_metrics['avg_path_length_of_components'].append(temp)
                            except:
                                return 2020
                        except:
                            tools.write_to_log_file(logfilepath,'Failed to calculate the average path length.')
                            return 2001
                    if option_metrics['avg_path_length_of_giant_component'] != False and option_metrics['avg_path_length']!=False:
                        try:
                            option_metrics['avg_path_length_of_giant_component'].append(temp[0])
                        except:
                            tools.write_to_log_file(logfilepath, 'Failed to get average path length of giant component. List must be empty.')
                            return 2002
                    elif option_metrics['avg_path_length_of_giant_component']!=False:
                        try:
                            av_len = nx.average_shortest_path_length(nx.connected_component_subgraphs(Gtemp)[0])
                            option_metrics['avg_path_length_of_giant_component'].append(av_len)
                        except:
                            tools.write_to_log_file(logfilepath, 'Failed to calculate the average path length of the giant component.')
                            return 2003

                    length_att = False
                    if option_metrics['avg_geo_path_length']!=False or option_metrics['avg_geo_path_length_of_components']!=False:
                        try:
                            for edge in Gtemp.edges(data=True):
                                for key in list(edge[2].keys()):
                                    if key == str(length):
                                        length_att = True
                                        break
                            if length_att == True:
                                temp=[]
                                for g in nx.connected_component_subgraphs(Gtemp):
                                    try:
                                        temp.append(nx.average_shortest_path_length(g,length_att))
                                    except:
                                        # could not calculate the geographic average path length
                                        tools.write_to_log_file(logfilepath, 'Escaped from calculating the geographic average path length of a subgraph. Did not add anything to the list.')
                                        pass
                                if option_metrics['avg_geo_path_length']!=False:
                                    avg = 0
                                    for dist in temp:
                                        avg+= dist
                                    option_metrics['avg_geo_path_length'].append(avg/len(temp))
                                if option_metrics['avg_geo_path_length_of_components']!=False:
                                    option_metrics['avg_geo_path_length_of_components'].append(temp)
                            else:
                                if option_metrics['avg_geo_path_length']!=False:
                                    option_metrics['avg_geo_path_length'].append(None)
                                if option_metrics['avg_geo_path_length_of_components']!=False:
                                    option_metrics['avg_geo_path_length_of_components'].append(None)
                        except:
                                tools.write_to_log_file(logfilepath, 'Failed during the geographic average path length calculations.')
                                return 2004
                except:
                    return 2052

                try:
                    if option_metrics['avg_geo_path_length_of_giant_component'] != False and option_metrics['avg_geo_path_length']!=False:
                        option_metrics['avg_geo_path_length_of_giant_component'].append(temp[0])
                    elif option_metrics['avg_geo_path_length_of_giant_component']!=False and length_att == True:
                        av_len = nx.average_shortest_path_length(nx.connected_component_subgraphs(Gtemp)[0],length_att)
                        option_metrics['avg_geo_path_length_of_giant_component'].append(av_len)
                    elif option_metrics['avg_geo_path_length_of_giant_component']!=False and length_att == False:
                        option_metrics['avg_geo_path_length_of_giant_component'].append(None)
                except:
                    tools.write_to_log_file(logfilepath, 'Failed calculating/getting the average geographic average path length of the giant component.')
                    return 2005
                try:
                    if option_metrics['diameter'] != False:
                        try:
                            if len(nx.connected_component_subgraphs(Gtemp)) > 1:
                                option_metrics['diameter'].append('ERROR')
                            else:
                                option_metrics['diameter'].append(nx.diameter(Gtemp))
                        except:
                            return 2023
                except:
                    return 203382
                #-------------------other calculations-----------------------------

                try:
                    if option_metrics['giant_component_size'] != False:
                        try:
                            giant_component = nx.connected_component_subgraphs(Gtemp)
                            number_of_components = nx.number_connected_components(Gtemp)
                        except:
                            giant_component = None
                            #return 2031

                        if giant_component != None :

                            if number_of_components > 1:
                                # size of giant component if exists
                                try:
                                    giant_component = giant_component[0]
                                except:
                                    pass #return 2032

                                try:
                                    giant_component = nx.number_of_nodes(giant_component)
                                except:
                                    pass#return 2033
                                try:
                                    option_metrics['giant_component_size'].append(giant_component)
                                except:
                                    pass#return 20331
                            else:

                                try:
                                    giant_component = nx.number_of_nodes(Gtemp)
                                except:
                                    pass#return 2033
                                try:
                                    option_metrics['giant_component_size'].append(giant_component)
                                except:
                                    pass#return 20331

                        elif giant_component != None:
                            try:
                                giant_component = nx.number_of_nodes(Gtemp)
                            except:
                                pass #return 20332
                            try:
                                option_metrics['giant_component_size'].append(giant_component)
                            except:
                                pass#return 20333
                        else:
                            try:
                                option_metrics['giant_component_size'].append(-9999)
                            except: return 20334
                except:
                    tools.write_to_log_file(logfilepath, 'Fialed to calculate the giant component size for the network. Error 20337.')
                    option_metrics['giant_component_size'].append(-9999)
                    #return 20337

                try:
                    if option_metrics['avg_size_of_components'] != False:
                        try:
                            option_metrics['avg_size_of_components'].append(nx.number_of_nodes(Gtemp)/float(len(nx.connected_component_subgraphs(Gtemp))))
                        except: 2025
                except:
                    return 20336
                #add the number of edges to the respective list
                number_of_ed = None
                try:
                    number_of_ed = Gtemp.number_of_edges()
                except:
                    pass
                if number_of_ed == None:
                    try:
                        number_of_ed = nx.number_of_edges(Gtemp)
                    except:
                        pass
                if number_of_ed == None:
                    try:
                        number_of_ed = len(Gtemp.edges())
                    except:
                        pass
                if number_of_ed == None:
                    return 203381
                else:
                    try:
                        basic_metrics['no_of_edges'].append(number_of_ed)
                    except:
                        return 20335
                try:
                    if option_metrics['avg_degree'] != False:
                        try:
                            degree_list = Gtemp.degree()
                            sumh = 0.0
                            for d in degree_list:
                                sumh += degree_list[d]
                            option_metrics['avg_degree'].append(sumh/(nx.number_of_nodes(Gtemp)))
                            Gtemp.graph['average_degree']=sumh/nx.number_of_nodes(Gtemp)
                        except:
                            return 2022
                except:
                    return 20334
                try:
                    if option_metrics['density']!=False:
                        try:
                            option_metrics['density'].append(nx.density(Gtemp))
                        except:
                            tools.write_to_log_file(logfilepath, 'Fialed to calculate the density of the network.')
                            return 2013
                except:
                    return 20333
                try:

                    if option_metrics['assortativity_coefficient']!=False:
                        try:
                            temp = nx.degree_assortativity_coefficient(Gtemp)
                        except:
                            tools.write_to_log_file(logfilepath,'Failed to calculate the degree assortativity coefficient.')
                            tools.write_to_log_file(logfilepath,temp = nx.degree_assortativity_coefficient(Gtemp))
                            return 2014
                        if str(temp) == 'nan':
                            temp = 0.0
                            option_metrics['assortativity_coefficient'].append(temp)
                except:
                    return 20332
                try:
                    if option_metrics['avg_degree_centrality']!=False:
                        try:
                            temp = nx.degree_centrality(Gtemp)
                        except:
                            tools.write_to_log_file(logfilepath, 'Failed to calculate the degree centrality.')
                            return 2015
                        avg=0
                        for val in list(temp.values()):
                            avg+=val
                        option_metrics['avg_degree_centrality'].append(avg/len(temp))
                except:
                    return 20331
        except:
            return 20349

        #add the number of nodes left to the respective list
        try:
            basic_metrics['no_of_nodes'].append(nx.number_of_nodes(Gtemp))
        except: return 2030

        try:
            var = iterate,Gtemp,i,to_b_nodes,from_a_nodes,a_to_b_edges,node_list,basic_metrics,option_metrics,source_nodes
        except:
            return 2035

        return var

def average_path_length(G, length = None):
    '''
    '''
    temp = []

    for g in nx.connected_component_subgraphs(G):
        try:
            if length == None:
                temp.append(nx.average_shortest_path_length(g))
            else:
                temp.append(nx.average_shortest_path_length(g, length))
        except:
            # could not calculate the average path length
            pass
    return temp

def metrics_initial(GnetA, GnetB, metrics, failure, handling_variables, store_n_e_atts, length, a_to_b_edges, source_nodes_A, source_nodes_B, logfilepath):
    '''
    Calculates the metrics initally prior to any nodes or edges being removed.
    '''
    print('in metrics initial')

    #unpack the parameter
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
    if GnetB != None:
        GB = GnetB.copy()
        if GB.is_directed() == True:
            U_GB = GB.to_undirected()
        else: U_GB = None
    else: GB = GnetB

    if GA.is_directed() == True:
        U_GA = GA.to_undirected()
    else: U_GA = None
    #---------------------------set counter to---------------------------------
    i = 0
    #-------------------------basic metrics------------------------------------
    basicA['nodes_removed'] = [[]] #nodes removed from network A for any reason (fails, isolated, subgraphs)
    basicA['no_of_nodes_removed'] = [0]
    basicA['no_of_nodes'] = [nx.number_of_nodes(GA)] #the number of nodes left in network A
    basicA['no_of_edges'] = [GA.number_of_edges()] #number of edges in the network
    try:
        if U_GA == None:
            basicA['no_of_components'] = [nx.number_connected_components(GA)] #number of subgraphs
        else:
            basicA['no_of_components'] = [nx.number_connected_components(U_GA)]
    except: return 1400

    try:
        basicA['no_of_isolated_nodes'] = [len(nx.isolates(GA))]
    except: return 1401
    print('in basic metrics')
    basicA['isolated_nodes_removed'] = [[]]
    basicA['nodes_selected_to_fail'] = [[]] #only those nodes which are selected to fail

    if failure['stand_alone'] != True:
        basicB['nodes_removed'] = [[]] #nodes removed from network A for any reason (fails, isolated, subgraphs)
        basicB['no_of_nodes_removed'] = [0]
        basicB['no_of_nodes'] = [nx.number_of_nodes(GB)] #the number of nodes left in network A
        basicB['no_of_edges'] = [GB.number_of_edges()] #number of edges in the network
        try:
            if U_GB == None:
                basicB['no_of_components'] = [nx.number_connected_components(GB)] #number of subgraphs
            else:
                basicB['no_of_components'] = [nx.number_connected_components(U_GB)]
        except: return 1402

        try:
            basicB['no_of_isolated_nodes'] = [len(nx.isolates(GB))]
        except: return 1403

        basicB['isolated_nodes_removed'] = [[]]
    print('done basics')
    if store_n_e_atts == True:
        temp = nx.degree(GA)
        for key in temp:GA.node[key]['degree']=temp[key]
        temp = nx.degree(GB)
        for key in temp:GB.node[key]['degree']=temp[key]

        GA.graph['no_of_nodes']=nx.number_of_nodes(GA)
    print('starting metric calcs')
    # start of metric calculations
    var = metric_calcs(GA, U_GA, optionA, handling_variables, source_nodes_A, length, store_n_e_atts, logfilepath)
    if type(var) == int:
        return var
    else: optionA = var
    print('done first lot of calcs')
    if failure['stand_alone'] == False:
        var = metric_calcs(GB, U_GB, optionB, handling_variables, source_nodes_B, length, store_n_e_atts, logfilepath)

        if type(var) == int:
            return var
        else: optionB = var

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
    var = networks,metrics,graphparameters

    return var

def metric_calcs(G, U_G, metric_list, handling_variables, source_nodes_A, length, store_n_e_atts, logfilepath):
    '''
    Function which calculates the optional metrics for either network.
    '''
    #tools.write_to_log_file(logfilepath, 'In metric calcs.')
    print('in metric calcs')
    connected_component_subgraphs = nx.connected_component_subgraphs(G)
    number_of_components =  nx.number_connected_components(G)

    if metric_list['size_of_components']==True:
        temp = []
        try:
            if U_G == None:
                for g in connected_component_subgraphs:
                    temp.append(g.number_of_nodes())
            else:
                for g in nx.connected_component_subgraphs(U_G):
                    temp.append(nx.number_of_nodes(g))
        except: return 1404

        metric_list['size_of_components']=[temp]

    tools.write_to_log_file(logfilepath, 'Calculated size of components.')
    if metric_list['giant_component_size']==True:
            if U_G == None:
                if number_of_components != 1:
                    metric_list['giant_component_size']=[nx.number_of_nodes(nx.connected_component_subgraphs(G)[0])]
                else:
                    metric_list['giant_component_size']=[G.number_of_nodes()]
            else:
                metric_list['giant_component_size']=[nx.number_of_nodes(nx.connected_component_subgraphs(U_G)[0])]

    tools.write_to_log_file(logfilepath, 'Got giant component size.')
    if metric_list['avg_size_of_components']==True:
            if U_G == None:
                metric_list['avg_size_of_components']=[(nx.number_of_nodes(G)/number_of_components)]
            else: metric_list['avg_size_of_components']=[(nx.number_of_nodes(G)/number_of_components)]
    tools.write_to_log_file(logfilepath, 'Got average size of components.')

    if metric_list['isolated_nodes'] == True:
        metric_list['isolated_nodes'] = [nx.isolates(G)]
    tools.write_to_log_file(logfilepath, 'Got isolated nodes.')
    if handling_variables['remove_isolates'] == True or metric_list['no_of_isolated_nodes_removed'] == True:
        metric_list['no_of_isolated_nodes_removed'] = [0]
    tools.write_to_log_file(logfilepath, 'Got number of isolates removed.')
    if handling_variables['remove_subgraphs'] == True or metric_list['subnodes'] == True or metric_list['no_of_subnodes'] == True:
        tools.write_to_log_file(logfilepath, 'Need to change code in inital metric calcs to get subnodes. Currently assumes none.')
        metric_list['subnodes'] = [[]] #nodes removed as part of isolated graphs
        metric_list['no_of_subnodes'] = [0] #count of nodes removed as part of subgraphs
    tools.write_to_log_file(logfilepath, 'Got subgraph values')
    if metric_list['source_nodes'] == True and source_nodes_A != None:
        temp = []
        for val in source_nodes_A: temp.append(val)
        metric_list['source_nodes'] = [temp]
    else: metric_list['source_nodes'] = False
    tools.write_to_log_file(logfilepath, 'Source nodes values.')

    if metric_list['failed_no_con_to_a_source'] == True and source_nodes_A != None:
        metric_list['failed_no_con_to_a_source'] = [[]]
    else: metric_list['failed_no_con_to_a_source'] = False
    tools.write_to_log_file(logfilepath, 'Cons to source nodes.')

    temp = []
    if metric_list['avg_path_length'] == True:
        temp = average_path_length(G) # get list of average path length of each component
        if temp != []:
            metric_list['avg_path_length'] = [sum(temp)/len(temp)]
        else:
            # need to do something when an empty list is returned
            pass
    tools.write_to_log_file(logfilepath, 'Calcualted average path length.')

    if metric_list['avg_path_length_of_components']==True or metric_list['avg_path_length_of_giant_component']==True:
        if temp == []:
            temp = average_path_length(G) # get list of average path length of each component
        if metric_list['avg_path_length_of_components']== True:
            metric_list['avg_path_length_of_components']=[temp]
        if metric_list['avg_path_length_of_giant_component']==True:
            metric_list['avg_path_length_of_giant_component']=[temp[0]]
    tools.write_to_log_file(logfilepath, 'Calculated avg path length of components/giant components.')

    if metric_list['avg_geo_path_length']==True or metric_list['avg_geo_path_length_of_components']==True or metric_list['avg_geo_path_length_of_giant_component']==True:
        #need to check that the edges have an attribute 'length'

            for edge in G.edges(data=True):
                for edge in G.edges(data=True):
                    if len(list(edge[2].keys())) > 0:
                        for key in list(edge[2].keys()):
                            if key == str(length):
                                temp = []
                                temp = average_path_length(G,length) # get list of average path length of each component

                                if metric_list['avg_geo_path_length']==True:
                                    metric_list['avg_geo_path_length']=[sum(temp)/len(temp)]
                                if metric_list['avg_geo_path_length_of_components']==True:
                                    metric_list['avg_geo_path_length_of_components']=[temp]
                                if metric_list['avg_geo_path_length_of_giant_component']==True:
                                    metric_list['avg_geo_path_length_of_giant_component']=[temp[0]]
                                break

                    if metric_list['avg_geo_path_length']== True:
                        metric_list['avg_geo_path_length']=[None]
                    if metric_list['avg_geo_path_length_of_components']==True:
                        metric_list['avg_geo_path_length_of_components']=[None]
                    if metric_list['avg_geo_path_length_of_giant_component']==True:
                        metric_list['avg_geo_path_length_of_giant_component']=[None]
                    break
                break

    tools.write_to_log_file(logfilepath, 'Passed geo avg path lengths.')

    if metric_list['avg_degree']==True:
        avg=0.0
        for node in G:
            avg+=G.degree(node)
        metric_list['avg_degree']=[avg/nx.number_of_nodes(G)]
    tools.write_to_log_file(logfilepath, 'Average degree calculations done.')

    if metric_list['density']==True:
        metric_list['density']=[nx.density(G)]
    tools.write_to_log_file(logfilepath, 'Calculated density.')

    if metric_list['maximum_betweenness_centrality']==True or metric_list['avg_betweenness_centrality']==True:
        try:
            temp = nx.betweenness_centrality(G)
        except: 1411
        if metric_list['maximum_betweenness_centrality'] != False:
            metric_list['maximum_betweenness_centrality']=[max(temp.values())]
        if metric_list['avg_betweenness_centrality'] != False:
            avg=0.0
            for val in list(temp.values()):
                avg+=val
            metric_list['avg_betweenness_centrality']=[avg/len(temp)]
        if store_n_e_atts == True:
            for key in temp: G.node[key]['betweenness_centrality'] = temp[key]
    tools.write_to_log_file(logfilepath, 'Betweenness calcs done.')

    if metric_list['assortativity_coefficient']==True:
        metric_list['assortativity_coefficient']=[nx.degree_assortativity_coefficient(G)]
    tools.write_to_log_file(logfilepath, 'Assortativity coefficient done.')

    if metric_list['clustering_coefficient']==True:
        metric_list['clustering_coefficient']=[nx.average_clustering(G)]
        temp = nx.clustering(G)
        if store_n_e_atts == True:
            for key in temp: G.node[key]['clustering'] = temp[key]
    tools.write_to_log_file(logfilepath, 'Clustering calculated.')

    if metric_list['transitivity']==True:
        try:
            metric_list['transitivity']=[nx.transitivity(G)]
        except: return 1415
    tools.write_to_log_file(logfilepath, 'Transitivity calculated.')

    if metric_list['square_clustering']==True:
        try:
            temp = nx.square_clustering(G)
        except: return 1416
        avg=0.0
        for val in list(temp.values()):
            avg+=val
        metric_list['square_clustering']=[avg/len(temp)]
        if store_n_e_atts == True:
            for key in temp: G.node[key]['square_clustering'] = temp[key]
    tools.write_to_log_file(logfilepath, 'Square clustering calcualted.')

    if metric_list['avg_neighbor_degree']==True:
        try:
            temp = nx.average_neighbor_degree(G)
        except: 1417
        avg=0.0
        for val in list(temp.values()):
            avg+=val
        metric_list['avg_neighbor_degree']=[avg/len(temp)]
        if store_n_e_atts == True:
            for key in temp: G.node[key]['avg_neighbor_degree'] = temp[key]
    tools.write_to_log_file(logfilepath, 'Avg neighbor degree done.')

    if metric_list['avg_degree_connectivity']==True:
        try:
            temp = nx.average_degree_connectivity(G)
        except: return 1418
        metric_list['avg_degree_connectivity']=[list(temp.values())]
    if metric_list['avg_degree_centrality']==True:
        try:
            temp = nx.degree_centrality(G)
        except: return 1419
        avg=0.0
        for val in list(temp.values()):
            avg+=val
        metric_list['avg_degree_centrality']=[avg/len(temp)]
        if store_n_e_atts == True:
            for key in temp: G.node[key]['avg_degree_centrality'] = temp[key]
    if metric_list['avg_closeness_centrality']==True:
        try:
            temp = nx.closeness_centrality(G)
        except: return 1420
        avg=0.0
        for val in list(temp.values()):
            avg+=val
        metric_list['avg_closeness_centrality']=[avg/len(temp)]
        if store_n_e_atts == True:
            for key in temp: G.node[key]['avg_closeness_centrality'] = temp[key]
    if metric_list['diameter']==True:
        try:
            metric_list['diameter']=[nx.diameter(G)]
        except: return 1421
    tools.write_to_log_file(logfilepath, 'Finished doing initial metric calcs.')
    print('completed metric calcs')
    var = metric_list
    return var

def default_parameters(fileName, failure, basicA=None, optionA=None, basicB=None, optionB=None):
    #metrics
    if basicA != None: pass
    else: basicA = {'nodes_removed':True,'no_of_nodes_removed':True,'no_of_nodes':True,'no_of_edges':True,'no_of_components':True,'no_of_isolated_nodes':True,'isolated_nodes_removed':True,'nodes_selected_to_fail':True}
    if optionA != None: pass
    else: optionA = {'size_of_components':False,'giant_component_size':False,'avg_size_of_components':False,'isolated_nodes':False,'no_of_isolated_nodes_removed':False,'subnodes':False,'no_of_subnodes':False,'avg_path_length':False,'avg_path_length_of_components':False,'avg_path_length_of_giant_component':False,'avg_geo_path_length':False,'avg_geo_path_length_of_components':False,'avg_geo_path_length_of_giant_component':False,'avg_degree':False,'density':False,'maximum_betweenness_centrality':False,'avg_betweenness_centrality':False,'assortativity_coefficient':False,'clustering_coefficient':False,'transitivity':False,'square_clustering':False,'avg_neighbor_degree':False,'avg_degree_connectivity':False,'avg_degree_centrality':False,'avg_closeness_centrality':False,'diameter':False}
    if basicB != None: pass
    else: basicB = None
    if optionB != None: pass
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
    print('reached here')
    values,error = outputs.outputresults(graphparameters, parameters, metrics, logfilepath, multiterations)
    return values
