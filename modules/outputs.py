# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 12:42:07 2014

@author: a8243587

Verson 1_4_0 - uses metric dicts rather than the metric lists

previuos version - outputs

"""

#custom modules
import error_classes
import tools

def write_to_db(networks,a_to_b_edges,failure,db_parameters,i):
    '''Writes a copy of the network to the database along with any attributes 
    which have been calculated. Called at end of step function.
    Inputs: graphparamerers and parameters
    Returns:   True/False '''
    GA, GB, GtempA, GtempB = networks
          
    import sys, ogr
    sys.path.append('C:/Users/Craig/GitRepo/nx_pgnet')
    import nx_pgnet
    conn, conn2, net_name_a, net_name_b, save_a, save_b = db_parameters
    conn = ogr.Open(conn)
    
    if save_a:
        print 'Writing out network(s)'
        #write network A
        if i == -99: return        
        GAWrite = GtempA.copy()
        net_name = net_name_a+'_'+str(i)
        
        nx_pgnet.write(conn).pgnet(GAWrite,net_name,27700,overwrite=True,
                directed=False,multigraph=False)

        #nx_pgnet.write(conn).pgnet(GAWrite,net_name,-1,overwrite=True,node_equality_key='id_')

    if save_b:    
        #write network B
        if i == -99: return  
        GBWrite = GtempB.copy()
        nx_pgnet.write(conn).pgnet(GBWrite,(net_name_b+'_'+str(i)),27700,overwrite=True)
        #nx_pgnet.write(conn).pgnet(GBWrite,(net_name_b+'_'+str(i)),-1,overwrite=True,node_equality_key='id_')
        if failure['dependency']:
            #convert to use exisitng connection rather than the once created by psycopg2
            #allSQL='SELECT * FROM "Inter_Lines"'
            #for row in conn.ExecuteSQL(allSQL):a_to_b_edges.append([row.p,row.t])
            #sql to create a table in the db for this time step
            import psycopg2
            con = psycopg2.connect(database=conn2['dbname'],user=conn2['user'],password=conn2['password'],port=conn2['port'])
            cur = con.cursor()
            table_name_old = 'inter_edges_at_t'
            table_name_new = 'Inter_edges_at_t_%s'%(i)
            cur.execute("DROP TABLE IF EXISTS %s" %(table_name_old))
            cur.execute("CREATE TABLE %s (id INT PRIMARY KEY, netA_node INT, netB_node INT)" %(table_name_old))
            con.commit()
            
            k = 0
            for edge in a_to_b_edges:
                 cur.execute("""INSERT INTO inter_edges_at_t VALUES (%s,%s,%s)""",
                    (k,edge[0],edge[1]))
                 k += 1
            
            con.commit()
            rename_db_table(conn2,table_name_old,table_name_new)
            
        elif failure['interdependency']:
            #write interdependency
            pass
    return

def write_results_table(basicA,optionA,basicB,optionB,i,STAND_ALONE,db_parameters):
    conn, conn2, net_name_a, net_name_b, save_a, save_b = db_parameters
    defaultA = 'network_a'; defaultB = 'network_b'
    
    if i == 0: 
        create_db_res_table(conn2,defaultA,optionA)
        if not STAND_ALONE: create_db_res_table(conn2,defaultB,optionB)
    if i <> -99:
        import psycopg2
        con = psycopg2.connect(database=conn2['dbname'],user=conn2['user'],password=conn2['password'],port=conn2['port'])
        cur = con.cursor()
        #-----------------write basic metrics out------------------------------
        #can't figure out how to have dynamic name variable and allow text to be written out to table as well
        cur.execute("""INSERT INTO network_a VALUES (%s,%s,%s,%s,%s,%s)""",
                    (i,basicA['no_of_nodes'][i],basicA['number_of_edges'][i],
                     basicA['number_of_components'][i],basicA['no_of_isolated_nodes'][i],basicA['nodes_removed'][i]))
        con.commit()
        #-----------------write option metrics out-----------------------------
        for keys in optionA:
            if optionA[keys]<>False and optionA[keys]<>True:
                if keys=='isolated_nodes_removed':
                    cur.execute("""UPDATE network_a SET isolated_nodes_removed='None' WHERE time_step=%s""" %(i))
                elif keys=='isolated_nodes':
                    cur.execute("""UPDATE network_a SET isolated_nodes='None' WHERE time_step=%s""" %(i))
                elif keys=='subnodes':
                    cur.execute("""UPDATE network_a SET subnodes='None' WHERE time_step=%s""" %(i))
                elif optionA[keys][i]==None:
                    cur.execute("""UPDATE network_a SET %s='None' WHERE time_step=%s"""%(keys,i))
                else:
                    cur.execute("""UPDATE network_a SET %s=%s WHERE time_step=%s""" %(keys,optionA[keys][i],i))
            con.commit()

        if not STAND_ALONE:
            #if dependency or interdependency
            #---------------write basic metrics out----------------------------
            cur.execute("""INSERT INTO network_b VALUES (%s,%s,%s,%s,%s,%s)""", 
                    (i,basicB['no_of_nodes'][i],basicB['number_of_edges'][i],
                     basicB['number_of_components'][i],basicB['no_of_isolated_nodes'][i],basicB['nodes_removed'][i]))
            con.commit()
            
            #---------------write option metrics out---------------------------
            for keys in optionB:
                if optionB[keys]<>False and optionB[keys]<>True:
                    if keys=='isolated_nodes_removed':
                        cur.execute("""UPDATE network_b SET isolated_nodes_removed='None' WHERE time_step=%s""" %(i))
                    elif keys=='isolated_nodes':
                        cur.execute("""UPDATE network_b SET isolated_nodes='None' WHERE time_step=%s""" %(i))
                    elif keys=='subnodes':
                        cur.execute("""UPDATE network_b SET subnodes='None' WHERE time_step=%s""" %(i))
                    elif optionB[keys][i]==None:
                        print 'the key this time is:', keys
                        cur.execute("""UPDATE network_a SET %s='None' WHERE time_step=%s"""%(keys,i))
                    else:
                        cur.execute("""UPDATE network_b SET %s=%s WHERE time_step=%s""" %(keys,optionB[keys][i],i))
                    con.commit()
        cur.close();con.close() 
    else:
        #if last iteration rename tabkes to something more specific
        rename_db_table(conn2,defaultA,table_name_new='results_'+net_name_a)
        if not STAND_ALONE:
            rename_db_table(conn2,defaultB,table_name_new='results_'+net_name_b)
    return

def create_db_res_table(con,table_name,option):
    import psycopg2
    con = psycopg2.connect(database=con['dbname'],user=con['user'],password=con['password'],port=con['port'])
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS %s" %(table_name))
    cur.execute("CREATE TABLE %s (time_step INT PRIMARY KEY, No_of_Nodes INT, No_of_Edges INT, No_of_Comp INT, No_of_Isolated_Nodes INT, nodes_removed varchar)" %(table_name))
    con.commit()
    for keys in option:
        cur.execute("ALTER TABLE %s ADD COLUMN %s varchar" %(table_name,keys))
    con.commit()
    cur.close();con.close()
    return

def rename_db_table(con,table_name_old,table_name_new):
    import psycopg2
    con = psycopg2.connect(database=con['dbname'],user=con['user'],password=con['password'],port=con['port'])
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS %s;" %(table_name_new))
    cur.execute("ALTER TABLE %s RENAME TO %s;" %(table_name_old,table_name_new))
    con.commit();cur.close();con.close()
    return

def outputresults(graphparameters, parameters,metrics,logfilepath=None,multiiterations=False):
    '''Controls how the results are output.
    Inputs: graphparametes and parameters containers
    Returns: all sets of metrics in a single container '''
    error = None
    #unpacking the variables
    networks,i,node_list,to_b_nodes,from_a_nodes = graphparameters
    failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length = parameters
    basicA,basicB,optionA,optionB,interdependency,cascading=metrics
    #if more than one simualtion has been run over the same network
    if multiiterations == True:
        #send to the method for calculating the averages and writing the results out
        basicA, basicB, optionA, optionB, error = average_txtresults(graphparameters, parameters,error)
        #if an error occurs
        if error <> None:
            raise error_classes.CalculationError('Error. Error in calculating the averages for the output.')
    else:
        try:
            #open output file
            outputfile = open(fileName,'a')
        except:
            raise error_classes.WriteError('Error. Could not open text file to write results to. File attempted was: %s' %(fileName))
        #send to the textout function to write the results out
        txtout(outputfile,graphparameters, parameters)
    #pack the metric values together again
    values = basicA, basicB, optionA, optionB  
    return values,error       
    
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
                        error = 0045
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
                        if items <> "['\n']" and len(items) > 0:
                            try:
                                temp.append(float(items))
                            except:
                                #if cant convert to a float, exit.
                                raise error_classes.CalculationError('Error. Could not convert what should be a numerical value to a float when calcautig the average of the results.')
                    #if more than one value read
                    if len(temp) <> 0:
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
        if i < 7:
            basic_metrics_A.append(metriclist_A[i])
            if dependency == True: basic_metrics_B.append(metriclist_B[i])
        #for all other metics, add to the optional lists
        elif i > 6 and i < len(line_index):
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
    nodes_removed,node_count_removed,count_nodes_left,number_of_edges,number_of_components,isolated_n_count = basic_metrics
    size_of_components,giant_component_size,av_nodes_in_components,isolated_nodes,isolated_n_count_removed,subnodes,subnodes_count,path_length,av_path_length_components,giant_component_av_path_length,av_path_length_geo,average_degree,inter_removed_count = option_metrics

    #write the basic metrics to the text file - if not set as False
    if nodes_removed <> False:
        outputfile.write('\nnodes removed,' + str(tools.replace_all(str(nodes_removed), {',':';','];':'],'})))
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
        outputfile.write('\nsize of each component,' + str(tools.replace_all(str(size_of_components),{',':';','];':'],'})))
    if giant_component_size <> False:
        outputfile.write('\nnumber of nodes in giant component,' + str(giant_component_size))
    if av_nodes_in_components <> False:
        outputfile.write('\naverage size of components,' + str(av_nodes_in_components))
    if isolated_nodes <> False:
        outputfile.write('\nisolated nodes,' + str(tools.replace_all(str(isolated_nodes), {',':';','];':'],'})))
    if isolated_n_count <> False:
        outputfile.write('\nisolated node count,' + str(str(isolated_n_count)))
    if isolated_n_count_removed <> False:
        outputfile.write('\nisolated node count,' + str(isolated_n_count_removed))
    if subnodes <> False:
        outputfile.write('\nsubnodes,' + str(tools.replace_all(str(tools.replace_all(str(subnodes) , {',':';',']];':']],'})),{'[];':','})))
    if subnodes_count <> False:
        outputfile.write('\nsubnodes count,' + str(subnodes_count))  
    if path_length <> False:
        outputfile.write('\naverage path length for whole graph,' + str(path_length))        
    if av_path_length_components <> False:
        outputfile.write('\naverage path length for each component,' + str(tools.replace_all(str(av_path_length_components),{',':';','];':'],'})))
    if giant_component_av_path_length <> False:
        outputfile.write('\naverage path length of giant component,' + str(giant_component_av_path_length))
    if average_degree <> False:
        outputfile.write('\naverage degree,' + str(average_degree))
    
def txtout(outputfile,graphparameters, parameters):        
    '''Writes the results to a specified text file.
    Inputs: the file operand, the graphparameters (metrics etc) and the parameters
    Returns: Nothing'''
    #unpack the variables
    metrics, STAND_ALONE, DEPENDENCY, INTERDEPENDENCY, SINGLE, SEQUENTIAL, CASCADING, RANDOM, DEGREE, BETWEENNESS, REMOVE_SUBGRAPHS, REMOVE_ISOLATES, NO_ISOLATES, fileName,a_to_b_edges = parameters    
    networks,i,node_list,to_b_nodes, from_a_nodes, basic_metrics_A,basic_metrics_B,option_metrics_A, option_metrics_B,interdependency_metrics,cascading_metrics = graphparameters    
    GA, GB, GtempA, GtempB = networks
    nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A,isolated_n_count_A = basic_metrics_A     
    size_of_components_A,giant_component_size_A,av_nodes_in_components_A,isolated_nodes_A,isolated_n_count_removed_A,subnodes_A,subnodes_count_A,path_length_A,av_path_length_components_A,giant_component_av_path_length_A,av_path_length_geo_A,average_degree_A,inter_removed_count_A = option_metrics_A
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
    