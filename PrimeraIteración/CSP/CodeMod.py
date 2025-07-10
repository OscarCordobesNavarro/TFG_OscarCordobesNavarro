import json
import numpy as np

import gurobipy as gp

with open("DataMod.json", "r") as f:
    data = json.load(f)


T = data["T"]
UnitsProduced = data["UnitsProduced"]
UnitsRequired = data["UnitsRequired"]
P = data["P"]

# MaterialUsedForPattern is now a parameter read from data
MaterialUsedForPattern = data["MaterialUsedForPattern"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
PatternUsageFrequency = model.addVars(P, name='PatternUsageFrequency', vtype=gp.GRB.INTEGER)

# ====== Define constraints ====== 

for t in range(T):
    model.addConstr(gp.quicksum(UnitsProduced[p][t] * PatternUsageFrequency[p] for p in range(P)) >= UnitsRequired[t], name=f'units_requirement_{t}')

for p in range(P):
    model.addConstr(PatternUsageFrequency[p] >= 0, name=f"non_negativity_pattern_{p}")

# Note: Removed redundant constraint as identified in the analysis

# ====== Define objective ====== 

model.setObjective(gp.quicksum(MaterialUsedForPattern[p] * PatternUsageFrequency[p] for p in range(P)), gp.GRB.MINIMIZE)

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

    ## Añadido para mostrar información por consola
    print("----------------- Modelo optimizado con éxito. ---------------")
    print("Estado:", solving_info["status"])
    print("Valor objetivo:", solving_info["objective_value"])
    print("Variables seleccionadas:")
    for var in solving_info["variables"]:
        print(f"  {var['symbol']}: {var['value']}")
    print("Tiempo de ejecución:", solving_info["runtime"])
    print("Iteraciones:", solving_info["iteration_count"])
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
