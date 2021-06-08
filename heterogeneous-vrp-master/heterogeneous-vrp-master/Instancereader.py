import pandas as pd


def read_nodes(filename):
    nodes = dict()
    locations = pd.read_excel(filename, sheet_name="Locations")
    lo = locations.values.tolist()

    # Customers
    c = len(lo)-1

    # Nodes
    for i in range(len(lo)):
        lon = lo[i][1]
        lat = lo[i][2]
        demand_kg = lo[i][3]
        demand_m3= lo[i][4]
        duration = lo[i][5]
        nodes[i] = {"lon": lon, "lat": lat, "demand_kg": demand_kg, "demand_m3": demand_m3, "duration": duration}
        #nodes.append({"id": i, "lon": lon, "lat": lat, "demand_kg": demand_kg, "demand_m3": demand_m3, "duration": duration})



    return {'c': c, 'nodes': nodes}

def read_distances(filename, c):
    distances = dict()
    dist = pd.read_excel(filename, sheet_name="Routes")
    d = dist.values.tolist()
    ii = 0
    j = 0

    for i in range(len(d)):

        a = i//c
        b = i%c

        tot = d[i][2]
        inside =  d[i][3]
        outside = d[i][4]
        duration = d[i][5]
        distances[(a, b)] = {"tot": tot, "inside": inside, "outside": outside, "duration": duration}
        #distances.append({"from": a, "to": b, "tot": tot, "inside": inside, "outside": outside, "duration": duration})

    return distances
