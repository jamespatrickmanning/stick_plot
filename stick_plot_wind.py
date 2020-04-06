# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 13:19:48 2020

@author: JiM 
extracted from Liu et al 2019 Fig 8 code
"""
import numpy as np
import os
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import date2num,DateFormatter,WeekdayLocator, MONDAY
import math
### HARDCODES #####
buoy=r'A01'#name of NERACOOS buoy
timespan=r'mar2020'# assumes you have renamed "download.csv" to "wind_<timespan>_<buoy>"
how_to_average='W' #W for weekly, D for daily
hta='Weekly' # written out for title
folder=os.path.join('C:'+os.sep, 'Users', 'Joann','Downloads'+os.sep)
### Functions
def sd2uv(s,d):
    u = float(s)*math.sin(math.pi*float(d)/180.)
    v = float(s)*math.cos(math.pi*float(d)/180.)
    return u,v
### read and parse wind data ###
infile=folder+r"wind_"+timespan+"_"+buoy+".csv"# wind spd & dir as downloaded from NERACOOS
dateparse = lambda x: pd.datetime.strptime(x[0:-4], '%Y-%m-%d %H:%M:%S')#removes the last 4 characters ' UTC'
df = pd.read_csv(infile, index_col='Time-UTC',parse_dates=['Time-UTC'], date_parser=dateparse)
time=list(df.index)
year=df.index[0].year # used later when labeling xaxis
#convert spd & dir to eastward and northward components of the wind
uw,vw=[],[]
for k in range(len(df)):
    [uw1,vw1]=sd2uv(df['A01-Hourly-Wind_Speed_m/s'][k],df['A01-Hourly-Wind_Direction_degrees'][k])
    uw.append(-1*uw1)# converts to direction towards
    vw.append(-1*vw1)
df['uw']=uw
df['vw']=vw
time=df.uw.resample(how_to_average).mean().index
#time[0]=time[0]+timedelta(days=2)
uw=df.uw.resample(how_to_average).mean().values
vw=df.vw.resample(how_to_average).mean().values


'''#test data
time=[dt(2020,3,4,0,0,0), dt(2020,3,15,0,0,0), dt(2020,3,30,0,0,0)]
year=time[0].year
uw=[10,0,-10]
vw=[10,20,-20]
'''
width=0.4 # not sure if this is needed
fig=plt.figure(figsize=(15,12))
ax1=fig.add_subplot(111)
ax1.set_title('Buoy '+buoy+' '+hta+' Wind Stickplot',fontsize=15) 

def stick_plot(time, u, v, **kw):
    width = kw.pop('width', 0.004) 
    headwidth = kw.pop('headwidth', 4)
    headlength = kw.pop('headlength', 6)
    headaxislength = kw.pop('headaxislength', 6)
    angles = kw.pop('angles', 'uv')
    ax = kw.pop('ax', None)
    if angles != 'uv':
        raise AssertionError("Stickplot angles must be 'uv' so that"
                             "if *U*==*V* the angle of the arrow on"
                             "the plot is 45 degrees CCW from the *x*-axis.")
    time, u, v = map(np.asanyarray, (time, u, v))
    if not ax:
        ax = ax1
    q=ax.quiver(date2num(time), [[0]*len(time)], u, v,color='green',scale=20.,width=width, headwidth=headwidth,headlength=headlength, headaxislength=headaxislength) #This Warning says the variable is assigned to but never used but this is needed to plot the wind stress direction  
    ref=10
    ax.quiverkey(q, 0.1, 0.85, ref,
                  "%s m/s" % ref,
                  labelpos='N', coordinates='axes',fontproperties={"weight": "bold","size":20})
    ax.axes.get_yaxis().set_visible(False)
    plt.xticks()
    ax.tick_params(axis="x", labelsize=20)
    
stick_plot(time,uw,vw,color='green')
'''
speed=[]
for a in np.arange(len(uw)):
    speed.append(np.sqrt(uw[a]**2+vw[a]**2))
ax1.bar(time,speed,width=0.08,alpha=0.2,label="wind_stress",zorder=0)
ax1.set_ylabel('Pa',fontsize=15) 
'''
mondays = WeekdayLocator(MONDAY)
ax1.xaxis.set_major_locator(mondays)
weekFormatter = DateFormatter('%b %d %Y')
ax1.xaxis_date()
ax1.tick_params(axis="x", labelsize=20)
#ax1.xaxis_font = {'size':40}
ax1.xaxis.set_major_formatter(weekFormatter)
ax1.set_xlim(time[0]-timedelta(days=2),time[-1])
#ax1.axes.get_xaxis().set_ticks([])
#ax1.set_xlabel(str(year),fontsize=20)
#ax1.set_ylim(-max(speed)-0.1,max(speed)+0.1)
