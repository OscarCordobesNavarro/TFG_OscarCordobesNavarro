import json
import numpy as np
import gurobipy as gp

with open("tmpData/TOgiUg9UEwARe4GSn3mI/data.json", "r") as f:
    data = json.load(f)

C = data["C"]
TravelCost = data["TravelCost"]
M = data["M"]

# Define N as the number of cities, assuming N should be equal to C
N = C

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
Route = model.addVars(M, N, N, name='Route', vtype=gp.GRB.BINARY)

# ====== Define constraints ====== 

# Eliminada no sentido
for i in range(M):
    model.addConstr(gp.quicksum(Route[i, j, j] for j in range(C)) == 2, name=f"route_start_end_{i}")

# Eliminada
for j in range(C):
    model.addConstr(gp.quicksum(Route[i, j, k] for i in range(M) for k in range(C)) == 1, name=f"visit_city_{j}")

# Eliminada redundante
for j in range(C):
    model.addConstr(gp.quicksum(Route[i, j, k] for i in range(M) for k in range(C)) == 1, name=f"visit_city_{j}")

# Mejorada
for i in range(M):
    for j in range(C):
        model.addConstr(gp.quicksum(Route[i, j, k] for k in range(C)) == gp.quicksum(Route[i, k, j] for k in range(C)), name=f"route_balance_{i}_{j}")

# Eliminada no sentido
model.addConstr(gp.quicksum(Route[i,j,k] for i in range(M) for j in range(C) for k in range(C)) <= M, name="vehicle_limit")

# Redundate
for j in range(C):
    for k in range(C):
        model.addConstr(TravelCost[j][k] >= 0, name=f"non_negativity_travel_cost_{j}_{k}")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(TravelCost[j][k] * Route[i, j, k] for i in range(M) for j in range(C) for k in range(C)), gp.GRB.MINIMIZE)

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