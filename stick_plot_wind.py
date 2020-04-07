# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 13:19:48 2020

@author: JiM 
extracted from Liu et al 2019 Fig 8 code
reads in a csv file downloaded from NERACOOS "graphing and download"site and generates a stick plot
"""
### Import modules
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
how_to_average='W' #R for raw, W for weekly, D for daily
hta='Raw' # written out for title
folder=os.path.join('C:'+os.sep, 'Users', 'Joann','Downloads'+os.sep)# provides back or forward slashes dependent on OS

### Functions
def sd2uv(s,d): # converts speed and direction to eastward and northward
    u = float(s)*math.sin(math.pi*float(d)/180.)
    v = float(s)*math.cos(math.pi*float(d)/180.)
    return u,v
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
    q=ax.quiver(date2num(time), [[0]*len(time)], u, v,color='red',scale=20.,width=width, headwidth=headwidth,headlength=headlength, headaxislength=headaxislength) #This Warning says the variable is assigned to but never used but this is needed to plot the wind stress direction  
    ref=10
    ax.quiverkey(q, 0.3, 0.85, ref,
                  "%s m/s" % ref,
                  labelpos='N', coordinates='axes',fontproperties={"weight": "bold","size":40})
    ax.axes.get_yaxis().set_visible(False)
    plt.xticks()
    ax.tick_params(axis="x", labelsize=40)

### read and parse wind data ###
infile=folder+r"wind_"+timespan+"_"+buoy+".csv"# wind spd & dir as downloaded from NERACOOS and renamed accordingly
dateparse = lambda x: pd.datetime.strptime(x[0:-4], '%Y-%m-%d %H:%M:%S')#removes the last 4 characters ' UTC'
df = pd.read_csv(infile, index_col='Time-UTC',parse_dates=['Time-UTC'], date_parser=dateparse)
time=list(df.index)
year=df.index[0].year # used later when labeling xaxis

#convert spd & dir to eastward and northward components of the wind
uw,vw=[],[]
for k in range(len(df)):
    [uw1,vw1]=sd2uv(df['A01-Hourly-Wind_Speed_m/s'][k],df['A01-Hourly-Wind_Direction_degrees'][k])
    uw.append(-1*uw1)# converts to direction towards multiplying by -1
    vw.append(-1*vw1)
#average wind to daily or weekly    
if how_to_average!='R':
    df['uw']=uw
    df['vw']=vw
    time=df.uw.resample(how_to_average).mean().index
    uw=df.uw.resample(how_to_average).mean().values
    vw=df.vw.resample(how_to_average).mean().values

# START FIGURE, CALL STICK_PLOT, and ANNOTATE PLOT
width=0.4 # not sure if this is needed
fig=plt.figure(figsize=(15,12))
ax1=fig.add_subplot(111)
if how_to_average=='D':
    hta='Daily'
elif how_to_average=='W':
    hta='Weekly'
ax1.set_title('Buoy '+buoy+' '+hta+' Wind Stickplot',fontsize=30)     
stick_plot(time,uw,vw,color='red')
mondays = WeekdayLocator(MONDAY)
ax1.xaxis.set_major_locator(mondays)
weekFormatter = DateFormatter('%b %d %Y')
fig.autofmt_xdate()
ax1.xaxis_date()
ax1.tick_params(axis="x", labelsize=20)
ax1.xaxis.set_major_formatter(weekFormatter)
ax1.set_xlim(time[0]-timedelta(days=2),time[-1])
plt.show()
plt.savefig("wind_"+timespan+"_"+buoy+"_"+hta+".png")
