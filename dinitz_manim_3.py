from manim import *
import collections

class DinitzManimExplanation(Scene):
    def construct(self):
        # --- Title ---
        title_main = Text("Dinitz's Algorithm: Phase 1", font_size=36).to_edge(UP)
        self.play(Write(title_main))
        self.wait(0.5)

        # --- Define Graph (same as before) ---
        vertices = list(range(1, 11))
        edges_input_tuples = [
          (1, 2), (1, 3), (1, 4), (3, 4), (2, 5), (3, 5), (4, 6),
          (5, 7), (5, 8), (6, 8), (6, 9), (7, 10), (8, 10), (9, 10)
        ]
        capacities_dict = {
            (1, 2): 25, (1, 3): 30, (1, 4): 20, (3, 4): 30, (2, 5): 25, (3, 5): 35, (4, 6): 30,
            (5, 7): 40, (5, 8): 40, (6, 8): 35, (6, 9): 30, (7, 10): 20, (8, 10): 20, (9, 10): 20
        }
        source_node, sink_node = 1, 10
        graph_layout = {
            1: [-6, 0, 0], 2: [-4, 2, 0], 3: [-4, 0, 0], 4: [-4, -2, 0],
            5: [-1.5, 1, 0], 6: [-1.5, -1, 0],
            7: [1.5, 2, 0], 8: [1.5, 0, 0], 9: [1.5, -2, 0],
            10: [4, 0, 0]
        }
        
        g = Graph(vertices, edges_input_tuples, layout=graph_layout, labels=True,
                  vertex_config={"radius": 0.35, "color": BLUE_D, "fill_opacity": 0.9, "stroke_color": WHITE, "stroke_width":2},
                  edge_config={"stroke_width": 3, "color": GREY_B})

        edge_cap_labels = VGroup()
        # ... (edge capacity label creation code - same as before, ensure it's here)
        for u, v in edges_input_tuples:
            cap = capacities_dict.get((u,v)) 
            if cap:
                edge_mo = g.edges.get((u,v)) or g.edges.get((v,u))
                if edge_mo:
                    mid_point = edge_mo.get_center()
                    direction_vector = edge_mo.get_unit_vector()
                    offset_dir = np.array([-direction_vector[1], direction_vector[0], 0]) * 0.3 
                    label_text_obj = Text(str(cap), font_size=18, color=BLACK).move_to(mid_point + offset_dir)
                    edge_cap_labels.add(label_text_obj)

        graph_group = VGroup(g, edge_cap_labels).scale(0.85).move_to(ORIGIN+DOWN*0.3)
        self.play(Create(g), Write(edge_cap_labels))
        self.wait(0.5)

        # --- BFS Animation for Levels (condensed for brevity, full logic from previous step) ---
        bfs_status_text = Text("Building Level Graph (BFS)...", font_size=24).next_to(title_main, DOWN, buff=0.2)
        self.play(Write(bfs_status_text))
        
        levels = {node: -1 for node in vertices} 
        level_texts_vg = VGroup().to_corner(UL).shift(RIGHT*0.5 + DOWN*0.5)
        level_colors = [RED_E, ORANGE, YELLOW_D, GREEN_C, BLUE_C, PURPLE_C] 
        
        # --- Simulating BFS completion and applying final level colors ---
        # Derived levels from Phase 1:
        # L0: {1}
        # L1: {2, 3, 4}
        # L2: {5, 6}
        # L3: {7, 8, 9}
        # L4: {10}
        simulated_levels = {1:0, 2:1, 3:1, 4:1, 5:2, 6:2, 7:3, 8:3, 9:3, 10:4}
        animations_bfs_nodes = []
        for node, level in simulated_levels.items():
            levels[node] = level # Store for later use
            if level != -1:
                animations_bfs_nodes.append(g.vertices[node].animate.set_fill(level_colors[level % len(level_colors)], opacity=1))
        
        level_texts_display = [
            "L0: {1}", "L1: {2, 3, 4}", "L2: {5, 6}", "L3: {7, 8, 9}", "L4: {10}"
        ]
        for i, txt in enumerate(level_texts_display):
            lt = Text(txt, font_size=20)
            if i > 0: lt.next_to(level_texts_vg[-1], DOWN, aligned_edge=LEFT)
            level_texts_vg.add(lt)

        self.play(*animations_bfs_nodes, Write(level_texts_vg), run_time=1)
        self.play(FadeOut(bfs_status_text))
        self.wait(0.5)

        # --- Show level graph edges only (dim others) ---
        level_graph_status_text = Text("Isolating Level Graph Edges", font_size=24).next_to(title_main, DOWN, buff=0.2)
        self.play(Write(level_graph_status_text))

        level_graph_edges_anims = []
        non_level_graph_edges_anims = []
        level_graph_edge_color = WHITE 
        dim_color = GREY_D
        dim_opacity = 0.25

        for u, v in edges_input_tuples:
            is_level_graph_edge = (levels.get(u, -1) != -1 and levels.get(v, -1) != -1 and \
                                   levels[v] == levels[u] + 1 and \
                                   capacities_dict.get((u,v),0) > 0) # Phase 1: cap > 0 is res_cap > 0
            
            edge_mobject = g.edges.get((u,v))
            if edge_mobject:
                if is_level_graph_edge:
                    level_graph_edges_anims.append(
                        edge_mobject.animate.set_color(level_colors[levels[u]%len(level_colors)]).set_stroke(opacity=1.0, width=4.5)
                    ) # Color by source node's level
                else:
                    non_level_graph_edges_anims.append(
                        edge_mobject.animate.set_color(dim_color).set_stroke(opacity=dim_opacity, width=2)
                    )
        
        if non_level_graph_edges_anims: self.play(*non_level_graph_edges_anims, run_time=0.7)
        if level_graph_edges_anims: self.play(*level_graph_edges_anims, run_time=0.7)
        self.play(FadeOut(level_graph_status_text))
        self.wait(1)
        
        # --- TODO 2: Animate DFS path finding ---
        dfs_status_text = Text("DFS: Finding Augmenting Path in Level Graph", font_size=24).next_to(title_main, DOWN, buff=0.2)
        self.play(Write(dfs_status_text))
        self.wait(0.5)

        # DFS path to find: 1 -> 2 -> 5 -> 7 -> 10
        # Colors for DFS
        DFS_EXPLORE_COLOR = PINK # Color for edge/node currently being explored
        DFS_PATH_COLOR = YELLOW_C # Color for edges/nodes on the final found path
        DFS_BACKTRACK_NODE_COLOR = GREY_BROWN # Color for nodes visited but not in final path
        DFS_BACKTRACK_EDGE_COLOR = GREY # Color for edges tried but not in final path (or back to level graph color)

        # This is a manual animation of one specific DFS path.
        # A general recursive DFS animation function would be more complex.
        
        # Path: 1 -> 2
        self.play(
            g.vertices[1].animate.set_stroke(color=DFS_PATH_COLOR, width=4),
            g.vertices[2].animate.set_fill(DFS_EXPLORE_COLOR),
            g.edges[(1,2)].animate.set_color(DFS_EXPLORE_COLOR).set_stroke(width=5.5),
            run_time=0.7
        )
        self.wait(0.3)
        
        # Path: 2 -> 5
        self.play(
            g.vertices[2].animate.set_stroke(color=DFS_PATH_COLOR, width=4).set_fill(level_colors[levels[2]%len(level_colors)]), # Node 2 is part of path
            g.vertices[5].animate.set_fill(DFS_EXPLORE_COLOR),
            g.edges[(2,5)].animate.set_color(DFS_EXPLORE_COLOR).set_stroke(width=5.5),
            run_time=0.7
        )
        self.wait(0.3)

        # Path: 5 -> 7
        self.play(
            g.vertices[5].animate.set_stroke(color=DFS_PATH_COLOR, width=4).set_fill(level_colors[levels[5]%len(level_colors)]), # Node 5 is part of path
            g.vertices[7].animate.set_fill(DFS_EXPLORE_COLOR),
            g.edges[(5,7)].animate.set_color(DFS_EXPLORE_COLOR).set_stroke(width=5.5),
            run_time=0.7
        )
        self.wait(0.3)

        # Path: 7 -> 10 (Sink reached)
        self.play(
            g.vertices[7].animate.set_stroke(color=DFS_PATH_COLOR, width=4).set_fill(level_colors[levels[7]%len(level_colors)]), # Node 7 is part of path
            g.vertices[10].animate.set_stroke(color=DFS_PATH_COLOR, width=4).set_fill(level_colors[levels[10]%len(level_colors)]),# Node 10 is part of path & sink
            g.edges[(7,10)].animate.set_color(DFS_EXPLORE_COLOR).set_stroke(width=5.5),
            run_time=0.7
        )
        self.wait(0.3)

        # Highlight the full path found
        found_path_nodes = [1, 2, 5, 7, 10]
        found_path_edges = [(1,2), (2,5), (5,7), (7,10)]
        
        path_highlight_anims_nodes = []
        for node_idx in found_path_nodes:
            path_highlight_anims_nodes.append(g.vertices[node_idx].animate.set_fill(DFS_PATH_COLOR).set_stroke(color=RED, width=3))
        
        path_highlight_anims_edges = []
        for u,v in found_path_edges:
            path_highlight_anims_edges.append(g.edges[(u,v)].animate.set_color(DFS_PATH_COLOR).set_stroke(width=6))

        path_found_text = Text("Augmenting Path Found!", font_size=24, color=DFS_PATH_COLOR)
        path_found_text.next_to(dfs_status_text, DOWN, buff=0.3)
        self.play(
            *path_highlight_anims_nodes,
            *path_highlight_anims_edges,
            Write(path_found_text),
            run_time=1.0
        )
        self.wait(1)

        # Calculate bottleneck for this path (1->2->5->7->10)
        # Capacities: C(1,2)=25, C(2,5)=25, C(5,7)=40, C(7,10)=20
        # Bottleneck = 20
        bottleneck_val = 20
        bottleneck_text = Text(f"Bottleneck capacity: {bottleneck_val}", font_size=24)
        bottleneck_text.next_to(path_found_text, DOWN, buff=0.2)
        self.play(Write(bottleneck_text))
        self.wait(2)

        # Store the found path and bottleneck for the next TODO
        self.found_path_for_flow_aug = {
            "nodes": found_path_nodes,
            "edges": found_path_edges,
            "bottleneck": bottleneck_val
        }

        self.play(FadeOut(dfs_status_text), FadeOut(path_found_text), FadeOut(bottleneck_text))
        self.wait(1)
        # Graph with path highlighted remains for next step.
        # Levels text (level_texts_vg) also remains.

        # TODO: Animate flow augmentation and residual graph updates