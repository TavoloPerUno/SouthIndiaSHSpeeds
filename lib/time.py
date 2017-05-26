import pytz, datetime, time

def getTimeFromEpoch(timeStp, zoneCode):
    local = pytz.timezone (zoneCode)
    naive = datetime.datetime.strptime (timeStp, "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone (pytz.utc)
    return (utc_dt.timestamp())