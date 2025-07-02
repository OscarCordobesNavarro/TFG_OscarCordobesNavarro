
import json
import numpy as np

import gurobipy as gp

with open("VRPData.json", "r") as f:
    data = json.load(f)


C = data["C"]
CityDistances = data["CityDistances"]
V = data["V"]
VehicleCapacity = data["VehicleCapacity"]
CityDemand = data["CityDemand"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
Travel = model.addVars(V, C, C, name='Travel', vtype=gp.GRB.BINARY)
u_i = model.addVars(C, name='u_i', vtype=gp.GRB.CONTINUOUS)

# ====== Define constraints ====== 

# for v in range(V):
#     model.addConstr(gp.quicksum(Travel[v, 0, j] for j in range(C)) == 1, name=f"vehicle_{v}_start")
#     model.addConstr(gp.quicksum(Travel[v, j, 0] for j in range(C)) == 1, name=f"vehicle_{v}_end")

for v in range(V):
    model.addConstr(gp.quicksum(Travel[v, 0, j] for j in range(1, C)) == 1, name=f"vehicle_{v}_start")

# Cada vehículo debe regresar al depósito
for v in range(V):
    model.addConstr(gp.quicksum(Travel[v, j, 0] for j in range(1, C)) == 1, name=f"vehicle_{v}_end")

# for i in range(C):
#     model.addConstr(gp.quicksum(Travel[v, i, j] for v in range(V) for j in range(C)) == 1, name=f"visit_once_{i}")

for i in range(1, C):
    model.addConstr(gp.quicksum(Travel[v, j, i] for v in range(V) for j in range(C)) == 1, name=f"visit_once_{i}")

for v in range(V):
    model.addConstr(gp.quicksum(CityDemand[i] * Travel[v, i, j] for i in range(1, C) for j in range(C)) <= VehicleCapacity, name=f"capacity_constraint_veh_{v}")

for v in range(V):
    for i in range(C):
        model.addConstr(gp.quicksum(Travel[v, i, j] for j in range(C)) == gp.quicksum(Travel[v, j, i] for j in range(C)), name=f"flow_conservation_v{v}_i{i}")

for v in range(V):
    for i in range(1, C):
        for j in range(1, C):
            if i != j:
                model.addConstr(u_i[i] - u_i[j] + C * Travel[v, i, j] <= C - 1, name=f"subtour_elimination_{v}_{i}_{j}")

for i in range(C):
    model.addConstr(gp.quicksum(Travel[v, i, j] for v in range(V) for j in range(C)) >= 0, name=f"non_negative_visits_city_{i}")

for v in range(V):
    model.addConstr(gp.quicksum(CityDistances[i][j] * Travel[v, i, j] for i in range(C) for j in range(C)) >= 0, name=f"total_distance_non_negative_v{v}")

for c in range(C):
    model.addConstr(CityDemand[c] >= 0, name=f"demand_non_negative_{c}")

model.addConstr(VehicleCapacity >= 0, name="vehicle_capacity_non_negative")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(Travel[v, i, j] * CityDistances[i][j] for v in range(V) for i in range(C) for j in range(C)), gp.GRB.MINIMIZE)

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

