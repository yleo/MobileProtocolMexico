import math
def distKm(l1, l2):
    lon1 = l1[0]
    lat1 = l1[1]
    lon2 = l2[0]
    lat2 = l2[1]
    lon = lon2-lon1
    lat = lat2-lat1
    
    y = lat*110.54
    x = lon*111.32*math.cos(lat)
    
    return math.sqrt(y*y + x*x)

print distKm((-99.093981, 19.462011), (-99.09321179, 19.44640873))