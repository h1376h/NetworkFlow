import graphviz
from collections import deque

def find_shortest_path_bfs(graph_edges, source, sink):
    """
    Finds a shortest path from source to sink using BFS.
    Returns the path as a list of edges, or None if no path exists.
    'graph_edges' is a list of tuples (u, v, capacity).
    """
    adj = {}
    for u, v, _ in graph_edges:
        adj.setdefault(u, []).append(v)
        # If your graph is undirected for path finding purposes, add:
        # adj.setdefault(v, []).append(u)

    if source not in adj:
        return None # Source node has no outgoing edges

    queue = deque([(source, [source])]) # Store (current_node, path_to_current_node)
    visited_paths = {source} # Keep track of nodes for which we've found a path

    while queue:
        current_node, path = queue.popleft()

        if current_node == sink:
            path_edges = []
            for i in range(len(path) - 1):
                path_edges.append((path[i], path[i+1]))
            return path_edges

        if current_node in adj:
            for neighbor in adj[current_node]:
                if neighbor not in visited_paths: # Process each node only once for shortest path
                    visited_paths.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append((neighbor, new_path))
    return None

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

    all_nodes = set()
    for u, v, _ in edges_with_capacities:
        all_nodes.add(u)
        all_nodes.add(v)

    # Define node styles
    for node in all_nodes:
        if node == source_node:
            dot.node(node, label=f"🚚  {node}\n(Warehouse)", shape='Mdiamond', style='filled', fillcolor='lightblue')
        elif node in sink_nodes:
            dot.node(node, label=f"📦  {node}\n(Distribution Ctr)", shape='doublecircle', style='filled', fillcolor='lightgreen')
        else:
            dot.node(node, shape='ellipse', style='filled', fillcolor='whitesmoke')

    # Find shortest path to the target sink
    shortest_path_edges = find_shortest_path_bfs(edges_with_capacities, source_node, highlight_sink_target)
    
    highlighted_edges_set = set()
    if shortest_path_edges:
        print(f"Shortest path found to {highlight_sink_target}: {shortest_path_edges}")
        for u, v in shortest_path_edges:
            highlighted_edges_set.add((u,v))
    else:
        print(f"No path found from {source_node} to {highlight_sink_target}")

    # Add edges with capacities and highlighting
    for u, v, capacity in edges_with_capacities:
        is_highlighted = (u,v) in highlighted_edges_set
        if is_highlighted:
            dot.edge(u, v, label=str(capacity), color='red', penwidth='2.5', fontcolor='red')
        else:
            dot.edge(u, v, label=str(capacity), color='gray')

    # Render the graph
    try:
        dot.render(filename, view=False, format='png')
        print(f"Graph saved as {filename}.png and {filename}.dot")
    except Exception as e:
        print(f"Error rendering graph: {e}")
        print("Please ensure Graphviz is installed and in your system's PATH.")

if __name__ == '__main__':
    # Define the network structure: (node1, node2, capacity)
    # 'S' is Source (Warehouse)
    # 'T1', 'T2' are Sinks (Distribution Centers)
    # 'A', 'B', 'C', 'D', 'E' are intermediate hubs
    network_edges = [
        ('S', 'A', 10),
        ('S', 'B', 12),
        ('A', 'C', 8),
        ('A', 'D', 4),
        ('B', 'D', 7),
        ('B', 'E', 6),
        ('C', 'T1', 9),
        ('D', 'T1', 5), # Path to T1
        ('D', 'T2', 6), # Path to T2
        ('E', 'T2', 10),
        ('A', 'B', 3), # A connection between intermediate hubs
        ('C', 'D', 2)  # Another connection
    ]

    source = 'S'
    sinks = ['T1', 'T2']
    target_sink_for_highlight = 'T1' # We want to highlight a path to T1

    generate_delivery_network_graph(network_edges, source, sinks, target_sink_for_highlight, filename="package_delivery_shortest_path")

    # Example 2: Highlight path to T2
    # target_sink_for_highlight_2 = 'T2'
    # generate_delivery_network_graph(network_edges, source, sinks, target_sink_for_highlight_2, filename="package_delivery_shortest_path_T2")