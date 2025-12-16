"""
Video Exporter - Exports video with tracking overlays using FFmpeg
"""
import cv2
import numpy as np
import subprocess
import os
import tempfile
import traceback
from typing import Optional, List
from pathlib import Path
from ..tracking.tracker_manager import TrackerManager
from .overlay_renderer import OverlayRenderer


class VideoExporter:
    """Handles video export with tracking overlays"""
    
    def __init__(self, tracker_manager: TrackerManager):
        self.tracker_manager = tracker_manager
        self.overlay_renderer = OverlayRenderer()
        self.temp_dir = None

    def export_tracked_video(self, original_video_path: str, tracking_data: dict,
                             output_path: str,
                             progress_callback=None,
                             tracking_start_frame: Optional[int] = None,
                             tracking_end_frame: Optional[int] = None) -> bool:
        """
        Render a tracked video from raw tracking_data and mux audio from the original.
        tracking_data format: {player_id: {frame_idx: {'bbox': (x,y,w,h) or None, ...}}}
        """
        try:
            cap = cv2.VideoCapture(original_video_path)
            if not cap.isOpened():
                print("❌ ERROR: Could not open source video for export.")
                return False

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

            if width <= 0 or height <= 0 or total_frames <= 0:
                print(f"❌ Invalid video properties: frames={total_frames}, size={width}x{height}")
                cap.release()
                return False

            # Prepare temp file for video without audio
            self.temp_dir = tempfile.mkdtemp()
            temp_video = os.path.join(self.temp_dir, 'tracked_no_audio.mp4')

            # Prefer H.264 then fallback
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            writer = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
            if not writer.isOpened():
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

            if not writer.isOpened():
                print("❌ ERROR: Could not open VideoWriter for tracked export.")
                cap.release()
                return False

            players = self.tracker_manager.get_all_players()

            frame_idx = 0
            frames_written = 0
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                if progress_callback and total_frames > 0:
                    progress_callback(frame_idx + 1, total_frames)

                # Update each player's current bbox from tracking_data
                for player in players:
                    frame_data = tracking_data.get(player.player_id, {}).get(frame_idx)
                    bbox = None
                    if frame_data:
                        bbox = frame_data.get('bbox')

                    player.current_bbox = bbox
                    if bbox is not None and hasattr(player, 'padding_offset') and player.padding_offset != (0, 0, 0, 0):
                        x, y, w, h = bbox
                        offset_x, offset_y, offset_w, offset_h = player.padding_offset
                        player.current_original_bbox = (x + offset_x, y + offset_y, w - offset_w, h - offset_h)
                    else:
                        player.current_original_bbox = bbox

                frame_with_overlay = self.overlay_renderer.draw_all_markers(
                    frame,
                    players,
                    frame_idx=frame_idx,
                    tracking_start_frame=tracking_start_frame,
                    tracking_end_frame=tracking_end_frame
                )

                writer.write(frame_with_overlay)
                frames_written += 1
                frame_idx += 1

            cap.release()
            writer.release()

            if frames_written == 0:
                print("❌ ERROR: No frames written during tracked export.")
                self._cleanup_temp_files()
                return False

            # Mux original audio back
            success = self._add_audio_with_ffmpeg(original_video_path, temp_video, output_path)
            self._cleanup_temp_files()
            return success

        except Exception as e:
            print(f"Error in export_tracked_video: {e}")
            traceback.print_exc()
            self._cleanup_temp_files()
            return False
    
    def export_video(self, input_path: str, output_path: str,
                    progress_callback=None,
                    tracking_start_frame: Optional[int] = None,
                    tracking_end_frame: Optional[int] = None) -> bool:
        """
        Export video with tracking overlays using FAST VideoWriter method
        
        Args:
            input_path: Path to input video
            output_path: Path to output video
            progress_callback: Optional callback function(frame_idx, total_frames)
            tracking_start_frame: Start frame for tracking (None = from beginning)
            tracking_end_frame: End frame for tracking (None = to end)
            
        Returns:
            True if export successful
        """
        try:
            # Get video properties from tracker_manager (more reliable)
            total_frames = self.tracker_manager.total_frames
            fps = self.tracker_manager.fps
            width = self.tracker_manager.frame_width
            height = self.tracker_manager.frame_height
            
            if total_frames <= 0 or width <= 0 or height <= 0:
                print(f"Error: Invalid video properties: frames={total_frames}, size={width}x{height}")
                return False
            
            print(f"⚡ ULTRA-FAST Export: {total_frames} frames at {fps} FPS ({width}x{height})")
            
            # Create temporary video file (no audio yet)
            self.temp_dir = tempfile.mkdtemp()
            temp_video = os.path.join(self.temp_dir, 'video_no_audio.mp4')
            
            # Try hardware-accelerated H.264 first (fastest), fallback to mp4v
            # H264 is MUCH faster and better quality than mp4v
            try:
                fourcc = cv2.VideoWriter_fourcc(*'H264')  # Hardware H.264 (fastest!)
                video_writer = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
                if not video_writer.isOpened():
                    # Fallback to avc1 (another H.264 variant)
                    fourcc = cv2.VideoWriter_fourcc(*'avc1')
                    video_writer = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
                print("✅ Using H.264 codec (hardware accelerated)")
            except:
                # Last fallback
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
                print("⚠️ Using mp4v codec (slower)")
            
            if not video_writer.isOpened():
                print("❌ ERROR: Could not open VideoWriter!")
                return False
            
            # ULTRA-FAST: Open video once and read sequentially (no seeking!)
            print("Processing frames (ULTRA-FAST sequential read)...")
            frames_written = 0
            
            # Open video for sequential reading (MUCH faster than seeking!)
            input_cap = cv2.VideoCapture(input_path)
            if not input_cap.isOpened():
                print("❌ ERROR: Could not open input video!")
                return False
            
            # Read and process ALL frames sequentially
            frame_idx = 0
            while True:
                ret, frame = input_cap.read()
                if not ret or frame is None:
                    break
                
                if progress_callback:
                    progress_callback(frame_idx + 1, total_frames)
                
                # Get stored tracking results for this frame
                players = self.tracker_manager.get_all_players()
                for player in players:
                    stored_bbox = self.tracker_manager.get_bbox_at_frame(
                        player.player_id, frame_idx
                    )
                    # CRITICAL: Always update current_bbox - set to None if no tracking data for this frame
                    # This prevents showing bbox from a different frame
                    player.current_bbox = stored_bbox

                    # Calculate current_original_bbox from stored_bbox using padding offset
                    if stored_bbox is not None and hasattr(player, 'padding_offset') and player.padding_offset != (0, 0, 0, 0):
                        x, y, w, h = stored_bbox
                        offset_x, offset_y, offset_w, offset_h = player.padding_offset
                        # Reverse the padding: original = padded + offset
                        orig_x = x + offset_x
                        orig_y = y + offset_y
                        orig_w = w - offset_w
                        orig_h = h - offset_h
                        player.current_original_bbox = (orig_x, orig_y, orig_w, orig_h)
                    else:
                        player.current_original_bbox = stored_bbox

                    if stored_bbox is None:
                        # Log missing bbox for debugging
                        if frame_idx % 30 == 0:  # Log every 30 frames
                            print(f"[Export] WARNING: No bbox for player {player.player_id} (name: {player.name}) at frame {frame_idx}")
                
                # Draw overlays - verify player data
                if frame_idx == 0:  # Log first frame for debugging
                    print(f"[Export] Frame 0: Drawing {len(players)} players")
                    for player in players:
                        print(f"  Player ID: {player.player_id}, Name: {player.name}, Bbox: {player.current_bbox}, Style: {player.marker_style}")
                
                # Draw markers only if frame is in tracking range
                frame_with_overlay = self.overlay_renderer.draw_all_markers(
                    frame, 
                    players,
                    frame_idx=frame_idx,
                    tracking_start_frame=tracking_start_frame,
                    tracking_end_frame=tracking_end_frame
                )
                
                # Write directly to video file (FAST!)
                video_writer.write(frame_with_overlay)
                frames_written += 1
                
                # Progress logging
                if frame_idx % 50 == 0:
                    print(f"  ⚡ {frame_idx}/{total_frames} frames processed")
                
                frame_idx += 1
            
            input_cap.release()
            
            # Release video writer
            video_writer.release()
            
            print(f"✅ Processed {frames_written}/{total_frames} frames")
            
            if frames_written == 0:
                print("❌ ERROR: No frames were written!")
                return False
            
            # Add audio from original video using FFmpeg (fast operation)
            print("Adding audio from original video...")
            success = self._add_audio_with_ffmpeg(input_path, temp_video, output_path)
            
            # Cleanup
            self._cleanup_temp_files()
            
            if success:
                print(f"✅ Video exported successfully to: {output_path}")
            
            return success
            
        except Exception as e:
            print(f"Error exporting video: {e}")
            traceback.print_exc()
            self._cleanup_temp_files()
            return False
    
    def _add_audio_with_ffmpeg(self, input_video: str, video_no_audio: str,
                               output_path: str) -> bool:
        """
        Add audio from original video to processed video using FFmpeg (FAST!)

        Args:
            input_video: Original video with audio
            video_no_audio: Processed video without audio
            output_path: Final output path

        Returns:
            True if successful
        """
        try:
            # Strategy 1: Try to copy both video and audio (fastest - no re-encoding at all!)
            print("Running FFmpeg to add audio (Strategy 1: copy both streams)...")
            cmd = [
                'ffmpeg', '-y',
                '-i', video_no_audio,  # Video input (no audio)
                '-i', input_video,     # Audio source
                '-c:v', 'copy',        # Copy video stream (no re-encoding!)
                '-c:a', 'aac',         # Re-encode audio to AAC for compatibility
                '-b:a', '192k',        # High quality audio
                '-map', '0:v:0',       # Use video from first input
                '-map', '1:a:0?',      # Use audio from second input (optional - won't fail if no audio)
                '-shortest',           # Match shortest stream duration
                output_path
            ]

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            if result.returncode == 0:
                print("✅ Successfully added audio using stream copy")
                return True

            print(f"⚠️ Strategy 1 failed: {result.stderr}")

            # Strategy 2: Re-encode video but keep audio quality
            print("Running FFmpeg to add audio (Strategy 2: re-encode video)...")
            cmd2 = [
                'ffmpeg', '-y',
                '-i', video_no_audio,  # Video input (no audio)
                '-i', input_video,     # Audio source
                '-c:v', 'libx264',     # Re-encode video with libx264 for compatibility
                '-preset', 'fast',     # Fast encoding preset (better quality than ultrafast)
                '-crf', '18',          # High quality
                '-c:a', 'aac',         # Re-encode audio to AAC
                '-b:a', '192k',        # High quality audio
                '-map', '0:v:0',       # Use video from first input
                '-map', '1:a:0?',      # Use audio from second input (optional)
                '-shortest',           # Match shortest stream duration
                output_path
            ]

            result2 = subprocess.run(
                cmd2,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            if result2.returncode == 0:
                print("✅ Successfully added audio with re-encoding")
                return True

            print(f"⚠️ Strategy 2 failed: {result2.stderr}")

            # Strategy 3: Just copy video without audio as last resort
            print("❌ Audio merge failed, copying video without audio...")
            import shutil
            shutil.copy2(video_no_audio, output_path)
            print("⚠️ WARNING: Video exported WITHOUT audio!")
            return True

        except FileNotFoundError:
            print("❌ FFmpeg not found! Copying video without audio...")
            import shutil
            shutil.copy2(video_no_audio, output_path)
            print("⚠️ WARNING: Install FFmpeg to enable audio in exported videos!")
            return True
        except Exception as e:
            print(f"Error adding audio: {e}")
            traceback.print_exc()
            return False
    
    def _export_with_ffmpeg(self, input_path: str, output_path: str,
                           frames_dir: str, fps: float, width: int, height: int,
                           codec: str, bitrate: int, total_frames: int) -> bool:
        """
        Export video using FFmpeg with original quality settings
        
        Args:
            input_path: Original video path (for audio)
            output_path: Output video path
            frames_dir: Directory with processed frames
            fps: Frame rate
            width: Video width
            height: Video height
            codec: Video codec
            bitrate: Video bitrate
            total_frames: Total number of frames
            
        Returns:
            True if successful
        """
        try:
            # Determine codec for output
            if codec.lower() in ['h264', 'avc1']:
                video_codec = 'libx264'
            elif codec.lower() in ['h265', 'hevc']:
                video_codec = 'libx265'
            else:
                video_codec = 'libx264'  # Default
            
            # FFmpeg command to combine frames with audio
            # First, create video from frames
            frames_pattern = os.path.join(frames_dir, 'frame_%06d.png')
            
            # Temporary video file (video only)
            temp_video = os.path.join(self.temp_dir, 'temp_video.mp4')
            
            # Create video from frames with high quality settings
            # Use lossless or near-lossless encoding to preserve quality
            print(f"Creating video from frames at {fps} FPS...")
            cmd1 = [
                'ffmpeg', '-y',
                '-framerate', str(fps),  # Input framerate
                '-i', frames_pattern,
                '-c:v', video_codec,
                '-preset', 'fast',  # Faster preset for better compatibility
                '-crf', '18',  # High quality CRF (lower = better quality)
                '-pix_fmt', 'yuv420p',
                '-vf', f'scale={width}:{height}',  # Ensure correct resolution
                '-r', str(fps),  # Output framerate
                temp_video
            ]
            
            print(f"FFmpeg command: {' '.join(cmd1)}")
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            result1 = subprocess.run(cmd1, capture_output=True, text=True, 
                                    creationflags=creationflags)
            if result1.returncode != 0:
                print(f"FFmpeg error (video): {result1.stderr}")
                return False
            print("Video created successfully")
            
            # Combine video with original audio
            print("Combining video with audio...")
            cmd2 = [
                'ffmpeg', '-y',
                '-i', temp_video,
                '-i', input_path,
                '-c:v', 'copy',  # Copy video (don't re-encode)
                '-c:a', 'aac',  # Encode audio to AAC for compatibility
                '-b:a', '192k',  # Audio bitrate
                '-map', '0:v:0',  # Video from first input
                '-map', '1:a:0?',  # Audio from second input (if exists)
                '-shortest',  # Use shortest stream
                output_path
            ]
            
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            result2 = subprocess.run(cmd2, capture_output=True, text=True,
                                    creationflags=creationflags)
            if result2.returncode != 0:
                print(f"FFmpeg warning (combine with audio): {result2.stderr}")
                print("Trying without audio...")
                # Try without audio if audio copy fails
                cmd2_no_audio = [
                    'ffmpeg', '-y',
                    '-i', temp_video,
                    '-c:v', 'copy',
                    output_path
                ]
                result2 = subprocess.run(cmd2_no_audio, capture_output=True, text=True,
                                        creationflags=creationflags)
                if result2.returncode != 0:
                    print(f"FFmpeg error (no audio): {result2.stderr}")
                    return False
                print("Video exported without audio")
            else:
                print("Video exported with audio successfully")
            
            return True
            
        except FileNotFoundError:
            print("FFmpeg not found. Please install FFmpeg and add it to PATH.")
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"Error in FFmpeg export: {e}")
            traceback.print_exc()
            return False
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Error cleaning up temp files: {e}")
