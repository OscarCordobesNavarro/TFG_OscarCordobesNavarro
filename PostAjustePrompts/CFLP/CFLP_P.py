import json
import numpy as np
import gurobipy as gp

with open("Data5.json", "r") as f:
    data = json.load(f)

TransportCost = data["TransportCost"]
OpeningCost = data["OpeningCost"]
Demand = data["Demand"]
C = data["C"]
Capacity = data["Capacity"]
L = data["L"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
OpenFacility = model.addVars(L, name='OpenFacility', vtype=gp.GRB.BINARY)
UnitsShipped = model.addVars(L, C, name='UnitsShipped', vtype=gp.GRB.CONTINUOUS)

# ====== Define constraints ====== 

for c in range(C):
    model.addConstr(gp.quicksum(UnitsShipped[l, c] for l in range(L)) == Demand[c], name=f"demand_constraint_c{c}")

for l in range(L):
    model.addConstr(gp.quicksum(UnitsShipped[l, c] for c in range(C)) <= Capacity[l] * OpenFacility[l], name=f"capacity_constraint_{l}")

for l in range(L):
    for c in range(C):
        model.addConstr(UnitsShipped[l, c] <= Demand[c] * OpenFacility[l], name=f"demand_assignment_{l}_{c}")

for l in range(L):
    model.addConstr(OpenFacility[l] <= 1, name=f"OpenFacility_once_{l}")

for l in range(L):
    for c in range(C):
        model.addConstr(UnitsShipped[l, c] >= 0, name=f"non_negativity_{l}_{c}")

model.addConstr(gp.quicksum(OpenFacility[l] for l in range(L)) <= L, name="facility_open_once")

# Ensure TransportCost is non-negative (assuming it's a numpy array or a list of lists)
TransportCost = np.array(TransportCost)
for l in range(L):
    for c in range(C):
        assert TransportCost[l, c] >= 0, f"TransportCost[{l}, {c}] is negative!"

# ====== Define objective ====== 

model.setObjective(gp.quicksum(OpeningCost[l] * OpenFacility[l] for l in range(L)) + gp.quicksum(TransportCost[l, c] * UnitsShipped[l, c] for l in range(L) for c in range(C)), gp.GRB.MINIMIZE)

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

    # Mostrar información detallada por consola
    print("----------------- Modelo optimizado con éxito. ---------------")
    print("Estado:", solving_info["status"])
    print("Valor objetivo:", solving_info["objective_value"])
    print("Tiempo de ejecución:", solving_info["runtime"])
    print("Iteraciones:", solving_info["iteration_count"])
    print("\nVariables seleccionadas (valor distinto de 0):")
    for var in solving_info["variables"]:
        if var['value'] != 0:
            print(f"  {var['symbol']}: {var['value']}")
    print("\nResumen de instalaciones abiertas:")
    for var in solving_info["variables"]:
        if var['symbol'].startswith("OpenFacility") and var['value'] > 0.5:
            print(f"  {var['symbol']} abierta")
    print("\nResumen de unidades enviadas:")
    for var in solving_info["variables"]:
        if var['symbol'].startswith("UnitsShipped") and var['value'] > 0:
            print(f"  {var['symbol']}: {var['value']}")
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