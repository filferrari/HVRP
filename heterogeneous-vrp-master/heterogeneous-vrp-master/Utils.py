from typing import Dict, List, Tuple



node = int
Arc = Tuple[int, int]


def create_tour(arcs: Dict[Arc, bool]) -> List[node]:
    nodes = sorted(set([customer_i for (customer_i, customer_j) in arcs]))
    #print(nodes)

    successors = [[]]
    while len(successors) < len(nodes):
        successors.append([])
    for (i,j) in arcs.keys():
        if arcs[i,j] == True:
            successors[i] += [j]
    #print("successors: ", successors)

    length_succ = 0
    for i in successors:
        length_succ += len(i)
    #print(length_succ)

    first_node = 0
    tour = [first_node]

    while len(tour) < length_succ:
        next_node = successors[first_node].pop(0)
        tour.append(next_node)
        first_node = next_node
    return tour


def create_routes(tour: List[int]) -> List[List[int]]:
    routes = list()
    routes.append([0])
    tour.remove(0)
    #print(routes)
    #print(tour)
    while len(tour) != 0:
        if tour[0] != 0:
            routes[-1].append(tour[0])
            tour.pop(0)
        else:
            routes[-1].append(0)
            tour.pop(0)
            routes.append([0])
        #print(len(tour))
    routes[-1].append(0)
    return routes


def calculate_kg_required(route, nodes):

    kg = 0
    for r_i in route:
        kg += nodes[r_i]["demand_kg"]
    return kg


def calculate_m3_required(route, nodes):

    m3 = 0
    for r_i in route:
        m3 += nodes[r_i]["demand_m3"]
    return m3


def solution_cost(routes, dist, vehicle_consumption, gas_price):

    sol_distance = list()
    for route in routes:
        route_distance = 0
        for i in range(1, len(route)):
            route_distance += dist[(route[i-1], route[i])]["tot"]
        sol_distance.append(route_distance)

    # print(sol_distance)

    # compute costs
    sol_cost = sol_distance.copy()

    for i in range(len(sol_distance)):
        sol_cost[i] = sol_cost[i] * vehicle_consumption * gas_price

    return sum(sol_cost)


def compute_distance(route, dist):

    distance = 0

    for i in range(len(route) - 1):

        distance += dist[(route[i], route[i + 1])]["tot"]

    return distance


def divide_routes(routes, nodes):

    number_t1 = 0
    number_t2 = 0

    routes_t1 = []
    routes_t2 = []
    for i in routes:
        if calculate_kg_required(i, nodes) > 883 or calculate_m3_required(i, nodes) > 5.80 * 1000:
            number_t1 += 1
            routes_t1.append(i)
        else:
            number_t2 += 1
            routes_t2.append(i)

    return routes_t1, routes_t2