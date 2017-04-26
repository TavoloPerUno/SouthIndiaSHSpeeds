import lib.interpolate as itp
import googlemaps
import pandas as pd
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyD3sNjKSAqK_7eBo8FNRbyapjUODTXnh_M')

# Geocoding an address
orig_geocode = gmaps.geocode('SH 20, Belagavi, Karnataka')
dest_geocode = gmaps.geocode('SH 20, Bagalkot, Karnataka')
orgLat = orig_geocode[0]['geometry']['location']['lat']
orgLng = orig_geocode[0]['geometry']['location']['lng']
destLat = dest_geocode[0]['geometry']['location']['lat']
destLng = dest_geocode[0]['geometry']['location']['lng']

waypoints = itp.interpolateRoute(100, orgLat, orgLng, destLat, destLng)
points = pd.DataFrame(columns = ["Id", "Name", "Lat", "Lng"])
for idx, pt in enumerate(waypoints):
    if idx == 0:
        points.loc[idx] = [idx + 1, "Belgaum", pt[0], pt[1]]
    elif idx == len(waypoints) - 1:
        points.loc[idx] = [idx + 1, "Bagalkot", pt[0], pt[1]]
    else:
        points.loc[idx] = [idx + 1, "", pt[0], pt[1]]

rdPoints = pd.DataFrame(columns = ["Id", "Name", "Lat", "Lng"])


i=0
while(i < len(points)):
    if(i+99 < len(points)):
        tpts = str(points.iloc[0]['Lat']) + ',' + str(points.iloc[0]['Lng']) + '|' + \
               ''.join([str(pt['Lat']) + ',' + str(pt['Lng']) + '|' for index, pt in points[i:i+98].iterrows()]) \
               + str(points.iloc[len(points) - 1]['Lat']) + ',' + str(points.iloc[len(points) - 1]['Lng'])

        rgPts = gmaps.snap_to_roads(tpts, interpolate=False)
        if(i == 0):
            rdPoints.loc[0] = ["1", "Belgaum", rgPts[0]['location']['latitude'], rgPts[0]['location']['longitude']]
        for loc in rgPts[0:99]:
            rdPoints.loc[len(rdPoints)] = [str(len(rdPoints)+ 1), "", loc['location']['latitude'], loc['location']['longitude']]

    else:
        tpts = str(points.iloc[0]['Lat']) + ',' + str(points.iloc[0]['Lng'])  + \
               ''.join(['|' + str(pt['Lat']) + ',' + str(pt['Lng'])  for index, pt in points[i:len(points)].iterrows()])
        rgPts = gmaps.snap_to_roads(tpts, interpolate=False)
        for loc in rgPts[0:len(rgPts)-2]:
            rdPoints.loc[len(rdPoints)] = [str(len(rdPoints) + 1), "", loc['location']['latitude'], loc['location']['longitude']]
        rdPoints.loc[len(rdPoints)] = [str(len(rdPoints) + 1), "", loc['location']['latitude'], loc['location']['longitude']]
    i += 98

print(rdPoints)