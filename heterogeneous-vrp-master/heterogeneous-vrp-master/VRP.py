import gurobipy as gp
from gurobipy import *
from Utils import create_tour, create_routes


def solve_VRP(nodes, dist, vehicles, gas_price):
    m = gp.Model("VRP_Baseline")


    ### DECISION VARIABLES
    # x_ijm: indicates whether arc(i,j) is used by vehicle m
    # y_ijm: represents the load delivered from vehicle m to customer j coming from customer i
    # w_ijm: represents the volume delivered from vehicle m to customer j coming from customer i
    # z_im:  indicates whether customer i is served by vehicle m

    x = dict()
    for vehicle in vehicles:
        for node_i in nodes:
            for node_j in nodes:
                x[node_i["id"], node_j["id"], vehicle["id"]] = m.addVar(lb=0.0, ub=1.0, vtype=gp.GRB.BINARY, name=f'RD sub-tour{node_i["id"], node_j["id"]} with vehicle {vehicle["id"]}')
    m.update()

    y = dict()
    for vehicle in vehicles:
        for node_i in nodes:
            for node_j in nodes:
                y[node_i["id"], node_j["id"], vehicle["id"]] = m.addVar(lb=0.0, vtype=gp.GRB.CONTINUOUS, name=f'Load{node_i["id"], node_j["id"]} vehicle {vehicle["id"]}')
    m.update()

    w = dict()
    for vehicle in vehicles:
        for node_i in nodes:
            for node_j in nodes:
                w[node_i["id"], node_j["id"], vehicle["id"]] = m.addVar(lb=0.0, vtype=gp.GRB.CONTINUOUS, name=f'Volume{node_i["id"], node_j["id"]} vehicle {vehicle["id"]}')
    m.update()

    z = dict()
    for vehicle in vehicles:
        for node_i in nodes:
            if node_i["id"]:
                z[node_i["id"], vehicle["id"]] = m.addVar(lb=0.0, ub=1.0, vtype=gp.GRB.BINARY, name=f'Vehicle to customer match{node_i["id"], vehicle["id"]}')
    m.update()


    ### 1- OBJECTIVE FUNCTION

    costs = LinExpr()
    for vehicle in vehicles:
        for node_i in nodes:
            for node_j in nodes:
                index = node_i["id"] * len(nodes) + node_j["id"]
                costs += x[node_i["id"], node_j["id"], vehicle["id"]] * dist[index]["tot"] * gas_price * vehicle["consumption"]

    m.setObjective(costs, sense=gp.GRB.MINIMIZE)
    m.update()

    ### CONSTRAINTS

    # 2- Flow Conservation

    # (2.1) flow conservation for all regular customers
    for vehicle in vehicles:
        for i in range(1, len(nodes)):
            x_ijm = LinExpr()
            x_jim = LinExpr()
            for node in nodes:
                x_ijm += x[i, node["id"], vehicle["id"]]
                x_jim += x[node["id"], i, vehicle["id"]]
            m.addConstr(lhs=x_ijm, sense=gp.GRB.EQUAL, rhs=z[i, vehicle["id"]])
            m.addConstr(lhs=x_jim, sense=gp.GRB.EQUAL, rhs=z[i, vehicle["id"]])
    m.update()

    # (2.2) guarantees that every tour starts and ends at depot
    for vehicle in vehicles:
        x_0jm = LinExpr()
        x_j0m = LinExpr()
        for node in nodes:
            x_0jm += x[0, node["id"], vehicle["id"]]
            x_j0m += x[node["id"], 0, vehicle["id"]]
        sub = x_0jm - x_j0m
        m.addConstr(lhs=sub, sense=gp.GRB.EQUAL, rhs=0)
        m.update()

    # 3- Demand Fulfillment

    # (3.1.1) kg demand fulfillment
    load_carried = LinExpr()
    for vehicle in vehicles:
        for node_i in nodes:
            if node_i["id"] == 0:
                continue
            y_ijm = LinExpr()
            y_jim = LinExpr()
            demandkg_im = node_i["demand_kg"] * z[node_i["id"], vehicle["id"]]
            load_carried += demandkg_im
            for node_j in nodes:
                y_ijm += y[node_i["id"], node_j["id"], vehicle["id"]]
                y_jim += y[node_j["id"], node_i["id"], vehicle["id"]]
            sub = y_jim - y_ijm
            m.addConstr(lhs=sub, sense=gp.GRB.EQUAL, rhs=demandkg_im)

    # (3.1.2) total demand of customers is leaving the depot
    y_ijm = LinExpr()
    y_jim = LinExpr()
    load_carried = load_carried * (-1)
    for vehicle in vehicles:
        for node in nodes:
            y_ijm += y[0, node["id"], vehicle["id"]]
            y_jim += y[node["id"], 0, vehicle["id"]]
    sub = y_jim - y_ijm
    m.addConstr(lhs=sub, sense=gp.GRB.EQUAL, rhs=load_carried)
    m.update()

    # (3.2.1) volume demand fulfillment
    volume_carried = LinExpr()
    for vehicle in vehicles:
        for node_i in nodes:
            if node_i["id"] == 0:
                continue
            w_ijm = LinExpr()
            w_jim = LinExpr()
            demandm3_im = node_i["demand_m3"] * z[node_i["id"], vehicle["id"]]
            volume_carried += demandm3_im
            for node_j in nodes:
                w_ijm += w[node_i["id"], node_j["id"], vehicle["id"]]
                w_jim += w[node_j["id"], node_i["id"], vehicle["id"]]
            sub = w_jim - w_ijm
            m.addConstr(lhs=sub, sense=gp.GRB.EQUAL, rhs=demandm3_im)

    # (3.2.2) total demand of customers is leaving the depot
    w_ijm = LinExpr()
    w_jim = LinExpr()
    volume_carried = volume_carried * (-1)
    for vehicle in vehicles:
        for node in nodes:
            w_ijm += w[0, node["id"], vehicle["id"]]
            w_jim += w[node["id"], 0, vehicle["id"]]
    sub = w_jim - w_ijm
    m.addConstr(lhs=sub, sense=gp.GRB.EQUAL, rhs=volume_carried)
    m.update()

    # 4- Capacity

    # (4.1) load
    for vehicle in vehicles:
        load = LinExpr()
        for node_i in nodes:
            for node_j in nodes:
                load += y[node_i["id"], node_j["id"], vehicle["id"]]
                capacity_kg = vehicle["max load"]
        m.addConstr(lhs=load, sense=gp.GRB.LESS_EQUAL, rhs=capacity_kg)
    m.update()

    # (4.2) volume
    for vehicle in vehicles:
        volume = LinExpr()
        for node_i in nodes:
            for node_j in nodes:
                volume += w[node_i["id"], node_j["id"], vehicle["id"]]
                capacity_m3 = vehicle["vol capacity"]
        m.addConstr(lhs=volume, sense=gp.GRB.LESS_EQUAL, rhs=capacity_m3)
    m.update()

    # 5- vehicle returns empty to the depot

    # (5.1) load

    for vehicle in vehicles:
        for node in nodes:
            final_load = y[node["id"], 0, vehicle["id"]]
            m.addConstr(lhs=final_load, sense=gp.GRB.EQUAL, rhs=0)
    m.update()

    # (5.2) volume

    for vehicle in vehicles:
        for node in nodes:
            final_volume = w[node["id"], 0, vehicle["id"]]
            m.addConstr(lhs=final_volume, sense=gp.GRB.EQUAL, rhs=0)
    m.update()



    # 6- each customer is served once

    # (6)

    for node in nodes:
        if node["id"] == 0:
            continue
        delivery = LinExpr()
        for vehicle in vehicles:
            delivery += z[node["id"], vehicle["id"]]
        m.addConstr(lhs=delivery, sense=gp.GRB.EQUAL, rhs=1)
    m.update()

    m.optimize()

    if m.Status == gp.GRB.OPTIMAL:
        """arcs_used = dict()
        for node_i, node_j, vehicle in x:
            arcs_used[node_i, node_j, vehicle] = (x[node_i, node_j, vehicle].X >= m.params.IntFeasTol)
        #interim_solution = create_tour(arcs_used)
        #solution = create_routes(interim_solution)

        used_vehicles = list()
        for node in nodes:
            for vehicle in vehicles:
                if z[node["id"], vehicle["id"]].X >= m.params.IntFeasTol:
                    used_vehicles.append(vehicle["id"])
                    continue
"""
        return m.ObjVal #, arcs_used, used_vehicles

    elif m.Status == gp.GRB.INFEASIBLE:
        message_1 = 'Model is infeasible'
        return message_1

    else:
        message_2 = 'Model could not be solved to optimality'
        return message_2