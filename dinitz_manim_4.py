from manim import *
import collections

# --- Style and Layout Constants ---
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.18

MAIN_TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28 # For text below main title
PHASE_TEXT_FONT_SIZE = 22    # For text below section title
STATUS_TEXT_FONT_SIZE = 20   # For text below phase title
NODE_LABEL_FONT_SIZE = 16
EDGE_CAPACITY_LABEL_FONT_SIZE = 12
EDGE_FLOW_PREFIX_FONT_SIZE = 12
LEVEL_TEXT_FONT_SIZE = 18

MAIN_TITLE_SMALL_SCALE = 0.65

BUFF_VERY_SMALL = 0.05
BUFF_SMALL = 0.1
BUFF_MED = 0.25
BUFF_LARGE = 0.4
BUFF_XLARGE = 0.6

RING_COLOR = YELLOW_C
RING_STROKE_WIDTH = 3.5
RING_RADIUS_OFFSET = 0.1
RING_Z_INDEX = 4

LEVEL_COLORS = [RED_D, ORANGE, YELLOW_D, GREEN_D, BLUE_D, PURPLE_D, PINK]
DEFAULT_NODE_COLOR = BLUE_E
DEFAULT_EDGE_COLOR = GREY_C
LABEL_TEXT_COLOR = DARK_GREY # Used for edge labels, node labels are initially WHITE
LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH = 4.5
DFS_EDGE_TRY_WIDTH = LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH * 1.15
DFS_PATH_EDGE_WIDTH = LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH * 1.25

DIMMED_OPACITY = 0.20
DIMMED_COLOR = GREY_BROWN

TOP_CENTER_ANCHOR = UP * (config.frame_height / 2 - BUFF_SMALL)

class DinitzAlgorithmVisualizer(Scene):

    def setup_titles_and_placeholders(self):
        # Initializes the main title and placeholders for other informational text.
        self.main_title = Text("Visualizing Dinitz's Algorithm", font_size=MAIN_TITLE_FONT_SIZE)
        self.main_title.move_to(TOP_CENTER_ANCHOR)
        self.main_title.set_z_index(5) # Ensure title is on top
        self.add(self.main_title)
        self.play(Write(self.main_title), run_time=1)
        self.wait(0.5)

        # Placeholders for section titles, phase descriptions, and status updates.
        self.current_section_title_mobj = Text("", font_size=SECTION_TITLE_FONT_SIZE, weight=BOLD)
        self.phase_text_mobj = Text("", font_size=PHASE_TEXT_FONT_SIZE, weight=BOLD)
        self.algo_status_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE)

        # Grouping these texts for easier management and positioning.
        self.info_texts_group = VGroup(
            self.current_section_title_mobj,
            self.phase_text_mobj,
            self.algo_status_mobj
        ).set_z_index(5) # Ensure these are also on top

        self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED)
        self.info_texts_group.next_to(self.main_title, DOWN, buff=BUFF_MED)

        self.add(self.info_texts_group)

        # Placeholder for displaying levels found during BFS.
        self.level_display_vgroup = VGroup().set_z_index(5)
        self.level_display_vgroup.to_corner(UR, buff=BUFF_LARGE)
        self.add(self.level_display_vgroup)


    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
        # Helper function to animate transitions between old and new text mobjects.
        old_text_had_actual_content = isinstance(old_mobj, Text) and old_mobj.text != ""
        out_animation = None
        in_animation = None

        if old_text_had_actual_content:
            out_animation = FadeOut(old_mobj, run_time=0.35)

        if new_text_content_str != "":
            # Create new mobject only if there's new text.
            in_animation = FadeIn(new_mobj, run_time=0.35, shift=ORIGIN)

        animations_to_play = []
        if out_animation: animations_to_play.append(out_animation)
        if in_animation: animations_to_play.append(in_animation)

        if animations_to_play:
            self.play(*animations_to_play)

    def _update_text_generic(self, text_attr_name, new_text_str, font_size, weight, color, play_anim=True):
        # Generic function to update one of the informational text mobjects.
        old_mobj = getattr(self, text_attr_name)
        was_placeholder = (old_mobj.text == "") # Check if the old mobject was just an empty placeholder

        new_mobj = Text(new_text_str, font_size=font_size, weight=weight, color=color)

        # Replace old mobject with new one in the VGroup and scene.
        try:
            idx = self.info_texts_group.submobjects.index(old_mobj)
            self.info_texts_group.remove(old_mobj)
            # If the old mobject was a placeholder and part of the scene, remove it.
            if was_placeholder and old_mobj in self.mobjects:
                self.remove(old_mobj)
            self.info_texts_group.insert(idx, new_mobj)
        except ValueError: # pragma: no cover (Should not happen if setup is correct)
            # Fallback if old_mobj wasn't in info_texts_group for some reason
            if old_mobj in self.mobjects:
                self.remove(old_mobj)
            self.info_texts_group.add(new_mobj) # Add if it was never there or as a fallback

        setattr(self, text_attr_name, new_mobj) # Update the attribute to point to the new mobject

        # Rearrange the info_texts_group after update.
        self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED)
        # Reposition relative to the main title if it exists.
        if hasattr(self, 'main_title') and self.main_title in self.mobjects:
             self.info_texts_group.next_to(self.main_title, DOWN, buff=BUFF_MED)

        self.bring_to_front(self.info_texts_group) # Ensure it's visible

        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_str)
        else:
            # If not animating, directly remove old and add new if necessary.
            if old_mobj in self.mobjects and old_mobj is not new_mobj : self.remove(old_mobj)
            if new_text_str != "" and new_mobj not in self.mobjects: self.add(new_mobj)
            elif new_text_str == "" and new_mobj in self.mobjects : self.remove(new_mobj) # Remove if new text is empty

    def update_section_title(self, text_str, play_anim=True):
        # Updates the section title text.
        self._update_text_generic("current_section_title_mobj", text_str, SECTION_TITLE_FONT_SIZE, BOLD, WHITE, play_anim)

    def update_phase_text(self, text_str, color=WHITE, play_anim=True):
        # Updates the phase description text.
        self._update_text_generic("phase_text_mobj", text_str, PHASE_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True):
        # Updates the algorithm status text.
        self._update_text_generic("algo_status_mobj", text_str, STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim)

    def _dfs_recursive_find_path_anim(self, u, pushed, current_path_info_list):
        # Recursive DFS function to find an augmenting path in the level graph.
        # u: current node
        # pushed: current bottleneck capacity found so far in the path from source to u
        # current_path_info_list: list to store information about edges in the found path for animation
        
        u_dot_group = self.node_mobjects[u]
        u_dot = u_dot_group[0]

        # Highlight the current node being visited by DFS
        highlight_ring = Circle(
            radius=u_dot.width/2 * 1.3, # Slightly larger than the node
            color=PINK,
            stroke_width=RING_STROKE_WIDTH * 0.7
        ).move_to(u_dot.get_center()).set_z_index(u_dot.z_index + 2) # Ensure ring is above node
        self.dfs_traversal_highlights.add(highlight_ring)
        self.play(Create(highlight_ring), run_time=0.25)

        if u == self.sink_node: # Base case: Reached the sink node
            self.play(FadeOut(highlight_ring), run_time=0.15) # Remove highlight
            self.dfs_traversal_highlights.remove(highlight_ring)
            return pushed # Return the bottleneck capacity of the path found

        # Explore neighbors of u
        while self.ptr[u] < len(self.adj[u]):
            v_candidate = self.adj[u][self.ptr[u]] # Get next neighbor using pointer

            # Calculate residual capacity of the edge (u, v_candidate)
            res_cap_cand = self.capacities.get((u, v_candidate), 0) - self.flow.get((u, v_candidate), 0)
            edge_mo_cand = self.edge_mobjects.get((u,v_candidate)) # Get mobject for the edge

            # Check if this edge is part of the current Level Graph (LG)
            # 1. Edge mobject exists (i.e., it's an original edge, not just a conceptual reverse edge for logic)
            # 2. Level of v_candidate is exactly one greater than level of u
            # 3. Residual capacity is positive
            is_valid_lg_edge = (edge_mo_cand and \
                               self.levels.get(v_candidate, -1) == self.levels.get(u, -1) + 1 and \
                               res_cap_cand > 0)

            if is_valid_lg_edge:
                actual_v = v_candidate
                edge_mo_for_v = edge_mo_cand
                res_cap_for_v = res_cap_cand

                # Store original appearance for restoration
                original_edge_color = edge_mo_for_v.get_color()
                original_edge_width = edge_mo_for_v.get_stroke_width()
                original_edge_opacity = edge_mo_for_v.get_stroke_opacity()

                # Animate trying this edge
                self.play(edge_mo_for_v.animate.set_color(YELLOW_A).set_stroke(width=DFS_EDGE_TRY_WIDTH, opacity=1.0), run_time=0.3)

                # Recursively call DFS for the neighbor
                # Pass min(pushed, res_cap_for_v) as the new bottleneck capacity
                tr = self._dfs_recursive_find_path_anim(actual_v, min(pushed, res_cap_for_v), current_path_info_list)

                if tr > 0: # If a path to sink is found through this edge (tr > 0)
                    # Add edge info to path list for later animation of augmentation
                    current_path_info_list.append(((u, actual_v), edge_mo_for_v, original_edge_color, original_edge_width, original_edge_opacity))
                    self.play(FadeOut(highlight_ring), run_time=0.15) # Remove highlight from u
                    self.dfs_traversal_highlights.remove(highlight_ring)
                    return tr # Propagate the bottleneck flow value back up the recursion

                # If DFS from actual_v did not reach the sink (tr == 0)
                # This edge led to a dead end in this DFS attempt. Restore its appearance.
                self.play(
                    edge_mo_for_v.animate.set_color(original_edge_color).set_stroke(width=original_edge_width, opacity=original_edge_opacity),
                    run_time=0.3
                )
                # Indicate that this edge was tried but didn't lead to a path in this attempt
                self.play(Indicate(edge_mo_for_v, color=RED_D, scale_factor=1.0, run_time=0.35)) 

            self.ptr[u] += 1 # Move pointer to the next neighbor of u for subsequent attempts from u

        # If loop finishes, all neighbors of u (from current ptr[u] onwards) have been tried without finding a path.
        # Node u is "stuck" in this DFS traversal from its predecessor.
        # "Retreat to previous node" is handled by returning 0.
        # The concept of "deleting node from LG" for this path is implicitly handled by ptr:
        # u won't be successfully used again from this specific incoming path because ptr[u] has advanced.
        
        # No specific text for "stuck" here to avoid clutter; visual cues suffice.
        # Fade out highlight for current node u as we backtrack.
        self.play(FadeOut(highlight_ring), run_time=0.15)
        self.dfs_traversal_highlights.remove(highlight_ring)
        return 0 # Return 0 to indicate no path to sink found from u with remaining edges

    def animate_dfs_path_finding_phase(self):
        # This function orchestrates the DFS phase to find a blocking flow in the current level graph.
        
        # ptr[v] stores the next edge to explore from node v in its adjacency list during DFS.
        # This helps avoid re-exploring edges that led to dead ends in the current DFS phase.
        self.ptr = {v_id: 0 for v_id in self.vertices_data} 

        total_flow_this_phase = 0 # Accumulates flow found in this Dinitz phase
        path_count_this_phase = 0 # Counts DFS attempts to find paths
        self.dfs_traversal_highlights = VGroup().set_z_index(RING_Z_INDEX + 1) # For DFS node highlights
        self.add(self.dfs_traversal_highlights)

        self.update_phase_text(f"Phase {self.current_phase_num}: Finding Augmenting Paths in LG (DFS)", color=ORANGE, play_anim=True)
        self.wait(0.5)

        while True: # Loop to find multiple augmenting paths (blocking flow) in the current Level Graph (LG)
            path_count_this_phase += 1
            self.update_status_text(f"DFS Attempt #{path_count_this_phase}: Searching s->t path from S={self.source_node} in LG", play_anim=True)

            current_path_anim_info = [] # Stores ((u,v), edge_mo, original_style_info...) for edges in the found path

            # Call recursive DFS to find one s-t path.
            # float('inf') is the initial available capacity for the path.
            bottleneck_flow = self._dfs_recursive_find_path_anim(
                self.source_node,
                float('inf'), 
                current_path_anim_info 
            )

            if bottleneck_flow == 0:
                # No more s-t paths can be found in the current Level Graph.
                self.update_status_text("No more s-t paths in current Level Graph.", color=YELLOW_C, play_anim=True)
                self.wait(1.5)
                break # Exit the while loop for this DFS phase

            # An s-t path was found. Augment flow along this path.
            total_flow_this_phase += bottleneck_flow
            self.update_status_text(f"Path s->t found! Bottleneck: {bottleneck_flow:.1f}. Augmenting flow.", color=GREEN_A, play_anim=True)

            # Highlight the found path
            path_highlight_anims = []
            current_path_anim_info.reverse() # Path is collected in reverse during DFS backtracking
            for (u_path,v_path), edge_mo_path, _, _, _ in current_path_anim_info:
                path_highlight_anims.append(
                    edge_mo_path.animate.set_color(GREEN_D).set_stroke(width=DFS_PATH_EDGE_WIDTH, opacity=1.0)
                )
            if path_highlight_anims:
                self.play(AnimationGroup(*path_highlight_anims, lag_ratio=0.15, run_time=0.8))
            self.wait(0.6)

            # Update flow values, text labels, and edge appearances (part of "residual graph updates")
            augmentation_anims = [] # Animations for edge style changes (e.g., dimming)
            text_update_anims = []  # Animations for flow text value changes

            for (u,v), edge_mo, orig_color, orig_width, orig_opacity in current_path_anim_info:
                # Augment flow on the forward edge (u,v)
                self.flow[(u,v)] = self.flow.get((u,v), 0) + bottleneck_flow
                # Update flow on the conceptual reverse edge (v,u) for residual graph correctness
                self.flow[(v,u)] = self.flow.get((v,u), 0) - bottleneck_flow

                # Update the displayed flow value text mobject for edge (u,v)
                old_flow_text_mobj = self.edge_flow_val_text_mobjects[(u,v)]
                new_flow_val = self.flow[(u,v)]
                # Format flow value (integer if whole number, else one decimal place)
                new_flow_str = f"{new_flow_val:.0f}" if abs(new_flow_val - round(new_flow_val)) < 0.01 else f"{new_flow_val:.1f}"
                
                arrow = self.edge_mobjects[(u,v)] # Get arrow mobject for orientation
                # Create a target text mobject for smooth animation (become)
                target_text_template = Text(
                    new_flow_str,
                    font=old_flow_text_mobj.font,
                    font_size=EDGE_FLOW_PREFIX_FONT_SIZE, # Use consistent font size
                    color=LABEL_TEXT_COLOR
                )
                # Ensure consistent height if scaled_flow_text_height is set
                if hasattr(self, 'scaled_flow_text_height') and self.scaled_flow_text_height is not None:
                    target_text_template.set_height(self.scaled_flow_text_height)
                else: # pragma: no cover
                    target_text_template.match_height(old_flow_text_mobj) # Fallback
                
                target_text_template.move_to(old_flow_text_mobj.get_center()) # Position at old text's center
                target_text_template.rotate(arrow.get_angle(), about_point=target_text_template.get_center()) # Match edge angle
                text_update_anims.append(old_flow_text_mobj.animate.become(target_text_template))

                # Check if the edge (u,v) is still part of the Level Graph after augmentation
                res_cap_after = self.capacities[(u,v)] - self.flow.get((u,v),0)
                is_still_lg_edge = (self.levels.get(u,-1)!=-1 and self.levels.get(v,-1)!=-1 and \
                                    self.levels[v]==self.levels[u]+1 and res_cap_after > 0)

                if not is_still_lg_edge: 
                    # Edge is saturated or no longer a valid forward edge in the LG. Dim it.
                    augmentation_anims.append(edge_mo.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR, width=EDGE_STROKE_WIDTH))
                else: 
                    # Edge is still usable in LG. Revert its appearance to the LG style.
                    # (It was green from path highlighting, now back to its level color)
                    augmentation_anims.append(edge_mo.animate.set_color(LEVEL_COLORS[self.levels[u]%len(LEVEL_COLORS)]).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, opacity=orig_opacity))

            all_augmentation_related_anims = text_update_anims + augmentation_anims
            if all_augmentation_related_anims:
                 self.play(AnimationGroup(*all_augmentation_related_anims, lag_ratio=0.1), run_time=1.2)
            else: # pragma: no cover (Should always have animations if path found)
                 self.wait(1.0)

            # "Restart from s": The loop continues to find the next path in the *same* Level Graph.
            self.update_status_text(f"Augmented. Flow this phase: {total_flow_this_phase:.1f}. Searching for next s-t path...", color=WHITE, play_anim=True)
            self.wait(1.0)

        # Cleanup any remaining DFS highlights (e.g., if loop broke early or source was stuck initially)
        if self.dfs_traversal_highlights.submobjects:
            self.play(FadeOut(self.dfs_traversal_highlights), run_time=0.2)
            self.remove(self.dfs_traversal_highlights) # Ensure removal from scene
        return total_flow_this_phase # Return total flow pushed in this Dinitz phase

    def construct(self):
        # Main method to construct the animation scene.
        self.setup_titles_and_placeholders()
        
        self.scaled_flow_text_height = None # Will be set after scaling graph, for consistent text size

        # --- Graph Data Definition ---
        self.source_node, self.sink_node = 1, 10
        self.vertices_data = list(range(1, 11)) # Nodes 1 to 10
        self.edges_with_capacity_list = [ # (u, v, capacity)
            (1,2,25),(1,3,30),(1,4,20),(2,5,25),(3,4,30),(3,5,35),(4,6,30),
            (5,7,40),(5,8,40),(6,8,35),(6,9,30),(7,10,20),(8,10,20),(9,10,20)
        ]
        
        # --- Graph Data Structures ---
        self.capacities = collections.defaultdict(int) # Stores original capacities
        self.flow = collections.defaultdict(int)       # Stores current flow on edges
        self.adj = collections.defaultdict(list)       # Adjacency list for graph traversal

        # Populate capacities and adjacency list.
        # Also add reverse edges to adj for BFS/DFS on the residual graph.
        # Their capacities are implicitly 0 via defaultdict if not in original list.
        for u,v,cap in self.edges_with_capacity_list:
            self.capacities[(u,v)] = cap
            if v not in self.adj[u]: # Add forward edge to adjacency list
                self.adj[u].append(v)
            # Add reverse edge to adjacency list for residual graph logic
            if u not in self.adj[v]: 
                self.adj[v].append(u)

        # Predefined layout for nodes to ensure a clear visualization
        self.graph_layout = {
            1: [-3,0,0], 2:[-2,1,0], 3:[-2,0,0], 4:[-2,-1,0], 5:[-0.5,0.75,0], 6:[-0.5,-0.75,0],
            7: [1,1,0], 8:[1,0,0], 9:[1,-1,0], 10:[2.5,0,0]
        }

        # Dictionaries to store Manim mobjects for graph elements
        self.node_mobjects = {}; self.edge_mobjects = {};
        self.edge_capacity_text_mobjects = {}; self.edge_flow_val_text_mobjects = {};
        self.edge_slash_text_mobjects = {} # For the "/" in "flow/capacity"
        self.edge_label_groups = {} # VGroup for "flow / capacity" text per edge

        self.desired_large_scale = 1.6 # Scaling factor for the graph display

        self.update_section_title("1. Building the Network", play_anim=False) # Initial section title

        # --- Create Node Mobjects ---
        nodes_vgroup = VGroup() # Group for all node mobjects
        for v_id in self.vertices_data:
            dot = Dot(point=self.graph_layout[v_id], radius=NODE_RADIUS, color=DEFAULT_NODE_COLOR, z_index=2, stroke_color=BLACK, stroke_width=NODE_STROKE_WIDTH)
            # Node labels are initially WHITE by default Text behavior
            label = Text(str(v_id), font_size=NODE_LABEL_FONT_SIZE, weight=BOLD).move_to(dot.get_center()).set_z_index(3)
            self.node_mobjects[v_id] = VGroup(dot,label); nodes_vgroup.add(self.node_mobjects[v_id])
        self.play(LaggedStart(*[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data], lag_ratio=0.05), run_time=1.5)

        # --- Create Edge Mobjects ---
        edges_vgroup = VGroup() # Group for all edge mobjects
        edge_grow_anims = []
        for u,v,cap in self.edges_with_capacity_list: # Only create mobjects for original edges
            n_u_dot = self.node_mobjects[u][0]; n_v_dot = self.node_mobjects[v][0]
            arrow = Arrow(n_u_dot.get_center(), n_v_dot.get_center(), buff=NODE_RADIUS, 
                          stroke_width=EDGE_STROKE_WIDTH, color=DEFAULT_EDGE_COLOR, 
                          max_tip_length_to_length_ratio=0.2, tip_length=ARROW_TIP_LENGTH, z_index=0)
            self.edge_mobjects[(u,v)] = arrow; edges_vgroup.add(arrow)
            edge_grow_anims.append(GrowArrow(arrow))
        self.play(LaggedStart(*edge_grow_anims, lag_ratio=0.05), run_time=1.5)

        # --- Create Edge Label Mobjects (Flow/Capacity) ---
        all_edge_labels_vgroup = VGroup()
        capacities_to_animate_write = []
        flow_slashes_to_animate_write = []

        for u, v, cap in self.edges_with_capacity_list: # Labels only for original edges
            arrow = self.edge_mobjects[(u,v)]
            # Initial flow is 0
            flow_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            slash_mobj = Text("/", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            cap_text_mobj = Text(str(cap), font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=LABEL_TEXT_COLOR)

            self.edge_flow_val_text_mobjects[(u,v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u,v)] = slash_mobj
            self.edge_capacity_text_mobjects[(u,v)] = cap_text_mobj

            label_group = VGroup(flow_val_mobj, slash_mobj, cap_text_mobj)
            label_group.arrange(RIGHT, buff=BUFF_VERY_SMALL) # Arrange "0 / cap"
            label_group.move_to(arrow.get_center()) # Position near edge center
            label_group.rotate(arrow.get_angle())   # Align with edge
            # Offset label slightly from the edge for clarity
            offset_distance = 0.25 
            offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * offset_distance
            label_group.shift(offset_vector)
            label_group.set_z_index(1) # Above edges, below nodes
            self.edge_label_groups[(u,v)] = label_group
            all_edge_labels_vgroup.add(label_group)
            
            # For animation
            capacities_to_animate_write.append(cap_text_mobj)
            flow_slashes_to_animate_write.append(VGroup(flow_val_mobj, slash_mobj))

        if capacities_to_animate_write: self.play(LaggedStart(*[Write(c) for c in capacities_to_animate_write], lag_ratio=0.05), run_time=1.2)
        if flow_slashes_to_animate_write: self.play(LaggedStart(*[Write(fs_group) for fs_group in flow_slashes_to_animate_write], lag_ratio=0.05), run_time=1.2)

        # Group all network elements for scaling and positioning
        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, all_edge_labels_vgroup)
        
        # Scale and position the entire network
        temp_scaled_network_for_height = self.network_display_group.copy().scale(self.desired_large_scale)
        # Calculate target Y position to center it nicely below titles
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_XLARGE
        target_position = np.array([0, network_target_y, 0])
        self.play(self.network_display_group.animate.scale(self.desired_large_scale).move_to(target_position))
        
        # Store scaled height of flow text for consistent updates later
        if self.edge_flow_val_text_mobjects:
            first_edge_key = next(iter(self.edge_flow_val_text_mobjects))
            sample_flow_mobj = self.edge_flow_val_text_mobjects[first_edge_key]
            self.scaled_flow_text_height = sample_flow_mobj.height 
        else: # pragma: no cover
            # Fallback if no edges (should not happen with example data)
            dummy_text = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE)
            self.scaled_flow_text_height = dummy_text.height * self.desired_large_scale

        # Store base visual attributes of nodes and edges after scaling, for restoration or reference
        self.base_node_visual_attrs = {} 
        for v_id, node_group in self.node_mobjects.items():
            dot = node_group[0]
            label = node_group[1] # Get the label mobject
            self.base_node_visual_attrs[v_id] = {
                "width": dot.get_width(), "fill_color": dot.get_fill_color(),
                "stroke_color": dot.get_stroke_color(), "stroke_width": dot.get_stroke_width(),
                "opacity": dot.get_fill_opacity(),
                "label_color": label.get_color() # Store initial label color (should be WHITE)
            }
        self.base_edge_visual_attrs = {}
        for edge_key, edge_mo in self.edge_mobjects.items():
            self.base_edge_visual_attrs[edge_key] = {
                "color": edge_mo.get_color(), # Should be DEFAULT_EDGE_COLOR
                "stroke_width": edge_mo.get_stroke_width(),
                "opacity": edge_mo.get_stroke_opacity()
            }

        # Highlight Source (S) and Sink (T) nodes
        s_dot = self.node_mobjects[self.source_node][0]; t_dot = self.node_mobjects[self.sink_node][0]
        source_ring = Circle(radius=s_dot.width/2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(s_dot.get_center()).set_z_index(RING_Z_INDEX)
        sink_ring = Circle(radius=t_dot.width/2 + RING_RADIUS_OFFSET, color=RING_COLOR, stroke_width=RING_STROKE_WIDTH).move_to(t_dot.get_center()).set_z_index(RING_Z_INDEX)
        self.source_ring_mobj = source_ring; self.sink_ring_mobj = sink_ring
        self.play(Create(self.source_ring_mobj), Create(self.sink_ring_mobj), run_time=0.75)
        self.wait(1.0)
        self.update_status_text("", play_anim=False); self.wait(0.5) # Clear status before starting algorithm

        # --- Dinitz Algorithm Execution Begins ---
        self.update_section_title("2. Dinitz Algorithm Execution")
        self.current_phase_num = 0 # Start with phase 0, will increment before first BFS
        self.max_flow_value = 0
        
        # Main loop of Dinitz: Repeats as long as BFS finds an s-t path in residual graph
        while True:
            self.current_phase_num += 1
            # --- BFS Phase: Construct Level Graph (LG) ---
            self.update_phase_text(f"Phase {self.current_phase_num}: Construct Level Graph (LG) using BFS", color=BLUE_B)
            self.update_status_text(f"Starting BFS from S={self.source_node} to find levels to T={self.sink_node}")
            self.wait(0.5)

            # Reset levels for all nodes (-1 means unvisited/unreachable)
            self.levels = {v_id: -1 for v_id in self.vertices_data} 
            q_bfs = collections.deque() # Queue for BFS

            # Start BFS from source node
            current_bfs_level_num = 0
            self.levels[self.source_node] = current_bfs_level_num
            q_bfs.append(self.source_node)
            
            # Display level information on screen
            # Clear previous level display if any
            if self.level_display_vgroup.submobjects:
                self.play(FadeOut(self.level_display_vgroup))
                self.remove(self.level_display_vgroup) # Ensure it's fully removed before re-adding
                self.level_display_vgroup = VGroup().set_z_index(5).to_corner(UR, buff=BUFF_LARGE)
                self.add(self.level_display_vgroup)


            l_p0 = Text(f"L{current_bfs_level_num}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[0])
            l_n0 = Text(f" {{{self.source_node}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
            l0_vg = VGroup(l_p0,l_n0).arrange(RIGHT,buff=BUFF_VERY_SMALL)
            self.level_display_vgroup.add(l0_vg)
            # Ensure consistent arrangement and positioning
            self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
            self.play(Write(l0_vg))
            max_level_text_width = config.frame_width * 0.30 # Max width for level display to avoid overflow
            
            # --- Visual Reset before new BFS phase ---
            # Restore all original graph nodes and edges to their base appearance.
            # This ensures that visual styles from the previous phase (e.g., dimming, level colors)
            # do not incorrectly carry over to the new phase's LG construction.
            restore_anims = []
            for v_id, node_attrs in self.base_node_visual_attrs.items():
                node_dot = self.node_mobjects[v_id][0]
                node_lbl = self.node_mobjects[v_id][1]
                restore_anims.append(node_dot.animate.set_width(node_attrs["width"])
                                                        .set_fill(node_attrs["fill_color"], opacity=node_attrs["opacity"])
                                                        .set_stroke(color=node_attrs["stroke_color"], width=node_attrs["stroke_width"]))
                # Restore node label to its original color
                restore_anims.append(node_lbl.animate.set_color(node_attrs["label_color"])) 
            
            for edge_key, edge_attrs in self.base_edge_visual_attrs.items():
                edge_mo = self.edge_mobjects.get(edge_key)
                if edge_mo:
                    restore_anims.append(edge_mo.animate.set_color(edge_attrs["color"])
                                                       .set_stroke(width=edge_attrs["stroke_width"], opacity=edge_attrs["opacity"]))
            if restore_anims:
                self.play(AnimationGroup(*restore_anims, lag_ratio=0.01, run_time=0.75))
            
            # Re-highlight S and T rings (as they might be part of network_display_group affected by general fades)
            # and re-color the source node for the start of the current BFS.
            s_dot_obj = self.node_mobjects[self.source_node][0]; s_lbl_obj = self.node_mobjects[self.source_node][1]
            s_base_width = self.base_node_visual_attrs[self.source_node]["width"]
            s_label_base_color = self.base_node_visual_attrs[self.source_node]["label_color"]

            self.play(
                self.source_ring_mobj.animate.set_opacity(1), 
                self.sink_ring_mobj.animate.set_opacity(1),
                s_dot_obj.animate.set_fill(LEVEL_COLORS[0]).set_width(s_base_width * 1.1), 
                s_lbl_obj.animate.set_color(BLACK if sum(color_to_rgb(LEVEL_COLORS[0])) > 1.5 else WHITE) # Contrast color for S label against its new level color
            )


            # BFS main loop
            while q_bfs:
                nodes_to_process_this_level = list(q_bfs); q_bfs.clear() # Process one level at a time
                if not nodes_to_process_this_level: break 

                target_level = self.levels[nodes_to_process_this_level[0]] + 1
                
                nodes_found_next_lvl_set = set() 
                node_color_anims_bfs = []      
                edge_highlight_anims_bfs_step = [] 

                for u_bfs in nodes_to_process_this_level:
                    node_to_indicate = self.node_mobjects[u_bfs]
                    ind_u = SurroundingRectangle(node_to_indicate, color=YELLOW_C, buff=0.03, stroke_width=2.0, corner_radius=0.05)
                    self.play(Create(ind_u), run_time=0.15)

                    for v_n_bfs in self.adj[u_bfs]: 
                        res_cap_bfs = self.capacities.get((u_bfs,v_n_bfs),0) - self.flow.get((u_bfs,v_n_bfs),0)
                        
                        if res_cap_bfs > 0 and self.levels[v_n_bfs] == -1: 
                            self.levels[v_n_bfs] = target_level 
                            nodes_found_next_lvl_set.add(v_n_bfs)
                            q_bfs.append(v_n_bfs) 
                            
                            lvl_color = LEVEL_COLORS[target_level % len(LEVEL_COLORS)]
                            n_v_dot = self.node_mobjects[v_n_bfs][0]; n_v_lbl = self.node_mobjects[v_n_bfs][1]
                            v_base_width = self.base_node_visual_attrs[v_n_bfs]["width"]
                            node_color_anims_bfs.append(n_v_dot.animate.set_fill(lvl_color).set_width(v_base_width * 1.1))
                            rgb_c = color_to_rgb(lvl_color); lbl_c = BLACK if sum(rgb_c)>1.5 else WHITE 
                            node_color_anims_bfs.append(n_v_lbl.animate.set_color(lbl_c))
                            
                            edge_mo_bfs = self.edge_mobjects.get((u_bfs, v_n_bfs))
                            if edge_mo_bfs:
                                 edge_color_bfs = LEVEL_COLORS[self.levels[u_bfs]%len(LEVEL_COLORS)] 
                                 edge_highlight_anims_bfs_step.append(edge_mo_bfs.animate.set_color(edge_color_bfs).set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH))
                            
                            # No need for bfs_path_found_to_sink_this_phase, sink reachability checked by levels[self.sink_node]
                    
                    self.play(FadeOut(ind_u), run_time=0.15) 
                
                if node_color_anims_bfs or edge_highlight_anims_bfs_step: 
                    self.play(AnimationGroup(*(node_color_anims_bfs + edge_highlight_anims_bfs_step), lag_ratio=0.1), run_time=0.6)
                
                if nodes_found_next_lvl_set:
                    n_str = ", ".join(map(str, sorted(list(nodes_found_next_lvl_set))))
                    l_px = Text(f"L{target_level}:", font_size=LEVEL_TEXT_FONT_SIZE, color=LEVEL_COLORS[target_level%len(LEVEL_COLORS)])
                    l_nx = Text(f" {{{n_str}}}", font_size=LEVEL_TEXT_FONT_SIZE, color=WHITE)
                    l_vg = VGroup(l_px,l_nx).arrange(RIGHT,buff=BUFF_VERY_SMALL)
                    self.level_display_vgroup.add(l_vg)
                    self.level_display_vgroup.arrange(DOWN, aligned_edge=LEFT, buff=BUFF_SMALL).to_corner(UR, buff=BUFF_LARGE)
                    if self.level_display_vgroup.width > max_level_text_width: 
                        self.level_display_vgroup.scale_to_fit_width(max_level_text_width).to_corner(UR, buff=BUFF_LARGE)
                    self.play(Write(l_vg)); self.wait(0.3)
                
                if not q_bfs : break 

            # --- After BFS for current phase ---
            if self.levels[self.sink_node] == -1: 
                self.update_status_text(f"Sink T={self.sink_node} NOT Reached by BFS. Algorithm Terminates. Final Max Flow: {self.max_flow_value:.1f}", color=RED_C)
                self.wait(3)
                break 
            else: 
                self.update_status_text(f"Sink T={self.sink_node} Reached at Level L{self.levels[self.sink_node]}. Level Graph (LG) Built.", color=GREEN_A)
                self.wait(0.5)
                self.update_status_text("Isolating LG: Highlighting valid forward edges, dimming others.", play_anim=True)
                
                lg_edge_anims_iso = []; non_lg_edge_anims_iso = []
                for (u_lg,v_lg), edge_mo_lg in self.edge_mobjects.items():
                    res_cap_lg = self.capacities[(u_lg,v_lg)]-self.flow.get((u_lg,v_lg),0)
                    is_lg_edge = (self.levels.get(u_lg,-1)!=-1 and self.levels.get(v_lg,-1)!=-1 and \
                                    self.levels[v_lg]==self.levels[u_lg]+1 and \
                                    res_cap_lg > 0 )
                    if is_lg_edge:
                        edge_c = LEVEL_COLORS[self.levels[u_lg]%len(LEVEL_COLORS)] 
                        lg_edge_anims_iso.append(edge_mo_lg.animate.set_stroke(opacity=1.0, width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH).set_color(edge_c))
                    else:
                        non_lg_edge_anims_iso.append(edge_mo_lg.animate.set_stroke(opacity=DIMMED_OPACITY, color=DIMMED_COLOR))
                
                if non_lg_edge_anims_iso + lg_edge_anims_iso: 
                    self.play(AnimationGroup(*(non_lg_edge_anims_iso + lg_edge_anims_iso), lag_ratio=0.05), run_time=0.75)
                self.wait(1)
                self.update_status_text("Level Graph Isolated. Ready for DFS phase.", color=GREEN_A, play_anim=True)
                self.wait(1)

                # --- DFS Phase: Find Blocking Flow in LG ---
                flow_this_phase = self.animate_dfs_path_finding_phase() 
                self.max_flow_value += flow_this_phase

                self.update_phase_text(f"End of Dinitz Phase {self.current_phase_num}. Total Max Flow: {self.max_flow_value:.1f}", color=TEAL_A, play_anim=True)
                self.wait(1.5)

                if flow_this_phase == 0:
                     self.update_status_text(f"No augmenting flow found in this LG. Max Flow: {self.max_flow_value:.1f}. Algorithm terminates.", color=YELLOW_C, play_anim=True)
                     self.wait(3)
                     break 
                else: 
                     self.update_status_text(f"Blocking flow of {flow_this_phase:.1f} found. Current Max Flow: {self.max_flow_value:.1f}.", color=BLUE_A, play_anim=True)
                     self.wait(1.5) 
        
        self.update_section_title("3. Algorithm Complete", play_anim=True)
        
        final_mobjects_to_keep_list_end = [
            self.main_title, 
            self.current_section_title_mobj, 
            self.phase_text_mobj, 
            self.algo_status_mobj,
            self.level_display_vgroup 
        ]
        mobjects_to_fade_out_finally = Group()
        for mobj in self.mobjects:
            is_kept = False
            for kept_group_or_item in final_mobjects_to_keep_list_end:
                if mobj is kept_group_or_item or (isinstance(kept_group_or_item, VGroup) and mobj in kept_group_or_item.submobjects):
                    is_kept = True
                    break
            if not is_kept and mobj is not None:
                 mobjects_to_fade_out_finally.add(mobj)
        
        if mobjects_to_fade_out_finally.submobjects:
            self.play(FadeOut(mobjects_to_fade_out_finally), run_time=1.5)
        
        self.wait(3)
