"""
Tracker Manager - Manages multiple player trackers
"""
import cv2
import numpy as np
import traceback
from typing import List, Dict, Optional, Tuple
from .player_tracker import PlayerTracker, TrackerType


class PlayerData:
    """Data structure for a tracked player"""
    def __init__(self, player_id: int, name: str, marker_style: str, 
                 initial_frame: int, bbox: Tuple[int, int, int, int]):
        self.player_id = player_id
        self.name = name
        self.marker_style = marker_style  # 'arrow', 'circle', 'rectangle'
        self.initial_frame = initial_frame  # First frame where player was marked (for tracking start)
        self.bbox = bbox  # Bbox at initial_frame (used for tracking initialization)
        # Learning frames: frames where user marked this player for learning (before tracking starts)
        # Format: {frame_idx: bbox}
        self.learning_frames: Dict[int, Tuple[int, int, int, int]] = {initial_frame: bbox}
        self.tracker = PlayerTracker(TrackerType.CSRT)
        self.current_bbox = bbox
        self.tracking_lost = False
        self.color = self._get_default_color()
    
    def add_learning_frame(self, frame_idx: int, bbox: Tuple[int, int, int, int]):
        """Add a learning frame for this player"""
        self.learning_frames[frame_idx] = bbox
        # Update initial_frame to the earliest learning frame
        if frame_idx < self.initial_frame:
            self.initial_frame = frame_idx
            self.bbox = bbox
    
    def _get_default_color(self) -> Tuple[int, int, int]:
        """Get default color based on marker style"""
        color_map = {
            'arrow': (0, 255, 255),        # Yellow
            'circle': (0, 255, 255),       # Yellow (for 3D floor hoop)
            'rectangle': (255, 100, 0),    # Blue (forced in renderer)
            'spotlight': (0, 200, 255),    # Orange
            'outline': (255, 0, 255)       # Magenta
        }
        return color_map.get(self.marker_style, (255, 255, 255))


class TrackerManager:
    """Manages multiple player trackers"""
    
    def __init__(self):
        self.players: Dict[int, PlayerData] = {}
        self.next_player_id = 1
        self.video_cap = None
        self.video_path: Optional[str] = None
        self.total_frames = 0
        self.fps = 30.0
        self.duration = 0.0
        self.frame_width = 0
        self.frame_height = 0
        self.current_frame_idx = 0
        # Store tracking results: {player_id: {frame_idx: bbox}}
        self.tracking_results: Dict[int, Dict[int, Tuple[int, int, int, int]]] = {}
    
    def _is_valid_fps(self, fps: float) -> bool:
        return 1 <= fps <= 240
    
    def _is_valid_frame_count(self, frame_count: float) -> bool:
        return 1 <= frame_count <= 100000
    
    def _count_frames(self, cap: cv2.VideoCapture) -> int:
        """Count frames manually when CAP_PROP_FRAME_COUNT is unreliable"""
        frame_count = 0
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while True:
            ret, _ = cap.read()
            if not ret:
                break
            frame_count += 1
            if frame_count > 100000:
                break
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return frame_count
    
    def probe_video(self, video_path: str) -> Optional[Dict[str, float]]:
        """Read metadata from video without keeping the capture open"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not self._is_valid_fps(fps):
            fps = 30.0
        
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if not self._is_valid_frame_count(frame_count):
            frame_count = self._count_frames(cap)
        else:
            frame_count = int(frame_count)
        
        duration = frame_count / fps if fps > 0 else 0.0
        
        cap.release()
        
        return {
            "fps": fps,
            "frame_count": frame_count,
            "duration": duration,
            "width": width,
            "height": height
        }
        
    def load_video(self, video_path: str, metadata: Optional[Dict[str, float]] = None) -> bool:
        """
        Load video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if video loaded successfully
        """
        try:
            if metadata is None:
                metadata = self.probe_video(video_path)
            if metadata is None:
                return False
            
            # Release existing capture if any
            if self.video_cap is not None:
                self.video_cap.release()
            
            video_cap = cv2.VideoCapture(video_path)
            if not video_cap.isOpened():
                return False
            
            self.video_cap = video_cap
            self.video_path = video_path
            self.fps = metadata.get("fps", 30.0)
            self.total_frames = int(metadata.get("frame_count", 0))
            self.duration = metadata.get("duration", 0.0)
            self.frame_width = int(metadata.get("width", 0))
            self.frame_height = int(metadata.get("height", 0))
            self.current_frame_idx = 0
            return True
        except Exception as e:
            print(f"Error loading video: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def add_player(self, name: str, marker_style: str, 
                   initial_frame: int, bbox: Tuple[int, int, int, int]) -> int:
        """
        Add a new player to track
        
        Args:
            name: Player name
            marker_style: Style of marker ('arrow', 'circle', 'rectangle')
            initial_frame: Frame index where player is marked
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            Player ID
        """
        player_id = self.next_player_id
        self.next_player_id += 1
        
        player = PlayerData(player_id, name, marker_style, initial_frame, bbox)
        self.players[player_id] = player
        
        return player_id
    
    def add_learning_frame_to_player(self, player_id: int, frame_idx: int, bbox: Tuple[int, int, int, int]) -> bool:
        """
        Add a learning frame to an existing player
        
        Args:
            player_id: Player ID
            frame_idx: Frame index where player is marked
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            True if successful, False if player not found
        """
        if player_id not in self.players:
            return False
        
        self.players[player_id].add_learning_frame(frame_idx, bbox)
        return True
    
    def update_trackers(self, frame: np.ndarray, frame_idx: int = None) -> Dict[int, Optional[Tuple[int, int, int, int]]]:
        """
        Update all trackers with current frame
        
        Args:
            frame: Current frame (BGR format)
            frame_idx: Optional frame index for storing results
            
        Returns:
            Dictionary mapping player_id to current bbox (or None if lost)
        """
        results = {}
        
        for player_id, player in self.players.items():
            bbox = player.tracker.update(frame)
            player.current_bbox = bbox
            player.tracking_lost = (bbox is None)
            results[player_id] = bbox
            
            # Store result if frame_idx provided
            if frame_idx is not None:
                if player_id not in self.tracking_results:
                    self.tracking_results[player_id] = {}
                self.tracking_results[player_id][frame_idx] = bbox
        
        return results
    
    def get_bbox_at_frame(self, player_id: int, frame_idx: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Get bounding box for a player at a specific frame
        
        Args:
            player_id: Player ID
            frame_idx: Frame index
            
        Returns:
            Bounding box or None
        """
        if player_id in self.tracking_results:
            bbox = self.tracking_results[player_id].get(frame_idx)
            if frame_idx % 30 == 0:  # Log every 30 frames
                print(f"get_bbox_at_frame: player={player_id}, frame={frame_idx}, bbox={bbox}")
            return bbox
        else:
            print(f"ERROR: Player {player_id} not found in tracking_results!")
            return None
    
    def get_frame(self, frame_idx: int) -> Optional[np.ndarray]:
        """
        Get specific frame from video - uses multiple strategies for problematic codecs
        
        Args:
            frame_idx: Frame index (0-based)
            
        Returns:
            Frame as numpy array or None if error
        """
        if self.video_path is None:
            return None
        
        if frame_idx < 0 or (self.total_frames > 0 and frame_idx >= self.total_frames):
            return None
        
        try:
            # Strategy 1: Try with existing video_cap with reset
            if self.video_cap is not None and self.video_cap.isOpened():
                print(f"Strategy 1: Trying with existing video_cap")
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset first
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = self.video_cap.read()
                print(f"Strategy 1 result: ret={ret}, frame is None={frame is None}")
                if ret and frame is not None:
                    print(f"✅ Frame {frame_idx} read successfully with Strategy 1")
                    return frame
            
            # Strategy 2: Open new capture and seek - VERIFY seek worked!
            print(f"Strategy 2: Opening new VideoCapture")
            temp_cap = cv2.VideoCapture(self.video_path)
            if temp_cap.isOpened():
                temp_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                # Verify the seek actually worked
                actual_pos = int(temp_cap.get(cv2.CAP_PROP_POS_FRAMES))
                print(f"Strategy 2: Requested frame {frame_idx}, actual position={actual_pos}")
                
                if actual_pos == frame_idx:
                    ret, frame = temp_cap.read()
                    print(f"Strategy 2 result: ret={ret}, frame is None={frame is None}")
                    if ret and frame is not None:
                        temp_cap.release()
                        print(f"✅ Frame {frame_idx} read successfully with Strategy 2")
                        return frame
                
                # If we got here, Strategy 2 failed - try Strategy 3
                print(f"Strategy 2: Seek failed! Falling back to Strategy 3")
                # Strategy 3: Sequential read (for codecs with broken seeking)
                print(f"Strategy 3: Sequential read from beginning to frame {frame_idx}")
                temp_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                current_frame = None
                for i in range(frame_idx + 1):
                    ret, current_frame = temp_cap.read()
                    if not ret or current_frame is None:
                        print(f"ERROR: Sequential read failed at frame {i}")
                        temp_cap.release()
                        return None
                
                temp_cap.release()
                if current_frame is not None:
                    print(f"✅ Frame {frame_idx} read successfully with Strategy 3 (sequential)")
                    return current_frame
            
            print(f"❌ ERROR: All strategies failed to read frame {frame_idx}")
            return None
            
        except Exception as e:
            print(f"❌ Exception in get_frame for frame {frame_idx}: {e}")
            traceback.print_exc()
            return None
    
    def get_first_frame(self) -> Optional[np.ndarray]:
        """Get first frame of video"""
        return self.get_frame(0)
    
    def get_player(self, player_id: int) -> Optional[PlayerData]:
        """Get player data by ID"""
        return self.players.get(player_id)
    
    def get_all_players(self) -> List[PlayerData]:
        """Get all players - sorted by player_id for consistency"""
        return sorted(list(self.players.values()), key=lambda p: p.player_id)
    
    def remove_player(self, player_id: int) -> bool:
        """
        Remove a player from tracking
        
        Args:
            player_id: ID of player to remove
            
        Returns:
            True if player was removed
        """
        if player_id in self.players:
            self.players[player_id].tracker.reset()
            del self.players[player_id]
            return True
        return False
    
    def reset(self):
        """Reset all trackers"""
        for player in self.players.values():
            player.tracker.reset()
        self.players.clear()
        self.next_player_id = 1
        self.current_frame_idx = 0
        self.tracking_results.clear()
    
    def release(self):
        """Release video capture"""
        if self.video_cap is not None:
            self.video_cap.release()
            self.video_cap = None

