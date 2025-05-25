from manim import *
import collections

class DinitzManimExplanation(Scene):
    def construct(self):
        # --- Title ---
        title_main = Text("Dinitz's Algorithm: Phase 1 - Blocking Flow", font_size=36).to_edge(UP)
        self.play(Write(title_main))
        self.wait(0.5)

        # --- Define Graph ---
        vertices = list(range(1, 11))
        edges_input_tuples = [
          (1, 2), (1, 3), (1, 4), (3, 4), (2, 5), (3, 5), (4, 6),
          (5, 7), (5, 8), (6, 8), (6, 9), (7, 10), (8, 10), (9, 10)
        ]
        self.capacities_dict = {
            (1, 2): 25, (1, 3): 30, (1, 4): 20, (3, 4): 30, (2, 5): 25, (3, 5): 35, (4, 6): 30,
            (5, 7): 40, (5, 8): 40, (6, 8): 35, (6, 9): 30, (7, 10): 20, (8, 10): 20, (9, 10): 20
        }
        source_node, sink_node = 1, 10
        graph_layout = {1: [-6,0,0], 2: [-4,2,0], 3: [-4,0,0], 4: [-4,-2,0], 5: [-1.5,1,0], 6: [-1.5,-1,0], 7: [1.5,2,0], 8: [1.5,0,0], 9: [1.5,-2,0], 10: [4,0,0]}
        
        self.g = Graph(vertices, edges_input_tuples, layout=graph_layout, labels=True,
                  vertex_config={"radius": 0.35, "color": BLUE_D, "fill_opacity": 0.9, "stroke_color": WHITE, "stroke_width":2},
                  edge_config={"stroke_width": 3, "color": GREY_B})
        
        self.flow_on_edges = {edge: 0 for edge in edges_input_tuples} # u,v -> flow
        self.edge_label_mobjects = {} # (u,v) -> TextMobject
        initial_edge_labels_vg = VGroup()
        for u, v in edges_input_tuples:
            cap = self.capacities_dict.get((u,v))
            if cap is not None:
                edge_mo = self.g.edges.get((u,v))
                if edge_mo:
                    mid_point = edge_mo.get_center()
                    direction_vector = edge_mo.get_unit_vector()
                    offset_dir = np.array([-direction_vector[1], direction_vector[0], 0]) * 0.3
                    label_text_obj = Text(f"0/{cap}", font_size=18, color=BLACK).move_to(mid_point + offset_dir)
                    initial_edge_labels_vg.add(label_text_obj)
                    self.edge_label_mobjects[(u,v)] = label_text_obj
        
        self.graph_group = VGroup(self.g, initial_edge_labels_vg).scale(0.85).move_to(ORIGIN+DOWN*0.3)
        self.play(Create(self.g), Write(initial_edge_labels_vg))
        self.wait(0.5)

        # --- BFS State (Applied Directly) ---
        bfs_status_text = Text("Phase 1 Level Graph Established", font_size=24, weight=BOLD).next_to(title_main, DOWN, buff=0.2)
        self.play(Write(bfs_status_text))

        self.levels = {1:0, 2:1, 3:1, 4:1, 5:2, 6:2, 7:3, 8:3, 9:3, 10:4}
        level_colors = [RED_E, ORANGE, YELLOW_D, GREEN_C, BLUE_C, PURPLE_C]
        bfs_node_animations = []
        for node, level in self.levels.items():
            if level != -1: 
                bfs_node_animations.append(self.g.vertices[node].animate.set_fill(level_colors[level % len(level_colors)], opacity=1))
        
        level_texts_display_data = {0:[1], 1:[2,3,4], 2:[5,6], 3:[7,8,9], 4:[10]}
        current_level_texts_vg = VGroup() # Start with an empty VGroup for current texts
        for i in range(len(level_texts_display_data)):
            nodes_str = ", ".join(map(str, sorted(level_texts_display_data.get(i,[]))))
            lt = Text(f"L{i}: {{{nodes_str}}}", font_size=20)
            if i > 0 and current_level_texts_vg: lt.next_to(current_level_texts_vg[-1], DOWN, aligned_edge=LEFT)
            current_level_texts_vg.add(lt)
        current_level_texts_vg.to_corner(UL).shift(RIGHT*0.5 + DOWN*0.5)
        
        self.play(*bfs_node_animations, Write(current_level_texts_vg), run_time=1)
        self.level_texts_vg = current_level_texts_vg # Keep reference if needed later
        
        level_graph_edges_anims = []
        non_level_graph_edges_anims = []
        for u, v in edges_input_tuples:
            is_level_graph_edge = (self.levels.get(u, -1) != -1 and self.levels.get(v, -1) != -1 and \
                                   self.levels[v] == self.levels[u] + 1 and \
                                   self.capacities_dict.get((u,v),0) > 0)
            edge_mobject = self.g.edges.get((u,v))
            if edge_mobject:
                if is_level_graph_edge:
                    level_graph_edges_anims.append(
                        edge_mobject.animate.set_color(level_colors[self.levels[u]%len(level_colors)]).set_stroke(opacity=1.0, width=4.5)
                    )
                else:
                    non_level_graph_edges_anims.append(
                        edge_mobject.animate.set_color(GREY_D).set_stroke(opacity=0.25, width=2)
                    )
        if non_level_graph_edges_anims: self.play(*non_level_graph_edges_anims, run_time=0.7)
        if level_graph_edges_anims: self.play(*level_graph_edges_anims, run_time=0.7)
        self.play(FadeOut(bfs_status_text))
        self.wait(0.5)

        # --- First Path Augmentation (State Applied Directly) ---
        path1_details = {"nodes": [1,2,5,7,10], "edges": [(1,2),(2,5),(5,7),(7,10)], "bottleneck": 20}
        
        for u_p1,v_p1 in path1_details["edges"]:
            self.flow_on_edges[(u_p1,v_p1)] += path1_details["bottleneck"]
            new_flow_p1 = self.flow_on_edges[(u_p1,v_p1)]
            cap_p1 = self.capacities_dict[(u_p1,v_p1)]
            old_label_mobject_p1 = self.edge_label_mobjects[(u_p1,v_p1)]
            new_label_mobject_p1 = Text(f"{new_flow_p1}/{cap_p1}", font_size=18, color=BLACK).move_to(old_label_mobject_p1.get_center())
            self.remove(old_label_mobject_p1).add(new_label_mobject_p1) 
            self.edge_label_mobjects[(u_p1,v_p1)] = new_label_mobject_p1
            if new_flow_p1 == cap_p1: self.g.edges[(u_p1,v_p1)].set_color(RED_D) 
            # Edges not saturated by path 1 retain their level graph color.
            # The next step will reset them explicitly if needed.

        path1_augmented_text = Text("Path 1 (1-2-5-7-10) augmented. Flow: 20.", font_size=20).next_to(title_main, DOWN, buff=0.2)
        self.play(Write(path1_augmented_text))
        self.wait(1)
        
        # --- Start Animation for Finding Second Augmenting Path ---
        status_text = Text("DFS: Searching for Path 2 in Level Graph...", font_size=24).move_to(path1_augmented_text)
        self.play(ReplacementTransform(path1_augmented_text, status_text))
        self.wait(1)

        reset_anims_p1_edges = []
        path1_non_saturated_edges_after_flow = [(1,2), (2,5), (5,7)] # (7,10) is saturated
        for u,v in path1_non_saturated_edges_after_flow:
            if self.flow_on_edges.get((u,v),0) < self.capacities_dict.get((u,v),0) : # Double check not saturated
                 reset_anims_p1_edges.append(self.g.edges[(u,v)].animate.set_color(level_colors[self.levels[u]%len(level_colors)]).set_stroke(width=4.5))
        if reset_anims_p1_edges: self.play(*reset_anims_p1_edges, run_time=0.5)
        
        DFS_EXPLORE_COLOR = PINK
        CURRENT_DFS_PATH_COLOR = GOLD 
        self.play(self.g.vertices[source_node].animate.set_fill(CURRENT_DFS_PATH_COLOR).set_stroke(color=RED_D, width=3))
        self.wait(0.5)

        # --- Animate DFS for Path 2: 1 -> 2 -> 5 -> (try 7, backtrack) -> 8 -> 10 ---
        # Step 1: 1 -> 2 
        self.play(
            self.g.edges[(1,2)].animate.set_color(DFS_EXPLORE_COLOR).set_stroke(width=5.5),
            self.g.vertices[2].animate.set_fill(DFS_EXPLORE_COLOR),
            run_time=0.7
        )
        self.wait(0.3)

        # Step 2: 2 -> 5
        self.play(
            self.g.vertices[1].animate.set_fill(CURRENT_DFS_PATH_COLOR), 
            self.g.edges[(1,2)].animate.set_color(CURRENT_DFS_PATH_COLOR).set_stroke(width=6), 
            self.g.vertices[2].animate.set_fill(CURRENT_DFS_PATH_COLOR), 
            self.g.edges[(2,5)].animate.set_color(DFS_EXPLORE_COLOR).set_stroke(width=5.5), 
            self.g.vertices[5].animate.set_fill(DFS_EXPLORE_COLOR),
            run_time=0.7
        )
        self.wait(0.3)
        
        # Step 3: From 5, try 5 -> 7
        self.play(
            self.g.edges[(2,5)].animate.set_color(CURRENT_DFS_PATH_COLOR).set_stroke(width=6), 
            self.g.vertices[5].animate.set_fill(CURRENT_DFS_PATH_COLOR), 
            self.g.edges[(5,7)].animate.set_color(DFS_EXPLORE_COLOR).set_stroke(width=5.5), 
            self.g.vertices[7].animate.set_fill(DFS_EXPLORE_COLOR),
            run_time=0.7
        )
        self.wait(0.3)

        # Step 4: From 7, try 7 -> 10 (SATURATED!)
        # Edge (7,10) should already be RED_D from Path 1 saturation
        blocked_edge_flash = ShowPassingFlash(self.g.edges[(7,10)].copy().set_color(RED_B), time_width=0.5, run_time=0.7)
        blocked_text = Text("Edge (7,10) Saturated! Path Blocked.", font_size=20, color=RED_A).next_to(self.g.edges[(7,10)], UR, buff=0.1)
        self.play(blocked_edge_flash, Write(blocked_text), run_time=0.7)
        self.wait(0.5)

        # Step 5: Backtrack from 7 to 5
        backtrack_text = Text("Backtrack: 7 -> 5", font_size=20).next_to(blocked_text, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(Write(backtrack_text), run_time=0.5)
        self.play(
            self.g.edges[(5,7)].animate.set_color(level_colors[self.levels[5]%len(level_colors)]).set_stroke(width=4.5),
            self.g.vertices[7].animate.set_fill(level_colors[self.levels[7]%len(level_colors)]),
            FadeOut(blocked_text),
            run_time=0.7
        )
        self.wait(0.3)

        # Step 6: From 5, try 5 -> 8
        self.play(FadeOut(backtrack_text), run_time=0.2) 
        self.play(
            self.g.edges[(5,8)].animate.set_color(DFS_EXPLORE_COLOR).set_stroke(width=5.5), 
            self.g.vertices[8].animate.set_fill(DFS_EXPLORE_COLOR),
            run_time=0.7
        )
        self.wait(0.3)

        # Step 7: From 8, try 8 -> 10 - Sink Reached!
        self.play(
            self.g.vertices[5].animate.set_fill(CURRENT_DFS_PATH_COLOR), 
            self.g.edges[(5,8)].animate.set_color(CURRENT_DFS_PATH_COLOR).set_stroke(width=6), 
            self.g.vertices[8].animate.set_fill(CURRENT_DFS_PATH_COLOR), 
            self.g.edges[(8,10)].animate.set_color(DFS_EXPLORE_COLOR).set_stroke(width=5.5),
            self.g.vertices[10].animate.set_fill(CURRENT_DFS_PATH_COLOR), 
             run_time=0.7
        )
        self.wait(0.3)
        self.play(self.g.edges[(8,10)].animate.set_color(CURRENT_DFS_PATH_COLOR).set_stroke(width=6)) # Finalize last edge


        # --- Path 2 Found ---
        path2_found_text = Text("Augmenting Path 2 Found!", font_size=22, color=CURRENT_DFS_PATH_COLOR)
        path2_found_text.next_to(status_text, DOWN, buff=0.3)
        self.play(ReplacementTransform(status_text, path2_found_text))
        
        path2_bottleneck_val = 5
        path2_bottleneck_text = Text(f"Bottleneck: {path2_bottleneck_val}", font_size=22)
        path2_bottleneck_text.next_to(path2_found_text, DOWN, buff=0.2)
        self.play(Write(path2_bottleneck_text))
        self.wait(1)

        # --- Animate Flow Augmentation for Path 2 ---
        flow_aug2_status_text = Text(f"Pushing {path2_bottleneck_val} units along Path 2", font_size=24).next_to(title_main, DOWN, buff=0.2)
        self.play(Write(flow_aug2_status_text))

        path2_edges_tuples = [(1,2), (2,5), (5,8), (8,10)]
        passing_flash_anims_p2 = []
        for u,v in path2_edges_tuples:
            passing_flash_anims_p2.append(Succession(
                self.g.edges[(u,v)].animate.set_stroke(color=GREEN_C, width=8), # Changed GREEN_SCREEN
                self.g.edges[(u,v)].animate.set_stroke(color=CURRENT_DFS_PATH_COLOR, width=6),
                run_time=0.4
            ))
        self.play(LaggedStart(*passing_flash_anims_p2, lag_ratio=0.3), run_time=len(passing_flash_anims_p2)*0.3)
        self.wait(0.5)

        label_update_anims_p2 = []
        saturation_anims_p2 = []
        newly_saturated_edges_p2_text = []

        for u,v in path2_edges_tuples:
            self.flow_on_edges[(u,v)] += path2_bottleneck_val 
            new_flow = self.flow_on_edges[(u,v)]
            cap = self.capacities_dict[(u,v)]
            
            old_label_mobject = self.edge_label_mobjects[(u,v)]
            # Important: Create new Text mobject for ReplacementTransform
            new_label_mobject = Text(f"{new_flow}/{cap}", font_size=18, color=BLACK).move_to(old_label_mobject.get_center())
            
            label_update_anims_p2.append(ReplacementTransform(old_label_mobject, new_label_mobject))
            self.edge_label_mobjects[(u,v)] = new_label_mobject 

            if new_flow == cap: 
                saturation_anims_p2.append(self.g.edges[(u,v)].animate.set_color(RED_D).set_stroke(width=7))
                newly_saturated_edges_p2_text.append(f"({u},{v})")
        
        if label_update_anims_p2: self.play(*label_update_anims_p2, run_time=1.5)
        if saturation_anims_p2:
            self.play(*saturation_anims_p2, run_time=1.0)
            if newly_saturated_edges_p2_text:
                saturated_info_text_p2 = Text(f"Edges {', '.join(newly_saturated_edges_p2_text)} now saturated.", font_size=20, color=RED_D)
                saturated_info_text_p2.next_to(flow_aug2_status_text, DOWN, buff=0.4) # Increased buff
                self.play(Write(saturated_info_text_p2))
                self.wait(1)
                self.play(FadeOut(saturated_info_text_p2))
        
        self.wait(1)
        self.play(FadeOut(flow_aug2_status_text), FadeOut(path2_found_text), FadeOut(path2_bottleneck_text))
        self.wait(1)

        end_text = Text("Second flow augmentation complete.", font_size=24)
        end_text.next_to(self.graph_group, DOWN, buff=0.3)
        self.play(Write(end_text))
        self.wait(3)
        
        # Fade out all visual elements before ending
        all_mobjects_to_fade = VGroup(title_main, self.graph_group, self.level_texts_vg, end_text)
        # Filter out None or non-Mobjects just in case, though all here should be fine.
        # For robustly fading everything actually on screen:
        self.play(*[FadeOut(mob) for mob in self.mobjects if isinstance(mob, Mobject)])