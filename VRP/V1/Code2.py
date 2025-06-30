import json
import numpy as np

import gurobipy as gp

with open("Data.json", "r") as f:
    data = json.load(f)


Capacity = data["Capacity"]
Demand = data["Demand"]
N = data["N"]
TravelCost = np.array(data["TravelCost"])  # Convert to numpy array

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
Route = model.addVars(N, N, name='Route', vtype=gp.GRB.BINARY)
NumRoutes = model.addVar(name='NumRoutes', vtype=gp.GRB.INTEGER)
K = model.addVar(name='K', vtype=gp.GRB.INTEGER)

# ====== Define constraints ====== 

for i in range(N):
    model.addConstr(gp.quicksum(Route[i, j] for j in range(N)) == 1, name=f"visit_once_{i}")

model.addConstr(gp.quicksum(Demand[j] * Route[i, j] for i in range(N) for j in range(N)) <= Capacity, name="delivery_capacity")

model.addConstr(gp.quicksum(Route[0, j] for j in range(N)) == 1, name="start_at_depot")
model.addConstr(gp.quicksum(Route[i, 0] for i in range(N)) == 1, name="end_at_depot")

model.addConstr(NumRoutes >= 1, name="positive_num_routes")

for i in range(N):
    for j in range(N):
        model.addConstr(TravelCost[i, j] >= 0, name=f"non_negative_travel_cost_{i}_{j}")

for i in range(N):
    model.addConstr(Demand[i] >= 0, name=f"demand_non_negative_{i}")

model.addConstr(Capacity > 0, name="positive_capacity")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(TravelCost[i, j] * Route[i, j] for i in range(N) for j in range(N)), gp.GRB.MINIMIZE)

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