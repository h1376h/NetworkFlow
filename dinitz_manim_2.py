from manim import *
import collections

# Manim Community Edition uses config.background_color
# You can set it globally or per scene. For this example, default is fine.
# config.background_color = GREY_E 

class DinitzManimExplanation(Scene):
    def construct(self):
        # --- Title ---
        title = Text("Understanding Dinitz's Algorithm: Phase 1 BFS", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        # --- Define Graph based on Edges_example ---
        vertices = list(range(1, 11))
        # Edges as (u,v) tuples. Manim's Graph will create mobjects for these.
        # We need to ensure we can reference them correctly.
        edges_input_tuples = [
          (1, 2), (1, 3), (1, 4), (3, 4), (2, 5), (3, 5), (4, 6),
          (5, 7), (5, 8), (6, 8), (6, 9), (7, 10), (8, 10), (9, 10)
        ]
        capacities_dict = {
            (1, 2): 25, (1, 3): 30, (1, 4): 20, (3, 4): 30, (2, 5): 25, (3, 5): 35, (4, 6): 30,
            (5, 7): 40, (5, 8): 40, (6, 8): 35, (6, 9): 30, (7, 10): 20, (8, 10): 20, (9, 10): 20
        }
        # For Phase 1 BFS, residual capacity = capacity for all original edges
        # We won't show flow updates in this BFS step, just reachability.

        source_node, sink_node = 1, 10

        graph_layout = {
            1: [-6, 0, 0], 2: [-4, 2, 0], 3: [-4, 0, 0], 4: [-4, -2, 0],
            5: [-1.5, 1, 0], 6: [-1.5, -1, 0],
            7: [1.5, 2, 0], 8: [1.5, 0, 0], 9: [1.5, -2, 0],
            10: [4, 0, 0]
        }
        
        g = Graph(vertices, edges_input_tuples, layout=graph_layout, labels=True,
                  vertex_config={"radius": 0.35, "color": BLUE_D, "fill_opacity": 0.9},
                  edge_config={"stroke_width": 3, "color": GREY_B})

        edge_cap_labels = VGroup()
        for u, v in edges_input_tuples:
            cap = capacities_dict.get((u,v)) # Assuming (u,v) is the key for capacity
            if cap:
                edge_mo = g.edges[(u,v)] if (u,v) in g.edges else g.edges[(v,u)]
                mid_point = edge_mo.get_center()
                direction_vector = edge_mo.get_unit_vector()
                offset_dir = np.array([-direction_vector[1], direction_vector[0], 0]) * 0.25 # Perpendicular offset
                
                label = Text(str(cap), font_size=18, color=BLACK).move_to(mid_point + offset_dir)
                edge_cap_labels.add(label)
        
        graph_group = VGroup(g, edge_cap_labels).scale(0.9).move_to(ORIGIN+DOWN*0.2)
        self.play(Create(g), Write(edge_cap_labels))
        self.wait(1)

        # --- BFS Animation for Levels ---
        bfs_intro_text = Text("Phase 1: Build Level Graph using BFS from Source (1)", font_size=28).next_to(title, DOWN, buff=0.3)
        self.play(Write(bfs_intro_text))
        
        levels = {node: -1 for node in vertices} # Stores level number for each node
        # Manim mobjects for level texts, e.g., "L0: {1}"
        level_texts_vg = VGroup().to_corner(UL).shift(RIGHT*0.5 + DOWN*0.5) 
        
        # Level colors (adjust as needed)
        level_colors = [RED_E, ORANGE, YELLOW_D, GREEN_C, BLUE_C, PURPLE_C] 

        # Queue for BFS
        q = collections.deque()
        
        # --- Level 0 ---
        current_level_number = 0
        levels[source_node] = current_level_number
        q.append(source_node)
        
        # Animate source node
        self.play(g.vertices[source_node].animate.set_fill(level_colors[current_level_number]), run_time=0.5)
        level0_text_mobj = Text(f"L{current_level_number}: {{{source_node}}}", font_size=22)
        level_texts_vg.add(level0_text_mobj)
        self.play(Write(level_texts_vg))
        self.wait(0.5)

        # --- Subsequent Levels (L1, L2, L3, L4) ---
        while q:
            current_level_number += 1
            nodes_in_current_processing_level = list(q) # Nodes whose neighbors we explore
            q.clear() # Prepare queue for nodes in the *next* level
            
            nodes_found_in_next_level = []
            animations_for_next_level_nodes = []
            animations_for_next_level_edges = []

            if not nodes_in_current_processing_level: # Should not happen if sink is reachable
                break

            for u_node in nodes_in_current_processing_level:
                # Find neighbors of u_node from edges_input_tuples
                # (In Dinitz, we consider residual graph edges. For Phase 1 BFS, this means original edges with capacity > 0)
                for v_candidate in vertices: # Iterate all possible vertices
                    if levels[v_candidate] == -1: # If not yet visited/leveled
                        # Check if an edge exists between u_node and v_candidate
                        edge_uv = None
                        is_forward_edge = False # Is (u_node, v_candidate) an original edge?

                        if (u_node, v_candidate) in edges_input_tuples and capacities_dict.get((u_node, v_candidate), 0) > 0:
                            edge_uv = (u_node, v_candidate)
                            is_forward_edge = True
                        elif (v_candidate, u_node) in edges_input_tuples and capacities_dict.get((v_candidate, u_node), 0) > 0:
                             # For BFS, an undirected edge is fine if we just care about connection.
                             # In Dinitz level graph, edges are directed u -> v where level[v] = level[u]+1
                             # Here, we are finding nodes for next level, so u is current, v is next.
                             # This means we are interested in a path from u_node to v_candidate.
                             # If original edge is (v_candidate, u_node), this is not a forward path for BFS from u_node.
                             # So, we only consider original (u_node, v_candidate) for this simple BFS visualization.
                             # A full residual graph BFS would also consider flow[v_candidate, u_node] > 0.
                             # For Phase 1, no flow exists, so this simplification is fine.
                            pass


                        if is_forward_edge: # Edge (u_node, v_candidate) exists and has capacity
                            levels[v_candidate] = current_level_number
                            nodes_found_in_next_level.append(v_candidate)
                            q.append(v_candidate) # Add to queue for processing in the *next* iteration

                            # Prepare animations
                            animations_for_next_level_nodes.append(
                                g.vertices[v_candidate].animate.set_fill(level_colors[current_level_number % len(level_colors)])
                            )
                            # Get the Manim edge mobject. edges_input_tuples defines how g.edges is keyed.
                            manim_edge_key = edge_uv 
                            animations_for_next_level_edges.append(
                                g.edges[manim_edge_key].animate.set_color(level_colors[current_level_number % len(level_colors)])
                            )
            
            if not nodes_found_in_next_level: # No new nodes found for the next level
                if levels[sink_node] == -1:
                    sink_unreachable_text = Text("Sink is not reachable!", font_size=24, color=RED)
                    sink_unreachable_text.next_to(level_texts_vg, DOWN, aligned_edge=LEFT)
                    self.play(Write(sink_unreachable_text))
                break # BFS complete or stuck

            # Play animations for the newly found level
            if animations_for_next_level_nodes:
                self.play(*animations_for_next_level_nodes, run_time=1.0)
            if animations_for_next_level_edges:
                self.play(*animations_for_next_level_edges, run_time=1.0)
            
            # Add text for the new level
            nodes_str = ", ".join(map(str, sorted(list(set(nodes_found_in_next_level))))) # Unique sorted nodes
            next_level_text_mobj = Text(f"L{current_level_number}: {{{nodes_str}}}", font_size=22)
            if level_texts_vg:
                 next_level_text_mobj.next_to(level_texts_vg[-1], DOWN, aligned_edge=LEFT)
            level_texts_vg.add(next_level_text_mobj)
            self.play(Write(next_level_text_mobj))
            self.wait(1)

            if sink_node in nodes_found_in_next_level and levels[sink_node] == current_level_number:
                sink_reached_text = Text(f"Sink ({sink_node}) reached at Level {current_level_number}!", font_size=24, color=GREEN)
                sink_reached_text.next_to(bfs_intro_text, DOWN, buff=0.5) # Position near BFS intro
                self.play(Write(sink_reached_text))
                self.wait(1)
                # self.play(FadeOut(sink_reached_text)) # Optional: fade out after a bit
                break # BFS for Phase 1 level graph is complete once sink is leveled
        
        bfs_complete_text = Text("BFS for Phase 1 Level Graph complete.", font_size=24)
        bfs_complete_text.next_to(graph_group, DOWN, buff=0.5)
        self.play(Write(bfs_complete_text))
        self.wait(2)

        # Cleanup for next steps
        self.play(FadeOut(bfs_intro_text), FadeOut(level_texts_vg), FadeOut(bfs_complete_text),
                  FadeOut(title.to_edge(UP, buff=0.1))) # Also move title slightly up or fade it too
        self.wait(1)
        # Graph (g and edge_cap_labels) remains for next TODOs

        # TODO: Show level graph edges only (dim others)
        # TODO: Animate DFS path finding
        # TODO: Animate flow augmentation and residual graph updates