"""
Phase 3: Manual Bbox Correction Example
דוגמת Phase 3 - תיקון ידני של bbox
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from src.tracking.tracker_manager import TrackerManager
from src.ui.tracking_review_dialog import TrackingReviewDialog
from src.ui.bbox_editor import BboxEditor
import cv2


def manual_bbox_editor_standalone_example():
    """
    Standalone example of BboxEditor widget
    """
    print("=" * 60)
    print("BboxEditor Standalone Example")
    print("=" * 60)

    app = QApplication(sys.argv)

    # Load a test frame
    video_path = "path/to/your/video.mp4"  # Change this!
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to load video")
        return

    # Create bbox editor
    editor = BboxEditor()
    editor.setWindowTitle("Bbox Editor Test")
    editor.resize(800, 600)

    # Set frame with initial bbox
    initial_bbox = (100, 100, 150, 200)  # x, y, w, h
    editor.set_frame(frame, initial_bbox)

    # Connect to bbox_changed signal
    def on_bbox_changed(bbox):
        print(f"Bbox changed: {bbox}")

    editor.bbox_changed.connect(on_bbox_changed)

    # Show editor
    editor.show()

    print("\nInstructions:")
    print("- Drag corners to resize")
    print("- Drag middle to move")
    print("- Click and drag to draw new bbox")
    print("- ESC to cancel")
    print("- Delete to clear")

    sys.exit(app.exec())


def full_workflow_with_manual_correction():
    """
    Complete workflow: Track -> Review -> Manual Correction -> Re-track
    """
    print("=" * 60)
    print("Complete Workflow with Manual Correction")
    print("=" * 60)

    app = QApplication(sys.argv)

    video_path = "path/to/your/video.mp4"  # Change this!

    # Setup
    tracker_manager = TrackerManager()
    if not tracker_manager.load_video(video_path):
        print("❌ Failed to load video")
        return

    print(f"✅ Video loaded: {tracker_manager.total_frames} frames")

    # Add player
    player_id = tracker_manager.add_player(
        name="Player 1",
        marker_style="circle",
        initial_frame=0,
        bbox=(150, 150, 60, 100)
    )

    print(f"✅ Added player {player_id}")

    # Phase 1: Initial tracking
    print("\n🎯 Phase 1: Initial tracking...")
    tracking_data = tracker_manager.generate_tracking_data(0, 200)

    # Phase 2 & 3: Review and Manual Correction
    print("\n👁️  Phase 2 & 3: Opening review UI with manual correction...")
    print("\nWorkflow:")
    print("1. Review confidence graph")
    print("2. Click on problematic frame")
    print("3. Click 'Fix Frame' button")
    print("4. Draw/edit bbox on the frame")
    print("5. Bbox is automatically saved as learning frame")
    print("6. Click 'Re-track' to update tracking from correction")
    print("7. Review again and repeat if needed")
    print("8. Click 'Continue to Export' when satisfied")

    dialog = TrackingReviewDialog(tracker_manager, tracking_data)
    result = dialog.exec()

    if result == dialog.DialogCode.Accepted:
        print("\n✅ User approved - ready for export!")

        # Check how many learning frames were added
        player = tracker_manager.get_player(player_id)
        print(f"\nLearning frames: {len(player.learning_frames)}")
        for frame_idx, bbox in player.learning_frames.items():
            print(f"  Frame {frame_idx}: {bbox}")

    else:
        print("\n❌ User cancelled")

    print("\n" + "=" * 60)


def bbox_editor_features_demo():
    """
    Demonstrate all BboxEditor features
    """
    print("=" * 60)
    print("BboxEditor Features Demo")
    print("=" * 60)

    app = QApplication(sys.argv)

    # Load frame
    video_path = "path/to/your/video.mp4"
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to load video")
        return

    # Create editor
    editor = BboxEditor()
    editor.setWindowTitle("BboxEditor Features Demo")
    editor.resize(1000, 700)

    # Set initial bbox
    editor.set_frame(frame, (200, 150, 120, 180))

    # Track changes
    changes_count = [0]

    def on_bbox_changed(bbox):
        changes_count[0] += 1
        print(f"\n📝 Change #{changes_count[0]}")
        print(f"   New bbox: {bbox}")
        print(f"   Size: {bbox[2]} x {bbox[3]} pixels")
        print(f"   Area: {bbox[2] * bbox[3]} px²")

    editor.bbox_changed.connect(on_bbox_changed)

    editor.show()

    print("\n" + "=" * 60)
    print("Features to try:")
    print("=" * 60)
    print("\n1. RESIZE FROM CORNERS:")
    print("   - Hover over corner (cursor changes)")
    print("   - Click and drag to resize")
    print("   - Maintains opposite corner fixed")
    print("\n2. RESIZE FROM EDGES:")
    print("   - Hover over edge (cursor changes)")
    print("   - Click and drag to resize from that edge")
    print("\n3. MOVE BBOX:")
    print("   - Click inside bbox (cursor changes to move)")
    print("   - Drag to move entire bbox")
    print("\n4. DRAW NEW BBOX:")
    print("   - Click outside bbox")
    print("   - Drag to create new bbox")
    print("   - Old bbox is replaced")
    print("\n5. KEYBOARD SHORTCUTS:")
    print("   - ESC: Cancel current operation")
    print("   - Delete/Backspace: Clear bbox")
    print("\n6. VISUAL FEEDBACK:")
    print("   - Green bbox: Normal")
    print("   - Cyan bbox: Active (being edited)")
    print("   - Dashed bbox: Drawing new")
    print("   - White handles: Resize/move points")
    print("\n" + "=" * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    print("🎬 Phase 3: Manual Bbox Correction Examples")
    print("=" * 60)

    print("\nNote: Update video_path in the code!")
    print("\nAvailable examples:")
    print("  1. manual_bbox_editor_standalone_example() - Test BboxEditor widget")
    print("  2. full_workflow_with_manual_correction() - Complete workflow")
    print("  3. bbox_editor_features_demo() - Feature demonstration")

    # Uncomment to run:
    # manual_bbox_editor_standalone_example()
    # full_workflow_with_manual_correction()
    # bbox_editor_features_demo()

    print("\n" + "=" * 60)
    print("💡 Tip: Uncomment the function you want to run")
    print("=" * 60)
