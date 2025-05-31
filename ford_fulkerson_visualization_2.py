"""
Ford-Fulkerson Method Visualization

This module provides visualizations for different implementations of the Ford-Fulkerson method
for solving maximum flow problems. It demonstrates why Ford-Fulkerson is considered a method
rather than a specific algorithm, by implementing and animating several variants:

1. Basic Ford-Fulkerson with DFS path finding
2. Edmonds-Karp (Ford-Fulkerson with BFS path finding)
3. Capacity Scaling approach

Each implementation follows the same general framework (find augmenting paths, augment flow),
but uses different strategies for path selection, leading to different performance characteristics.

The visualizations are created using Manim (Mathematical Animation Engine).
"""

from manim import *
import collections
import numpy as np

# Utility function to lighten colors for visualization
def lighten_color(color, factor=0.5):
    """
    Lightens the given color by mixing it with white.
    
    Parameters:
    color : str or array-like
        Color to lighten in any format accepted by manim
    factor : float
        Factor to lighten by (0.0 to 1.0, where 0.0 is no change and 1.0 is white)
    
    Returns:
    str : Lightened color in hex format
    """
    if isinstance(color, str):
        # Convert hex or named color to RGB
        rgb = color_to_rgb(color)
    else:
        rgb = color
    
    # Mix with white (1, 1, 1)
    lightened = [c + (1 - c) * factor for c in rgb]
    
    # Convert back to hex
    return rgb_to_hex(lightened)

# --- Style and Layout Constants ---
NODE_RADIUS = 0.28
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.16

MAIN_TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28
PHASE_TEXT_FONT_SIZE = 22
STATUS_TEXT_FONT_SIZE = 20
NODE_LABEL_FONT_SIZE = 16
EDGE_CAPACITY_LABEL_FONT_SIZE = 12
EDGE_FLOW_PREFIX_FONT_SIZE = 12
MAX_FLOW_DISPLAY_FONT_SIZE = 20

BUFF_VERY_SMALL = 0.05
BUFF_SMALL = 0.1
BUFF_MED = 0.25
BUFF_LARGE = 0.4
BUFF_XLARGE = 0.6

RING_COLOR = YELLOW_C
RING_STROKE_WIDTH = 3.5
RING_RADIUS_OFFSET = 0.1
RING_Z_INDEX = 20

DEFAULT_NODE_COLOR = BLUE_E
DEFAULT_EDGE_COLOR = GREY_C
LABEL_TEXT_COLOR = DARK_GREY
PATH_EDGE_HIGHLIGHT_WIDTH = 4.5
PATH_EDGE_COLOR = YELLOW_D
AUGMENT_EDGE_COLOR = GREEN_C
BOTTLENECK_EDGE_COLOR = RED_D

DIMMED_OPACITY = 0.20
DIMMED_COLOR = GREY_BROWN

# Flow pulse animation constants
FLOW_PULSE_COLOR = BLUE_B
FLOW_PULSE_WIDTH_FACTOR = 1.8
FLOW_PULSE_TIME_WIDTH = 0.35
FLOW_PULSE_EDGE_RUNTIME = 0.5
FLOW_PULSE_Z_INDEX_OFFSET = 10
EDGE_UPDATE_RUNTIME = 0.3

class FordFulkersonVisualizer(Scene):
    """Base class for Ford-Fulkerson method visualizations."""
    
    def _format_number(self, value, precision=1):
        """Formats a number as an integer if it's whole, otherwise as a float with given precision."""
        if value == int(value):
            return f"{int(value)}"
        else:
            return f"{value:.{precision}f}"
            
    def _create_edge_arrow(
        self,
        start_node_mob: VGroup,
        end_node_mob: VGroup,
        start_pos_override=None,
        end_pos_override=None,
        tip_length=ARROW_TIP_LENGTH,
        color=DEFAULT_EDGE_COLOR,
        stroke_width=EDGE_STROKE_WIDTH
    ):
        """
        Creates an Arrow mobject between two nodes, ensuring the arrowhead
        stops precisely at the node's border.
        """
        start_dot = start_node_mob[0]
        end_dot = end_node_mob[0]

        start_pos = start_pos_override if start_pos_override is not None else start_dot.get_center()
        end_pos = end_pos_override if end_pos_override is not None else end_dot.get_center()

        if np.linalg.norm(end_pos - start_pos) < 1e-6:
            return VGroup()

        direction = normalize(end_pos - start_pos)
        start_buffer = start_dot.width / 2
        end_buffer = end_dot.width / 2

        line_start_point = start_pos + direction * start_buffer
        line_end_point = end_pos - direction * end_buffer

        return Arrow(
            line_start_point,
            line_end_point,
            buff=0,
            stroke_width=stroke_width,
            color=color,
            tip_length=tip_length,
            z_index=5
        )
    
    def setup_titles_and_placeholders(self):
        """Set up the main title and text placeholders."""
        self.main_title = Text("Visualizing Ford-Fulkerson Method", font_size=MAIN_TITLE_FONT_SIZE)
        self.main_title.to_edge(UP, buff=BUFF_LARGE).set_z_index(10)
        self.add(self.main_title)

        self.current_section_title_mobj = Text("", font_size=SECTION_TITLE_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.phase_text_mobj = Text("", font_size=PHASE_TEXT_FONT_SIZE, weight=BOLD).set_z_index(10)
        self.algo_status_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE).set_z_index(10)
        self.calculation_details_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE).set_z_index(10)
        self.max_flow_display_mobj = Text("", font_size=MAX_FLOW_DISPLAY_FONT_SIZE, weight=BOLD, color=GREEN_C).set_z_index(10)

        self.info_texts_group = VGroup(
            self.current_section_title_mobj,
            self.phase_text_mobj,
            self.algo_status_mobj,
            self.calculation_details_mobj
        ).arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        self.add(self.info_texts_group)
    
    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
        """Animate the update of text mobjects."""
        old_text_had_actual_content = False
        if isinstance(old_mobj, Text) and old_mobj.text != "": old_text_had_actual_content = True
        elif isinstance(old_mobj, Tex) and old_mobj.tex_string != "": old_text_had_actual_content = True
        elif isinstance(old_mobj, MarkupText) and old_mobj.text != "": old_text_had_actual_content = True

        new_text_has_actual_content = bool(new_text_content_str and new_text_content_str != "")

        anims_to_play = []
        if old_text_had_actual_content:
            anims_to_play.append(FadeOut(old_mobj, scale=0.8, run_time=0.25))

        if new_text_has_actual_content:
            anims_to_play.append(FadeIn(new_mobj, scale=1.2, run_time=0.25))

        if anims_to_play:
            self.play(*anims_to_play)
    
    def _update_text_generic(self, text_attr_name, new_text_content, font_size, weight, color, play_anim=True, is_latex=False, is_markup=False):
        """Generic method to update text mobjects."""
        old_mobj = getattr(self, text_attr_name)

        if is_markup:
            new_mobj = MarkupText(new_text_content, font_size=font_size, color=color)
        elif is_latex:
            new_mobj = Tex(new_text_content, color=color)
            ref_text_for_height = Text("Mg", font_size=font_size)
            if ref_text_for_height.height > 0.001 and new_mobj.height > 0.001 and new_mobj.tex_string:
                new_mobj.scale_to_fit_height(ref_text_for_height.height)
        else:
            new_mobj = Text(new_text_content, font_size=font_size, weight=weight, color=color)

        current_idx = -1
        is_in_info_group = hasattr(self, 'info_texts_group') and old_mobj in self.info_texts_group.submobjects

        if is_in_info_group:
            current_idx = self.info_texts_group.submobjects.index(old_mobj)
            new_mobj.move_to(old_mobj.get_center())
            self.info_texts_group.remove(old_mobj)
        elif old_mobj in self.mobjects:
             new_mobj.move_to(old_mobj.get_center())

        if old_mobj in self.mobjects:
            self.remove(old_mobj)

        if current_idx != -1:
            self.info_texts_group.insert(current_idx, new_mobj)
        
        setattr(self, text_attr_name, new_mobj)

        if is_in_info_group:
            self.info_texts_group.arrange(DOWN, center=True, buff=BUFF_MED).next_to(self.main_title, DOWN, buff=BUFF_MED)
        
        new_mobj.set_z_index(old_mobj.z_index if hasattr(old_mobj, 'z_index') and old_mobj.z_index is not None else 10)

        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_content)
        else:
            is_empty_new_content = False
            if isinstance(new_mobj, Text) and not new_mobj.text: is_empty_new_content = True
            elif isinstance(new_mobj, Tex) and not new_mobj.tex_string: is_empty_new_content = True
            elif isinstance(new_mobj, MarkupText) and not new_mobj.text: is_empty_new_content = True

            if not is_empty_new_content:
                if not is_in_info_group and new_mobj not in self.mobjects:
                     self.add(new_mobj)
    
    def update_section_title(self, text_str, play_anim=True):
        self._update_text_generic("current_section_title_mobj", text_str, SECTION_TITLE_FONT_SIZE, BOLD, WHITE, play_anim)

    def update_phase_text(self, text_str, color=WHITE, play_anim=True):
        self._update_text_generic("phase_text_mobj", text_str, PHASE_TEXT_FONT_SIZE, BOLD, color, play_anim)

    def update_status_text(self, text_str, color=WHITE, play_anim=True, is_latex=False):
        self._update_text_generic("algo_status_mobj", text_str, STATUS_TEXT_FONT_SIZE, NORMAL, color, play_anim, is_latex=is_latex, is_markup=False)

    def update_max_flow_display(self, play_anim=True):
        new_text_str = self._format_number(self.max_flow_value)
        old_mobj = self.max_flow_display_mobj
        
        new_mobj = Text(new_text_str, font_size=MAX_FLOW_DISPLAY_FONT_SIZE, weight=BOLD, color=GREEN_C).set_z_index(10)
        
        if hasattr(self, 'sink_node') and self.sink_node in self.node_mobjects:
            sink_dot = self.node_mobjects[self.sink_node][0]
            new_mobj.next_to(sink_dot, DOWN, buff=BUFF_MED)
        
        if old_mobj in self.mobjects:
            self.remove(old_mobj)

        setattr(self, "max_flow_display_mobj", new_mobj)
        
        if play_anim:
            self._animate_text_update(old_mobj, new_mobj, new_text_str)
        else: 
            is_empty_new_content = (isinstance(new_mobj, Text) and new_mobj.text == "")
            if not is_empty_new_content and new_mobj not in self.mobjects:
                self.add(new_mobj)
    
    def display_calculation_details(self, path_info=None, bottleneck_value=None, play_anim=True):
        """Display calculation details for the current augmenting path."""
        if path_info is None or bottleneck_value is None:
            self._update_text_generic("calculation_details_mobj", "", STATUS_TEXT_FONT_SIZE, NORMAL, WHITE, play_anim, is_markup=False)
            return
            
        min_parts = []
        for (u, v), _ in path_info:
            res_cap = self.capacities.get((u, v), 0) - self.flow.get((u, v), 0)
            u_display = "s" if u == self.source_node else "t" if u == self.sink_node else str(u)
            v_display = "s" if v == self.source_node else "t" if v == self.sink_node else str(v)
            
            formatted_res_cap = self._format_number(res_cap)
            min_parts.append(f"<span fgcolor='#8888FF'>{formatted_res_cap}</span> on {u_display}→{v_display}")
        
        formatted_bottleneck_val = self._format_number(bottleneck_value)
        calculation_markup_str = f"Bottleneck = min({', '.join(min_parts)}) = <span fgcolor='#8888FF'>{formatted_bottleneck_val}</span>"
        
        self._update_text_generic("calculation_details_mobj", calculation_markup_str, STATUS_TEXT_FONT_SIZE, NORMAL, YELLOW_B, play_anim, is_markup=True)

    def initialize_network(self, graph_data=None):
        """Initialize the network with either provided graph data or a default graph."""
        # Initialize algorithm variables
        self.max_flow_value = 0
        
        # Define graph structure if not provided
        if graph_data is None:
            self.source_node, self.sink_node = 's', 't'
            self.vertices_data = ['s', 'a', 'b', 'c', 'd', 't']
            self.edges_with_capacity_list = [
                ('s','a',10), ('s','c',10), 
                ('a','b',4), ('a','c',2), ('a','d',8),
                ('b','t',10),
                ('c','d',9),
                ('d','b',6), ('d','t',10)
            ]
        else:
            self.source_node = graph_data.get('source', 's')
            self.sink_node = graph_data.get('sink', 't')
            self.vertices_data = graph_data.get('vertices', [])
            self.edges_with_capacity_list = graph_data.get('edges', [])
        
        # Initialize data structures
        self.capacities = collections.defaultdict(int)  # (u,v) -> capacity
        self.flow = collections.defaultdict(int)        # (u,v) -> flow
        self.adj = collections.defaultdict(list)        # Adjacency list 
        
        # Build the graph
        for u, v, cap in self.edges_with_capacity_list:
            self.capacities[(u, v)] = cap
            if v not in self.adj[u]: self.adj[u].append(v)
            if u not in self.adj[v]: self.adj[v].append(u)  # For residual edges
        
        # Define layout for nodes (if not provided, use automatic layout)
        if hasattr(self, 'graph_layout') and self.graph_layout:
            pass  # Use existing layout
        else:
            # Simple automatic layout - can be improved
            self.graph_layout = self._generate_auto_layout()
    
    def _generate_auto_layout(self):
        """Generate automatic layout for the network."""
        layout = {}
        nodes_by_level = self._organize_nodes_by_level()
        
        max_nodes_in_level = max(len(level) for level in nodes_by_level.values())
        level_spacing = 2.0
        node_spacing = 1.5
        
        for level_idx, nodes in nodes_by_level.items():
            level_x = level_idx * level_spacing - (len(nodes_by_level) - 1) * level_spacing / 2
            
            if len(nodes) == 1:
                # Single node at this level - center it
                node = nodes[0]
                layout[node] = [level_x, 0, 0]
            else:
                # Multiple nodes - distribute vertically
                total_height = (len(nodes) - 1) * node_spacing
                start_y = -total_height / 2
                
                for i, node in enumerate(nodes):
                    node_y = start_y + i * node_spacing
                    layout[node] = [level_x, node_y, 0]
        
        return layout
    
    def _organize_nodes_by_level(self):
        """Organize nodes by their distance from source."""
        # BFS to find distances from source
        distances = {self.source_node: 0}
        queue = [self.source_node]
        visited = {self.source_node}
        
        while queue:
            node = queue.pop(0)
            for neighbor in self.adj[node]:
                if neighbor not in visited and self.capacities.get((node, neighbor), 0) > 0:
                    visited.add(neighbor)
                    distances[neighbor] = distances[node] + 1
                    queue.append(neighbor)
        
        # Group nodes by distance
        nodes_by_level = collections.defaultdict(list)
        for node in self.vertices_data:
            level = distances.get(node, -1)
            if level == -1:  # Node not reachable from source
                # Find the nearest reachable node and place after it
                nearest_reachable = None
                min_distance = float('inf')
                
                for potential_parent in self.vertices_data:
                    if potential_parent in distances and node in self.adj[potential_parent]:
                        if distances[potential_parent] < min_distance:
                            min_distance = distances[potential_parent]
                            nearest_reachable = potential_parent
                
                if nearest_reachable:
                    level = distances[nearest_reachable] + 1
                else:
                    # If still not placeable, put at the end
                    level = max(distances.values()) + 1 if distances else 0
            
            nodes_by_level[level].append(node)
        
        # Ensure sink is at the last level
        if self.sink_node in nodes_by_level[max(nodes_by_level.keys())]:
            pass  # Sink is already at the last level
        else:
            # Remove sink from its current level
            for level, nodes in list(nodes_by_level.items()):
                if self.sink_node in nodes:
                    nodes.remove(self.sink_node)
                    if not nodes:  # Remove empty level
                        del nodes_by_level[level]
            
            # Add sink to a new last level
            max_level = max(nodes_by_level.keys()) if nodes_by_level else 0
            nodes_by_level[max_level + 1].append(self.sink_node)
        
        return nodes_by_level
    
    def setup_network_visualization(self):
        """Create visual elements for the network."""
        # Create and animate node mobjects (dots and labels)
        self.node_mobjects = {}
        nodes_vgroup = VGroup()
        
        for v_id in self.vertices_data:
            dot = Dot(
                point=self.graph_layout[v_id], 
                radius=NODE_RADIUS, 
                color=DEFAULT_NODE_COLOR, 
                z_index=10, 
                stroke_color=BLACK, 
                stroke_width=NODE_STROKE_WIDTH
            )
            
            label_str = v_id  # Use node ID directly as label
            label = Text(
                label_str, 
                font_size=NODE_LABEL_FONT_SIZE, 
                weight=BOLD
            ).move_to(dot.get_center()).set_z_index(11)
            
            self.node_mobjects[v_id] = VGroup(dot, label)
            nodes_vgroup.add(self.node_mobjects[v_id])
        
        self.play(
            LaggedStart(
                *[GrowFromCenter(self.node_mobjects[vid]) for vid in self.vertices_data], 
                lag_ratio=0.05
            ), 
            run_time=1.5
        )
        self.wait(0.5)
        
        # Create and animate edge mobjects (arrows)
        self.edge_mobjects = {}
        self.original_edge_tuples = set((u, v) for u, v, _ in self.edges_with_capacity_list)
        edges_vgroup = VGroup()
        edge_grow_anims = []
        
        for u, v, _ in self.edges_with_capacity_list:
            arrow = self._create_edge_arrow(
                self.node_mobjects[u],
                self.node_mobjects[v],
                tip_length=ARROW_TIP_LENGTH,
                color=DEFAULT_EDGE_COLOR,
                stroke_width=EDGE_STROKE_WIDTH
            )
            self.edge_mobjects[(u, v)] = arrow
            edges_vgroup.add(arrow)
            edge_grow_anims.append(GrowArrow(arrow))
        
        self.play(
            LaggedStart(*edge_grow_anims, lag_ratio=0.05), 
            run_time=1.5
        )
        self.wait(0.5)
        
        # Create and animate edge labels (flow/capacity)
        self.edge_flow_val_text_mobjects = {}
        self.edge_slash_text_mobjects = {}
        self.edge_capacity_text_mobjects = {}
        self.edge_label_groups = {}
        
        all_edge_labels_vgroup = VGroup()
        capacities_to_animate_write = []
        flow_slashes_to_animate_write = []
        
        for u, v, cap in self.edges_with_capacity_list:
            arrow = self.edge_mobjects[(u, v)]
            flow_val_mobj = Text("0", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            slash_mobj = Text("/", font_size=EDGE_FLOW_PREFIX_FONT_SIZE, color=LABEL_TEXT_COLOR)
            cap_text_mobj = Text(str(cap), font_size=EDGE_CAPACITY_LABEL_FONT_SIZE, color=LABEL_TEXT_COLOR)
            
            self.edge_flow_val_text_mobjects[(u, v)] = flow_val_mobj
            self.edge_slash_text_mobjects[(u, v)] = slash_mobj
            self.edge_capacity_text_mobjects[(u, v)] = cap_text_mobj
            
            label_group = VGroup(flow_val_mobj, slash_mobj, cap_text_mobj).arrange(RIGHT, buff=BUFF_VERY_SMALL)
            label_group.move_to(arrow.get_center()).rotate(arrow.get_angle())
            offset_vector = rotate_vector(arrow.get_unit_vector(), PI/2) * 0.15
            label_group.shift(offset_vector).set_z_index(6)
            
            self.edge_label_groups[(u, v)] = label_group
            all_edge_labels_vgroup.add(label_group)
            capacities_to_animate_write.append(cap_text_mobj)
            flow_slashes_to_animate_write.append(VGroup(flow_val_mobj, slash_mobj))
        
        if capacities_to_animate_write:
            self.play(
                LaggedStart(*[Write(c) for c in capacities_to_animate_write], lag_ratio=0.05), 
                run_time=1.2
            )
            self.wait(0.5)
        
        if flow_slashes_to_animate_write:
            self.play(
                LaggedStart(*[Write(fs_group) for fs_group in flow_slashes_to_animate_write], lag_ratio=0.05), 
                run_time=1.2
            )
            self.wait(0.5)
        
        # Group all network elements and scale/position them
        self.network_display_group = VGroup(nodes_vgroup, edges_vgroup, all_edge_labels_vgroup)
        self.desired_large_scale = 1.6
        
        temp_scaled_network_for_height = self.network_display_group.copy().scale(self.desired_large_scale)
        network_target_y = (-config.frame_height / 2) + (temp_scaled_network_for_height.height / 2) + BUFF_XLARGE
        target_position = np.array([0, network_target_y, 0])
        
        self.play(
            self.network_display_group.animate.scale(self.desired_large_scale).move_to(target_position)
        )
        self.wait(0.5)
        
        # Store base visual attributes for edges and nodes
        self.base_edge_visual_attrs = {}
        for edge_key, edge_mo in self.edge_mobjects.items():
            self.base_edge_visual_attrs[edge_key] = {
                "color": edge_mo.get_color(),
                "stroke_width": edge_mo.get_stroke_width(),
                "opacity": edge_mo.get_stroke_opacity()
            }
        
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
        
        # Highlight source and sink nodes briefly
        source_node_dot = self.node_mobjects[self.source_node][0]
        sink_node_dot = self.node_mobjects[self.sink_node][0]
        
        temp_source_ring = Circle(
            radius=source_node_dot.width / 2 + RING_RADIUS_OFFSET, 
            color=RING_COLOR, 
            stroke_width=RING_STROKE_WIDTH
        ).move_to(source_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        
        temp_sink_ring = Circle(
            radius=sink_node_dot.width / 2 + RING_RADIUS_OFFSET, 
            color=RING_COLOR, 
            stroke_width=RING_STROKE_WIDTH
        ).move_to(sink_node_dot.get_center()).set_z_index(RING_Z_INDEX)
        
        self.play(Create(temp_source_ring), Create(temp_sink_ring), run_time=0.4)
        self.play(
            Indicate(temp_source_ring, color=WHITE, scale_factor=1.15, rate_func=there_and_back_with_pause, run_time=0.7),
            Indicate(temp_sink_ring, color=WHITE, scale_factor=1.15, rate_func=there_and_back_with_pause, run_time=0.7)
        )
        self.play(FadeOut(temp_source_ring), FadeOut(temp_sink_ring), run_time=0.4)

class BasicFordFulkersonDFS(FordFulkersonVisualizer):
    """Ford-Fulkerson with DFS path finding."""
    
    def construct(self):
        """Main method for creating the visualization."""
        self.setup_titles_and_placeholders()
        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)
        
        self.update_section_title("1. Building the Flow Network", play_anim=True)
        self.initialize_network()
        self.setup_network_visualization()
        
        self.update_section_title("2. Running Ford-Fulkerson with DFS", play_anim=True)
        self.update_phase_text("Finding Augmenting Paths with DFS", color=BLUE_B, play_anim=True)
        self.wait(1.0)
        
        # Main algorithm loop
        iteration = 0
        while True:
            iteration += 1
            self.update_status_text(f"Iteration {iteration}: Finding augmenting path using DFS", play_anim=True)
            self.wait(1.0)
            
            # Find augmenting path
            path, bottleneck = self._find_augmenting_path_dfs()
            
            if not path:
                self.update_status_text("No more augmenting paths found. Algorithm complete.", color=GREEN_C, play_anim=True)
                self.wait(2.0)
                break
            
            # Visualize the path
            path_info = []
            path_edge_highlights = []
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_mo = self.edge_mobjects.get((u, v))
                if edge_mo:
                    path_info.append(((u, v), edge_mo))
                    path_edge_highlights.append(
                        edge_mo.animate.set_color(PATH_EDGE_COLOR).set_stroke(width=PATH_EDGE_HIGHLIGHT_WIDTH)
                    )
            
            self.play(AnimationGroup(*path_edge_highlights, lag_ratio=0.1), run_time=1.0)
            self.wait(0.5)
            
            # Display bottleneck calculation
            self.display_calculation_details(path_info, bottleneck, play_anim=True)
            self.wait(1.5)
            
            # Augment flow along the path
            self._augment_flow(path, bottleneck)
            self.wait(1.0)
            
            # Update max flow display
            self.update_max_flow_display(play_anim=True)
            self.wait(1.0)
        
        self.update_section_title("3. Ford-Fulkerson Summary", play_anim=True)
        self.update_status_text(f"Final Max Flow: {self.max_flow_value}", color=GREEN_A, play_anim=True)
        self.wait(3.0)
    
    def _find_augmenting_path_dfs(self):
        """Find an augmenting path using DFS."""
        visited = set()
        
        def dfs(node, path, min_capacity):
            if node == self.sink_node:
                return path, min_capacity
            
            visited.add(node)
            
            for neighbor in self.adj[node]:
                residual_capacity = 0
                
                # Check forward edge
                if (node, neighbor) in self.capacities:
                    residual_capacity = self.capacities[(node, neighbor)] - self.flow[(node, neighbor)]
                # Check backward edge (negative flow represents reverse flow)
                elif (neighbor, node) in self.capacities:
                    residual_capacity = self.flow[(neighbor, node)]
                
                if residual_capacity > 0 and neighbor not in visited:
                    result = dfs(neighbor, path + [neighbor], min(min_capacity, residual_capacity))
                    if result[0]:  # If path is found
                        return result
            
            return [], 0  # No path found
        
        path, bottleneck = dfs(self.source_node, [self.source_node], float('inf'))
        
        if path:
            # Visual feedback for traversing the path
            self.update_status_text(f"Augmenting path found: {' → '.join(path)}", color=YELLOW_D, play_anim=True)
            return path, bottleneck
        else:
            return [], 0
    
    def _augment_flow(self, path, bottleneck):
        """Augment flow along the given path."""
        self.update_status_text(f"Augmenting flow by {bottleneck} units", color=GREEN_D, play_anim=True)
        
        path_augmentation_sequence = []
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            animations_for_current_edge_step = []
            
            # Flow pulse animation
            if (u, v) in self.edge_mobjects:
                edge_mo = self.edge_mobjects[(u, v)]
                flash_edge_copy = edge_mo.copy()
                flash_edge_copy.set_color(FLOW_PULSE_COLOR).set_stroke(width=edge_mo.stroke_width * FLOW_PULSE_WIDTH_FACTOR).set_opacity(1.0)
                flash_edge_copy.set_z_index(edge_mo.z_index + FLOW_PULSE_Z_INDEX_OFFSET)
                
                pulse_animation = ShowPassingFlash(
                    flash_edge_copy, time_width=FLOW_PULSE_TIME_WIDTH, run_time=FLOW_PULSE_EDGE_RUNTIME
                )
                animations_for_current_edge_step.append(pulse_animation)
                
                # Update edge appearance
                animations_for_current_edge_step.append(
                    edge_mo.animate.set_color(AUGMENT_EDGE_COLOR).set_stroke(width=PATH_EDGE_HIGHLIGHT_WIDTH)
                )
            
            # Update flow values
            if (u, v) in self.capacities:
                self.flow[(u, v)] += bottleneck
                
                # Update flow text with a direct approach
                if (u, v) in self.edge_flow_val_text_mobjects:
                    old_flow_text = self.edge_flow_val_text_mobjects[(u, v)]
                    new_flow_val = self.flow[(u, v)]
                    new_flow_str = f"{new_flow_val}"
                    
                    # Create a new text object that's exactly the same as the old one but with new text
                    new_flow_text = Text(
                        new_flow_str,
                        font_size=EDGE_FLOW_PREFIX_FONT_SIZE,
                        color=LABEL_TEXT_COLOR
                    )
                    
                    # Match size and position
                    new_flow_text.height = old_flow_text.height
                    new_flow_text.move_to(old_flow_text.get_center())
                    
                    # Preserve rotation of the original text
                    edge_mo = self.edge_mobjects[(u, v)]
                    new_flow_text.rotate(edge_mo.get_angle())
                    
                    # Replace the old text mobject in the scene and in our data structures
                    animations_for_current_edge_step.append(
                        ReplacementTransform(old_flow_text, new_flow_text)
                    )
                    self.edge_flow_val_text_mobjects[(u, v)] = new_flow_text
                    
            elif (v, u) in self.capacities:
                # Reverse edge
                self.flow[(v, u)] -= bottleneck
                
                # Update flow text
                if (v, u) in self.edge_flow_val_text_mobjects:
                    old_flow_text = self.edge_flow_val_text_mobjects[(v, u)]
                    new_flow_val = self.flow[(v, u)]
                    new_flow_str = f"{new_flow_val}"
                    
                    # Create a new text object
                    new_flow_text = Text(
                        new_flow_str,
                        font_size=EDGE_FLOW_PREFIX_FONT_SIZE,
                        color=LABEL_TEXT_COLOR
                    )
                    
                    # Match size and position
                    new_flow_text.height = old_flow_text.height
                    new_flow_text.move_to(old_flow_text.get_center())
                    
                    # Preserve rotation of the original text
                    edge_mo = self.edge_mobjects[(v, u)]
                    new_flow_text.rotate(edge_mo.get_angle())
                    
                    # Replace the old text mobject
                    animations_for_current_edge_step.append(
                        ReplacementTransform(old_flow_text, new_flow_text)
                    )
                    self.edge_flow_val_text_mobjects[(v, u)] = new_flow_text
            
            path_augmentation_sequence.append(Succession(*animations_for_current_edge_step, lag_ratio=1.0))
        
        if path_augmentation_sequence:
            self.play(Succession(*path_augmentation_sequence, lag_ratio=1.0))
        
        # Reset edge appearance
        reset_anims = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if (u, v) in self.edge_mobjects:
                edge_mo = self.edge_mobjects[(u, v)]
                edge_attrs = self.base_edge_visual_attrs.get((u, v), {})
                reset_anims.append(
                    edge_mo.animate.set_color(edge_attrs.get("color", DEFAULT_EDGE_COLOR))
                            .set_stroke(width=edge_attrs.get("stroke_width", EDGE_STROKE_WIDTH))
                )
        
        if reset_anims:
            self.play(AnimationGroup(*reset_anims, lag_ratio=0.05), run_time=0.5)
        
        self.max_flow_value += bottleneck

# Add a custom method to the Text class to update text content
def set_value(self, new_text):
    """Custom method to update Text content while preserving all other properties."""
    original_height = self.height
    original_position = self.get_center()
    original_angle = self.get_angle() if hasattr(self, 'get_angle') else 0
    
    # Create a new text object with the same properties but new content
    updated_text = Text(
        new_text,
        font=self.font,
        font_size=self.font_size,
        color=self.get_color(),
        weight=self.weight if hasattr(self, 'weight') else NORMAL
    )
    
    # Match size and position
    updated_text.height = original_height
    updated_text.move_to(original_position)
    if original_angle != 0:
        updated_text.rotate(original_angle)
    
    # Copy all the important properties from the original text
    self.become(updated_text)
    return self

# Add the method to the Text class
Text.set_value = set_value

class FordFulkersonBFS(FordFulkersonVisualizer):
    """Ford-Fulkerson with BFS path finding (Edmonds-Karp algorithm)."""
    
    def construct(self):
        """Main method for creating the visualization."""
        self.setup_titles_and_placeholders()
        self.main_title = Text("Visualizing Edmonds-Karp Algorithm", font_size=MAIN_TITLE_FONT_SIZE)
        self.main_title.to_edge(UP, buff=BUFF_LARGE).set_z_index(10)
        self.add(self.main_title)
        
        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)
        
        self.update_section_title("1. Building the Flow Network", play_anim=True)
        self.initialize_network()
        self.setup_network_visualization()
        
        self.update_section_title("2. Running Ford-Fulkerson with BFS (Edmonds-Karp)", play_anim=True)
        self.update_phase_text("Finding Shortest Augmenting Paths with BFS", color=BLUE_B, play_anim=True)
        self.wait(1.0)
        
        # Main algorithm loop
        iteration = 0
        while True:
            iteration += 1
            self.update_status_text(f"Iteration {iteration}: Finding shortest augmenting path using BFS", play_anim=True)
            self.wait(1.0)
            
            # Find augmenting path
            path, bottleneck, visited_nodes = self._find_augmenting_path_bfs()
            
            # Visualize BFS exploration
            self._visualize_bfs_exploration(visited_nodes)
            
            if not path:
                self.update_status_text("No more augmenting paths found. Algorithm complete.", color=GREEN_C, play_anim=True)
                self.wait(2.0)
                break
            
            # Visualize the path
            path_info = []
            path_edge_highlights = []
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_mo = self.edge_mobjects.get((u, v))
                if edge_mo:
                    path_info.append(((u, v), edge_mo))
                    path_edge_highlights.append(
                        edge_mo.animate.set_color(PATH_EDGE_COLOR).set_stroke(width=PATH_EDGE_HIGHLIGHT_WIDTH)
                    )
            
            self.play(AnimationGroup(*path_edge_highlights, lag_ratio=0.1), run_time=1.0)
            self.wait(0.5)
            
            # Display bottleneck calculation
            self.display_calculation_details(path_info, bottleneck, play_anim=True)
            self.wait(1.5)
            
            # Augment flow along the path
            self._augment_flow(path, bottleneck)
            self.wait(1.0)
            
            # Update max flow display
            self.update_max_flow_display(play_anim=True)
            self.wait(1.0)
        
        self.update_section_title("3. Edmonds-Karp Summary", play_anim=True)
        self.update_status_text(f"Final Max Flow: {self.max_flow_value}", color=GREEN_A, play_anim=True)
        self.wait(3.0)
    
    def _find_augmenting_path_bfs(self):
        """Find the shortest augmenting path using BFS."""
        queue = [(self.source_node, [self.source_node], float('inf'), set([self.source_node]))]
        visited = {self.source_node}
        all_visited_nodes = []  # For visualization
        
        while queue:
            node, path, min_capacity, current_visited = queue.pop(0)
            all_visited_nodes.append((node, current_visited.copy()))
            
            if node == self.sink_node:
                return path, min_capacity, all_visited_nodes
            
            for neighbor in self.adj[node]:
                residual_capacity = 0
                
                # Check forward edge
                if (node, neighbor) in self.capacities:
                    residual_capacity = self.capacities[(node, neighbor)] - self.flow[(node, neighbor)]
                # Check backward edge
                elif (neighbor, node) in self.capacities:
                    residual_capacity = self.flow[(neighbor, node)]
                
                if residual_capacity > 0 and neighbor not in visited:
                    visited.add(neighbor)
                    new_visited = current_visited.copy()
                    new_visited.add(neighbor)
                    queue.append((
                        neighbor, 
                        path + [neighbor], 
                        min(min_capacity, residual_capacity),
                        new_visited
                    ))
        
        return [], 0, all_visited_nodes
    
    def _visualize_bfs_exploration(self, visited_nodes):
        """Visualize BFS exploration process."""
        if not visited_nodes:
            return
        
        # Create highlight rings for BFS exploration
        highlight_rings = {}
        for v_id in self.vertices_data:
            if v_id == self.source_node:
                continue  # Skip source node
                
            node_dot = self.node_mobjects[v_id][0]
            ring = Circle(
                radius=node_dot.width / 2 + RING_RADIUS_OFFSET * 0.8,
                color=BLUE_C,
                stroke_width=RING_STROKE_WIDTH * 0.8
            ).move_to(node_dot.get_center()).set_z_index(RING_Z_INDEX - 1).set_opacity(0)
            
            highlight_rings[v_id] = ring
            self.add(ring)
        
        # Animate BFS exploration
        for node, visited in visited_nodes:
            if node == self.source_node:
                continue  # Skip source node
                
            anims = []
            
            # Highlight current node
            current_ring = highlight_rings[node]
            anims.append(current_ring.animate.set_opacity(1))
            
            # Flash explored edges
            for v in visited:
                if v != node and (v, node) in self.edge_mobjects:
                    edge_mo = self.edge_mobjects[(v, node)]
                    anims.append(Flash(
                        edge_mo, 
                        color=BLUE_C, 
                        line_stroke_width=2,
                        flash_radius=0.2,
                        line_length=0.1,
                        run_time=0.5
                    ))
            
            if anims:
                self.play(AnimationGroup(*anims, lag_ratio=0.1), run_time=0.5)
                self.wait(0.2)
        
        # Remove highlight rings
        all_rings = list(highlight_rings.values())
        if all_rings:
            self.play(FadeOut(VGroup(*all_rings)), run_time=0.5)
            for ring in all_rings:
                self.remove(ring)
    
    def _augment_flow(self, path, bottleneck):
        """Augment flow along the given path."""
        self.update_status_text(f"Augmenting flow by {bottleneck} units", color=GREEN_D, play_anim=True)
        
        path_augmentation_sequence = []
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            animations_for_current_edge_step = []
            
            # Flow pulse animation
            if (u, v) in self.edge_mobjects:
                edge_mo = self.edge_mobjects[(u, v)]
                flash_edge_copy = edge_mo.copy()
                flash_edge_copy.set_color(FLOW_PULSE_COLOR).set_stroke(width=edge_mo.stroke_width * FLOW_PULSE_WIDTH_FACTOR).set_opacity(1.0)
                flash_edge_copy.set_z_index(edge_mo.z_index + FLOW_PULSE_Z_INDEX_OFFSET)
                
                pulse_animation = ShowPassingFlash(
                    flash_edge_copy, time_width=FLOW_PULSE_TIME_WIDTH, run_time=FLOW_PULSE_EDGE_RUNTIME
                )
                animations_for_current_edge_step.append(pulse_animation)
                
                # Update edge appearance
                animations_for_current_edge_step.append(
                    edge_mo.animate.set_color(AUGMENT_EDGE_COLOR).set_stroke(width=PATH_EDGE_HIGHLIGHT_WIDTH)
                )
            
            # Update flow values
            if (u, v) in self.capacities:
                self.flow[(u, v)] += bottleneck
                
                # Update flow text with a direct approach
                if (u, v) in self.edge_flow_val_text_mobjects:
                    old_flow_text = self.edge_flow_val_text_mobjects[(u, v)]
                    new_flow_val = self.flow[(u, v)]
                    new_flow_str = f"{new_flow_val}"
                    
                    # Create a new text object that's exactly the same as the old one but with new text
                    new_flow_text = Text(
                        new_flow_str,
                        font_size=EDGE_FLOW_PREFIX_FONT_SIZE,
                        color=LABEL_TEXT_COLOR
                    )
                    
                    # Match size and position
                    new_flow_text.height = old_flow_text.height
                    new_flow_text.move_to(old_flow_text.get_center())
                    
                    # Preserve rotation of the original text
                    edge_mo = self.edge_mobjects[(u, v)]
                    new_flow_text.rotate(edge_mo.get_angle())
                    
                    # Replace the old text mobject in the scene and in our data structures
                    animations_for_current_edge_step.append(
                        ReplacementTransform(old_flow_text, new_flow_text)
                    )
                    self.edge_flow_val_text_mobjects[(u, v)] = new_flow_text
                    
            elif (v, u) in self.capacities:
                # Reverse edge
                self.flow[(v, u)] -= bottleneck
                
                # Update flow text
                if (v, u) in self.edge_flow_val_text_mobjects:
                    old_flow_text = self.edge_flow_val_text_mobjects[(v, u)]
                    new_flow_val = self.flow[(v, u)]
                    new_flow_str = f"{new_flow_val}"
                    
                    # Create a new text object
                    new_flow_text = Text(
                        new_flow_str,
                        font_size=EDGE_FLOW_PREFIX_FONT_SIZE,
                        color=LABEL_TEXT_COLOR
                    )
                    
                    # Match size and position
                    new_flow_text.height = old_flow_text.height
                    new_flow_text.move_to(old_flow_text.get_center())
                    
                    # Preserve rotation of the original text
                    edge_mo = self.edge_mobjects[(v, u)]
                    new_flow_text.rotate(edge_mo.get_angle())
                    
                    # Replace the old text mobject
                    animations_for_current_edge_step.append(
                        ReplacementTransform(old_flow_text, new_flow_text)
                    )
                    self.edge_flow_val_text_mobjects[(v, u)] = new_flow_text
            
            path_augmentation_sequence.append(Succession(*animations_for_current_edge_step, lag_ratio=1.0))
        
        if path_augmentation_sequence:
            self.play(Succession(*path_augmentation_sequence, lag_ratio=1.0))
        
        # Reset edge appearance
        reset_anims = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if (u, v) in self.edge_mobjects:
                edge_mo = self.edge_mobjects[(u, v)]
                edge_attrs = self.base_edge_visual_attrs.get((u, v), {})
                reset_anims.append(
                    edge_mo.animate.set_color(edge_attrs.get("color", DEFAULT_EDGE_COLOR))
                            .set_stroke(width=edge_attrs.get("stroke_width", EDGE_STROKE_WIDTH))
                )
        
        if reset_anims:
            self.play(AnimationGroup(*reset_anims, lag_ratio=0.05), run_time=0.5)
        
        self.max_flow_value += bottleneck

class FordFulkersonComparison(Scene):
    """Explains why Ford-Fulkerson is a method and not an algorithm, by comparing different implementations."""
    
    def construct(self):
        # Using 3Blue1Brown style with darker background and more vibrant colors
        self.camera.background_color = "#1C1C1C"  # Darker background like 3b1b
        
        # Create title with animation
        title = Text("Ford-Fulkerson: A Method, Not an Algorithm", font_size=42)
        title.to_edge(UP, buff=0.7)
        
        # Animate title with fancy reveal (letter by letter)
        self.play(AddTextLetterByLetter(title, run_time=1.8))
        self.wait(0.5)
        
        # Animated underline for title (3b1b style)
        underline = Line(
            start=title.get_corner(DL) + LEFT * 0.2,
            end=title.get_corner(DR) + RIGHT * 0.2,
            color=YELLOW_C,
            stroke_width=3
        )
        self.play(Create(underline, run_time=0.8))
        self.wait(0.5)
        
        # Main explanation with stepwise revealing
        explanation_text = [
            "Ford-Fulkerson provides a framework for maximum flow problems",
            "by iteratively finding augmenting paths until none remain.",
            "Different path-finding strategies create distinct algorithms",
            "with varying efficiency characteristics."
        ]
        
        explanation_group = VGroup()
        for i, line in enumerate(explanation_text):
            text = Text(line, font_size=24, color=LIGHT_GRAY)
            explanation_group.add(text)
        
        explanation_group.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        explanation_group.next_to(underline, DOWN, buff=0.5)
        
        # Reveal explanation line by line with 3b1b-style animations
        for i, line in enumerate(explanation_group):
            self.play(
                FadeIn(line, shift=UP*0.3), 
                run_time=0.7
            )
            # Flash key words with different colors
            if i == 0:
                self.play(
                    Circumscribe(line, color=BLUE_B, run_time=0.5),
                    rate_func=smooth
                )
            elif i == 1:
                self.play(
                    Circumscribe(line, color=GREEN_B, run_time=0.5),
                    rate_func=smooth
                )
            self.wait(0.2)
        
        self.wait(0.8)
        
        # Create a subtle pulsing effect around the entire explanation
        surrounding_rect = SurroundingRectangle(
            explanation_group, 
            color=BLUE_D,
            buff=0.2,
            stroke_width=2,
            stroke_opacity=0.5,
            fill_opacity=0.05,
            fill_color=BLUE_E,
            corner_radius=0.2
        )
        self.play(FadeIn(surrounding_rect, scale=1.05))
        
        # Move explanation up to make room for algorithm comparison
        self.play(
            AnimationGroup(
                surrounding_rect.animate.scale(0.85).to_edge(UP, buff=2.0).set_opacity(0.7),
                explanation_group.animate.scale(0.85).to_edge(UP, buff=2.2).set_opacity(0.8),
                lag_ratio=0.05
            ),
            run_time=1.0
        )
        
        # Core concept graphic with reveal animation
        ff_core_concept = VGroup()
        
        # Central box for core concept
        core_box = RoundedRectangle(
            width=7,
            height=1.6,
            corner_radius=0.3,
            fill_color=BLUE_E,
            fill_opacity=0.6,
            stroke_color=BLUE_B,
            stroke_width=2.5
        )
        
        # Core text
        core_text = Text(
            "Find augmenting paths & push flow until no paths exist", 
            font_size=21, 
            color=WHITE
        ).move_to(core_box)
        
        ff_core_concept.add(core_box, core_text)
        ff_core_concept.move_to(ORIGIN).shift(UP * 1.7)
        
        # Animated appear with glow effect
        glow_box = core_box.copy().set_fill(opacity=0).set_stroke(color=BLUE_A, width=8, opacity=0.8)
        
        self.play(
            FadeIn(core_box, scale=1.1, run_time=0.8),
            FadeIn(core_text, shift=DOWN*0.2, run_time=0.8)
        )
        self.play(
            glow_box.animate.set_stroke(opacity=0).scale(1.1),
            rate_func=there_and_back,
            run_time=1.2
        )
        self.wait(0.5)
        
        # Create three algorithm boxes with arrows from core concept
        algorithms = [
            {
                "name": "Basic Ford-Fulkerson (DFS)",
                "description": "Uses depth-first search\nto find augmenting paths",
                "key_points": ["Simple implementation", "O(|E|·f) time complexity", "May be slow for large capacities"],
                "color": RED_D
            },
            {
                "name": "Edmonds-Karp (BFS)",
                "description": "Uses breadth-first search\nfor shortest augmenting paths",
                "key_points": ["Finds shortest paths first", "O(|V|·|E|²) time complexity", "More efficient on most graphs"],
                "color": GREEN_D
            },
            {
                "name": "Capacity Scaling",
                "description": "Prioritizes paths with\nlarge residual capacities",
                "key_points": ["Considers high-capacity edges first", "O(|E|²·log(U)) time complexity", "Efficient for large capacity networks"],
                "color": BLUE_D
            }
        ]
        
        algo_boxes = VGroup()
        algo_titles = VGroup()
        algo_descriptions = VGroup()
        algo_key_points = []
        arrows = VGroup()
        
        # Layout calculations - with more horizontal space
        box_width = 3.5
        box_height = 1.1
        box_spacing = 4.5
        start_x = -(box_spacing) * (len(algorithms) - 1) / 2
        
        # Create algorithm boxes and content
        for i, algo in enumerate(algorithms):
            # Position with better spacing
            x_pos = start_x + i * box_spacing
            y_pos = -0.8  # Move down for better spacing
            
            # Algorithm box
            algo_box = RoundedRectangle(
                width=box_width,
                height=box_height,
                corner_radius=0.2,
                fill_color=algo["color"],
                fill_opacity=0.7,
                stroke_color=lighten_color(algo["color"], 0.3),
                stroke_width=2
            )
            algo_box.move_to([x_pos, y_pos, 0])
            
            # Algorithm name
            algo_name = Text(algo["name"], font_size=20, color=WHITE)
            algo_name.scale_to_fit_width(box_width - 0.4)
            algo_name.move_to(algo_box)
            
            # Description below box
            description = Text(algo["description"], font_size=18, color=LIGHT_GRAY)
            description.scale_to_fit_width(box_width - 0.3)
            description.next_to(algo_box, DOWN, buff=0.4)
            
            # Key points below description - fixed spacing
            key_points_group = VGroup()
            for j, point in enumerate(algo["key_points"]):
                bullet = Text("•", font_size=16, color=lighten_color(algo["color"], 0.3))
                point_text = Text(point, font_size=16, color=LIGHT_GRAY)
                point_group = VGroup(bullet, point_text).arrange(RIGHT, buff=0.1, aligned_edge=UP)
                key_points_group.add(point_group)
            
            key_points_group.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            key_points_group.next_to(description, DOWN, buff=0.4)
            
            # Curved arrow from core concept to algorithm
            start_point = core_box.get_edge_center(DOWN) + DOWN * 0.1
            end_point = algo_box.get_edge_center(UP) + UP * 0.1
            
            if i == 0:  # Left algorithm - curved left
                control_point = np.array([start_point[0] - 1.5, (start_point[1] + end_point[1])/2, 0])
                path = CubicBezier(
                    start_point,
                    start_point + DOWN * 0.5,
                    control_point,
                    end_point
                )
            elif i == 2:  # Right algorithm - curved right
                control_point = np.array([start_point[0] + 1.5, (start_point[1] + end_point[1])/2, 0])
                path = CubicBezier(
                    start_point,
                    start_point + DOWN * 0.5,
                    control_point,
                    end_point
                )
            else:  # Middle algorithm - straight
                path = Line(start_point, end_point)
            
            arrow = Arrow(
                path.point_from_proportion(0.8),  # Place arrow near end
                path.get_end(),
                color=lighten_color(algo["color"], 0.3),
                buff=0.1,
                stroke_width=2.5,
                tip_length=0.2,
                max_stroke_width_to_length_ratio=5
            )
            
            curve = VMobject(stroke_color=lighten_color(algo["color"], 0.1), stroke_width=2)
            curve.set_points(path.get_points()[:path.get_num_points()-5])  # Remove last few points where arrow will be
            
            # Store all elements for animation
            algo_boxes.add(algo_box)
            algo_titles.add(algo_name)
            algo_descriptions.add(description)
            algo_key_points.append(key_points_group)
            arrows.add(VGroup(curve, arrow))
        
        # Animate the curved arrows from core concept to algorithms
        for i, arrow_group in enumerate(arrows):
            curve, arrow = arrow_group
            self.play(
                Create(curve, run_time=0.8),
                run_time=0.8
            )
            self.play(
                GrowArrow(arrow, run_time=0.5)
            )
        
        # Animate the algorithm boxes with staggered appearance
        for i, (box, title) in enumerate(zip(algo_boxes, algo_titles)):
            self.play(
                FadeIn(box, scale=1.1, run_time=0.7),
                run_time=0.7
            )
            self.play(
                FadeIn(title, shift=DOWN*0.2, run_time=0.4),
                run_time=0.4
            )
            
            # Add pulsing glow effect
            glow = box.copy().set_fill(opacity=0).set_stroke(color=lighten_color(algorithms[i]["color"], 0.5), width=6, opacity=0.7)
            self.play(
                glow.animate.set_stroke(opacity=0).scale(1.08),
                rate_func=there_and_back,
                run_time=0.8
            )
        
        # Animate descriptions with subtle wipe effect
        self.play(
            *[FadeIn(desc, shift=UP*0.2) for desc in algo_descriptions],
            run_time=0.8,
            lag_ratio=0.2
        )
        
        # Animate key points for each algorithm with coordinated bullet point appearance
        for i, points in enumerate(algo_key_points):
            self.play(
                LaggedStart(
                    *[FadeIn(point, shift=RIGHT*0.3) for point in points], 
                    lag_ratio=0.3
                ),
                run_time=1.0
            )
        
        self.wait(0.7)
        
        # Conclusion banner at bottom with glowing effect
        conclusion_banner = RoundedRectangle(
            width=12,
            height=0.9,
            corner_radius=0.3,
            fill_color="#2C2C2C",
            fill_opacity=1,
            stroke_color=YELLOW_C,
            stroke_width=2.5
        ).to_edge(DOWN, buff=0.4)
        
        conclusion_text = Text(
            "All variants guarantee optimal max flow, but with different efficiency characteristics",
            font_size=20,
            color=YELLOW_C
        )
        conclusion_text.scale_to_fit_width(conclusion_banner.width - 0.6)
        conclusion_text.move_to(conclusion_banner)
        
        glow_banner = conclusion_banner.copy().set_fill(opacity=0).set_stroke(color=YELLOW_A, width=6, opacity=0.8)
        
        self.play(
            FadeIn(conclusion_banner, scale=1.05, run_time=0.8),
            Write(conclusion_text, run_time=1.2),
            run_time=1.2
        )
        
        self.play(
            glow_banner.animate.set_stroke(opacity=0).scale(1.03),
            rate_func=there_and_back_with_pause,
            run_time=1.5
        )
        
        self.wait(1.5)

class FordFulkersonCapacityScaling(FordFulkersonVisualizer):
    """Ford-Fulkerson with capacity scaling approach."""
    
    def construct(self):
        """Main method for creating the visualization."""
        self.setup_titles_and_placeholders()
        self.main_title = Text("Visualizing Ford-Fulkerson with Capacity Scaling", font_size=MAIN_TITLE_FONT_SIZE - 4)
        self.main_title.to_edge(UP, buff=BUFF_LARGE).set_z_index(10)
        self.add(self.main_title)
        
        self.play(Write(self.main_title), run_time=1)
        self.wait(1.5)
        
        self.update_section_title("1. Building the Flow Network", play_anim=True)
        self.initialize_network()
        self.setup_network_visualization()
        
        self.update_section_title("2. Running Ford-Fulkerson with Capacity Scaling", play_anim=True)
        self.update_phase_text("Finding Large Capacity Paths First", color=BLUE_B, play_anim=True)
        self.wait(1.0)
        
        # Find maximum capacity in the network
        max_capacity = max(cap for _, _, cap in self.edges_with_capacity_list)
        # Determine initial delta - largest power of 2 not exceeding max_capacity
        delta = 1
        while delta * 2 <= max_capacity:
            delta *= 2
        
        # Main algorithm loop
        self.update_status_text(f"Initial delta = {delta} (largest power of 2 ≤ max capacity)", color=YELLOW_D, play_anim=True)
        self.wait(1.5)
        
        while delta >= 1:
            self.update_phase_text(f"Phase: delta = {delta}", color=BLUE_B, play_anim=True)
            self.wait(1.0)
            
            iteration = 0
            while True:
                iteration += 1
                self.update_status_text(f"Iteration {iteration} with delta = {delta}: Finding path", play_anim=True)
                self.wait(1.0)
                
                # Find augmenting path with current delta
                path, bottleneck = self._find_augmenting_path_dfs_with_scaling(delta)
                
                if not path:
                    self.update_status_text(f"No more paths with capacity ≥ {delta}. Reducing delta.", color=YELLOW_D, play_anim=True)
                    self.wait(1.5)
                    break
                
                # Visualize the path
                path_info = []
                path_edge_highlights = []
                
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    edge_mo = self.edge_mobjects.get((u, v))
                    if edge_mo:
                        path_info.append(((u, v), edge_mo))
                        path_edge_highlights.append(
                            edge_mo.animate.set_color(PATH_EDGE_COLOR).set_stroke(width=PATH_EDGE_HIGHLIGHT_WIDTH)
                        )
                
                self.play(AnimationGroup(*path_edge_highlights, lag_ratio=0.1), run_time=1.0)
                self.wait(0.5)
                
                # Display bottleneck calculation
                self.display_calculation_details(path_info, bottleneck, play_anim=True)
                self.wait(1.5)
                
                # Augment flow along the path
                self._augment_flow(path, bottleneck)
                self.wait(1.0)
                
                # Update max flow display
                self.update_max_flow_display(play_anim=True)
                self.wait(1.0)
            
            # Reduce delta for next phase
            delta //= 2
            if delta < 1:
                self.update_status_text("Delta < 1. Algorithm complete.", color=GREEN_C, play_anim=True)
                self.wait(2.0)
                break
        
        self.update_section_title("3. Capacity Scaling Summary", play_anim=True)
        self.update_status_text(f"Final Max Flow: {self.max_flow_value}", color=GREEN_A, play_anim=True)
        self.wait(3.0)
    
    def _find_augmenting_path_dfs_with_scaling(self, delta):
        """Find an augmenting path using DFS with capacity scaling threshold."""
        visited = set()
        
        def dfs(node, path, min_capacity):
            if node == self.sink_node:
                return path, min_capacity
            
            visited.add(node)
            
            for neighbor in self.adj[node]:
                residual_capacity = 0
                
                # Check forward edge
                if (node, neighbor) in self.capacities:
                    residual_capacity = self.capacities[(node, neighbor)] - self.flow[(node, neighbor)]
                # Check backward edge
                elif (neighbor, node) in self.capacities:
                    residual_capacity = self.flow[(neighbor, node)]
                
                # Only consider edges with capacity >= delta
                if residual_capacity >= delta and neighbor not in visited:
                    result = dfs(neighbor, path + [neighbor], min(min_capacity, residual_capacity))
                    if result[0]:  # If path is found
                        return result
            
            return [], 0  # No path found
        
        path, bottleneck = dfs(self.source_node, [self.source_node], float('inf'))
        
        if path:
            # Visual feedback for traversing the path
            self.update_status_text(f"Augmenting path found: {' → '.join(path)}", color=YELLOW_D, play_anim=True)
            return path, bottleneck
        else:
            return [], 0
    
    def _augment_flow(self, path, bottleneck):
        """Augment flow along the given path."""
        self.update_status_text(f"Augmenting flow by {bottleneck} units", color=GREEN_D, play_anim=True)
        
        path_augmentation_sequence = []
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            animations_for_current_edge_step = []
            
            # Flow pulse animation
            if (u, v) in self.edge_mobjects:
                edge_mo = self.edge_mobjects[(u, v)]
                flash_edge_copy = edge_mo.copy()
                flash_edge_copy.set_color(FLOW_PULSE_COLOR).set_stroke(width=edge_mo.stroke_width * FLOW_PULSE_WIDTH_FACTOR).set_opacity(1.0)
                flash_edge_copy.set_z_index(edge_mo.z_index + FLOW_PULSE_Z_INDEX_OFFSET)
                
                pulse_animation = ShowPassingFlash(
                    flash_edge_copy, time_width=FLOW_PULSE_TIME_WIDTH, run_time=FLOW_PULSE_EDGE_RUNTIME
                )
                animations_for_current_edge_step.append(pulse_animation)
                
                # Update edge appearance
                animations_for_current_edge_step.append(
                    edge_mo.animate.set_color(AUGMENT_EDGE_COLOR).set_stroke(width=PATH_EDGE_HIGHLIGHT_WIDTH)
                )
            
            # Update flow values
            if (u, v) in self.capacities:
                self.flow[(u, v)] += bottleneck
                
                # Update flow text with a direct approach
                if (u, v) in self.edge_flow_val_text_mobjects:
                    old_flow_text = self.edge_flow_val_text_mobjects[(u, v)]
                    new_flow_val = self.flow[(u, v)]
                    new_flow_str = f"{new_flow_val}"
                    
                    # Create a new text object that's exactly the same as the old one but with new text
                    new_flow_text = Text(
                        new_flow_str,
                        font_size=EDGE_FLOW_PREFIX_FONT_SIZE,
                        color=LABEL_TEXT_COLOR
                    )
                    
                    # Match size and position
                    new_flow_text.height = old_flow_text.height
                    new_flow_text.move_to(old_flow_text.get_center())
                    
                    # Preserve rotation of the original text
                    edge_mo = self.edge_mobjects[(u, v)]
                    new_flow_text.rotate(edge_mo.get_angle())
                    
                    # Replace the old text mobject in the scene and in our data structures
                    animations_for_current_edge_step.append(
                        ReplacementTransform(old_flow_text, new_flow_text)
                    )
                    self.edge_flow_val_text_mobjects[(u, v)] = new_flow_text
                    
            elif (v, u) in self.capacities:
                # Reverse edge
                self.flow[(v, u)] -= bottleneck
                
                # Update flow text
                if (v, u) in self.edge_flow_val_text_mobjects:
                    old_flow_text = self.edge_flow_val_text_mobjects[(v, u)]
                    new_flow_val = self.flow[(v, u)]
                    new_flow_str = f"{new_flow_val}"
                    
                    # Create a new text object
                    new_flow_text = Text(
                        new_flow_str,
                        font_size=EDGE_FLOW_PREFIX_FONT_SIZE,
                        color=LABEL_TEXT_COLOR
                    )
                    
                    # Match size and position
                    new_flow_text.height = old_flow_text.height
                    new_flow_text.move_to(old_flow_text.get_center())
                    
                    # Preserve rotation of the original text
                    edge_mo = self.edge_mobjects[(v, u)]
                    new_flow_text.rotate(edge_mo.get_angle())
                    
                    # Replace the old text mobject
                    animations_for_current_edge_step.append(
                        ReplacementTransform(old_flow_text, new_flow_text)
                    )
                    self.edge_flow_val_text_mobjects[(v, u)] = new_flow_text
            
            path_augmentation_sequence.append(Succession(*animations_for_current_edge_step, lag_ratio=1.0))
        
        if path_augmentation_sequence:
            self.play(Succession(*path_augmentation_sequence, lag_ratio=1.0))
        
        # Reset edge appearance
        reset_anims = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if (u, v) in self.edge_mobjects:
                edge_mo = self.edge_mobjects[(u, v)]
                edge_attrs = self.base_edge_visual_attrs.get((u, v), {})
                reset_anims.append(
                    edge_mo.animate.set_color(edge_attrs.get("color", DEFAULT_EDGE_COLOR))
                            .set_stroke(width=edge_attrs.get("stroke_width", EDGE_STROKE_WIDTH))
                )
        
        if reset_anims:
            self.play(AnimationGroup(*reset_anims, lag_ratio=0.05), run_time=0.5)
        
        self.max_flow_value += bottleneck 