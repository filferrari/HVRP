import Instancereader
import Construction
from Utils import *
from Plot import draw_routes
from Improvement import *
from statistics import *
import VRP


# (1) read instance data
# NYC1 contains just the high demand customers, NYC contains all

instance = "NYC.xlsx"

data = Instancereader.read_nodes(instance)
nodes = data["nodes"]
C = data["c"]

# print(nodes, "\n")

dist = Instancereader.read_distances(instance, C +1)
# print(dist, "\n")

# (2) vehicles

# TO BE UPDATED
gas_price = 0.63

# LIST HERE ALL THE VEHICLES TO BE USED
t1 = {"model": "t1", "vol capacity": 34.80 * 1000, "max load": 2800, "consumption": 0.175}
t2 = {"model": "t2", "vol capacity": 5.80 * 1000, "max load": 883, "consumption": 0.08}

# CREATION OF VEHICLE DICTIONARY; ONE ENTRY FOR EVERY VEHICLE

models = [t1, t2]
availability = [8, 12]

vehicles = dict()
id = 1

for i in range(len(models)):
    for j in range(availability[i]):
        vehicles[id] = models[i].copy()
        id += 1

# print(vehicles, "\n")

# NAIVE SOLUTION - JUST IGNORE
"""
routes = naive_solution(vehicles, nodes)
print(routes)

naive_cost = solution_cost(routes, dist, vehicles, gas_price)
print(naive_cost)

draw_routes(routes, nodes)
"""

# CONSTRUCTION HEURISTICS
# CHOOSE BETWEEN IDEA_1, _2 AND _3

routes = Construction.idea_2(vehicles, nodes, dist, availability)

print("\n number of routes", len(routes))

# DIVISION OF ROUTES BY VEHICLE

# function to be made scalable, maybe return list of lists and divide later

routes_t1, routes_t2 = divide_routes(routes, nodes)

# CALCULATION OF SOLUTION COST - TO BE IMPROVED
cost_t1 = solution_cost(routes_t1, dist, t1["consumption"], gas_price)
cost_t2 = solution_cost(routes_t2, dist, t2["consumption"], gas_price)
print("\n total cost of solution", cost_t1 + cost_t2)
print("\n routes t1", len(routes_t1), routes_t1, "\n routes t2", len(routes_t2), routes_t2)


# RANDOM CAPACITY CHECK - USED FOR TESTING
# print(calculate_kg_required(routes_t2[-3], nodes), calculate_m3_required(routes_t2[-3], nodes), routes_t2[-3])

# VRP solution - CAN BE IGNORED
"""
solution = VRP.solve_VRP(nodes, dist, vehicles, gas_price)

if type(solution) == str:
    print(solution)
else:
    costs = solution #, routes, used_vehicles = solution

    print("cost of solution :", costs)
    #print("used vehicles :", used_vehicles)
    #print("tours :", tours)
"""

# ######################################## IMPROVEMENTS #####################################################

# routes = hillclimbing(routes, dist, nodes)
routes = vnd(routes, dist, nodes)

# DIVISION OF ROUTES BY VEHICLE

routes_t1, routes_t2 = divide_routes(routes, nodes)  # function to be made scalable, maybe return list of lists and divide later

# CALCULATION OF SOLUTION COST - TO BE IMPROVED
cost_t1 = solution_cost(routes_t1, dist, t1["consumption"], gas_price)
cost_t2 = solution_cost(routes_t2, dist, t2["consumption"], gas_price)
print("\n total cost of solution", cost_t1 + cost_t2)
print("\n routes t1", len(routes_t1), routes_t1, "\n routes t2", len(routes_t2), routes_t2)
print("\n number of routes", len(routes))

# PLOTTING SOLUTION
draw_routes(routes, nodes)
