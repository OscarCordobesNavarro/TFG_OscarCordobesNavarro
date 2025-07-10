import json
import numpy as np
import gurobipy as gp

with open("Data.json", "r") as f:
    data = json.load(f)

TransportCost = data["TransportCost"]
OpeningCost = data["OpeningCost"]
C = data["C"]
Demand = data["Demand"]
L = data["L"]
Capacity = data["Capacity"]

# Define model
model = gp.Model('model')


# ====== Define variables ====== 
UnitsShipped = model.addVars(L, C, name='UnitsShipped', vtype=gp.GRB.CONTINUOUS)
OpenFacility = model.addVars(L, name='OpenFacility', vtype=gp.GRB.BINARY)

# ====== Define constraints ====== 

for c in range(C):
    model.addConstr(gp.quicksum(UnitsShipped[l, c] for l in range(L)) == Demand[c], name=f"demand_fulfillment_customer_{c}")

for l in range(L):
    model.addConstr(gp.quicksum(UnitsShipped[l, c] for c in range(C)) <= Capacity[l] * OpenFacility[l], name=f"capacity_constraint_{l}")

for l in range(L):
    for c in range(C):
        model.addConstr(UnitsShipped[l, c] <= Demand[c] * OpenFacility[l], name=f"demand_assignment_{l}_{c}")

for l in range(L):
    for c in range(C):
        model.addConstr(UnitsShipped[l, c] >= 0, name=f"non_negative_shipment_{l}_{c}")

for c in range(C):
    model.addConstr(gp.quicksum(UnitsShipped[l, c] for l in range(L)) <= Demand[c], name=f'demand_constraint_{c}')

# ====== Define objective ====== 

model.setObjective(gp.quicksum(OpeningCost[l] * OpenFacility[l] for l in range(L)) + gp.quicksum(TransportCost[l][c] * UnitsShipped[l, c] for l in range(L) for c in range(C)), gp.GRB.MINIMIZE)

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