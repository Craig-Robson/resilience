# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 12:42:07 2014

@author: a8243587

Verson 1_4_0 - uses metric dicts rather than the metric lists

previuos version - outputs

"""

#custom modules
import error_classes, tools
import ogr,sys

def write_to_db(networks,a_to_b_edges,failure,db_parameters,i):
    '''Writes a copy of the network to the database along with any attributes 
    which have been calculated. Called at end of step function.
    Inputs: graphparamerers and parameters
    Returns:   True/False '''
    GA, GB, GtempA, GtempB = networks
    sys.path.append('C:/Users/Craig/GitRepo/nx_pgnet')
    sys.path.append('C:/a8243587_DATA/GitRepo/nx_pgnet')
    try:
        import nx_pgnet
    except:
        return 5201
    
    conn, net_name_a, net_name_b, save_a, save_b, srid_a, srid_b, spatial_a, spatial_b = db_parameters
    conn = ogr.Open(conn)
    if conn == None:
        return 5202
    
    if save_a:
        print('Writing out network(s)')
        #write network A
        if i == -99: return        
        GAWrite = GtempA.copy()
        net_name = net_name_a+'_'+str(i)
        if spatial_a:
            try:
                nx_pgnet.write(conn).pgnet(GAWrite,net_name,srid_a,overwrite=True,
                    directed=False,multigraph=False)
            except:
                print("Error caused by no nodes being left in the network 'a'")
                return 5205
        else:
            try:
                nx_pgnet.write(conn).pgnet(GAWrite,net_name,-1,overwrite=True,
                node_equality_key='id_')
            except:
                return 5207
            

    if save_b:    
        #write network B
        if i == -99: return  
        GBWrite = GtempB.copy()
        if spatial_b:
            try:
                nx_pgnet.write(conn).pgnet(GBWrite,(net_name_b+'_'+str(i)),srid_b,
                   overwrite=True)
            except:
                #add networkx error handler in here??
                print("Error caused by no nodes being left in the network 'b'")
                return 5206
        else:
            try:
                nx_pgnet.write(conn).pgnet(GBWrite,(net_name_b+'_'+str(i)),-1,
                   overwrite=True,node_equality_key='id_')
            except:
                return 5208
                
        if failure['dependency']: #dependency edge table
            try:
                table_name_old = 'inter_edges_at_t'
                table_name_new = 'inter_edges_at_t_%s'%(i)
                conn.ExecuteSQL("DROP TABLE IF EXISTS %s" %(table_name_old))
                conn.ExecuteSQL("CREATE TABLE %s (id INT PRIMARY KEY, netA_node INT, netB_node INT)" %(table_name_old)) 
                k = 0
                for edge in a_to_b_edges:
                     conn.ExecuteSQL("INSERT INTO inter_edges_at_t VALUES (%s,%s,%s)" %(k,edge[0],edge[1]))
                     k += 1
            except:
                return 5210
            try:
                rename_db_table(conn,table_name_old,table_name_new)
            except:
                return 5211
                
        elif failure['interdependency']:
            #write interdependency
            pass
    
    return True

def write_results_table(metrics,i,failure,db_parameters,k):
    '''
    At each time step writes the metrics calculated to a table in the database.
    If i=0 creates the table as well. At the end, renames the table.
    '''
    import ogr
    basicA,basicB,optionA,optionB,dependency,cascading = metrics
    conn, net_name_a, net_name_b, save_a, save_b, srid_a, srid_b, spatial_a, spatial_b = db_parameters
    defaultA = 'network_a'; defaultB = 'network_b'
    print('Writing results table(s)')

    conn = ogr.Open(conn)
    if conn == None:
        return 
        
    if i == 0: 
        var = create_db_res_table(conn,defaultA,optionA,dependency,cascading,'A')
        if type(var) == int:
            return var
        
        if not failure['stand_alone']:
            var = create_db_res_table(conn,defaultB,optionB,dependency,cascading,'B')
            if type(var) == int:
                return var+3 #this is so we know if network a or b
                
    if i != -100:
        #-----------------write basic metrics out------------------------------
        #can't figure out how to have dynamic name variable and allow text to be written out to table as well
        try:
            conn.ExecuteSQL("""INSERT INTO network_a VALUES (%s,%s,%s,%s,%s)""" 
                    %(i,basicA['no_of_nodes'][i],basicA['no_of_edges'][i],
                      basicA['no_of_components'][i],basicA['no_of_isolated_nodes'][i]))
            if basicA['nodes_removed'][i]==[]: conn.ExecuteSQL("""UPDATE network_a SET nodes_removed='{}' WHERE time_step=%s""" %(i))        
            else:            
                if len(basicA['nodes_removed'][i])==1:conn.ExecuteSQL("""UPDATE network_a SET nodes_removed=ARRAY %s WHERE time_step=%s""" %(str(basicA['nodes_removed'][i]),i))
                else:conn.ExecuteSQL("""UPDATE network_a SET nodes_removed=ARRAY%s WHERE time_step=%s""" %(basicA['nodes_removed'][i],i))
            if basicA['nodes_selected_to_fail'][i]==[]: conn.ExecuteSQL("""UPDATE network_a SET nodes_selected_to_fail='{}' WHERE time_step=%s""" %(i))        
            else:            
                if len(basicA['nodes_selected_to_fail'][i])==1:conn.ExecuteSQL("""UPDATE network_a SET nodes_selected_to_fail=ARRAY %s WHERE time_step=%s""" %(str(basicA['nodes_selected_to_fail'][i]),i))
                else:conn.ExecuteSQL("""UPDATE network_a SET nodes_selected_to_fail=%s WHERE time_step=%s""" %(basicA['nodes_selected_to_fail'][i],i))
        except:
            return 5255
        #-----------------write option metrics out-----------------------------
        try:
            for keys in optionA:
                if optionA[keys]!=False and optionA[keys]!=True:
                    try:
                        if keys=='subnodes'or keys=='isolated_nodes_removed' or keys=='isolated_nodes' or keys=='size_of_components' or keys=='avg_path_length_of_components' or keys=='avg_geo_path_length_of_components' or keys=='avg_degree_connectivity':
                            if optionA[keys][i]==[]:conn.ExecuteSQL("""UPDATE network_a SET %s='{}' WHERE time_step=%s""" %(keys,i))        
                            else:
                                if len(optionA[keys][i])==1:conn.ExecuteSQL("""UPDATE network_a SET %s=ARRAY %s WHERE time_step=%s""" %(keys,str(optionA[keys][i]),i))
                                else:conn.ExecuteSQL("""UPDATE network_a SET %s=ARRAY %s WHERE time_step=%s""" %(keys,optionA[keys][i],i))
                        elif optionA[keys][i]==[] or optionA[keys][i]==[[]]:
                            conn.ExecuteSQL("""UPDATE network_a SET %s='[]' WHERE time_step=%s""" %(keys,i))
                        elif optionA[keys][i]==None: conn.ExecuteSQL("""UPDATE network_a SET %s='ERROR' WHERE time_step=%s"""%(keys,i))
                        else: conn.ExecuteSQL("""UPDATE network_a SET %s=%s WHERE time_step=%s""" %(keys,optionA[keys][i],i))
                    except:
                        if keys=='subnodes':
                            subnd=[]
                            for item in optionA[keys][i]:
                                for nd in item: subnd.append(nd)
                            conn.ExecuteSQL("""UPDATE network_a SET %s= ARRAY %s WHERE time_step=%s""" %(keys,subnd,i))
                        else:
                            conn.ExecuteSQL("""UPDATE network_a SET %s='ERROR' WHERE time_step=%s""" %(keys,i))
                            print("Error occured when writing values to database for network 'a' where the key is '%s'" %(keys))
                            print(optionA[keys][i])
                            exit()
        except:
            return 5256

        if not failure['stand_alone']:
            #if dependency or interdependency
            #---------------write basic metrics out----------------------------
            try:
                conn.ExecuteSQL("""INSERT INTO network_b VALUES (%s,%s,%s,%s,%s)""" 
                    %(i,basicB['no_of_nodes'][i],basicB['no_of_edges'][i],
                      basicB['no_of_components'][i],basicB['no_of_isolated_nodes'][i]))
                try:
                    if basicB['nodes_removed'][i]==[]: conn.ExecuteSQL("""UPDATE network_b SET nodes_removed='{}' WHERE time_step=%s""" %(i))        
                    else: conn.ExecuteSQL("""UPDATE network_b SET nodes_removed= ARRAY %s WHERE time_step=%s""" %(basicB['nodes_removed'][i],i))
                except:
                    print("Error in basicB 'nodes_removed' when trying to write out results.")
                    exit()
            except:
                return 5257
            #---------------write option metrics out---------------------------
            for keys in optionB:
                try:
                    if optionB[keys]!=False and optionB[keys]!=True:
                        try:
                            if keys=='subnodes'or keys=='isolated_nodes_removed' or keys=='isolated_nodes' or keys=='size_of_components' or keys=='avg_path_length_of_components' or keys=='avg_geo_path_length_of_components' or keys=='avg_degree_connectivity':
                                if optionB[keys][i]==[]:conn.ExecuteSQL("""UPDATE network_b SET %s='{}' WHERE time_step=%s""" %(keys,i))
                                elif len(optionB[keys][i])==1:conn.ExecuteSQL("""UPDATE network_b SET %s=ARRAY %s WHERE time_step=%s""" %(keys,str(optionB[keys][i]),i))
                                else:conn.ExecuteSQL("""UPDATE network_b SET %s=ARRAY %s WHERE time_step=%s""" %(keys,optionB[keys][i],i))
                            elif optionB[keys][i]==[] or optionB[keys][i]==[[]]:conn.ExecuteSQL("""UPDATE network_b SET %s='[]' WHERE time_step=%s""" %(keys,i))
                            elif optionB[keys][i]==None: conn.ExecuteSQL("""UPDATE network_a SET %s='ERROR' WHERE time_step=%s"""%(keys,i))
                            else: conn.ExecuteSQL("""UPDATE network_b SET %s=%s WHERE time_step=%s""" %(keys,optionB[keys][i],i))
                        except:
                            if keys=='subnodes':
                                subnd=[]
                                for item in optionB[keys][i]:
                                    for nd in item: subnd.append(nd)
                                conn.ExecuteSQL("""UPDATE network_b SET %s= ARRAY %s WHERE time_step=%s""" %(keys,subnd,i))
                            else:
                                conn.ExecuteSQL("""UPDATE network_b SET %s='ERROR' WHERE time_step=%s""" %(keys,i))
                                print("Error occured when writing values to database for network 'b' where the key is '%s'" %(keys))
                except:
                    return 5258
                    
            # write out dependency metrics
            for keys in list(dependency.keys()):
                
                if dependency[keys]!=False:
                    try:
                        if keys=='no_of_nodes_removed_from_A':
                            conn.ExecuteSQL("""UPDATE network_a SET %s=%s WHERE time_step=%s""" %(keys,dependency[keys][i],i))
                        elif keys=='nodes_removed_from_A':
                            if dependency[keys][i]==[]:
                                conn.ExecuteSQL("""UPDATE network_a SET %s='{}' WHERE time_step=%s""" %(keys,i))
                            else:conn.ExecuteSQL("""UPDATE network_a SET %s= ARRAY %s WHERE time_step=%s""" %(keys,dependency[keys][i],i))
                        elif keys=='no_of_nodes_removed_from_B':
                            conn.ExecuteSQL("""UPDATE network_b SET %s=%s WHERE time_step=%s""" %(keys,dependency[keys][i],i))
                        elif keys=='nodes_removed_from_B':
                            if dependency[keys][i]==[]:
                                conn.ExecuteSQL("""UPDATE network_b SET %s='{}' WHERE time_step=%s""" %(keys,i))
                            else:conn.ExecuteSQL("""UPDATE network_b SET %s= ARRAY %s WHERE time_step=%s""" %(keys,dependency[keys][i],i))          
                    except:
                        return 5259
            if failure['interdependency']==True:
                pass                
            
    if k==-99:
        #if last iteration rename tables to something more specific
        var = rename_db_table(conn,defaultA,table_name_new='results_'+net_name_a)
        if type(var) == int:
            return var
        if not failure['stand_alone']:
            var = rename_db_table(conn,defaultB,table_name_new='results_'+net_name_b)
            if type(var) == int:
                return var
    return True

def create_db_res_table(conn,table_name,option,dependency,cascading,net):
    '''
    '''
    try:
        conn.ExecuteSQL("DROP TABLE IF EXISTS %s" %(table_name))
        conn.ExecuteSQL("CREATE TABLE %s (time_step INT PRIMARY KEY,"
                    "no_of_nodes INT, no_of_edges INT, no_of_comp INT,"
                    "no_of_isolated_nodes INT, nodes_removed INT ARRAY,"
                    "nodes_selected_to_fail INT ARRAY, isolated_nodes_removed INT ARRAY)" %(table_name))
    except:
        return 5241
    
    try:
        for keys in option:
            if option[keys]==False: pass
            elif option[keys]=='subnodes':conn.ExecuteSQL("ALTER TABLE %s ADD COLUMN %s INT ARRAY" %(table_name,keys))
            else:conn.ExecuteSQL("ALTER TABLE %s ADD COLUMN %s varchar" %(table_name,keys))
    except:
        return 5242
                
    try:
        for keys in dependency:
            #this will write out no matter A or B - need to sort so it does not do this
            if dependency[keys]==False: pass
            else:
                if net=='A':
                    if keys=='nodes_removed_from_A' or keys=='no_of_nodes_removed_from_A':
                        conn.ExecuteSQL("ALTER TABLE %s ADD COLUMN %s varchar" %(table_name,keys))
                elif net=='B':
                    if keys=='nodes_removed_from_B' or keys=='no_of_nodes_removed_from_B':
                        conn.ExecuteSQL("ALTER TABLE %s ADD COLUMN %s varchar" %(table_name,keys))
    except:
        return 5243
        
    if cascading != None:
        for keys in cascading:
            if cascading[keys]==False: pass
            else:conn.ExecuteSQL("ALTER TABLE %s ADD COLUMN %s varchar" %(table_name,keys))
                
    return True

def rename_db_table(conn,table_name_old,table_name_new):
    '''
    Rename the table and delete the old version.
    '''
    conn.ExecuteSQL("DROP TABLE IF EXISTS %s;" %(table_name_new))
    conn.ExecuteSQL("ALTER TABLE %s RENAME TO %s;" %(table_name_old,table_name_new))
    return

def outputresults(graphparameters, parameters,metrics,logfilepath=None,multiiterations=False):
    '''Controls how the results are output.
    Inputs: graphparametes and parameters containers
    Returns: all sets of metrics in a single container '''
    error = None
    #unpacking the variables
    networks,i,node_list,to_b_nodes,from_a_nodes,source_nodes_A,source_nodes_B = graphparameters
    failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length = parameters
    basicA,basicB,optionA,optionB,dependency,cascading=metrics
    #if more than one simualtion has been run over the same network
    if multiiterations == True:
        #send to the method for calculating the averages and writing the results out
        basicA, basicB, optionA, optionB, error = average_txtresults(graphparameters, parameters,error)
        #if an error occurs
        if error != None:
            raise error_classes.CalculationError('Error. Error in calculating the averages for the output.')
    else:
        try:
            #open output file
            outputfile = open(fileName,'a')
        except:
            tools.write_to_log_file(logfilepath,'Failed to open output file.')
            return 5001
            #raise error_classes.WriteError('Error. Could not open text file to write results to. File attempted was: %s' %(fileName))
        #send to the textout function to write the results out
        var = txtout(outputfile,graphparameters, parameters,metrics)
        if type(var) == int:
            tools.write_to_log_file(logfilepath, 'Error code %s returned when attempting to write results to text file.' %(var))
            return var

    #pack the metric values together again
    var = basicA, basicB, optionA, optionB, dependency,cascading
    return var
    
def average_txtresults(graphparameters, parameters,error):
    '''Reads a txt file with results in and produces an average set and writes 
    back to the same text file. Appends the averages to the end of the file.'''
    #unpack the graphparameters and parameters
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges = parameters
    networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics = graphparameters
    #open file which contains all the results form the simulations
    fread = open(fileName, 'r')
    #list of metrics - these are then added to a list for network A and B
    line_index = ['took this many steps','nodes removed','count removed nodes',
                  'number of nodes left','number of edges','number of components',
                  'isolated nodes count','size of each component',
                  'number of ndoes in giant component',
                  'average size of components','isolated nodes',
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
        #unused????
        elif line.startswith('The analysis') or line.startswith('Start size'):
            pass
        else:
            i = 0
            #loop through the list of metric names
            while i < len(line_index):
                #G,dlist,removed_nodes,node -not sure why these are here
                #check if the line starts with the meric name in the list at position i
                if line.startswith(line_index[i]):
                    #if found, split the line
                    try:
                        a,b = line.split(',[')
                    except:
                        #if can't split the line, there must be an error in the text file
                        raise error_classes.CalculationError('Error. Could not read the values in the results file successfuly to calculate the averages.')
                        error = 0o045
                        return basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B,error
                    #once split, edit the string to make it readable
                    b = b.replace('[','');b=b.replace(']','')
                    if line_index[i] == 'nodes removed':
                        b = b.split(';')
                    else:                        
                        b = b.split(',')
                    #loop through the items, adding them to the 'temp' list
                    temp = []
                    for items in b:
                        items = items.strip()
                        if items != "['\n']" and len(items) > 0:
                            try:
                                temp.append(float(items))
                            except:
                                #if cant convert to a float, exit.
                                raise error_classes.CalculationError('Error. Could not convert what should be a numerical value to a float when calcautig the average of the results.')
                    #if more than one value read
                    if len(temp) != 0:
                        #find out for which network the result is for and append to the respective list
                        if network_is == 'A':
                            temp_metrics_A[i].append(temp)
                        elif network_is == 'B':
                            dependency = True
                            temp_metrics_B[i].append(temp)
                        else:
                            raise error_classes.OutputError('Error. The network the values are assoicated with was not found when calcualting the averages for the output.')
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
            raise error_classes.OutputError('Error. Major error in average results.')
        
        #go through each of the metrics in the list
        metriclist = []
        while y < len(temp_metrics):
            temp_metric = temp_metrics[y]
            #find the length of the longest list for the metric
            if len(temp_metric) != 0:
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
        if i < 7:
            basic_metrics_A.append(metriclist_A[i])
            if dependency == True: basic_metrics_B.append(metriclist_B[i])
        #for all other metics, add to the optional lists
        elif i > 6 and i < len(line_index):
            option_metrics_A.append(metriclist_A[i])
            if dependency == True: option_metrics_B.append(metriclist_B[i])
        i += 1
  
    return basic_metrics_A,basic_metrics_B,option_metrics_A,option_metrics_B,error
    
def results(basic_metrics_A, basic_metrics_B,STAND_ALONE): #print out and write out the results
    '''Prints some results to the console.
    Inputs: basic metrics set for network A and B
    Returns: Nothing '''
    nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A = basic_metrics_A
    nodes_removed_B,node_count_removed_B,count_nodes_left_B,number_of_edges_B,number_of_components_B = basic_metrics_B
    print('NETWORK A')    
    print('nodes_removed_A: ', nodes_removed_A)
    print('number_of_edges_A: ', number_of_edges_A)
    print('node_count_removed_A: ', node_count_removed_A)
    print('count_nodes_left_A: ', count_nodes_left_A)
    print('number_of_components_A: ', number_of_components_A)
    if STAND_ALONE == False:  
        print('NETWORK B')    
        print('nodes_removed_B: ', nodes_removed_B)
        print('number_of_edges_B: ', number_of_edges_B)    
        print('node_count_removed_B: ', node_count_removed_B)
        print('count_nodes_left_B: ', count_nodes_left_B)
        print('number_of_components_B: ', number_of_components_B) 

def write_text_file(outputfile,CASCADING,basic,option):
    '''Writes the metrics to the text file.
    Inputs: file operand, CASCADING variable, basic_metrics set and option_metrics set
    Returns: Nothing'''
    #unpack the variables
    
    #write the basic metrics to the text file
    try:
        outputfile.write('\nnodes removed,' + str(tools.replace_all(str(basic['nodes_removed']), {',':';','];':'],'})))
        outputfile.write('\nnumber of nodes removed,' + str(basic['no_of_nodes_removed']))
        outputfile.write('\nnumber of nodes left,' + str(basic['no_of_nodes']))   
        outputfile.write('\nnumber of edges,' + str(basic['no_of_edges']))
        outputfile.write('\nnumber of components,' + str(basic['no_of_components']))
        outputfile.write('\nnumber of isolates,' + str(str(basic['no_of_isolated_nodes'])))
        outputfile.write('\nisolated nodes removed,' + str(tools.replace_all(str(basic['isolated_nodes_removed']), {',':';','];':'],'})))
    except:
        return 5031
    
    #need to do below as not needed for basic B    
    try:    
        if basic['nodes_selected_to_fail']!=False:outputfile.write('\nnodes selected to fail,' + str(basic['nodes_selected_to_fail']))
    except:
        return 5032
        
    #write the optional metrics to the rext file - if not set as False
    try:
        if option['size_of_components'] != False:
            outputfile.write('\nsize of each component,' + str(tools.replace_all(str(option['size_of_components']),{',':';','];':'],'})))
        if option['giant_component_size'] != False:
            outputfile.write('\nnumber of nodes in giant component,' + str(option['giant_component_size']))
        if option['avg_size_of_components'] != False:
            outputfile.write('\naverage size of components,' + str(option['avg_size_of_components']))
        if option['isolated_nodes'] != False:
            outputfile.write('\nisolated nodes,' + str(tools.replace_all(str(option['isolated_nodes']), {',':';','];':'],'})))
        if option['no_of_isolated_nodes_removed'] != False:
            outputfile.write('\nnumber of isolated nodes removed,' + str(option['no_of_isolated_nodes_removed']))
        if option['subnodes'] != False:
            outputfile.write('\nsubgraph nodes,' + str(tools.replace_all(str(tools.replace_all(str(option['subnodes']) , {',':';',']];':']],'})),{'[];':'[],'})))
        if option['no_of_subnodes'] != False:
            outputfile.write('\nnumber of subnodes,' + str(option['no_of_subnodes']))  
        if option['source_nodes'] != False:
            outputfile.write('\nsource nodes,' + str(option['source_nodes']))
        if option['failed_no_con_to_a_source'] != False:
            outputfile.write('\nfailed as no connection to a source,' + str(option['failed_no_con_to_a_source']))
        if option['avg_path_length'] != False:
            outputfile.write('\naverage path length for whole graph,' + str(option['avg_path_length']))
        if option['avg_path_length_of_components'] != False:
            outputfile.write('\naverage path length for each component,' + str(tools.replace_all(str(option['avg_path_length_of_components']),{',':';','];':'],'})))
        if option['avg_path_length_of_giant_component'] != False:
            outputfile.write('\naverage path length of giant component,' + str(option['avg_path_length_of_giant_component']))
        if option['avg_geo_path_length']!=False:
            outputfile.write('\naverage geographic path length for whole graph,' + str(option['avg_geo_path_length']))
        if option['avg_geo_path_length_of_components']!=False:
             outputfile.write('\naverage geographic path length for each component,' + str(tools.replace_all(str(option['avg_geo_path_length_of_components']),{',':';','];':'],'})))
        if option['avg_geo_path_length_of_giant_component']!=False:
            outputfile.write('\naverage geographic path length of giant component,' + str(option['avg_geo_path_length_of_giant_component']))
        if option['avg_degree'] != False:
            outputfile.write('\naverage degree,' + str(option['avg_degree']))
        if option['density']!=False:
            outputfile.write('\ndensity,' + str(option['density']))
        if option['maximum_betweenness_centrality']!=False:
            outputfile.write('\nmaximum betweenness centrality,' + str(option['maximum_betweenness_centrality']))
        if option['avg_betweenness_centrality']!=False:
            outputfile.write('\naverage betweenness centrality of nodes,' + str(option['avg_betweenness_centrality']))
        if option['assortativity_coefficient']!=False:
            outputfile.write('\nassortativity coefficient,' + str(option['assortativity_coefficient']))
        if option['clustering_coefficient']!=False:
            outputfile.write('\nclustering coefficient,' + str(option['clustering_coefficient']))
        if option['transitivity']!=False:
            outputfile.write('\ntransitivity,' + str(option['transitivity']))
        if option['square_clustering']!=False:
            outputfile.write('\nsquare clustering,' + str(option['square_clustering']))
        if option['avg_neighbor_degree']!=False:
            outputfile.write('\naverage neighbor degree,' + str(option['avg_neighbor_degree']))
        if option['avg_degree_connectivity']!=False:
            outputfile.write('\naverage degree connectivity,' + str(option['avg_degree_connectivity']))
        if option['avg_degree_centrality']!=False:
            outputfile.write('\naverage degree centrality,' + str(option['avg_degree_centrality']))
        if option['avg_closeness_centrality']!=False:
            outputfile.write('\naverage closeness centrality,' + str(option['avg_closeness_centrality']))
        if option['diameter']!=False:
            outputfile.write('\ndiameter,' + str(option['diameter']))
    except:
        return 5033
        
    return True
    
def txtout(outputfile,graphparameters, parameters,metrics):        
    '''Writes the results to a specified text file.
    Inputs: the file operand, the graphparameters (metrics etc) and the parameters
    Returns: Nothing'''
    #unpack the variables
    failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length=parameters    
    networks,i,node_list,to_b_nodes,from_a_nodes,source_nodes_A,source_nodes_B = graphparameters 
    GA, GB, GtempA, GtempB = networks
    basicA,basicB,optionA,optionB,dependency,cascading=metrics

    #write the parameters for the analysis out
    try:
        outputfile.write('\nThe analysis parameters were:')    
        if failure['single'] == True: outputfile.write('SINGLE = True, ')
        elif failure['sequential'] == True: outputfile.write('Sequential = True, ')
        elif failure['cascading'] == True: outputfile.write('Cascading = True, ') 
        else: outputfile.write('Error!')
        
        if failure['random'] == True: outputfile.write('RANDOM = True')
        elif failure['degree'] == True: outputfile.write('DEGREE = True')
        elif failure['betweenness'] == True: outputfile.write('BETWEENNESS = True')
        else: outputfile.write('Error!')    
        #write the options used out
        if handling_variables['remove_subgraphs'] == True: outputfile.write(', REMOVE_SUBGRAPHS = True')
        if handling_variables['remove_isolates'] == True: outputfile.write(', REMOVE_ISOLATES = True')
        if handling_variables['no_isolates'] == True: outputfile.write(', NO_ISOLATES = True')
    except:
        return 5010
        
    #write out the first few lines for network A
    outputfile.write('\nNETWORK A')
    outputfile.write('\nTook this manny steps: '+ str(len(basicA['no_of_nodes'])-1))
    #use the function to write the metric results out for the network A
    print("Writing results to file (%s)" %outputfile)
    var = write_text_file(outputfile,failure['cascading'],basicA,optionA)     

    if type(var) == int:
        return var        
        
    #write the results for the metrics for network B using the function
    if failure['dependency'] == True or failure['interdependency'] == True:
        try:
            if failure['interdependency']:
                outputfile.write('\nno of nodes removed due to dependency failure,' + str(dependency['no_of_nodes_removed_from_A']))
                outputfile.write('\nnodes removed due to dependency failure,' + str(tools.replace_all(str(dependency['nodes_removed_from_A']), {',':';','];':'],'})))
            outputfile.write('\nNETWORK B')
            write_text_file(outputfile,failure['cascading'],basicB,optionB)
            outputfile.write('\nno of nodes removed due to dependency failure,' + str(dependency['no_of_nodes_removed_from_B']))
            outputfile.write('\nnodes removed due to dependency failure,' + str(tools.replace_all(str(dependency['nodes_removed_from_B']), {',':';','];':'],'})))
        except:
            return 5011
    
    return True