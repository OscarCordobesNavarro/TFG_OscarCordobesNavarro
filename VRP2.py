import json
import numpy as np
import gurobipy as gp

with open("tmpData/mqhP1toIGVu3Jad8y61P/data.json", "r") as f:
    data = json.load(f)

Distance = data["Distance"]
Q = data["Q"]
N = data["N"]
Demand = data["Demand"]
P = data["P"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
U = model.addVars(N, name='U', vtype=gp.GRB.CONTINUOUS)
X = model.addVars(N, N, P, name='X', vtype=gp.GRB.BINARY)

# ====== Define constraints ====== 

for k in range(P):
    model.addConstr(gp.quicksum(X[0, j, k] for j in range(1, N)) == 1, name=f"departure_from_depot_vehicle_{k}")
    model.addConstr(gp.quicksum(X[i, 0, k] for i in range(1, N)) == 1, name=f"return_to_depot_vehicle_{k}")

for j in range(1, N):
    model.addConstr(gp.quicksum(X[i, j, k] for i in range(N) for k in range(P)) == 1, name=f"visit_once_{j}")

for i in range(1, N):
    for k in range(P):
        model.addConstr(gp.quicksum(X[i, j, k] for j in range(N)) == gp.quicksum(X[j, i, k] for j in range(N)), name=f"flow_conservation_{i}_{k}")

for k in range(P):
    model.addConstr(gp.quicksum(Demand[i] * X[i, j, k] for i in range(1, N) for j in range(N)) <= Q, name=f'vehicle_capacity_{k}')

for i in range(1, N):
    for j in range(1, N):
        for k in range(P):
            if i != j:
                model.addConstr(U[i] - U[j] + (N-1) * X[i, j, k] <= N-2, name=f"subtour_elimination_{i}_{j}_{k}")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(Distance[i][j] * X[i, j, k] for i in range(N) for j in range(N) for k in range(P)), gp.GRB.MINIMIZE)

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