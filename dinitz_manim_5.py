from manim import *
import collections

# Helper to get a standard Manim color for levels, cycling through the list
LEVEL_COLORS = [RED_E, ORANGE, YELLOW_D, GREEN_C, BLUE_C, PURPLE_D, PINK]

class DinitzAlgorithmVisualizer(Scene):
    def construct(self):
        # --- Title ---
        main_title = Text("Visualizing Dinitz's Algorithm for Max Flow", font_size=40)
        self.play(Write(main_title))
        self.wait(1)
        self.play(main_title.animate.to_edge(UP).scale(0.8))

        # --- Graph Definition ---
        self.source_node, self.sink_node = 1, 10
        self.vertices_data = list(range(1, 11)) 
        self.edges_with_capacity_list = [
            (1, 2, 25), (1, 3, 30), (1, 4, 20),
            (2, 5, 25),
            (3, 4, 30), (3, 5, 35),
            (4, 6, 30),
            (5, 7, 40), (5, 8, 40),
            (6, 8, 35), (6, 9, 30),
            (7, 10, 20), (8, 10, 20), (9, 10, 20)
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
        self.edge_flow_capacity_labels = {} 

        # --- Part A: Animated Graph Creation ---
        section_title_graph_build = Text("1. Building the Network", font_size=30).next_to(main_title, DOWN, buff=0.5)
        self.play(Write(section_title_graph_build))
        self.wait(0.5)

        nodes_vgroup_on_screen = VGroup() 
        for i, v_id in enumerate(self.vertices_data):
            node_dot = Dot(point=self.graph_layout[v_id], radius=0.3, color=BLUE_E, z_index=2)
            node_label_text = str(v_id)
            node_label = Text(node_label_text, font_size=20, weight=BOLD).move_to(node_dot.get_center()).set_z_index(3)
            self.node_mobjects[v_id] = VGroup(node_dot, node_label)
            nodes_vgroup_on_screen.add(self.node_mobjects[v_id])
            self.play(GrowFromCenter(self.node_mobjects[v_id]), run_time=0.3 + 0.05*i)
        self.wait(0.5)
        self.nodes_vgroup = nodes_vgroup_on_screen

        edges_drawing_text = Text("Adding Edges (Flow / Capacity)", font_size=22).next_to(section_title_graph_build, DOWN, buff=0.5)
        self.play(ReplacementTransform(section_title_graph_build, edges_drawing_text)) 

        all_edges_vgroup = VGroup()
        all_labels_vgroup = VGroup()

        for i, (u, v, cap) in enumerate(self.edges_with_capacity_list):
            node_u_vg = self.node_mobjects[u]; node_v_vg = self.node_mobjects[v]
            line = Line(node_u_vg[0].get_center(), node_v_vg[0].get_center(), z_index=0)
            line.put_start_and_end_on(
                node_u_vg[0].get_critical_point(line.get_unit_vector()),
                node_v_vg[0].get_critical_point(-line.get_unit_vector())
            )
            arrow = Arrow(start=line.get_start(), end=line.get_end(), stroke_width=4, color=GREY_D,
                          max_tip_length_to_length_ratio=0.15, tip_length=0.2)
            self.edge_mobjects[(u,v)] = arrow
            all_edges_vgroup.add(arrow)
            
            flow_val = self.flow.get((u,v), 0)
            label_text_str = f"{flow_val}/{cap}"
            perp_direction = rotate_vector(arrow.get_unit_vector(), TAU/4) 
            label_pos = arrow.get_center() + perp_direction * 0.35
            
            if (u,v) in [(3,4), (6,8), (5,8), (1,3), (4,6)]: label_pos = arrow.get_center() - perp_direction * 0.35 # Manual adjustments

            flow_label_mobj = Text(label_text_str, font_size=16, color=DARK_GREY, weight=NORMAL).move_to(label_pos).set_z_index(1)
            self.edge_flow_capacity_labels[(u,v)] = flow_label_mobj
            all_labels_vgroup.add(flow_label_mobj)
            self.play(GrowArrow(arrow), Write(flow_label_mobj), run_time=0.3 + 0.05*i)
        
        self.play(FadeOut(edges_drawing_text))
        self.wait(0.5)
        
        self.network_display_group = VGroup(self.nodes_vgroup, all_edges_vgroup, all_labels_vgroup)
        self.play(self.network_display_group.animate.scale(0.8).to_edge(DOWN, buff=0.3))
        self.wait(1)

        # --- Part B: Dynamic Dinitz Algorithm Animation ---
        self.levels = {v_id: -1 for v_id in self.vertices_data}
        self.ptr = {v_id: 0 for v_id in self.vertices_data} 

        dinitz_steps_title = Text("2. Dinitz Algorithm: Step-by-Step", font_size=28).next_to(main_title, DOWN, buff=0.5)
        self.play(Write(dinitz_steps_title))
        self.wait(1)

        # --- Phase 1 ---
        phase_text = Text("Phase 1", font_size=24, weight=BOLD).next_to(dinitz_steps_title, DOWN, buff=0.3)
        self.play(Write(phase_text))

        bfs_status_text = Text("Building Level Graph (BFS from Source 1)", font_size=20).next_to(phase_text, DOWN, buff=0.3)
        self.play(Write(bfs_status_text))

        q_bfs = collections.deque()
        self.levels = {v_id: -1 for v_id in self.vertices_data} 

        current_bfs_level_num = 0
        self.levels[self.source_node] = current_bfs_level_num
        q_bfs.append(self.source_node) 
        
        level_display_vgroup = VGroup().to_corner(UL).shift(DOWN*1.0 + RIGHT*0.5) 

        source_node_dot = self.node_mobjects[self.source_node][0] 
        self.play(source_node_dot.animate.set_color(LEVEL_COLORS[0]).scale(1.1), run_time=0.5)
        l_text_mobj = Text(f"L{current_bfs_level_num}: {{{self.source_node}}}", font_size=18)
        l_text_mobj.align_to(level_display_vgroup, UL)
        level_display_vgroup.add(l_text_mobj)
        self.play(Write(l_text_mobj))

        while q_bfs: 
            nodes_to_process_this_level = list(q_bfs)
            q_bfs.clear() 
            
            if not nodes_to_process_this_level: break

            current_bfs_level_num += 1 
            nodes_found_in_next_level = []
            
            level_specific_edge_animations = []
            level_specific_node_animations = []

            for u_bfs in nodes_to_process_this_level:
                indicator_u = SurroundingRectangle(self.node_mobjects[u_bfs], color=YELLOW, buff=0.05, corner_radius=0.1, stroke_width=2)
                self.play(Create(indicator_u), run_time=0.2)

                for v_neighbor in self.adj[u_bfs]: 
                    res_cap_uv = self.capacities[(u_bfs, v_neighbor)] - self.flow.get((u_bfs, v_neighbor), 0)
                    if res_cap_uv > 0 and self.levels[v_neighbor] == -1: 
                        self.levels[v_neighbor] = current_bfs_level_num
                        nodes_found_in_next_level.append(v_neighbor)
                        q_bfs.append(v_neighbor) 

                        level_color = LEVEL_COLORS[current_bfs_level_num % len(LEVEL_COLORS)]
                        edge_mobj_uv = self.edge_mobjects[(u_bfs,v_neighbor)]
                        node_v_dot = self.node_mobjects[v_neighbor][0]
                        node_v_label = self.node_mobjects[v_neighbor][1]

                        level_specific_edge_animations.append(edge_mobj_uv.animate.set_color(level_color))
                        level_specific_node_animations.append(node_v_dot.animate.set_color(level_color).scale(1.1))
                        
                        rgb_components = color_to_rgb(level_color) 
                        label_color_for_node = BLACK if sum(rgb_components) > 1.5 else WHITE 
                        level_specific_node_animations.append(node_v_label.animate.set_color(label_color_for_node))
                
                self.play(FadeOut(indicator_u), run_time=0.2)
            
            current_anims_to_play = []
            if level_specific_edge_animations: current_anims_to_play.extend(level_specific_edge_animations)
            if level_specific_node_animations: current_anims_to_play.extend(level_specific_node_animations)
            if current_anims_to_play: self.play(*current_anims_to_play, run_time=0.8)

            if nodes_found_in_next_level:
                nodes_str = ", ".join(map(str, sorted(nodes_found_in_next_level)))
                l_text_mobj = Text(f"L{current_bfs_level_num}: {{{nodes_str}}}", font_size=18)
                l_text_mobj.next_to(level_display_vgroup[-1], DOWN, aligned_edge=LEFT, buff=0.15)
                level_display_vgroup.add(l_text_mobj)
                self.play(Write(l_text_mobj))
                self.wait(0.5)
            
            if not q_bfs: break
        
        self.current_status_text_mobject = Text("",font_size=22).next_to(bfs_status_text, DOWN)
        self.add(self.current_status_text_mobject) 

        if self.levels[self.sink_node] == -1:
            sink_status_mobj = Text("Sink NOT Reached in BFS! Max flow found.", color=RED)
            self.play(ReplacementTransform(bfs_status_text, VGroup()), 
                      Transform(self.current_status_text_mobject, sink_status_mobj))
            self.wait(3)
            self.play(*[FadeOut(mob) for mob in self.mobjects if isinstance(mob, Mobject)])
            return 
        else:
            sink_status_mobj = Text(f"Sink Reached at L{self.levels[self.sink_node]}. Level Graph Built.", color=GREEN)
            self.play(ReplacementTransform(bfs_status_text, VGroup()), 
                      Transform(self.current_status_text_mobject, sink_status_mobj))
            self.wait(1)

        # --- Isolate Level Graph Edges --- 
        isolate_lg_text = Text("Isolating Level Graph Edges...", font_size=20).next_to(phase_text, DOWN, buff=0.3)
        self.play(ReplacementTransform(self.current_status_text_mobject, isolate_lg_text)) 
        self.current_status_text_mobject = isolate_lg_text 

        lg_edge_anims = []
        non_lg_edge_anims = []
        for (u,v), edge_mobj in self.edge_mobjects.items():
            is_level_graph_edge = (self.levels.get(u, -1) != -1 and \
                                   self.levels.get(v, -1) != -1 and \
                                   self.levels[v] == self.levels[u] + 1 and \
                                   (self.capacities[(u,v)] - self.flow.get((u,v),0) > 0) ) 
            
            if is_level_graph_edge:
                lg_edge_anims.append(edge_mobj.animate.set_stroke(opacity=1.0, width=5))
                # Corrected line using global LEVEL_COLORS:
                lg_edge_anims.append(edge_mobj.animate.set_color(LEVEL_COLORS[self.levels[u] % len(LEVEL_COLORS)]))
            else:
                non_lg_edge_anims.append(edge_mobj.animate.set_stroke(opacity=0.2, color=GREY_C))
        
        if non_lg_edge_anims: self.play(*non_lg_edge_anims, run_time=1.0)
        if lg_edge_anims: self.play(*lg_edge_anims, run_time=0.5) 
        self.wait(1)

        # --- TODO: Animate DFS path finding (based on self.levels and residual graph) ---
        # --- TODO: Animate flow augmentation and residual graph updates ---
        
        self.wait(5) 
        all_scene_items_to_fade = VGroup(main_title, self.network_display_group, dinitz_steps_title, phase_text, self.current_status_text_mobject, level_display_vgroup)
        # Using Group for more permissive Mobject types if needed, though VGroup should be fine here.
        # Filter self.mobjects to only include those we want to explicitly fade.
        # For robustly fading all *user-added visual mobjects*:
        # It's often best to add them to a master VGroup as they are created for the scene.
        # For now, explicitly list main groups.
        self.play(FadeOut(all_scene_items_to_fade), run_time=1)
        self.wait(1)