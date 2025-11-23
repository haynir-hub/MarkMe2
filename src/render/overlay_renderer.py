"""
Overlay Renderer - Renders visual markers on video frames
"""
import cv2
import numpy as np
from typing import Tuple, Optional
import math
from .modern_styles import ModernStyles


class OverlayRenderer:
    """Renders visual markers (arrows, circles, rectangles) on frames"""
    
    def __init__(self):
        self.arrow_size = 30
        self.circle_thickness = 3
        self.circle_glow_size = 5
        self.rectangle_thickness = 3
        
        # Position smoothing for markers (especially circles)
        self.position_buffers = {}  # player_id -> [(center_x, center_y), ...]
        
        # Modern styles instance
        self.modern_styles = ModernStyles()
        
        # Frame counter for animations
        self.frame_count = 0
        self.position_buffer_size = 5
    
    def draw_marker(self, frame: np.ndarray, bbox: Tuple[int, int, int, int],
                   marker_style: str, color: Tuple[int, int, int]) -> np.ndarray:
        """
        Draw marker on frame based on style
        
        Args:
            frame: Frame to draw on (BGR format)
            bbox: Bounding box (x, y, width, height)
            marker_style: Style ('arrow', 'circle', 'rectangle', 'spotlight', 'outline', 
                          'neon_ring', 'pulse', 'gradient', 'dynamic_arrow', 'hexagon', 'crosshair')
            color: BGR color tuple
            
        Returns:
            Frame with marker drawn
        """
        if bbox is None:
            return frame
        
        # Increment frame counter for animations
        self.frame_count += 1
        
        x, y, w, h = bbox
        
        # Classic styles
        if marker_style == 'arrow':
            return self._draw_arrow(frame, bbox, color)
        elif marker_style == 'circle':
            return self._draw_circle(frame, bbox, color)
        elif marker_style == 'rectangle':
            return self._draw_rectangle(frame, bbox, color)
        elif marker_style == 'spotlight':
            return self._draw_spotlight(frame, bbox, color)
        elif marker_style == 'outline':
            return self._draw_outline(frame, bbox, color)
        
        # Modern styles
        elif marker_style == 'neon_ring':
            return self.modern_styles.draw_neon_ring(frame, bbox, color)
        elif marker_style == 'pulse':
            # Force orange color for pulse (BGR: 0, 165, 255)
            orange_color = (0, 165, 255)
            return self.modern_styles.draw_pulse_circle(frame, bbox, orange_color, self.frame_count)
        elif marker_style == 'gradient':
            # Gradient colors (purple variants)
            color1 = (255, 0, 200)  # Purple
            color2 = (200, 0, 255)  # Purple variant
            return self.modern_styles.draw_gradient_ring(frame, bbox, color1, color2, self.frame_count)
        elif marker_style == 'dynamic_arrow':
            return self.modern_styles.draw_dynamic_arrow(frame, bbox, color, self.frame_count)
        elif marker_style == 'hexagon':
            return self.modern_styles.draw_hexagon_outline(frame, bbox, color)
        elif marker_style == 'crosshair':
            return self.modern_styles.draw_crosshair(frame, bbox, color)
        elif marker_style == 'spotlight_modern':
            return self.modern_styles.draw_spotlight(frame, bbox, color)
        elif marker_style == 'flame':
            return self.modern_styles.draw_flame(frame, bbox, color, self.frame_count)
        else:
            return frame
    
    def _draw_arrow(self, frame: np.ndarray, bbox: Tuple[int, int, int, int],
                   color: Tuple[int, int, int]) -> np.ndarray:
        """
        Draw beautiful arrow above player's head with glow effect
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Arrow color (yellow)
            
        Returns:
            Frame with arrow
        """
        x, y, w, h = bbox
        
        # Calculate arrow position (above head)
        center_x = x + w // 2
        # Position arrow higher above head
        arrow_y = max(0, y - 50)  # Higher above head
        arrow_x = center_x
        
        # Make arrow size proportional to player size
        arrow_size = max(int(w * 0.35), 35)  # Proportional to body width, larger
        
        # Create arrow shape - more elegant with sharper point
        tip_y = arrow_y
        base_y = arrow_y + arrow_size
        base_width = arrow_size
        
        # Draw glow effect (multiple layers)
        for i in range(4, 0, -1):
            overlay = frame.copy()
            glow_size = arrow_size + i * 3
            glow_base_width = base_width + i * 2
            glow_tip_y = tip_y - i
            glow_base_y = base_y + i
            
            glow_points = np.array([
                [arrow_x, glow_tip_y],
                [arrow_x - glow_base_width // 2, glow_base_y],
                [arrow_x + glow_base_width // 2, glow_base_y]
            ], np.int32)
            
            cv2.fillPoly(overlay, [glow_points], color)
            cv2.addWeighted(overlay, 0.15 - (i * 0.03), frame, 1.0 - (0.15 - (i * 0.03)), 0, frame)
        
        # Draw main arrow with better shape
        arrow_points = np.array([
            [arrow_x, tip_y],
            [arrow_x - base_width // 2, base_y],
            [arrow_x - base_width // 3, base_y - arrow_size // 4],  # Inner point for sharper look
            [arrow_x, base_y - arrow_size // 3],
            [arrow_x + base_width // 3, base_y - arrow_size // 4],  # Inner point
            [arrow_x + base_width // 2, base_y]
        ], np.int32)
        
        # Fill arrow
        cv2.fillPoly(frame, [arrow_points], color)
        
        # Draw outline for definition
        cv2.polylines(frame, [arrow_points], True, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Add highlight on top
        highlight_color = tuple(min(c + 50, 255) for c in color)
        highlight_points = np.array([
            [arrow_x, tip_y],
            [arrow_x - base_width // 4, base_y - arrow_size // 2],
            [arrow_x, base_y - arrow_size // 2.5],
            [arrow_x + base_width // 4, base_y - arrow_size // 2]
        ], np.int32)
        cv2.fillPoly(frame, [highlight_points], highlight_color)
        
        return frame
    
    def _draw_circle(self, frame: np.ndarray, bbox: Tuple[int, int, int, int],
                    color: Tuple[int, int, int]) -> np.ndarray:
        """
        Draw 3D floor hoop around player's feet (like professional sports broadcasts)
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Circle color
            
        Returns:
            Frame with 3D floor hoop
        """
        x, y, w, h = bbox
        
        # Calculate ellipse center (feet position - on the floor)
        # X axis: Use precise center
        center_x = x + w // 2
        
        # Calculate ellipse size - LARGE ENOUGH to keep player inside during movement
        # Use larger radius to accommodate running/movement
        radius_x = max(int(w * 0.8), 45)  # Large horizontal radius - around feet with margin
        radius_y = max(int(w * 0.15), 10)  # Smaller vertical radius - flat on floor
        
        # Y axis: Place ring CENTERED at ANKLE level (above feet, at ankle)
        # Bottom of ellipse should be at feet level (y + h)
        # So: center_y + radius_y = y + h
        # Therefore: center_y = y + h - radius_y
        center_y = y + h - radius_y  # Center at ankle level, bottom touches feet
        
        # Debug: Log circle position
        if np.random.random() < 0.1:  # Log 10% of frames to avoid spam
            print(f"🎯 Circle: bbox=({x}, {y}, {w}, {h}) → center=({center_x}, {center_y}), radius=({radius_x}, {radius_y})")
        
        # Ensure within frame bounds
        frame_h, frame_w = frame.shape[:2]
        if center_x < 0 or center_x >= frame_w or center_y < 0 or center_y >= frame_h:
            return frame
        
        # Draw full circle (360 degrees) - MORE TRANSPARENT so it doesn't hide video
        # Draw glow effect (multiple ellipses with decreasing opacity) - REDUCED opacity
        for i in range(self.circle_glow_size):
            alpha = 0.12 - (i * 0.02)  # Much more transparent (was 0.25)
            glow_rx = radius_x + i * 3  # Smaller glow (was i * 4)
            glow_ry = radius_y + i * 1  # Smaller glow (was i * 2)
            overlay = frame.copy()
            cv2.ellipse(overlay, (center_x, center_y), (glow_rx, glow_ry), 0, 0, 360, color, 2)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Draw main ellipse (full circle - 360 degrees) - THINNER and MORE TRANSPARENT
        overlay = frame.copy()
        cv2.ellipse(overlay, (center_x, center_y), (radius_x, radius_y), 0, 0, 360, color, max(1, self.circle_thickness - 1))
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)  # 60% opacity - more transparent
        
        # Add inner highlight for depth - MORE TRANSPARENT
        inner_rx = int(radius_x * 0.85)
        inner_ry = int(radius_y * 0.85)
        lighter_color = tuple(min(c + 60, 255) for c in color)
        overlay = frame.copy()
        cv2.ellipse(overlay, (center_x, center_y), (inner_rx, inner_ry), 0, 0, 360, lighter_color, 1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)  # 40% opacity - very transparent
        
        return frame
    
    def _draw_rectangle(self, frame: np.ndarray, bbox: Tuple[int, int, int, int],
                       color: Tuple[int, int, int]) -> np.ndarray:
        """
        Draw clean blue border rectangle around player (no fill)
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Rectangle color (will be overridden to blue)
            
        Returns:
            Frame with rectangle
        """
        x, y, w, h = bbox
        
        # Force blue color for rectangle (BGR format)
        blue_color = (255, 100, 0)  # Bright blue
        
        # Draw outer glow for depth
        padding = 2
        overlay = frame.copy()
        cv2.rectangle(overlay, 
                     (x - padding, y - padding), 
                     (x + w + padding, y + h + padding), 
                     blue_color, 
                     self.rectangle_thickness + 1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Draw main border (clean, no fill)
        cv2.rectangle(frame, (x, y), (x + w, y + h), blue_color, self.rectangle_thickness)
        
        # Add corner highlights for professional look
        corner_size = 10
        corner_color = (255, 200, 100)  # Light cyan
        # Top-left corner
        cv2.line(frame, (x, y), (x + corner_size, y), corner_color, 2)
        cv2.line(frame, (x, y), (x, y + corner_size), corner_color, 2)
        # Top-right corner
        cv2.line(frame, (x + w, y), (x + w - corner_size, y), corner_color, 2)
        cv2.line(frame, (x + w, y), (x + w, y + corner_size), corner_color, 2)
        # Bottom-left corner
        cv2.line(frame, (x, y + h), (x + corner_size, y + h), corner_color, 2)
        cv2.line(frame, (x, y + h), (x, y + h - corner_size), corner_color, 2)
        # Bottom-right corner
        cv2.line(frame, (x + w, y + h), (x + w - corner_size, y + h), corner_color, 2)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_size), corner_color, 2)
        
        return frame
    
    def _draw_spotlight(self, frame: np.ndarray, bbox: Tuple[int, int, int, int],
                       color: Tuple[int, int, int]) -> np.ndarray:
        """
        Draw spotlight effect on player (like stadium lighting)
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Spotlight color
            
        Returns:
            Frame with spotlight
        """
        x, y, w, h = bbox
        
        # Calculate spotlight center
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Calculate spotlight radius
        radius = max(w, h) // 2 + 20
        
        # Create spotlight mask with gradient
        overlay = frame.copy()
        
        # Draw multiple circles with decreasing opacity for smooth gradient
        for i in range(10, 0, -1):
            alpha = 0.15 * (i / 10)
            current_radius = int(radius * (1 + (10 - i) * 0.1))
            cv2.circle(overlay, (center_x, center_y), current_radius, color, -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Add bright center highlight
        cv2.circle(frame, (center_x, center_y), radius // 3, color, -1)
        overlay = frame.copy()
        cv2.circle(overlay, (center_x, center_y), radius // 3, (255, 255, 255), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        return frame
    
    def _draw_outline(self, frame: np.ndarray, bbox: Tuple[int, int, int, int],
                     color: Tuple[int, int, int]) -> np.ndarray:
        """
        Draw professional glow outline around player (like TV graphics)
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Outline color
            
        Returns:
            Frame with outline
        """
        x, y, w, h = bbox
        
        # Create mask for the player area
        overlay = frame.copy()
        
        # Draw thick outer glow
        for i in range(10, 0, -1):
            alpha = 0.08 * (i / 10)
            thickness = i * 2
            padding = i * 3
            cv2.rectangle(overlay, 
                         (x - padding, y - padding), 
                         (x + w + padding, y + h + padding), 
                         color, 
                         thickness)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Draw main outline
        cv2.rectangle(frame, (x - 2, y - 2), (x + w + 2, y + h + 2), color, 3)
        
        # Add bright inner edge
        lighter_color = tuple(min(c + 80, 255) for c in color)
        cv2.rectangle(frame, (x + 2, y + 2), (x + w - 2, y + h - 2), lighter_color, 2)
        
        return frame
    
    def draw_all_markers(self, frame: np.ndarray, 
                        players_data: list,
                        frame_idx: Optional[int] = None,
                        tracking_start_frame: Optional[int] = None,
                        tracking_end_frame: Optional[int] = None) -> np.ndarray:
        """
        Draw all player markers on frame
        
        Args:
            frame: Frame to draw on
            players_data: List of player data objects with bbox, style, color
            frame_idx: Current frame index (for tracking range check)
            tracking_start_frame: Start frame for tracking (None = from beginning)
            tracking_end_frame: End frame for tracking (None = to end)
            
        Returns:
            Frame with all markers
        """
        result_frame = frame.copy()
        
        # Check if we should draw markers for this frame (respect tracking range)
        should_draw = True
        if frame_idx is not None:
            if tracking_start_frame is not None and frame_idx < tracking_start_frame:
                should_draw = False  # Before tracking start - don't draw!
            if tracking_end_frame is not None and frame_idx > tracking_end_frame:
                should_draw = False  # After tracking end - don't draw!
        
        if not should_draw:
            # Don't draw any markers - return frame as-is
            return result_frame
        
        print(f"draw_all_markers: Drawing {len(players_data)} players")
        for player in players_data:
            print(f"  Player {player.player_id}: bbox={player.current_bbox}, style={player.marker_style}")
            if player.current_bbox is not None:
                result_frame = self.draw_marker(
                    result_frame,
                    player.current_bbox,
                    player.marker_style,
                    player.color
                )
            else:
                print(f"  WARNING: Player {player.player_id} has None bbox!")
        
        return result_frame


