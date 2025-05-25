from manim import *
import collections

# --- Style Constants ---
NODE_RADIUS = 0.3
NODE_STROKE_WIDTH = 2
EDGE_STROKE_WIDTH = 4
ARROW_TIP_LENGTH = 0.2
CAPACITY_FONT_SIZE = 16
FLOW_FONT_SIZE = 16
STATUS_TEXT_FONT_SIZE = 22
LEVEL_TEXT_FONT_SIZE = 18

LEVEL_COLORS = [RED_E, ORANGE, YELLOW_D, GREEN_C, BLUE_C, PURPLE_D, PINK]
DEFAULT_NODE_COLOR = BLUE_E
DEFAULT_EDGE_COLOR = GREY_D
LABEL_COLOR = DARK_GREY # For "0/Cap" labels
LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH = 5.5
DIMMED_OPACITY = 0.25
DIMMED_COLOR = GREY_C


class DinitzAlgorithmVisualizer(Scene):
    def construct(self):
        # --- Title ---
        main_title = Text("Visualizing Dinitz's Algorithm", font_size=40)
        self.play(Write(main_title))
        self.wait(1)
        self.play(main_title.animate.to_edge(UP).scale(0.8))

        # --- Graph Definition ---
        self.source_node, self.sink_node = 1, 10
        self.vertices_data = list(range(1, 11))
        self.edges_with_capacity_list = [
            (1, 2, 25), (1, 3, 30), (1, 4, 20), (2, 5, 25), (3, 4, 30), 
            (3, 5, 35), (4, 6, 30), (5, 7, 40), (5, 8, 40), (6, 8, 35), 
            (6, 9, 30), (7, 10, 20), (8, 10, 20), (9, 10, 20)
        ]
        
        self.capacities = collections.defaultdict(int)
        self.flow = collections.defaultdict(int) 
        self.adj = collections.defaultdict(list) 

        for u, v, cap in self.edges_with_capacity_list:
            self.capacities[(u,v)] = cap
            self.adj[u].append(v)

        self.graph_layout = {
            1: [-6.5, 0, 0], 2: [-4.5, 2, 0], 3: [-4.5, 0, 0], 4: [-4.5, -2, 0],
            5: [-2, 1.5, 0], 6: [-2, -1.5, 0], 
            7: [1.5, 2, 0], 8: [1.5, 0, 0], 9: [1.5, -2, 0],
            10: [4.5, 0, 0] 
        }

        self.node_mobjects = {} 
        self.edge_mobjects = {} 
        self.edge_capacity_text_mobjects = {} # Stores Text("Cap")
        self.edge_flow_val_text_mobjects = {} # Stores Text("0")
        self.edge_slash_text_mobjects = {}    # Stores Text("/")

        # --- Part A: Animated Graph Creation (Refactored Order) ---
        current_status_text = Text("1. Building the Network", font_size=STATUS_TEXT_FONT_SIZE, weight=BOLD).next_to(main_title, DOWN, buff=0.4)
        self.play(Write(current_status_text))
        self.wait(0.5)

        # 1. Add Nodes one by one
        nodes_vgroup_on_screen = VGroup() 
        node_creation_subtitle = Text("Adding Nodes...", font_size=18).next_to(current_status_text, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(node_creation_subtitle))
        for i, v_id in enumerate(self.vertices_data):
            node_dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, z_index=2, stroke_color=BLACK, stroke_width=1)
            node_label_text = str(v_id)
            node_label = Text(node_label_text, font_size=20, weight=BOLD).move_to(node_dot.get_center()).set_z_index(3)
            self.node_mobjects[v_id] = VGroup(node_dot, node_label)
            nodes_vgroup_on_screen.add(self.node_mobjects[v_id])
            self.play(GrowFromCenter(self.node_mobjects[v_id]), run_time=0.2 + 0.02*i)
        self.play(FadeOut(node_creation_subtitle))
        self.nodes_vgroup = nodes_vgroup_on_screen

        # 2. Add Edges one by one
        edge_creation_subtitle = Text("Adding Edges...", font_size=18).next_to(current_status_text, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(edge_creation_subtitle))
        all_edges_vgroup = VGroup()
        for i, (u, v, cap) in enumerate(self.edges_with_capacity_list):
            node_u_dot = self.node_mobjects[u][0]
            node_v_dot = self.node_mobjects[v][0]
            arrow = Arrow(node_u_dot.get_center(), node_v_dot.get_center(), buff=NODE_RADIUS, 
                          stroke_width=EDGE_STROKE_WIDTH, color=DEFAULT_EDGE_COLOR,
                          max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH, z_index=0)
            self.edge_mobjects[(u,v)] = arrow
            all_edges_vgroup.add(arrow)
            self.play(GrowArrow(arrow), run_time=0.2 + 0.02*i)
        self.play(FadeOut(edge_creation_subtitle))
        self.wait(0.2)

        # 3. Add Capacity Labels (after all edges are drawn)
        cap_label_subtitle = Text("Adding Capacities...", font_size=18).next_to(current_status_text, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(cap_label_subtitle))
        all_capacity_labels_vg = VGroup()
        # Manual offsets for tricky labels {(u,v): [dx, dy, dz_offset_from_perp]}
        manual_cap_offsets = {
            (3,4): RIGHT*0.1 + DOWN*0.4, (6,8): LEFT*0.1+DOWN*0.4, (5,8): UP*0.4, (1,3): DOWN*0.4, (4,6): UP*0.4,
            (1,2): LEFT*0.1 + UP*0.3, (1,4): LEFT*0.1+DOWN*0.3
        }
        for i, (u, v, cap) in enumerate(self.edges_with_capacity_list):
            arrow = self.edge_mobjects[(u,v)]
            perp_direction = rotate_vector(arrow.get_unit_vector(), TAU/4)
            base_label_pos = arrow.get_center() + perp_direction * 0.45
            
            # Apply manual offset if defined
            if (u,v) in manual_cap_offsets:
                base_label_pos = arrow.get_center() + manual_cap_offsets[(u,v)]

            capacity_text_mobj = Text(str(cap), font_size=CAPACITY_FONT_SIZE, color=LABEL_COLOR, weight=NORMAL).move_to(base_label_pos).set_z_index(1)
            self.edge_capacity_text_mobjects[(u,v)] = capacity_text_mobj
            all_capacity_labels_vg.add(capacity_text_mobj)
            self.play(Write(capacity_text_mobj), run_time=0.1 + 0.02*i)
        self.play(FadeOut(cap_label_subtitle))
        self.wait(0.2)

        # 4. Add Initial "0 / " Flow Prefixes (after all capacities are drawn)
        flow_label_subtitle = Text("Adding Initial Flow (0 / Capacity)...", font_size=18).next_to(current_status_text, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(flow_label_subtitle))
        all_flow_prefixes_vg = VGroup()
        for i, (u, v, cap) in enumerate(self.edges_with_capacity_list):
            capacity_text_mobj = self.edge_capacity_text_mobjects[(u,v)]
            
            flow_val_mobj = Text("0", font_size=FLOW_FONT_SIZE, color=LABEL_COLOR, weight=NORMAL)
            slash_mobj = Text("/", font_size=FLOW_FONT_SIZE, color=LABEL_COLOR, weight=NORMAL)

            # Position "0" then "/" then existing "Cap"
            slash_mobj.next_to(capacity_text_mobj, LEFT, buff=0.08, aligned_edge=DOWN)
            flow_val_mobj.next_to(slash_mobj, LEFT, buff=0.08, aligned_edge=DOWN)
            
            self.edge_flow_val_text_mobjects[(u,v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u,v)] = slash_mobj # Store if needed, or group
            all_flow_prefixes_vg.add(flow_val_mobj, slash_mobj)
            self.play(Write(flow_val_mobj), Write(slash_mobj), run_time=0.1 + 0.02*i)
        self.play(FadeOut(flow_label_subtitle))
        self.wait(0.5)

        self.network_display_group = VGroup(self.nodes_vgroup, all_edges_vgroup, all_capacity_labels_vg, all_flow_prefixes_vg)
        self.play(self.network_display_group.animate.scale(0.9).to_edge(DOWN, buff=0.2)) # Adjusted scale and buff
        self.play(ReplacementTransform(current_status_text, Text("",font_size=1))) # Clear status text
        self.wait(1)


        # --- Part B: Dynamic Dinitz Algorithm Animation ---
        self.levels = {v_id: -1 for v_id in self.vertices_data}
        self.ptr = {v_id: 0 for v_id in self.vertices_data} 

        dinitz_title = Text("2. Dinitz Algorithm: Step-by-Step", font_size=28).next_to(main_title, DOWN, buff=0.4)
        self.play(Write(dinitz_title))
        self.wait(1)

        # --- Phase 1 ---
        phase_text = Text("Phase 1", font_size=24, weight=BOLD).next_to(dinitz_title, DOWN, buff=0.3)
        self.play(Write(phase_text))

        # Re-introduce status text mobject for algorithm steps
        self.algo_status_text = Text("", font_size=STATUS_TEXT_FONT_SIZE).next_to(phase_text, DOWN, buff=0.3)
        self.add(self.algo_status_text)
        self.update_algo_status("Building Level Graph (BFS from Source 1)")


        q_bfs = collections.deque()
        self.levels = {v_id: -1 for v_id in self.vertices_data} 

        current_bfs_level_num = 0
        self.levels[self.source_node] = current_bfs_level_num
        q_bfs.append(self.source_node) 
        
        level_display_vgroup = VGroup().to_corner(UL).shift(DOWN*0.8 + RIGHT*0.5) 
        self.add(level_display_vgroup)

        source_node_dot = self.node_mobjects[self.source_node][0] 
        self.play(source_node_dot.animate.set_color(LEVEL_COLORS[0]).scale(1.1), run_time=0.5)
        l_text_mobj = Text(f"L{current_bfs_level_num}: {{{self.source_node}}}", font_size=LEVEL_TEXT_FONT_SIZE)
        l_text_mobj.align_to(level_display_vgroup, UL)
        level_display_vgroup.add(l_text_mobj)
        self.play(Write(l_text_mobj))

        # --- Refactored BFS Animation Loop ---
        while q_bfs: 
            nodes_to_process_this_level = list(q_bfs) # Nodes at level k (e.g. L0)
            q_bfs.clear() # Will be populated with nodes for level k+1
            
            if not nodes_to_process_this_level: break

            target_level_for_discovery = self.levels[nodes_to_process_this_level[0]] + 1 # Level k+1
            nodes_found_for_next_level_set = set()
            
            node_color_animations_for_new_level = []

            for u_bfs in nodes_to_process_this_level: # u_bfs is at level k
                indicator_u = SurroundingRectangle(self.node_mobjects[u_bfs], color=YELLOW, buff=0.05, corner_radius=0.1, stroke_width=2)
                self.play(Create(indicator_u), run_time=0.15)

                for v_neighbor in self.adj[u_bfs]: 
                    res_cap_uv = self.capacities[(u_bfs, v_neighbor)] - self.flow.get((u_bfs, v_neighbor), 0)
                    if res_cap_uv > 0 and self.levels[v_neighbor] == -1: # Not yet leveled
                        self.levels[v_neighbor] = target_level_for_discovery # Assign level k+1
                        nodes_found_for_next_level_set.add(v_neighbor)
                        q_bfs.append(v_neighbor) 
                        
                        level_color = LEVEL_COLORS[target_level_for_discovery % len(LEVEL_COLORS)]
                        node_v_dot = self.node_mobjects[v_neighbor][0]
                        node_v_label = self.node_mobjects[v_neighbor][1]
                        
                        node_color_animations_for_new_level.append(node_v_dot.animate.set_color(level_color).scale(1.1))
                        rgb_components = color_to_rgb(level_color) 
                        label_color_for_node = BLACK if sum(rgb_components) > 1.5 else WHITE 
                        node_color_animations_for_new_level.append(node_v_label.animate.set_color(label_color_for_node))
                
                self.play(FadeOut(indicator_u), run_time=0.15)
            
            # Animate coloring of all nodes found FOR THIS NEW LEVEL together
            if node_color_animations_for_new_level: self.play(*node_color_animations_for_new_level, run_time=0.7)

            # Now, animate coloring of edges connecting PREVIOUS level to THIS NEWLY COLORED level
            edge_color_animations_for_level_links = []
            if nodes_found_for_next_level_set: # If any nodes were actually found for level k+1
                for u_prev_level in nodes_to_process_this_level: # Nodes at level k
                    for v_newly_leveled in nodes_found_for_next_level_set: # Nodes at level k+1
                        # Check if v_newly_leveled was indeed reached from u_prev_level at this step
                        if v_newly_leveled in self.adj[u_prev_level] and \
                           self.levels[v_newly_leveled] == self.levels[u_prev_level] + 1:
                            res_cap_uv = self.capacities[(u_prev_level, v_newly_leveled)] - self.flow.get((u_prev_level, v_newly_leveled), 0)
                            if res_cap_uv > 0:
                                edge_mobj_uv = self.edge_mobjects[(u_prev_level,v_newly_leveled)]
                                # Color edge based on the level of its source node (u_prev_level)
                                edge_color = LEVEL_COLORS[self.levels[u_prev_level] % len(LEVEL_COLORS)]
                                edge_color_animations_for_level_links.append(edge_mobj_uv.animate.set_color(edge_color).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
            
            if edge_color_animations_for_level_links: self.play(*edge_color_animations_for_level_links, run_time=0.7)


            if nodes_found_for_next_level_set:
                nodes_str = ", ".join(map(str, sorted(list(nodes_found_for_next_level_set))))
                l_text_mobj = Text(f"L{target_level_for_discovery}: {{{nodes_str}}}", font_size=LEVEL_TEXT_FONT_SIZE)
                l_text_mobj.next_to(level_display_vgroup[-1], DOWN, aligned_edge=LEFT, buff=0.15)
                level_display_vgroup.add(l_text_mobj)
                self.play(Write(l_text_mobj))
                self.wait(0.5)
            
            if not q_bfs: break 
        
        final_bfs_status_text = Text("") # Placeholder for final BFS status
        final_bfs_status_text.move_to(self.algo_status_text.get_center()) # Position it
        if self.levels[self.sink_node] == -1:
            final_bfs_status_text.become(Text("Sink NOT Reached in BFS! Max flow found.", color=RED, font_size=STATUS_TEXT_FONT_SIZE))
            self.play(Transform(self.algo_status_text, final_bfs_status_text))
            self.wait(3); self.play(*[FadeOut(mob) for mob in self.mobjects if isinstance(mob, Mobject)]); return 
        else:
            final_bfs_status_text.become(Text(f"Sink Reached at L{self.levels[self.sink_node]}. Level Graph Built.", color=GREEN, font_size=STATUS_TEXT_FONT_SIZE))
            self.play(Transform(self.algo_status_text, final_bfs_status_text))
            self.wait(1)

        # --- Isolate Level Graph Edges --- 
        isolate_lg_text_mobj = Text("Isolating Level Graph Edges...", font_size=STATUS_TEXT_FONT_SIZE)
        isolate_lg_text_mobj.move_to(self.algo_status_text.get_center())
        self.play(Transform(self.algo_status_text, isolate_lg_text_mobj)) 

        lg_edge_anims = []
        non_lg_edge_anims = []
        for (u,v), edge_mobj in self.edge_mobjects.items():
            is_level_graph_edge = (self.levels.get(u, -1) != -1 and \
                                   self.levels.get(v, -1) != -1 and \
                                   self.levels[v] == self.levels[u] + 1 and \
                                   (self.capacities[(u,v)] - self.flow.get((u,v),0) > 0) ) 
            
            if is_level_graph_edge: # These edges should already be colored by BFS correctly
                lg_edge_anims.append(edge_mobj.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
            else:
                non_lg_edge_anims.append(edge_mobj.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR))
        
        if non_lg_edge_anims: self.play(*non_lg_edge_anims, run_time=1.0)
        if lg_edge_anims: self.play(*lg_edge_anims, run_time=0.5) 
        self.wait(1)
        self.play(FadeOut(self.algo_status_text)) # Clear status for next step (DFS)


        # --- TODO: Animate DFS path finding (based on self.levels and residual graph) ---
        # --- TODO: Animate flow augmentation and residual graph updates ---
        
        self.wait(5) 
        # Cleanup (example, adjust based on what's actually on screen)
        all_scene_items_to_fade = VGroup(main_title, self.network_display_group, dinitz_title, phase_text, level_display_vgroup)
        if hasattr(self, 'current_algo_status_text') and self.current_algo_status_text in self.mobjects :
             all_scene_items_to_fade.add(self.current_algo_status_text)

        self.play(FadeOut(all_scene_items_to_fade, run_time=1))
        self.wait(1)

    # Helper for status text update if needed later
    def update_algo_status(self, text_str, play_animation=True):
        new_text_mobj = Text(text_str, font_size=STATUS_TEXT_FONT_SIZE)
        new_text_mobj.move_to(self.algo_status_text.get_center())
        if play_animation:
            self.play(Transform(self.algo_status_text, new_text_mobj))
        else: # Direct update (less smooth)
            self.remove(self.algo_status_text)
            self.algo_status_text = new_text_mobj
            self.add(self.algo_status_text)