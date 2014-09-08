# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 19:50:43 2013

@author: Craig

THIS SCRIPT IS FOR THE STORAGE OF THE DATA FOR ALL NETWORKS WHICH ARE TO BE 
TESTED IN THE FAILURE MODEL

"""

def closest_match():
    '''
    list for the networks recorded as the closest matches
    '''
    conn = ''
    '''
    NETWORK_NAME=[
    'uk_internal_routes','usa_routes_only','europe_internal_flights',
    'north_america_internal_flights',
    'easyjet_flights_final_2',
    'ba_flights_final']
    '''
    NETWORK_NAME=['tyne_river_edited_3',
    'severn_river_edited_v3',
    'janet_connections_3rdlvl',
    'london_lightrail_May2013',
    'boston_subway_geo_w_tapan_2012',
    'LightRail_Baseline',
    'ireland_lightrail_alltrack_geo',
    'ratp_integrated_rail',
    'ratp_metro',
    'ratp_rer',
    'ratp_tram',
    'tyne_wear_metro_geo_w_shortcuts',
    'manchester_metrolink_geo',
    'london_tube',
    'london_tube_v3',
    'london_dlr',
    'london_overground_route_rail',
    'london_lightrail_May2013',
    'boston_subway_geo_w_tapan_2012',
    'tyne_wear_motorways_a_roads_v2',
    'tyne_wear_motorways_a_b_roads_v3',
    'leeds_motorways_a_b_roads_3',
    'mk_motorways_a_b_minor_roads_4',
    'mk_motorways_a_b_roads_2',
    'NationalGrid_Elec_Trans_Jan2012_MT',
    'NationalGrid_Gas_Trans_Jan2012',
    'ire_m_t_roads',
    'ire_m_t_p_5']
    
    return NETWORK_NAME, conn


def lightrail_networks():
    '''
    This function is used for populating the lightrail network list.
    '''
    dbname = 'lightrail'
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    NETWORK_NAME = []
    NETWORK_NAME.append('LightRail_baseline')
    #NETWORK_NAME.append('ireland_lightrail')
    NETWORK_NAME.append('ireland_lightrail_alltrack')
    #NETWORK_NAME.append('ireland_lightrail_alltrack_geo')
    NETWORK_NAME.append('ratp_integrated_rail')
    #NETWORK_NAME.append('ratp_integrated_rail_w_tram_links')
    NETWORK_NAME.append('ratp_metro')
    NETWORK_NAME.append('ratp_rer')
    NETWORK_NAME.append('ratp_tram')
    #NETWORK_NAME.append('tyne_wear_metro')
    #NETWORK_NAME.append('tyne_wear_metro_w_shortcuts')
    #NETWORK_NAME.append('tyne_wear_metro_geo_w_shortcuts')
    #NETWORK_NAME.append('manchester_metrolink_direct')
    #NETWORK_NAME.append('manchester_metrolink_geo')
    #NETWORK_NAME.append('london_tube')
    #NETWORK_NAME.append('london_tube_v3')
    #NETWORK_NAME.append('london_dlr')
    #NETWORK_NAME.append('london_overground_route_rail')
    #NETWORK_NAME.append('london_lightrail_May2013')
    #NETWORK_NAME.append('boston_subway_direct_w_tapan_2012')
    #NETWORK_NAME.append('boston_subway_geo_2012')
    #NETWORK_NAME.append('boston_subway_geo_w_tapan_2012')
    return NETWORK_NAME, conn

def road_regional_networks():    
    dbname = 'roads'
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    NETWORK_NAME = []
    #NETWORK_NAME.append('tyne_wear_motorways_a_roads_v2')
    #NETWORK_NAME.append('tyne_wear_motorways_a_b_roads_v3')
    #NETWORK_NAME.append('tyne_wear_motor_a_b_minor_roads_4')
    #NETWORK_NAME.append('leeds_motorways_a_b_minor_roads_v6')
    NETWORK_NAME.append('leeds_motorways_a_b_roads_3')
    NETWORK_NAME.append('mk_motorways_a_b_minor_roads_4')
    NETWORK_NAME.append('mk_motorways_a_b_roads_2')
    return NETWORK_NAME, conn
    
def road_national_networks():    
    dbname = 'roads'
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    NETWORK_NAME = []
    NETWORK_NAME.append('ire_m_t_roads')
    NETWORK_NAME.append('ire_m_t_p_5')
    return NETWORK_NAME, conn

def other_networks():
    dbname = 'other'
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    NETWORK_NAME = []
    #NETWORK_NAME.append('tyne_river_edited_3')
    NETWORK_NAME.append('severn_river_edited_v2')
    NETWORK_NAME.append('severn_river_edited_v3')
    NETWORK_NAME.append('janet_connections_3rdlvl')
    return NETWORK_NAME, conn

def air_networks():
    dbname = 'air'
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    NETWORK_NAME = []
    NETWORK_NAME.append('uk_internal_routes')  
    NETWORK_NAME.append('usa_routes_only')
    NETWORK_NAME.append('europe_internal_flights')
    NETWORK_NAME.append('north_america_internal_flights')
    NETWORK_NAME.append('easyjet_flights_final_2')
    NETWORK_NAME.append('ba_flights_final')

    return NETWORK_NAME, conn

def infra_networks():
    dbname = 'infrastructure'
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    NETWORK_NAME = []
    NETWORK_NAME.append('NationalGrid_Elec_Trans_Jan2012')
    NETWORK_NAME.append('NationalGrid_Elec_Trans_Jan2012_NT')
    NETWORK_NAME.append('NationalGrid_Elec_Trans_Jan2012_MT')
    NETWORK_NAME.append('NationalGrid_Gas_Trans_Jan2012')
    return NETWORK_NAME, conn
    
def er_networks():
    dbname = "theoretic_networks_er"
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    #first 30
    NETWORK_NAME = [1717,908,378,356,1756,134,1410,557,1168,1788, 1485,743,1622,96,1665,57,1077,497,1616,255, 1234,564,334,74,87,825,102,494,1435,1648]#1094,397,1608,1440,1199,1965,1713,1792,1215,653,1085,1757,781,1516,1998,222,642,842,1892,1904,1699,620,1542,1939,1659,177,900,904,1970,857,1606,1966,1423,230,1692,1790,1641,441,1468,814,424,271,214,448,756,156,1860,870,1392,773,871,666,953,1247,1698,799,1023,197,1492,1492,1522,275,773,1937,744,135,970,861,746,1138
    #full 100
    NETWORK_NAME = [1717,908,378,356,1756,134,1410,557,1168,1788, 1485,743,1622,96,1665,57,1077,497,1616,255, 1234,564,334,74,87,825,102,494,1435,1648,1094,397,1608,1440,1199,1965,1713,1792,1215,653,1085,1757,781,1516,1998,222,642,842,1892,1904,1699,620,1542,1939,1659,177,900,904,1970,857,1606,1966,1423,230,1692,1790,1641,441,1468,814,424,271,214,1430,756,156,1860,870,1392,773,871,666,953,1247,1698,799,1023,197,1492,1492,1522,275,773,1937,744,135,970,861,746,1138]
    #NETWORK_NAME = [164,1387,912,1578,1727,271,298,149,57,467,36,75,80,8,50,106,105,86,73,235,21,55,437,160,277,346,21,360,475,110]
    return NETWORK_NAME, conn
    
def gnm_networks():
    dbname = "theoretic_networks_gnm"
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    #first 30
    NETWORK_NAME = [803,1544,1297,1286,1507,1902,729,1834,1275,940,1793,996,815,1022,840,691,1788,1582,308,270,1265,270,1919,569,15,1426,1374,710,622,1748]
    #full 100
    NETWORK_NAME = [803,1544,1297,1286,1507,1902,729,1834,1275,940,1793,996,815,1022,840,691,1788,1582,308,270,1265,270,1919,569,15,1426,1374,710,622,1748,714,1177,249,1770,651,1818,706,1367,1495,69,953,1624,1160,1984,991,505,1255,193,247,227,530,1509,1921,1033,62,1854,1882,547,599,66,1932,1449,338,42,878,776,1411,911,621,79,1777,1649,147,1696,906,588,1737,1527,471,1144,871,1332,97,747,1116,1221,460,1592,305,342,636,287,1011,556,1858,785,1692,379,1198,1982,1011,556,1858,785,1692,379,1198,1982]
    return NETWORK_NAME, conn    
    
def ws_networks():
    dbname = "theoretic_networks_ws"
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    #NETWORK_NAME = [1602,538,185,173,438,1160,1448,692,1289,649,398,1322,642,210,1726,632,70,732,1861,120,891,609,1938,68,811,588,1490,1382,1518,1765]
    #first 30
    NETWORK_NAME = [813,1009,1003,70,1966,1000,214,1894,369,1326, 804,202,703,706,1707,1935,974,1673,1458,1874, 840,1474,329,58,1568,391,1585,55,588,806]#,1750,387,1216,1637,871,1592,924,1589,1114,331,1265,995,73,14,1333,625,197,905,1701,512,522,312,143,523,997,30,1874,1219,95,1055,351,616,36,435,261,1868,1162,1022,957,152,1976,837,969,1654,98,636,1386,405,169,1443,58,1225,1778,1168,670,1795,184,74,1238,264,1089,678,1275,1532,1456,1340,1097,481,1007,104]
    #full 100
    NETWORK_NAME = [813,1009,1003,70,1966,1000,214,1894,369,1326, 804,202,703,706,1707,1935,974,1673,1458,1874, 840,1474,329,58,1568,391,1585,55,588,806,1750,387,1216,1637,871,1592,924,1589,1114,331,1265,995,73,14,1333,625,197,905,1701,512,522,312,143,523,997,30,1874,1219,95,1055,351,616,36,435,261,1868,1162,1022,957,152,1976,837,969,1654,98,636,1386,405,169,1443,58,1225,1778,1168,670,1795,184,74,1238,264,1089,678,1275,1532,1456,1340,1097,481,1007,1046]

    return NETWORK_NAME, conn
    
def ba_networks():
    dbname = "theoretic_networks_ba"
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    #first 30
    NETWORK_NAME = [909,696,94,193,19,1504,1677,1430,854,16,1424,1699,1076,899,660,1271,545,1397,409,1872,583,1163,955,1373,1305,264,1137,533,345,359]
    #full 100
    NETWORK_NAME = [909,696,94,193,19,1504,1677,1430,854,16,1424,1699,1076,899,660,1271,545,1397,409,1872,583,1163,955,1373,1305,264,1137,533,345,359,1807,809,828,1318,1772,32,1597,1125,1324,666,163,204,1949,857,140,6,885,1783,796,1106,157,1448,1319,180,967,1125,550,324,713,1508,233,636,49,818,1927,1089,1214,948,336,1041,754,201,1066,1354,1235,1736,119,544,860,576,1917,893,1183,1760,946,1510,365,1491,1422,1932,831,1427,1842,302,1696,1200,1847,1683,768,658]
    return NETWORK_NAME,conn
    
def hra_networks():
    dbname = "theoretic_networks_hr+"
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    #full 100
    NETWORK_NAME = [820,259,8,91,15,1111,1365,6,13,91,3,3,10,31,91,364,820,111,1111,156,259,31,1111,9,6,511,341,111,6,781,400,255,7,1365,21,40,57,73,10,91,91,11,21,820,781,21,31,7,73,259,111,1365,781,31,1093,6,341,31,364,21,13,43,7,8,121,11,11,259,9,585,121,21,255,7,8,10,364,259,57,15,255,400,111,341,8,6,1111,1365,1111,10,511,1111,73,511,400,1365,1111,40,63,121]
    #full 100
    NETWORK_NAME = [820,259,8,91,15,1111,1365,6,13,91,3,3,10,31,91,364,820,111,1111,156,259,31,1111,9,6,511,341,111,6,781,400,255,7,1365,21,40,57,73,10,91,91,11,21,820,781,21,31,7,73,259,111,1365,781,31,1093,6,341,31,364,21,13,43,7,8,121,11,11,259,9,585,121,21,255,7,8,10,364,259,57,15,255,400,111,341,8,6,1111,1365,1111,10,511,1111,73,511,400,1365,1111,40,63,121]
    return NETWORK_NAME,conn
    
def hr_networks():
    dbname = "theoretic_networks_hr"
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    #wrong
    NETWORK_NAME = [2,9,5461,3280,2801,585,9,4,57,364,127,40,400,1555,1555,21,15,4681,364,9331,4681,40,156,9331,57,2,31,585,127,15]
    #full 100 correct
    NETWORK_NAME = [511,400,4,43,156,21,40,781,511,40,2,43,121,40,85,259,2,7,9,21,13,2,127,156,21,9,40,127,8,31,2,2,5,1555,73,1555,31,8,9,2,57,85,4,31,2,85,2,9,259,259,3,2,2,3,8,2,1365,4,2,2,7,43,1555,7,341,341,511,585,400,7,2,2,1093,1555,6,31,31,73,781,85,40,15,43,57,21,2,2,6,57,21,259,2,9,5,121,8,2,73,585,85]
    return NETWORK_NAME,conn
    
def hc_networks():
    dbname = "theoretic_networks_hc"
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    NETWORK_NAME = [5,25,125,625,4,16,64,256,1024]
    return NETWORK_NAME,conn
    
def tree_networks():
    dbname = "theoretic_networks_tree"
    host = 'local' ; user = 'postgres' ; password = 'aaSD2011' ; port = '5433'
    conn = "PG: host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (host, dbname, user, password, port)
    #NETWORK_NAME = [2,2,2,2,2,2,3,7,15,31,63,127,255,511,4,13,40,121,364,1093,5,21,85,341,1365,6,31,156,781,7]
    NETWORK_NAME = [2,2,2,2,2,2,3,7,15,31,63,127,255,511,4,13,40,121,364,1093,5,21,85,341,1365,6,31,156,781,7,43,259,1555,8,57,400,9,73,585,10,91,820,11,111,1111]
    return NETWORK_NAME,conn


