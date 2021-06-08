from Utils import calculate_kg_required, calculate_m3_required

"""
Below three heuristics are presented, being idea_2 the cheapest and idea_3 the most expensive. 
idea_1 results in a set of routes which would require more vehicle than we have.

ROOM FOR IMPROVEMENT IN THE HEURISTICS:

. All the algorithms are written for two-vehicle fleets and need to be generalized.
. In idea_2 the routes to split could be selected randomly and not just as the last ones
. In idea_3 the selections of vehicles for dividing the giga-tour could be randomized 
. All the construction heuristics could be made feasible through a relocate operator

"""

def naive_solution(vehicles, nodes):
    """
    create routes by assigning customers to an active route as long as the capacity constraint is not violated,
    otherwise the active route is closed and a new route is created with the customer assigned to it.

    :param customer nodes
    :return: list of routes
    """
    routes = list()
    a = 1
    v = vehicles[a]
    routes.append([0])
    load = 0
    volume = 0
    for n in range(1, len(nodes)):

        q = nodes[n]["demand_kg"]
        m3 = nodes[n]["demand_m3"]
        # if the capacity would be exceeded
        if volume + m3 > v["vol capacity"] or load + q > v["max load"]:
            # close active route
            routes[-1].append(0)
            # open new route
            routes.append([0])
            a += 1
            v = vehicles[a]
            load = 0
            volume = 0

        # assign customer to route
        routes[-1].append(n)
        load += q
        volume += m3

    # close active route
    routes[-1].append(0)

    return routes


def idea_1(vehicles, nodes, dist, availability):
    """
    Performs the parallel version of the Clark & Wright Savings Heuristic (Clark & Wright, 1964) to construct a
    solution. First, the savings value  is calculated for all pair of customers (s_ij = c_i0 + c_0j - c_ij).
    Then the solution is initialized by creating a route for each customer, going from
    the depot to the customer and immediately back to the depot.
    Starting with the largest savings s_ij, we test whether the route r_i ending with node i and r_j beginning with
    node j can be merged, and if possible, they are indeed merged. Then we continue with the largest savings value
    until no more merges are possible. The heterogeneity of the fleet is taken into account and the capacity of the
    vehicle is updated when the number of filled routes i s higher than the availability of that vehicle

    step by step explanation is provided in the code

    :return: list of routes
    """
    #  availability of vehicles
    v = [8, 12]
    capacity_kg = 2800
    capacity_vol = 34.80 * 1000
    capacity_over = 0
    min_demand_kg = min(nodes[i]["demand_m3"] for i in nodes)
    min_demand_m3 = min(nodes[i]["demand_kg"] for i in nodes)
    max_demand_kg = max(nodes[i]["demand_m3"] for i in nodes)
    max_demand_m3 = max(nodes[i]["demand_kg"] for i in nodes)

    # parameter to subtract to the vehicle capacity to obtain the level at which the route is to consider full
    # (not possible to add other customers)

    p = 1
    high_demand_kg = (p*min_demand_kg + (1-p)*max_demand_kg)
    high_demand_m3 = (p*min_demand_m3 + (1-p)*max_demand_m3)
    savings = list()
    full_routes = []

    # CALCULATION OF THE SAVINGS AND SORTING OF BEST PAIRINGS (BY DESCENDING SAVING)

    for i in range(1, len(nodes)):
        for j in range(1, len(nodes)):
            if i != j:
                s_ij = dist[(i, 0)]["tot"] + dist[(0, j)]["tot"] - dist[(i, j)]["tot"]
                savings.append((i, j, s_ij))

    savings.sort(key=lambda s: -s[2])

    # CREATE ONE ROUTE FOR EVERY CUSTOMER

    routes = list()
    for i in range(1, len(nodes)):
        routes.append([i])

    # STARTING FROM THE HIGHEST SAVING YOU WOULD GET BY MERGING i AND j, MERGE THE ROUTE THAT STARTS WITH j WITH THE
    # ONE ENDING WITH i IF THE CAPACITY IS ENOUGH

    for (i, j, s_ij) in savings:
        r_i = -1  # route with i at the end
        r_j = -1  # route with j in the beginning
        for r in routes:
            if r[-1] == i:
                r_i = r
            if r[0] == j:
                r_j = r

        # METHOD TO UPDATE THE ROUTE CAPACITY

        if len(v):
            if capacity_over == v[0]:   # if we exceed capacity #(available vehicles of type we are using) times
                capacity_over = 0       # reset the count
                capacity_kg = 883       # update the capacities
                capacity_vol = 5.80 * 1000
                v.pop(0)                # remove the availability for vehicle type we just used

        # check whether there are routes ending with i and starting with j, whether they are not the same route and they
        # are not in the already completed routes (view next steps)

        if r_i != -1 and r_j != -1 and r_i != r_j and r_i not in full_routes and r_j not in full_routes:

            # if the capacity is enough

            if calculate_kg_required(r_i, nodes) + calculate_kg_required(r_j, nodes) <= capacity_kg\
                    and calculate_m3_required(r_i, nodes) + calculate_m3_required(r_j, nodes) <= capacity_vol:

                # combine them
                r_i.extend(r_j)
                routes.remove(r_j)
                # print(routes)

            else:

                # check if the routes that cannot be merged can be considered full

                if r_i not in full_routes and (calculate_kg_required(r_i, nodes) >= capacity_kg - high_demand_kg
                                               or calculate_m3_required(r_i, nodes) >= capacity_vol - high_demand_m3):

                    # append the route to the full routes list

                    full_routes.append(r_i)
                    capacity_over += 1
                    # print("capacity", capacity_over, "i", r_i, "routes", full_routes)
                    # print(capacity_vol, capacity_kg)

                if r_j not in full_routes and (calculate_kg_required(r_j, nodes) >= capacity_kg - high_demand_kg
                                               or calculate_m3_required(r_j, nodes) >= capacity_vol - high_demand_m3):

                    full_routes.append(r_j)
                    capacity_over += 1
                    # print("capacity", capacity_over, "j", r_j, "routes", full_routes)
                    # print(capacity_vol, capacity_kg)

            # if we have more than one vehicle type left

            if len(v) <= 1:
                continue

            # check if we are leaving behind unfilled routes which would exceed the capacity if performed with the
            # lowest capacity vehicles (which we use last)

            filled = []
            not_assigned_kg = 0
            not_assigned_m3 = 0

            # sum the demand of the routes which are not full but are bigger than the capacity of the smallest vehicle

            for r in routes:
                if r not in full_routes and calculate_m3_required(r, nodes) > 5.80 * 1000\
                        and calculate_kg_required(r, nodes) > 883:

                    filled.append(r)

            for r in filled:
                not_assigned_kg += calculate_kg_required(r, nodes)
                not_assigned_m3 += calculate_m3_required(r, nodes)

            # calculate how many vehicles would be needed to cover those routes if put together
            # idea: cane we merge those unfilled routes we left behind with the remaining vehicles?

            not_assigned_routes = max(not_assigned_kg/capacity_kg, not_assigned_m3/capacity_vol)

            # if total vehicles required is bigger than availability -1 --> switch to next vehicle type

            if capacity_over + not_assigned_routes > 7:  # parameter needs to be updated

                # print("Capacity for vehicle type finished, change type", filled, capacity_over)
                capacity_over = 8

    # add the depot node at the beginning and end of the final routes

    for route in routes:
        route.insert(0, 0)
        route.append(0)

    return routes


def idea_2(vehicles, nodes, dist, availability):
    """
    Variation of idea 1.
    All the routes are calculated with the capacity of the first vehicle. Afterwards, all the routes not assignable to
    a vehicle are split in single nodes and the procedure is repeated for the next vehicle type.

    :return: list of routes
    """
    v = 1
    savings = list()
    # s_ij = c_i0 + c_0j - c_ij
    for i in range(1, len(nodes)):
        for j in range(1, len(nodes)):
            if i != j:
                s_ij = dist[(i, 0)]["tot"] + dist[(0, j)]["tot"] - dist[(i, j)]["tot"]
                savings.append((i, j, s_ij))

    savings.sort(key=lambda s: -s[2])

    routes = list()
    for i in range(1, len(nodes)):
        routes.append([i])

    for (i, j, s_ij) in savings:
        r_i = -1  # route with i at the end
        r_j = -1  # route with j in the beginning
        for r in routes:
            if r[-1] == i:
                r_i = r
            if r[0] == j:
                r_j = r

        # check whether there are routes ending with i and starting with j, and they are not the same route
        if r_i != -1 and r_j != -1 and r_i != r_j:

            # check capacity constraint

            if calculate_kg_required(r_i, nodes) + calculate_kg_required(r_j, nodes) <= vehicles[1]["max load"]\
                    and calculate_m3_required(r_i, nodes) + calculate_m3_required(r_j, nodes) <= vehicles[1]["vol capacity"]:

                r_i.extend(r_j)
                routes.remove(r_j)
                # print(routes)
    # """
    #  ##################################### CAPACITY CHECKING --- NEW ##########################################

    # print(routes, "starting solution")

    # checking fleet capacity, we can do it just at the end as only now we know how many routes we have

    if len(routes) > availability[0]:  # if more routes than t1 availability
        over_capacity = routes[-(len(routes)-availability[0]):]  # the undeliverable route is removed
        routes = routes[:(availability[0]-1)]
        over_capacity = [item for items in over_capacity for item in items]  # routes are uncombined
        # print(over_capacity, "not deliverable with t1 vehicles")

        for i in over_capacity:  # recalculating route with t2 capacity
            routes.append([i])
        # print(routes, "before recalculating for vehicle t2")

        for (i, j, s_ij) in savings:
            if i not in over_capacity:
                continue
            if j not in over_capacity:
                continue
            # print(i, j, s_ij)

            r_i = -1  # route with i at the end
            r_j = -1  # route with j in the beginning
            for r in routes:
                if r[-1] == i:
                    r_i = r
                if r[0] == j:
                    r_j = r

            # check whether there are routes ending with i and starting with j, and they are not the same route
            if r_i != -1 and r_j != -1 and r_i != r_j:
                # check capacity constraint
                # print(r_i, r_j)

                if calculate_kg_required(r_i, nodes) + calculate_kg_required(r_j, nodes) <= vehicles[9]["max load"] \
                        and calculate_m3_required(r_i, nodes) + calculate_m3_required(r_j, nodes) <= vehicles[9]["vol capacity"]:   # vehicle number 9 is the first t2

                    r_i.extend(r_j)
                    routes.remove(r_j)
                    # print(routes)
                else:
                    kgc = vehicles[9]["max load"]
                    volc = vehicles[9]["vol capacity"]

                    # print(f" tot weight {calculate_kg_required(r_i, nodes) + calculate_kg_required(r_j, nodes)} "
                    #      f"capacity {kgc}"f" tot vol "
                    #      f"{calculate_m3_required(r_i, nodes) + calculate_m3_required(r_j, nodes)} capacity {volc} ")

    # """

    # add the depot node at the beginning and end of the final routes
    for route in routes:
        route.insert(0, 0)
        route.append(0)

    return routes


def idea_3(vehicles, nodes, dist, availability):
    """
    Giga-tour: one single route is created without capacity constraints. The giga-tour is then divided assigning
    sequentially its customers to a vehicle until the capacity is reached, then to the next and so on.

    :return: list of routes
    """
    v = 1
    savings = list()
    # s_ij = c_i0 + c_0j - c_ij
    for i in range(1, len(nodes)):
        for j in range(1, len(nodes)):
            if i != j:
                s_ij = dist[(i, 0)]["tot"] + dist[(0, j)]["tot"] - dist[(i, j)]["tot"]
                savings.append((i, j, s_ij))

    savings.sort(key=lambda s: -s[2])

    routes = list()
    for i in range(1, len(nodes)):
        routes.append([i])

    for (i, j, s_ij) in savings:
        r_i = -1  # route with i at the end
        r_j = -1  # route with j in the beginning
        for r in routes:
            if r[-1] == i:
                r_i = r
            if r[0] == j:
                r_j = r

        # check whether there are routes ending with i and starting with j, and they are not the same route

        if r_i != -1 and r_j != -1 and r_i != r_j:

            r_i.extend(r_j)
            routes.remove(r_j)

    # print(routes)

    # ############################# DIVIDE GIGA-TOUR FOR AVAILABLE VEHICLES #########################################

    routes_divided = [[0]]
    count = 0
    # kg_cap = 883
    # vol_cap = 5.80 * 1000
    kg_cap = 2800
    vol_cap = 34.80 * 1000

    for x in routes[0]:

        a = routes_divided[count].copy()
        a.append(x)

        if count == 8:
            # kg_cap = 2800
            # vol_cap = 34.80 * 1000
            kg_cap = 883
            vol_cap = 5.80 * 1000

        if calculate_kg_required(a, nodes) <= kg_cap and calculate_m3_required(a, nodes) <= vol_cap:
            routes_divided[count].append(x)

        else:
            count += 1
            routes_divided.append([0])
            routes_divided[count].append(x)

    for route in routes_divided:
        route.append(0)

    return routes_divided
