
import json
import numpy as np

import gurobipy as gp

with open("Data3.json", "r") as f:
    data = json.load(f)


MaxCapacity = data["MaxCapacity"]
Weights = data["Weights"]
N = data["N"]
Values = data["Values"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
X = model.addVars(N, name='X', vtype=gp.GRB.BINARY)

# ====== Define constraints ====== 

model.addConstr(gp.quicksum(Weights[i] * X[i] for i in range(N)) <= MaxCapacity, name="weight_capacity")

for i in range(N):
    model.addConstr(X[i] >= 0, name=f"non_negativity_{i}")

model.addConstr(gp.quicksum(Weights[i] * X[i] for i in range(N)) <= MaxCapacity, name="weight_capacity")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(Values[i] * X[i] for i in range(N)), gp.GRB.MAXIMIZE)

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

