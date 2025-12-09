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
                       color: Tuple[int, int, int] = (0, 255, 255), player=None) -> np.ndarray:
        """
        Neon glowing ring - modern style around feet with 3D layering effect
        Player body hides the back part of the ring (180-360 degrees)

        Args:
            frame: Frame to draw on
            bbox: Bounding box (padded)
            color: Ring color (BGR)
            player: Player object (for accessing original_bbox)

        Returns:
            Frame with neon ring
        """
        x, y, w, h = bbox
        center_x = x + w // 2

        # Calculate radii
        radius_x = max(int(w * 0.7), 40)  # Horizontal radius
        radius_y = max(int(w * 0.15), 10)  # Vertical radius (flat ellipse)

        # Position ring on floor at feet contact point
        # Use original_bbox if available (before padding was added)
        if hasattr(player, 'current_original_bbox') and player and player.current_original_bbox:
            orig_x, orig_y, orig_w, orig_h = player.current_original_bbox
            # Feet are at the BOTTOM of the original bbox (where the actual feet are)
            feet_level = orig_y + orig_h
        else:
            # Fallback: use mathematical calculation based on padding
            padding_factor = 0.20
            total_padding_multiplier = 1 + (2 * padding_factor)  # 1.4
            feet_ratio = (1 + padding_factor) / total_padding_multiplier  # 0.857
            feet_level = y + int(h * feet_ratio)

        center_y = feet_level - radius_y
        
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
                          frame_count: int = 0, player=None) -> np.ndarray:
        """
        Pulsing circle animation - expands and contracts

        Args:
            frame: Frame to draw on
            bbox: Bounding box (padded)
            color: Circle color
            frame_count: Current frame number (for animation)
            player: Player object (for accessing original_bbox)

        Returns:
            Frame with pulsing circle
        """
        x, y, w, h = bbox
        center_x = x + w // 2

        # Base radius - LARGE ENOUGH to keep player inside during movement
        # Use larger radius to accommodate running/movement
        base_radius_x = max(int(w * 0.8), 45)  # Large - around feet with margin
        base_radius_y = max(int(w * 0.15), 10)  # Smaller vertical radius - flat on floor

        # Pulse animation (sine wave)
        pulse_factor = 1.0 + 0.15 * math.sin(frame_count * 0.2)
        radius_x = int(base_radius_x * pulse_factor)
        radius_y = int(base_radius_y * pulse_factor)

        # Position ring on floor at feet contact point
        # Use original_bbox if available (before padding was added)
        if hasattr(player, 'current_original_bbox') and player and player.current_original_bbox:
            orig_x, orig_y, orig_w, orig_h = player.current_original_bbox
            # Feet are at the BOTTOM of the original bbox (where the actual feet are)
            feet_level = orig_y + orig_h
        else:
            # Fallback: use padded bbox with offset
            floor_offset = int(h * 0.10)  # Add 10% of height to reach actual floor
            feet_level = (y + h) + floor_offset

        center_y = feet_level - radius_y  # Position so bottom touches floor
        
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
                          frame_count: int = 0, player=None) -> np.ndarray:
        """
        Gradient ring with rotating glow effect - purple with more presence

        Args:
            frame: Frame to draw on
            bbox: Bounding box (padded)
            color1: Start color (purple)
            color2: End color (purple variant)
            frame_count: Current frame number (for rotation animation)
            player: Player object (for accessing original_bbox)

        Returns:
            Frame with gradient ring
        """
        x, y, w, h = bbox
        center_x = x + w // 2

        # Calculate radii - LARGE ENOUGH to keep player inside during movement
        # Use larger radius to accommodate running/movement
        radius_x = max(int(w * 0.8), 45)  # Large size - around feet with margin
        radius_y = max(int(w * 0.15), 10)  # Smaller vertical radius - flat on floor

        # Position ring on floor at feet contact point
        # Use original_bbox if available (before padding was added)
        if hasattr(player, 'current_original_bbox') and player and player.current_original_bbox:
            orig_x, orig_y, orig_w, orig_h = player.current_original_bbox
            # Feet are at the BOTTOM of the original bbox (where the actual feet are)
            feet_level = orig_y + orig_h
        else:
            # Fallback: use padded bbox with offset
            floor_offset = int(h * 0.10)  # Add 10% of height to reach actual floor
            feet_level = (y + h) + floor_offset

        center_y = feet_level - radius_y  # Position so bottom touches floor
        
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
                       color: Tuple[int, int, int] = (100, 255, 255), player=None) -> np.ndarray:
        """
        Alien spaceship beam effect - light column from ceiling to floor with darkened background
        Creates dramatic spotlight effect highlighting only the tracked players

        Args:
            frame: Frame to draw on
            bbox: Bounding box (padded)
            color: Light color (cyan/white)
            player: Player object (for accessing original_bbox)

        Returns:
            Frame with alien beam effect
        """
        x, y, w, h = bbox
        height, width = frame.shape[:2]

        # Calculate light column center using original_bbox for accurate feet position
        center_x = x + w // 2

        # Get feet position for floor circle
        if hasattr(player, 'current_original_bbox') and player and player.current_original_bbox:
            orig_x, orig_y, orig_w, orig_h = player.current_original_bbox
            feet_y = orig_y + orig_h
        else:
            feet_y = y + h

        center_y = feet_y  # Beam goes to feet level
        
        # Light column width - narrower at top, wider at bottom (like a cone)
        # Make wider to accommodate player movement
        top_width = max(int(w * 0.4), 25)  # Narrow at top (wider than before)
        bottom_width = max(int(w * 1.5), 75)  # Wider at bottom (more room for movement)
        
        # Create a mask for the light column area
        mask = np.zeros((height, width), dtype=np.float32)
        
        # Create smooth gradient mask for light column
        y_coords, x_coords = np.ogrid[:height, :width]
        
        # Calculate distance from center line (horizontal distance)
        dx = np.abs(x_coords - center_x)

        # Calculate width at each y position (linear interpolation from top to feet)
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

        # Create beam cone mask (only inside the cone, above feet)
        # Inside cone: value between 0-1 (for smooth beam edges)
        # Outside cone OR below feet: 0 (completely dark)
        beam_cone_mask = 1.0 - smoothstep  # 1.0 at center, 0.0 at cone edges

        # Also fade from top to bottom (brighter at top, slightly dimmer at player level)
        top_fade = 1.0
        bottom_fade = 0.9
        y_fade = top_fade - (top_fade - bottom_fade) * np.clip(y_coords / max(center_y, 1), 0, 1)
        beam_cone_mask = beam_cone_mask * y_fade

        # CRITICAL: Limit beam to ONLY above feet level
        # Below feet OR outside cone: mask = 0 (use darkened frame)
        # Inside cone AND above feet: mask > 0 (brighten)
        beam_vertical_mask = np.where(y_coords <= feet_y, 1.0, 0.0)
        beam_cone_mask = beam_cone_mask * beam_vertical_mask

        # Apply uniform darkening to entire frame
        darkened_frame = (frame * 0.50).astype(np.uint8)  # Darken by 50% everywhere

        # Calculate brightness boost ONLY inside the beam cone
        # Outside: no boost (will use darkened_frame)
        # Inside: boost from 1.0 to 1.3
        brightness_boost = 1.0 + beam_cone_mask * 0.3  # 1.0 outside, up to 1.3 inside

        # Brighten the beam area
        brightened_frame = np.clip(frame.astype(np.float32) * brightness_boost[:, :, np.newaxis], 0, 255).astype(np.uint8)

        # Create 3-channel mask for blending
        mask_3channel = np.stack([beam_cone_mask, beam_cone_mask, beam_cone_mask], axis=2)

        # Blend: use brightened frame inside cone, darkened frame everywhere else
        # This ensures uniform darkness outside the cone (no gradients in dark areas)
        result = (brightened_frame.astype(np.float32) * mask_3channel +
                 darkened_frame.astype(np.float32) * (1 - mask_3channel)).astype(np.uint8)

        # Add bright floor circle where beam hits the ground (like alien abduction)
        # Make floor circle match the bottom width of the cone exactly
        floor_radius_x = int(bottom_width * 0.5)  # Half of bottom_width = radius
        floor_radius_y = int(bottom_width * 0.12)  # Flat ellipse on floor

        # Draw glowing floor circle
        for i in range(4, 0, -1):
            overlay = result.copy()
            glow_radius_x = floor_radius_x + i * 8
            glow_radius_y = floor_radius_y + i * 3
            cv2.ellipse(overlay, (center_x, feet_y), (glow_radius_x, glow_radius_y),
                       0, 0, 360, color, -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, 0.15 - (i * 0.03), result, 1.0 - (0.15 - (i * 0.03)), 0, result)

        # Main floor circle (brightest)
        overlay = result.copy()
        cv2.ellipse(overlay, (center_x, feet_y), (floor_radius_x, floor_radius_y),
                   0, 0, 360, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.4, result, 0.6, 0, result)

        return result

    @staticmethod
    def get_spotlight_mask(frame_shape: tuple, bbox: Tuple[int, int, int, int], player=None) -> np.ndarray:
        """
        Calculate spotlight mask without drawing (for combining multiple spotlights)

        Args:
            frame_shape: Shape of frame (height, width, channels)
            bbox: Bounding box (padded)
            player: Player object (for accessing original_bbox)

        Returns:
            2D mask array (values 0-1)
        """
        height, width = frame_shape[:2]
        x, y, w, h = bbox

        # Calculate light column center using original_bbox for accurate feet position
        center_x = x + w // 2

        # Get feet position
        if hasattr(player, 'current_original_bbox') and player and player.current_original_bbox:
            orig_x, orig_y, orig_w, orig_h = player.current_original_bbox
            feet_y = orig_y + orig_h
        else:
            feet_y = y + h

        center_y = feet_y

        # Light column width - narrower at top, wider at bottom (like a cone)
        # Make wider to accommodate player movement
        top_width = max(int(w * 0.4), 25)  # Narrow at top (wider than before)
        bottom_width = max(int(w * 1.5), 75)  # Wider at bottom (more room for movement)

        # Create smooth gradient mask for light column
        y_coords, x_coords = np.ogrid[:height, :width]

        # Calculate distance from center line (horizontal distance)
        dx = np.abs(x_coords - center_x)

        # Calculate width at each y position (linear interpolation from top to feet)
        y_normalized = np.clip(y_coords / max(center_y, 1), 0, 1)
        width_at_y = top_width + (bottom_width - top_width) * y_normalized

        # Distance from center line normalized by width at this y
        normalized_distance = dx / np.maximum(width_at_y, 1)

        # Create smooth falloff - fully lit in center, gradually darken towards edges
        falloff_start = 0.0
        falloff_end = 1.0

        # Smoothstep interpolation
        t = np.clip((normalized_distance - falloff_start) / (falloff_end - falloff_start), 0, 1)
        smoothstep = t * t * (3 - 2 * t)

        # Create beam cone mask (only inside the cone, above feet)
        beam_cone_mask = 1.0 - smoothstep  # 1.0 at center, 0.0 at cone edges

        # Fade from top to bottom
        top_fade = 1.0
        bottom_fade = 0.9
        y_fade = top_fade - (top_fade - bottom_fade) * np.clip(y_coords / max(center_y, 1), 0, 1)
        beam_cone_mask = beam_cone_mask * y_fade

        # Limit beam to ONLY above feet level
        beam_vertical_mask = np.where(y_coords <= feet_y, 1.0, 0.0)
        beam_cone_mask = beam_cone_mask * beam_vertical_mask

        return beam_cone_mask

    @staticmethod
    def apply_spotlight_mask(original_frame: np.ndarray, darkened_frame: np.ndarray,
                            combined_mask: np.ndarray) -> np.ndarray:
        """
        Apply combined spotlight mask to frame

        Args:
            original_frame: Original bright frame
            darkened_frame: Pre-darkened frame
            combined_mask: Combined mask from all spotlights (2D array, 0-1)

        Returns:
            Frame with spotlight effect
        """
        # Calculate brightness boost based on combined mask
        brightness_boost = 1.0 + combined_mask * 0.3  # 1.0 outside, up to 1.3 inside

        # Brighten the beam areas
        brightened_frame = np.clip(original_frame.astype(np.float32) * brightness_boost[:, :, np.newaxis], 0, 255).astype(np.uint8)

        # Create 3-channel mask for blending
        mask_3channel = np.stack([combined_mask, combined_mask, combined_mask], axis=2)

        # Blend: use brightened frame inside cones, darkened frame everywhere else
        result = (brightened_frame.astype(np.float32) * mask_3channel +
                 darkened_frame.astype(np.float32) * (1 - mask_3channel)).astype(np.uint8)

        return result

    @staticmethod
    def draw_spotlight_floor_circle(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                                    color: Tuple[int, int, int] = (100, 255, 255), player=None) -> np.ndarray:
        """
        Draw only the floor circle for spotlight (used after mask is applied)

        Args:
            frame: Frame to draw on
            bbox: Bounding box (padded)
            color: Light color (cyan/white)
            player: Player object (for accessing original_bbox)

        Returns:
            Frame with floor circle
        """
        x, y, w, h = bbox

        # Calculate center and feet position
        center_x = x + w // 2

        if hasattr(player, 'current_original_bbox') and player and player.current_original_bbox:
            orig_x, orig_y, orig_w, orig_h = player.current_original_bbox
            feet_y = orig_y + orig_h
        else:
            feet_y = y + h

        # Light column width - match the beam cone width
        bottom_width = max(int(w * 1.5), 75)

        # Floor circle dimensions
        floor_radius_x = int(bottom_width * 0.5)
        floor_radius_y = int(bottom_width * 0.12)

        # Draw glowing floor circle
        for i in range(4, 0, -1):
            overlay = frame.copy()
            glow_radius_x = floor_radius_x + i * 8
            glow_radius_y = floor_radius_y + i * 3
            cv2.ellipse(overlay, (center_x, feet_y), (glow_radius_x, glow_radius_y),
                       0, 0, 360, color, -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, 0.15 - (i * 0.03), frame, 1.0 - (0.15 - (i * 0.03)), 0, frame)

        # Main floor circle (brightest)
        overlay = frame.copy()
        cv2.ellipse(overlay, (center_x, feet_y), (floor_radius_x, floor_radius_y),
                   0, 0, 360, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

        return frame

    @staticmethod
    def draw_spotlight_no_darken(original_frame: np.ndarray, darkened_frame: np.ndarray,
                                 bbox: Tuple[int, int, int, int],
                                 color: Tuple[int, int, int] = (100, 255, 255), player=None) -> np.ndarray:
        """
        Draw spotlight effect WITHOUT darkening the frame again (for multiple spotlights)
        This function is called from draw_all_markers when there are multiple spotlight players

        Args:
            original_frame: Original bright frame to blend
            darkened_frame: Pre-darkened frame (darkened once for all spotlights)
            bbox: Bounding box (padded)
            color: Light color (cyan/white)
            player: Player object (for accessing original_bbox)

        Returns:
            Frame with alien beam effect added
        """
        x, y, w, h = bbox
        height, width = original_frame.shape[:2]

        # Calculate light column center using original_bbox for accurate feet position
        center_x = x + w // 2

        # Get feet position for floor circle
        if hasattr(player, 'current_original_bbox') and player and player.current_original_bbox:
            orig_x, orig_y, orig_w, orig_h = player.current_original_bbox
            feet_y = orig_y + orig_h
        else:
            feet_y = y + h

        center_y = feet_y  # Beam goes to feet level

        # Light column width - narrower at top, wider at bottom (like a cone)
        # Make wider to accommodate player movement
        top_width = max(int(w * 0.4), 25)  # Narrow at top (wider than before)
        bottom_width = max(int(w * 1.5), 75)  # Wider at bottom (more room for movement)

        # Create a mask for the light column area
        y_coords, x_coords = np.ogrid[:height, :width]

        # Calculate distance from center line for each pixel
        # Create cone-shaped mask
        width_at_y = np.where(y_coords <= center_y,
                             top_width + (bottom_width - top_width) * (y_coords / max(center_y, 1)),
                             bottom_width)

        distance_from_center = np.abs(x_coords - center_x)
        normalized_distance = np.clip(distance_from_center / (width_at_y / 2), 0, 1)

        # Use smoothstep function for natural transition
        falloff_start = 0.0
        falloff_end = 1.0

        # Smoothstep interpolation
        t = np.clip((normalized_distance - falloff_start) / (falloff_end - falloff_start), 0, 1)
        smoothstep = t * t * (3 - 2 * t)

        # Create beam cone mask (only inside the cone, above feet)
        # Inside cone: value between 0-1 (for smooth beam edges)
        # Outside cone OR below feet: 0 (completely dark)
        beam_cone_mask = 1.0 - smoothstep  # 1.0 at center, 0.0 at cone edges

        # Also fade from top to bottom (brighter at top, slightly dimmer at player level)
        top_fade = 1.0
        bottom_fade = 0.9
        y_fade = top_fade - (top_fade - bottom_fade) * np.clip(y_coords / max(center_y, 1), 0, 1)
        beam_cone_mask = beam_cone_mask * y_fade

        # CRITICAL: Limit beam to ONLY above feet level
        # Below feet OR outside cone: mask = 0 (use darkened frame)
        # Inside cone AND above feet: mask > 0 (brighten)
        beam_vertical_mask = np.where(y_coords <= feet_y, 1.0, 0.0)
        beam_cone_mask = beam_cone_mask * beam_vertical_mask

        # Calculate brightness boost ONLY inside the beam cone
        # Outside: no boost (will use darkened_frame)
        # Inside: boost from 1.0 to 1.3
        brightness_boost = 1.0 + beam_cone_mask * 0.3  # 1.0 outside, up to 1.3 inside

        # Brighten the beam area
        brightened_frame = np.clip(original_frame.astype(np.float32) * brightness_boost[:, :, np.newaxis], 0, 255).astype(np.uint8)

        # Create 3-channel mask for blending
        mask_3channel = np.stack([beam_cone_mask, beam_cone_mask, beam_cone_mask], axis=2)

        # Blend: use brightened frame inside cone, darkened frame everywhere else
        # This ensures uniform darkness outside the cone (no gradients in dark areas)
        result = (brightened_frame.astype(np.float32) * mask_3channel +
                 darkened_frame.astype(np.float32) * (1 - mask_3channel)).astype(np.uint8)

        # Add bright floor circle where beam hits the ground (like alien abduction)
        # Make floor circle match the bottom width of the cone exactly
        floor_radius_x = int(bottom_width * 0.5)  # Half of bottom_width = radius
        floor_radius_y = int(bottom_width * 0.12)  # Flat ellipse on floor

        # Draw glowing floor circle
        for i in range(4, 0, -1):
            overlay = result.copy()
            glow_radius_x = floor_radius_x + i * 8
            glow_radius_y = floor_radius_y + i * 3
            cv2.ellipse(overlay, (center_x, feet_y), (glow_radius_x, glow_radius_y),
                       0, 0, 360, color, -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, 0.15 - (i * 0.03), result, 1.0 - (0.15 - (i * 0.03)), 0, result)

        # Main floor circle (brightest)
        overlay = result.copy()
        cv2.ellipse(overlay, (center_x, feet_y), (floor_radius_x, floor_radius_y),
                   0, 0, 360, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.4, result, 0.6, 0, result)

        return result

    @staticmethod
    def draw_dynamic_arrow(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                          color: Tuple[int, int, int] = (0, 255, 255),  # Bright cyan - very visible
                          frame_count: int = 0, player=None) -> np.ndarray:
        """
        Dynamic animated arrow - smooth bouncing with sharper design and bright colors

        Args:
            frame: Frame to draw on
            bbox: Bounding box (padded)
            color: Arrow color (bright cyan by default)
            frame_count: Frame number for animation
            player: Player object (for accessing original_bbox)

        Returns:
            Frame with dynamic arrow
        """
        x, y, w, h = bbox
        center_x = x + w // 2

        # Position arrow above head using original_bbox if available
        if hasattr(player, 'current_original_bbox') and player and player.current_original_bbox:
            orig_x, orig_y, orig_w, orig_h = player.current_original_bbox
            # Position much higher above original head
            base_arrow_y = max(0, orig_y - 65)
        else:
            # Fallback
            base_arrow_y = max(0, y - 65)

        # Smooth bounce animation
        bounce_offset = int(8 * math.sin(frame_count * 0.12))
        arrow_y = max(0, base_arrow_y + bounce_offset)

        # Arrow size - proportional to player size, smaller
        arrow_size = max(int(w * 0.25), 25)  # Smaller and proportional
        
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
                            color: Tuple[int, int, int] = (255, 150, 0), player=None) -> np.ndarray:
        """
        Hexagon outline - futuristic look with large size to contain entire player

        Args:
            frame: Frame to draw on
            bbox: Bounding box (padded)
            color: Hexagon color
            player: Player object (for accessing original_bbox)

        Returns:
            Frame with hexagon
        """
        x, y, w, h = bbox
        center_x = x + w // 2
        center_y = y + h // 2

        # Much larger hexagon to contain entire player with margin
        # Use height for size calculation to ensure it covers head to feet
        size_horizontal = max(int(w * 0.75), 50)  # Wider
        size_vertical = max(int(h * 0.65), 70)  # Taller to cover full body
        
        # Calculate hexagon points (elliptical to fit body shape better)
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 2
            # Use different radii for horizontal and vertical
            px = int(center_x + size_horizontal * math.cos(angle))
            py = int(center_y + size_vertical * math.sin(angle))
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
                   color: Tuple[int, int, int] = (0, 215, 255),
                   frame_count: int = 0, player=None) -> np.ndarray:
        """
        Premium golden star icon above player - "Player on Fire" indicator
        Professional championship-level broadcast style

        Args:
            frame: Frame to draw on
            bbox: Bounding box (padded)
            color: Star color (gold BGR)
            frame_count: Current frame number (for animation)
            player: Player object (for accessing original_bbox)

        Returns:
            Frame with golden star effect
        """
        x, y, w, h = bbox
        center_x = x + w // 2

        # Position star above head using original_bbox if available
        if hasattr(player, 'current_original_bbox') and player and player.current_original_bbox:
            orig_x, orig_y, orig_w, orig_h = player.current_original_bbox
            # Position above original head (slightly lower than arrows)
            star_y = max(0, orig_y - 50)
        else:
            # Fallback
            star_y = max(0, y - 50)

        # Star size proportional to player
        star_size = max(int(w * 0.35), 30)

        # Pulsing animation (subtle)
        pulse = 1.0 + 0.08 * math.sin(frame_count * 0.15)
        radius = int(star_size * pulse)
        
        # Create 5-pointed star (championship star)
        star_points = []
        num_points = 5

        for i in range(num_points * 2):
            angle = (i * math.pi / num_points) - (math.pi / 2)  # Start from top
            if i % 2 == 0:
                # Outer point
                current_radius = radius
            else:
                # Inner point
                current_radius = int(radius * 0.4)

            x_point = int(center_x + current_radius * math.cos(angle))
            y_point = int(star_y + current_radius * math.sin(angle))
            star_points.append([x_point, y_point])

        star_points = np.array(star_points, np.int32)

        # Gold colors for premium look
        gold_dark = (0, 165, 215)  # Darker gold
        gold_bright = (0, 215, 255)  # Bright gold
        gold_white = (200, 245, 255)  # Almost white gold

        # Draw outer glow (golden aura)
        for i in range(6, 0, -1):
            overlay = frame.copy()
            glow_size = int(radius * (1.0 + i * 0.12))

            # Create larger star for glow
            glow_points = []
            for j in range(num_points * 2):
                angle = (j * math.pi / num_points) - (math.pi / 2)
                if j % 2 == 0:
                    current_radius = glow_size
                else:
                    current_radius = int(glow_size * 0.4)
                x_point = int(center_x + current_radius * math.cos(angle))
                y_point = int(star_y + current_radius * math.sin(angle))
                glow_points.append([x_point, y_point])

            glow_points = np.array(glow_points, np.int32)
            cv2.fillPoly(overlay, [glow_points], gold_bright)
            cv2.addWeighted(overlay, 0.12 - (i * 0.015), frame, 1.0 - (0.12 - (i * 0.015)), 0, frame)

        # Draw main star (golden)
        cv2.fillPoly(frame, [star_points], gold_bright)

        # Add darker gold outline for definition
        cv2.polylines(frame, [star_points], True, gold_dark, 2, cv2.LINE_AA)

        # Add bright center highlight (white-gold)
        center_highlight_size = int(radius * 0.2)
        cv2.circle(frame, (center_x, star_y), center_highlight_size, gold_white, -1, cv2.LINE_AA)
        
        return frame

