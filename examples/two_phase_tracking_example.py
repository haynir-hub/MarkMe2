"""
דוגמת שימוש במערכת מעקב דו-שלבית
Two-Phase Tracking System Example

דוגמה זו מראה כיצד להשתמש בפונקציה generate_tracking_data()
כדי לבצע מעקב עם אפשרות לסקירה ותיקון.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tracking.tracker_manager import TrackerManager
from src.render.video_exporter import VideoExporter


def example_basic_usage():
    """דוגמה בסיסית: מעקב פשוט עם סטטיסטיקות"""
    print("=" * 60)
    print("דוגמה 1: שימוש בסיסי")
    print("=" * 60)

    # צור tracker manager
    tracker_manager = TrackerManager()

    # טען וידאו
    video_path = "path/to/your/video.mp4"  # שנה לנתיב אמיתי
    if not tracker_manager.load_video(video_path):
        print("❌ שגיאה בטעינת הוידאו")
        return

    print(f"✅ וידאו נטען: {tracker_manager.total_frames} פריימים")

    # הוסף שחקנים
    player1_id = tracker_manager.add_player(
        name="Player 1",
        marker_style="circle",
        initial_frame=0,
        bbox=(100, 100, 50, 80)  # x, y, width, height
    )

    player2_id = tracker_manager.add_player(
        name="Player 2",
        marker_style="arrow",
        initial_frame=0,
        bbox=(300, 150, 50, 80)
    )

    print(f"✅ הוספו {len(tracker_manager.players)} שחקנים")

    # שלב 1: צור נתוני מעקב
    print("\n🎯 מתחיל מעקב...")
    tracking_data = tracker_manager.generate_tracking_data(
        start_frame=0,
        end_frame=500,  # או None לכל הוידאו
        progress_callback=lambda curr, total: print(f"  התקדמות: {curr}/{total} פריימים", end='\r')
    )

    print("\n\n✅ מעקב הושלם!")

    # ניתוח תוצאות
    print("\n" + "=" * 60)
    print("סטטיסטיקות:")
    print("=" * 60)

    for player_id, frames_data in tracking_data.items():
        player = tracker_manager.get_player(player_id)
        successful = [f for f, d in frames_data.items() if d['bbox'] is not None]
        lost = [f for f, d in frames_data.items() if d['bbox'] is None]
        low_conf = [f for f, d in frames_data.items() if d['confidence'] < 0.6]

        print(f"\n{player.name} (ID: {player_id}):")
        print(f"  ✅ מעקב מוצלח: {len(successful)} פריימים")
        print(f"  ❌ מעקב אבוד: {len(lost)} פריימים")
        print(f"  ⚠️  ביטחון נמוך: {len(low_conf)} פריימים")

        if low_conf:
            print(f"  פריימים בעייתיים: {low_conf[:5]}...")  # הראה 5 ראשונים


def example_with_corrections():
    """דוגמה מתקדמת: זיהוי בעיות ותיקון"""
    print("\n" + "=" * 60)
    print("דוגמה 2: זיהוי בעיות ותיקון")
    print("=" * 60)

    tracker_manager = TrackerManager()
    video_path = "path/to/your/video.mp4"

    if not tracker_manager.load_video(video_path):
        print("❌ שגיאה בטעינת הוידאו")
        return

    # הוסף שחקן
    player_id = tracker_manager.add_player(
        name="Player 1",
        marker_style="circle",
        initial_frame=0,
        bbox=(100, 100, 50, 80)
    )

    # מעקב ראשוני
    print("🎯 מעקב ראשוני...")
    tracking_data = tracker_manager.generate_tracking_data(0, 1000)

    # זהה פריימים בעייתיים
    print("\n🔍 מחפש פריימים בעייתיים...")
    problematic_frames = []

    for frame_idx, data in tracking_data[player_id].items():
        # קריטריונים לפריים בעייתי:
        if data['confidence'] < 0.5:  # ביטחון נמוך
            problematic_frames.append((frame_idx, "ביטחון נמוך", data['confidence']))
        elif data['bbox'] is None:  # מעקב אבוד
            problematic_frames.append((frame_idx, "מעקב אבוד", 0.0))

    if problematic_frames:
        print(f"\n⚠️  נמצאו {len(problematic_frames)} פריימים בעייתיים:")
        for frame_idx, reason, conf in problematic_frames[:10]:  # הראה 10 ראשונים
            print(f"  - פריים {frame_idx}: {reason} (confidence={conf:.2f})")

        # בשלב זה, המשתמש יכול לסמן מחדש פריימים בעייתיים דרך ה-UI
        # לדוגמה:
        print("\n💡 בעתיד: כאן המשתמש יכול לקפוץ לפריימים ולתקן ידנית")

        # סימולציה: נוסיף learning frame
        if problematic_frames:
            fix_frame = problematic_frames[0][0]
            print(f"\n🔧 מדמה תיקון בפריים {fix_frame}...")

            # בפועל, המשתמש יסמן את ה-bbox החדש דרך ה-UI
            # כאן נשתמש ב-bbox מקורי כדוגמה
            tracker_manager.add_learning_frame_to_player(
                player_id=player_id,
                frame_idx=fix_frame,
                bbox=(120, 110, 50, 80)  # bbox מתוקן
            )

            # מעקב מחדש מהנקודה המתוקנת ואילך
            print(f"🔄 מעקב מחדש מפריים {fix_frame} ואילך...")
            tracking_data = tracker_manager.generate_tracking_data(fix_frame, 1000)

            print("✅ מעקב מחדש הושלם!")
    else:
        print("✅ לא נמצאו פריימים בעייתיים!")


def example_export_after_tracking():
    """דוגמה: ייצוא לאחר מעקב דו-שלבי"""
    print("\n" + "=" * 60)
    print("דוגמה 3: ייצוא לאחר מעקב")
    print("=" * 60)

    tracker_manager = TrackerManager()
    video_path = "path/to/your/video.mp4"
    output_path = "path/to/output.mp4"

    if not tracker_manager.load_video(video_path):
        print("❌ שגיאה בטעינת הוידאו")
        return

    # הוסף שחקנים
    tracker_manager.add_player("Player 1", "circle", 0, (100, 100, 50, 80))

    # שלב 1: מעקב
    print("🎯 שלב 1: מעקב...")
    tracking_data = tracker_manager.generate_tracking_data(0, None)

    # (כאן יכול להיות שלב סקירה ותיקון)

    # שלב 2: ייצוא
    print("\n📹 שלב 2: ייצוא...")
    exporter = VideoExporter(tracker_manager)

    success = exporter.export_video(
        input_path=video_path,
        output_path=output_path,
        progress_callback=lambda curr, total: print(f"  ייצוא: {curr}/{total} פריימים", end='\r')
    )

    if success:
        print(f"\n✅ ייצוא הושלם: {output_path}")
    else:
        print("\n❌ שגיאה בייצוא")


def example_confidence_analysis():
    """דוגמה: ניתוח ציוני ביטחון"""
    print("\n" + "=" * 60)
    print("דוגמה 4: ניתוח confidence")
    print("=" * 60)

    tracker_manager = TrackerManager()
    video_path = "path/to/your/video.mp4"

    if not tracker_manager.load_video(video_path):
        print("❌ שגיאה בטעינת הוידאו")
        return

    player_id = tracker_manager.add_player("Player 1", "circle", 0, (100, 100, 50, 80))

    # מעקב
    tracking_data = tracker_manager.generate_tracking_data(0, 500)

    # ניתוח confidence
    confidences = [d['confidence'] for d in tracking_data[player_id].values()]

    avg_conf = sum(confidences) / len(confidences)
    min_conf = min(confidences)
    max_conf = max(confidences)

    print(f"\nניתוח ביטחון:")
    print(f"  ממוצע: {avg_conf:.2f}")
    print(f"  מינימום: {min_conf:.2f}")
    print(f"  מקסימום: {max_conf:.2f}")

    # התפלגות
    high_conf = len([c for c in confidences if c >= 0.8])
    medium_conf = len([c for c in confidences if 0.5 <= c < 0.8])
    low_conf = len([c for c in confidences if c < 0.5])

    print(f"\nהתפלגות:")
    print(f"  גבוה (≥0.8): {high_conf} פריימים ({high_conf/len(confidences)*100:.1f}%)")
    print(f"  בינוני (0.5-0.8): {medium_conf} פריימים ({medium_conf/len(confidences)*100:.1f}%)")
    print(f"  נמוך (<0.5): {low_conf} פריימים ({low_conf/len(confidences)*100:.1f}%)")


if __name__ == "__main__":
    print("🎬 דוגמאות למערכת מעקב דו-שלבית")
    print("=" * 60)
    print("\nהערה: שנה את נתיבי הוידאו בקוד לפני הרצה!\n")

    # הרץ דוגמאות
    # example_basic_usage()
    # example_with_corrections()
    # example_export_after_tracking()
    # example_confidence_analysis()

    print("\n" + "=" * 60)
    print("💡 טיפ: הסר את ההערות (#) כדי להריץ דוגמה ספציפית")
    print("=" * 60)
