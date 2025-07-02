import json
import networkx as nx
import matplotlib.pyplot as plt
import os

# Cargar datos del JSON
json_path = os.path.join(os.path.dirname(__file__), 'Data2.json')
with open(json_path, 'r') as f:
    data = json.load(f)

N = data['N']
distances = data['Distances']

# Crear grafo dirigido
G = nx.DiGraph()

# Agregar nodos
for i in range(N):
    G.add_node(i, label=f'Ciudad {i+1}')

# Agregar aristas con distancias
for i in range(N):
    for j in range(N):
        if i != j:
            G.add_edge(i, j, weight=distances[i][j])

# Posiciones de los nodos en círculo
pos = nx.circular_layout(G)

# Dibujar nodos
nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=700)
# Dibujar etiquetas de los nodos
labels = {i: f'Ciudad {i+1}' for i in range(N)}
nx.draw_networkx_labels(G, pos, labels, font_size=12)
# Dibujar aristas
nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)
# Dibujar etiquetas de las aristas (distancias)
edge_labels = {(i, j): distances[i][j] for i in range(N) for j in range(N) if i != j}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

plt.title('Visualización del TSP (Traveling Salesman Problem)')
plt.axis('off')
plt.show()
