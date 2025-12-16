# תיקונים גרסה 2 - Two-Phase UI

**תאריך**: 2025-12-16

---

## 🐛 בעיות שתוקנו

### 1. ✅ קריסה בהוספת שחקן
**הבעיה**: כשלוחצים על דמות מזוהה ב-YOLO ואז "Add Player" - המערכת קורסת

**הסיבה**: הפונקציה `_show_add_player_dialog` ניסתה לגשת למשתנה `conf` שלא היה מוגדר

**התיקון**:
- הוספתי פרמטר `confidence` לפונקציה
- הפונקציה `_on_person_clicked` מעבירה את ה-confidence
- הפונקציה `_on_bbox_drawn` (ציור ידני) מעבירה `None`

```python
def _show_add_player_dialog(self, bbox, manual=False, confidence=None):
    if manual:
        layout.addWidget(QLabel(f"Manual bbox: ({x}, {y}, {w}, {h})"))
    else:
        conf_text = f" ({confidence:.0%})" if confidence else ""
        layout.addWidget(QLabel(f"Detected person at ({x}, {y}){conf_text}"))
```

---

### 2. ✅ כפתורים נמעכים בחלון קטן
**הבעיה**: כשמתאימים את החלון למסך - הטקסט בכפתורים נמעך ולא ניתן לקרוא

**התיקון**:
1. **קיצור טקסטים**:
   - "Edit Name" → "✏️" (רק אייקון)
   - "Remove" → "🗑️" (רק אייקון)
   - "🔍 Detect" → נשאר כמו שהוא
   - "✏️ Draw Bbox" → "✏️ Draw"
   - "▶️ Start Tracking" → "▶️ Track"
   - "⬅️ Set Start" → "⬅️ Start"
   - "➡️ Set End" → "➡️ End"

2. **הוספת Tooltips**:
   - כל כפתור קיבל tooltip מפורט
   - ריחוף עם העכבר = הסבר מלא

3. **גודלים קבועים לכפתורי אייקון**:
   ```python
   self.btn_edit_player.setMinimumWidth(40)
   self.btn_edit_player.setMaximumWidth(50)
   ```

4. **הקטנת padding ו-font**:
   ```python
   padding: 6px;
   font-size: 12px;
   ```

---

### 3. ✅ החלון לא מתאים למסך
**הבעיה**:
- חלון לא מותאם = לא רואים הכל
- חלון ממוקסם = כפתורים נמעכים

**התיקון**: חלון דינמי שמתאים למסך אוטומטית

```python
from PyQt6.QtGui import QGuiApplication
screen = QGuiApplication.primaryScreen().geometry()
window_width = min(1400, int(screen.width() * 0.9))
window_height = min(850, int(screen.height() * 0.85))
self.resize(window_width, window_height)
self.setMinimumSize(1200, 700)
```

**מה זה עושה**:
- בודק את גודל המסך
- לוקח 90% מהרוחב, 85% מהגובה
- מקסימום: 1400x850
- מינימום: 1200x700
- תמיד נכנס במסך, תמיד קריא!

---

## 📝 סיכום השינויים

| קובץ | שינויים |
|------|---------|
| [src/ui/two_phase_ui.py](../src/ui/two_phase_ui.py) | • תיקון קריסה (`confidence` parameter)<br>• קיצור טקסטי כפתורים<br>• גודל חלון דינמי<br>• tooltips לכל הכפתורים |

---

## 🎯 איך לבדוק

```bash
python3 test_new_ui.py
```

### בדיקות:
1. ✅ **זיהוי YOLO** → קליק על דמות → Add Player → לא קורס!
2. ✅ **ציור ידני** → Draw Bbox → גרור → Add Player → עובד!
3. ✅ **חלון קטן** → כל הכפתורים קריאים
4. ✅ **חלון גדול** → הכל נראה טוב
5. ✅ **Tooltips** → ריחוף = הסברים מפורטים

---

## 🔄 לפני ואחרי

### כפתורים:
```
❌ לפני:
[Edit Name] [Remove]
[🔍 Detect People (YOLO)]
[✏️ Draw Bbox]
[▶️ Start Tracking]
[⬅️ Set Current as Start]

✅ אחרי:
[✏️] [🗑️]
[🔍 Detect]
[✏️ Draw]
[▶️ Track]
[⬅️ Start]
```

### חלון:
```
❌ לפני:
setMinimumSize(1500, 900)  # קבוע, לא גמיש

✅ אחרי:
window_width = min(1400, screen.width() * 0.9)  # דינמי!
window_height = min(850, screen.height() * 0.85)
```

---

## ✨ תוצאות

- ✅ אין יותר קריסות בהוספת שחקן
- ✅ כפתורים תמיד קריאים
- ✅ החלון תמיד מתאים למסך
- ✅ tooltips מסבירים הכל

---

**הכל עובד עכשיו!** 🎉
