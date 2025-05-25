import collections
from manim import *

# Configuration for a slightly nicer look
# config.background_color = GREY_E # Manim CE uses config.background_color
# config.frame_width = 14.2 # Default is 14.22 (16/9 * 8) but can be adjusted

class DinitzManimExplanation(Scene):
    def construct(self):
        # --- Title ---
        title = Text("Understanding Dinitz's Algorithm for Max Flow", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        # --- Define Graph based on Edges_example ---
        # Manim uses 0-indexed vertices by default in its Graph class if labels aren't specified.
        # We'll use explicit vertex labels 1-10.
        vertices = list(range(1, 11))
        edges_input = [
          (1, 2), (1, 3), (1, 4), (3, 4), (2, 5), (3, 5), (4, 6),
          (5, 7), (5, 8), (6, 8), (6, 9), (7, 10), (8, 10), (9, 10)
        ]
        # Capacities for labeling (Manim Graph doesn't store arbitrary edge data easily for animation beyond labels)
        capacities_dict = {
            (1, 2): 25, (1, 3): 30, (1, 4): 20, (3, 4): 30, (2, 5): 25, (3, 5): 35, (4, 6): 30,
            (5, 7): 40, (5, 8): 40, (6, 8): 35, (6, 9): 30, (7, 10): 20, (8, 10): 20, (9, 10): 20
        }
        source_node, sink_node = 1, 10

        # Create a Manim Graph object
        # We need to define a layout. Spring layout is okay for a start.
        # For specific visualizations, manual layout (vertex_config) is often better.
        graph_layout = {
            1: [-5, 0, 0], 2: [-3, 1.5, 0], 3: [-3, 0, 0], 4: [-3, -1.5, 0],
            5: [-0.5, 0.75, 0], 6: [-0.5, -0.75, 0],
            7: [2, 1.5, 0], 8: [2, 0, 0], 9: [2, -1.5, 0],
            10: [4.5, 0, 0]
        }
        
        g = Graph(vertices, edges_input, layout=graph_layout, labels=True,
                  vertex_config={"radius": 0.4, "color": BLUE_C, "fill_opacity": 0.8},
                  edge_config={"stroke_width": 3, "color": GREY_BROWN})

        # Add capacity labels to edges (as Text mobjects)
        edge_cap_labels = VGroup()
        for u, v in edges_input:
            cap = capacities_dict.get((u,v)) or capacities_dict.get((v,u)) # Assuming undirected for capacities display
            if cap:
                # Position label near the midpoint of the edge
                mid_point = g.edges[(u,v)].get_center() # Manim Graph stores edges as (u,v) or (v,u)
                # Adjust label position slightly to avoid overlap with edge
                direction_vector = g.edges[(u,v)].get_unit_vector()
                # Perpendicular vector for offset (Manim uses [x,y,z])
                offset_dir = np.array([-direction_vector[1], direction_vector[0], 0]) * 0.3
                
                label = Text(str(cap), font_size=20, color=BLACK).move_to(mid_point + offset_dir)
                edge_cap_labels.add(label)
        
        graph_group = VGroup(g, edge_cap_labels)
        self.play(Create(g), Write(edge_cap_labels))
        self.play(graph_group.animate.scale(0.8).move_to(ORIGIN + DOWN*0.5))
        self.wait(1)

        # --- Step 1: Introduce Level Graph Concept & BFS for Phase 1 ---
        phase1_text = Text("Phase 1: Build Level Graph using BFS", font_size=28).next_to(g, UP, buff=0.5)
        self.play(Write(phase1_text))
        self.wait(0.5)

        # BFS Animation for Levels
        levels = {node: -1 for node in vertices}
        level_colors = [YELLOW_A, GREEN_A, BLUE_A, PINK, PURPLE_A]
        
        # Source node
        levels[source_node] = 0
        self.play(g.vertices[source_node].animate.set_fill(level_colors[0]), run_time=0.5)
        level0_text = Text(f"L0: {{{source_node}}}", font_size=24).to_corner(UL).shift(DOWN*0.5)
        self.play(Write(level0_text))

        # Level 1
        level1_nodes = []
        animations_level1 = []
        q = collections.deque([source_node])
        visited_bfs = {source_node}

        # Simple BFS logic for animation (assumes residual graph is initially the capacity graph)
        # Level 0 done (source_node)
        
        # Finding Level 1
        next_q = collections.deque()
        level1_found_nodes_text = []
        while q:
            u = q.popleft()
            for v_neighbor in g.vertices: # Check all potential neighbors
                # Check if (u,v_neighbor) is an edge with capacity
                original_edge = (u,v_neighbor) if (u,v_neighbor) in edges_input else (v_neighbor,u) if (v_neighbor,u) in edges_input else None
                if original_edge and capacities_dict.get(original_edge,0)>0: # simplified: check capacity
                    if v_neighbor not in visited_bfs:
                         if levels[u] == 0: # For level 1 nodes from source
                            levels[v_neighbor] = 1
                            level1_nodes.append(v_neighbor)
                            animations_level1.append(g.vertices[v_neighbor].animate.set_fill(level_colors[1]))
                            animations_level1.append(g.edges[original_edge].animate.set_color(level_colors[1]))
                            visited_bfs.add(v_neighbor)
                            next_q.append(v_neighbor)
                            level1_found_nodes_text.append(str(v_neighbor))
        
        if animations_level1:
            self.play(*animations_level1, run_time=1.5)
            level1_text_str = f"L1: {{{', '.join(level1_found_nodes_text)}}}"
            level1_text = Text(level1_text_str, font_size=24).next_to(level0_text, DOWN, aligned_edge=LEFT)
            self.play(Write(level1_text))
        q = next_q
        self.wait(1)
        
        # TODO: Continue BFS for L2, L3, L4 (similar logic for each level)
        # TODO: Show level graph edges only (dim others)
        # TODO: Animate DFS path finding
        # TODO: Animate flow augmentation and residual graph updates

        explanation_text = Text("BFS explores layer by layer to define levels from the Source.", font_size=24)
        explanation_text.next_to(graph_group, DOWN, buff=0.5)
        self.play(Write(explanation_text))
        self.wait(2)

        # Fade out phase specific texts
        self.play(FadeOut(phase1_text), FadeOut(level0_text), FadeOut(level1_text), FadeOut(explanation_text))
        self.wait(2)
        # End Scene