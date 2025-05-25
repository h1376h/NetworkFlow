import collections
import networkx as nx # For verification
import networkx.algorithms.flow as nx_flow # For dinitz verification

class DinitzDetailed:
    def __init__(self, edges_input_list, num_nodes_max_id):
        self.N = num_nodes_max_id
        # adj[u] = list of v for original directed edges (u,v)
        self.adj = [[] for _ in range(self.N + 1)]
        # capacity[(u,v)] = capacity of original directed edge (u,v)
        self.capacity = collections.defaultdict(int)
        # flow[(u,v)] = current flow on original directed edge (u,v)
        self.flow = collections.defaultdict(int)
        
        # level[u] = level of node u in current level graph, -1 if not reachable
        self.level = [-1] * (self.N + 1)
        # ptr[u] = Dinitz optimization: pointer to next edge to try in DFS from node u
        # to avoid re-exploring dead ends in the same phase's blocking flow search.
        # For this illustrative version, ptr will manage indices for iterating neighbors.
        self.ptr = [0] * (self.N + 1)
        
        # List to store actual path edges and flow for detailed printing after DFS finds a path
        self.current_path_details_for_printing = []


        print("--- Initializing Graph for Detailed Dinitz ---")
        for u, v, cap in edges_input_list:
            print(f"Adding original edge: {u} -> {v} with capacity {cap}")
            self.adj[u].append(v)
            self.capacity[(u, v)] = cap
        print("--------------------------------------------\n")

    def _get_residual_capacity(self, u, v):
        """Calculates residual capacity of edge u -> v."""
        # Case 1: u -> v is a forward edge in residual graph (from original u -> v)
        # Residual capacity = capacity[u,v] - flow[u,v]
        if self.capacity.get((u,v), 0) > 0: # If (u,v) is an original edge
            return self.capacity[(u,v)] - self.flow.get((u,v), 0)
        # Case 2: u -> v is a backward edge in residual graph (from original v -> u having flow)
        # Residual capacity = flow[v,u]
        elif self.flow.get((v,u), 0) > 0: # If (v,u) is an original edge that has flow
             return self.flow.get((v,u),0)
        return 0


    def _bfs(self, s, t):
        """Builds the level graph using BFS. Returns True if sink is reachable."""
        print("--- Building Level Graph (BFS) ---")
        for i in range(self.N + 1): self.level[i] = -1
        
        self.level[s] = 0
        q = collections.deque([s])
        print(f"Source node {s} is at level 0.")

        while q:
            u = q.popleft()
            # print(f"  BFS: Exploring from node {u} (level {self.level[u]})")
            
            # Explore neighbors v of u in the residual graph
            # Check original forward edges u -> v_neighbor
            for v_neighbor in self.adj[u]:
                if (self.capacity[(u,v_neighbor)] - self.flow.get((u,v_neighbor),0) > 0) and self.level[v_neighbor] == -1:
                    self.level[v_neighbor] = self.level[u] + 1
                    # print(f"    Node {v_neighbor} reached (via fwd {u}->{v_neighbor}). Level: {self.level[v_neighbor]}. ResCap: {self.capacity[(u,v_neighbor)] - self.flow.get((u,v_neighbor),0)}")
                    q.append(v_neighbor)
            
            # Check original backward edges v_neighbor -> u (which form residual edges u -> v_neighbor)
            # To do this, we iterate all possible source nodes of such backward edges
            for v_potential_source in range(1, self.N + 1):
                if v_potential_source == u: continue
                # If original edge (v_potential_source, u) exists and has flow
                if self.capacity.get((v_potential_source,u),0) > 0 and self.flow.get((v_potential_source,u),0) > 0:
                    # This creates a residual edge u -> v_potential_source with capacity = self.flow[(v_potential_source,u)]
                    if self.level[v_potential_source] == -1: # If v_potential_source not yet leveled
                        self.level[v_potential_source] = self.level[u] + 1
                        # print(f"    Node {v_potential_source} reached (via bwd {v_potential_source}->{u}). Level: {self.level[v_potential_source]}. ResCap: {self.flow.get((v_potential_source,u),0)}")
                        q.append(v_potential_source)
        
        if self.level[t] != -1:
            print(f"Sink node {t} reached at level {self.level[t]}.")
            print("Level graph construction complete for this phase.")
            print("Levels found (node: level):", {i: lvl for i, lvl in enumerate(self.level) if lvl != -1 and i > 0})
            return True
        else:
            print(f"Sink node {t} is NOT reachable in this phase.")
            return False

    def _dfs_augment_and_get_path(self, u, t, pushed_amount):
        """
        Finds an augmenting path using DFS in the current level graph.
        Augments flow along the path found.
        Returns the amount of flow pushed along this path.
        Populates self.current_path_details_for_printing with ((x,y), flow_on_xy, type) for printing.
        """
        if pushed_amount == 0: return 0
        if u == t: # Reached sink
            return pushed_amount 

        # Iterate using self.ptr[u] for Dinitz optimization
        # self.adj[u] gives original forward neighbors
        # We also need to consider residual edges from original backward flows
        
        # For this illustrative version, we simplify ptr usage and reconstruct neighbor list for current u
        # Neighbors for DFS are (v) such that R(u,v) > 0 and level[v] == level[u] + 1
        
        # Check original forward edges u -> v
        # Using ptr to iterate through self.adj[u]
        while self.ptr[u] < len(self.adj[u]):
            v_neighbor = self.adj[u][self.ptr[u]]
            if self.level[v_neighbor] == self.level[u] + 1: # Check level condition
                res_cap_uv = self.capacity[(u,v_neighbor)] - self.flow.get((u,v_neighbor),0)
                if res_cap_uv > 0:
                    # print(f"    DFS: Trying fwd {u}(lvl {self.level[u]}) -> {v_neighbor}(lvl {self.level[v_neighbor]}) with ResCap {res_cap_uv}")
                    tr_pushed = self._dfs_augment_and_get_path(v_neighbor, t, min(pushed_amount, res_cap_uv))
                    if tr_pushed > 0:
                        self.flow[(u,v_neighbor)] = self.flow.get((u,v_neighbor),0) + tr_pushed
                        self.current_path_details_for_printing.append(((u, v_neighbor), tr_pushed, "forward"))
                        return tr_pushed
            self.ptr[u] +=1 # Move to next neighbor in adj[u]
        
        # Check original backward edges v_neighbor -> u (which form residual edges u -> v_neighbor)
        # This part is trickier with ptr if not iterating a pre-built residual graph adjacency list.
        # For simplicity of ptr, this illustrative version will primarily focus ptr on forward edges.
        # We will iterate all possible v_neighbors for backward flow opportunities.
        for v_neighbor in range(1, self.N + 1): # Can optimize this by pre-calculating reverse adj list
            if v_neighbor == u: continue
            if self.level[v_neighbor] == self.level[u] + 1: # Check level condition
                # Check if original edge (v_neighbor, u) has flow, creating residual u -> v_neighbor
                if self.capacity.get((v_neighbor,u),0) > 0 and self.flow.get((v_neighbor,u),0) > 0:
                    res_cap_uv = self.flow.get((v_neighbor,u),0)
                    if res_cap_uv > 0:
                        # print(f"    DFS: Trying bwd {u}(lvl {self.level[u]}) -> {v_neighbor}(lvl {self.level[v_neighbor]}) with ResCap {res_cap_uv} (from flow on {v_neighbor}->{u})")
                        tr_pushed = self._dfs_augment_and_get_path(v_neighbor, t, min(pushed_amount, res_cap_uv))
                        if tr_pushed > 0:
                            self.flow[(v_neighbor,u)] = self.flow.get((v_neighbor,u),0) - tr_pushed # Reduce flow on original backward edge
                            self.current_path_details_for_printing.append(((v_neighbor, u), tr_pushed, "backward_reduced")) # Note: this edge is v->u
                            return tr_pushed
        return 0


    def calculate_max_flow(self, s, t):
        print(f"--- Calculating Max Flow from Source {s} to Sink {t} (Detailed Steps) ---\n")
        total_max_flow = 0
        phase = 1

        while self._bfs(s, t): # While sink is reachable in level graph
            print(f"\n--- Phase {phase}: Finding Blocking Flow ---")
            # Reset pointers for DFS for the new level graph
            for i in range(self.N + 1): self.ptr[i] = 0 
            
            flow_in_phase = 0
            path_num_in_phase = 1
            
            while True: # Keep finding paths in the current level graph
                self.current_path_details_for_printing = [] # Clear for current path
                print(f"  Phase {phase}, Path Search {path_num_in_phase}: Starting DFS from source {s}...")
                
                pushed_on_path = self._dfs_augment_and_get_path(s, t, float('inf'))
                
                if pushed_on_path > 0:
                    print(f"  Found Augmenting Path in Phase {phase} (Search {path_num_in_phase}):")
                    print(f"    Bottleneck Flow Pushed: {pushed_on_path}")
                    
                    # Reconstruct and print path (in reverse from self.current_path_details_for_printing)
                    # The current_path_details are added in child-first order due to recursion.
                    # To print S -> ... -> T, we need to reverse it or build it carefully.
                    # For now, just list the segments that were augmented.
                    path_str_segments = []
                    # The current_path_details_for_printing has segments in reverse order of path
                    # To show S->...->T, we need to trace it properly.
                    # Let's just show the augmented edges for now:
                    print(f"    Augmented Edges (and flow reduction for backward parts):")
                    for (edge_uv, flow_val, type_info) in reversed(self.current_path_details_for_printing):
                        if type_info == "forward":
                            print(f"      {edge_uv[0]} -> {edge_uv[1]} by {flow_val}")
                        else: # backward_reduced
                            print(f"      Reduced flow on {edge_uv[0]} -> {edge_uv[1]} by {flow_val} (effectively pushing {edge_uv[1]} -> {edge_uv[0]})")
                    
                    total_max_flow += pushed_on_path
                    flow_in_phase += pushed_on_path
                    path_num_in_phase +=1
                    print(f"  Current flow in phase: {flow_in_phase}, Total max flow so far: {total_max_flow}")
                    print(f"  Current Non-Zero Flows:")
                    current_flows_sorted = sorted([item for item in self.flow.items() if item[1] > 0])
                    for (u_f, v_f), val_f in current_flows_sorted: print(f"    {u_f} -> {v_f}: {val_f}")
                    print("-" * 30)
                else: 
                    print(f"  No more augmenting paths found in Phase {phase} for this level graph.")
                    break 
            
            if flow_in_phase == 0:
                print("Blocking flow for this phase is 0. Algorithm terminates.")
                break
            print(f"--- End of Phase {phase}: Total flow pushed in this phase = {flow_in_phase} ---")
            phase += 1
            print("\n")

        print(f"\n--- Detailed Dinitz Algorithm Finished ---")
        print(f"Maximum Flow from {s} to {t}: {total_max_flow}")
        
        print("\nFinal Flow Distribution (non-zero flows on original edges):")
        final_flows_sorted = sorted([item for item in self.flow.items() if item[1] > 0 and self.capacity.get(item[0],0) > 0])
        for (u, v), val in final_flows_sorted:
             print(f"  Edge ({u} -> {v}): {val} units (Original Capacity: {self.capacity[(u,v)]})")
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

# Determine number of nodes (max node ID for 1-based indexing)
max_node_id = 0
for u_node, v_node, _ in Edges_example:
    max_node_id = max(max_node_id, u_node, v_node)

# --- Run the Detailed Dinitz Implementation ---
dinitz_solver = DinitzDetailed(Edges_example, max_node_id)
calculated_max_flow_detailed = dinitz_solver.calculate_max_flow(source_node, sink_node)

# --- NetworkX Verification ---
print("\n\n--- NetworkX Verification ---")
print(f"NetworkX version: {nx.__version__}")
print("Attempting to calculate max flow using NetworkX's dinitz function for comparison...")

# Create the graph for NetworkX
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