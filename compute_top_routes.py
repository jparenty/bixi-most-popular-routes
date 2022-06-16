# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 14:43:45 2021

Take as input all the bixi rides for a given years and write as output:
    - top 100 rides per [freq].csv in data directory


@author: jeanp
##NOTE###
#
#
# excecuter le code a freq journaliere et mettre tout les resultats dans un dict qu on ecrit dans un xlsx de environ 200 pages
# nous permettra de voir les tendances journaliere
#
#
# *simple* Problem encounter: 
# - missing 2 stations'name from stations_2019.csv, we where left with 2 bixi stations' codes that we needed to find the name and position of
# - data formating for month of May, starting code and ending code where float instead of int.
# - duplicates station in stations_2020.csv, same stations code but different names, keep only one of the 2, they are located at the same place
#
#*harder*:
"""
from time import sleep
import os.path as osp
import os, sys
import numpy as np
import pandas as pd
from datetime import datetime
from tqdm import trange

script_dir = osp.dirname(__file__)

#start_index_test = unique_start_code.index(7070)



def create_matrix(rides_month):
    #ride_april = ride_april.reset_index(drop = True)
    #rides_month = rides_months[7]
    #reformat rides_month start station code column to int
    rides_month['start_station_code'] = rides_month['start_station_code'].astype(str)
    rides_month['start_station_code'] = pd.to_numeric(rides_month['start_station_code'], downcast="integer", errors='coerce')
    
    rides_month['end_station_code'] = rides_month['end_station_code'].astype(str)
    rides_month['end_station_code'] = pd.to_numeric(rides_month['end_station_code'], downcast="integer", errors='coerce')
    
    rides_month = rides_month.dropna().reset_index(drop=True)
    
    
    #rides_month_subset_test = rides_month.loc[ (rides_month.start_station_code == 7125)  & (rides_month.end_station_code == 7125)]

    
    #get unique values of start_station_code and end_station_code
    unique_start_code = sorted(rides_month['start_station_code'].unique())
    unique_end_code = sorted(rides_month['end_station_code'].unique())
    
    #chosing the longest unique code series betnwee start code and end code to then use it to create the matrix
    if len(unique_start_code) > len(unique_end_code):
        unique_code = unique_start_code
    elif len(unique_start_code) < len(unique_end_code):
        unique_code = unique_end_code
    else:
        unique_code = unique_start_code
    
    #creating a matrix of shape matrix(number of unique stations, number of unique stations) with 0s to represent the number of ridess that take place for each possible combinaison of stations
    matrix = np.zeros((len(unique_code), len(unique_code))) 
    
    #iterate over all the ridess and for each row increment the right combinaison of station in the matrix
    for i in range(0, len(rides_month)):
        
        #locate start and end station's code
        start_station = rides_month['start_station_code'].iloc[i]
        end_station = rides_month['end_station_code'].iloc[i]
        
        #find the corresponding name index for the start and end station from unique_start_code and unique_end_code 
        start_index = unique_code.index(start_station)
        end_index = unique_code.index(end_station)
        
        #if start_station == 7125 and end_station == 7125:
        #    print(f'start_index = {start_index}, end_index = {end_index}')
        #if start_index == 38 and end_index == 38:
            #print(rides_month.iloc[i])
            #print(f'index: {i}')
            #print(f'start station: {start_station}, end station: {end_station}')
            #print(f'start index: {start_index}, end index: {end_index}')
            #print('###############')
        #technically we could use either only unique_start_code or unique_end_code ti set up the index as they're the same list
   
        #start station code on the y axis
        #end station code on the x axis
        count = matrix[start_index][end_index]
        matrix[start_index][end_index] = count + 1
    
    return matrix, unique_code

def get_top100_from_matrix(matrix, stations):
    
    matrix_duplicate = np.copy(matrix)

    num_largest = 500
    
    x = np.zeros(num_largest, dtype = int)    
    y = np.zeros(num_largest, dtype = int)
    
    for idx in range(num_largest):
        x[idx] = int(np.unravel_index(matrix_duplicate.argmax(), matrix_duplicate.shape)[0])
        y[idx] = int(np.unravel_index(matrix_duplicate.argmax(), matrix_duplicate.shape)[1])
        #print(f'x: {x}, y: {y}')
        matrix_duplicate[x[idx]][y[idx]] = 0.
    
    start_station =  []
    #fill up start station from the top 100 rides
    for i in range(0, len(x)):
        code_station = x[i]
        start_station.append(stations['name'][code_station])
        
    end_station = []
    for i in range(0, len(y)):
        end_code_station = y[i]
        end_station.append(stations['name'][end_code_station])
                
    count = matrix[x, y]
    
    top_100 = pd.DataFrame(list(zip(start_station, end_station, count)), columns = ['Start Station', 'End Station', 'Occurence'])
    
    return top_100


def add_duration_member_lat_long(top, rides_month, stations_name, year, month):
    
    #initiate the new columns for top 100
    top.insert(loc=1,column="Start Latitude", value='')
    top.insert(loc=2, column="Start Longitude", value='')
    
    top.insert(loc=4,column="End Latitude", value='')
    top.insert(loc=5,column="End Longitude", value='')
    
    top['Average Duration'] = ''
    top['Percentage Member'] = ''
    
    #insert month and year column
    top.insert(loc=0,column="Year", value=year)
    top.insert(loc=1,column="Month", value=month)
    
    #fill the new columns for each route
    for i in range(0, len(top)):
        start_station = top['Start Station'][i]
        end_station = top['End Station'][i]
        
        #retreive additional information about start station
        start_code = stations_name.loc[stations_name['name'] == start_station]['code'].iloc[0]
        start_lat = stations_name.loc[stations_name['name'] == start_station]['latitude'].iloc[0]
        start_long = stations_name.loc[stations_name['name'] == start_station]['longitude'].iloc[0]
        
        #retreive additional information about end station
        end_code = stations_name.loc[stations_name['name'] == end_station]['code'].iloc[0]
        end_lat = stations_name.loc[stations_name['name'] == end_station]['latitude'].iloc[0]
        end_long = stations_name.loc[stations_name['name'] == end_station]['longitude'].iloc[0]
        
        all_rides_route = rides_month.loc[ (rides_month.start_station_code == start_code) & (rides_month.end_station_code == end_code)]
        
        #compute avg duration of the specific route and percentage of member        
        avg_duration = all_rides_route['duration_sec'].mean()
        percentage_member = all_rides_route['is_member'].mean()*100
        
        top['Start Latitude'][i] = start_lat
        top['Start Longitude'][i] = start_long
        
        top['End Latitude'][i] = end_lat
        top['End Longitude'][i] = end_long
        
        top['Average Duration'][i] = avg_duration
        top['Percentage Member'][i] = percentage_member
        
        
    return top


def clean_stations_name(stations_name, unique_code):
    #remove duplicate from stations_name
    stations_name = stations_name.drop_duplicates(subset=['code'], keep='last')
    #only keep the stations that are used in in the analysed month
    stations_name = stations_name[stations_name['code'].isin(unique_code)].reset_index(drop=True)
      
    return stations_name

def nlargest_indices(arr, n):
    
    uniques = np.unique(arr)
    #print(uniques)
    threshold = uniques[-n]
    
    return np.where(arr >= threshold)


def main(rides, stations_name, year):
    
    year = 2020
    #read station dataset
    stations_name = pd.read_csv('./data/Stations_2020.csv',  encoding = "utf-8")
    stations_name = stations_name.rename(columns={stations_name.columns[0] : 'code'})
    stations_name = stations_name.sort_values(by = ['code']).reset_index(drop=True)
    
    
    #check_unique_start_code = unique_start_code.isin(stations_name['code'])
    #stations_name_code = list(stations_name['code'])
    #set(unique_start_code) - set(stations_name_code)
    
    #read rides dataset
    rides = pd.read_csv("./data/trajet_2020.csv")
    
    rides.head(10)
    rides.tail(10)            
    
    #format start_date column as date type
    rides["start_date"] = pd.to_datetime(rides["start_date"], format='%Y-%m-%d')
    rides["start_date"] = rides['start_date'].dt.strftime('%Y-%m-%d')
    rides["start_date"] = pd.to_datetime(rides["start_date"], format='%Y-%m-%d')

    #format start_date column as date type    
    rides["end_date"] = pd.to_datetime(rides["end_date"], format='%Y-%m-%d')
    rides["end_date"] = rides['end_date'].dt.strftime('%Y-%m-%d')
    rides["end_date"] = pd.to_datetime(rides["end_date"], format='%Y-%m-%d')

    
    #group     
    g =rides.groupby(pd.Grouper(key='start_date', freq='M'))
    rides_months = [group for _,group in g]
            
    name_month = ["april", "may", "june", "july", "august", "september", "october", "november"]
    
    #chekcing that project has correct directory structure to store output data
    #create appropriate directory to store data if needed
    if not os.path.isdir(os.path.join(script_dir, '..', 'data')):
        os.mkdir(os.path.join(script_dir, '..', 'data'))
    
    if not os.path.isdir(os.path.join(script_dir, '..', 'data', 'bixi_ride', year)):
        os.mkdir(os.path.join(script_dir, '..', 'data', 'bixi_ride', year)) 
    
    #if not os.path.isdir(os.path.join(script_dir, '..', 'data', year)):
    #    os.mkdir(os.path.join(script_dir, '..', 'data', year)) 
    
    for i in trange(0, len(rides_months)):
        matrix, unique_code = create_matrix(rides_months[i])     
        stations = clean_stations_name(stations_name, unique_code)
        top_500 = get_top100_from_matrix(matrix, stations)
        top_500 = add_duration_member_lat_long(top_500, rides_months[i], stations, year, name_month[i])
        #write top_100 results to csv
        top_500.to_csv('./data/bixi_ride/' + str(year) + '_top500' + '/top_500_' + name_month[i] + '_' + str(year) + '.csv', encoding='utf-8', index=False)
        
        
    ##########
    ## TEST ##
    ##########
    top_500_april_2020 = top_100
    top_500_april_2020.insert(loc=0,column="Month", value=4)
    #top_500_april_2020["Date"] = pd.to_datetime(top_500_april_2020["Date"], format='%Y-%m')
    
    top_500_april_2020.to_csv('./data/bixi_ride/Test/top_500_april_2020.csv', encoding='utf-8', index=False)
    
    top_500_may_2020 = top_100
    top_500_may_2020.insert(loc=0,column="Month", value=5)
    #top_500_may_2020["Date"] = pd.to_datetime(top_500_may_2020["Date"], format='%Y-%m')    
    
    top_500_may_2020.to_csv('./data/bixi_ride/Test/top_500_may_2020.csv', encoding='utf-8', index=False)
    
    ride_november_2020 = rides_months[7]
    
    stations_name.loc[stations_name['name'] == "Rosemont / Viau" ]
    stations_name.loc[stations_name['name'] == "Dollard / Bernard" ]
    
    stations_name.loc[stations_name['name'] == "Parc Jean-Drapeau (Chemin Macdonald)" ]


    ride_november_2020_subset = ride_november_2020.loc[ (ride_november_2020.start_station_code == 7124) & (ride_november_2020.end_station_code == 7124)]
    
    ride_april = rides_months[0]
    
    ride_april = ride_april.sort_values(by = ['start_station_code', 'end_station_code'], ascending = (True, True))
    
    rides_subset = ride_april.loc[ (ride_april.start_station_code == 6034) ]
    rides_subset_berri = rides_months[0].loc[ (rides.start_station_code == 6023) & (rides.end_station_code == 6023)]
    
    ride_subset2 = ride_april.loc[ (ride_april.start_station_code == 6036) & (ride_april.end_station_code == 6036)] 
     


if __name__ == '__main__':
    main()