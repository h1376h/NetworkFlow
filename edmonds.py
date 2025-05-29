from manim import *
import collections
import numpy as np

# --- Style and Layout Constants (mostly reused) ---
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.16

MAIN_TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28 # For text below main title
ITERATION_TEXT_FONT_SIZE = 22 # For text below section title (was PHASE_TEXT_FONT_SIZE)
STATUS_TEXT_FONT_SIZE = 20   # For text below iteration title
NODE_LABEL_FONT_SIZE = 16
EDGE_CAPACITY_LABEL_FONT_SIZE = 12 # Used for original edges
EDGE_FLOW_PREFIX_FONT_SIZE = 12    # Used for original edges & pure reverse residual
MAX_FLOW_DISPLAY_FONT_SIZE = 20 # For the new current flow display

BUFF_VERY_SMALL = 0.05
BUFF_SMALL = 0.1
BUFF_MED = 0.25
BUFF_LARGE = 0.4
BUFF_XLARGE = 0.6

RING_COLOR = YELLOW_C
RING_STROKE_WIDTH = 3.5
RING_RADIUS_OFFSET = 0.1
RING_Z_INDEX = 4

DEFAULT_NODE_COLOR = BLUE_E
DEFAULT_EDGE_COLOR = GREY_C
LABEL_TEXT_COLOR = DARK_GREY

# BFS/Path Colors
BFS_VISITED_NODE_COLOR = YELLOW_A
BFS_EXPLORE_EDGE_COLOR = ORANGE
PATH_FOUND_COLOR = GREEN_D
PATH_HIGHLIGHT_WIDTH = EDGE_STROKE_WIDTH * 1.3 # Was DFS_PATH_EDGE_WIDTH
BOTTLENECK_EDGE_INDICATE_COLOR = RED_D

DIMMED_OPACITY = 0.20
DIMMED_COLOR = GREY_BROWN

REVERSE_EDGE_COLOR = GREY_B
REVERSE_EDGE_OPACITY = 0.15 # Make 0.0 if you want them initially invisible
REVERSE_EDGE_STROKE_WIDTH_FACTOR = 0.6
REVERSE_EDGE_Z_INDEX = -1

# Flow pulse animation constants
FLOW_PULSE_COLOR = BLUE_B
FLOW_PULSE_WIDTH_FACTOR = 1.8
FLOW_PULSE_TIME_WIDTH = 0.35  # Proportion of edge length lit up by flash
FLOW_PULSE_EDGE_RUNTIME = 0.5 # Time for pulse to traverse one edge
FLOW_PULSE_Z_INDEX_OFFSET = 10
EDGE_UPDATE_RUNTIME = 0.3     # Time for text/visual updates after pulse on an edge


class EdmondsKarpVisualizer(Scene):

    def setup_titles_and_placeholders(self):
        self.main_title = Text("Visualizing Edmonds-Karp Algorithm for Max Flow", font_size=MAIN_TITLE_FONT_SIZE)
        self.main_title.to_edge(UP, buff=BUFF_LARGE).set_z_index(10)
        self.add(self.main_title)

        self.current_section_title_mobj = Text("", font_size=SECTION_TITLE_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.iteration_text_mobj = Text("", font_size=ITERATION_TEXT_FONT_SIZE, weight=BOLD).set_z_index(10) # Renamed from phase_text_mobj
        self.algo_status_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE).set_z_index(10)
        self.max_flow_display_mobj = Text("", font_size=MAX_FLOW_DISPLAY_FONT_SIZE, weight=BOLD, color=GREEN_C).set_z_index(10)

        self.info_texts_group = VGroup(
            self.current_section_title_mobj,
            self.iteration_text_mobj,
            self.algo_status_mobj,
            self.max_flow_display_mobj
        ).arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        self.add(self.info_texts_group)
        
        self.action_text_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE, weight=BOLD, color=YELLOW).set_z_index(RING_Z_INDEX + 50)
        # Position will be set later, near source node

    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
        old_text_had_actual_content = (isinstance(old_mobj, Text) and old_mobj.text != "") or \
                                      (isinstance(old_mobj, Tex) and old_mobj.tex_string != "")
        
        new_text_has_actual_content = bool(new_text_content_str and new_text_content_str != "")

        anims_to_play = []
        if old_text_had_actual_content:
            anims_to_play.append(FadeOut(old_mobj, scale=0.8, run_time=0.25))
            
        if new_text_has_actual_content:
            anims_to_play.append(FadeIn(new_mobj, scale=1.2, run_time=0.25))

        if anims_to_play:
            self.play(*anims_to_play)

    def _update_text_generic(self, text_attr_name, new_text_content, font_size, weight, color, play_anim=True, is_latex=False):
        old_mobj = getattr(self, text_attr_name)

        if is_latex:
            new_mobj = Tex(new_text_content, color=color)
            ref_text_for_height = Text("Mg", font_size=font_size)
            if ref_text_for_height.height > 0.001 and new_mobj.height > 0.001:
                new_mobj.scale_to_fit_height(ref_text_for_height.height)
        else:
            new_mobj = Text(new_text_content, font_size=font_size, weight=weight, color=color)

        current_idx = -1
        if old_mobj in self.info_texts_group.submobjects:
            current_idx = self.info_texts_group.submobjects.index(old_mobj)
            new_mobj.move_to(old_mobj.get_center())
            self.info_texts_group.remove(old_mobj)

        if old_mobj in self.mobjects :
            self.remove(old_mobj)

        if current_idx != -1 :
            self.info_texts_group.insert(current_idx, new_mobj)

        setattr(self, text_attr_name, new_mobj)
        self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        new_mobj.set_z_index(old_mobj.z_index if hasattr(old_mobj, 'z_index') and old_mobj.z_index is not None else 10)

        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_content)
        else:
            is_empty_new_content = (isinstance(new_mobj, Text) and new_mobj.text == "") or \
                                   (isinstance(new_mobj, Tex) and new_mobj.tex_string == "")
            is_in_group = new_mobj in self.info_texts_group.submobjects

            if not is_empty_new_content:
                if not is_in_group and new_mobj not in self.mobjects:
                    self.add(new_mobj)

    def update_section_title(self, text_str, play_anim=True):
        self._update_text_generic("current_section_title_mobj", text_str, SECTION_TITLE_FONT_SIZE, BOLD, WHITE, play_anim)

    def update_iteration_text(self, text_str, color=WHITE, play_anim=True): # Renamed from update_phase_text
        self._update_text_generic("iteration_text_mobj", text_str, ITERATION_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True, is_latex=False):
        self._update_text_generic("algo_status_mobj", text_str, STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim, is_latex=is_latex)

    def update_max_flow_display(self, play_anim=True):
        new_text_str = f"Current Max Flow: {self.max_flow_value:.1f}"
        self._update_text_generic("max_flow_display_mobj", new_text_str, MAX_FLOW_DISPLAY_FONT_SIZE, BOLD, GREEN_C, play_anim)

    def _update_action_text(self, new_text_content, new_color=YELLOW, animate=True): # Simplified from _update_sink_action_text
        current_mobj = self.action_text_mobj
        old_text_content = current_mobj.text
        old_color_val = current_mobj.get_color()

        if old_text_content == new_text_content and old_color_val == new_color:
            return 

        target_text_template = Text(
            new_text_content,
            font_size=STATUS_TEXT_FONT_SIZE,
            weight=current_mobj.weight,
            color=new_color
        )

        if hasattr(self, 'node_mobjects') and hasattr(self, 'source_node') and \
           self.source_node in self.node_mobjects and self.node_mobjects.get(self.source_node) is not None:
            source_node_group = self.node_mobjects[self.source_node]
            if isinstance(source_node_group, VGroup) and len(source_node_group.submobjects) > 0:
                source_node_dot = source_node_group[0]
                target_text_template.next_to(source_node_dot, UP, buff=BUFF_SMALL)
            else: 
                target_text_template.move_to(current_mobj.get_center())
        else: 
            target_text_template.move_to(current_mobj.get_center())
        
        target_text_template.set_z_index(current_mobj.z_index)

        if animate:
            if old_text_content and not new_text_content: 
                self.play(FadeOut(current_mobj, run_time=0.25, scale=0.8))
                current_mobj.become(target_text_template) 
            elif not old_text_content and new_text_content: 
                current_mobj.become(target_text_template)
                self.play(FadeIn(current_mobj, run_time=0.25, scale=1.2))
            elif old_text_content and new_text_content: 
                old_mobj_anim_copy = current_mobj.copy() 
                current_mobj.become(target_text_template) 
                self.play(
                    FadeOut(old_mobj_anim_copy, run_time=0.20, scale=0.8),
                    FadeIn(current_mobj, run_time=0.20, scale=1.2) 
                )
            elif new_text_content and old_text_content == new_text_content and old_color_val != new_color:
                self.play(current_mobj.animate.set_color(new_color), run_time=0.3)
            elif not new_text_content and not old_text_content and old_color_val != new_color:
                current_mobj.set_color(new_color) 
        else: 
            current_mobj.become(target_text_template) 
            if current_mobj not in self.mobjects and new_text_content: 
                self.add(current_mobj)

    def _restore_graph_appearance(self, highlight_exceptions=None):
        # Restores nodes and edges to their base appearance, optionally keeping some highlighted.
        # highlight_exceptions: dict of {mobject: {attr: val}} to keep certain highlights.
        if highlight_exceptions is None: highlight_exceptions = {}
        
        anims = []
        # Restore nodes
        for v_id, node_group in self.node_mobjects.items():
            dot, lbl = node_group
            base_attrs = self.base_node_visual_attrs[v_id]
            if dot not in highlight_exceptions:
                anims.append(dot.animate.set_width(base_attrs["width"])
                                     .set_fill(base_attrs["fill_color"], opacity=base_attrs["opacity"])
                                     .set_stroke(color=base_attrs["stroke_color"], width=base_attrs["stroke_width"]))
            if lbl not in highlight_exceptions:
                # Handle s/t labels which might have been transformed
                original_text = "s" if v_id == self.source_node else "t" if v_id == self.sink_node else str(v_id)
                if lbl.text != original_text : # If it was changed to s/t and needs restoring if it was not s/t
                    if not ( (v_id == self.source_node and lbl.text == "s") or \
                             (v_id == self.sink_node and lbl.text == "t") ):
                        # This case is tricky, typically s/t labels are kept.
                        # For simplicity, just ensure color is restored.
                        anims.append(lbl.animate.set_color(base_attrs["label_color"]))
                else:
                     anims.append(lbl.animate.set_color(base_attrs["label_color"]))


        # Restore edges and their labels
        for edge_key, edge_mo in self.edge_mobjects.items():
            base_attrs = self.base_edge_visual_attrs[edge_key]
            current_res_cap = self.capacities.get(edge_key, 0) - self.flow.get(edge_key, 0)
            
            target_color = base_attrs["color"]
            target_width = base_attrs["stroke_width"]
            target_opacity = base_attrs["opacity"]

            if edge_key not in self.original_edge_tuples: # Non-original (residual) edges
                if current_res_cap > 0 :
                    target_opacity = REVERSE_EDGE_OPACITY if REVERSE_EDGE_OPACITY > 0 else 0.05 # Slightly visible if usable
                    target_color = REVERSE_EDGE_COLOR
                else: # No residual capacity, make it very dim or invisible
                    target_opacity = 0.0 if REVERSE_EDGE_OPACITY == 0.0 else 0.01
            else: # Original edges
                 if current_res_cap <= 0: # Saturated original edge
                    target_color = DIMMED_COLOR
                    target_opacity = DIMMED_OPACITY


            if edge_mo not in highlight_exceptions:
                 anims.append(edge_mo.animate.set_color(target_color)
                                        .set_stroke(width=target_width, opacity=target_opacity))

            # Restore labels
            label_group = self.edge_label_groups.get(edge_key)
            if label_group and label_group not in highlight_exceptions:
                base_label_opacity = self.base_label_visual_attrs.get(edge_key, {}).get("opacity", 0.0)
                
                if edge_key in self.original_edge_tuples:
                    final_label_opacity = DIMMED_OPACITY if current_res_cap <= 0 else 1.0
                    anims.append(label_group.animate.set_opacity(final_label_opacity))
                    if final_label_opacity > 0: # Restore text color for visible original labels
                        for part in label_group.submobjects:
                            if isinstance(part, Text): anims.append(part.animate.set_color(LABEL_TEXT_COLOR))
                else: # Non-original (residual capacity label)
                    res_cap_label_mobj = self.edge_residual_capacity_mobjects.get(edge_key)
                    if res_cap_label_mobj:
                        if current_res_cap > 0 and target_opacity > 0.01: # If edge is visible and has capacity
                            # Update text and make visible
                            new_text = Text(f"{current_res_cap:.0f}", font=res_cap_label_mobj.font, font_size=res_cap_label_mobj.font_size, color=target_color)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: new_text.height = self.scaled_flow_text_height * 0.9
                            new_text.move_to(res_cap_label_mobj.get_center()).set_opacity(1.0 if target_opacity > DIMMED_OPACITY else 0.7) # Make label visible
                            anims.append(res_cap_label_mobj.animate.become(new_text))
                        else: # Hide label
                            anims.append(res_cap_label_mobj.animate.set_opacity(0.0))
        
        if anims:
            self.play(AnimationGroup(*anims, lag_ratio=0.01, run_time=0.75))
        self.wait(0.25)

    def _bfs_find_augmenting_path_and_animate_search(self):
        # Performs BFS to find an augmenting path from source to sink in the residual graph.
        # Animates the BFS traversal.
        # Returns: (path_edges, bottleneck_capacity) or (None, 0) if no path.
        
        self.update_status_text(f"BFS: Searching for path S ({self.source_node}) -> T ({self.sink_node}) in residual graph.", play_anim=True)
        self.wait(1.5)

        q = collections.deque([(self.source_node, [self.source_node], float('inf'))]) # (curr_node, current_path_nodes, path_bottleneck)
        # parent_map = {self.source_node: None} # To reconstruct path edges
        visited_nodes_bfs = {self.source_node}
        
        bfs_animations = []
        path_edges_found = None
        final_bottleneck = 0

        # Highlight source node
        s_dot, s_lbl = self.node_mobjects[self.source_node]
        bfs_animations.append(s_dot.animate.set_fill(BFS_VISITED_NODE_COLOR, opacity=0.8).set_width(self.base_node_visual_attrs[self.source_node]["width"] * 1.15))
        bfs_animations.append(s_lbl.animate.set_color(BLACK)) # Assuming BFS_VISITED_NODE_COLOR is light
        if bfs_animations: self.play(*bfs_animations, run_time=0.4); bfs_animations = []
        self.wait(0.5)

        temp_bfs_highlights = VGroup() # Store temporary highlights like exploring edges/nodes
        self.add(temp_bfs_highlights)

        while q:
            u, path_nodes_so_far, current_bottleneck = q.popleft()
            u_display_name = "s" if u == self.source_node else "t" if u == self.sink_node else str(u)
            
            # Animate exploring from u
            u_dot, _ = self.node_mobjects[u]
            explore_ring = Circle(radius=u_dot.width/2 * 1.4, color=PINK, stroke_width=RING_STROKE_WIDTH*0.6).move_to(u_dot.get_center()).set_z_index(u_dot.z_index + 1)
            self.play(Create(explore_ring), run_time=0.3)
            temp_bfs_highlights.add(explore_ring)
            self.update_status_text(f"BFS: Exploring from node {u_display_name}.", play_anim=False)
            self.wait(0.7)

            # Sort neighbors for deterministic exploration (optional but good for consistency)
            # Neighbors are determined by self.adj, residual capacity check happens next.
            sorted_potential_neighbors = sorted(self.adj[u])

            for v in sorted_potential_neighbors:
                edge_key = (u,v)
                residual_capacity = self.capacities.get(edge_key, 0) - self.flow.get(edge_key, 0)
                edge_mo = self.edge_mobjects.get(edge_key)
                v_display_name = "s" if v == self.source_node else "t" if v == self.sink_node else str(v)

                if edge_mo and residual_capacity > 0 and v not in visited_nodes_bfs:
                    self.update_status_text(f"BFS: Edge ({u_display_name} -> {v_display_name}), Res.Cap: {residual_capacity:.0f}. Visiting {v_display_name}.", play_anim=False)
                    
                    # Animate trying edge
                    original_edge_color = edge_mo.get_color()
                    original_edge_width = edge_mo.get_stroke_width()
                    self.play(edge_mo.animate.set_color(BFS_EXPLORE_EDGE_COLOR).set_stroke(width=PATH_HIGHLIGHT_WIDTH*0.9), run_time=0.3)
                    temp_bfs_highlights.add(edge_mo.copy().set_color(original_edge_color).set_stroke(width=original_edge_width)) # Store to revert

                    visited_nodes_bfs.add(v)
                    new_path_nodes = path_nodes_so_far + [v]
                    new_bottleneck = min(current_bottleneck, residual_capacity)

                    v_dot, v_lbl = self.node_mobjects[v]
                    self.play(
                        v_dot.animate.set_fill(BFS_VISITED_NODE_COLOR, opacity=0.8).set_width(self.base_node_visual_attrs[v]["width"] * 1.1),
                        v_lbl.animate.set_color(BLACK), # Assuming BFS_VISITED_NODE_COLOR is light
                        run_time=0.4
                    )
                    self.wait(0.6)
                    
                    # Revert edge exploration highlight, but keep node highlight
                    self.play(edge_mo.animate.set_color(original_edge_color).set_stroke(width=original_edge_width), run_time=0.2)


                    if v == self.sink_node: # Path to sink found
                        self.update_status_text(f"BFS: Path to Sink T ({self.sink_node}) found!", color=GREEN_B, play_anim=True)
                        self.wait(1.0)
                        
                        # Construct path_edges list
                        path_edges_found = []
                        for i in range(len(new_path_nodes) - 1):
                            path_edges_found.append((new_path_nodes[i], new_path_nodes[i+1]))
                        
                        final_bottleneck = new_bottleneck
                        
                        # Highlight the found path
                        path_highlight_anims = []
                        for (node_u, node_v) in path_edges_found:
                            path_edge_mo = self.edge_mobjects[(node_u, node_v)]
                            path_highlight_anims.append(path_edge_mo.animate.set_color(PATH_FOUND_COLOR).set_stroke(width=PATH_HIGHLIGHT_WIDTH, opacity=1.0))
                        
                        if path_highlight_anims:
                            self.play(AnimationGroup(*path_highlight_anims, lag_ratio=0.1), run_time=0.8)
                        
                        self.play(FadeOut(temp_bfs_highlights), run_time=0.3) # Fade out BFS specific highlights
                        temp_bfs_highlights.remove(*temp_bfs_highlights.submobjects)
                        return path_edges_found, final_bottleneck

                    q.append((v, new_path_nodes, new_bottleneck))
                    # Break from inner loop to process next in BFS queue (true BFS behavior) - actually, no, continue exploring from u
            
            self.play(FadeOut(explore_ring), run_time=0.2) # Remove exploration ring for u
            if explore_ring in temp_bfs_highlights: temp_bfs_highlights.remove(explore_ring)
            
        # No path to sink found
        self.play(FadeOut(temp_bfs_highlights), run_time=0.3)
        temp_bfs_highlights.remove(*temp_bfs_highlights.submobjects)
        self.update_status_text(f"BFS: No path from S to T found in residual graph.", color=YELLOW_C, play_anim=True)
        self.wait(1.5)
        return None, 0

    def _animate_flow_augmentation(self, path_edges, bottleneck_flow):
        if not path_edges or bottleneck_flow == 0:
            return

        self.update_status_text(f"Augmenting flow by {bottleneck_flow:.1f} along the found path.", color=GREEN_A, play_anim=True)
        self._update_action_text("Augmenting...", new_color=GREEN_B, animate=True)
        self.wait(1.0)

        # Bottleneck edge indication
        bottleneck_edge_mos_to_indicate = []
        for (u,v) in path_edges:
            res_cap_before_aug = self.capacities.get((u,v), 0) - self.flow.get((u,v), 0)
            if abs(res_cap_before_aug - bottleneck_flow) < 0.01:
                 bottleneck_edge_mos_to_indicate.append(self.edge_mobjects[(u,v)])
        
        if bottleneck_edge_mos_to_indicate:
            self.update_status_text(f"Path Bottleneck: {bottleneck_flow:.1f}. Identifying bottleneck edges...", color=YELLOW_A, play_anim=True)
            self.wait(0.5)
            flash_anims = [
                Indicate(edge_mo, color=BOTTLENECK_EDGE_INDICATE_COLOR, scale_factor=1.05, rate_func=there_and_back_with_pause, run_time=1.0)
                for edge_mo in bottleneck_edge_mos_to_indicate
            ]
            if flash_anims:
                self.play(AnimationGroup(*flash_anims, lag_ratio=0.05))
                self.wait(0.5)


        path_augmentation_sequence = []
        for (u,v) in path_edges:
            edge_mo = self.edge_mobjects[(u,v)]
            animations_for_current_edge_step = []

            # 1. Flow Pulse Animation
            flash_edge_copy = edge_mo.copy()
            flash_edge_copy.set_color(FLOW_PULSE_COLOR)
            flash_edge_copy.set_stroke(width=edge_mo.stroke_width * FLOW_PULSE_WIDTH_FACTOR, opacity=1.0)
            flash_edge_copy.set_z_index(edge_mo.z_index + FLOW_PULSE_Z_INDEX_OFFSET)
            
            pulse_animation = ShowPassingFlash(
                flash_edge_copy, 
                time_width=FLOW_PULSE_TIME_WIDTH, 
                run_time=FLOW_PULSE_EDGE_RUNTIME
            )
            animations_for_current_edge_step.append(pulse_animation)

            # 2. Prepare animations for number updates and edge visual changes
            text_updates_this_edge = []
            visual_updates_this_edge = []

            # Update flow values (internal state)
            self.flow[(u,v)] = self.flow.get((u,v), 0) + bottleneck_flow
            self.flow[(v,u)] = self.flow.get((v,u), 0) - bottleneck_flow 

            # --- Animation for forward edge (u,v) ---
            res_cap_after_uv = self.capacities.get((u,v),0) - self.flow.get((u,v),0)
            
            # Update flow text on original edge (u,v)
            if (u,v) in self.original_edge_tuples:
                old_flow_text_mobj = self.edge_flow_val_text_mobjects[(u,v)]
                new_flow_val_uv = self.flow[(u,v)]
                new_flow_str_uv = f"{new_flow_val_uv:.0f}" if abs(new_flow_val_uv - round(new_flow_val_uv)) < 0.01 else f"{new_flow_val_uv:.1f}"
                target_text_template_uv = Text(new_flow_str_uv, font=old_flow_text_mobj.font, font_size=old_flow_text_mobj.font_size, color=LABEL_TEXT_COLOR)
                if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height:
                    target_text_template_uv.height = self.scaled_flow_text_height
                else: target_text_template_uv.match_height(old_flow_text_mobj)
                target_text_template_uv.move_to(old_flow_text_mobj.get_center()).rotate(edge_mo.get_angle(), about_point=target_text_template_uv.get_center())
                text_updates_this_edge.append(old_flow_text_mobj.animate.become(target_text_template_uv))
                
                # Visual update for original edge (u,v)
                if res_cap_after_uv <= 0: # Saturated
                    visual_updates_this_edge.append(edge_mo.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR, width=self.base_edge_visual_attrs[(u,v)]["stroke_width"]))
                    # Also dim its full label group
                    label_grp_uv = self.edge_label_groups.get((u,v))
                    if label_grp_uv: visual_updates_this_edge.append(label_grp_uv.animate.set_opacity(DIMMED_OPACITY))
                else: # Still has capacity
                    visual_updates_this_edge.append(edge_mo.animate.set_stroke(opacity=self.base_edge_visual_attrs[(u,v)]["opacity"], color=self.base_edge_visual_attrs[(u,v)]["color"], width=self.base_edge_visual_attrs[(u,v)]["stroke_width"]))
                    label_grp_uv = self.edge_label_groups.get((u,v))
                    if label_grp_uv: visual_updates_this_edge.append(label_grp_uv.animate.set_opacity(1.0))


            # Update residual capacity label for non-original edge (u,v)
            elif (u,v) in self.edge_residual_capacity_mobjects:
                label_mobj_uv = self.edge_residual_capacity_mobjects.get((u,v))
                if label_mobj_uv:
                    if res_cap_after_uv > 0:
                        target_label_uv = Text(f"{res_cap_after_uv:.0f}", font=label_mobj_uv.font, font_size=label_mobj_uv.font_size, color=REVERSE_EDGE_COLOR)
                        if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_uv.height = self.scaled_flow_text_height * 0.9
                        target_label_uv.move_to(label_mobj_uv.get_center()).set_opacity(1.0)
                        text_updates_this_edge.append(label_mobj_uv.animate.become(target_label_uv))
                        visual_updates_this_edge.append(edge_mo.animate.set_stroke(opacity=REVERSE_EDGE_OPACITY, color=REVERSE_EDGE_COLOR, width=self.base_edge_visual_attrs[(u,v)]["stroke_width"]))
                    else: # Non-original edge saturated
                        text_updates_this_edge.append(label_mobj_uv.animate.set_opacity(0.0))
                        visual_updates_this_edge.append(edge_mo.animate.set_stroke(opacity=0.0 if REVERSE_EDGE_OPACITY == 0 else 0.01, color=REVERSE_EDGE_COLOR))


            # --- Animation for reverse component (v,u) ---
            # This handles how the reverse capacity changes.
            rev_edge_key = (v,u)
            rev_edge_mo = self.edge_mobjects.get(rev_edge_key)
            if rev_edge_mo:
                res_cap_after_vu = self.capacities.get(rev_edge_key,0) - self.flow.get(rev_edge_key,0)

                if rev_edge_key in self.original_edge_tuples: # If (v,u) is an original edge
                    old_flow_text_mobj_vu = self.edge_flow_val_text_mobjects[rev_edge_key]
                    new_flow_val_vu = self.flow[rev_edge_key] # This has been decreased by bottleneck_flow
                    new_flow_str_vu = f"{new_flow_val_vu:.0f}" if abs(new_flow_val_vu - round(new_flow_val_vu)) < 0.01 else f"{new_flow_val_vu:.1f}"
                    target_text_template_vu = Text(new_flow_str_vu, font=old_flow_text_mobj_vu.font, font_size=old_flow_text_mobj_vu.font_size, color=LABEL_TEXT_COLOR)
                    if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_text_template_vu.height = self.scaled_flow_text_height
                    else: target_text_template_vu.match_height(old_flow_text_mobj_vu)
                    target_text_template_vu.move_to(old_flow_text_mobj_vu.get_center()).rotate(rev_edge_mo.get_angle(), about_point=target_text_template_vu.get_center())
                    text_updates_this_edge.append(old_flow_text_mobj_vu.animate.become(target_text_template_vu))

                    # Visual update for original edge (v,u)
                    if res_cap_after_vu <= 0:
                        visual_updates_this_edge.append(rev_edge_mo.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR))
                        label_grp_vu = self.edge_label_groups.get(rev_edge_key)
                        if label_grp_vu: visual_updates_this_edge.append(label_grp_vu.animate.set_opacity(DIMMED_OPACITY))
                    else:
                        visual_updates_this_edge.append(rev_edge_mo.animate.set_stroke(opacity=self.base_edge_visual_attrs[rev_edge_key]["opacity"], color=self.base_edge_visual_attrs[rev_edge_key]["color"]))
                        label_grp_vu = self.edge_label_groups.get(rev_edge_key)
                        if label_grp_vu: visual_updates_this_edge.append(label_grp_vu.animate.set_opacity(1.0))
                
                elif rev_edge_key in self.edge_residual_capacity_mobjects: # If (v,u) is a non-original (residual) edge
                    label_mobj_vu = self.edge_residual_capacity_mobjects.get(rev_edge_key)
                    if label_mobj_vu:
                        if res_cap_after_vu > 0: # Residual capacity for (v,u) is now positive
                            target_label_vu = Text(f"{res_cap_after_vu:.0f}", font=label_mobj_vu.font, font_size=label_mobj_vu.font_size, color=REVERSE_EDGE_COLOR)
                            if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height: target_label_vu.height = self.scaled_flow_text_height * 0.9
                            target_label_vu.move_to(label_mobj_vu.get_center()).set_opacity(1.0)
                            text_updates_this_edge.append(label_mobj_vu.animate.become(target_label_vu))
                            # Make sure the edge itself is visible
                            visual_updates_this_edge.append(rev_edge_mo.animate.set_stroke(opacity=REVERSE_EDGE_OPACITY, color=REVERSE_EDGE_COLOR, width=self.base_edge_visual_attrs[rev_edge_key]["stroke_width"]))
                        else: # Residual capacity for (v,u) is zero or less (should not be less if C=0)
                            text_updates_this_edge.append(label_mobj_vu.animate.set_opacity(0.0))
                            # Hide or dim the edge
                            visual_updates_this_edge.append(rev_edge_mo.animate.set_stroke(opacity=0.0 if REVERSE_EDGE_OPACITY == 0 else 0.01, color=REVERSE_EDGE_COLOR))


            if text_updates_this_edge or visual_updates_this_edge:
                update_group_for_this_edge = AnimationGroup(
                    *(text_updates_this_edge + visual_updates_this_edge), 
                    lag_ratio=0.0, 
                    run_time=EDGE_UPDATE_RUNTIME 
                )
                animations_for_current_edge_step.append(update_group_for_this_edge)

            path_augmentation_sequence.append(Succession(*animations_for_current_edge_step, lag_ratio=1.0)) 

        if path_augmentation_sequence:
            self.play(Succession(*path_augmentation_sequence, lag_ratio=1.0)) 
            self.wait(0.5)
        
        self.max_flow_value += bottleneck_flow
        self.update_max_flow_display(play_anim=True)
        self._update_action_text("", animate=True) # Clear "Augmenting..."
        self.wait(0.5)


    def construct(self):
        self.setup_titles_and_placeholders()
        if self.action_text_mobj not in self.mobjects: self.add(self.action_text_mobj)

        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)

        self.scaled_flow_text_height = None 
        self.update_section_title("1. Building the Flow Network", play_anim=True)

        self.current_iteration_num = 0
        self.max_flow_value = 0

        # Define graph structure
        self.source_node, self.sink_node = 1, 10
        self.vertices_data = list(range(1, 11)) 
        self.edges_with_capacity_list = [
            (1,2,25),(1,3,30),(1,4,20),(2,5,25),(3,4,30),(3,5,35),(4,6,30),
            (5,7,40),(5,8,40),(6,8,35),(6,9,30),(7,10,20),(8,10,20),(9,10,20)
        ]
        self.original_edge_tuples = set([(u,v) for u,v,c in self.edges_with_capacity_list])

        self.capacities = collections.defaultdict(int)
        self.flow = collections.defaultdict(int)    
        self.adj = collections.defaultdict(list)      

        for u,v,cap in self.edges_with_capacity_list:
            self.capacities[(u,v)] = cap
            if v not in self.adj[u]: self.adj[u].append(v)
            if u not in self.adj[v]: self.adj[v].append(u) # For residual graph structure

        self.graph_layout = { 
            1: [-4,0,0], 2:[-2,1,0], 3:[-2,0,0], 4:[-2,-1,0], 5:[-0.5,0.75,0], 6:[-0.5,-0.75,0],
            7: [1,1,0], 8:[1,0,0], 9:[1,-1,0], 10:[2.5,0,0]
        }

        self.node_mobjects = {}; self.edge_mobjects = {};
        self.edge_capacity_text_mobjects = {}; self.edge_flow_val_text_mobjects = {};
        self.edge_slash_text_mobjects = {} 
        self.edge_label_groups = {} 
        self.base_label_visual_attrs = {} 
        self.edge_residual_capacity_mobjects = {}

        self.desired_large_scale = 1.6 

        # Create node mobjects
        nodes_vgroup = VGroup()
        for v_id in self.vertices_data:
            dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, z_index=2, stroke_color=BLACK, stroke_width=NODE_STROKE_WIDTH)
            label = Text(str(v_id), font_size=NODE_LABEL_FONT_SIZE, weight=BOLD).move_to(dot.get_center()).set_z_index(3)
            self.node_mobjects[v_id] = VGroup(dot,label); nodes_vgroup.add(self.node_mobjects[v_id])
        self.play(LaggedStart(*[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data], lag_ratio=0.05), run_time=1.5)
        self.wait(0.5)

        # Create edge mobjects
        edges_vgroup = VGroup()
        edge_grow_anims = []
        for u,v,cap in self.edges_with_capacity_list: 
            n_u_dot = self.node_mobjects[u][0]; n_v_dot = self.node_mobjects[v][0]
            arrow = Arrow(n_u_dot.get_center(), n_v_dot.get_center(), buff=NODE_RADIUS, stroke_width=EDGE_STROKE_WIDTH, color=DEFAULT_EDGE_COLOR, max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH, z_index=0)
            self.edge_mobjects[(u,v)] = arrow; edges_vgroup.add(arrow)
            edge_grow_anims.append(GrowArrow(arrow))
        self.play(LaggedStart(*edge_grow_anims, lag_ratio=0.05), run_time=1.5)
        self.wait(0.5)

        # Create edge labels (flow/capacity)
        all_edge_labels_vgroup = VGroup() 
        capacities_to_animate_write = []
        flow_slashes_to_animate_write = []

        for u, v, cap in self.edges_with_capacity_list:
            arrow = self.edge_mobjects[(u,v)]
            flow_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            slash_mobj = Text("/", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR) 
            cap_text_mobj = Text(str(cap), font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=LABEL_TEXT_COLOR)

            self.edge_flow_val_text_mobjects[(u,v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u,v)] = slash_mobj
            self.edge_capacity_text_mobjects[(u,v)] = cap_text_mobj
            self.base_label_visual_attrs[(u,v)] = {"opacity": 1.0} 

            label_group = VGroup(flow_val_mobj, slash_mobj, cap_text_mobj).arrange(RIGHT, buff=BUFF_VERY_SMALL)
            label_group.move_to(arrow.get_center()).rotate(arrow.get_angle()) 
            offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * 0.15 
            label_group.shift(offset_vector).set_z_index(1) 
            self.edge_label_groups[(u,v)] = label_group
            all_edge_labels_vgroup.add(label_group)
            capacities_to_animate_write.append(cap_text_mobj)
            flow_slashes_to_animate_write.append(VGroup(flow_val_mobj, slash_mobj)) 

        # Create mobjects for potential reverse/residual edges (initially hidden or dimmed)
        all_nodes_in_graph = set(self.vertices_data)
        for u_node in all_nodes_in_graph:
            for v_node in all_nodes_in_graph: # Consider all pairs for potential residual edges
                if u_node == v_node: continue
                current_edge_tuple = (u_node, v_node)
                # Create if not an original edge AND not already created as part of original edges (e.g. if graph was directed initially)
                if current_edge_tuple not in self.original_edge_tuples and current_edge_tuple not in self.edge_mobjects:
                    n_u_dot = self.node_mobjects[u_node][0]; n_v_dot = self.node_mobjects[v_node][0]
                    rev_arrow = Arrow(n_u_dot.get_center(), n_v_dot.get_center(), buff=NODE_RADIUS,
                                        stroke_width=EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR,
                                        color=REVERSE_EDGE_COLOR,
                                        max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH * 0.8, 
                                        z_index=REVERSE_EDGE_Z_INDEX) 
                    rev_arrow.set_opacity(REVERSE_EDGE_OPACITY if REVERSE_EDGE_OPACITY > 0 else 0.0) 
                    self.edge_mobjects[current_edge_tuple] = rev_arrow
                    edges_vgroup.add(rev_arrow) # Add to the main edges group for scaling

                    # Residual capacity label for these non-original edges
                    # Initial capacity is 0, so label is "0" and transparent
                    res_cap_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR, opacity=0.0) 
                    res_cap_val_mobj.move_to(rev_arrow.get_center()).rotate(rev_arrow.get_angle())
                    offset_vector_rev = rotate_vector(rev_arrow.get_unit_vector(), PI / 2) * 0.15
                    res_cap_val_mobj.shift(offset_vector_rev).set_z_index(1) 

                    self.edge_residual_capacity_mobjects[current_edge_tuple] = res_cap_val_mobj
                    self.base_label_visual_attrs[current_edge_tuple] = {"opacity": 0.0}

                    pure_rev_label_group = VGroup(res_cap_val_mobj) 
                    pure_rev_label_group.set_opacity(0.0) 
                    self.edge_label_groups[current_edge_tuple] = pure_rev_label_group
                    all_edge_labels_vgroup.add(pure_rev_label_group)

        if capacities_to_animate_write: self.play(LaggedStart(*[Write(c) for c in capacities_to_animate_write], lag_ratio=0.05), run_time=1.2); self.wait(0.5)
        if flow_slashes_to_animate_write: self.play(LaggedStart(*[Write(fs_group) for fs_group in flow_slashes_to_animate_write], lag_ratio=0.05), run_time=1.2); self.wait(0.5)

        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, all_edge_labels_vgroup)
        temp_scaled_network_for_height = self.network_display_group.copy().scale(self.desired_large_scale)
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_XLARGE 
        target_position = np.array([0, network_target_y, 0]) 

        self.base_edge_visual_attrs = {}
        for edge_key, edge_mo in self.edge_mobjects.items():
            self.base_edge_visual_attrs[edge_key] = {
                "color": edge_mo.get_color(),
                "stroke_width": edge_mo.get_stroke_width(),
                "opacity": edge_mo.get_stroke_opacity()
            }
            if edge_key not in self.base_label_visual_attrs: 
                self.base_label_visual_attrs[edge_key] = {"opacity": 1.0 if edge_key in self.original_edge_tuples else 0.0} 

        self.play(self.network_display_group.animate.scale(self.desired_large_scale).move_to(target_position))
        self.wait(0.5)
        
        if hasattr(self, 'node_mobjects') and hasattr(self, 'source_node') and \
           self.source_node in self.node_mobjects and self.node_mobjects.get(self.source_node):
            source_node_dot = self.node_mobjects[self.source_node][0] 
            self.action_text_mobj.next_to(source_node_dot, UP, buff=BUFF_SMALL)
        else:
            self.action_text_mobj.to_corner(UL, buff=BUFF_MED) 

        for edge_key, edge_mo in self.edge_mobjects.items():
            base_attrs_edge = self.base_edge_visual_attrs.get(edge_key)
            if base_attrs_edge:
                current_opacity = base_attrs_edge["opacity"]
                if edge_key not in self.original_edge_tuples and REVERSE_EDGE_OPACITY == 0.0:
                    current_opacity = 0.0 
                edge_mo.set_opacity(current_opacity) 
            label_grp = self.edge_label_groups.get(edge_key)
            if label_grp: 
                base_attrs_label = self.base_label_visual_attrs.get(edge_key)
                if base_attrs_label:
                    label_grp.set_opacity(base_attrs_label["opacity"])
                elif edge_key in self.original_edge_tuples: 
                    label_grp.set_opacity(1.0)
                else: 
                    label_grp.set_opacity(0.0)

        sample_text_mobj = None
        for key_orig_edge in self.original_edge_tuples: 
            if key_orig_edge in self.edge_flow_val_text_mobjects and self.edge_flow_val_text_mobjects[key_orig_edge] is not None:
                sample_text_mobj = self.edge_flow_val_text_mobjects[key_orig_edge]
                break
        if sample_text_mobj: 
            self.scaled_flow_text_height = sample_text_mobj.height
        else: 
            dummy_text_unscaled = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE)
            self.scaled_flow_text_height = dummy_text_unscaled.scale(self.desired_large_scale).height

        self.base_node_visual_attrs = {}
        for v_id, node_group in self.node_mobjects.items():
            dot, label = node_group 
            self.base_node_visual_attrs[v_id] = {
                "width": dot.width, 
                "fill_color": dot.get_fill_color(),
                "stroke_color": dot.get_stroke_color(),
                "stroke_width": dot.get_stroke_width(),
                "opacity": dot.get_fill_opacity(),
                "label_color": label.get_color()
            }

        source_node_dot = self.node_mobjects[self.source_node][0]
        sink_node_dot = self.node_mobjects[self.sink_node][0]
        temp_source_ring = Circle(radius=source_node_dot.width / 2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(source_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        temp_sink_ring = Circle(radius=sink_node_dot.width / 2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(sink_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        self.play(Create(temp_source_ring), Create(temp_sink_ring), run_time=0.4)
        self.play(Indicate(temp_source_ring, color=WHITE, scale_factor=1.15, rate_func=there_and_back_with_pause, run_time=0.7),
                  Indicate(temp_sink_ring, color=WHITE, scale_factor=1.15, rate_func=there_and_back_with_pause, run_time=0.7))
        self.play(FadeOut(temp_source_ring), FadeOut(temp_sink_ring), run_time=0.4)

        source_label_original = self.node_mobjects[self.source_node][1]
        sink_label_original = self.node_mobjects[self.sink_node][1]
        new_s_label_mobj = Text("s", font_size=NODE_LABEL_FONT_SIZE, weight=BOLD, color=self.base_node_visual_attrs[self.source_node]["label_color"]).move_to(source_label_original.get_center()).set_z_index(source_label_original.z_index)
        new_t_label_mobj = Text("t", font_size=NODE_LABEL_FONT_SIZE, weight=BOLD, color=self.base_node_visual_attrs[self.sink_node]["label_color"]).move_to(sink_label_original.get_center()).set_z_index(sink_label_original.z_index)
        self.play(Transform(source_label_original, new_s_label_mobj), Transform(sink_label_original, new_t_label_mobj), run_time=0.5)
        self.node_mobjects[self.source_node][1] = new_s_label_mobj
        self.node_mobjects[self.sink_node][1] = new_t_label_mobj
        self.wait(0.5)

        # --- Start Edmonds-Karp Algorithm Iterations ---
        self.update_section_title("2. Running Edmonds-Karp Algorithm", play_anim=True)
        self.update_max_flow_display(play_anim=False) # Show initial flow
        self.wait(1.0)

        while True:
            self.current_iteration_num += 1
            self.update_iteration_text(f"Iteration {self.current_iteration_num}: Find Augmenting Path (BFS)", color=BLUE_B, play_anim=True)
            self._update_action_text("", animate=False) 
            self.wait(1.0) 

            # Restore graph to a neutral state before BFS highlighting, keeping existing flow states
            self._restore_graph_appearance() # This will visually show current residual graph

            # BFS to find an augmenting path and its bottleneck capacity
            # This function also animates the BFS search and path highlight
            path_edges, bottleneck_capacity = self._bfs_find_augmenting_path_and_animate_search()

            if bottleneck_capacity == 0 or not path_edges:
                self.update_iteration_text(f"End of Iteration {self.current_iteration_num -1}", color=TEAL_A, play_anim=False)
                self.update_status_text("No more augmenting paths found. Algorithm terminates.", color=RED_C, play_anim=True)
                self.wait(3.0)
                break # Exit main Edmonds-Karp loop
            
            # Animate flow augmentation along the found path
            # This function updates self.flow, animates pulses, text, and edge visuals
            self._animate_flow_augmentation(path_edges, bottleneck_capacity)
            
            self.update_iteration_text(f"Iteration {self.current_iteration_num}: Flow Augmented. Total Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
            self.wait(2.5)
            
            # Prepare for next iteration or termination
            if self.current_iteration_num >= 25: # Safety break for very long runs
                 self.update_status_text("Reached maximum iterations. Terminating.", color=RED_A, play_anim=True); self.wait(2); break


        # Algorithm conclusion
        self.update_section_title("3. Edmonds-Karp Algorithm Summary", play_anim=True)
        self.wait(1.0)
        final_status_msg = f"Algorithm Concluded. Final Max Flow: {self.max_flow_value:.1f}"
        final_status_color = GREEN_A
        if self.max_flow_value == 0 and self.current_iteration_num <=1 : # No path ever found
            final_status_msg = f"Algorithm Concluded. Sink Unreachable or no capacity. Max Flow: {self.max_flow_value:.1f}"
            final_status_color = RED_A
        
        self.update_status_text(final_status_msg, color=final_status_color, play_anim=True)
        self.update_iteration_text("",play_anim=True) # Clear iteration text
        self.wait(5.0)

        if hasattr(self, 'node_mobjects') and self.node_mobjects and \
           hasattr(self, 'source_node') and hasattr(self, 'sink_node') and \
           self.source_node in self.node_mobjects and self.sink_node in self.node_mobjects:
            source_dot_final = self.node_mobjects[self.source_node][0]
            sink_dot_final = self.node_mobjects[self.sink_node][0]
            other_node_dots_final = [self.node_mobjects[nid][0] for nid in self.vertices_data if nid != self.source_node and nid != self.sink_node and nid in self.node_mobjects]
            
            anims_final_emphasis = [Flash(dot, color=BLUE_A, flash_radius=NODE_RADIUS * 2.0) for dot in other_node_dots_final]
            anims_final_emphasis.append(Flash(source_dot_final, color=GOLD_D, flash_radius=NODE_RADIUS * 3.0))
            anims_final_emphasis.append(Flash(sink_dot_final, color=RED_C, flash_radius=NODE_RADIUS * 3.0))
            if anims_final_emphasis:
                self.play(*anims_final_emphasis, run_time=2.0)
        self.wait(2.0)
        
        # Clean up scene
        mobjects_that_should_remain = Group(self.main_title, self.info_texts_group)
        final_mobjects_to_fade_out = Group()
        all_descendants_of_kept = set()
        for mobj_to_keep in mobjects_that_should_remain:
            all_descendants_of_kept.update(mobj_to_keep.get_family())
        for mobj_on_scene in list(self.mobjects): 
            if mobj_on_scene not in all_descendants_of_kept:
                final_mobjects_to_fade_out.add(mobj_on_scene)
        if final_mobjects_to_fade_out.submobjects: 
            self.play(FadeOut(final_mobjects_to_fade_out, run_time=1.0))
        self.wait(6)