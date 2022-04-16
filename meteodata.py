# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
pd.set_option('display.max_columns', None)

#import matplotlib.pyplot as plt
from meteostat import Stations, Daily, Hourly
import datetime as dt
import numpy as np

import requests
#import urllib.parse

def getMeteostat(loc='03647',date_range=None,offset=0,sample_rate='daily',interpol=1,min_coverage=0.9):
    
    # Address entered - trying to fetch lat & lon
    if isinstance(loc,dict):
        
        latlong,_=address2coords(view=0,**loc)
        
        if len(latlong)>0:
            print('Successfully derived lat & lon from address data!')
            loc=list(latlong.iloc[0,:])
        else:
            print('!!! Sorry, address query did not return any lat/lon data - try different address')
            loc=None
    
    # If loc entered is valid and/or geodata search was successful
    if loc is not None:
        
        # Sample rate
        if sample_rate!='daily':
            sample_rate='hourly'
            f='H'
        else:
            f='D'
        
        # If no date range was entered, use last 365 days, with selected offset in days
        if date_range is None:
            print('Date range not provided - taking last year, offset=',offset,'days')
            end=dt.datetime.today()-dt.timedelta(days=offset)
            delta=365+offset
            start=dt.datetime.today()-dt.timedelta(days=delta)
            #start = dt.datetime(2018, 1, 1)
            #end = dt.datetime(2018, 12, 31)
            date_range=[start,end]

        print('Using time period from ',date_range[0],' to ',date_range[1],' with ',sample_rate,' frequency')

        # If loc is a list/tuple then lat & lon was entered - fetch 20 closest stations and prioritize by data 
        # coverage & distance
        if isinstance(loc,(list,tuple)):
            print('Fetching nearby stations for latitude ',loc[0],' and longitude ',loc[1])
            st= Stations()
            st=st.nearby(loc[0], loc[1])
            #st1=st.inventory(sample_rate, date_range[0])
            #st2=st.inventory(sample_rate, date_range[1])
            #st1 = st1.fetch(10).reset_index()
            #st2 = st2.fetch(10).reset_index()
            #st = pd.concat([st1,st2],axis=0,ignore_index=True)

            #st=st.drop_duplicates().reset_index(drop=True)

            st=st.fetch(20).reset_index()

            col_start=sample_rate+'_start'
            col_end=sample_rate+'_end'

            st[col_start]=pd.to_datetime(st[col_start],dayfirst=True,errors='coerce')
            st[col_end]=pd.to_datetime(st[col_end],dayfirst=True,errors='coerce')

            null_date = pd.to_datetime('1900-01-01',dayfirst=True,errors='coerce')
            st['no_range']=0
            st.loc[st[col_start].isnull(),'no_range']=1
            st[col_start]=st[col_start].fillna(null_date)
            st[col_end]=st[col_end].fillna(null_date)

            st['valid_obs']=0
            st['coverage']=0

            #display(st)

            true_rng=pd.date_range(start=date_range[0], end=date_range[1], freq=f)

            # Analyzing valid ranges returned by Stations.nearby()
            for i in range(len(st)):

                rng=pd.date_range(start=st.loc[i,col_start], end=st.loc[i,col_end], freq=f)
                cond=(rng>=date_range[0])&(rng<=date_range[1])
                st.loc[i,'valid_obs']=-np.sum(cond)
                st.loc[i,'coverage']=-np.sum(cond)/len(true_rng)


            # Checking rows with NaNs - sometimes Stations.nearby returns no data for given station
            # but Daily() or Hourly() actually returns data - check rows with no data again using Daily()/Hourly()

            if np.sum(st['no_range']==1)>0:

                ids=list(st.loc[st['no_range']==1,'id'].astype(str))
                
                print('Double-checking data availability for the following station IDs:')
                print(ids)
                
                for idd in ids:
                    if sample_rate=='daily':
                        d = Daily(idd, date_range[0], date_range[1])
                    else:
                        d = Hourly(idd, date_range[0], date_range[1])

                    #d = d.normalize()
                    #d = d.interpolate()
                    d = d.fetch()

                    if len(d)>0:
                        d=d.reset_index()
                        st.loc[st['id']==idd,'valid_obs']=-len(d)
                        st.loc[st['id']==idd,'coverage']=-len(d)/len(true_rng)
                        st.loc[st['id']==idd,col_start]=d.loc[0,'time']
                        st.loc[st['id']==idd,col_end]=d.loc[len(d)-1,'time']
            
            # Check data completeness & order by coverage (completeness) and distance
            st['adj_coverage']=st['coverage']/min_coverage
            st.loc[st['adj_coverage']<-1,'adj_coverage']=-1
            st=st.sort_values(by=['adj_coverage','distance'],ascending=True).reset_index(drop=True)

            display(st.head())

            loc=st.loc[0,'id']
        
        # Pulling the data
        print('Puling ',sample_rate,' data for location ',loc,' and time period from ',date_range[0],' to ',date_range[1])

        if sample_rate=='daily':

            # Get daily data
            print('Pulling daily data')
            data = Daily(loc, date_range[0], date_range[1])

        else:

            print('Pulling hourly data')
            data = Hourly(loc, date_range[0], date_range[1])

        if np.sum(interpol)>0:
            data = data.normalize()
            data = data.interpolate()

        data = data.fetch()
        
    else:
        data=None
        print('!!! Sorry, location info not recognized')
    
    return(data)

def address2coords(street='',town='',country='',postcode='',n=1,view=1,*args):
    
    '''EXAMPLES:
    address2coords(country='United kingdom',postcode='OX18 4NH')
    
    indata={'country':'united kingdom','postcode':'OX18 4NH'}
    address2coords(**indata)
    
    address2coords(town='Vresina',country='Czech republic',n=2)
    
    address2coords(postcode='74285',country='Czech republic')
    '''
    
    response=None
    out=pd.DataFrame(columns=['Latitude','Longitude'])
    
    if len(street)>0:
        qs="&treet="+street
    else:
        qs=''
    
    if len(town)>0:
        qt="&city="+town
    else:
        qt=''
        
    if len(country)>0:
        qc="&country="+country
    else:
        qc=''
        
    if len(postcode)>0:
        qp="&postalcode="+postcode
    else:
        qp=''
    
    qry= qs+ qt + qc + qp
    
    '''lq = len(qry)-1
    
    if qry[lq]=='+':
        qry=qry[0:lq]'''
    
    if np.sum(view)>0: print('Fetching lon & lat for the following query: ',qry)
    
    if len(qry)>3:
    
        ns=str(n)
        #url = "https://nominatim.openstreetmap.org/?addressdetails=1&q=" + qry +"&format=json&limit="+ns
        url="https://nominatim.openstreetmap.org/search.php?format=json&addressdetails=1&limit="+ns+qry
        if np.sum(view)>0: print('Full query: ',url)
            
        response = requests.get(url).json()

        if len(response)>0:
            print('SUCCESS - found at least one record')
            
            if n>len(response):
                n=len(response)
            
            out['Latitude']=[0]*n
            out['Longitude']=[0]*n
            
            for i in range(n):
                out.loc[i,'Latitude']=float(response[i]["lat"])
                out.loc[i,'Longitude']=float(response[i]["lon"])

        else:
            print('SORRY - no luck, try with a different query!')
            
    else:
        
        print('!!! You entered empty query')
        
    if np.sum(view)>0: 
        print('Latitude & longitude data:')
        print(out)
        print('**************** FULL RESPONSE:')
        print(response)
    
    return(out,response)