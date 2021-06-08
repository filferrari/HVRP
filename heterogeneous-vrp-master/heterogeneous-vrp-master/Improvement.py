# Procedures to improve complete solutions
from Utils import *


def hillclimbing(solution, dist, nodes):
    """
    simple improvement procedure which tries to find a (local) optima by continuously calling
    find_first_improvement_2Opt(solution, instance) until no further improvements are found.
    :param solution: list of routes to improve
    :param dist: distance between nodes
    :param nodes: info about customers
    :return: the provided solution or an improved solution
    """
    improved = True
    while improved:
        improved, solution = find_first_improvement_2Opt(solution, dist)
        # improved, solution = find_first_improvement_relocate(solution, dist, nodes)
        # improved, solution = find_first_improvement_exchange(solution, dist, nodes)

    return solution


def vnd(solution, dist, nodes):
    """
    Variable Neighborhood Decent procedure, searching three neighborhoods (2opt, relocate, exchange) in a structured
    way. Neighborhoods are ordered, if an improvement was found, the search continues from the first neighborhood.
    Otherwise the next neighborhood in order is searched. This continues until no improvements can be found.
    :param solution: list of routes to improve
    :param dist: distance between nodes
    :param nodes: info about customers
    :return: the provided solution or an improved solution
    """
    improved = True
    while improved:
        improved, solution = find_first_improvement_2Opt(solution, dist)
        if not improved:
            improved, solution = find_first_improvement_relocate(solution, dist, nodes)
            if not improved:
                improved, solution = find_first_improvement_exchange(solution, dist, nodes)

    return solution


def find_first_improvement_relocate(solution, dist, nodes):
    """
    search for the first improving relocate
    Example: [[0,1,2,0],[0,3,4,5,0]] => [[0,1,3,2,0],[0,4,5,0]]
        A relocate move could be to move customer 3 between 1 and 2.
    :param solution: list of routes to improve
    :param dist: distance between nodes
    :param nodes: info about customers
    :return: (True, S') if an improvement was found alongside the improved solution S'.
        Otherwise (False, S), with the original solution S.
    """

    # TODO: apply improvements from the exchange neighborhood here as well

    for r1_id, route1 in enumerate(solution):
        current_distance_r1 = compute_distance(route1, dist)
        for i in range(1, len(route1) - 2):

            for r2_id, route2 in enumerate(solution):

                # checking the capacity for the route - to make scalable

                if calculate_m3_required(route2, nodes) > 5.80 * 1000 or calculate_kg_required(route2, nodes) > 883:
                    capacity_kg = 2800
                    capacity_m3 = 34.80 * 1000
                else:
                    capacity_kg = 883
                    capacity_m3 = 5.80 * 1000

                if r1_id == r2_id:
                    # no intra route optimization
                    # TODO: implement case for intra route optimization
                    continue

                current_distance_r2 = compute_distance(route2, dist)

                for j in range(1, len(route2) - 1):
                    # check capacity constraint for r2
                    if calculate_m3_required(route2, nodes) + nodes[route1[i]]["demand_m3"] > capacity_m3 and \
                            calculate_kg_required(route2, nodes) + nodes[route1[i]]["demand_kg"] > capacity_kg:

                        # this move lead to an infeasible solution, just continue
                        continue

                    new_r1 = route1[:i] + route1[i + 1:]
                    new_r2 = route2[:j] + [route1[i]] + route2[j:]

                    change_in_r1 = compute_distance(new_r1, dist) - current_distance_r1
                    change_in_r2 = compute_distance(new_r2, dist) - current_distance_r2

                    if change_in_r1 + change_in_r2 < -0.000001:
                        solution[r1_id] = new_r1
                        solution[r2_id] = new_r2
                        return True, solution

    return False, solution


def find_first_improvement_exchange(solution, dist, nodes):
    """
    search for the first improving exchange
    Example: [[0,1,2,0],[0,3,4,5,0]] => [[0,4,2,0],[0,3,1,5,0]]
        A exchange move could be to swap customer 4 between 1.
    :param solution: list of routes to improve
    :param dist: distance between nodes
    :param nodes: info about customers
    :return: (True, S') if an improvement was found alongside the improved solution S'.
        Otherwise (False, S), with the original solution S.
    """

    current_demand_kg = [0] * len(solution)
    current_demand_m3 = [0] * len(solution)
    for r_id, route in enumerate(solution):

        current_demand_kg[r_id] = calculate_kg_required(route, nodes)
        current_demand_m3[r_id] = calculate_m3_required(route, nodes)

    for r1_id, route1 in enumerate(solution):

        if current_demand_m3[r1_id] > 5.80 * 1000 or current_demand_kg[r1_id] > 883:
            capacity_kg_1 = 2800
            capacity_m3_1 = 34.80 * 1000
        else:
            capacity_kg_1 = 883
            capacity_m3_1 = 5.80 * 1000

        for i in range(1, len(route1) - 2):

            # TODO: remove symmetry in the neighborhood - each pair exchange is tested twice!

            for r2_id, route2 in enumerate(solution):

                if current_demand_m3[r2_id] > 5.80 * 1000 or current_demand_kg[r2_id] > 883:
                    capacity_kg_2 = 2800
                    capacity_m3_2 = 34.80 * 1000
                else:
                    capacity_kg_2 = 883
                    capacity_m3_2 = 5.80 * 1000

                if r1_id == r2_id:
                    # no intra route optimization for now
                    # TODO: implement case for intra route optimization
                    continue

                for j in range(1, len(route2) - 2):
                    # check capacity constraint for r2
                    if current_demand_kg[r1_id] - nodes[route1[i]]["demand_kg"] + nodes[route2[j]]["demand_kg"] > capacity_kg_1 or \
                            current_demand_m3[r1_id] - nodes[route1[i]]["demand_m3"] + nodes[route2[j]]["demand_m3"] > capacity_m3_1:

                        # this move lead to an infeasible solution, just continue
                        continue

                    # check capacity constraint for r2
                    if current_demand_kg[r2_id] - nodes[route2[j]]["demand_kg"] + nodes[route1[i]]["demand_kg"] > capacity_kg_2 or \
                            current_demand_m3[r2_id] - nodes[route2[j]]["demand_m3"] + nodes[route1[i]]["demand_m3"] > capacity_m3_2:
                        # this move lead to an infeasible solution, just continue
                        continue

                    # Example:
                    # i=1 v       j=3 v
                    # [[0,1,2,0],[0,3,4,5,0]] => [[0,4,2,0],[0,3,1,5,0]]
                    # r1: remove: (0,1),(1,2), add: (0,4),(4,2)
                    change_in_r1 = - dist[(route1[i - 1], route1[i])]["tot"] \
                                   - dist[(route1[i], route1[i + 1])]["tot"] \
                                   + dist[(route1[i - 1], route2[j])]["tot"] \
                                   + dist[(route2[j], route1[i + 1])]["tot"]
                    # r2: remove: (3,4),(4,5), add: (3,1),(1,5)
                    change_in_r2 = - dist[(route2[j - 1], route2[j])]["tot"] \
                                   - dist[(route2[j], route2[j + 1])]["tot"] \
                                   + dist[(route2[j - 1], route1[i])]["tot"] \
                                   + dist[(route1[i], route2[j + 1])]["tot"]

                    if change_in_r1 + change_in_r2 < -0.000001:
                        solution[r1_id] = route1[:i] + [route2[j]] + route1[i + 1:]
                        solution[r2_id] = route2[:j] + [route1[i]] + route2[j + 1:]
                        return True, solution

    return False, solution


def find_first_improvement_2Opt(solution, dist):
    """
    search for the first improving 2-opt move.
    A 2-opt consist of removing two edges and reconnecting the nodes differently but feasible way.
    In other terms, a consecutive subset of visits is reversed.

    Example: [0,1,2,3,4,5,0] => [0,1,4,3,2,5,0]
        A 2-opt could be removing edges between 1-2 and 4-5, and connecting 1-4 and 2-5.

    :param solution: list of routes to improve
    :param dist: distance between nodes
    :return: (True, S') if an improvement was found alongside the improved solution S'.
        Otherwise (False, S), with the original solution S.
    """

    # TODO: apply improvements from the exchange neighborhood here as well

    for r_id, route in enumerate(solution):
        current_distance = compute_distance(route, dist)
        # [0, 1, 2, .., 9, 0]
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                if i == 1 and j == len(route) - 2:
                    continue

                # we do not need to check the capacity constraint
                # as no customer is added = demand does not change

                new_route = route[:i] + list(reversed(route[i:j + 1])) + route[j + 1:]

                new_distance = compute_distance(new_route, dist)

                if new_distance - current_distance < -0.000001:
                    solution[r_id] = new_route
                    return True, solution

    return False, solution
