from manim import *
import collections
import numpy as np
import random

# --- Style and Layout Constants ---
NODE_RADIUS = 0.35
NODE_STROKE_WIDTH = 1.5
EDGE_STROKE_WIDTH = 3.5
ARROW_TIP_LENGTH = 0.16
REVERSE_ARROW_TIP_LENGTH = 0.12 

MAIN_TITLE_FONT_SIZE = 38
SECTION_TITLE_FONT_SIZE = 28
PHASE_TEXT_FONT_SIZE = 22
STATUS_TEXT_FONT_SIZE = 20
NODE_LABEL_FONT_SIZE = 16
EDGE_CAPACITY_LABEL_FONT_SIZE = 12
EDGE_FLOW_PREFIX_FONT_SIZE = 12
LEVEL_TEXT_FONT_SIZE = 18
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

LEVEL_COLORS = [RED_D, ORANGE, YELLOW_D, GREEN_D, BLUE_D, PURPLE_D, PINK]
DEFAULT_NODE_COLOR = BLUE_E
STUDENT_NODE_COLOR = BLUE_D
BOOK_NODE_COLOR = GREEN_D
SOURCE_NODE_COLOR = RED_D
SINK_NODE_COLOR = PURPLE_D
DEFAULT_EDGE_COLOR = GREY_C
LABEL_TEXT_COLOR = DARK_GREY
LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH = 4.5
DFS_EDGE_TRY_WIDTH = LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH * 1.15
DFS_PATH_EDGE_WIDTH = LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH * 1.25
BOTTLENECK_EDGE_INDICATE_COLOR = RED_D
BOTTLENECK_CALCULATION_NUMBER_COLOR = BLUE_B

DIMMED_OPACITY = 0.20
DIMMED_COLOR = GREY_BROWN

REVERSE_EDGE_COLOR = GREY_B
REVERSE_EDGE_OPACITY = 0.25
REVERSE_EDGE_STROKE_WIDTH_FACTOR = 0.6
REVERSE_EDGE_Z_INDEX = 4

EDGE_SHIFT_AMOUNT = 0.12

# Flow pulse animation constants
FLOW_PULSE_COLOR = BLUE_B
FLOW_PULSE_WIDTH_FACTOR = 1.8
FLOW_PULSE_TIME_WIDTH = 0.35
FLOW_PULSE_EDGE_RUNTIME = 0.5
FLOW_PULSE_Z_INDEX_OFFSET = 10
EDGE_UPDATE_RUNTIME = 0.3

# --- Sink Action Text States ---
SINK_ACTION_STATES = {
    "nothing": {"text": "", "color": WHITE},
    "augment": {"text": "augment", "color": GREEN_B},
    "retreat": {"text": "retreat", "color": ORANGE},
    "advance": {"text": "advance", "color": YELLOW_A},
}

class BipartiteMatchingDinitz(Scene):
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
        self.main_title = Text("Bipartite Matching using Dinitz", font_size=MAIN_TITLE_FONT_SIZE)
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

        self.level_display_vgroup = VGroup().set_z_index(10).to_corner(UR, buff=BUFF_XLARGE)
        self.add(self.level_display_vgroup)

        self.sink_action_text_mobj = Text("", font_size=STATUS_TEXT_FONT_SIZE, weight=BOLD, color=YELLOW).set_z_index(RING_Z_INDEX + 50) 

    def _animate_text_update(self, old_mobj, new_mobj, new_text_content_str):
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
        new_text_str = f"Maximum Matching: {self._format_number(self.max_flow_value)}"
        old_mobj = self.max_flow_display_mobj
        
        new_mobj = Text(new_text_str, font_size=MAX_FLOW_DISPLAY_FONT_SIZE, weight=BOLD, color=GREEN_C).set_z_index(10)
        
        if hasattr(self, 'sink_node') and self.sink_node in self.node_mobjects:
            sink_dot = self.node_mobjects[self.sink_node][0]
            new_mobj.next_to(sink_dot, DOWN, buff=BUFF_MED)
        
        # This mobject is NOT part of info_texts_group, handled directly.
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
        if path_info is None or bottleneck_value is None:
            self._update_text_generic("calculation_details_mobj", "", STATUS_TEXT_FONT_SIZE, NORMAL, WHITE, play_anim, is_markup=False)
            return
            
        # For unit-capacity networks, bottleneck is always 1
        path_str = " → ".join([self.get_node_display_name(n) for n in path_info])
        bottleneck_str = f"Bottleneck: {bottleneck_value}"
        full_text = f"{path_str}\n{bottleneck_str}"
        
        self._update_text_generic("calculation_details_mobj", full_text, STATUS_TEXT_FONT_SIZE, NORMAL, WHITE, play_anim, is_markup=False)

    def _update_sink_action_text(self, state: str, animate=True):
        """Updates the sink action text to one of the predefined states."""
        old_mobj = self.sink_action_text_mobj
        state_info = SINK_ACTION_STATES.get(state, SINK_ACTION_STATES["nothing"])
        
        new_mobj = Text(
            state_info["text"],
            font_size=STATUS_TEXT_FONT_SIZE,
            weight=BOLD,
            color=state_info["color"]
        ).set_z_index(old_mobj.z_index)
        
        if hasattr(self, 'sink_node') and self.sink_node in self.node_mobjects:
            sink_dot = self.node_mobjects[self.sink_node][0]
            new_mobj.next_to(sink_dot, UP, buff=BUFF_SMALL)
        
        if old_mobj in self.mobjects:
            self.remove(old_mobj)
            
        self.sink_action_text_mobj = new_mobj
        
        if animate and state_info["text"]:
            self.play(FadeIn(new_mobj, scale=1.2))
        elif state_info["text"]:
            self.add(new_mobj)

    def _dfs_advance_and_retreat(self, u, pushed, current_path_info_list):
        """
        Recursive DFS for finding a path in the level graph.
        u: current node being processed
        pushed: how much flow has been pushed so far (always 1 for unit capacity)
        current_path_info_list: edges in the current path
        
        Returns: flow_pushed, reached_sink
        """
        if u == self.sink_node:
            self._update_sink_action_text("augment", animate=True)
            return pushed, True
            
        # Get the node mobject and mark the search as being at this node now
        u_mobject = self.node_mobjects[u]
        if not hasattr(self, 'search_ring') or self.search_ring is None:
            self.search_ring = Circle(
                radius=u_mobject[0].width / 2 + RING_RADIUS_OFFSET,
                stroke_width=RING_STROKE_WIDTH,
                stroke_color=RING_COLOR,
                z_index=RING_Z_INDEX
            )
            self.search_ring.move_to(u_mobject[0].get_center())
            self.play(Create(self.search_ring))
        else:
            self.play(self.search_ring.animate.move_to(u_mobject[0].get_center()))

        # Update status text to show we're at this node
        self.update_status_text(f"DFS at node {self.get_node_display_name(u)}")
        
        # Try to find a path to the sink through adjacent nodes in the level graph
        for v in self.level_graph_adj_list[u]:
            # Check if there's residual capacity (always 1 for unit capacity network)
            if self.residual_capacities[(u, v)] > 0:
                # Show we're trying this edge
                edge_key = (u, v)
                edge_arrow = self.edge_arrows[edge_key]
                
                # Highlight the edge being tried
                self.play(
                    edge_arrow.animate.set_stroke(width=DFS_EDGE_TRY_WIDTH, color=YELLOW_D),
                    run_time=0.3
                )
                
                # If node v is one level lower than u in the level graph
                if self.level[v] == self.level[u] + 1:
                    self._update_sink_action_text("advance", animate=True)
                    
                    # Update status to show we're advancing to v
                    self.update_status_text(f"Advancing to {self.get_node_display_name(v)}")
                    
                    # Save current edge in path
                    current_path_info_list.append((u, v))
                    
                    # Recursive DFS from v
                    flow_pushed, reached_sink = self._dfs_advance_and_retreat(v, min(pushed, self.residual_capacities[(u, v)]), current_path_info_list)
                    
                    # If we reached the sink, propagate result back
                    if reached_sink:
                        return flow_pushed, True
                    
                    # If not, remove the edge from the path
                    current_path_info_list.pop()
                
                # Reset edge highlighting to level graph style
                self.play(
                    edge_arrow.animate.set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, color=LEVEL_COLORS[self.level[u] % len(LEVEL_COLORS)]),
                    run_time=0.3
                )
        
        # If we're here, we couldn't find a path to the sink
        self._update_sink_action_text("retreat", animate=True)
        self.update_status_text(f"Retreating from {self.get_node_display_name(u)}")
        
        # Mark this node as "deleted" from the level graph for visualization
        self.play(
            u_mobject[0].animate.set_fill(DIMMED_COLOR, opacity=DIMMED_OPACITY),
            u_mobject[1].animate.set_opacity(DIMMED_OPACITY),
            run_time=0.5
        )
        
        return 0, False

    def animate_dfs_path_finding_phase(self):
        """
        Finds a blocking flow in the level graph using DFS.
        Animates the path finding, bottleneck calculation, and flow update.
        """
        self.update_phase_text("Finding Augmenting Paths", color=YELLOW_D)
        
        # Set up for path finding
        current_path_info_list = []
        
        # Start DFS from source node
        flow_pushed, reached_sink = self._dfs_advance_and_retreat(self.source_node, float('inf'), current_path_info_list)
        
        # If we found a path to the sink
        if reached_sink:
            # Convert path edges to nodes for visualization
            path_nodes = [self.source_node]
            for u, v in current_path_info_list:
                path_nodes.append(v)
            
            # Display the found path and bottleneck value
            self.display_calculation_details(path_nodes, flow_pushed)
            
            # Highlight path edges
            path_edge_highlights = []
            for u, v in current_path_info_list:
                edge_key = (u, v)
                edge_arrow = self.edge_arrows[edge_key]
                path_edge_highlights.append(
                    edge_arrow.animate.set_stroke(width=DFS_PATH_EDGE_WIDTH, color=GREEN_D)
                )
            
            self.play(*path_edge_highlights, run_time=0.5)
            
            # Augment flow along the path (always by 1 for unit capacity)
            self.update_phase_text("Augmenting Flow", color=GREEN_D)
            
            # Animation of flow being pushed through the path
            for i, (u, v) in enumerate(current_path_info_list):
                edge_key = (u, v)
                edge_arrow = self.edge_arrows[edge_key]
                
                # Animate flow pulse
                flow_pulse = Line(
                    edge_arrow.get_start(),
                    edge_arrow.get_end(),
                    stroke_width=EDGE_STROKE_WIDTH * FLOW_PULSE_WIDTH_FACTOR,
                    stroke_color=FLOW_PULSE_COLOR,
                    z_index=edge_arrow.z_index + FLOW_PULSE_Z_INDEX_OFFSET
                )
                
                # Create and run the flow pulse animation
                self.play(Create(flow_pulse), run_time=FLOW_PULSE_EDGE_RUNTIME)
                self.remove(flow_pulse)
                
                # Update residual capacities
                self.residual_capacities[(u, v)] -= flow_pushed
                self.residual_capacities[(v, u)] += flow_pushed
                
                # Update flow values for this edge
                self.flow[(u, v)] += flow_pushed
                
                # If it's the last edge, update the max flow value
                if i == len(current_path_info_list) - 1:
                    self.max_flow_value += flow_pushed
                    self.update_max_flow_display()
            
            # Reset edge highlighting
            reset_edge_highlights = []
            for u, v in current_path_info_list:
                edge_key = (u, v)
                edge_arrow = self.edge_arrows[edge_key]
                reset_edge_highlights.append(
                    edge_arrow.animate.set_stroke(width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH, color=LEVEL_COLORS[self.level[u] % len(LEVEL_COLORS)])
                )
            
            self.play(*reset_edge_highlights, run_time=0.5)
            
            # Clean up search ring
            if hasattr(self, 'search_ring') and self.search_ring is not None:
                self.play(FadeOut(self.search_ring))
                self.search_ring = None
            
            return True  # Found an augmenting path
        else:
            # Clean up search ring
            if hasattr(self, 'search_ring') and self.search_ring is not None:
                self.play(FadeOut(self.search_ring))
                self.search_ring = None
            
            return False  # No augmenting path found

    def get_node_display_name(self, node_id):
        """Returns a display name for a node based on its ID and type."""
        if node_id == self.source_node:
            return "Source"
        elif node_id == self.sink_node:
            return "Sink"
        elif node_id in self.student_nodes:
            return f"S{self.student_nodes.index(node_id)}"
        elif node_id in self.book_nodes:
            return f"B{self.book_nodes.index(node_id)}"
        else:
            return str(node_id)

    def construct(self):
        """Main method to set up and animate the bipartite matching using Dinitz algorithm."""
        self.setup_titles_and_placeholders()
        
        # Network parameters
        num_students = 3
        num_books = 4
        
        # Create nodes: students, books, source, and sink
        self.student_nodes = [f"student_{i}" for i in range(num_students)]
        self.book_nodes = [f"book_{i}" for i in range(num_books)]
        self.source_node = "source"
        self.sink_node = "sink"
        all_nodes = [self.source_node] + self.student_nodes + self.book_nodes + [self.sink_node]
        
        # Node positions
        student_positions = [
            LEFT * 3 + UP * 2,
            LEFT * 3,
            LEFT * 3 + DOWN * 2
        ]
        
        book_positions = [
            RIGHT * 3 + UP * 3,
            RIGHT * 3 + UP * 1,
            RIGHT * 3 + DOWN * 1,
            RIGHT * 3 + DOWN * 3
        ]
        
        source_position = LEFT * 6
        sink_position = RIGHT * 6
        
        # Node colors
        node_colors = {
            self.source_node: SOURCE_NODE_COLOR,
            self.sink_node: SINK_NODE_COLOR
        }
        
        for student in self.student_nodes:
            node_colors[student] = STUDENT_NODE_COLOR
            
        for book in self.book_nodes:
            node_colors[book] = BOOK_NODE_COLOR
        
        # Set up node positions dictionary
        self.node_positions = {}
        for i, student in enumerate(self.student_nodes):
            self.node_positions[student] = student_positions[i]
            
        for i, book in enumerate(self.book_nodes):
            self.node_positions[book] = book_positions[i]
            
        self.node_positions[self.source_node] = source_position
        self.node_positions[self.sink_node] = sink_position
        
        # Create edges with unit capacities
        self.original_edges = []
        self.capacities = {}
        
        # Source to students
        for student in self.student_nodes:
            self.original_edges.append((self.source_node, student))
            self.capacities[(self.source_node, student)] = 1
        
        # Students to books (bipartite edges)
        # For this example, we'll create a few specific connections
        student_book_pairs = [
            (0, 0), (0, 1),  # Student 0 can read books 0 and 1
            (1, 1), (1, 2),  # Student 1 can read books 1 and 2
            (2, 2), (2, 3)   # Student 2 can read books 2 and 3
        ]
        
        for s, b in student_book_pairs:
            student = self.student_nodes[s]
            book = self.book_nodes[b]
            self.original_edges.append((student, book))
            self.capacities[(student, book)] = 1
        
        # Books to sink
        for book in self.book_nodes:
            self.original_edges.append((book, self.sink_node))
            self.capacities[(book, self.sink_node)] = 1
        
        # Initialize flow and residual capacities
        self.flow = {edge: 0 for edge in self.original_edges}
        self.residual_capacities = {}
        
        for u, v in self.original_edges:
            self.residual_capacities[(u, v)] = self.capacities[(u, v)]
            self.residual_capacities[(v, u)] = 0
        
        # Create network visualization
        self.node_mobjects = {}
        self.edge_arrows = {}
        self.edge_labels = {}
        
        # Load SVG icons
        student_0_svg = SVGMobject("student_0.svg").scale(0.2)
        student_1_svg = SVGMobject("student_1.svg").scale(0.2)
        book_svg = SVGMobject("book.svg").scale(0.2)
        
        # Create nodes
        for node in all_nodes:
            position = self.node_positions[node]
            color = node_colors[node]
            
            # Create dot
            dot = Dot(
                radius=NODE_RADIUS,
                stroke_width=NODE_STROKE_WIDTH,
                fill_color=color,
                fill_opacity=1,
                z_index=10
            ).move_to(position)
            
            # Create label
            label_text = self.get_node_display_name(node)
            label = Text(
                label_text,
                font_size=NODE_LABEL_FONT_SIZE,
                z_index=11
            ).next_to(dot, DOWN, buff=BUFF_SMALL)
            
            # For students and books, add SVG icons
            icon = None
            if node in self.student_nodes:
                # Alternate between student icons
                if self.student_nodes.index(node) % 2 == 0:
                    icon = student_0_svg.copy()
                else:
                    icon = student_1_svg.copy()
                icon.move_to(dot.get_center())
            elif node in self.book_nodes:
                icon = book_svg.copy()
                icon.move_to(dot.get_center())
            
            # Group dot and label (and icon if present)
            if icon:
                self.node_mobjects[node] = VGroup(dot, label, icon)
            else:
                self.node_mobjects[node] = VGroup(dot, label)
        
        # Create edges
        for u, v in self.original_edges:
            u_mobject = self.node_mobjects[u]
            v_mobject = self.node_mobjects[v]
            
            # Create forward edge
            edge_arrow = self._create_edge_arrow(
                u_mobject,
                v_mobject,
                color=DEFAULT_EDGE_COLOR
            )
            
            self.edge_arrows[(u, v)] = edge_arrow
            
            # Create reverse edge (initially invisible)
            reverse_edge_arrow = self._create_edge_arrow(
                v_mobject,
                u_mobject,
                color=REVERSE_EDGE_COLOR,
                stroke_width=EDGE_STROKE_WIDTH * REVERSE_EDGE_STROKE_WIDTH_FACTOR
            )
            
            reverse_edge_arrow.set_opacity(0)
            self.edge_arrows[(v, u)] = reverse_edge_arrow
        
        # Animation to show the network
        self.update_section_title("Bipartite Matching Network", play_anim=True)
        
        # Add nodes to scene
        node_creation_anims = []
        for node in all_nodes:
            node_creation_anims.append(FadeIn(self.node_mobjects[node]))
        
        self.play(*node_creation_anims, run_time=1.5)
        
        # Add edges to scene
        edge_creation_anims = []
        for u, v in self.original_edges:
            edge_creation_anims.append(Create(self.edge_arrows[(u, v)]))
        
        self.play(*edge_creation_anims, run_time=1.5)
        
        # Initialize max flow value
        self.max_flow_value = 0
        self.update_max_flow_display(play_anim=False)
        
        # Dinitz algorithm main loop
        iteration = 0
        max_iterations = 5  # Safety limit
        
        while iteration < max_iterations:
            iteration += 1
            self.update_section_title(f"Dinitz Algorithm - Iteration {iteration}", play_anim=True)
            
            # Build level graph (BFS from source)
            self.update_phase_text("Building Level Graph (BFS)", color=BLUE_D)
            
            # Initialize levels and level graph adjacency list
            self.level = {node: -1 for node in all_nodes}
            self.level[self.source_node] = 0
            self.level_graph_adj_list = {node: [] for node in all_nodes}
            
            # BFS queue
            queue = collections.deque([self.source_node])
            
            # Create visualization for level rings
            level_rings = {}
            
            while queue:
                u = queue.popleft()
                u_level = self.level[u]
                u_mobject = self.node_mobjects[u]
                
                # Create level ring if not already created
                if u_level not in level_rings:
                    level_color = LEVEL_COLORS[u_level % len(LEVEL_COLORS)]
                    level_ring = Circle(
                        radius=NODE_RADIUS + RING_RADIUS_OFFSET,
                        stroke_width=RING_STROKE_WIDTH,
                        stroke_color=level_color,
                        z_index=RING_Z_INDEX - 1
                    )
                    level_rings[u_level] = level_ring
                
                # Move level ring to current node and show it
                level_ring = level_rings[u_level]
                level_ring.move_to(u_mobject[0].get_center())
                
                if level_ring not in self.mobjects:
                    self.play(Create(level_ring), run_time=0.3)
                else:
                    self.play(level_ring.animate.move_to(u_mobject[0].get_center()), run_time=0.3)
                
                # Explore edges from u with residual capacity
                for v in all_nodes:
                    edge_key = (u, v)
                    if edge_key in self.residual_capacities and self.residual_capacities[edge_key] > 0:
                        # If v is not yet labeled
                        if self.level[v] == -1:
                            self.level[v] = u_level + 1
                            queue.append(v)
                            
                            # Add edge to level graph
                            self.level_graph_adj_list[u].append(v)
                            
                            # Highlight edge in level graph
                            if edge_key in self.edge_arrows:
                                edge_arrow = self.edge_arrows[edge_key]
                                level_color = LEVEL_COLORS[u_level % len(LEVEL_COLORS)]
                                self.play(
                                    edge_arrow.animate.set_stroke(
                                        width=LEVEL_GRAPH_EDGE_HIGHLIGHT_WIDTH,
                                        color=level_color
                                    ),
                                    run_time=0.3
                                )
            
            # Clean up level rings
            for level_ring in level_rings.values():
                self.play(FadeOut(level_ring), run_time=0.3)
            
            # Check if sink is reachable
            if self.level[self.sink_node] == -1:
                self.update_status_text("Sink not reachable, maximum flow reached.")
                break
            
            # Find blocking flow in level graph
            while self.animate_dfs_path_finding_phase():
                # Continue finding paths until no more exist
                pass
        
        # Final max flow display
        self.update_phase_text("Maximum Matching Found", color=GREEN_D)
        self.update_status_text(f"Maximum matching size: {int(self.max_flow_value)}")
        
        # Highlight the matching edges
        matching_edges = []
        for student in self.student_nodes:
            for book in self.book_nodes:
                if (student, book) in self.flow and self.flow[(student, book)] > 0:
                    matching_edges.append((student, book))
        
        # Highlight the matching edges
        matching_edge_highlights = []
        for u, v in matching_edges:
            edge_key = (u, v)
            edge_arrow = self.edge_arrows[edge_key]
            matching_edge_highlights.append(
                edge_arrow.animate.set_stroke(width=DFS_PATH_EDGE_WIDTH, color=GREEN_D)
            )
        
        self.play(*matching_edge_highlights, run_time=1.0)
        
        # Wait at the end
        self.wait(2) 