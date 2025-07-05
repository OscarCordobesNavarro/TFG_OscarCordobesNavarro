import json
import numpy as np

import gurobipy as gp

with open("Data4.json", "r") as f:
    data = json.load(f)


BinCapacity = data["BinCapacity"]
N = data["N"]
ItemSizes = data["ItemSizes"]

# Define the number of bins
B = N

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
ItemInBin = model.addVars(N, B, name='ItemInBin', vtype=gp.GRB.BINARY)
BinUsed = model.addVars(B, name='BinUsed', vtype=gp.GRB.BINARY)
TotalBinsUsed = model.addVar(name='TotalBinsUsed', vtype=gp.GRB.INTEGER)

# ====== Define constraints ====== 

for b in range(B):
    model.addConstr(gp.quicksum(ItemSizes[i] * ItemInBin[i, b] for i in range(N)) <= BinCapacity * BinUsed[b], name=f"bin_capacity_{b}")

for i in range(N):
    model.addConstr(gp.quicksum(ItemInBin[i, b] for b in range(B)) == 1, name=f"assign_item_{i}_to_one_bin")

for i in range(N):
    model.addConstr(ItemSizes[i] >= 0, name=f"non_negativity_item_{i}")

model.addConstr(gp.quicksum(BinUsed[b] for b in range(B)) >= 0, name="non_negative_bins_used")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(BinUsed[b] for b in range(B)), gp.GRB.MINIMIZE)

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
    total_size = 0
    for var in solving_info["variables"]:
        if var['value'] == 1 and var['symbol'].startswith("ItemInBin"):
            # Extraer el índice del item
            parts = var['symbol'].split('[')[1].split(']')[0].split(',')
            item_idx = int(parts[0])
            total_size += ItemSizes[item_idx]
            print(f"  {var['symbol']}: {var['value']}")
    print("Tiempo de ejecución:", solving_info["runtime"])
    print("Iteraciones:", solving_info["iteration_count"])
    print("Suma total de los tamaños de los items asignados:", total_size)
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