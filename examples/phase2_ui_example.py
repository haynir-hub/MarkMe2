"""
Phase 2 UI Example - Complete two-phase tracking workflow with UI
דוגמת Phase 2 - זרימת עבודה מלאה עם ממשק משתמש
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMessageBox
from src.tracking.tracker_manager import TrackerManager
from src.tracking.tracking_analyzer import TrackingAnalyzer
from src.ui.tracking_review_dialog import TrackingReviewDialog
from src.render.video_exporter import VideoExporter


def complete_workflow_example(video_path: str, output_path: str):
    """
    Complete example of two-phase tracking workflow with UI

    Args:
        video_path: Path to input video
        output_path: Path for output video
    """
    print("=" * 60)
    print("Two-Phase Tracking - Complete Workflow")
    print("=" * 60)

    # Create Qt application (required for UI)
    app = QApplication(sys.argv)

    # Step 1: Setup tracker manager
    print("\n📹 Step 1: Loading video...")
    tracker_manager = TrackerManager()

    if not tracker_manager.load_video(video_path):
        print("❌ Failed to load video")
        return

    print(f"✅ Video loaded: {tracker_manager.total_frames} frames at {tracker_manager.fps} FPS")

    # Step 2: Add players (in real app, this would be done via UI)
    print("\n👤 Step 2: Adding players...")

    # Example: Add two players
    player1_id = tracker_manager.add_player(
        name="Player 1",
        marker_style="circle",
        initial_frame=0,
        bbox=(100, 100, 50, 80)
    )

    player2_id = tracker_manager.add_player(
        name="Player 2",
        marker_style="arrow",
        initial_frame=0,
        bbox=(300, 150, 50, 80)
    )

    print(f"✅ Added {len(tracker_manager.players)} players")

    # Step 3: Phase 1 - Generate tracking data
    print("\n🎯 Step 3: Phase 1 - Generating tracking data...")

    tracking_data = tracker_manager.generate_tracking_data(
        start_frame=0,
        end_frame=min(500, tracker_manager.total_frames - 1),  # First 500 frames or less
        progress_callback=lambda curr, total: print(f"  Progress: {curr}/{total} frames", end='\r')
    )

    print("\n✅ Tracking data generated")

    # Step 4: Automatic analysis
    print("\n🔍 Step 4: Analyzing tracking quality...")

    analyzer = TrackingAnalyzer()

    for player_id in tracking_data:
        player = tracker_manager.get_player(player_id)
        player_data = tracking_data[player_id]

        # Analyze issues
        issues = analyzer.analyze(
            player_data,
            tracker_manager.frame_width,
            tracker_manager.frame_height
        )

        # Get summary
        summary = analyzer.get_summary(issues)

        # Calculate quality score
        quality_score = analyzer.calculate_tracking_quality_score(player_data, issues)

        print(f"\n{player.name}:")
        print(f"  Quality Score: {quality_score:.2f}")
        print(f"  Total Issues: {summary['total']}")
        print(f"  By Severity: {summary['by_severity']}")
        print(f"  By Type: {summary['by_type']}")

        if summary['critical_frames']:
            print(f"  Critical Frames: {summary['critical_frames'][:10]}...")  # Show first 10

        # Get correction suggestions
        suggestions = analyzer.suggest_corrections(issues, player_data)
        if suggestions:
            print(f"  Suggested Corrections: {len(suggestions)} frames")
            for frame_idx, reason in suggestions[:5]:  # Show first 5
                print(f"    - Frame {frame_idx}: {reason}")

    # Step 5: Manual review via UI
    print("\n👁️  Step 5: Opening review UI...")
    print("  Instructions:")
    print("  - Review confidence graph")
    print("  - Click on problematic frames")
    print("  - Fix frames if needed")
    print("  - Click 'Continue to Export' when done")

    review_dialog = TrackingReviewDialog(
        tracker_manager=tracker_manager,
        tracking_data=tracking_data
    )

    result = review_dialog.exec()

    if result == review_dialog.DialogCode.Accepted:
        print("\n✅ User approved tracking")

        # Step 6: Export
        print("\n📹 Step 6: Exporting video with overlays...")

        exporter = VideoExporter(tracker_manager)

        success = exporter.export_video(
            input_path=video_path,
            output_path=output_path,
            progress_callback=lambda curr, total: print(f"  Export: {curr}/{total} frames", end='\r')
        )

        if success:
            print(f"\n✅ Video exported successfully: {output_path}")
        else:
            print("\n❌ Export failed")

    else:
        print("\n❌ User cancelled")

    print("\n" + "=" * 60)
    print("Workflow Complete")
    print("=" * 60)


def analyzer_only_example(video_path: str):
    """
    Example: Use analyzer without UI (programmatic analysis)

    Args:
        video_path: Path to input video
    """
    print("=" * 60)
    print("Tracking Analyzer - Programmatic Example")
    print("=" * 60)

    tracker_manager = TrackerManager()

    if not tracker_manager.load_video(video_path):
        print("❌ Failed to load video")
        return

    # Add player and track
    player_id = tracker_manager.add_player("Player 1", "circle", 0, (100, 100, 50, 80))
    tracking_data = tracker_manager.generate_tracking_data(0, 300)

    # Analyze
    analyzer = TrackingAnalyzer()
    issues = analyzer.analyze(
        tracking_data[player_id],
        tracker_manager.frame_width,
        tracker_manager.frame_height
    )

    # Print detailed issues
    print("\n🔍 Detailed Issues:")
    for issue in issues[:20]:  # Show first 20
        print(f"  Frame {issue.frame_idx}: [{issue.severity}] {issue.description}")

    # Find gaps
    gaps = analyzer.find_tracking_gaps(tracking_data[player_id])
    if gaps:
        print(f"\n⚠️  Found {len(gaps)} tracking gaps:")
        for start, end in gaps:
            print(f"  Frames {start}-{end} ({end - start + 1} frames)")

    # Get suggestions
    suggestions = analyzer.suggest_corrections(issues, tracking_data[player_id])
    print(f"\n💡 Suggested {len(suggestions)} frames for manual correction")

    # Quality metrics
    quality_score = analyzer.calculate_tracking_quality_score(tracking_data[player_id], issues)
    print(f"\n📊 Overall Quality Score: {quality_score:.2f}")

    if quality_score >= 0.8:
        print("  ✅ Excellent tracking quality")
    elif quality_score >= 0.6:
        print("  ⚠️  Good tracking, some corrections recommended")
    elif quality_score >= 0.4:
        print("  ⚠️  Fair tracking, corrections needed")
    else:
        print("  ❌ Poor tracking, significant corrections required")


if __name__ == "__main__":
    print("🎬 Phase 2 UI Examples")
    print("=" * 60)

    # Example paths (change these!)
    video_path = "path/to/your/video.mp4"
    output_path = "path/to/output.mp4"

    print("\nNote: Update video_path and output_path in the code!")
    print("\nAvailable examples:")
    print("  1. complete_workflow_example() - Full UI workflow")
    print("  2. analyzer_only_example() - Programmatic analysis only")

    # Uncomment to run:
    # complete_workflow_example(video_path, output_path)
    # analyzer_only_example(video_path)

    print("\n" + "=" * 60)
    print("💡 Tip: Uncomment the function you want to run")
    print("=" * 60)
