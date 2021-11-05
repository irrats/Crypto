#!/usr/bin/env python

import pandas as pd
import numpy as np
from datetime import datetime
import os

#function to validate the Start Date
def GetStartDate():
    isValid=False
    while not isValid:
        userIn = input('Enter Start date(yyyy-mm-dd): ')
        try: # strptime throws an exception if the input doesn't match the pattern
            sd = datetime.strptime(userIn, "%Y-%m-%d")
            isValid=True
        except:
            print("Invalid date. Try again in format: yyyy-mm-dd")
    return sd


# function to insert the End Date or leave current date
def GetEndDate():

    userIn = str(input('Enter End date(yyyy-mm-dd) OR Press "x" to proceed with now-date: '))
    if userIn ==str('x'): # strptime throws an exception if the input doesn't match the pattern
        ed = datetime.now()
    else:
        ed = datetime.strptime(userIn, "%Y-%m-%d")     
    return ed


#Input variables
file = str(input('Enter File Name ex: LTC.csv '))
start_date = GetStartDate() #validates date input
end_date = GetEndDate()  #returns either custom date or now
time_frame = str(input('Enter Timeframe to filter in Minutes. Ex: 1/5/15/60 '))

#saves path to file to save the output in the same folder as input file
savepath = os.path.dirname(os.path.realpath(file))


#cretae df
df = pd.read_csv(file, dtype=str, parse_dates=['date'], skiprows = 1)

#extract symbol of current pair (for naming and volume-variables)
str_symbol = str(df['symbol'][3]) #eth/usdt
part_symbol = str_symbol.partition('/') #split
first_sym = 'Volume ' + part_symbol[0] #eth
second_sym = 'Volume ' + part_symbol[2] #usdt


#rename columns in df accordingly
df.columns = ['unix', 'date', 'symbol', 'open', 'high', 'low', 'close', first_sym, second_sym, 'tradecount']
#set type of data for each column
df['tradecount'] = df['tradecount'].astype(float)
df['high'] = df['high'].astype(float)
df['low'] = df['low'].astype(float)
df['open'] = df['open'].astype(float)
df['close'] = df['close'].astype(float)
df[first_sym] = df[first_sym].astype(float)
df[second_sym] = df[second_sym].astype(float)



#filtering between 2 dates
after_start_date = df["date"] >= start_date
before_end_date = df["date"] <= end_date
between_two_dates = after_start_date & before_end_date
#extracting the dates diapason
df= df.loc[between_two_dates]

#set timeframe as per input n mins
df = df.set_index('date').resample(time_frame + 'T').agg({'open': 'first', 'high':'max', 'low':'min', 'close': 'last', first_sym: 'sum', second_sym: 'sum','tradecount':'sum'})


#replace symbol sign for naming
symbol = str_symbol.replace('/', '_')
#date str to datetime for naming
str_start = start_date.strftime("%Y%m%d")
str_end = end_date.strftime("%Y%m%d")


#reformat columns add decimals
df.columns = ['open', 'high', 'low', 'close', first_sym, second_sym, 'tradecount']
#set type of data for each column + formatting with defined num  decimals
df['tradecount'] = df['tradecount'].round().astype(int)
df[first_sym] = df[first_sym].apply(lambda x: f"{x:.10f}")
df[second_sym] = df[second_sym].apply(lambda x: f"{x:.10f}")
df['high'] = df['high'].apply(lambda x: f"{x:.8f}")
df['low'] = df['low'].apply(lambda x: f"{x:.8f}")
df['open'] = df['open'].apply(lambda x: f"{x:.8f}")
df['close'] = df['close'].apply(lambda x: f"{x:.8f}")

#save to csv file
df.to_csv(os.path.join(savepath, symbol + '_' + time_frame + '_'+ str_start + '_' + str_end +'.csv'))
