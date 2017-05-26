import time
import googlemaps
import numpy as np
import pandas as pd
import os

gmaps = googlemaps.Client(key='AIzaSyCC6DUYR8zCoWDX_RCaEXCcz3ZmXgS5X38')

def getDistAndDuration(lat1,lng1,lat2,lng2, depTime):
    res = gmaps.directions(str(lat1) + ',' + str(lng1), str(lat2) + ',' + str(lng2),
                           mode='driving', waypoints=None, alternatives=False, avoid=None,
                           language=None, units='metric', region=None, departure_time=depTime,
                           arrival_time=None, optimize_waypoints=False, transit_mode=None,
                           transit_routing_preference=None, traffic_model="best_guess")
    dist = 0
    t = 0
    for lg in res[0]['legs']:
        dist += lg['distance']['value']
        t += lg['duration']['value']
    return ([dist, t])

def loadDistAndDuration(pts, depTime = time.time()):
    pts['Duration'] = pd.Series(np.zeros(len(pts)), index=pts.index)
    for idx, pt in pts[1:].iterrows():
        res = getDistAndDuration(pts.iloc[idx - 1]['Lat'], pts.iloc[idx - 1]['Lng'], pt['Lat'], pt['Lng'],
                                     depTime)
        pts.set_value(idx, 'Distance', res[0])
        pts.set_value(idx, 'Duration', res[1])

def writeDistAndDuration(ptsFile, speedFile, depTime = time.time()):
    pts = pd.read_csv(ptsFile)
    loadDistAndDuration(pts, depTime)
    pts.to_csv(speedFile, index=False)
