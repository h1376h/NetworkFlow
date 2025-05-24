import graphviz
import collections
import os

step_counter = 0
BACKWARD_EDGE_COLOR = "darkolivegreen"

NODE_POSITIONS = {
    "1": "0.5,3.0!", "2": "2.0,4.0!", "3": "2.0,3.0!", "4": "2.0,2.0!",
    "5": "3.5,3.5!", "6": "3.5,2.5!", "7": "5.0,4.0!", "8": "5.0,3.0!",
    "9": "5.0,2.0!", "10": "6.5,3.0!"
}

def generate_graphviz_dot(nodes_set, edges_data, title_explanation, output_directory,
                          use_absolute_positions=False,
                          source_node_id=None, # To color the source node
                          sink_node_id=None,   # To color the sink node
                          highlight_edges=None, path_edges=None):
    global step_counter, NODE_POSITIONS

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
            print(f"Created directory: {output_directory}")
        except OSError as e:
            print(f"Error creating directory {output_directory}: {e}")
            return

    graph_viz_name = f"Dinitz_Algorithm_Step_{step_counter}"
    current_engine = 'neato' if use_absolute_positions else 'dot'

    dot = graphviz.Digraph(name=graph_viz_name,
                           comment="Flow Network Visualization",
                           engine=current_engine,
                           format='png')

    if not use_absolute_positions:
        dot.attr(rankdir='LR')
        dot.attr(nodesep='0.5')
        dot.attr(ranksep='1.0')
    else:
        # For neato with fixed positions, these can sometimes help
        # dot.attr(overlap="scale") # helps prevent node overlap by scaling
        # dot.attr(splines="true")  # default, for smooth edges
        dot.graph_attr['sep'] = '+15,15'
        pass

    for node_id_int in sorted(list(nodes_set)):
        node_id_str = str(node_id_int)
        node_attrs = {}
        node_attrs['shape'] = 'circle'
        if use_absolute_positions:
            if node_id_str in NODE_POSITIONS:
                node_attrs['pos'] = NODE_POSITIONS[node_id_str]
            else:
                print(f"Warning: Node {node_id_str} is active but not in NODE_POSITIONS map. '{current_engine}' will auto-place it.")

        # Apply specific colors for source and sink nodes
        if source_node_id is not None and node_id_int == source_node_id:
            node_attrs['style'] = 'filled'
            node_attrs['fillcolor'] = 'mediumseagreen'
            node_attrs['fontcolor'] = 'white' # Ensure text is visible on green
        elif sink_node_id is not None and node_id_int == sink_node_id:
            node_attrs['style'] = 'filled'
            node_attrs['fillcolor'] = 'tomato'
            node_attrs['fontcolor'] = 'white' # Ensure text is visible on red
        
        dot.node(node_id_str, **node_attrs)

    for i, edge_tuple in enumerate(edges_data):
        u, v, flow_value, capacity_value, _, reverse_edge_idx = edge_tuple
        is_original_algorithmic_backward_edge = (capacity_value == 0)

        if is_original_algorithmic_backward_edge and flow_value == 0:
            continue

        current_color = BACKWARD_EDGE_COLOR if is_original_algorithmic_backward_edge else "black"
        current_penwidth = "1"
        current_style = "solid"
        label = f"{flow_value}/{capacity_value}"
        
        # Fontsize adjustments for edge labels
        edge_label_fontsize = "10" # Default edge label font size
        if is_original_algorithmic_backward_edge:
            edge_label_fontsize = "7" # Smaller font size for backward edges

        if highlight_edges and i in highlight_edges: # Level graph edges
            current_color = "blue"; current_penwidth = "2"
        if path_edges and i in path_edges: # Augmenting path edges
            current_color = "purple"; current_penwidth = "3"; current_style = "dashed" # Changed to purple

        # Modified: Added fontsize attribute to dot.edge
        dot.edge(str(u), str(v), label=label, color=current_color, penwidth=current_penwidth, style=current_style, fontsize=edge_label_fontsize, _attributes={'id': f'e{i}'})

    dot.attr(label=f'\n{title_explanation}', labelloc='t', fontsize='16')

    file_basename = f"step_{step_counter:03d}"
    expected_png_path = os.path.join(output_directory, file_basename + ".png")
    dot_source_candidate_1 = os.path.join(output_directory, file_basename)
    dot_source_candidate_2 = os.path.join(output_directory, file_basename + ".gv")
    rendered_file_path = None
    try:
        rendered_file_path = dot.render(filename=file_basename, directory=output_directory, view=False, cleanup=True)
        print(f"Graphviz.render reported: '{rendered_file_path}'")
        if os.path.exists(expected_png_path):
            print(f"SUCCESS: PNG file confirmed at '{expected_png_path}'")
            if os.path.exists(dot_source_candidate_1) and dot_source_candidate_1 != expected_png_path:
                print(f"WARNING: Intermediate DOT source file '{dot_source_candidate_1}' was not cleaned up.")
            elif os.path.exists(dot_source_candidate_2) and dot_source_candidate_2 != expected_png_path:
                print(f"WARNING: Intermediate DOT source file '{dot_source_candidate_2}' was not cleaned up.")
        else:
            print(f"ERROR: PNG file NOT FOUND at expected path '{expected_png_path}'.")
            if rendered_file_path and os.path.exists(rendered_file_path) and rendered_file_path != expected_png_path:
                 print(f"However, file reported by render ('{rendered_file_path}') exists and is different.")
            elif os.path.exists(dot_source_candidate_1): print(f"However, a file (DOT source?) exists at: '{dot_source_candidate_1}'")
            elif os.path.exists(dot_source_candidate_2): print(f"However, a file (DOT source?) exists at: '{dot_source_candidate_2}'")
            else: print(f"No other residual files found for '{file_basename}' in '{output_directory}'.")
    except graphviz.backend.execute.CalledProcessError as e:
        stderr_output = e.stderr.decode(errors='replace') if e.stderr else "N/A"
        print(f"Graphviz rendering FAILED for '{file_basename}' (CalledProcessError): {e}\nStderr: {stderr_output}\nCheck Graphviz installation and PATH. Engine: {current_engine}")
    except FileNotFoundError as e:
        print(f"Graphviz rendering FAILED for '{file_basename}' (FileNotFoundError): {e}\nThis means '{current_engine}' executable not found. Check Graphviz installation and PATH.")
    except Exception as e:
        print(f"An UNEXPECTED ERROR during rendering of '{file_basename}.png': {e} (Type: {type(e)})")

    step_counter += 1


def construct_level_graph_dinitz(source_node, sink_node, edges_arr, adj, output_dir, all_nodes,
                                 use_absolute_pos_flag=False, current_phase_num=0):
    global step_counter
    for i in range(len(edges_arr)): edges_arr[i][4] = False
    levels = {}; q = collections.deque()
    if source_node not in all_nodes: return False, {}, set()
    levels[source_node] = 0; q.append(source_node)

    while q:
        u = q.popleft()
        for v, edge_idx in adj.get(u, []):
            edge = edges_arr[edge_idx]
            if (edge[3] - edge[2]) > 0 and v not in levels:
                levels[v] = levels[u] + 1; q.append(v)

    level_graph_indices = set()
    for i, (u,v,flow,cap,_,_) in enumerate(edges_arr):
        if u in levels and v in levels and levels.get(v) == levels.get(u, float('-inf')) + 1 and (cap - flow) > 0:
            edges_arr[i][4] = True; level_graph_indices.add(i)

    title = (f"Step {step_counter}: Phase {current_phase_num} - Constructing Level Graph\n"
             f"S:{source_node}(Green), T:{sink_node}(Red). Labels:Flow/Cap.\nBFS on residual. Blue:Level Graph edges.")
    generate_graphviz_dot(all_nodes, edges_arr, title, output_dir,
                          use_absolute_positions=use_absolute_pos_flag,
                          source_node_id=source_node, sink_node_id=sink_node, # Pass S/T for coloring
                          highlight_edges=level_graph_indices)
    return sink_node in levels, levels, level_graph_indices

def dfs_find_path_dinitz(source, sink, edges_arr, levels, adj, ptr):
    path_edges_rev, path_nodes_rev = [], []
    def _dfs(u, flow_in):
        if u == sink: return flow_in
        while ptr.get(u,0) < len(adj.get(u,[])):
            v, edge_idx = adj[u][ptr[u]]
            edge = edges_arr[edge_idx]
            res_cap = edge[3] - edge[2]
            if res_cap > 0 and v in levels and levels.get(v) == levels.get(u, float('-inf')) + 1:
                pushed = _dfs(v, min(flow_in, res_cap))
                if pushed > 0:
                    path_nodes_rev.append(v); path_edges_rev.append(edge_idx)
                    return pushed
            ptr[u] = ptr.get(u,0) + 1
        return 0
    b_flow = _dfs(source, float('inf'))
    return (path_edges_rev[::-1], [source] + path_nodes_rev[::-1], b_flow) if b_flow > 0 else ([], [], 0)


def dinitz_visualized(source, sink, original_edges, output_dir="dinitz_colored_nodes_example",
                      use_absolute_positions_flag=True):
    global step_counter, BACKWARD_EDGE_COLOR, NODE_POSITIONS
    step_counter = 0

    edges_data = []
    adj = collections.defaultdict(list)
    all_graph_nodes = set([source, sink])
    for u_orig, v_orig, _ in original_edges: all_graph_nodes.add(u_orig); all_graph_nodes.add(v_orig)
    if use_absolute_positions_flag:
        for node_id_str in NODE_POSITIONS.keys(): all_graph_nodes.add(int(node_id_str))

    for u, v, capacity in original_edges:
        fwd_idx = len(edges_data); bwd_idx = fwd_idx + 1
        edges_data.append([u, v, 0, capacity, False, bwd_idx])
        adj[u].append((v, fwd_idx))
        edges_data.append([v, u, 0, 0, False, fwd_idx]) # capacity is 0 for original backward edge
        adj[v].append((u, bwd_idx))

    title_initial = (f"Step {step_counter}: Initial Graph (S:{source}(Green), T:{sink}(Red))\nTotal Flow:0. Labels:Flow/Cap.")
    generate_graphviz_dot(all_graph_nodes, edges_data, title_initial, output_dir,
                          use_absolute_positions=use_absolute_positions_flag,
                          source_node_id=source, sink_node_id=sink)

    total_max_flow = 0; phase_num = 0
    while True:
        phase_num += 1
        print(f"\n--- Dinitz: Phase {phase_num} ---")
        is_reachable, levels, lvl_indices = construct_level_graph_dinitz(
            source, sink, edges_data, adj, output_dir, all_graph_nodes,
            use_absolute_pos_flag=use_absolute_positions_flag, current_phase_num=phase_num)
        if not is_reachable: break
        ptr = {n:0 for n in all_graph_nodes}
        while True:
            path_EIs, path_nodes, path_flow = dfs_find_path_dinitz(source, sink, edges_data, levels, adj, ptr)
            if path_flow == 0: break
            path_s = '->'.join(map(str,path_nodes))
            title_path = (f"Step {step_counter}: Phase {phase_num} - Augmenting Path Found\nPath(Purple dashed):{path_s}"
                          f"\nBottleneck:{path_flow}. Current Total Flow:{total_max_flow}.\nS:{source}(Green), T:{sink}(Red). Blue:Level Graph.")
            generate_graphviz_dot(all_graph_nodes, edges_data, title_path, output_dir,
                                  use_absolute_positions=use_absolute_positions_flag,
                                  source_node_id=source, sink_node_id=sink,
                                  highlight_edges=lvl_indices, path_edges=set(path_EIs))
            total_max_flow += path_flow
            print(f"Path:{path_s}, Flow:{path_flow}. Total Flow:{total_max_flow}")
            for edge_idx in path_EIs:
                edges_data[edge_idx][2] += path_flow
                edges_data[edges_data[edge_idx][5]][2] -= path_flow # This is flow on backward edge
            title_aug = (f"Step {step_counter}: Phase {phase_num} - Flow Augmented\nPushed {path_flow} via {path_s}."
                         f"\nTotal Max Flow:{total_max_flow}. S:{source}(Green), T:{sink}(Red).\nResidual graph updated.")
            generate_graphviz_dot(all_graph_nodes, edges_data, title_aug, output_dir,
                                  use_absolute_positions=use_absolute_positions_flag,
                                  source_node_id=source, sink_node_id=sink,
                                  highlight_edges=lvl_indices) # No path_edges highlighted here
    title_final = (f"Step {step_counter}: Final State (S:{source}(Green), T:{sink}(Red))\nAlgorithm Ended. Total Max Flow:{total_max_flow}.")
    generate_graphviz_dot(all_graph_nodes, edges_data, title_final, output_dir,
                          use_absolute_positions=use_absolute_positions_flag,
                          source_node_id=source, sink_node_id=sink)
    print(f"\nMax Flow: {total_max_flow}. Visuals in '{os.path.abspath(output_dir)}'")
    return total_max_flow

Edges_example = [
  [1, 2, 25],
  [1, 3, 30],
  [1, 4, 20],
  [3, 4, 30], # u, v, capacity
  [2, 5, 25],
  [3, 5, 35],
  [4, 6, 30],
  [5, 7, 40],
  [5, 8, 40],
  [6, 8, 35],
  [6, 9, 30],
  [7, 10, 20],
  [8, 10, 20],
  [9, 10, 20]
]
if __name__ == '__main__':
    final_flow = dinitz_visualized(1, 10, Edges_example, use_absolute_positions_flag=True)