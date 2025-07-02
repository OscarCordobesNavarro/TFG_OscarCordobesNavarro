
import json
import numpy as np

import gurobipy as gp

with open("CPPData.json", "r") as f:
    data = json.load(f)


MaterialUsedForPattern = data["MaterialUsedForPattern"]
P = data["P"]
T = data["T"]
Pattern = data["Pattern"]
Demand = data["Demand"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
TimesPatternUsed = model.addVars(P, name='TimesPatternUsed', vtype=gp.GRB.INTEGER)

# ====== Define constraints ====== 

for t in range(T):
    model.addConstr(gp.quicksum(Pattern[t][p] * TimesPatternUsed[p] for p in range(P)) >= Demand[t], name=f'demand_constraint_type_{t}')

for p in range(P):
    model.addConstr(TimesPatternUsed[p] >= 0, name=f"non_negativity_pattern_{p}")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(MaterialUsedForPattern[p] * TimesPatternUsed[p] for p in range(P)), gp.GRB.MINIMIZE)

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

