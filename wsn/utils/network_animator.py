from manim import *
from ..visualization.data_packet import DataPacket
from typing import List

class NetworkAnimator:
    """Handles common network animation sequences"""
    @staticmethod
    def animate_packet_transmission(scene: Scene, packet: DataPacket, path: List[np.ndarray], 
                                  flash_color: str = YELLOW_A, 
                                  move_time: float = 0.5,
                                  flash_radius: float = 0.5):
        """Animate packet transmission along a path"""
        for next_pos in path[1:]:
            scene.play(
                packet.animate.move_to(next_pos),
                run_time=move_time
            )
            scene.play(Flash(
                Circle(radius=0.3).move_to(next_pos),
                color=flash_color,
                flash_radius=flash_radius
            ))

    @staticmethod
    def show_transmission_failure(scene: Scene, node_pos: np.ndarray, 
                                error_msg: str = "No route to sink!",
                                animation_time: float = 1,
                                pause_time: float = 0.5,
                                flash_radius: float = 0.5):
        """Show transmission failure animation"""
        error_cross = Cross(stroke_color=RED).scale(0.5)
        error_cross.move_to(node_pos)
        
        error_text = Text(error_msg, font_size=20, color=RED)
        error_text.next_to(error_cross, DOWN, buff=0.2)
        error_group = VGroup(error_cross, error_text)
        
        scene.play(
            Create(error_cross),
            Write(error_text),
            Flash(Circle().move_to(node_pos), color=RED, flash_radius=flash_radius),
            run_time=animation_time
        )
        scene.wait(pause_time)
        scene.play(FadeOut(error_group)) 