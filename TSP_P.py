import json
import numpy as np
import gurobipy as gp

with open("TSPData.json", "r") as f:
    data = json.load(f)

N = data["N"]
Distance = data["Distance"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
SubtourElimination = model.addVars(N, name='SubtourElimination', vtype=gp.GRB.CONTINUOUS)
TravelDecision = model.addVars(N, N, name='TravelDecision', vtype=gp.GRB.BINARY)

# ====== Define constraints ====== 

for i in range(N):
    model.addConstr(gp.quicksum(TravelDecision[i, j] for j in range(N)) == 1, name=f"visit_each_city_once_from_{i}")

for j in range(N):
    model.addConstr(gp.quicksum(TravelDecision[i, j] for i in range(N)) == 1, name=f"visit_each_city_once_to_{j}")

for i in range(N):
    model.addConstr(TravelDecision[i, i] == 0, name=f"no_self_loop_{i}")

for i in range(N):
    model.addConstr(gp.quicksum(TravelDecision[i, j] for j in range(N)) == 1, name=f"incoming_connection_{i}")

for j in range(N):
    model.addConstr(gp.quicksum(TravelDecision[i, j] for i in range(N)) == 1, name=f"outgoing_connection_{j}")

# model.addConstr(gp.quicksum(SubtourElimination[i] for i in range(N)) <= N - 1, name="subtour_elimination")

# for j in range(N):
#     model.addConstr(gp.quicksum(TravelDecision[i, j] for i in range(N)) == 1)

# for i in range(N):
#     model.addConstr(gp.quicksum(TravelDecision[i, j] for j in range(N)) == 1)

for i in range(N):
    for j in range(N):
        if i != j:
            # model.addConstr(SubtourElimination[j] - SubtourElimination[i] + N * TravelDecision[i, j] >= 1)
            model.addConstr(SubtourElimination[j] - SubtourElimination[i] + N * TravelDecision[i, j] <= N - 1)

# ====== Define objective ====== 

model.setObjective(gp.quicksum(TravelDecision[i, j] * Distance[i][j] for i in range(N) for j in range(N)), gp.GRB.MINIMIZE)

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