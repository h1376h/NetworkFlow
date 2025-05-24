from manim import *
from wsn.nodes import NetworkNode, NetworkConnection
from wsn.utils import NetworkGenerator, PathFinder
from wsn.visualization import DataPacket, ClusterBoundary
import random
import math

class TDMA(Scene):
    def __init__(self):
        super().__init__()
        self.num_nodes = 3
        self.tdma_slot_duration = 1.0
        self.communication_range = 1.5
        self.node_energy = {i: 100.0 for i in range(self.num_nodes)}
        
        # Define node positions once for reuse
        self.node_positions = [
            np.array([-0.5, 2, 0]),    # Cluster Member 1 (left)
            np.array([0.5, 2, 0]),     # Cluster Member 2 (right)
            np.array([0, 1.2, 0])        # Cluster Head (bottom)
        ]
        
        # Add network generator for better node placement
        self.network_gen = NetworkGenerator()
        
        # Add clock parameters
        self.clock_radius = 0.5
        self.clock_position = np.array([3, 2, 0])  # Top right corner

    def construct(self):
        # Enhanced introduction
        self.show_title()
        
        # Show the problem with better visuals
        self.show_collision_problem()
        
        # Show TDMA solution with energy-aware animations
        self.show_tdma_solution()
        
        # Enhanced conclusion with metrics
        self.show_conclusion()

    def show_title(self):
        # Create more engaging title sequence
        title = Text("Time Division Multiple Access (TDMA)", font_size=40)
        subtitle = Text("A Solution for Channel Access in Wireless Networks", font_size=32)
        
        VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(Write(subtitle))
        self.wait()
        
        self.play(
            title.animate.scale(0.5).to_corner(UL),
            FadeOut(subtitle),
        )

    def create_energy_wave(self, source_point: np.ndarray, max_radius: float = None, 
                          color: str = BLUE) -> AnimationGroup:
        """Create expanding wave animation for transmissions"""
        if max_radius is None:
            max_radius = self.communication_range
        
        num_waves = 2
        waves = VGroup(*[
            Circle(radius=0.1, stroke_width=3-i, stroke_color=color)
            .move_to(source_point)
            .set_opacity(0.8)
            for i in range(num_waves)
        ])
        
        animations = []
        for i, wave in enumerate(waves):
            animations.append(
                Succession(
                    Wait(i * 0.1),  # Shorter delay between waves
                    AnimationGroup(
                        ApplyMethod(
                            wave.scale, max_radius/0.1,
                            rate_func=smooth,
                            run_time=0.5  # Faster expansion
                        ),
                        ApplyMethod(
                            wave.set_opacity, 0,
                            rate_func=linear,
                            run_time=0.5
                        )
                    )
                )
            )
        return AnimationGroup(*animations, lag_ratio=0.1)

    def show_collision_problem(self):
        # Use the shared node positions
        nodes = VGroup(
            NetworkNode(self.node_positions[0], 0, is_cluster_head=False),  # CM1
            NetworkNode(self.node_positions[1], 1, is_cluster_head=False),  # CM2
            NetworkNode(self.node_positions[2], 2, is_cluster_head=True)    # CH
        )
        
        problem = Text(
            "What happens when cluster members transmit simultaneously?",
            font_size=32
        ).to_edge(DOWN)
        
        # Use consistent communication range
        ranges = VGroup(*[
            Circle(
                radius=self.communication_range,
                stroke_color=BLUE_A,
                stroke_opacity=0.4,
                stroke_width=1.5
            ).move_to(node.get_center())
            for node in nodes
        ])
        
        self.play(
            Create(nodes),
            Create(ranges),
            Write(problem)
        )

        # Create and fade in packets one by one
        packet1 = DataPacket().move_to(nodes[0].get_center())
        packet2 = DataPacket().move_to(nodes[1].get_center())
        packets = VGroup(packet1, packet2)
        
        self.play(
            FadeIn(packet1),
            FadeIn(packet2)
        )

        # Simultaneous transmission to receiver
        receiver_point = nodes[2].get_center()
        
        # Animate packets moving to receiver and waves expanding
        self.play(
            *[self.create_energy_wave(nodes[i].get_center(), max_radius=0.8, color=RED_A) for i in range(2)],
            packet1.animate.move_to(receiver_point),
            packet2.animate.move_to(receiver_point),
            rate_func=linear,
            run_time=0.5
        )

        # Enhanced collision effect
        explosion = VGroup(
            Circle(color=RED).scale(0.5),
            Text("💥", font_size=40)
        ).move_to(receiver_point)

        consequences = VGroup(
            Text("• Lost information", font_size=24),
            Text("• Wasted energy", font_size=24),
            Text("• Network congestion", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT).next_to(explosion, DOWN, buff=0.5)

        self.play(
            Create(explosion),
            Flash(
                receiver_point,
                color=RED,
                flash_radius=1,
                num_lines=12
            ),
            *[FadeOut(packet) for packet in packets]
        )

        self.play(Write(consequences))
        self.wait()

        # Clean up for next scene
        self.play(*[FadeOut(mob) for mob in [
            problem, ranges, explosion, 
            consequences, nodes
        ]])

    def create_clock(self):
        """Create a clock visualization with two colored halves"""
        # Create two filled semicircles
        semicircle1 = Sector(
            radius=self.clock_radius,
            start_angle=-PI/2,
            angle=PI,
            color=GREEN,
            stroke_width=2,
            fill_opacity=0.5
        ).move_to(self.clock_position + np.array([self.clock_radius/2, 0, 0]))  # Move right
        
        semicircle2 = Sector(
            radius=self.clock_radius,
            start_angle=PI/2,
            angle=PI,
            color=BLUE,
            stroke_width=2,
            fill_opacity=0.5
        ).move_to(self.clock_position + np.array([-self.clock_radius/2, 0, 0]))  # Move left
        
        # Add hour marks
        hour_marks = VGroup()
        for i in range(12):
            angle = i * TAU / 12
            mark_start = self.clock_radius * 0.9
            mark_end = self.clock_radius
            start_point = np.array([
                mark_start * math.cos(angle),
                mark_start * math.sin(angle),
                0
            ])
            end_point = np.array([
                mark_end * math.cos(angle),
                mark_end * math.sin(angle),
                0
            ])
            mark = Line(start_point, end_point, color=WHITE)
            mark.shift(self.clock_position)
            hour_marks.add(mark)
        
        # Add clock hand
        hand = Line(
            self.clock_position,
            self.clock_position + np.array([0, self.clock_radius * 0.8, 0]),
            color=RED,
            stroke_width=3
        )
        
        return VGroup(semicircle1, semicircle2, hour_marks, hand)

    def create_data_packet_content(self):
        """Create fake data content for visualization"""
        # Define sensor data types with values and units
        data_types = {
            "Temp": (23, "°C"),
            "Humid": (45, "%"),
            "CO2": (410, "ppm"),
            "Light": (800, "lux")
        }
        
        # Select random data type and format string
        data_type = random.choice(list(data_types.keys()))
        value, unit = data_types[data_type]
        data_string = f"{data_type}: {value}{unit}"
        
        # Create the packet at the bottom
        packet = DataPacket().scale(1)
        
        # Create the data content box
        data_box = VGroup(
            Rectangle(
                width=1.2,
                height=0.6,
                stroke_color=WHITE,
                fill_color=DARK_GREY,
                fill_opacity=0.8
            ),
            Text(data_string, font_size=16, color=WHITE)
        )
        data_box[1].move_to(data_box[0].get_center())
        
        # Position the packet below the data box
        data_box.next_to(packet, UP, buff=0.2)
        
        # Add connecting line between packet and box
        line = Line(
            packet.get_top(),
            data_box[0].get_bottom(),
            stroke_width=1,
            color=WHITE
        )
        
        # Make the data box and line follow the packet's position
        data_box.add_updater(lambda m: m.next_to(packet, UP, buff=0.2))
        line.add_updater(lambda l: l.put_start_and_end_on(packet.get_top(), data_box[0].get_bottom()))
        
        return VGroup(packet, line, data_box)

    def show_tdma_solution(self):
        # Create nodes and ranges as before
        nodes = VGroup(
            NetworkNode(self.node_positions[0], 0, is_cluster_head=False),  # CM1
            NetworkNode(self.node_positions[1], 1, is_cluster_head=False),  # CM2
            NetworkNode(self.node_positions[2], 2, is_cluster_head=True)    # CH
        )
        
        ranges = VGroup(*[
            Circle(
                radius=self.communication_range,
                stroke_color=BLUE,
                stroke_opacity=0.3,
                stroke_width=1
            ).move_to(node.get_center())
            for node in nodes
        ])
        
        self.play(
            Create(nodes),
            Create(ranges)
        )

        # Create timeline
        timeline = NumberLine(
            x_range=[0, 4, 1],
            length=8,
            include_numbers=True,
            include_tip=True,
            color=GRAY
        ).shift(DOWN * 2)
        
        time_label = Text("Time", font_size=24).next_to(timeline, RIGHT)
        
        self.play(
            Create(timeline),
            Write(time_label)
        )

        # Create slots and cycles but don't show them yet
        slot_height = 0.5
        colors = [BLUE, GREEN]
        slots = VGroup(*[
            Rectangle(
                width=timeline.get_unit_size(),
                height=slot_height,
                stroke_color=WHITE,
                fill_color=color,
                fill_opacity=0.3
            ).next_to(timeline.number_to_point(i + 0.5), UP, buff=0.2)
            for i, color in enumerate(colors * 2)
        ])

        slot_labels = VGroup(*[
            Text(f"CM{(i % 2) + 1} Slot", font_size=16)
            .move_to(slots[i])
            for i in range(len(slots))
        ])

        cycle_width = timeline.get_unit_size() * 2
        cycle_height = slot_height + 0.2
        cycle_rectangles = VGroup(*[
            Rectangle(
                width=cycle_width,
                height=cycle_height,
                stroke_color=WHITE,
                stroke_width=2,
                fill_opacity=0
            ).move_to(VGroup(slots[i*2], slots[i*2 + 1]).get_center())
            for i in range(2)
        ])

        cycle_labels = VGroup(*[
            Text(f"Cycle {i+1}", font_size=16)
            .next_to(cycle_rectangles[i], UP, buff=0.1)
            for i in range(2)
        ])

        # Add clock visualization
        clock = self.create_clock()
        hand = clock[-1]
        self.play(Create(clock))

        # Improve transmission animations
        for cycle in range(2):
            cycle_slots = []  # Store completed slots for this cycle
            
            for i in range(2):  # Loop through CM nodes
                active_node = nodes[i]
                current_slot = slots[cycle * 2 + i]
                current_slot_label = slot_labels[cycle * 2 + i]
                receiver_node = nodes[2]
                
                # Show the current slot appearing
                self.play(
                    FadeIn(current_slot),
                    FadeIn(current_slot_label),
                    run_time=0.5
                )
                
                # Simulate dynamic slot duration
                slot_duration = random.uniform(0.8, 1.2)
                
                # Check for transmission failure
                transmission_success = random.random() > 0.1  # 10% chance of failure
                
                # Create data packet with content
                packet_content = self.create_data_packet_content()
                packet_content[0].move_to(active_node.get_center())
                
                # Highlight active node
                self.play(
                    active_node.animate.set_color(YELLOW).scale(1.2),
                    Rotate(hand, angle=TAU/6, about_point=self.clock_position, rate_func=linear),
                    run_time=slot_duration * 0.4
                )
                
                # Show data being prepared
                self.play(
                    FadeIn(packet_content[0]),  # First show dot
                    Rotate(hand, angle=TAU/12, about_point=self.clock_position, rate_func=linear),
                    run_time=slot_duration * 0.3
                )
                
                self.play(
                    FadeIn(packet_content[1]),  # Then show connecting line
                    FadeIn(packet_content[2]),  # Then show data box
                    Rotate(hand, angle=TAU/12, about_point=self.clock_position, rate_func=linear),
                    run_time=slot_duration * 0.3
                )
                
                if transmission_success:
                    # Animate data transmission with wave effect
                    self.play(
                        self.create_energy_wave(
                            active_node.get_center(),
                            color=colors[i],
                            max_radius=2.5
                        ),
                        packet_content[0].animate.move_to(receiver_node.get_center()),
                        Rotate(hand, angle=TAU/6, about_point=self.clock_position, rate_func=linear),
                        run_time=slot_duration * 1.2
                    )
                    
                    # Add success indicator
                    success_mark = Text("✓", font_size=28, color=GREEN).next_to(receiver_node, UP)
                    self.play(
                        FadeIn(success_mark),
                        Flash(receiver_node.get_center(), color=GREEN, flash_radius=0.5),
                        run_time=0.3
                    )
                else:
                    # Indicate transmission failure
                    failure_mark = Text("✗", font_size=28, color=RED).next_to(receiver_node, UP)
                    self.play(
                        FadeIn(failure_mark),
                        Flash(receiver_node.get_center(), color=RED, flash_radius=0.5),
                        run_time=0.3
                    )
                
                # Clean up
                self.play(
                    FadeOut(packet_content[0]),
                    FadeOut(packet_content[1]),
                    FadeOut(packet_content[2]),
                    FadeOut(success_mark) if transmission_success else FadeOut(failure_mark),
                    active_node.animate.scale(1/1.2).set_color(BLUE),
                    run_time=slot_duration * 0.4
                )
                
                cycle_slots.append(current_slot)
                cycle_slots.append(current_slot_label)
                
                # If this was the second slot in the cycle, show the cycle rectangle
                if i == 1:
                    current_cycle_rect = cycle_rectangles[cycle]
                    current_cycle_label = cycle_labels[cycle]
                    
                    self.play(
                        Create(current_cycle_rect),
                        Write(current_cycle_label),
                        run_time=0.5
                    )
                
                self.wait(0.2)

        # Final explanation
        explanation = Text(
            "Each node transmits in its assigned time slot over two cycles",
            font_size=24,
            color=YELLOW
        ).next_to(timeline, DOWN, buff=0.3)
        
        self.play(Write(explanation))
        self.wait()
        self.play(FadeOut(explanation))

    def show_conclusion(self):
        # First clear previous elements
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        
        # Create and position conclusion text
        conclusion = VGroup(
            Text("TDMA Benefits:", color=YELLOW, font_size=36),
            Text("• No collisions", font_size=28),
            Text("• Fair access", font_size=28),
            Text("• Predictable timing", font_size=28)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        
        # Center the conclusion group on screen
        conclusion.move_to(ORIGIN)
        
        self.play(Write(conclusion))
        self.wait(2)
        
        # Final fadeout
        self.play(FadeOut(conclusion)) 