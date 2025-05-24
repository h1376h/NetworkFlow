from manim import *
from wsn.nodes import NetworkNode, NetworkConnection
from wsn.utils import NetworkAnimator, NetworkGenerator, PathFinder
from wsn.visualization import DataPacket, ClusterBoundary
import random

class WSNVisualization(Scene):
    def __init__(self):
        super().__init__()
        self.communication_range = 2.5
        random.seed(42)  # For reproducibility
        
    def construct(self):
        # Network parameters
        width = config.frame_width - 2  # Leave some margin
        height = config.frame_height - 2
        num_nodes = 10
        min_distance = 1.0

        # Add title and explanation
        title = Text("Wireless Sensor Networks (WSN)", font_size=40)
        title.to_edge(UP)
        explanation = VGroup(
            Text("A network of distributed sensors", font_size=28),
            Text("collecting and transmitting environmental data", font_size=28)
        ).arrange(DOWN, buff=0.3)
        explanation.next_to(title, DOWN, buff=0.5)

        self.play(Write(title))
        self.play(FadeIn(explanation))
        self.wait()
        self.play(
            title.animate.scale(0.6).to_corner(UL),
            FadeOut(explanation)
        )

        # Create sink node at center
        sink_pos = ORIGIN
        sink_node = NetworkNode(sink_pos, 0, is_sink=True)
        node_positions = [sink_pos]
        nodes = [sink_node]

        # Generate sensor nodes
        for i in range(num_nodes):
            pos = NetworkGenerator.find_valid_position(
                width, height, min_distance, node_positions
            )
            node = NetworkNode(pos, len(nodes))
            nodes.append(node)
            node_positions.append(pos)

        # Create connections
        connections = NetworkGenerator.create_connections(
            node_positions, self.communication_range
        )

        # Show sink node with explanation
        sink_explanation = Text(
            "Sink Node: Central collector of all sensor data",
            font_size=24,
            color=RED_A
        ).to_edge(DOWN)

        self.play(
            Create(sink_node),
            Write(sink_explanation),
            Flash(sink_node, color=RED, flash_radius=0.8),
            run_time=1.5
        )
        self.wait()
        self.play(FadeOut(sink_explanation))

        # Show sensor nodes with explanation
        sensor_explanation = Text(
            "Sensor Nodes: Distributed devices monitoring the environment",
            font_size=24,
            color=BLUE_A
        ).to_edge(DOWN)

        self.play(Write(sensor_explanation))
        for node in nodes[1:]:
            self.play(
                Create(node),
                Create(Circle(
                    radius=self.communication_range,
                    stroke_color=BLUE_A,
                    stroke_opacity=0.3,
                    stroke_width=1
                ).move_to(node.get_center())),
                run_time=0.3
            )
        self.play(FadeOut(sensor_explanation))

        # Show network connections
        network_explanation = Text(
            "Nodes within range form a communication network",
            font_size=24
        ).to_edge(DOWN)
        self.play(Write(network_explanation))

        for connection in connections:
            self.play(Create(connection), run_time=0.1)

        # Show data transmission
        self.play(FadeOut(network_explanation))
        data_explanation = Text(
            "Data must reach sink through multi-hop routing",
            font_size=24,
            color=YELLOW_A
        ).to_edge(DOWN)
        self.play(Write(data_explanation))

        # Create adjacency list for path finding
        adj_list = PathFinder.create_adjacency_list(node_positions, connections)

        # Animate multiple data transmissions
        for _ in range(3):
            source_indices = random.sample(range(1, len(nodes)), 2)
            
            for idx in source_indices:
                packet = DataPacket()
                packet.move_to(node_positions[idx])
                self.play(FadeIn(packet))
                
                # Find path to sink
                path = PathFinder.find_path(idx, 0, adj_list, node_positions)
                
                if path:
                    # Convert path indices to positions
                    path_positions = [node_positions[i] for i in path[:-1]]
                    path_positions.append(sink_pos)  # Add sink position as final destination
                    
                    # Create route lines
                    route_lines = VGroup()
                    for i in range(len(path_positions) - 1):
                        route = NetworkConnection(
                            path_positions[i],
                            path_positions[i + 1],
                            is_route=True
                        )
                        route_lines.add(route)
                    
                    # Create route lines one by one
                    for line in route_lines:
                        self.play(Create(line))
                    
                    # Move packet along path
                    for next_pos in path_positions[1:]:
                        self.play(
                            packet.animate.move_to(next_pos),
                            run_time=0.5
                        )
                        if not np.allclose(next_pos, sink_pos):
                            self.play(Flash(
                                Circle(radius=0.3).move_to(next_pos),
                                color=YELLOW_A,
                                flash_radius=0.5
                            ))
                    
                    # Show delivery at sink
                    self.play(
                        Flash(sink_node, color=YELLOW_A, flash_radius=0.5),
                        FadeOut(packet)
                    )
                    
                    # Uncreate route lines one by one from sink to source
                    # and each line fades from end to start
                    for line in route_lines:
                        reversed_line = Line(
                            start=line.get_end(),
                            end=line.get_start(),
                            stroke_color=line.get_stroke_color(),
                            stroke_width=line.get_stroke_width(),
                            stroke_opacity=line.get_stroke_opacity()
                        )
                        self.remove(line)
                        self.add(reversed_line)
                        self.play(Uncreate(reversed_line))

                else:
                    NetworkAnimator.show_transmission_failure(
                        self, node_positions[idx]
                    )

        self.play(FadeOut(data_explanation))

        # Final emphasis
        self.play(
            *[
                Flash(node, color=BLUE_A, flash_radius=0.5)
                for node in random.sample(nodes[1:], 3)
            ],
            Flash(sink_node, color=RED, flash_radius=0.8),
            run_time=1.5
        )
        
        self.wait(1) 