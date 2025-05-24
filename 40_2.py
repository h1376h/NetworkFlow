import graphviz
from collections import deque

def find_shortest_path_bfs(graph_edges, source, sink):
    """
    Finds a shortest path from source to sink using BFS.
    Returns the path as a list of edges, or None if no path exists.
    'graph_edges' is a list of tuples (u, v, capacity).
    """
    adj = {}
    # Create an adjacency list for the graph
    for u, v, _ in graph_edges: # We only care about connectivity for BFS, not capacity here
        adj.setdefault(u, []).append(v)

    if source not in adj:
        return None # Source node has no outgoing edges, so no path

    queue = deque([(source, [source])]) # Store (current_node, path_to_current_node_as_list_of_nodes)
    # visited_paths is used to ensure we find the shortest path by not reprocessing nodes
    # once they've been reached. For unweighted graphs / BFS, first time a node is reached is via a shortest path.
    visited_nodes = {source} 

    while queue:
        current_node, path_nodes = queue.popleft()

        if current_node == sink:
            # Reconstruct path as list of edges
            path_edges = []
            for i in range(len(path_nodes) - 1):
                path_edges.append((path_nodes[i], path_nodes[i+1]))
            return path_edges

        if current_node in adj:
            for neighbor in adj[current_node]:
                if neighbor not in visited_nodes: # If neighbor hasn't been visited yet
                    visited_nodes.add(neighbor) # Mark as visited
                    new_path_nodes = list(path_nodes)
                    new_path_nodes.append(neighbor)
                    queue.append((neighbor, new_path_nodes))
    return None # No path found

def generate_delivery_network_graph(edges_with_capacities, source_node, sink_nodes, highlight_sink_target, filename="delivery_network"):
    """
    Generates a Graphviz graph for the delivery network.

    Args:
        edges_with_capacities (list): List of tuples (u, v, capacity).
        source_node (str): The name of the source node.
        sink_nodes (list): A list of names for the sink nodes.
        highlight_sink_target (str): The specific sink node to find and highlight a path to.
        filename (str): The base name for the output file (e.g., "delivery_network").
    """
    dot = graphviz.Digraph(comment='Package Delivery Network', engine='dot')
    dot.attr(rankdir='LR') # Left to Right layout
    dot.attr(label=f"Shortest Augmenting Path to {highlight_sink_target}") # Add a title to the graph
    dot.attr(fontsize='20')


    all_nodes = set()
    for u, v, _ in edges_with_capacities:
        all_nodes.add(u)
        all_nodes.add(v)

    # Define node styles
    for node in all_nodes:
        if node == source_node:
            dot.node(node, label=f"🚚  {node}\n(Warehouse)", shape='Mdiamond', style='filled', fillcolor='skyblue', fontsize='10')
        elif node in sink_nodes:
            dot.node(node, label=f"📦  {node}\n(Distribution Ctr)", shape='doublecircle', style='filled', fillcolor='lightgreen', fontsize='10')
        else:
            dot.node(node, label=f"{node}", shape='ellipse', style='filled', fillcolor='whitesmoke', fontsize='10')

    # Find shortest path to the target sink
    shortest_path_edges = find_shortest_path_bfs(edges_with_capacities, source_node, highlight_sink_target)
    
    highlighted_edges_set = set()
    if shortest_path_edges:
        num_segments = len(shortest_path_edges)
        print(f"Shortest path found to {highlight_sink_target} ({num_segments} segments): {shortest_path_edges}")
        for u, v in shortest_path_edges:
            highlighted_edges_set.add((u,v))
    else:
        print(f"No path found from {source_node} to {highlight_sink_target}")

    # Add edges with capacities and highlighting
    for u, v, capacity in edges_with_capacities:
        is_highlighted = (u,v) in highlighted_edges_set
        edge_attrs = {
            'label': str(capacity),
            'color': 'red' if is_highlighted else 'dimgray',
            'penwidth': '3.0' if is_highlighted else '1.5',
            'fontcolor': 'red' if is_highlighted else 'dimgray',
            'fontsize': '10'
        }
        dot.edge(u, v, **edge_attrs)

    # Render the graph
    try:
        dot.render(filename, view=False, format='png')
        print(f"Graph saved as {filename}.png and {filename}") # .dot file is also saved
    except Exception as e:
        print(f"Error rendering graph: {e}")
        print("Please ensure Graphviz is installed and in your system's PATH.")

if __name__ == '__main__':
    # Define the network structure: (node1, node2, capacity)
    # 'S' is Source (Warehouse)
    # 'T1', 'T2' are Sinks (Distribution Centers)
    # 'A', 'B', 'C', 'D', 'E', 'F' are intermediate hubs

    # Modified network_edges to ensure the shortest path to T1 has 4 segments
    network_edges = [
        ('S', 'A', 10), ('S', 'B', 12),
        ('A', 'C', 8),  ('A', 'D', 4),  # S->A->C is 2 segments
        ('B', 'D', 7),  ('B', 'E', 6),
        # ('C', 'T1', 9),  # REMOVED to eliminate 3-segment path S->A->C->T1
        # ('D', 'T1', 5),  # REMOVED to eliminate 3-segment paths S->A->D->T1 and S->B->D->T1
        ('D', 'T2', 6), ('E', 'T2', 10), # Paths to T2 remain, shortest might be 3 segments
        ('A', 'B', 3),  
        ('C', 'D', 2),

        # New path to T1 via node 'F' to make it 4 segments: S -> A -> C -> F -> T1
        ('C', 'F', 5),  # S->A->C->F is 3 segments to F
        ('F', 'T1', 7)   # S->A->C->F->T1 is 4 segments to T1
    ]

    source = 'S'
    sinks = ['T1', 'T2'] # Node 'F' is an intermediate node, not a sink
    
    target_sink_for_highlight_T1 = 'T1' 
    generate_delivery_network_graph(network_edges, source, sinks, target_sink_for_highlight_T1, filename="package_delivery_4segment_path_T1")

    # Example 2: Highlight path to T2 (this might still be 3 segments)
    target_sink_for_highlight_T2 = 'T2'
    generate_delivery_network_graph(network_edges, source, sinks, target_sink_for_highlight_T2, filename="package_delivery_path_T2")