"""
Tracking Review Dialog - UI for reviewing and correcting tracking data
חלון סקירת מעקב - ממשק לסקירה ותיקון נתוני מעקב
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QListWidget, QListWidgetItem,
                             QSplitter, QWidget, QProgressBar, QCheckBox,
                             QSpinBox, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from ..tracking.tracker_manager import TrackerManager


class ConfidenceGraph(QWidget):
    """Widget for displaying confidence graph over time"""

    frame_clicked = pyqtSignal(int)  # Emits frame index when clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracking_data = {}
        self.player_id = None
        self.current_frame = 0
        self.setMinimumHeight(100)
        self.setMaximumHeight(150)

    def set_data(self, tracking_data: Dict[int, Dict[str, any]], player_id: int):
        """Set tracking data to display"""
        self.tracking_data = tracking_data
        self.player_id = player_id
        self.update()

    def set_current_frame(self, frame_idx: int):
        """Update current frame indicator"""
        self.current_frame = frame_idx
        self.update()

    def paintEvent(self, event):
        """Draw the confidence graph"""
        if not self.tracking_data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Background
        painter.fillRect(0, 0, width, height, QColor(40, 40, 40))

        # Draw grid
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        for i in range(0, 11, 2):  # Horizontal grid lines
            y = height - (i * height / 10)
            painter.drawLine(0, int(y), width, int(y))

        if not self.tracking_data:
            painter.end()
            return

        # Get frame range
        frames = sorted(self.tracking_data.keys())
        if not frames:
            painter.end()
            return

        min_frame = min(frames)
        max_frame = max(frames)
        frame_range = max_frame - min_frame

        if frame_range == 0:
            painter.end()
            return

        # Draw confidence line
        points = []
        for frame_idx in frames:
            data = self.tracking_data[frame_idx]
            confidence = data.get('confidence', 0.0)

            x = int((frame_idx - min_frame) / frame_range * width)
            y = int(height - (confidence * height))
            points.append((x, y, confidence, data.get('is_learning_frame', False)))

        # Draw confidence zones
        # High confidence zone (green)
        painter.setPen(QPen(QColor(0, 150, 0, 30), 1))
        painter.fillRect(0, 0, width, int(height * 0.2), QColor(0, 150, 0, 20))

        # Medium confidence zone (yellow)
        painter.fillRect(0, int(height * 0.2), width, int(height * 0.3), QColor(150, 150, 0, 20))

        # Low confidence zone (red)
        painter.fillRect(0, int(height * 0.5), width, int(height * 0.5), QColor(150, 0, 0, 20))

        # Draw confidence line
        painter.setPen(QPen(QColor(0, 200, 255), 2))
        for i in range(len(points) - 1):
            x1, y1, _, _ = points[i]
            x2, y2, _, _ = points[i + 1]
            painter.drawLine(x1, y1, x2, y2)

        # Draw points
        for x, y, confidence, is_learning in points:
            if is_learning:
                # Learning frames - larger, gold color
                painter.setPen(QPen(QColor(255, 215, 0), 1))
                painter.setBrush(QColor(255, 215, 0))
                painter.drawEllipse(x - 4, y - 4, 8, 8)
            elif confidence < 0.5:
                # Low confidence - red
                painter.setPen(QPen(QColor(255, 0, 0), 1))
                painter.setBrush(QColor(255, 0, 0))
                painter.drawEllipse(x - 3, y - 3, 6, 6)
            else:
                # Normal - cyan
                painter.setPen(QPen(QColor(0, 200, 255), 1))
                painter.setBrush(QColor(0, 200, 255))
                painter.drawEllipse(x - 2, y - 2, 4, 4)

        # Draw current frame indicator
        if min_frame <= self.current_frame <= max_frame:
            x = int((self.current_frame - min_frame) / frame_range * width)
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawLine(x, 0, x, height)

        # Draw labels
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawText(5, 15, f"Frame {min_frame}")
        painter.drawText(width - 80, 15, f"Frame {max_frame}")
        painter.drawText(5, height - 5, "0.0")
        painter.drawText(5, 15, "1.0")

        painter.end()

    def mousePressEvent(self, event):
        """Handle mouse click to jump to frame"""
        if not self.tracking_data:
            return

        frames = sorted(self.tracking_data.keys())
        if not frames:
            return

        min_frame = min(frames)
        max_frame = max(frames)
        frame_range = max_frame - min_frame

        if frame_range == 0:
            return

        # Calculate clicked frame
        x = event.position().x()
        frame_idx = int(min_frame + (x / self.width()) * frame_range)
        frame_idx = max(min_frame, min(max_frame, frame_idx))

        self.frame_clicked.emit(frame_idx)


class TrackingReviewDialog(QDialog):
    """Dialog for reviewing and correcting tracking data"""

    def __init__(self, tracker_manager: TrackerManager,
                 tracking_data: Dict[int, Dict[int, Dict[str, any]]],
                 parent=None):
        super().__init__(parent)
        self.tracker_manager = tracker_manager
        self.tracking_data = tracking_data
        self.current_frame_idx = 0
        self.current_player_id = None
        self.problematic_frames = []

        self.setWindowTitle("סקירת מעקב - Tracking Review")
        self.setMinimumSize(1200, 800)

        self._init_ui()
        self._analyze_tracking_data()
        self._load_first_player()

    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()

        # Top section: Player selection and statistics
        top_layout = QHBoxLayout()

        # Player info
        player_group = QGroupBox("שחקנים - Players")
        player_layout = QVBoxLayout()

        self.player_list = QListWidget()
        self.player_list.currentItemChanged.connect(self._on_player_changed)
        player_layout.addWidget(self.player_list)

        # Populate player list
        for player_id, player in self.tracker_manager.players.items():
            item = QListWidgetItem(f"{player.name} (ID: {player_id})")
            item.setData(Qt.ItemDataRole.UserRole, player_id)
            self.player_list.addItem(item)

        player_group.setLayout(player_layout)
        top_layout.addWidget(player_group, 1)

        # Statistics
        stats_group = QGroupBox("סטטיסטיקות - Statistics")
        stats_layout = QVBoxLayout()

        self.stats_label = QLabel("בחר שחקן - Select player")
        stats_layout.addWidget(self.stats_label)

        stats_group.setLayout(stats_layout)
        top_layout.addWidget(stats_group, 2)

        layout.addLayout(top_layout)

        # Confidence graph
        graph_group = QGroupBox("גרף ביטחון - Confidence Graph")
        graph_layout = QVBoxLayout()

        self.confidence_graph = ConfidenceGraph()
        self.confidence_graph.frame_clicked.connect(self._jump_to_frame)
        graph_layout.addWidget(self.confidence_graph)

        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("🟡 Learning Frame"))
        legend_layout.addWidget(QLabel("🔴 Low Confidence (<0.5)"))
        legend_layout.addWidget(QLabel("🔵 Normal Tracking"))
        legend_layout.addStretch()
        graph_layout.addLayout(legend_layout)

        graph_group.setLayout(graph_layout)
        layout.addWidget(graph_group)

        # Middle section: Video preview and problematic frames list
        middle_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Video preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout()

        self.video_label = QLabel("טוען וידאו...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        preview_layout.addWidget(self.video_label)

        # Frame controls
        controls_layout = QHBoxLayout()

        self.prev_frame_btn = QPushButton("◀ פריים קודם")
        self.prev_frame_btn.clicked.connect(self._prev_frame)
        controls_layout.addWidget(self.prev_frame_btn)

        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(self.tracker_manager.total_frames - 1)
        self.frame_slider.valueChanged.connect(self._on_frame_changed)
        controls_layout.addWidget(self.frame_slider, 3)

        self.next_frame_btn = QPushButton("פריים הבא ▶")
        self.next_frame_btn.clicked.connect(self._next_frame)
        controls_layout.addWidget(self.next_frame_btn)

        preview_layout.addLayout(controls_layout)

        # Frame info
        info_layout = QHBoxLayout()
        self.frame_info_label = QLabel("פריים: 0 / 0")
        info_layout.addWidget(self.frame_info_label)

        self.confidence_label = QLabel("ביטחון: N/A")
        info_layout.addWidget(self.confidence_label)

        preview_layout.addLayout(info_layout)

        preview_widget.setLayout(preview_layout)
        middle_splitter.addWidget(preview_widget)

        # Problematic frames list
        problems_widget = QWidget()
        problems_layout = QVBoxLayout()

        problems_label = QLabel("פריימים בעייתיים - Problematic Frames")
        problems_layout.addWidget(problems_label)

        # Filters
        filter_layout = QHBoxLayout()

        self.show_low_conf_cb = QCheckBox("ביטחון נמוך")
        self.show_low_conf_cb.setChecked(True)
        self.show_low_conf_cb.stateChanged.connect(self._update_problems_list)
        filter_layout.addWidget(self.show_low_conf_cb)

        self.show_lost_cb = QCheckBox("מעקב אבוד")
        self.show_lost_cb.setChecked(True)
        self.show_lost_cb.stateChanged.connect(self._update_problems_list)
        filter_layout.addWidget(self.show_lost_cb)

        filter_layout.addWidget(QLabel("סף:"))
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setMinimum(0)
        self.threshold_spin.setMaximum(100)
        self.threshold_spin.setValue(50)
        self.threshold_spin.setSuffix("%")
        self.threshold_spin.valueChanged.connect(self._update_problems_list)
        filter_layout.addWidget(self.threshold_spin)

        problems_layout.addLayout(filter_layout)

        self.problems_list = QListWidget()
        self.problems_list.itemClicked.connect(self._on_problem_clicked)
        problems_layout.addWidget(self.problems_list)

        # Fix button
        self.fix_frame_btn = QPushButton("תקן פריים זה")
        self.fix_frame_btn.clicked.connect(self._fix_current_frame)
        problems_layout.addWidget(self.fix_frame_btn)

        problems_widget.setLayout(problems_layout)
        middle_splitter.addWidget(problems_widget)

        middle_splitter.setSizes([700, 300])
        layout.addWidget(middle_splitter, 3)

        # Bottom section: Action buttons
        button_layout = QHBoxLayout()

        self.re_track_btn = QPushButton("🔄 מעקב מחדש - Re-track")
        self.re_track_btn.clicked.connect(self._re_track)
        button_layout.addWidget(self.re_track_btn)

        button_layout.addStretch()

        self.export_btn = QPushButton("📹 המשך לייצוא - Continue to Export")
        self.export_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.export_btn)

        self.close_btn = QPushButton("סגור - Close")
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _analyze_tracking_data(self):
        """Analyze tracking data to find problematic frames"""
        # This will be populated when player is selected
        pass

    def _load_first_player(self):
        """Load the first player in the list"""
        if self.player_list.count() > 0:
            self.player_list.setCurrentRow(0)

    def _on_player_changed(self, current, previous):
        """Handle player selection change"""
        if current is None:
            return

        self.current_player_id = current.data(Qt.ItemDataRole.UserRole)
        player_data = self.tracking_data.get(self.current_player_id, {})

        # Update confidence graph
        self.confidence_graph.set_data(player_data, self.current_player_id)

        # Update statistics
        self._update_statistics()

        # Update problems list
        self._update_problems_list()

        # Load first frame
        if player_data:
            first_frame = min(player_data.keys())
            self._jump_to_frame(first_frame)

    def _update_statistics(self):
        """Update statistics display"""
        if self.current_player_id is None:
            return

        player = self.tracker_manager.get_player(self.current_player_id)
        player_data = self.tracking_data.get(self.current_player_id, {})

        if not player_data:
            self.stats_label.setText("אין נתוני מעקב - No tracking data")
            return

        total_frames = len(player_data)
        tracked = len([f for f, d in player_data.items() if d['bbox'] is not None])
        lost = len([f for f, d in player_data.items() if d['bbox'] is None])
        learning = len([f for f, d in player_data.items() if d['is_learning_frame']])
        avg_conf = sum([d['confidence'] for d in player_data.values()]) / total_frames if total_frames > 0 else 0

        low_conf = len([f for f, d in player_data.items() if d['confidence'] < 0.5])

        stats_text = f"""
        <b>{player.name}</b><br>
        <br>
        סה"כ פריימים: {total_frames}<br>
        מעקב מוצלח: {tracked} ({tracked/total_frames*100:.1f}%)<br>
        מעקב אבוד: {lost} ({lost/total_frames*100:.1f}%)<br>
        ביטחון נמוך: {low_conf} ({low_conf/total_frames*100:.1f}%)<br>
        Learning frames: {learning}<br>
        <br>
        ביטחון ממוצע: {avg_conf:.2f}
        """

        self.stats_label.setText(stats_text)

    def _update_problems_list(self):
        """Update list of problematic frames"""
        self.problems_list.clear()

        if self.current_player_id is None:
            return

        player_data = self.tracking_data.get(self.current_player_id, {})
        threshold = self.threshold_spin.value() / 100.0

        problems = []

        for frame_idx, data in sorted(player_data.items()):
            reason = None

            if self.show_lost_cb.isChecked() and data['bbox'] is None:
                reason = "מעקב אבוד - Lost"
            elif self.show_low_conf_cb.isChecked() and data['confidence'] < threshold:
                reason = f"ביטחון נמוך - Low confidence ({data['confidence']:.2f})"

            if reason:
                problems.append((frame_idx, reason, data['confidence']))

        # Add to list
        for frame_idx, reason, conf in problems:
            item = QListWidgetItem(f"פריים {frame_idx}: {reason}")
            item.setData(Qt.ItemDataRole.UserRole, frame_idx)

            # Color code by severity
            if conf == 0.0:
                item.setForeground(QColor(255, 0, 0))  # Red for lost
            elif conf < 0.3:
                item.setForeground(QColor(255, 100, 0))  # Orange for very low
            else:
                item.setForeground(QColor(255, 200, 0))  # Yellow for low

            self.problems_list.addItem(item)

    def _on_problem_clicked(self, item):
        """Handle click on problematic frame"""
        frame_idx = item.data(Qt.ItemDataRole.UserRole)
        self._jump_to_frame(frame_idx)

    def _jump_to_frame(self, frame_idx: int):
        """Jump to specific frame"""
        self.current_frame_idx = frame_idx
        self.frame_slider.setValue(frame_idx)
        self._display_frame(frame_idx)

    def _on_frame_changed(self, frame_idx: int):
        """Handle frame slider change"""
        self.current_frame_idx = frame_idx
        self._display_frame(frame_idx)

    def _display_frame(self, frame_idx: int):
        """Display frame with tracking overlay"""
        # Get frame
        frame = self.tracker_manager.get_frame(frame_idx)
        if frame is None:
            self.video_label.setText(f"שגיאה בטעינת פריים {frame_idx}")
            return

        # Draw tracking overlay if available
        if self.current_player_id is not None:
            player_data = self.tracking_data.get(self.current_player_id, {})
            if frame_idx in player_data:
                data = player_data[frame_idx]
                bbox = data.get('bbox')
                confidence = data.get('confidence', 0.0)
                is_learning = data.get('is_learning_frame', False)

                if bbox is not None:
                    x, y, w, h = [int(v) for v in bbox]

                    # Choose color based on confidence
                    if is_learning:
                        color = (255, 215, 0)  # Gold for learning frames
                        thickness = 3
                    elif confidence < 0.5:
                        color = (0, 0, 255)  # Red for low confidence
                        thickness = 2
                    else:
                        color = (0, 255, 0)  # Green for good tracking
                        thickness = 2

                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)

                    # Draw confidence text
                    text = f"{confidence:.2f}"
                    if is_learning:
                        text = f"LEARNING {text}"
                    cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                              0.5, color, 2)

        # Convert to QPixmap and display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        # Scale to fit label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(),
                                      Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)

        # Update info labels
        self.frame_info_label.setText(f"פריים: {frame_idx} / {self.tracker_manager.total_frames - 1}")

        if self.current_player_id and frame_idx in self.tracking_data.get(self.current_player_id, {}):
            data = self.tracking_data[self.current_player_id][frame_idx]
            conf_text = f"ביטחון: {data['confidence']:.2f}"
            if data['is_learning_frame']:
                conf_text += " (Learning Frame)"
            self.confidence_label.setText(conf_text)
        else:
            self.confidence_label.setText("ביטחון: N/A")

        # Update graph
        self.confidence_graph.set_current_frame(frame_idx)

    def _prev_frame(self):
        """Go to previous frame"""
        if self.current_frame_idx > 0:
            self._jump_to_frame(self.current_frame_idx - 1)

    def _next_frame(self):
        """Go to next frame"""
        if self.current_frame_idx < self.tracker_manager.total_frames - 1:
            self._jump_to_frame(self.current_frame_idx + 1)

    def _fix_current_frame(self):
        """Mark current frame for manual correction"""
        # TODO: Implement manual bbox marking
        # For now, just show message
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "תיקון ידני - Manual Correction",
            f"תכונה זו תאפשר סימון ידני של ה-bbox בפריים {self.current_frame_idx}.\n"
            f"זה יוסיף learning frame חדש ויעדכן את המעקב.\n\n"
            f"This feature will allow manual bbox marking in frame {self.current_frame_idx}.\n"
            f"It will add a new learning frame and update tracking.\n\n"
            f"(בפיתוח - In Development)"
        )

    def _re_track(self):
        """Re-run tracking with current corrections"""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "מעקב מחדש - Re-track",
            "האם לבצע מעקב מחדש עם התיקונים הנוכחיים?\n"
            "Re-run tracking with current corrections?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Get frame range
            player_data = self.tracking_data.get(self.current_player_id, {})
            if not player_data:
                return

            min_frame = min(player_data.keys())
            max_frame = max(player_data.keys())

            # Re-run tracking
            self.tracking_data = self.tracker_manager.generate_tracking_data(
                min_frame, max_frame
            )

            # Refresh display
            self._on_player_changed(self.player_list.currentItem(), None)

            QMessageBox.information(
                self,
                "הושלם - Complete",
                "מעקב מחדש הושלם!\nRe-tracking complete!"
            )
