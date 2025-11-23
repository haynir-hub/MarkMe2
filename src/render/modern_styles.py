"""
Modern Marker Styles - Beautiful, eye-catching marker styles for sports videos
"""
import cv2
import numpy as np
from typing import Tuple
import math


class ModernStyles:
    """Collection of modern, professional marker styles"""
    
    @staticmethod
    def draw_neon_ring(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                       color: Tuple[int, int, int] = (0, 255, 255)) -> np.ndarray:
        """
        Neon glowing ring - modern style around feet with 3D layering effect
        Player body hides the back part of the ring (180-360 degrees)
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box (x, y, w, h)
            color: Ring color (BGR)
            
        Returns:
            Frame with neon ring
        """
        x, y, w, h = bbox
        center_x = x + w // 2
        
        # Calculate radii - LARGE ENOUGH to keep player inside during movement
        # Use larger radius to accommodate running/movement
        radius_x = max(int(w * 0.8), 45)  # Large horizontal radius - around feet with margin
        radius_y = max(int(w * 0.15), 10)  # Smaller vertical radius - flat on floor
        
        # Place ring CENTERED at ANKLE level (above feet, at ankle)
        # Bottom of ellipse should be at feet level (y + h)
        # So: center_y + radius_y = y + h
        # Therefore: center_y = y + h - radius_y
        center_y = y + h - radius_y  # Center at ankle level, bottom touches feet
        
        # Draw full neon ring (360 degrees) - MORE TRANSPARENT so it doesn't hide video
        # Reduced glow for less intrusion
        for i in range(6, 0, -1):
            overlay = frame.copy()
            glow_intensity = 0.25 - (i * 0.03)  # More transparent (was 0.5)
            cv2.ellipse(
                overlay,
                (center_x, center_y),
                (radius_x + i * 3, radius_y + i * 2),  # Smaller glow
                0, 0, 360,  # Full circle (360 degrees)
                color,
                max(1, int(3 * i / 6)),  # Thinner
                cv2.LINE_AA
            )
            cv2.addWeighted(overlay, glow_intensity, frame, 1.0 - glow_intensity, 0, frame)
        
        # Main ring (brightest) - MORE TRANSPARENT
        overlay = frame.copy()
        cv2.ellipse(
            overlay,
            (center_x, center_y),
            (radius_x, radius_y),
            0, 0, 360,  # Full circle
            color,
            3,  # Thinner (was 4)
            cv2.LINE_AA
        )
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)  # 60% opacity
        
        # Add extra bright inner ring for visibility - MORE TRANSPARENT
        lighter_color = tuple(min(c + 100, 255) for c in color)
        overlay = frame.copy()
        cv2.ellipse(
            overlay,
            (center_x, center_y),
            (int(radius_x * 0.9), int(radius_y * 0.9)),
            0, 0, 360,  # Full circle
            lighter_color,
            2,
            cv2.LINE_AA
        )
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)  # 40% opacity
        
        return frame
    
    @staticmethod
    def draw_pulse_circle(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                          color: Tuple[int, int, int] = (0, 165, 255),  # Orange in BGR (B=0, G=165, R=255)
                          frame_count: int = 0) -> np.ndarray:
        """
        Pulsing circle animation - expands and contracts
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Circle color
            frame_count: Current frame number (for animation)
            
        Returns:
            Frame with pulsing circle
        """
        x, y, w, h = bbox
        center_x = x + w // 2
        
        # Base radius - LARGE ENOUGH to keep player inside during movement
        # Use larger radius to accommodate running/movement
        base_radius_x = max(int(w * 0.8), 45)  # Large - around feet with margin
        base_radius_y = max(int(w * 0.15), 10)  # Smaller vertical radius - flat on floor
        
        # Place ring CENTERED at ANKLE level (above feet, at ankle)
        # Bottom of ellipse should be at feet level (y + h)
        # So: center_y + radius_y = y + h
        # Therefore: center_y = y + h - radius_y
        center_y = y + h - base_radius_y  # Center at ankle level, bottom touches feet
        
        # Pulse animation (sine wave)
        pulse_factor = 1.0 + 0.15 * math.sin(frame_count * 0.2)
        radius_x = int(base_radius_x * pulse_factor)
        radius_y = int(base_radius_y * pulse_factor)
        
        # Draw full pulsing circle (360 degrees) - MORE TRANSPARENT so it doesn't hide video
        # Draw outer fading ring - MORE TRANSPARENT
        for i in range(3):
            alpha_factor = 1.0 - (i * 0.3)
            overlay = frame.copy()
            cv2.ellipse(
                overlay,
                (center_x, center_y),
                (radius_x + i * 4, radius_y + i * 2),  # Smaller glow
                0, 0, 360,  # Full circle
                color,
                2,
                cv2.LINE_AA
            )
            cv2.addWeighted(overlay, alpha_factor * 0.25, frame, 1.0 - alpha_factor * 0.25, 0, frame)  # More transparent
        
        # Draw main circle - MORE TRANSPARENT
        overlay = frame.copy()
        cv2.ellipse(
            overlay,
            (center_x, center_y),
            (radius_x, radius_y),
            0, 0, 360,  # Full circle
            color,
            2,  # Thinner (was 3)
            cv2.LINE_AA
        )
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)  # 60% opacity
        
        return frame
    
    @staticmethod
    def draw_gradient_ring(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                          color1: Tuple[int, int, int] = (255, 200, 0),
                          color2: Tuple[int, int, int] = (255, 0, 200),
                          frame_count: int = 0) -> np.ndarray:
        """
        Gradient ring with rotating glow effect - purple with more presence
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color1: Start color (purple)
            color2: End color (purple variant)
            frame_count: Current frame number (for rotation animation)
            
        Returns:
            Frame with gradient ring
        """
        x, y, w, h = bbox
        center_x = x + w // 2
        
        # Calculate radii - LARGE ENOUGH to keep player inside during movement
        # Use larger radius to accommodate running/movement
        radius_x = max(int(w * 0.8), 45)  # Large size - around feet with margin
        radius_y = max(int(w * 0.15), 10)  # Smaller vertical radius - flat on floor
        
        # Place ring CENTERED at ANKLE level (above feet, at ankle)
        # Bottom of ellipse should be at feet level (y + h)
        # So: center_y + radius_y = y + h
        # Therefore: center_y = y + h - radius_y
        center_y = y + h - radius_y  # Center at ankle level, bottom touches feet
        
        # Draw rotating glow effect (outer glow that rotates)
        rotation_offset = int(frame_count * 2) % 360  # Rotate glow
        
        # Draw outer rotating glow
        for i in range(8, 0, -1):
            overlay = frame.copy()
            glow_radius_x = radius_x + i * 4
            glow_radius_y = radius_y + i * 2
            
            # Draw rotating segments
            for angle in range(0, 360, 30):
                glow_angle = (angle + rotation_offset) % 360
                # Calculate gradient color based on angle
                t = (glow_angle / 360.0)
                glow_color = (
                    int(color1[0] * (1 - t) + color2[0] * t),
                    int(color1[1] * (1 - t) + color2[1] * t),
                    int(color1[2] * (1 - t) + color2[2] * t)
                )
                
                cv2.ellipse(
                    overlay,
                    (center_x, center_y),
                    (glow_radius_x, glow_radius_y),
                    0,
                    glow_angle - 15,
                    glow_angle + 15,
                    glow_color,
                    3,
                    cv2.LINE_AA
                )
            cv2.addWeighted(overlay, 0.2 - (i * 0.02), frame, 1.0 - (0.2 - (i * 0.02)), 0, frame)
        
        # Draw main thick gradient ring
        overlay = frame.copy()
        num_segments = 360
        for angle in range(0, num_segments, 2):
            # Calculate gradient color
            t = angle / num_segments
            color = (
                int(color1[0] * (1 - t) + color2[0] * t),
                int(color1[1] * (1 - t) + color2[1] * t),
                int(color1[2] * (1 - t) + color2[2] * t)
            )
            
            # Draw arc segment with thicker line
            cv2.ellipse(
                overlay,
                (center_x, center_y),
                (radius_x, radius_y),
                0,
                angle,
                angle + 5,
                color,
                5,  # Thicker line for more presence
                cv2.LINE_AA
            )
        # Apply transparency
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)  # More opaque for presence
        
        # Add inner bright ring
        inner_overlay = frame.copy()
        for angle in range(0, 360, 3):
            t = angle / 360.0
            bright_color = (
                min(255, int(color1[0] * (1 - t) + color2[0] * t) + 50),
                min(255, int(color1[1] * (1 - t) + color2[1] * t) + 50),
                min(255, int(color1[2] * (1 - t) + color2[2] * t) + 50)
            )
            cv2.ellipse(
                inner_overlay,
                (center_x, center_y),
                (int(radius_x * 0.85), int(radius_y * 0.85)),
                0,
                angle,
                angle + 5,
                bright_color,
                2,
                cv2.LINE_AA
            )
        cv2.addWeighted(inner_overlay, 0.5, frame, 0.5, 0, frame)
        
        return frame
    
    @staticmethod
    def draw_spotlight(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                       color: Tuple[int, int, int] = (100, 255, 255)) -> np.ndarray:
        """
        Light column effect - like alien spaceship beam from ceiling, following player
        Darkens entire image, creates a vertical light column from top to player
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Light color (cyan/white)
            
        Returns:
            Frame with light column effect
        """
        x, y, w, h = bbox
        height, width = frame.shape[:2]
        
        # Calculate light column center (center of bbox horizontally, extends from top)
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Light column width - narrower at top, wider at bottom (like a cone)
        top_width = max(int(w * 0.3), 20)  # Narrow at top
        bottom_width = max(int(w * 1.2), 60)  # Wider at bottom
        
        # Create a mask for the light column area
        mask = np.zeros((height, width), dtype=np.float32)
        
        # Create smooth gradient mask for light column
        y_coords, x_coords = np.ogrid[:height, :width]
        
        # Calculate distance from center line (horizontal distance)
        dx = np.abs(x_coords - center_x)
        
        # Calculate width at each y position (linear interpolation from top to bottom)
        # At top (y=0): width = top_width
        # At player level (y=center_y): width = bottom_width
        y_normalized = np.clip(y_coords / max(center_y, 1), 0, 1)
        width_at_y = top_width + (bottom_width - top_width) * y_normalized
        
        # Distance from center line normalized by width at this y
        normalized_distance = dx / np.maximum(width_at_y, 1)
        
        # Create smooth falloff - fully lit in center, gradually darken towards edges
        # Use smoothstep function for natural transition
        falloff_start = 0.0
        falloff_end = 1.0
        
        # Smoothstep interpolation
        t = np.clip((normalized_distance - falloff_start) / (falloff_end - falloff_start), 0, 1)
        smoothstep = t * t * (3 - 2 * t)
        
        # Inside light column: brightness = 1.0 (fully lit)
        # Outside light column: brightness = 0.6 (more darkened)
        # Transition zone: smooth gradient
        mask = 1.0 - (smoothstep * 0.4)  # 1.0 in center, 0.6 at edges
        
        # Also fade from top to bottom (brighter at top, slightly dimmer at player level)
        top_fade = 1.0
        bottom_fade = 0.9
        y_fade = top_fade - (top_fade - bottom_fade) * np.clip(y_coords / max(center_y, 1), 0, 1)
        mask = mask * y_fade
        
        # Apply darkening to entire frame first (darken everything more)
        darkened_frame = (frame * 0.65).astype(np.uint8)  # Darken by 35%
        
        # Create 3-channel mask for color blending
        mask_3channel = np.stack([mask, mask, mask], axis=2)
        
        # Blend: light column area uses original brightness, rest is darkened
        result = (frame.astype(np.float32) * mask_3channel + 
                 darkened_frame.astype(np.float32) * (1 - mask_3channel)).astype(np.uint8)
        
        # Add bright light column border for definition (like beam edges)
        # Draw vertical lines on sides of light column
        for y_pos in range(0, min(center_y + bottom_width, height), 5):
            width_at_this_y = int(top_width + (bottom_width - top_width) * (y_pos / max(center_y, 1)))
            left_x = center_x - width_at_this_y // 2
            right_x = center_x + width_at_this_y // 2
            
            if 0 <= left_x < width:
                cv2.line(result, (left_x, y_pos), (left_x, min(y_pos + 5, height)), color, 1, cv2.LINE_AA)
            if 0 <= right_x < width:
                cv2.line(result, (right_x, y_pos), (right_x, min(y_pos + 5, height)), color, 1, cv2.LINE_AA)
        
        # Add bright center line (core of the beam)
        bright_center_color = (255, 255, 255)  # White
        for y_pos in range(0, min(center_y + bottom_width, height), 3):
            cv2.line(result, (center_x, y_pos), (center_x, min(y_pos + 3, height)), bright_center_color, 1, cv2.LINE_AA)
        
        return result
    
    @staticmethod
    def draw_dynamic_arrow(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                          color: Tuple[int, int, int] = (0, 255, 200),
                          frame_count: int = 0) -> np.ndarray:
        """
        Dynamic animated arrow - smooth bouncing with sharper, more elegant design
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Arrow color
            frame_count: Frame number for animation
            
        Returns:
            Frame with dynamic arrow
        """
        x, y, w, h = bbox
        center_x = x + w // 2
        
        # Smooth bounce animation - position arrow ABOVE head
        bounce_offset = int(12 * math.sin(frame_count * 0.12))  # Smoother, larger bounce
        # Position arrow above head (top of bbox minus offset)
        arrow_y = max(0, y - 55 + bounce_offset)  # Higher above head
        
        # Arrow size - proportional to player size, larger
        arrow_size = max(int(w * 0.4), 40)  # Larger and proportional
        
        # Create sharper, more elegant arrow shape
        tip_y = arrow_y
        base_y = arrow_y + arrow_size
        base_width = arrow_size
        
        # Draw glow effect (multiple layers for smooth glow)
        for i in range(5, 0, -1):
            overlay = frame.copy()
            glow_size = arrow_size + i * 4
            glow_base_width = base_width + i * 3
            glow_tip_y = tip_y - i * 2
            glow_base_y = base_y + i * 2
            
            glow_points = np.array([
                [center_x, glow_tip_y],
                [center_x - glow_base_width // 2, glow_base_y],
                [center_x - glow_base_width // 3, glow_base_y - glow_size // 4],
                [center_x, glow_base_y - glow_size // 3],
                [center_x + glow_base_width // 3, glow_base_y - glow_size // 4],
                [center_x + glow_base_width // 2, glow_base_y]
            ], np.int32)
            
            cv2.fillPoly(overlay, [glow_points], color)
            cv2.addWeighted(overlay, 0.12 - (i * 0.02), frame, 1.0 - (0.12 - (i * 0.02)), 0, frame)
        
        # Draw main arrow with sharper, more elegant shape
        arrow_points = np.array([
            [center_x, tip_y],
            [center_x - base_width // 2, base_y],
            [center_x - base_width // 3, base_y - arrow_size // 4],  # Inner point for sharper look
            [center_x, base_y - arrow_size // 3],
            [center_x + base_width // 3, base_y - arrow_size // 4],  # Inner point
            [center_x + base_width // 2, base_y]
        ], np.int32)
        
        # Fill arrow
        cv2.fillPoly(frame, [arrow_points], color)
        
        # Draw outline for definition (thicker, more visible)
        cv2.polylines(frame, [arrow_points], True, (255, 255, 255), 3, cv2.LINE_AA)
        
        # Add highlight on top for depth
        highlight_color = tuple(min(c + 60, 255) for c in color)
        highlight_points = np.array([
            [center_x, tip_y],
            [center_x - base_width // 4, base_y - arrow_size // 2],
            [center_x, base_y - arrow_size // 2.5],
            [center_x + base_width // 4, base_y - arrow_size // 2]
        ], np.int32)
        cv2.fillPoly(frame, [highlight_points], highlight_color)
        
        # Add subtle inner outline for extra sharpness
        cv2.polylines(frame, [highlight_points], True, (255, 255, 255), 1, cv2.LINE_AA)
        
        return frame
    
    @staticmethod
    def draw_hexagon_outline(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                            color: Tuple[int, int, int] = (255, 150, 0)) -> np.ndarray:
        """
        Hexagon outline - futuristic look
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Hexagon color
            
        Returns:
            Frame with hexagon
        """
        x, y, w, h = bbox
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Hexagon size
        size = max(int(w * 0.7), 35)
        
        # Calculate hexagon points
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 2
            px = int(center_x + size * math.cos(angle))
            py = int(center_y + size * math.sin(angle))
            points.append([px, py])
        
        points = np.array(points, np.int32)
        
        # Draw glow
        for i in range(3, 0, -1):
            overlay = frame.copy()
            cv2.polylines(overlay, [points], True, color, i * 2, cv2.LINE_AA)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Draw main hexagon
        cv2.polylines(frame, [points], True, color, 3, cv2.LINE_AA)
        
        return frame
    
    @staticmethod
    def draw_crosshair(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                       color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Crosshair targeting system - tactical look
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Crosshair color
            
        Returns:
            Frame with crosshair
        """
        x, y, w, h = bbox
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Circle radius
        radius = max(int(max(w, h) * 0.6), 40)
        
        # Draw circle
        cv2.circle(frame, (center_x, center_y), radius, color, 2, cv2.LINE_AA)
        cv2.circle(frame, (center_x, center_y), radius - 5, color, 1, cv2.LINE_AA)
        
        # Draw crosshair lines
        line_len = 15
        gap = 8
        
        # Top
        cv2.line(frame, (center_x, center_y - radius - gap), 
                (center_x, center_y - radius - gap - line_len), color, 2, cv2.LINE_AA)
        # Bottom
        cv2.line(frame, (center_x, center_y + radius + gap), 
                (center_x, center_y + radius + gap + line_len), color, 2, cv2.LINE_AA)
        # Left
        cv2.line(frame, (center_x - radius - gap, center_y), 
                (center_x - radius - gap - line_len, center_y), color, 2, cv2.LINE_AA)
        # Right
        cv2.line(frame, (center_x + radius + gap, center_y), 
                (center_x + radius + gap + line_len, center_y), color, 2, cv2.LINE_AA)
        
        # Draw corner brackets
        bracket_size = 10
        corners = [
            (center_x - radius, center_y - radius),  # Top-left
            (center_x + radius, center_y - radius),  # Top-right
            (center_x - radius, center_y + radius),  # Bottom-left
            (center_x + radius, center_y + radius)   # Bottom-right
        ]
        
        for i, (cx, cy) in enumerate(corners):
            # Determine bracket direction
            h_dir = 1 if i % 2 == 1 else -1
            v_dir = 1 if i >= 2 else -1
            
            # Horizontal line
            cv2.line(frame, (cx, cy), (cx + h_dir * bracket_size, cy), color, 2, cv2.LINE_AA)
            # Vertical line
            cv2.line(frame, (cx, cy), (cx, cy + v_dir * bracket_size), color, 2, cv2.LINE_AA)
        
        # Center dot
        cv2.circle(frame, (center_x, center_y), 3, color, -1, cv2.LINE_AA)
        
        return frame
    
    @staticmethod
    def draw_flame(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                   color: Tuple[int, int, int] = (0, 100, 255),
                   frame_count: int = 0) -> np.ndarray:
        """
        Professional flame icon above player's head - realistic fire shape with smooth curves
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box
            color: Flame color (orange/red BGR)
            frame_count: Current frame number (for animation)
            
        Returns:
            Frame with flame effect
        """
        x, y, w, h = bbox
        center_x = x + w // 2
        
        # Position flame above head
        flame_base_y = max(0, y - 20)  # Above head with gap
        flame_height = max(int(h * 0.4), 40)  # Taller and more visible
        flame_base_width = max(int(w * 0.35), 18)  # Base width
        
        # Animation parameters
        anim_speed = 0.2
        wave1 = math.sin(frame_count * anim_speed)
        wave2 = math.sin(frame_count * anim_speed * 1.6 + 1.2)
        wave3 = math.sin(frame_count * anim_speed * 0.85 + 2.8)
        
        # Create realistic flame shape with smooth curves using bezier-like points
        # Main flame: wider at base, narrows to point at top with wavy sides
        num_points = 30  # More points for smoother curve
        
        # Base points
        base_left = center_x - flame_base_width // 2
        base_right = center_x + flame_base_width // 2
        base_center = center_x
        
        # Top point (animated)
        top_x = center_x + int(wave1 * 3)
        top_y = flame_base_y - flame_height + int(wave2 * 5)
        
        # Create smooth flame outline using multiple control points
        flame_points = []
        
        # Left side: smooth curve from base_left to top
        for i in range(num_points // 2 + 1):
            t = i / (num_points / 2)  # 0 to 1
            
            # Use smooth interpolation with wave animation
            # Create wavy side effect
            wave_offset = wave1 * (1 - t) * 6 + wave2 * (1 - t) * 4
            
            # Smooth curve using cubic interpolation
            # Start at base_left, curve inward, then to top
            if t < 0.5:
                # Lower half: curve inward
                curve_factor = t * 2  # 0 to 1
                x_pos = base_left + int((base_center - base_left) * curve_factor * 0.7) + int(wave_offset)
                y_pos = flame_base_y - int(flame_height * t * 2 * 0.5)
            else:
                # Upper half: curve to top
                curve_factor = (t - 0.5) * 2  # 0 to 1
                x_pos = base_center + int((top_x - base_center) * curve_factor) + int(wave_offset * (1 - curve_factor))
                y_pos = flame_base_y - int(flame_height * (0.5 + curve_factor * 0.5))
            
            flame_points.append([int(x_pos), int(y_pos)])
        
        # Right side: smooth curve from top to base_right
        for i in range(num_points // 2, -1, -1):
            t = i / (num_points / 2)  # 1 to 0
            
            # Wave animation for right side
            wave_offset = wave3 * (1 - t) * 6 + wave1 * (1 - t) * 4
            
            if t > 0.5:
                # Upper half: from top
                curve_factor = (1 - t) * 2  # 1 to 0
                x_pos = top_x + int((base_center - top_x) * (1 - curve_factor)) + int(wave_offset * curve_factor)
                y_pos = flame_base_y - int(flame_height * (0.5 + (1 - curve_factor) * 0.5))
            else:
                # Lower half: to base_right
                curve_factor = t * 2  # 0 to 1
                x_pos = base_center + int((base_right - base_center) * curve_factor * 0.7) + int(wave_offset)
                y_pos = flame_base_y - int(flame_height * (1 - t * 2) * 0.5)
            
            flame_points.append([int(x_pos), int(y_pos)])
        
        flame_points = np.array(flame_points, np.int32)
        
        # Draw outer glow layers
        for i in range(5, 0, -1):
            overlay = frame.copy()
            glow_points = flame_points.copy()
            
            # Expand glow outward
            for j in range(len(glow_points)):
                # Calculate direction from center
                dx = glow_points[j][0] - center_x
                dy = glow_points[j][1] - (flame_base_y - flame_height // 2)
                dist = math.sqrt(dx*dx + dy*dy) if (dx != 0 or dy != 0) else 1
                
                # Expand outward
                expand_factor = i * 1.5
                glow_points[j][0] = int(glow_points[j][0] + (dx / dist) * expand_factor)
                glow_points[j][1] = int(glow_points[j][1] + (dy / dist) * expand_factor)
            
            glow_color = (
                min(255, color[0] + i * 12),
                min(255, color[1] + i * 8),
                min(255, color[2] + i * 18)
            )
            cv2.fillPoly(overlay, [glow_points], glow_color)
            cv2.addWeighted(overlay, 0.18 - (i * 0.03), frame, 1.0 - (0.18 - (i * 0.03)), 0, frame)
        
        # Draw main flame
        cv2.fillPoly(frame, [flame_points], color)
        
        # Add bright yellow/white core (inner flame)
        bright_yellow = (0, 220, 255)  # Bright yellow-white in BGR
        core_points = flame_points.copy()
        
        # Shrink core inward
        for j in range(len(core_points)):
            dx = core_points[j][0] - center_x
            dy = core_points[j][1] - (flame_base_y - flame_height // 2)
            dist = math.sqrt(dx*dx + dy*dy) if (dx != 0 or dy != 0) else 1
            
            # Shrink inward (keep top point)
            shrink_factor = 0.4 if j < len(core_points) // 3 else 0.3
            core_points[j][0] = int(core_points[j][0] - (dx / dist) * shrink_factor * dist)
            core_points[j][1] = int(core_points[j][1] - (dy / dist) * shrink_factor * dist * 0.7)
        
        cv2.fillPoly(frame, [core_points], bright_yellow)
        
        # Add subtle outline
        cv2.polylines(frame, [flame_points], True, (0, 40, 180), 2, cv2.LINE_AA)
        
        return frame

