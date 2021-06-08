def savings_algorithm(vehicles, nodes, dist, availability):
    """
    Performs the parallel version of the Clark & Wright Savings Heuristic (Clark & Wright, 1964) to construct a
    solution. First, the savings value  is calculated for all pair of customers (s_ij = c_i0 + c_0j - c_ij).
    Then the solution is initialized by creating a route for each customer, going from
    the depot to the customer and immediately back to the depot.
    Starting with the largest savings s_ij, we test whether the route r_i ending with node i and r_j beginning with
    node j can be merged, and if possible, they are indeed merged. Then we continue with the largest savings value
    until no more merges are possible.

    :param instance: corresponding instance
    :return: list of routes
    """
    v =1
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

                # How should we consider the maximum capacity here?
                # combine them
                r_i.extend(r_j)
                routes.remove(r_j)
                # print(routes)
    #"""
    # CAPACITY CHECKING --- NEW
    print(routes, "starting solution")
    # checking fleet capacity, we can do it just at the end as only now we know how many routes we have
    if len(routes) > availability[0]:  # if more routes than t1 availability
        over_capacity = routes[-(len(routes)-availability[0]):]  # the undeliverable route is removed
        routes = routes[:(availability[0]-1)]
        over_capacity = [item for items in over_capacity for item in items]
        print(over_capacity, "not deliverable with t1 vehicles")
        for i in over_capacity:  # recalculating route with t2 capacity
            routes.append([i])
        print(routes, "before recalculating for vehicle t2")
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
                print(r_i, r_j)

                if calculate_kg_required(r_i, nodes) + calculate_kg_required(r_j, nodes) <= vehicles[9]["max load"] \
                        and calculate_m3_required(r_i, nodes) + calculate_m3_required(r_j, nodes) <= vehicles[9]["vol capacity"]:   # vehicle number 9 is the first t2

                    r_i.extend(r_j)
                    routes.remove(r_j)
                    # print(routes)
                else:
                    kgc=vehicles[9]["max load"]
                    volc=vehicles[9]["vol capacity"]
                    print(f" tot weight {calculate_kg_required(r_i, nodes) + calculate_kg_required(r_j, nodes)} capacity {kgc}"
                          f" tot vol {calculate_m3_required(r_i, nodes) + calculate_m3_required(r_j, nodes)} capacity {volc} ")


    #"""
    # add the depot node at the beginning and end of the final routes
    for route in routes:
        route.insert(0, 0)
        route.append(0)

    return routes
