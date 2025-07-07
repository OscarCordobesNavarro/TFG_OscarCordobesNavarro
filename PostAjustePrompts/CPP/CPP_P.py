import json
import numpy as np
import gurobipy as gp

with open("Data5.json", "r") as f:
    data = json.load(f)

Demand = data["Demand"]
T = data["T"]
P = data["P"]
Pattern = data["Pattern"]
MaterialUsedForPattern = data["MaterialUsedForPattern"]

# Define model
model = gp.Model('model')

# ====== Define variables ====== 
UsageCount = model.addVars(P, name='UsageCount', vtype=gp.GRB.INTEGER)

# ====== Define constraints ====== 

for t in range(T):
    model.addConstr(gp.quicksum(Pattern[p][t] * UsageCount[p] for p in range(P)) >= Demand[t], name=f"demand_met_{t}")

for p in range(P):
    model.addConstr(UsageCount[p] >= 0, name=f"non_negative_usage_{p}")

for p in range(P):
    for t in range(T):
        model.addConstr(Pattern[p][t] >= 0, name=f"non_negativity_pattern_{p}_{t}")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(MaterialUsedForPattern[p] * UsageCount[p] for p in range(P)), gp.GRB.MINIMIZE)

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