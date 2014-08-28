"""
********
Version 1_4_0 - replaces the lists of metrics with dicts - integrates with 
v5_4_0 of main resilince module.

Version 1_4_1 - replaces the parameter list with dicts - integrates with 
v5_4_1 of main resilince module.

Last good version - run_ia_analysis or run_inter_analysis
********
"""
#import networkx
import networkx as nx
import sys, ogr

#specify location of module and import
sys.path.append('C:/Users/Craig/GitRepo/nx_pgnet')
sys.path.append("C:/a8243587_DATA/GitRepo/nx_pgnet")
sys.path.append("C:/a8243587_DATA/resilience_module")
import interdependency_analysis_v5_4_3 as ia
import nx_pgnet, tools

#create a network using networkx - can use any of the networkx generators or 
#node and edge lists
host = 'localhost';user = 'postgres';password = 'aaSD2011';port = '5433'
dbname = 'london_sq_rdom_run5'
net_name_a = 'power_lines'; net_name_b = 'tube_lines'
conn = ogr.Open("PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port))

G = nx_pgnet.read(conn).pgnet(net_name_a)
for nd in G.nodes(data=True):
    G.node[nd[0]].pop('id')
#G = nx.Graph()
#edges=(1,2),(1,3),(2,3),(2,5),(3,4),(4,5)
#G.add_edges_from(edges)
#G = tools.add_node_field(G,field_name='id_')
    
#create a second, make = to none if to be ignored
GB = nx_pgnet.read(conn).pgnet(net_name_b)
for nd in GB.nodes(data=True):
    GB.node[nd[0]].pop('id')
#GB=nx.Graph()
#edges=(1,5),(1,2),(1,3),(2,3),(2,4),(3,4),(3,6),(4,6),(5,6)
#GB.add_edges_from(edges)
#GB = tools.add_node_field(GB,field_name='id_')

#dependency links(edges);needed if dependency or interdependency are True
#a_to_b_edges = [(2,1),(5,5),(5,6)]
a_to_b_edges=[]
allSQL='SELECT * FROM "Inter_Lines"'
for row in conn.ExecuteSQL(allSQL):a_to_b_edges.append([row.p,row.t])

'''
Need to check what happens with different combinations of dependency links.
Should be ok as it stands for dealing with london tube-power work.
'''
#interdependency links(edges);needed if interdependency is True
b_to_a_edges = []  #not used yet

#specifiy the location and name of output file
fileName = 'file location/file name.txt'

#sepcify the location and name for a log file, or make = to None if not wanted
logfilepath = None

#to save the metrics at end of each time step to db
write_results_table=True 
store_n_e_atts=True

#to save network(s) at each time step to the database
write_step_to_db = True
 
#parameters for above
save_a = True; save_b = True
#net_name_a = 'power_lines'; net_name_b = 'tube_lines'
#host = 'localhost'; user = 'postgres'
#password = 'aaSD2011'; port = '5433'
#dbname = 'london_seq_dgree'
srid_a=27700; srid_b=27700; spatial_a=True; spatial_b=True

#field name for geographic path length calculations
length = 'length'

#stand_alone, dependency, interdependency
failure = {'stand_alone':False, 'dependency':True, 'interdependency':False,
        'single':False, 'sequential':True, 'cascading':False,
        'random':True, 'degree':False, 'betweenness':False,'from_list':False}

#varaibles on how sub-graphs and isolated nodes are handled
handling_variables = {'remove_subgraphs':False,'remove_isolates':True,'no_isolates':False}

#basic metrics are: nodes_removed_A,node_count_removed_A,count_nodes_left_A,number_of_edges_A,number_of_components_A, isolated_n_count_A
basic_A = {'nodes_removed':True,'nodes_selected_to_fail':True,'no_of_nodes':True,
           'number_of_edges':True,'number_of_components':True,'no_of_isolated_nodes':True}
basic_B = basic_A.copy()

#need to make isolated_nodes_A/B true when doing, also inter_removed_count_A/B
option_A = {'giant_component_size':     True,
            'avg_nodes_in_components':  True,
            'avg_degree':               True,
            'isolated_nodes':           True,
            'isolated_nodes_removed':   True,
            'no_of_isolated_nodes_removed':True,
            'subnodes':                 True,
            'no_of_subnodes':           True,
            'path_length':              True,
            'avg_path_length_of_components':False,
            'path_length_of_giant_component':True,
            'path_length_geo':          True,
            'no_of_inter_removed':      False,
            'density':                  True,
            'nodes_removed_due_to_dependency_failure':False}

option_B = option_A.copy()
 
if failure['dependency']==True:
    option_B['no_of_inter_removed']=True
    option_B['nodes_removed_due_to_dependency_failure']=True
if failure['interdependency']==True: option_A['no_of_inter_removed']=True

conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
db_parameters = conn, net_name_a, net_name_b, save_a, save_b, srid_a, srid_b, spatial_a, spatial_b
metrics = basic_A,basic_B,option_A,option_B
parameters = metrics,failure,handling_variables,fileName,a_to_b_edges,write_step_to_db,write_results_table,db_parameters,store_n_e_atts,length

#run analysis
completed = ia.main(G, GB, parameters, logfilepath)
print 'Did the simulation complete (True/False): ', completed
