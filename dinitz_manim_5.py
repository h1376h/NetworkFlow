from manim import *
import collections

# --- Style and Layout Constants ---
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.18
CAPACITY_FONT_SIZE = 14
FLOW_FONT_SIZE = 14
LEVEL_TEXT_FONT_SIZE = 18
STATUS_TEXT_FONT_SIZE = 22
TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28
PHASE_TEXT_FONT_SIZE = 22

# Buffs for spacing
BUFF_VERY_SMALL = 0.05 # Corrected name
BUFF_SMALL = 0.1
BUFF_MED = 0.25
BUFF_LARGE = 0.5

# Colors
LEVEL_COLORS = [RED_E, ORANGE, YELLOW_D, GREEN_D, BLUE_D, PURPLE_D, PINK] 
DEFAULT_NODE_COLOR = BLUE_E
DEFAULT_EDGE_COLOR = GREY_D
LABEL_COLOR = DARK_GREY 
LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH = 5.0 # Slightly adjusted from 5.5
DIMMED_OPACITY = 0.25 # Corrected from 0.2
DIMMED_COLOR = GREY_C # Corrected from GREY_BROWN


class DinitzAlgorithmVisualizer(Scene):
    def construct(self):
        # --- Title ---
        main_title = Text("Visualizing Dinitz's Algorithm", font_size=TITLE_FONT_SIZE)
        main_title.to_edge(UP, buff=BUFF_MED)
        self.play(Write(main_title))
        self.wait(0.5)

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
        self.edge_capacity_text_mobjects = {}
        self.edge_flow_val_text_mobjects = {} 
        self.edge_slash_text_mobjects = {}    

        # --- Part A: Animated Graph Creation (Refactored Order) ---
        current_status_text = Text("1. Building the Network", font_size=SECTION_TITLE_FONT_SIZE, weight=NORMAL).next_to(main_title, DOWN, buff=BUFF_LARGE) # Changed weight
        self.play(Write(current_status_text))
        self.wait(0.5)

        nodes_vgroup_on_screen = VGroup() 
        node_creation_subtitle = Text("Adding Nodes...", font_size=18).next_to(current_status_text, DOWN, buff=BUFF_MED, aligned_edge=LEFT)
        self.play(Write(node_creation_subtitle))
        for i, v_id in enumerate(self.vertices_data):
            node_dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, z_index=2, stroke_color=BLACK, stroke_width=NODE_STROKE_WIDTH)
            node_label_text = str(v_id)
            node_label = Text(node_label_text, font_size=18, weight=BOLD).move_to(node_dot.get_center()).set_z_index(3) # Slightly smaller label
            self.node_mobjects[v_id] = VGroup(node_dot, node_label)
            nodes_vgroup_on_screen.add(self.node_mobjects[v_id])
            self.play(GrowFromCenter(self.node_mobjects[v_id]), run_time=0.2 + 0.02*i)
        self.play(FadeOut(node_creation_subtitle))
        self.nodes_vgroup = nodes_vgroup_on_screen

        edge_creation_subtitle = Text("Adding Edges...", font_size=18).next_to(current_status_text, DOWN, buff=BUFF_MED, aligned_edge=LEFT)
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

        cap_label_subtitle = Text("Adding Capacities...", font_size=18).next_to(current_status_text, DOWN, buff=BUFF_MED, aligned_edge=LEFT)
        self.play(Write(cap_label_subtitle))
        all_capacity_labels_vg = VGroup()
        manual_cap_offsets = {
            (3,4): DOWN*0.25, (6,8): DOWN*0.25, (5,8): UP*0.3, (1,3): DOWN*0.3, (4,6): UP*0.3,
            (1,2): LEFT*0.1+UP*0.2, (1,4): LEFT*0.1+DOWN*0.2, (6,9):DOWN*0.15+RIGHT*0.15,
            (2,5): RIGHT*0.1+UP*0.15, (3,5): RIGHT*0.1+DOWN*0.1, (5,7):LEFT*0.1+UP*0.15, (8,10): UP*0.25
        } 
        for i, (u, v, cap) in enumerate(self.edges_with_capacity_list):
            arrow = self.edge_mobjects[(u,v)]
            perp_direction = rotate_vector(arrow.get_unit_vector(), TAU/4)
            base_label_pos = arrow.get_center() + perp_direction * 0.40 # Default offset

            if (u,v) in manual_cap_offsets:
                base_label_pos = arrow.get_center() + manual_cap_offsets[(u,v)]

            capacity_text_mobj = Text(str(cap), font_size=CAPACITY_FONT_SIZE, color=LABEL_COLOR, weight=NORMAL).move_to(base_label_pos).set_z_index(1)
            self.edge_capacity_text_mobjects[(u,v)] = capacity_text_mobj
            all_capacity_labels_vg.add(capacity_text_mobj)
            self.play(Write(capacity_text_mobj), run_time=0.1 + 0.02*i)
        self.play(FadeOut(cap_label_subtitle))
        self.wait(0.2)

        flow_label_subtitle = Text("Adding Initial Flow (0 / Capacity)...", font_size=18).next_to(current_status_text, DOWN, buff=BUFF_MED, aligned_edge=LEFT)
        self.play(Write(flow_label_subtitle))
        all_flow_prefixes_vg = VGroup()
        for i, (u, v, cap) in enumerate(self.edges_with_capacity_list):
            capacity_text_mobj = self.edge_capacity_text_mobjects[(u,v)]
            
            flow_val_mobj = Text("0", font_size=FLOW_FONT_SIZE, color=LABEL_COLOR, weight=NORMAL)
            slash_mobj = Text("/", font_size=FLOW_FONT_SIZE, color=LABEL_COLOR, weight=NORMAL)

            slash_mobj.next_to(capacity_text_mobj, LEFT, buff=BUFF_VERY_SMALL, aligned_edge=DOWN) # Corrected BUFF name
            flow_val_mobj.next_to(slash_mobj, LEFT, buff=BUFF_VERY_SMALL, aligned_edge=DOWN) # Corrected BUFF name
            
            self.edge_flow_val_text_mobjects[(u,v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u,v)] = slash_mobj
            all_flow_prefixes_vg.add(flow_val_mobj, slash_mobj)
            self.play(Write(flow_val_mobj), Write(slash_mobj), run_time=0.1 + 0.02*i)
        self.play(FadeOut(flow_label_subtitle))
        self.wait(0.5)
        
        self.network_display_group = VGroup(self.nodes_vgroup, all_edges_vgroup, all_capacity_labels_vg, all_flow_prefixes_vg)
        # Removed self.network_display_group.arrange_in_grid(rows=1, cols=1) - This was the error source
        self.play(self.network_display_group.animate.scale(0.85).to_corner(DL, buff=BUFF_MED)) # Adjusted scale and buff
        self.play(ReplacementTransform(current_status_text, Text("",font_size=1))) # Clear status text area
        self.wait(1)

        # --- Part B: Dynamic Dinitz Algorithm Animation ---
        self.levels = {v_id: -1 for v_id in self.vertices_data}
        self.ptr = {v_id: 0 for v_id in self.vertices_data} 

        dinitz_title_text = Text("2. Dinitz Algorithm Execution", font_size=SECTION_TITLE_FONT_SIZE).next_to(main_title, DOWN, buff=BUFF_LARGE)
        self.play(Write(dinitz_title_text))
        self.wait(0.5)

        # --- Phase 1 ---
        phase_text = Text("Phase 1", font_size=PHASE_TEXT_FONT_SIZE, weight=BOLD).next_to(dinitz_title_text, DOWN, buff=BUFF_MED)
        self.play(Write(phase_text))

        self.algo_status_text = Text("", font_size=STATUS_TEXT_FONT_SIZE).next_to(phase_text, DOWN, buff=BUFF_SMALL)
        self.add(self.algo_status_text) 
        self.update_status_text_manim("Building Level Graph (BFS from S=1)")


        q_bfs = collections.deque()
        self.levels = {v_id: -1 for v_id in self.vertices_data} 

        current_bfs_level_num = 0
        self.levels[self.source_node] = current_bfs_level_num
        q_bfs.append(self.source_node) 
        
        level_display_vgroup = VGroup().to_corner(DR, buff=BUFF_MED) 
        self.add(level_display_vgroup)

        source_node_dot = self.node_mobjects[self.source_node][0] 
        self.play(source_node_dot.animate.set_color(LEVEL_COLORS[0]).scale(1.1), run_time=0.5)
        l_text_mobj = Text(f"L{current_bfs_level_num}: {{{self.source_node}}}", font_size=LEVEL_TEXT_FONT_SIZE)
        l_text_mobj.align_to(level_display_vgroup, UP+LEFT) 
        level_display_vgroup.add(l_text_mobj)
        self.play(Write(l_text_mobj))

        # --- Refactored BFS Animation Loop ---
        while q_bfs: 
            nodes_to_process_this_level = list(q_bfs) 
            q_bfs.clear() 
            if not nodes_to_process_this_level: break
            current_bfs_level_num += 1 
            nodes_found_for_next_level_set = set()
            node_color_animations_for_new_level = []

            for u_bfs in nodes_to_process_this_level: 
                indicator_u = SurroundingRectangle(self.node_mobjects[u_bfs], color=YELLOW_C, buff=0.05, corner_radius=0.1, stroke_width=2)
                self.play(Create(indicator_u), run_time=0.1)
                for v_neighbor in self.adj[u_bfs]: 
                    res_cap_uv = self.capacities[(u_bfs, v_neighbor)] - self.flow.get((u_bfs, v_neighbor), 0)
                    if res_cap_uv > 0 and self.levels[v_neighbor] == -1: 
                        self.levels[v_neighbor] = current_bfs_level_num
                        nodes_found_for_next_level_set.add(v_neighbor)
                        q_bfs.append(v_neighbor) 
                        level_color = LEVEL_COLORS[current_bfs_level_num % len(LEVEL_COLORS)]
                        node_v_dot = self.node_mobjects[v_neighbor][0]
                        node_v_label = self.node_mobjects[v_neighbor][1]
                        node_color_animations_for_new_level.append(node_v_dot.animate.set_color(level_color).scale(1.1))
                        rgb_components = color_to_rgb(level_color) 
                        label_color_for_node = BLACK if sum(rgb_components) > 1.5 else WHITE 
                        node_color_animations_for_new_level.append(node_v_label.animate.set_color(label_color_for_node))
                self.play(FadeOut(indicator_u), run_time=0.1)
            
            if node_color_animations_for_new_level: self.play(*node_color_animations_for_new_level, run_time=0.6)

            edge_color_animations_for_level_links = []
            if nodes_found_for_next_level_set:
                for u_prev_level in nodes_to_process_this_level: 
                    for v_newly_leveled in nodes_found_for_next_level_set: 
                        if v_newly_leveled in self.adj[u_prev_level] and self.levels[v_newly_leveled] == self.levels[u_prev_level] + 1:
                            res_cap_uv = self.capacities[(u_prev_level, v_newly_leveled)] - self.flow.get((u_prev_level, v_newly_leveled), 0)
                            if res_cap_uv > 0 :
                                edge_mobj_uv = self.edge_mobjects[(u_prev_level,v_newly_leveled)]
                                edge_color = LEVEL_COLORS[self.levels[u_prev_level] % len(LEVEL_COLORS)] 
                                edge_color_animations_for_level_links.append(edge_mobj_uv.animate.set_color(edge_color).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
            if edge_color_animations_for_level_links: self.play(*edge_color_animations_for_level_links, run_time=0.6)

            if nodes_found_for_next_level_set:
                nodes_str = ", ".join(map(str, sorted(list(nodes_found_for_next_level_set))))
                l_text_mobj = Text(f"L{current_bfs_level_num}: {{{nodes_str}}}", font_size=LEVEL_TEXT_FONT_SIZE)
                l_text_mobj.next_to(level_display_vgroup[-1], DOWN, aligned_edge=LEFT, buff=BUFF_SMALL)
                level_display_vgroup.add(l_text_mobj)
                self.play(Write(l_text_mobj))
                self.wait(0.5)
            if not q_bfs: break
        
        final_bfs_status_text_str = "" ; final_bfs_status_color = WHITE
        if self.levels[self.sink_node] == -1:
            final_bfs_status_text_str = "Sink NOT Reached! Max flow likely found." ; final_bfs_status_color = RED
        else:
            final_bfs_status_text_str = f"Sink Reached at L{self.levels[self.sink_node]}. Level Graph Built." ; final_bfs_status_color = GREEN
        self.update_status_text_manim(final_bfs_status_text_str, color=final_bfs_status_color)
        if self.levels[self.sink_node] == -1: self.wait(3); self.play(*[FadeOut(mob) for mob in self.mobjects]); return 

        # --- Isolate Level Graph Edges --- 
        self.update_status_text_manim("Isolating Level Graph Edges...")
        lg_edge_anims = []; non_lg_edge_anims = []
        for (u,v), edge_mobj in self.edge_mobjects.items():
            is_level_graph_edge = (self.levels.get(u, -1) != -1 and self.levels.get(v, -1) != -1 and \
                                   self.levels[v] == self.levels[u] + 1 and \
                                   (self.capacities[(u,v)] - self.flow.get((u,v),0) > 0) ) 
            if is_level_graph_edge:
                lg_edge_anims.append(edge_mobj.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(LEVEL_COLORS[self.levels[u] % len(LEVEL_COLORS)]))
            else:
                non_lg_edge_anims.append(edge_mobj.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR))
        if non_lg_edge_anims: self.play(*non_lg_edge_anims, run_time=0.7) # Dim non-LG edges
        if lg_edge_anims: self.play(*lg_edge_anims, run_time=0.7) # Highlight LG edges
        self.wait(1)
        self.update_status_text_manim("Level Graph Isolated. Ready for DFS.", color=GREEN)

        # TODO: Animate DFS path finding, flow augmentation...
        
        self.wait(5) 
        # Cleanup
        mobjects_to_fade = Group(*self.mobjects)
        if mobjects_to_fade.submobjects:
             self.play(FadeOut(mobjects_to_fade))
        self.wait(1)

    # Helper for status text update
    def update_status_text_manim(self, text_str, color=WHITE, play_anim=True):
        # Ensure self.algo_status_text exists and is on screen if we are transforming it
        if not hasattr(self, 'algo_status_text') or self.algo_status_text not in self.mobjects:
            # If it doesn't exist or isn't on screen, create and add it.
            # This might happen if it was faded out or not created yet.
            # For simplicity, assume it's created and added in construct, and we just update.
            # If it was faded, self.add(self.algo_status_text) might be needed before Transform.
            pass # Assume it's handled by initial add and subsequent Transforms

        new_text_mobj = Text(text_str, font_size=STATUS_TEXT_FONT_SIZE, color=color)
        new_text_mobj.move_to(self.algo_status_text.get_center()) # Position new text at old text's spot
        
        if play_anim:
            self.play(Transform(self.algo_status_text, new_text_mobj))
        else: # Direct update
            self.remove(self.algo_status_text)
            self.algo_status_text = new_text_mobj
            self.add(self.algo_status_text)
        # Important: After Transform, self.algo_status_text still points to the *original* mobject.
        # To make self.algo_status_text refer to the *new* state (new_text_mobj),
        # Manim's Transform doesn't change the original variable's reference.
        # A common pattern is to fade out old and write new, or use self.become().
        # For simplicity with Transform, we might need to manage which mobject is "current".
        # Let's make `update_status_text_manim` simpler: it replaces the text.
        self.remove(self.algo_status_text) # Remove old mobject from scene
        self.algo_status_text = new_text_mobj # Update instance variable
        self.add(self.algo_status_text) # Add new mobject to scene