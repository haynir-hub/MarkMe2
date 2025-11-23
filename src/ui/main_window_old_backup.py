"""
Main Window - Main application window
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QListWidget,
                             QListWidgetItem, QProgressBar, QMessageBox,
                             QGroupBox, QSizePolicy, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor
import cv2
import numpy as np
from pathlib import Path
import os

from ..tracking.tracker_manager import TrackerManager
from ..render.video_exporter import VideoExporter
from .video_canvas import VideoCanvas
from .player_selector import PlayerSelector


class ExportThread(QThread):
    """Thread for running export process"""
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, tracker_manager: TrackerManager, video_path: str, output_path: str):
        super().__init__()
        self.tracker_manager = tracker_manager
        self.video_path = video_path
        self.output_path = output_path
        self.cancelled = False
    
    def run(self):
        """Run export process"""
        try:
            from ..render.video_exporter import VideoExporter
            exporter = VideoExporter(self.tracker_manager)
            
            def progress_callback(current: int, total: int):
                self.progress.emit(current, total)
            
            success = exporter.export_video(
                self.video_path,
                self.output_path,
                progress_callback
            )
            
            if success:
                self.finished.emit(True, "Export completed successfully")
            else:
                self.finished.emit(False, "Export failed")
        except Exception as e:
            import traceback
            error_msg = f"Error during export: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.finished.emit(False, f"Error during export: {str(e)}")
    
    def cancel(self):
        """Cancel export process"""
        self.cancelled = True


class TrackingThread(QThread):
    """Thread for running tracking process"""
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, tracker_manager: TrackerManager, video_path: str):
        super().__init__()
        self.tracker_manager = tracker_manager
        self.video_path = video_path
        self.cancelled = False
    
    def run(self):
        """Run tracking process"""
        cap = None
        try:
            players = self.tracker_manager.get_all_players()
            if not players:
                self.finished.emit(False, "No players to track")
                return
            
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.finished.emit(False, "Failed to open video")
                return
            
            total_frames = self.tracker_manager.total_frames
            if total_frames <= 0:
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            if total_frames <= 0:
                self.finished.emit(False, "Invalid frame count")
                cap.release()
                return
            
            # Start from beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_idx = 0
            
            while frame_idx < total_frames:
                if self.cancelled:
                    break
                
                ret, frame = cap.read()
                if not ret or frame is None:
                    break
                
                for player in players:
                    if (not player.tracker.is_initialized) and frame_idx >= player.initial_frame:
                        print(f"Initializing tracker for player {player.player_id} at frame {frame_idx}")
                        init_success = player.tracker.init_tracker(frame, player.bbox)
                        player.tracking_lost = not init_success
                        if init_success:
                            player.current_bbox = player.bbox
                            if player.player_id not in self.tracker_manager.tracking_results:
                                self.tracker_manager.tracking_results[player.player_id] = {}
                            self.tracker_manager.tracking_results[player.player_id][frame_idx] = player.bbox
                            print(f"Player {player.player_id} initialized at frame {frame_idx}, bbox={player.bbox}")
                        else:
                            print(f"ERROR: Failed to initialize tracker for player {player.player_id}")
                
                # Update initialized trackers
                for player in players:
                    if not player.tracker.is_initialized:
                        continue
                    
                    if frame_idx > player.initial_frame:
                        bbox = player.tracker.update(frame)
                        player.current_bbox = bbox
                        player.tracking_lost = (bbox is None)
                        if frame_idx % 10 == 0:  # Log every 10 frames
                            print(f"Frame {frame_idx}: Player {player.player_id} bbox={bbox}")
                    else:
                        bbox = player.current_bbox
                    
                    if player.player_id not in self.tracker_manager.tracking_results:
                        self.tracker_manager.tracking_results[player.player_id] = {}
                    self.tracker_manager.tracking_results[player.player_id][frame_idx] = bbox
                
                self.progress.emit(frame_idx + 1, total_frames)
                frame_idx += 1
            
            if cap:
                cap.release()
            
            if frame_idx == 0:
                self.finished.emit(False, "Failed to process video frames")
            else:
                # Debug: Check tracking results
                print(f"\n=== Tracking Complete ===")
                for player in players:
                    results_count = len(self.tracker_manager.tracking_results.get(player.player_id, {}))
                    print(f"Player {player.player_id}: {results_count} frames tracked")
                    # Show first few and last few
                    if player.player_id in self.tracker_manager.tracking_results:
                        frames = sorted(self.tracker_manager.tracking_results[player.player_id].keys())
                        if len(frames) > 0:
                            print(f"  First 3 frames: {frames[:3]}")
                            print(f"  Last 3 frames: {frames[-3:]}")
                            # Show some bboxes
                            print(f"  Frame 0 bbox: {self.tracker_manager.tracking_results[player.player_id].get(0)}")
                            if len(frames) > 10:
                                print(f"  Frame 10 bbox: {self.tracker_manager.tracking_results[player.player_id].get(10)}")
                            if len(frames) > 20:
                                print(f"  Frame 20 bbox: {self.tracker_manager.tracking_results[player.player_id].get(20)}")
                print(f"=========================\n")
                
                self.finished.emit(True, "Tracking completed successfully")
        
        except Exception as e:
            import traceback
            error_msg = f"Error during tracking: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            if cap:
                cap.release()
            self.finished.emit(False, f"Error during tracking: {str(e)}")
    
    def cancel(self):
        """Cancel tracking process"""
        self.cancelled = True


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Markme - Player Tracking")
        self.setMinimumSize(1200, 800)
        
        # State
        self.video_path = None
        self.tracker_manager = TrackerManager()
        self.video_exporter = None
        self.tracking_thread = None
        self.export_thread = None
        self.current_frame_idx = 0
        self._waiting_for_bbox = False
        
        # UI Setup
        self._setup_ui()
        
        # Timer for preview updates
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self._update_preview)
    
    def _setup_ui(self):
        """Setup user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - Controls
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Video preview
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 3)
    
    def _create_left_panel(self) -> QWidget:
        """Create left control panel"""
        panel = QWidget()
        panel.setMaximumWidth(300)
        layout = QVBoxLayout()
        
        # Load Video
        load_group = QGroupBox("Video")
        load_layout = QVBoxLayout()
        self.load_btn = QPushButton("Load Video")
        self.load_btn.clicked.connect(self._load_video)
        load_layout.addWidget(self.load_btn)
        self.video_info_label = QLabel("No video loaded")
        self.video_info_label.setWordWrap(True)
        load_layout.addWidget(self.video_info_label)
        load_group.setLayout(load_layout)
        layout.addWidget(load_group)
        
        # Players
        players_group = QGroupBox("Players")
        players_layout = QVBoxLayout()
        self.players_list = QListWidget()
        self.players_list.itemClicked.connect(self._on_player_selected)
        players_layout.addWidget(self.players_list)
        
        self.add_player_btn = QPushButton("Add Player Marker")
        self.add_player_btn.clicked.connect(self._add_player_marker)
        self.add_player_btn.setEnabled(False)
        players_layout.addWidget(self.add_player_btn)
        
        self.remove_player_btn = QPushButton("Remove Selected")
        self.remove_player_btn.clicked.connect(self._remove_player)
        self.remove_player_btn.setEnabled(False)
        players_layout.addWidget(self.remove_player_btn)
        
        players_group.setLayout(players_layout)
        layout.addWidget(players_group)
        
        # Tracking
        tracking_group = QGroupBox("Tracking")
        tracking_layout = QVBoxLayout()
        self.start_tracking_btn = QPushButton("Start Tracking")
        self.start_tracking_btn.clicked.connect(self._start_tracking)
        self.start_tracking_btn.setEnabled(False)
        tracking_layout.addWidget(self.start_tracking_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        tracking_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        tracking_layout.addWidget(self.status_label)
        
        tracking_group.setLayout(tracking_layout)
        layout.addWidget(tracking_group)
        
        # Export
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout()
        self.export_btn = QPushButton("Export Video")
        self.export_btn.clicked.connect(self._export_video)
        self.export_btn.setEnabled(False)
        export_layout.addWidget(self.export_btn)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right video preview panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Video canvas
        self.video_canvas = VideoCanvas()
        self.video_canvas.bbox_selected.connect(self._on_bbox_selected)
        layout.addWidget(self.video_canvas)
        
        # Frame controls
        frame_controls = QHBoxLayout()
        self.prev_frame_btn = QPushButton("◀ Previous Frame")
        self.prev_frame_btn.clicked.connect(self._prev_frame)
        self.prev_frame_btn.setEnabled(False)
        frame_controls.addWidget(self.prev_frame_btn)
        
        self.frame_label = QLabel("Frame: 0 / 0")
        frame_controls.addWidget(self.frame_label)
        
        self.next_frame_btn = QPushButton("Next Frame ▶")
        self.next_frame_btn.clicked.connect(self._next_frame)
        self.next_frame_btn.setEnabled(False)
        frame_controls.addWidget(self.next_frame_btn)
        
        layout.addLayout(frame_controls)
        panel.setLayout(layout)
        return panel
    
    def _load_video(self):
        """Load video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.mov *.mkv *.webm);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Probe video metadata
        metadata = self.tracker_manager.probe_video(file_path)
        if metadata is None:
            QMessageBox.warning(self, "Error", "Failed to read video metadata")
            return
        
        width = int(metadata.get("width", 0))
        height = int(metadata.get("height", 0))
        fps = metadata.get("fps", 30.0)
        duration = metadata.get("duration", 0.0)
        frame_count = int(metadata.get("frame_count", 0))
        
        # Validate duration
        if duration > 60:
            QMessageBox.warning(
                self,
                "Error",
                f"Video duration ({duration:.1f}s) exceeds maximum (60s)"
            )
            return
        
        if frame_count == 0:
            QMessageBox.warning(self, "Error", "Video contains no frames")
            return
        
        # Check resolution (should support up to 4K)
        if width * height > 3840 * 2160:
            QMessageBox.warning(
                self,
                "Warning",
                "Video resolution exceeds 4K. Performance may be affected."
            )
        
        # Load video
        self.video_path = file_path
        self.tracker_manager.reset()
        if not self.tracker_manager.load_video(file_path, metadata):
            QMessageBox.warning(self, "Error", "Failed to load video")
            return
        
        # Display first frame
        first_frame = self.tracker_manager.get_first_frame()
        if first_frame is not None:
            self.video_canvas.set_frame(first_frame)
            self.current_frame_idx = 0
            self._update_frame_info()
        
        # Update UI
        file_name = Path(file_path).name
        self.video_info_label.setText(
            f"File: {file_name}\n"
            f"Resolution: {width}x{height}\n"
            f"FPS: {fps:.2f}\n"
            f"Duration: {duration:.1f}s"
        )
        
        self.add_player_btn.setEnabled(True)
        self.video_canvas.clear_bboxes()
        self.players_list.clear()
        
        # Enable navigation buttons
        self.prev_frame_btn.setEnabled(self.current_frame_idx > 0)
        self.next_frame_btn.setEnabled(self.tracker_manager.total_frames > 1)
        self._update_frame_navigation_buttons()
    
    def _add_player_marker(self):
        """Add a new player marker"""
        print("_add_player_marker called")
        if not self.video_path:
            print("No video loaded")
            QMessageBox.warning(self, "Warning", "Please load a video first.")
            return
        
        # User needs to draw bounding box first
        self.status_label.setText("Draw bounding box on video")
        self.status_label.setStyleSheet("color: yellow;")
        self._waiting_for_bbox = True
        print("Waiting for bbox draw...")
    
    def _on_bbox_selected(self, x: int, y: int, w: int, h: int):
        """Handle bounding box selection"""
        print(f"_on_bbox_selected called: bbox=({x}, {y}, {w}, {h})")
        try:
            # Validate bbox
            if w <= 0 or h <= 0:
                print(f"Invalid bbox size: {w}x{h}")
                QMessageBox.warning(self, "Error", "Invalid bounding box size.")
                self._waiting_for_bbox = False
                self.status_label.setText("Ready")
                self.status_label.setStyleSheet("")
                return
            
            # Show selector dialog
            selector = PlayerSelector(self)
            
            def on_confirmed(name: str, style: str):
                try:
                    # Add player to tracker
                    player_id = self.tracker_manager.add_player(
                        name, style, self.current_frame_idx, (x, y, w, h)
                    )
                    
                    # Get color for style
                    color_map = {
                        'arrow': (0, 255, 255),      # Yellow
                        'circle': (255, 255, 0),     # Cyan
                        'rectangle': (0, 0, 255)     # Red
                    }
                    color = color_map.get(style, (255, 255, 255))
                    
                    # Add to canvas
                    self.video_canvas.add_bbox(x, y, w, h, name, style, color)
                    
                    # Add to list
                    item = QListWidgetItem(f"{name} ({style})")
                    item.setData(Qt.ItemDataRole.UserRole, player_id)
                    self.players_list.addItem(item)
                    
                    # Update UI
                    self.start_tracking_btn.setEnabled(True)
                    self.remove_player_btn.setEnabled(True)
                    self.status_label.setText("")
                    self.status_label.setStyleSheet("")
                    self._waiting_for_bbox = False
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to add player: {str(e)}")
                    self._waiting_for_bbox = False
            
            selector.player_confirmed.connect(on_confirmed)
            result = selector.exec()
            
            if result != QDialog.DialogCode.Accepted:
                self._waiting_for_bbox = False
                self.status_label.setText("")
                self.status_label.setStyleSheet("")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error selecting bounding box: {str(e)}")
            self._waiting_for_bbox = False
            self.status_label.setText("")
            self.status_label.setStyleSheet("")
    
    def _on_player_selected(self, item: QListWidgetItem):
        """Handle player selection in list"""
        self.remove_player_btn.setEnabled(True)
    
    def _remove_player(self):
        """Remove selected player"""
        current_item = self.players_list.currentItem()
        if not current_item:
            return
        
        player_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Remove from tracker
        self.tracker_manager.remove_player(player_id)
        
        # Remove from list
        row = self.players_list.row(current_item)
        self.players_list.takeItem(row)
        
        # Remove from canvas
        self.video_canvas.remove_bbox(row)
        
        # Update UI
        if self.players_list.count() == 0:
            self.remove_player_btn.setEnabled(False)
            self.start_tracking_btn.setEnabled(False)
    
    def _prev_frame(self):
        """Go to previous frame"""
        try:
            if self.video_path and self.current_frame_idx > 0:
                self.current_frame_idx -= 1
                self._show_frame(self.current_frame_idx)
                # Stop auto-preview if manually navigating
                if self.preview_timer.isActive():
                    self.preview_timer.stop()
                # Update button states
                self._update_frame_navigation_buttons()
        except Exception as e:
            print(f"❌ Error going to previous frame: {e}")
            import traceback
            traceback.print_exc()
    
    def _next_frame(self):
        """Go to next frame"""
        try:
            if self.video_path and self.tracker_manager.total_frames > 0:
                if self.current_frame_idx < self.tracker_manager.total_frames - 1:
                    self.current_frame_idx += 1
                    self._show_frame(self.current_frame_idx)
                # Stop auto-preview if manually navigating
                if self.preview_timer.isActive():
                    self.preview_timer.stop()
                # Update button states
                self._update_frame_navigation_buttons()
        except Exception as e:
            print(f"❌ Error going to next frame: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_frame_navigation_buttons(self):
        """Update frame navigation button states"""
        try:
            if not self.video_path or self.tracker_manager.total_frames == 0:
                self.prev_frame_btn.setEnabled(False)
                self.next_frame_btn.setEnabled(False)
                return
            
            total = self.tracker_manager.total_frames
            if total > 0:
                self.prev_frame_btn.setEnabled(self.current_frame_idx > 0)
                self.next_frame_btn.setEnabled(self.current_frame_idx < total - 1)
            else:
                self.prev_frame_btn.setEnabled(False)
                self.next_frame_btn.setEnabled(False)
        except Exception as e:
            print(f"Error updating navigation buttons: {e}")
            self.prev_frame_btn.setEnabled(False)
            self.next_frame_btn.setEnabled(False)
    
    def _show_frame(self, frame_idx: int):
        """Show specific frame"""
        try:
            if frame_idx < 0 or (self.tracker_manager.total_frames > 0 and 
                               frame_idx >= self.tracker_manager.total_frames):
                print(f"Frame index out of bounds: {frame_idx}")
                return
            
            frame = self.tracker_manager.get_frame(frame_idx)
            if frame is None:
                print(f"❌ ERROR: Could not load frame {frame_idx}")
                return
            
            # If tracking is complete, show with overlays
            if self.export_btn.isEnabled() and len(self.tracker_manager.players) > 0:
                from ..render.overlay_renderer import OverlayRenderer
                renderer = OverlayRenderer()
                players = self.tracker_manager.get_all_players()
                
                print(f"_show_frame: Displaying frame {frame_idx} with {len(players)} players")
                
                # Update current_bbox from stored tracking results
                for player in players:
                    stored_bbox = self.tracker_manager.get_bbox_at_frame(
                        player.player_id, frame_idx
                    )
                    print(f"Player {player.player_id}: stored_bbox at frame {frame_idx} = {stored_bbox}")
                    if stored_bbox is not None:
                        player.current_bbox = stored_bbox
                    else:
                        print(f"WARNING: No bbox found for player {player.player_id} at frame {frame_idx}")
                
                frame_with_overlay = renderer.draw_all_markers(frame, players)
                self.video_canvas.set_frame(frame_with_overlay)
            else:
                # Just show frame without overlays
                print(f"_show_frame: Showing frame {frame_idx} WITHOUT overlays (export_enabled={self.export_btn.isEnabled()}, players={len(self.tracker_manager.players)})")
                self.video_canvas.set_frame(frame)
            
            self._update_frame_info()
            print(f"✅ Frame {frame_idx} displayed")
        except Exception as e:
            print(f"❌ Error showing frame {frame_idx}: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_frame_info(self):
        """Update frame information label"""
        try:
            total = self.tracker_manager.total_frames
            self.frame_label.setText(f"Frame: {self.current_frame_idx + 1} / {total}")
            # Update navigation buttons
            self._update_frame_navigation_buttons()
        except Exception as e:
            print(f"Error updating frame info: {e}")
    
    def _start_tracking(self):
        """Start tracking process"""
        if not self.video_path or len(self.tracker_manager.players) == 0:
            return
        
        # Clear previous tracking data
        self.tracker_manager.tracking_results.clear()
        
        # Disable controls
        self.start_tracking_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        self.add_player_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(self.tracker_manager.total_frames)
        self.progress_bar.setValue(0)
        self.status_label.setText("Tracking in progress...")
        self.status_label.setStyleSheet("color: green;")
        
        # Create and start tracking thread
        self.tracking_thread = TrackingThread(self.tracker_manager, self.video_path)
        self.tracking_thread.progress.connect(self._on_tracking_progress)
        self.tracking_thread.finished.connect(self._on_tracking_finished)
        self.tracking_thread.start()
    
    def _on_tracking_progress(self, current: int, total: int):
        """Handle tracking progress update"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Tracking: {current}/{total} frames")
    
    def _on_tracking_finished(self, success: bool, message: str):
        """Handle tracking completion"""
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("Tracking completed!")
            self.status_label.setStyleSheet("color: green;")
            self.export_btn.setEnabled(True)
            
            # Start preview updates
            self.preview_timer.start(33)  # ~30 FPS preview
        else:
            self.status_label.setText(f"Error: {message}")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.warning(self, "Tracking Error", message)
        
        # Re-enable controls
        self.start_tracking_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        self.add_player_btn.setEnabled(True)
    
    def _update_preview(self):
        """Update video preview with tracking"""
        if not self.video_path:
            self.preview_timer.stop()
            return
        
        # Get current frame
        frame = self.tracker_manager.get_frame(self.current_frame_idx)
        if frame is None:
            self.preview_timer.stop()
            return
        
        # Draw overlays using stored tracking results
        from ..render.overlay_renderer import OverlayRenderer
        renderer = OverlayRenderer()
        players = self.tracker_manager.get_all_players()
        
        # Update current_bbox from stored tracking results
        for player in players:
            stored_bbox = self.tracker_manager.get_bbox_at_frame(
                player.player_id, self.current_frame_idx
            )
            if stored_bbox is not None:
                player.current_bbox = stored_bbox
        
        frame_with_overlay = renderer.draw_all_markers(frame, players)
        self.video_canvas.set_frame(frame_with_overlay)
        
        # Auto-advance frame for preview
        if self.current_frame_idx < self.tracker_manager.total_frames - 1:
            self.current_frame_idx += 1
            self._update_frame_info()
        else:
            self.current_frame_idx = 0  # Loop back to start
    
    def _export_video(self):
        """Export video with tracking"""
        if not self.video_path:
            return
        
        # Get output path
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Video",
            "output_with_tracking.mp4",
            "Video Files (*.mp4);;All Files (*)"
        )
        
        if not output_path:
            return
        
        # Disable controls
        self.export_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        self.start_tracking_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(self.tracker_manager.total_frames)
        self.progress_bar.setValue(0)
        self.status_label.setText("Exporting video...")
        self.status_label.setStyleSheet("color: blue;")
        
        # Create and start export thread
        self.export_thread = ExportThread(self.tracker_manager, self.video_path, output_path)
        self.export_thread.progress.connect(self._on_export_progress)
        self.export_thread.finished.connect(self._on_export_finished)
        self.export_thread.start()
    
    def _on_export_progress(self, current: int, total: int):
        """Handle export progress update"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Exporting: {current}/{total} frames")
    
    def _on_export_finished(self, success: bool, message: str):
        """Handle export completion"""
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("Export completed!")
            self.status_label.setStyleSheet("color: green;")
            QMessageBox.information(
                self,
                "Success",
                message
            )
        else:
            self.status_label.setText(f"Export error")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.warning(self, "Export Error", message)
        
        # Re-enable controls
        self.export_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        self.start_tracking_btn.setEnabled(True)
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.tracking_thread and self.tracking_thread.isRunning():
            self.tracking_thread.cancel()
            self.tracking_thread.wait()
        
        if self.export_thread and self.export_thread.isRunning():
            self.export_thread.cancel()
            self.export_thread.wait()
        
        self.tracker_manager.release()
        event.accept()

