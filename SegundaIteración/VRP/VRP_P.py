import json
import numpy as np
import gurobipy as gp

# Load data
with open("Data5.json", "r") as f:
    data = json.load(f)

M = data["M"]
Distance = data["Distance"]
N = data["N"]

# Define model
model = gp.Model('model')

# ====== Define variables ====== 
Travel = model.addVars(N, N, name='Travel', vtype=gp.GRB.BINARY)

# ====== Define constraints ====== 

model.addConstr(gp.quicksum(Travel[0, j] for j in range(1, N)) == M, name="vehicles_leave_depot")

model.addConstr(gp.quicksum(Travel[j, 0] for j in range(1, N)) == M, name="vehicles_enter_depot")

for j in range(1, N):
    model.addConstr(gp.quicksum(Travel[i, j] for i in range(N)) == 1, name=f"customer_{j}_visit")

for i in range(1, N):  # Adjusted to start from 1 to N-1
    model.addConstr(gp.quicksum(Travel[i, j] for j in range(N)) == 1, name=f"customer_{i}_vehicle_leave")

for i in range(N):
    model.addConstr(Travel[i, i] == 0, name=f"no_self_loop_{i}")

from itertools import combinations

# Subtour elimination constraints should be carefully considered
for size in range(2, N):
    for S in combinations(range(1, N), size):  # Start from 1 to ignore the depot
        model.addConstr(gp.quicksum(Travel[i, j] for i in S for j in S) <= len(S) - 1, name=f"subtour_elimination_{S}")

# Remove unnecessary non-negativity constraints for distances

# ====== Define objective ====== 

model.setObjective(gp.quicksum(Distance[i][j] * Travel[i, j] for i in range(N) for j in range(N)), gp.GRB.MINIMIZE)

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
        for var in model.getVars() if var.x == 1
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