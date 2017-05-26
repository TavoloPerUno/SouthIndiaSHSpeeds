import gpxpy
import googlemaps
import lib.interpolate as itp
import pandas as pd
import os
import math
gmaps = googlemaps.Client(key='AIzaSyAPHp1f7OrbiYRHuNIPO9NjOEYB78mVVr4')

def getWaypointsFromGPX(gpxFile):
    gpx_file = open(gpxFile, 'r')

    wPts = pd.DataFrame(columns=["Name", "Lat", "Lng", "Distance"])

    gpx = gpxpy.parse(gpx_file)
    org = gpx.waypoints[0]
    dest = gpx.waypoints[1]

    wPts.loc[0] = [org.name, org.latitude, org.longitude, 0]

    i = 0
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                i += 1
                wPts.loc[i] = [point.name, point.latitude, point.longitude, itp.getPathLength(wPts.iloc[i - 1]['Lat'],
                                                                                              wPts.iloc[i - 1]['Lng'],
                                                                                              point.latitude,
                                                                                              point.longitude)]

    wPts.loc[i + 1] = [dest.name, dest.latitude, dest.longitude, itp.getPathLength(wPts.iloc[i]['Lat'],
                                                                                   wPts.iloc[i]['Lng'],
                                                                                   dest.latitude,
                                                                                   dest.longitude)]
    return wPts

def splitWaypointsEvenly(wPts, interval):
    finalPts = pd.DataFrame(columns=["Name", "Lat", "Lng", "Distance"])
    finalPts.loc[0] = [wPts.iloc[0]["Name"], wPts.iloc[0]["Lat"], wPts.iloc[0]["Lng"], wPts.iloc[0]["Distance"]]

    dist = 0
    for idx, pt in wPts.iterrows():
        if (idx == len(wPts) - 1):
            finalPts.loc[len(finalPts)] = [pt["Name"], pt["Lat"], pt["Lng"],
                                           itp.getPathLength(finalPts.iloc[len(finalPts) - 1]['Lat'],
                                                             finalPts.iloc[len(finalPts) - 1]['Lng'],
                                                             pt["Lat"],
                                                             pt["Lng"])]
        elif dist + pt["Distance"] < interval:
            dist += pt["Distance"]

        elif dist + pt["Distance"] == interval:
            finalPts.loc[len(finalPts)] = [pt["Name"], pt["Lat"], pt["Lng"],
                                           itp.getPathLength(finalPts.iloc[len(finalPts) - 1]['Lat'],
                                                             finalPts.iloc[len(finalPts) - 1]['Lng'],
                                                             pt["Lat"],
                                                             pt["Lng"])]
            dist = 0
        else:
            subpts = itp.interpolateRoute(1, wPts.iloc[idx - 1]["Lat"], wPts.iloc[idx - 1]["Lng"], pt["Lat"], pt["Lng"])
            nInterval = math.floor(abs(pt["Distance"] + dist) / interval)

            extraPts = ''
            oPtLat = finalPts.iloc[len(finalPts) - 1]['Lat']
            oPtLng = finalPts.iloc[len(finalPts) - 1]['Lng']
            for n in list(range(0, nInterval)):
                if (n + 1) * interval - 1 - dist != len(subpts):
                    ePt = subpts[math.ceil((n + 1) * interval - 1 - dist)]
                    eDist = itp.getPathLength(oPtLat,
                                              oPtLng,
                                              ePt[0],
                                              ePt[1])
                    if (eDist > interval - 3 and eDist < interval + 3):
                        oPtLat = ePt[0]
                        oPtLng = ePt[1]
                        extraPts += str(ePt[0]) + ',' + str(ePt[1]) + '|'
                    elif (eDist < interval - 2):
                        for eePt in subpts[math.ceil((n + 1) * interval - 1 - dist):]:
                            eeDist = itp.getPathLength(oPtLat,
                                                       oPtLng,
                                                       eePt[0],
                                                       eePt[1])
                            if (eeDist > interval - 3 and eeDist < interval + 3):
                                oPtLat = eePt[0]
                                oPtLng = eePt[1]
                                extraPts += str(eePt[0]) + ',' + str(eePt[1]) + '|'
                                break;
                    else:
                        for eePt in subpts[:math.ceil((n + 1) * interval - 1 - dist)]:
                            eeDist = itp.getPathLength(oPtLat,
                                                       oPtLng,
                                                       eePt[0],
                                                       eePt[1])
                            if (eeDist > interval - 3 and eeDist < interval + 3):
                                oPtLat = eePt[0]
                                oPtLng = eePt[1]
                                extraPts += str(eePt[0]) + ',' + str(eePt[1]) + '|'
                                break;
            tpts = str(wPts.iloc[idx - 1]["Lat"]) + ',' + str(wPts.iloc[idx - 1]["Lng"]) + '|' \
                   + extraPts \
                   + str(pt["Lat"]) + ',' + str(pt["Lng"])

            rgPts = gmaps.snap_to_roads(tpts, interpolate=False)

            for n in range(0, nInterval):
                finalPts.loc[len(finalPts)] = ["", rgPts[n + 1]['location']['latitude'],
                                               rgPts[n + 1]['location']['longitude'],
                                               itp.getPathLength(finalPts.iloc[len(finalPts) - 1]['Lat'],
                                                                 finalPts.iloc[len(finalPts) - 1]['Lng'],
                                                                 rgPts[n + 1]['location']['latitude'],
                                                                 rgPts[n + 1]['location']['longitude'])]
            dist = itp.getPathLength(finalPts.iloc[len(finalPts) - 1]['Lat'],
                                     finalPts.iloc[len(finalPts) - 1]['Lng'],
                                     pt["Lat"],
                                     pt["Lng"])
    return finalPts

def writeSplitRoutePoints(gpxFile, ptsFile, interval):
    pts = splitWaypointsEvenly(getWaypointsFromGPX(gpxFile), interval)
    pts.to_csv(path_or_buf=ptsFile, index=False)
