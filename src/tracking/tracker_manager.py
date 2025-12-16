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
                 initial_frame: int, bbox: Tuple[int, int, int, int],
                 original_bbox: Optional[Tuple[int, int, int, int]] = None):
        self.player_id = player_id
        self.name = name
        self.marker_style = marker_style  # 'arrow', 'circle', 'rectangle'
        self.initial_frame = initial_frame  # First frame where player was marked (for tracking start)
        self.bbox = bbox  # Bbox at initial_frame (used for tracking initialization) - this is the PADDED bbox
        self.original_bbox = original_bbox or bbox  # Original bbox BEFORE padding (for accurate marker placement)
        # Learning frames: frames where user marked this player for learning (before tracking starts)
        # Format: {frame_idx: bbox}
        self.learning_frames: Dict[int, Tuple[int, int, int, int]] = {initial_frame: bbox}
        self.original_learning_frames: Dict[int, Tuple[int, int, int, int]] = {initial_frame: original_bbox or bbox}
        self.tracker = PlayerTracker(TrackerType.CSRT)
        self.current_bbox = bbox
        self.current_original_bbox = original_bbox or bbox
        self.tracking_lost = False
        self.color = self._get_default_color()

        # Calculate padding offset (difference between padded and original bbox)
        if original_bbox and original_bbox != bbox:
            orig_x, orig_y, orig_w, orig_h = original_bbox
            pad_x, pad_y, pad_w, pad_h = bbox
            self.padding_offset = (orig_x - pad_x, orig_y - pad_y, pad_w - orig_w, pad_h - orig_h)
        else:
            self.padding_offset = (0, 0, 0, 0)  # No padding
    
    def add_learning_frame(self, frame_idx: int, bbox: Tuple[int, int, int, int],
                          original_bbox: Optional[Tuple[int, int, int, int]] = None):
        """Add a learning frame for this player"""
        self.learning_frames[frame_idx] = bbox
        self.original_learning_frames[frame_idx] = original_bbox or bbox
        # Update initial_frame to the earliest learning frame
        if frame_idx < self.initial_frame:
            self.initial_frame = frame_idx
            self.bbox = bbox
            self.original_bbox = original_bbox or bbox
    
    def _get_default_color(self) -> Tuple[int, int, int]:
        """Get default color based on marker style"""
        color_map = {
            'arrow': (0, 255, 255),        # Yellow
            'circle': (0, 255, 255),       # Yellow (for 3D floor hoop)
            'rectangle': (255, 100, 0),    # Blue (forced in renderer)
            'spotlight': (0, 200, 255),    # Orange
            'spotlight_modern': (200, 255, 255),  # Cyan/white beam
            'outline': (255, 0, 255),      # Magenta
            'nba_iso_ring': (0, 215, 255), # Gold/Cyan glow
            'floating_chevron': (0, 255, 0),  # Bright green for aerial chevron
            'crosshair': (255, 255, 0),       # Neon cyan tactical scope
            'tactical_brackets': (0, 215, 255), # Brackets in same broadcast yellow
            'sonar_ripple': (0, 215, 255)     # Floor ripple in broadcast yellow
        }
        return color_map.get(self.marker_style, (255, 255, 255))


class TrackerManager:
    """Manages multiple player trackers"""

    # Failure detection thresholds
    MAX_SIZE_CHANGE_FACTOR = 0.20   # 20% size change between frames
    MAX_CENTER_SHIFT_FACTOR = 0.10  # 10% center shift relative to box size
    
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
                   initial_frame: int, bbox: Tuple[int, int, int, int],
                   original_bbox: Optional[Tuple[int, int, int, int]] = None) -> int:
        """
        Add a new player to track

        Args:
            name: Player name
            marker_style: Style of marker ('arrow', 'circle', 'rectangle')
            initial_frame: Frame index where player is marked
            bbox: Bounding box (x, y, width, height) - PADDED bbox for tracking
            original_bbox: Original bbox BEFORE padding (for accurate marker placement)

        Returns:
            Player ID
        """
        player_id = self.next_player_id
        self.next_player_id += 1

        player = PlayerData(player_id, name, marker_style, initial_frame, bbox, original_bbox)
        self.players[player_id] = player

        return player_id
    
    def add_learning_frame_to_player(self, player_id: int, frame_idx: int, bbox: Tuple[int, int, int, int],
                                    original_bbox: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Add a learning frame to an existing player

        Args:
            player_id: Player ID
            frame_idx: Frame index where player is marked
            bbox: Bounding box (x, y, width, height) - PADDED bbox for tracking
            original_bbox: Original bbox BEFORE padding (for accurate marker placement)

        Returns:
            True if successful, False if player not found
        """
        if player_id not in self.players:
            return False

        self.players[player_id].add_learning_frame(frame_idx, bbox, original_bbox)
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
            # Debug: Print learning frames info every 100 frames
            if frame_idx is not None and frame_idx % 100 == 0:
                print(f"📊 Frame {frame_idx}: Player {player_id} learning_frames={list(player.learning_frames.keys())}")

            # Check if this frame is a learning frame - if so, reinitialize tracker
            if frame_idx is not None and frame_idx in player.learning_frames:
                # This is a learning frame! Use the exact bbox from learning frame
                learning_bbox = player.learning_frames[frame_idx]

                print(f"🔄 LEARNING FRAME DETECTED! Frame {frame_idx}")
                print(f"   Player {player_id}: Reinitializing tracker with bbox={learning_bbox}")

                # Reinitialize tracker with the correct bbox from learning frame
                player.tracker.init(frame, learning_bbox)
                bbox = learning_bbox

                # Also update current_original_bbox from original_learning_frames
                if frame_idx in player.original_learning_frames:
                    player.current_original_bbox = player.original_learning_frames[frame_idx]
                    print(f"   Updated current_original_bbox to {player.current_original_bbox}")
                else:
                    # Fallback: calculate from padded bbox
                    if player.padding_offset != (0, 0, 0, 0):
                        x, y, w, h = bbox
                        offset_x, offset_y, offset_w, offset_h = player.padding_offset
                        orig_x = x + offset_x
                        orig_y = y + offset_y
                        orig_w = w - offset_w
                        orig_h = h - offset_h
                        player.current_original_bbox = (orig_x, orig_y, orig_w, orig_h)
                    else:
                        player.current_original_bbox = bbox

                player.current_bbox = bbox
                player.tracking_lost = False
            else:
                # Normal tracking update
                bbox = player.tracker.update(frame)
                player.current_bbox = bbox
                player.tracking_lost = (bbox is None)

                # Calculate current_original_bbox from current_bbox using padding offset
                if bbox is not None and player.padding_offset != (0, 0, 0, 0):
                    x, y, w, h = bbox
                    offset_x, offset_y, offset_w, offset_h = player.padding_offset
                    # Reverse the padding: original = padded + offset
                    orig_x = x + offset_x
                    orig_y = y + offset_y
                    orig_w = w - offset_w
                    orig_h = h - offset_h
                    player.current_original_bbox = (orig_x, orig_y, orig_w, orig_h)
                else:
                    player.current_original_bbox = bbox

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

    def generate_tracking_data(self, start_frame: int = 0,
                              end_frame: Optional[int] = None,
                              progress_callback=None) -> Dict[int, Dict[int, Dict[str, any]]]:
        """
        Phase 1 of two-phase tracking: Generate raw tracking data without rendering.

        This function runs tracking on all players and stores coordinates with confidence scores.
        The data can then be reviewed and corrected before final export.

        Args:
            start_frame: Starting frame index (default: 0)
            end_frame: Ending frame index (default: last frame)
            progress_callback: Optional callback(current_frame, total_frames)

        Returns:
            Dictionary with structure:
            {
                player_id: {
                    frame_index: {
                        'bbox': (x, y, w, h),
                        'confidence': float,  # Tracker confidence (0.0-1.0)
                        'is_learning_frame': bool  # True if this was a user-marked frame
                    }
                }
            }

        Example:
            >>> tracker_manager.load_video("video.mp4")
            >>> tracker_manager.add_player("Player 1", "circle", 0, (100, 100, 50, 50))
            >>> data = tracker_manager.generate_tracking_data(0, 100)
            >>> # Review data, identify problematic frames
            >>> # Add corrections via add_learning_frame_to_player()
            >>> # Re-run generate_tracking_data() or just export
        """
        if self.video_path is None:
            raise ValueError("No video loaded. Call load_video() first.")

        if end_frame is None:
            end_frame = self.total_frames - 1

        # Validate frame range
        end_frame = min(end_frame, self.total_frames - 1)
        if start_frame < 0 or start_frame > end_frame:
            raise ValueError(f"Invalid frame range: {start_frame}-{end_frame}")

        print(f"🎯 Phase 1: Generating tracking data for frames {start_frame}-{end_frame}")
        print(f"   Players to track: {len(self.players)}")

        # Open video capture for sequential reading (faster than seeking)
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {self.video_path}")

        # Initialize tracking data structure
        tracking_data: Dict[int, Dict[int, Dict[str, any]]] = {}
        for player_id in self.players:
            tracking_data[player_id] = {}

        # Track last successful bbox per player for failure detection
        previous_bboxes: Dict[int, Optional[Tuple[int, int, int, int]]] = {}

        # Seek to start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        actual_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        # If seeking failed, read sequentially from beginning
        if actual_pos != start_frame:
            print(f"⚠️  Seeking failed (wanted {start_frame}, got {actual_pos}). Reading sequentially...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for i in range(start_frame):
                ret, _ = cap.read()
                if not ret:
                    cap.release()
                    raise RuntimeError(f"Failed to read to start frame {start_frame}")

        # Precompute sorted learning frames for each player (for safe initialization)
        player_learning_frames_sorted: Dict[int, List[int]] = {}
        for player_id, player in self.players.items():
            if player.learning_frames:
                player_learning_frames_sorted[player_id] = sorted(player.learning_frames.keys())
            else:
                # This should normally never happen, but guard against race conditions
                print(f"⚠️  Player {player_id} has no learning_frames; "
                      f"tracking will use initial bbox only and may be less accurate.")
                player_learning_frames_sorted[player_id] = []

        # Main tracking loop
        for current_frame_idx in range(start_frame, end_frame + 1):
            ret, frame = cap.read()
            if not ret or frame is None:
                print(f"⚠️  Failed to read frame {current_frame_idx}, stopping")
                break

            # Update progress
            if progress_callback:
                progress_callback(current_frame_idx - start_frame + 1, end_frame - start_frame + 1)

            # Track each player
            for player_id, player in self.players.items():
                learning_frames_sorted = player_learning_frames_sorted.get(player_id, [])
                has_learning_frames = bool(learning_frames_sorted)
                is_learning_frame = has_learning_frames and current_frame_idx in player.learning_frames

                failure_reason = None

                # Initialize or reinitialize tracker at learning frames
                if current_frame_idx == start_frame or is_learning_frame:
                    init_bbox = None

                    # Use learning frame bbox if available, otherwise use player's initial bbox
                    if is_learning_frame:
                        init_bbox = player.learning_frames[current_frame_idx]
                        print(f"🔄 Frame {current_frame_idx}: Reinitializing player {player_id} with learning frame bbox={init_bbox}")
                    elif current_frame_idx == start_frame:
                        if has_learning_frames:
                            # Prefer the last learning frame at or BEFORE start_frame.
                            # This avoids initializing with a bbox from a FUTURE frame,
                            # which can be very inaccurate for earlier frames.
                            past_or_equal = [f for f in learning_frames_sorted if f <= start_frame]
                            if past_or_equal:
                                closest_frame = max(past_or_equal)
                                init_bbox = player.learning_frames[closest_frame]
                                print(
                                    f"🔄 Frame {current_frame_idx}: Initializing player {player_id} "
                                    f"with latest learning frame <= start (frame {closest_frame}) "
                                    f"bbox={init_bbox}"
                                )
                            else:
                                # No learning frames before start_frame – safest is to wait until
                                # we actually reach the first learning frame instead of using
                                # a bbox from the future.
                                first_future = learning_frames_sorted[0]
                                print(
                                    f"⏸ Frame {current_frame_idx}: No learning frame before start for "
                                    f"player {player_id} (first at frame {first_future}); "
                                    f"skipping initialization until then."
                                )
                                init_bbox = None
                        else:
                            # Extremely defensive fallback: no learning_frames at all.
                            # Use player's initial bbox if available, but warn loudly.
                            init_bbox = getattr(player, "bbox", None)
                            print(
                                f"⚠️  Frame {current_frame_idx}: Player {player_id} has NO learning_frames; "
                                f"falling back to player.bbox={init_bbox}"
                            )

                    if init_bbox is not None:
                        player.tracker.init_tracker(frame, init_bbox)
                        bbox = init_bbox
                        success = True
                        # Learning / initialization frames get full confidence
                        confidence = 1.0
                    else:
                        # We deliberately chose not to initialize yet (e.g. before first learning frame)
                        bbox = None
                        success = False
                        confidence = 0.0
                else:
                    # Normal tracking update
                    bbox = player.tracker.update(frame)
                    success = (bbox is not None)

                    # Calculate confidence based on tracker success
                    # TODO: Improve confidence calculation (can use IoU with previous frame, tracker score, etc.)
                    confidence = 0.8 if success else 0.0

                    # External failure checks using previous bbox
                    prev_bbox = previous_bboxes.get(player_id)
                    if success and bbox is not None and prev_bbox is not None:
                        x, y, w, h = bbox
                        px, py, pw, ph = prev_bbox

                        # Guard against zero area
                        if pw > 0 and ph > 0:
                            size_change = abs((w * h) - (pw * ph)) / (pw * ph)
                        else:
                            size_change = 0.0

                        if size_change > self.MAX_SIZE_CHANGE_FACTOR:
                            failure_reason = 'SIZE_CHANGE'
                            success = False
                            confidence = 0.0
                        else:
                            # Center shift relative to box size
                            center_shift = ((x + w / 2) - (px + pw / 2)) ** 2 + ((y + h / 2) - (py + ph / 2)) ** 2
                            avg_dimension = max((pw + ph) / 2, 1e-3)
                            relative_shift = (center_shift ** 0.5) / avg_dimension

                            if relative_shift > self.MAX_CENTER_SHIFT_FACTOR:
                                failure_reason = 'POSITION_SHIFT'
                                success = False
                                confidence = 0.0

                # Store tracking data
                if success and bbox is not None:
                    tracking_data[player_id][current_frame_idx] = {
                        'bbox': bbox,
                        'confidence': confidence,
                        'is_learning_frame': is_learning_frame
                    }

                    # Also update tracking_results for compatibility with existing export code
                    if player_id not in self.tracking_results:
                        self.tracking_results[player_id] = {}
                    self.tracking_results[player_id][current_frame_idx] = bbox

                    # Remember last successful bbox for next frame checks
                    previous_bboxes[player_id] = bbox
                else:
                    # Track was lost - store None to indicate gap
                    tracking_data[player_id][current_frame_idx] = {
                        'bbox': None,
                        'confidence': 0.0,
                        'is_learning_frame': is_learning_frame,
                        'failure_reason': failure_reason if failure_reason else 'TRACKER_LOST'
                    }

                    if player_id not in self.tracking_results:
                        self.tracking_results[player_id] = {}
                    self.tracking_results[player_id][current_frame_idx] = None

            # Log progress every 50 frames
            if current_frame_idx % 50 == 0:
                print(f"  ⚡ Processed {current_frame_idx - start_frame + 1}/{end_frame - start_frame + 1} frames")

        cap.release()

        # Summary statistics
        print(f"\n✅ Phase 1 Complete: Generated tracking data")
        for player_id, player in self.players.items():
            frames_tracked = len([f for f in tracking_data[player_id] if tracking_data[player_id][f]['bbox'] is not None])
            frames_lost = len([f for f in tracking_data[player_id] if tracking_data[player_id][f]['bbox'] is None])
            learning_frames_count = len([f for f in tracking_data[player_id] if tracking_data[player_id][f]['is_learning_frame']])
            avg_confidence = sum([tracking_data[player_id][f]['confidence'] for f in tracking_data[player_id]]) / len(tracking_data[player_id]) if tracking_data[player_id] else 0.0

            print(f"   Player {player_id} ({player.name}):")
            print(f"      Frames tracked: {frames_tracked}")
            print(f"      Frames lost: {frames_lost}")
            print(f"      Learning frames used: {learning_frames_count}")
            print(f"      Average confidence: {avg_confidence:.2f}")

        print(f"\n💡 Next steps:")
        print(f"   1. Review tracking data to identify problematic frames")
        print(f"   2. Add corrections with add_learning_frame_to_player()")
        print(f"   3. Re-run generate_tracking_data() or export directly")

        return tracking_data
