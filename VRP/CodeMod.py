import json
import numpy as np
import gurobipy as gp

with open("Data.json", "r") as f:
    data = json.load(f)

C = data["C"]
TravelCost = data["TravelCost"]
M = data["M"]

# Define N as the number of cities, assuming N should be equal to C
N = C
# Define depot as city 0
DEPOT = 0

# Define model
model = gp.Model('VRP_Model')

# ====== Define variables ====== 
# Route[i,j,k] = 1 if vehicle i travels from city j to city k
Route = model.addVars(M, N, N, name='Route', vtype=gp.GRB.BINARY)

# u[i,j] = order/position of city j in the route of vehicle i (for MTZ subtour elimination)
u = model.addVars(M, N, name='Order', vtype=gp.GRB.CONTINUOUS, lb=0, ub=N-1)

# ====== Define constraints ====== 

# 1. Each vehicle must start and return to the depot
for i in range(M):
    # Each vehicle MUST leave the depot exactly once (forces all vehicles to be used)
    model.addConstr(gp.quicksum(Route[i, DEPOT, k] for k in range(1, C)) == 1, 
                   name=f"depot_departure_{i}")
    # If a vehicle leaves the depot, it must return
    model.addConstr(gp.quicksum(Route[i, DEPOT, k] for k in range(1, C)) == 
                   gp.quicksum(Route[i, k, DEPOT] for k in range(1, C)), 
                   name=f"depot_return_{i}")

# 2. Each non-depot city is visited exactly once
for j in range(1, C):  # Exclude depot
    model.addConstr(gp.quicksum(Route[i, j, k] for i in range(M) for k in range(C) if k != j) == 1, 
                   name=f"visit_city_{j}")

# 3. Flow conservation: if a vehicle enters a city, it must leave
for i in range(M):
    for j in range(C):
        model.addConstr(gp.quicksum(Route[i, k, j] for k in range(C) if k != j) == 
                       gp.quicksum(Route[i, j, k] for k in range(C) if k != j), 
                       name=f"flow_conservation_{i}_{j}")

# 4. No self-loops
for i in range(M):
    for j in range(C):
        model.addConstr(Route[i, j, j] == 0, name=f"no_self_loop_{i}_{j}")

# 5. MTZ subtour elimination constraints
for i in range(M):
    for j in range(1, C):  # Exclude depot
        for k in range(1, C):  # Exclude depot
            if j != k:
                model.addConstr(u[i, j] - u[i, k] + N * Route[i, j, k] <= N - 1, 
                               name=f"mtz_{i}_{j}_{k}")

# 6. Depot has order 0 for all vehicles
for i in range(M):
    model.addConstr(u[i, DEPOT] == 0, name=f"depot_order_{i}")

# ====== Define objective ====== 

# Minimize total travel cost (excluding self-loops which are already forbidden)
model.setObjective(gp.quicksum(TravelCost[j][k] * Route[i, j, k] 
                              for i in range(M) 
                              for j in range(C) 
                              for k in range(C) 
                              if j != k), gp.GRB.MINIMIZE)

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
    print("----------------- Modelo VRP optimizado con éxito. ---------------")
    print("Estado:", solving_info["status"])
    print("Valor objetivo:", solving_info["objective_value"])
    print("\nRutas de los vehículos:")
    
    # Mostrar rutas de manera más legible
    for i in range(M):
        route_edges = []
        vehicle_used = False
        for j in range(C):
            for k in range(C):
                if j != k and Route[i, j, k].X > 0.5:  # Variable binaria activa
                    route_edges.append((j, k))
                    vehicle_used = True
        
        if vehicle_used:
            print(f"  Vehículo {i}:")
            print(f"    Arcos: {route_edges}")
            
            # Construir la ruta completa empezando desde el depósito
            if route_edges:
                route_sequence = [DEPOT]
                current_city = DEPOT
                edges_dict = dict(route_edges)
                
                while current_city in edges_dict:
                    next_city = edges_dict[current_city]
                    route_sequence.append(next_city) 
                    current_city = next_city
                    if current_city == DEPOT:  # Regresó al depósito
                        break
                
                print(f"    Secuencia: {' -> '.join(map(str, route_sequence))}")
                
                # Calcular costo de esta ruta
                route_cost = sum(TravelCost[route_edges[i][0]][route_edges[i][1]] for i in range(len(route_edges)))
                print(f"    Costo: {route_cost}")
        else:
            print(f"  Vehículo {i}: No utilizado")
    
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