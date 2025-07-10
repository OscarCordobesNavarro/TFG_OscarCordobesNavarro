import json
import numpy as np

import gurobipy as gp

with open("Data5.json", "r") as f:
    data = json.load(f)


Distance = data["Distance"]
N = data["N"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
X = model.addVars(N, N, name='X', vtype=gp.GRB.BINARY)

# ====== Define constraints ====== 

for i in range(N):
    model.addConstr(gp.quicksum(X[i, j] for j in range(N)) == 1, name=f"visit_once_row_{i}")

for j in range(N):
    model.addConstr(gp.quicksum(X[i, j] for i in range(N)) == 1, name=f"visit_once_col_{j}")

model.addConstr(gp.quicksum(X[i, i] for i in range(N)) == 0, name="no_self_loop")

for j in range(N):
    model.addConstr(gp.quicksum(X[i, j] for i in range(N)) == 1, name=f"incoming_{j}")

for i in range(N):
    model.addConstr(gp.quicksum(X[i, j] for j in range(N) if j != i) == 1, name=f"outgoing_{i}")

from itertools import combinations

for size in range(2, N):
    for subset in combinations(range(N), size):
        model.addConstr(gp.quicksum(X[i, j] for i in subset for j in subset) <= len(subset) - 1, name="subtour_elimination_{}".format(subset))

for i in range(N):
    model.addConstr(X[i, i] == 0, name=f"no_self_loop_{i}")

model.addConstr(N >= 1, name="num_cities_positive")

for i in range(N):
    for j in range(N):
        if i != j:
            model.addConstr(Distance[i][j] >= 0, name=f"non_negative_distance_{i}_{j}")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(Distance[i][j] * X[i, j] for i in range(N) for j in range(N)), gp.GRB.MINIMIZE)

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
        if var['value'] == 1:
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