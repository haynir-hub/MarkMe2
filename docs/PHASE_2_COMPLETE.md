# ✅ Phase 2 הושלם - UI לסקירה ותיקון מעקב

## מה נוסף ב-Phase 2?

### 1. **Tracking Review Dialog** - UI מלא לסקירת מעקב ✅

**קובץ:** [src/ui/tracking_review_dialog.py](../src/ui/tracking_review_dialog.py)

**תכונות:**
- 📊 **גרף Confidence אינטראקטיבי**
  - הצגה ויזואלית של ציוני ביטחון לאורך זמן
  - קליק על הגרף לקפיצה לפריים
  - צביעה לפי רמות ביטחון (ירוק/צהוב/אדום)
  - סימון Learning Frames בזהב

- 👁️ **תצוגת וידאו עם Overlays**
  - הצגת הפריים עם bbox מסומן
  - צבעים לפי confidence (ירוק/צהוב/אדום)
  - סימון Learning Frames
  - ניווט מהיר עם slider וכפתורים

- 📋 **רשימת פריימים בעייתיים**
  - סינון לפי סוג בעיה (lost, low confidence)
  - סף confidence מתכוונן
  - קפיצה ישירה לפריים בעייתי
  - צביעה לפי חומרה

- 📈 **סטטיסטיקות מפורטות**
  - מספר פריימים tracked/lost
  - ציון ביטחון ממוצע
  - מספר Learning Frames
  - אחוזי הצלחה

- ⚙️ **פעולות**
  - תיקון ידני של פריימים (placeholder)
  - מעקב מחדש עם תיקונים
  - המשך לייצוא

### 2. **Tracking Analyzer** - זיהוי אוטומטי של בעיות ✅

**קובץ:** [src/tracking/tracking_analyzer.py](../src/tracking/tracking_analyzer.py)

**סוגי בעיות שמזוהות:**

1. **Lost Tracking** (מעקב אבוד)
   - bbox = None
   - Severity: Critical

2. **Low Confidence** (ביטחון נמוך)
   - Confidence < 0.5: High severity
   - Confidence < 0.3: Critical severity

3. **Sudden Jump** (קפיצה חדה)
   - תנועה גדולה בין פריימים (>100 פיקסלים)
   - מתחשב בפער בין פריימים
   - Severity: High/Critical

4. **Size Change** (שינוי גודל)
   - bbox גדל או הצטמצם פי 2 ומעלה
   - Severity: Medium/High

5. **Edge Detection** (קרוב לקצה)
   - bbox קרוב לקצה המסך (<20 פיקסלים)
   - עלול להצביע על drift
   - Severity: Medium

**פונקציות שימושיות:**

```python
analyzer = TrackingAnalyzer()

# ניתוח מלא
issues = analyzer.analyze(tracking_data, frame_width, frame_height)

# סיכום
summary = analyzer.get_summary(issues)
# Returns: {'total': 10, 'by_type': {...}, 'by_severity': {...}, 'frames_affected': [...]}

# הצעות תיקון
suggestions = analyzer.suggest_corrections(issues, tracking_data)
# Returns: [(frame_idx, reason), ...]

# זיהוי gaps
gaps = analyzer.find_tracking_gaps(tracking_data)
# Returns: [(start_frame, end_frame), ...]

# ציון איכות
quality_score = analyzer.calculate_tracking_quality_score(tracking_data, issues)
# Returns: 0.0-1.0 (1.0 = perfect)
```

## זרימת עבודה מלאה

### דוגמה 1: זרימה בסיסית עם UI

```python
from src.tracking.tracker_manager import TrackerManager
from src.tracking.tracking_analyzer import TrackingAnalyzer
from src.ui.tracking_review_dialog import TrackingReviewDialog
from PyQt6.QtWidgets import QApplication

# יצירת Qt application
app = QApplication(sys.argv)

# טעינת וידאו והוספת שחקנים
tracker_manager = TrackerManager()
tracker_manager.load_video("video.mp4")
tracker_manager.add_player("Player 1", "circle", 0, (100, 100, 50, 80))

# Phase 1: מעקב
tracking_data = tracker_manager.generate_tracking_data(0, 500)

# ניתוח אוטומטי (אופציונלי)
analyzer = TrackingAnalyzer()
issues = analyzer.analyze(
    tracking_data[1],  # player_id = 1
    tracker_manager.frame_width,
    tracker_manager.frame_height
)
quality = analyzer.calculate_tracking_quality_score(tracking_data[1], issues)
print(f"Quality Score: {quality:.2f}")

# Phase 2: סקירה ידנית עם UI
review_dialog = TrackingReviewDialog(tracker_manager, tracking_data)
if review_dialog.exec() == review_dialog.DialogCode.Accepted:
    # המשתמש אישר - המשך לייצוא
    exporter = VideoExporter(tracker_manager)
    exporter.export_video("video.mp4", "output.mp4")
```

### דוגמה 2: ניתוח פרוגרמטי ללא UI

```python
# מעקב
tracking_data = tracker_manager.generate_tracking_data(0, 1000)

# ניתוח
analyzer = TrackingAnalyzer()
for player_id, player_data in tracking_data.items():
    issues = analyzer.analyze(player_data, width, height)

    # בדיקת איכות
    quality = analyzer.calculate_tracking_quality_score(player_data, issues)

    if quality < 0.6:
        print(f"Player {player_id} needs review!")

        # קבל הצעות תיקון
        suggestions = analyzer.suggest_corrections(issues, player_data)
        for frame_idx, reason in suggestions:
            print(f"  Fix frame {frame_idx}: {reason}")

            # תקן אוטומטית (דוגמה)
            # tracker_manager.add_learning_frame_to_player(...)
```

### דוגמה 3: מציאת gaps ותיקון

```python
# מצא gaps במעקב
gaps = analyzer.find_tracking_gaps(tracking_data[1])

for start, end in gaps:
    gap_size = end - start + 1
    print(f"Gap: frames {start}-{end} ({gap_size} frames)")

    if gap_size < 10:
        # Gap קטן - תקן במרכז
        mid_frame = (start + end) // 2
        print(f"  Suggest fixing frame {mid_frame}")
    else:
        # Gap גדול - תקן בתחילה ובסוף
        print(f"  Suggest fixing frames {start} and {end}")
```

## ממשק ה-UI

### חלונות עיקריים:

1. **Player Selection** (שמאל למעלה)
   - רשימת שחקנים
   - בחירת שחקן לסקירה

2. **Statistics** (ימין למעלה)
   - סטטיסטיקות מפורטות
   - ציון ביטחון ממוצע
   - מספר פריימים בעייתיים

3. **Confidence Graph** (מרכז למעלה)
   - גרף אינטראקטיבי
   - אזורים צבעוניים לפי רמת ביטחון
   - קליק לקפיצה לפריים

4. **Video Preview** (מרכז שמאל)
   - הצגת פריים עם bbox
   - ניווט עם slider
   - כפתורי פריים הבא/קודם

5. **Problematic Frames** (מרכז ימין)
   - רשימה מסוננת
   - קפיצה לפריים
   - כפתור תיקון

### צבעים וסימונים:

- 🟢 **ירוק**: Confidence גבוה (>0.8)
- 🟡 **צהוב**: Confidence בינוני (0.5-0.8)
- 🔴 **אדום**: Confidence נמוך (<0.5)
- 🟡 **זהב**: Learning Frame (סומן ידנית)
- ⬜ **לבן**: קו מצביע על פריים נוכחי

## קבצים שנוספו

```
src/ui/tracking_review_dialog.py          [NEW - 688 lines]
  ├─ TrackingReviewDialog                 (Main dialog)
  └─ ConfidenceGraph                      (Custom widget)

src/tracking/tracking_analyzer.py         [NEW - 332 lines]
  ├─ TrackingIssue                        (Data class)
  └─ TrackingAnalyzer                     (Analysis engine)

examples/phase2_ui_example.py             [NEW - 220 lines]
  ├─ complete_workflow_example()          (Full UI workflow)
  └─ analyzer_only_example()              (Programmatic)
```

## TODO - מה עדיין חסר?

### 1. שיפור חישוב Confidence 📊
כרגע Confidence פשוט (0.8/1.0/0.0).
צריך:
- שילוב ציון מה-tracker (אם זמין)
- חישוב IoU עם פריים קודם
- בדיקת עקביות גודל
- התחשבות במהירות תנועה

### 2. Re-tracking חכם 🧠
כרגע re-tracking עובר על כל הפריימים מחדש.
צריך:
- re-track רק מהפריים המתוקן ואילך
- שמירת tracking הישן לפני התיקון
- אפשרות ל-undo/redo

### 3. ייצוא דו"ח 📄
- ייצוא רשימת בעיות ל-CSV/JSON
- סיכום איכות המעקב
- המלצות לשיפור

## הפעלת UI

### מתוך קוד Python:
```python
from PyQt6.QtWidgets import QApplication
from src.ui.tracking_review_dialog import TrackingReviewDialog

app = QApplication(sys.argv)
dialog = TrackingReviewDialog(tracker_manager, tracking_data)
dialog.exec()
```

### מתוך Main Window (בעתיד):
```python
# בתפריט או כפתור
def review_tracking(self):
    tracking_data = self.tracker_manager.generate_tracking_data(...)
    dialog = TrackingReviewDialog(self.tracker_manager, tracking_data)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Continue to export
        self.export_video()
```

## סיכום

✅ **Phase 2 הושלם בהצלחה!**

נוספו:
- UI מלא לסקירת מעקב
- מנתח אוטומטי של בעיות
- גרף confidence אינטראקטיבי
- זיהוי gaps, jumps, size changes
- חישוב ציון איכות
- המלצות לתיקון

**הבא:** Phase 3 - שיפור Confidence ותיקון ידני של bbox

---

**תאריך:** 15 דצמבר 2025
**ענף:** `feature/two-phase-tracking`
**סטטוס:** 🚧 Phase 2 הושלם, Phase 3 בהמתנה
