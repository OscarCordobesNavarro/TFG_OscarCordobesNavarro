
import json
import numpy as np

import gurobipy as gp

with open("tmpData/J8VUD0E3z9Ta9FS8EBXG/data.json", "r") as f:
    data = json.load(f)


Demand = data["Demand"]
N = data["N"]
TravelCost = data["TravelCost"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
Route = model.addVars(C, C, name='Route', vtype=gp.GRB.BINARY)
Depot = model.addVar(name='Depot', vtype=gp.GRB.INTEGER)
VehicleCapacity = model.addVars(N, name='VehicleCapacity', vtype=gp.GRB.CONTINUOUS)

# ====== Define constraints ====== 

for v in range(N):
    model.addConstr(gp.quicksum(Route[Depot, j] for j in range(C)) == 1, name=f"start_at_depot_vehicle_{v}")
    model.addConstr(gp.quicksum(Route[i, Depot] for i in range(C)) == 1, name=f"end_at_depot_vehicle_{v}")
    model.addConstr(gp.quicksum(Route[Depot, j] for j in range(C)) == gp.quicksum(Route[i, Depot] for i in range(C)), name=f"depot_balance_vehicle_{v}")

for i in range(C):
    model.addConstr(gp.quicksum(Route[i, j] for j in range(C)) == Demand[i], name=f'demand_met_{i}')

for i in range(N):
    model.addConstr(gp.quicksum(Route[i, j] * Demand[j] for j in range(C)) <= VehicleCapacity[i], name=f"vehicle_capacity_{i}")

model.setObjective(gp.quicksum(TravelCost[i][j] * Route[i][j] for i in range(C) for j in range(C)), gp.GRB.MINIMIZE)

model.addConstr(gp.quicksum(Route[i, j] for i in range(C) for j in range(C) if i != j) <= N, name="vehicle_limit")

for i in range(C):
    model.addConstr(gp.quicksum(Route[i, j] for j in range(C)) == 1, name=f"visit_once_{i}")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(TravelCost[i, j] * Route[i, j] for i in range(C) for j in range(C)), gp.GRB.MINIMIZE)

# Optimize model
model.optimize()


# Get model status
status = model.status


# Get solver information
solving_info = {}

if status == gp.GRB.OPTIMAL:
    solving_info["status"] = "Optimal (2)"
    solving_info["objective_value"] = model.objVal
    solving_info["variables"] = [
        {
            "symbol": var.VarName,
            "value": var.X,
        }
        for var in model.getVars()
    ]
    solving_info["runtime"] = model.Runtime
    solving_info["iteration_count"] = model.IterCount
else:
    status_dict = {
        gp.GRB.INFEASIBLE: "Infeasible",
        gp.GRB.INF_OR_UNBD: "Infeasible or Unbounded",
        gp.GRB.UNBOUNDED: "Unbounded",
        gp.GRB.OPTIMAL: "Optimal",
    }
    solving_info["status"] = (
        status_dict[model.status] + f" ({model.status})"
        if model.status in status_dict
        else status_dict[model.status]
    )
    solving_info["objective_value"] = None
    solving_info["variables"] = []
    solving_info["runtime"] = None
    solving_info["iteration_count"] = None

