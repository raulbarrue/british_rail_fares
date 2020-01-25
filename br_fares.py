#This script downloads the current British Rail fares and saves them into a csv file

import requests
import json
import pandas as pd
import time
from datetime import datetime


#List of stations as Origin and Destination. Please use NRS station codes.
stations = ['EUS','MAN','LIV']

flows = []
flows_check = []

#This double loop creates a list of flows from the "stations" list
#e.g. EUS to MAN, EUS to LIV, MAN to LIV, etc.
for station_1 in stations:
    for station_2 in stations:
        if station_1 != station_2:
            check = [station_1, station_2]
            check.sort()
            if check not in flows_check:
                flows.append([station_1, station_2])
                flows_check.append(check)

#SIMPLE MODE

#Call brfares.com API for each of the flows in the list and append the fares in the "results" list.
#If there is an error, that flow will be appended to the "errors" flow, where it can be checked at the end.
errors = []
results = []

for origin, destination in flows:
    try:
        url = 'http://api.brfares.com/querysimple?orig={}&dest={}'.format(origin, destination)
        data = requests.get(url).json()
        for i in range(len(data['fares'])):
            flow_orig = data['fares'][i]['flow_orig']['longname']
            flow_dest = data['fares'][i]['flow_dest']['longname']
            fare_setter = data['fares'][i]['fare_setter']['name']
            route = data['fares'][i]['route']['longname']
            ticket_type = data['fares'][i]['ticket']['code']
            ticket_type2 = data['fares'][i]['ticket']['type']['desc']
            ticket_name = data['fares'][i]['ticket']['longname']
            ticket_class = data['fares'][i]['ticket']['tclass']['desc']
            restriction_code = data['fares'][i]['restriction_code']
            updated_date = data['valid_date']
            valid_until = data['valid_until_date']
            if data['fares'][i]['adult']:
                fare = data['fares'][i]['adult']['fare']/100 #It's in pence...
            else:
                fare = None
            all_data = [updated_date,
                        valid_until,
                        origin,
                        destination, 
                        flow_orig,
                        flow_dest,
                        fare_setter,
                        route, 
                        ticket_type,
                        ticket_type2,
                        ticket_name,
                        ticket_class,
                        restriction_code,
                        fare]
            results.append(all_data)
            print(i, origin, destination, ticket_name, ticket_type)
    except:
        errors.append([origin, destination])
        print('Error', origin, destination)

#Create results dataframe
df_results = pd.DataFrame(results, columns = ['updated_date', 'valid_until_date', 'origin', 'destination', 'flow_origin', 'flow_destination', 'fare_setter', 'route', 'ticket_code', 'ticket_type', 'ticket_name', 'ticket_class', 'restriction_code', 'fare'])
df_results.updated_date = pd.to_datetime(df_results.updated_date, format = '%Y%m%d')
df_results.valid_until_date = pd.to_datetime(df_results.valid_until_date, format = '%Y%m%d')

#Export results to CSV
filename = datetime.today().strftime('%Y%m%d') + '_fares.csv'
df_results.to_csv(filename, index=False)

#Create errors dataframe and export to CSV
df_errors = pd.DataFrame(errors, columns = ['origin', 'destination'])
filename_errors = datetime.today().strftime('%Y%m%d') + '_errors.csv'
df_errors.to_csv(filename_errors, index=False)

