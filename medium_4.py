import collections
import os # For creating an output directory for images
import networkx as nx # For verification
import networkx.algorithms.flow as nx_flow # For dinitz verification
from graphviz import Digraph # For generating graph images

# --- DinitzDetailed Class (with Graphviz additions) ---
class DinitzDetailed:
    def __init__(self, edges_input_list, num_nodes_max_id, output_dir="dinitz_steps"):
        self.N = num_nodes_max_id
        self.adj = [[] for _ in range(self.N + 1)]
        self.capacity = collections.defaultdict(int)
        self.flow = collections.defaultdict(int)
        self.level = [-1] * (self.N + 1)
        self.ptr = [0] * (self.N + 1) # For DFS optimization
        self.current_path_edges = [] # Stores ((u,v), type) for current DFS path

        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.step_counter = 0 # For unique image filenames

        print("--- Initializing Graph for Detailed Dinitz ---")
        for u, v, cap in edges_input_list:
            # print(f"Adding original edge: {u} -> {v} with capacity {cap}")
            self.adj[u].append(v)
            self.capacity[(u, v)] = cap
        print(f"Graph initialized. Images will be saved in '{self.output_dir}/'")
        self.save_graphviz_state("initial_graph", "Initial Graph (Capacities)")
        print("--------------------------------------------\n")

    def save_graphviz_state(self, filename_suffix, graph_label, current_path_highlight=None, s_node=None, t_node=None):
        """Saves the current graph state (flows, capacities, levels) as an image."""
        dot = Digraph(comment=graph_label)
        dot.attr(label=graph_label, labelloc="t", fontsize="20")
        dot.attr(rankdir='LR') # Left to Right layout

        for i in range(1, self.N + 1):
            node_label = f"{i}\nL:{self.level[i]}" if self.level[i] != -1 else str(i)
            color = "lightblue"
            if self.level[i] != -1:
                # Simple color gradient for levels, can be improved
                colors = ["lightyellow", "lightgreen", "lightblue", "lightpink", "lightcoral"]
                color = colors[self.level[i] % len(colors)]
            if i == s_node: color = "green"
            if i == t_node: color = "red"
            dot.node(str(i), label=node_label, style="filled", fillcolor=color)

        # Edges from original graph definition
        for u in range(1, self.N + 1):
            for v in self.adj[u]: # Original directed edges
                cap = self.capacity.get((u,v), 0)
                flw = self.flow.get((u,v), 0)
                res_cap = cap - flw
                
                label = f"{flw}/{cap}"
                edge_color = "black"
                penwidth = "1.5"
                
                # Highlight current path if provided
                if current_path_highlight:
                    # current_path_highlight is a list of ((x,y), type_str) tuples
                    for (path_u, path_v), path_type in current_path_highlight:
                        if u == path_u and v == path_v and path_type == "forward":
                            edge_color = "blue"
                            penwidth = "3.0"
                        # Highlighting for reduction on backward edge needs to map to original edge
                        elif u == path_v and v == path_u and path_type == "backward_reduced": # Original edge was v->u
                             edge_color = "orange" # Indicates flow was reduced on this original edge
                             penwidth = "3.0"


                if cap > 0 : # Only draw original edges
                    if res_cap == 0 and flw > 0 : # Saturated edge
                        edge_color = "red" if edge_color=="black" else edge_color # Keep highlight if any
                    dot.edge(str(u), str(v), label=label, color=edge_color, penwidth=penwidth)
        
        # Add residual edges from backward flow for clarity (optional, can make graph busy)
        # for (v, u), flw_vu in self.flow.items():
        #     if flw_vu > 0 and self.capacity.get((v,u),0) > 0 : # flow on an original edge (v,u)
        #         # This creates a residual edge u -> v with capacity flw_vu
        #         # Check if original u->v edge already drawn; if not, draw this residual
        #         if not self.capacity.get((u,v),0) > 0:
        #              dot.edge(str(u), str(v), label=f"Res (Bwd): {flw_vu}", color="gray", style="dashed", penwidth="1.0")


        filepath = os.path.join(self.output_dir, f"{self.step_counter:02d}_{filename_suffix}")
        try:
            dot.render(filepath, view=False, format='png')
            print(f"  Saved graph image: {filepath}.png")
        except Exception as e:
            print(f"  Could not save graph image {filepath}.png (Graphviz not installed or error): {e}")
        self.step_counter += 1


    def _bfs(self, s, t):
        print("--- Building Level Graph (BFS) ---")
        for i in range(self.N + 1): self.level[i] = -1
        self.level[s] = 0
        q = collections.deque([s])
        # print(f"Source node {s} is at level 0.")

        while q:
            u = q.popleft()
            for v_neighbor in self.adj[u]: # Original u->v
                if (self.capacity[(u,v_neighbor)] - self.flow.get((u,v_neighbor),0) > 0) and self.level[v_neighbor] == -1:
                    self.level[v_neighbor] = self.level[u] + 1
                    q.append(v_neighbor)
            for v_source_of_backward_flow in range(1, self.N + 1):
                if u == v_source_of_backward_flow: continue
                if self.capacity.get((v_source_of_backward_flow,u),0) > 0 and self.flow.get((v_source_of_backward_flow,u),0) > 0:
                    if self.level[v_source_of_backward_flow] == -1:
                        self.level[v_source_of_backward_flow] = self.level[u] + 1
                        q.append(v_source_of_backward_flow)
        
        if self.level[t] != -1:
            print(f"Sink node {t} reached at level {self.level[t]}.")
            # print("Levels found (node: level):", {i: lvl for i, lvl in enumerate(self.level) if lvl != -1 and i > 0})
            self.save_graphviz_state(f"phase{self.current_phase}_level_graph", f"Phase {self.current_phase} - Level Graph", s_node=s, t_node=t)
            return True
        else:
            print(f"Sink node {t} is NOT reachable in this phase.")
            self.save_graphviz_state(f"phase{self.current_phase}_bfs_fail", f"Phase {self.current_phase} - BFS Fail (Sink Unreachable)", s_node=s, t_node=t)
            return False

    def _dfs_augment_and_get_path(self, u, t, pushed_amount):
        if pushed_amount == 0: return 0
        if u == t: return pushed_amount 

        # Using self.ptr[u] to iterate relevant neighbors.
        # Construct a list of potential next hops (v, res_cap_uv, is_fwd_type) in the level graph from u
        # This is done once per (u, level_graph_phase) when DFS first explores u.
        # For simplicity in this version, ptr logic is basic for iterating self.adj[u] first.
        
        # Iterate original forward edges u -> v (using ptr for these)
        while self.ptr[u] < len(self.adj[u]):
            v_neighbor = self.adj[u][self.ptr[u]]
            if self.level[v_neighbor] == self.level[u] + 1:
                res_cap_uv = self.capacity[(u,v_neighbor)] - self.flow.get((u,v_neighbor),0)
                if res_cap_uv > 0:
                    tr_pushed = self._dfs_augment_and_get_path(v_neighbor, t, min(pushed_amount, res_cap_uv))
                    if tr_pushed > 0:
                        self.flow[(u,v_neighbor)] = self.flow.get((u,v_neighbor),0) + tr_pushed
                        self.current_path_edges.append(((u, v_neighbor), "forward"))
                        return tr_pushed
            self.ptr[u] +=1
        
        # Iterate residual edges from original backward edges v_neighbor -> u
        # For these, ptr logic is not applied as simply here; we just iterate possibilities
        for v_neighbor in range(1, self.N + 1): 
            if v_neighbor == u: continue
            if self.level[v_neighbor] == self.level[u] + 1:
                if self.capacity.get((v_neighbor,u),0) > 0 and self.flow.get((v_neighbor,u),0) > 0:
                    res_cap_uv = self.flow.get((v_neighbor,u),0)
                    if res_cap_uv > 0:
                        tr_pushed = self._dfs_augment_and_get_path(v_neighbor, t, min(pushed_amount, res_cap_uv))
                        if tr_pushed > 0:
                            self.flow[(v_neighbor,u)] = self.flow.get((v_neighbor,u),0) - tr_pushed
                            self.current_path_edges.append(((v_neighbor, u), "backward_reduced"))
                            return tr_pushed
        return 0

    def calculate_max_flow(self, s, t):
        print(f"--- Calculating Max Flow from Source {s} to Sink {t} (Detailed Steps) ---\n")
        total_max_flow = 0
        self.current_phase = 0 # For filename of graphviz

        while True:
            self.current_phase += 1
            if not self._bfs(s, t): # Build level graph; if sink not reachable, break
                print("Algorithm terminates as sink is no longer reachable.")
                break
            
            print(f"\n--- Phase {self.current_phase}: Finding Blocking Flow ---")
            for i in range(self.N + 1): self.ptr[i] = 0 # Reset pointers for DFS
            
            flow_in_phase = 0
            path_num_in_phase = 1
            
            while True: 
                self.current_path_edges = [] # Clear for current path details
                # print(f"  Phase {self.current_phase}, Path Search {path_num_in_phase}: Starting DFS from source {s}...")
                
                pushed_on_path = self._dfs_augment_and_get_path(s, t, float('inf'))
                
                if pushed_on_path > 0:
                    print(f"  Augmenting Path {path_num_in_phase} in Phase {self.current_phase}:")
                    print(f"    Bottleneck Flow Pushed: {pushed_on_path}")
                    
                    # The path edges are in self.current_path_edges in reverse order of traversal
                    actual_path_for_highlight = []
                    path_str = f"{s}"
                    curr_node_in_path = s
                    
                    # Reconstruct path string (this is a bit tricky from current_path_edges)
                    # For highlighting, pass self.current_path_edges to save_graphviz_state
                    self.save_graphviz_state(
                        f"phase{self.current_phase}_path{path_num_in_phase}_flow{pushed_on_path}",
                        f"Phase {self.current_phase} - Path {path_num_in_phase} (Flow: {pushed_on_path})",
                        current_path_highlight=self.current_path_edges, s_node=s, t_node=t
                    )
                    
                    total_max_flow += pushed_on_path
                    flow_in_phase += pushed_on_path
                    path_num_in_phase +=1
                    print(f"    Current flow in phase: {flow_in_phase}, Total max flow so far: {total_max_flow}")
                    # print(f"    Current Non-Zero Flows:")
                    # current_flows_sorted = sorted([item for item in self.flow.items() if item[1] > 0])
                    # for (u_f, v_f), val_f in current_flows_sorted: print(f"      {u_f} -> {v_f}: {val_f}")
                    print("-" * 30)
                else: 
                    print(f"  No more augmenting paths found in Phase {self.current_phase} for this level graph.")
                    break 
            
            if flow_in_phase == 0:
                print("Blocking flow for this phase is 0. Algorithm terminates.")
                break
            print(f"--- End of Phase {self.current_phase}: Total flow pushed in this phase = {flow_in_phase} ---")
            print("\n")

        print(f"\n--- Detailed Dinitz Algorithm Finished ---")
        print(f"Maximum Flow from {s} to {t}: {total_max_flow}")
        
        print("\nFinal Flow Distribution (non-zero flows on original edges):")
        final_flows_sorted = sorted([item for item in self.flow.items() if item[1] > 0 and self.capacity.get(item[0],0) > 0])
        for (u, v), val in final_flows_sorted:
             print(f"  Edge ({u} -> {v}): {val} units (Original Capacity: {self.capacity[(u,v)]})")
        self.save_graphviz_state("final_flow_distribution", "Final Flow Distribution", s_node=s, t_node=t)
        return total_max_flow

# --- Define your graph ---
Edges_example = [ # u, v, capacity
  [1, 2, 25], [1, 3, 30], [1, 4, 20],
  [3, 4, 30],
  [2, 5, 25], [3, 5, 35], [4, 6, 30],
  [5, 7, 40], [5, 8, 40],
  [6, 8, 35], [6, 9, 30],
  [7, 10, 20], [8, 10, 20], [9, 10, 20]
]
source_node = 1
sink_node = 10

max_node_id = 0
for u_node, v_node, _ in Edges_example: max_node_id = max(max_node_id, u_node, v_node)

# --- Run the Detailed Dinitz Implementation ---
dinitz_solver = DinitzDetailed(Edges_example, max_node_id, output_dir="dinitz_steps_images")
calculated_max_flow_detailed = dinitz_solver.calculate_max_flow(source_node, sink_node)

# --- NetworkX Verification ---
# (Add the NetworkX verification code block here, as provided in the previous response)
print("\n\n--- NetworkX Verification ---")
print(f"NetworkX version: {nx.__version__}")
print("Attempting to calculate max flow using NetworkX's dinitz function for comparison...")

G_nx = nx.DiGraph()
for u_node, v_node, capacity_val in Edges_example:
    G_nx.add_edge(u_node, v_node, capacity=capacity_val)

try:
    R_nx = nx_flow.dinitz(G_nx, source_node, sink_node, capacity='capacity')
    max_flow_value_nx = R_nx.graph['flow_value']
    print(f"NetworkX (nx_flow.dinitz) calculated max flow: {max_flow_value_nx}")

    if calculated_max_flow_detailed == max_flow_value_nx:
        print("Verification SUCCESSFUL: NetworkX result matches the detailed step-by-step implementation!")
    else:
        print(f"Verification MISMATCH! Detailed implementation: {calculated_max_flow_detailed}, NetworkX: {max_flow_value_nx}")

except AttributeError:
    print("NetworkX Verification Error: nx.algorithms.flow.dinitz seems unavailable.")
    print("Trying nx.maximum_flow with algorithm='dinic' (for newer NetworkX versions)...")
    try:
        max_flow_value_nx, _ = nx.maximum_flow(G_nx, source_node, sink_node, capacity='capacity', algorithm='dinic')
        print(f"NetworkX (algorithm='dinic') calculated max flow: {max_flow_value_nx}")
        if calculated_max_flow_detailed == max_flow_value_nx:
            print("Verification SUCCESSFUL: NetworkX result matches the detailed step-by-step implementation!")
        else:
            print(f"Verification MISMATCH! Detailed implementation: {calculated_max_flow_detailed}, NetworkX: {max_flow_value_nx}")
    except Exception as e_dinic_str:
        print(f"NetworkX 'dinic' string method also failed: {e_dinic_str}")
        print("Could not verify with NetworkX Dinic/Dinitz.")
except Exception as e:
    print(f"An error occurred during NetworkX verification: {e}")