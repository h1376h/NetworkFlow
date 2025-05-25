import networkx as nx
import math

# Define PHI (golden ratio conjugate) and M_val
PHI = (math.sqrt(5) - 1) / 2  # ~0.618034
M_val = 100.0

# Create the graph
G_nx = nx.DiGraph()
G_nx.add_edge('s', 'x1', capacity=1.0)
G_nx.add_edge('s', 'x2', capacity=M_val)
G_nx.add_edge('x1', 'x2', capacity=1.0)
G_nx.add_edge('x1', 't', capacity=M_val)
G_nx.add_edge('x2', 't', capacity=PHI)

# Calculate max flow using Dinitz algorithm implemented in networkx
# The dinitz function returns the residual graph.
# The flow_value is an attribute of R.graph.
# Edge flows are attributes of R.edges.
R_nx = nx.algorithms.flow.dinitz(G_nx, 's', 't')
max_flow_value_nx = R_nx.graph['flow_value']

print("--- NetworkX Dinic's Algorithm Result ---")
print(f"Maximum flow value: {max_flow_value_nx:.5f}")
print(f"(Which is 1 + PHI = {1 + PHI:.5f})\n")

print("Final flow distribution on edges:")
for u, v, data in R_nx.edges(data=True):
    # In the residual graph R_nx, the 'flow' attribute on an edge (u,v)
    # that was part of the *original* graph G_nx stores the flow sent on (u,v).
    # We need to check if (u,v) was an original edge.
    if G_nx.has_edge(u,v):
        flow_on_edge = data.get('flow', 0)
        # networkx dinitz stores flow for original edges.
        # If an edge has capacity C and flow f, its residual capacity is C-f.
        # The 'flow' attribute seems to be directly what we need.
        if flow_on_edge > 1e-9 : # Print only if flow is significant
             print(f"Flow s({u}) -> d({v}): {flow_on_edge:.5f} / Capacity: {G_nx[u][v]['capacity']:.5f}")

print("\n--- End of NetworkX Dinic's Algorithm Result ---\n")