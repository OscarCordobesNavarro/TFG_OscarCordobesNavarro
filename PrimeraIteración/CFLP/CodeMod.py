import json
import numpy as np
import gurobipy as gp

with open("DataMod.json", "r") as f:
    data = json.load(f)


MaxCapacity = data["MaxCapacity"]
TransportationCost = data["TransportationCost"]
C = data["C"]
CustomerDemand = data["CustomerDemand"]
L = data["L"]
OpeningCost = data["OpeningCost"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
X = model.addVars(L, C, name='X', vtype=gp.GRB.CONTINUOUS)
NumberOfFacilitiesOpened = model.addVar(name='NumberOfFacilitiesOpened', vtype=gp.GRB.INTEGER)
Y = model.addVars(L, name='Y', vtype=gp.GRB.BINARY)
CustomerAssignment = model.addVars(L, C, name='CustomerAssignment', vtype=gp.GRB.INTEGER)

# ====== Define constraints ====== 

for l in range(L):
    model.addConstr(gp.quicksum(X[l, c] for c in range(C)) <= MaxCapacity[l] * Y[l], name=f"capacity_constraint_{l}")
    
for l in range(L):
    for c in range(C):
        model.addConstr(X[l, c] <= CustomerDemand[c] * Y[l], name=f"linking_constraint_{l}_{c}")

for c in range(C):
    model.addConstr(gp.quicksum(X[l, c] for l in range(L)) == CustomerDemand[c], name=f'demand_satisfaction_{c}')

NumberOfFacilitiesOpened = model.addVar(name="NumberOfFacilitiesOpened", vtype=gp.GRB.INTEGER)
model.addConstr(NumberOfFacilitiesOpened == gp.quicksum(Y[l] for l in range(L)), "facility_count_constraint")

for l in range(L):
    for c in range(C):
        model.addConstr(CustomerAssignment[l, c] >= 0, name=f"non_negativity_{l}_{c}")

# ====== Define objective ====== 

model.setObjective(gp.quicksum(OpeningCost[l] * Y[l] for l in range(L)) + gp.quicksum(TransportationCost[l][c] * X[l, c] for l in range(L) for c in range(C)), gp.GRB.MINIMIZE)

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
        for var in model.getVars() if var.X != 0
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