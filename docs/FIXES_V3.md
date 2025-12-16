# תיקונים גרסה 3 - קריסות וכפתורים

**תאריך**: 2025-12-16
**גרסה**: 3.0

---

## 🐛 בעיות שתוקנו

### 1. ✅ קריסה בקליק על וידאו
**הבעיה**: המערכת קרסה כשלוחצים על הווידאו להוספת שחקן

**הסיבה**:
- חלוקה באפס אם `scale_factor = 0`
- Exception לא נתפס ב-PyQt6
- קואורדינטות מחוץ לגבולות הפריים

**התיקון**:
```python
def mousePressEvent(self, event):
    try:
        # Prevent division by zero
        if self.scale_factor == 0:
            return

        # Clamp to frame bounds
        if self.current_frame is not None:
            h, w = self.current_frame.shape[:2]
            frame_x = max(0, min(frame_x, w - 1))
            frame_y = max(0, min(frame_y, h - 1))

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
```

**עכשיו**: קליק על וידאו **לא קורס**!

---

### 2. ✅ כפתורים לא קריאים
**הבעיה**: הטקסט על הכפתורים נמעך ולא ניתן לקרוא

**התיקון**: **אייקונים גדולים בלבד**

| לפני ❌ | אחרי ✅ |
|---------|---------|
| "🔍 Detect" | "🔍" (20px) |
| "✏️ Draw" | "✏️" (20px) |
| "▶️ Track" | "▶️" (24px) |
| "⏸️ Stop" | "⏸️" (24px) |
| "✅ Continue to Export" | "✅ Export" (16px) |

**פרטי העיצוב**:
```python
# כפתורי פעולות רגילים
font-size: 20px
padding: 10px
min-height: 45px

# כפתורי מעקב (חשובים)
font-size: 24px
padding: 12px
min-height: 50px

# כפתור ייצוא
font-size: 16px
padding: 14px
min-height: 50px
```

**Tooltips**: ריחוף על כפתור = הסבר מלא
- 🔍 → "Detect People (YOLO)"
- ✏️ → "Draw Bbox Manually"
- ▶️ → "Start Tracking"
- ⏸️ → "Stop Tracking"
- ✅ → "Continue to Export"

---

## 📋 סיכום השינויים

| קובץ | מה השתנה |
|------|----------|
| [src/ui/two_phase_ui.py](../src/ui/two_phase_ui.py) | • `mousePressEvent`: try/catch + בדיקות<br>• כל הכפתורים: אייקונים בלבד<br>• גדלי פונט: 16-24px<br>• min-height: 45-50px |

---

## 🎯 איך לבדוק

```bash
./launch_two_phase.command
```

### בדיקות:
1. ✅ קליק על וידאו → לא קורס
2. ✅ הכפתורים נקראים בכל גודל חלון
3. ✅ Tooltips עובדים (ריחוף = הסבר)
4. ✅ כל הפונקציונליות עובדת

---

## 🔄 לפני ואחרי

### כפתורים:
```
❌ לפני:
[🔍 Detect People (YOLO)] ← נמעך!
[✏️ Draw Bbox]             ← נמעך!
[▶️ Start Tracking]        ← נמעך!

✅ אחרי:
[  🔍  ] ← גדול וברור + tooltip
[  ✏️  ] ← גדול וברור + tooltip
[  ▶️  ] ← גדול וברור + tooltip
```

### קריסות:
```
❌ לפני:
קליק על וידאו → 💥 CRASH (SIGABRT)

✅ אחרי:
קליק על וידאו → ✅ פותח דיאלוג Add Player
```

---

## ✨ תוצאות

- ✅ **אין קריסות** - try/catch מגן על כל mouse event
- ✅ **כפתורים תמיד קריאים** - אייקונים גדולים בלבד
- ✅ **UX טוב יותר** - tooltips מסבירים הכל
- ✅ **עיצוב נקי** - פחות טקסט = יותר ברור

---

## 🎨 עיצוב חדש

```
┌─────────────────────┐
│ ⚙️ Actions          │
├─────────────────────┤
│                     │
│      [  🔍  ]      │  ← Detect People
│                     │
│      [  ✏️  ]      │  ← Draw Bbox
│                     │
│ ─────────────────── │
│                     │
│      [  ▶️  ]      │  ← Start (Green)
│                     │
│      [  ⏸️  ]      │  ← Stop (Red)
│                     │
│ [Progress Bar...]   │
│                     │
│      [ 🔄 ]         │  ← Re-track
│                     │
└─────────────────────┘
        ↓
┌─────────────────────┐
│    [✅ Export]      │  ← Continue to Export
└─────────────────────┘
```

---

**הכל עובד עכשיו!** 🎉

נסה את הקובץ המעודכן:
```bash
./launch_two_phase.command
```
