# מעבר למערכת מעקב דו-שלבית (Two-Phase Tracking)

## מטרת השדרוג

המערכת המקורית עובדת במעבר אחד על הסרטון - מתעקבת ומתייגת בו-זמנית. זה יכול לגרום ל:
- פספוסים קטנים במעקב
- איחורים או הקדמות של המרקר
- תקלות שקשה לזהות עד סוף התהליך

**הפתרון: מערכת דו-שלבית**
1. **שלב 1**: מעבר מלא על הסרטון ושמירת נתוני מעקב גולמיים (ללא rendering)
2. **שלב 2**: סקירה אנושית + תיקונים + ייצוא סופי

## מה השתנה?

### קובץ: `src/tracking/tracker_manager.py`

#### פונקציה חדשה: `generate_tracking_data()`

```python
def generate_tracking_data(self, start_frame: int = 0,
                          end_frame: Optional[int] = None,
                          progress_callback=None) -> Dict[int, Dict[int, Dict[str, any]]]
```

**תפקיד:**
- מריצה מעקב על כל ה-players בטווח הפריימים הנתון
- שומרת קואורדינטות + ציון ביטחון (confidence) לכל פריים
- **לא** מרנדרת ווידאו - רק אוספת נתונים

**מבנה הנתונים המוחזר:**
```python
{
    player_id: {
        frame_index: {
            'bbox': (x, y, w, h),           # Bounding box
            'confidence': float,             # ציון ביטחון 0.0-1.0
            'is_learning_frame': bool        # האם זה פריים שהמשתמש סימן ידנית
        }
    }
}
```

**יכולות מיוחדות:**
1. **Confidence tracking** - כל פריים מקבל ציון ביטחון:
   - Learning frames (שסומנו ידנית): 1.0
   - Tracked frames (מעקב אוטומטי): 0.8
   - Lost tracking: 0.0

2. **תאימות לאחור** - הפונקציה גם מעדכנת את `tracking_results` הקיים, כך שהקוד הישן ממשיך לעבוד

3. **סטטיסטיקות מפורטות** - בסוף המעקב, הפונקציה מדפיסה:
   - כמה פריימים עוקבו בהצלחה
   - כמה פריימים אבדו (lost tracking)
   - כמה learning frames נוצלו
   - ציון ביטחון ממוצע

## זרימת העבודה החדשה

### דוגמה 1: שימוש בסיסי
```python
# טען וידאו
tracker_manager.load_video("basketball_game.mp4")

# הוסף שחקנים
tracker_manager.add_player("Player 1", "circle", 0, (100, 100, 50, 80))
tracker_manager.add_player("Player 2", "arrow", 0, (300, 150, 50, 80))

# שלב 1: צור נתוני מעקב
tracking_data = tracker_manager.generate_tracking_data(start_frame=0, end_frame=500)

# שלב 2: סקור את הנתונים (TODO: UI לסקירה ותיקון)
# למצוא פריימים עם confidence נמוך
# להוסיף learning frames במקומות בעייתיים

# שלב 3: ייצוא (משתמש ב-tracking_results שכבר נוצר)
exporter.export_video(...)
```

### דוגמה 2: תיקון פריימים בעייתיים
```python
# רץ מעקב ראשוני
tracking_data = tracker_manager.generate_tracking_data(0, 1000)

# מצא פריימים עם confidence נמוך
for player_id, frames in tracking_data.items():
    for frame_idx, data in frames.items():
        if data['confidence'] < 0.5:  # סף נמוך
            print(f"⚠️ Player {player_id}, Frame {frame_idx}: Low confidence ({data['confidence']})")

# הוסף learning frame לתיקון
tracker_manager.add_learning_frame_to_player(
    player_id=1,
    frame_idx=450,
    bbox=(150, 200, 50, 80)
)

# רץ מעקב מחדש (רק מהפריים המתוקן ואילך)
tracking_data = tracker_manager.generate_tracking_data(450, 1000)
```

## התאמה למבנה הקיים

הפונקציה החדשה **לא משברת** את הקוד הקיים:

1. ✅ משתמשת ב-`PlayerData` הקיים
2. ✅ משתמשת ב-`learning_frames` הקיים
3. ✅ מעדכנת את `tracking_results` לתאימות עם הקוד הישן
4. ✅ תומכת ב-`progress_callback` כמו הקוד הישן
5. ✅ משתמשת באותו `PlayerTracker` (CSRT)

## מה עדיין צריך לפתח?

### Phase 2: UI לסקירה ותיקון (TODO)

1. **Tracking Review Dialog**
   - הצגת הווידאו עם overlays של הנתונים
   - גרף confidence לאורך זמן
   - דגשת פריימים בעייתיים (confidence נמוך)
   - אפשרות לקפוץ לפריימים ספציפיים

2. **Manual Correction UI**
   - קליק על פריים בעייתי
   - סימון מחדש של ה-player (יוסיף learning frame)
   - רענון אוטומטי של המעקב מהנקודה הזו ואילך

3. **Batch Review Mode**
   - סקירה מהירה של פריימים נבחרים (כל 10/20/50)
   - זיהוי אוטומטי של קפיצות חריגות (bbox שקפץ יותר מדי)
   - הצעות אוטומטיות לתיקון

### Phase 3: שיפורי Confidence (TODO)

כרגע הconfidence פשוט מדי:
- Learning frame = 1.0
- Tracked successfully = 0.8
- Lost = 0.0

**שיפורים אפשריים:**
```python
# חישוב confidence מבוסס על מספר פרמטרים:
def calculate_confidence(tracker_score, bbox, prev_bbox, is_learning_frame):
    if is_learning_frame:
        return 1.0

    confidence = 0.5  # בסיס

    # 1. ציון ה-tracker עצמו (אם זמין)
    if tracker_score is not None:
        confidence += tracker_score * 0.3

    # 2. עקביות עם פריים קודם (IoU)
    if prev_bbox:
        iou = calculate_iou(bbox, prev_bbox)
        confidence += iou * 0.2

    # 3. גודל ה-bbox סביר?
    bbox_size = bbox[2] * bbox[3]
    if 1000 < bbox_size < 50000:  # גודל סביר
        confidence += 0.1

    return min(confidence, 1.0)
```

## סטטוס הפיתוח

- ✅ **משימה 1 הושלמה**: פונקציה `generate_tracking_data()` נוספה
- ⏳ **משימה 2**: UI לסקירה ותיקון
- ⏳ **משימה 3**: שיפור חישוב confidence
- ⏳ **משימה 4**: זיהוי אוטומטי של בעיות
- ⏳ **משימה 5**: אופטימיזציה (re-tracking חכם - רק מהפריים המתוקן)

## הוראות שימוש נוכחיות

כרגע הפונקציה זמינה אבל **אין עדיין UI** לסקירה ותיקון.

**שימוש דרך קוד:**
```python
# בקובץ batch_exporter.py או במקום אחר
tracking_data = tracker_manager.generate_tracking_data(
    start_frame=0,
    end_frame=None,  # עד הסוף
    progress_callback=lambda curr, total: print(f"{curr}/{total}")
)

# בדוק את הנתונים
for player_id in tracking_data:
    low_conf_frames = [
        f for f, data in tracking_data[player_id].items()
        if data['confidence'] < 0.6
    ]
    print(f"Player {player_id}: {len(low_conf_frames)} frames with low confidence")
```

---

**תאריך יצירה:** 15 דצמבר 2025
**ענף:** `feature/two-phase-tracking`
**סטטוס:** 🚧 בפיתוח - Phase 1 הושלמה
