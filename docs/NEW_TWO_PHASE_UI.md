# New Two-Phase Tracking UI 🎯

**מערכת מעקב דו-שלבית חדשה - כל המערכת במסך אחד**

---

## ✨ מה חדש?

### 1. ממשק אחד פשוט
- **הכל במסך אחד** - ללא גלילה, ללא תפריטים נסתרים
- וידאו גדול משמאל (60% מהמסך)
- פקדים מסודרים מימין (40% מהמסך)
- גרף קומפקטי למטה

### 2. זיהוי והוספת שחקנים - שתי דרכים!

#### דרך 1: זיהוי אוטומטי (YOLO)
- לחץ "🔍 Detect" → YOLO מוצא דמויות
- **קליק על דמות בווידאו** → פותח דיאלוג להוספת שחקן
- בחר שם + סגנון מרקר → השחקן נוסף לרשימה

#### דרך 2: ציור ידני
- לחץ "✏️ Draw Bbox" (הכפתור ידלק)
- **קליק וגרור** על הווידאו לציור bbox
- שחרר → פותח דיאלוג להוספת שחקן
- בחר שם + סגנון מרקר → השחקן נוסף לרשימה

### 3. רשימת שחקנים חכמה
- כל שחקן עם checkbox (בחר מי לעקוב)
- שם + אייקון מרקר (🏀, 💡, 🎯 וכו')
- כפתורי Edit/Remove

### 4. בקרת טווח מעקב (חיסכון בזמן!)
- **Start Frame / End Frame** - עקוב רק בחלק מהסרטון
- כפתורים מהירים: "Set Current as Start/End"
- דוגמה: עקוב רק מפריים 50 עד 200

### 5. מעקב עם התקדמות
- **▶️ Start Tracking** - מתחיל מעקב (רק על שחקנים מסומנים)
- **⏸️ Stop Tracking** - עוצר באמצע אם צריך
- Progress bar מציג התקדמות
- **🔄 Re-track** - מעקב מחדש אחרי תיקונים

### 6. גרף Confidence אינטראקטיבי
- פס צבעוני קומפקטי
- ירוק = מעקב טוב, כתום = בינוני, אדום = בעיה
- **קליק על הגרף = קפיצה לפריים**

---

## 🚀 איך משתמשים?

### שלב 1: טען וידאו וזהה שחקנים

```python
python test_new_ui.py
```

1. בחר וידאו
2. החלון נפתח → לחץ "🔍 Detect People"
3. YOLO מוצא דמויות (בוקסים ירוקים)
4. **קליק על דמות** → הכנס שם + בחר מרקר
5. חזור על 2-4 עד שכל הדמויות מסומנות

### שלב 2: הגדר טווח (אופציונלי)

- אם רוצה לעקוב רק בחלק מהסרטון:
  - עבור לפריים ההתחלתי → לחץ "⬅️ Set Current as Start"
  - עבור לפריים הסופי → לחץ "➡️ Set Current as End"
- אם רוצה לעקוב בכל הסרטון → אל תשנה כלום

### שלב 3: התחל מעקב

1. **סמן checkboxes** של השחקנים שרוצה לעקוב
2. לחץ "▶️ Start Tracking"
3. המערכת עוברת על הסרטון ויוצרת tracking data
4. progress bar מראה התקדמות
5. אם צריך לעצור → "⏸️ Stop Tracking"

### שלב 4: בדוק תוצאות

1. **גרף ירוק** = הכל טוב ✅
2. **אזורים כתומים/אדומים** = יש בעיות ⚠️
3. קליק על אזור בעייתי → קפיצה לפריים
4. אם צריך תיקון:
   - לחץ "🔍 Detect People" שוב
   - קליק על הדמות הנכונה
   - זה יתקן את הפריים הזה

### שלב 5: Re-track (אם צריך)

- אם תיקנת פריימים → לחץ "🔄 Re-track"
- המערכת תריץ מעקב מחדש עם התיקונים
- בדוק שוב את הגרף

### שלב 6: המשך לייצוא

- כשהכל נראה טוב → "✅ Continue to Export"
- עכשיו המערכת תייצא את הוידאו עם המרקרים

---

## 🎨 פריסת המסך

```
┌────────────────────────────────────────────────────────────┐
│  Two-Phase Tracking - Phase 1                       [X]    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────────┐  ┌──────────────────────┐       │
│  │                     │  │ 👥 Players           │       │
│  │                     │  │ ☑ 🏀 Player 1        │       │
│  │   VIDEO PREVIEW     │  │ ☑ 💡 Player 2        │       │
│  │   (800x450)         │  │ [Edit] [Remove]      │       │
│  │                     │  ├──────────────────────┤       │
│  │   Click detected    │  │ 📹 Tracking Range    │       │
│  │   people to add     │  │ Start: [___0____]    │       │
│  │                     │  │ End:   [__300___]    │       │
│  └─────────────────────┘  ├──────────────────────┤       │
│                           │ ⚙️ Actions            │       │
│  📊 Confidence [▓▓░░▓▓]   │ 🔍 Detect People     │       │
│                           │                      │       │
│  Frame: 45/300            │ ▶️  Start Tracking   │       │
│  [◀] [────●────] [▶]      │ ⏸️  Stop Tracking    │       │
│                           │ 🔄 Re-track          │       │
│  Selected: Player 1       │                      │       │
│  Confidence: 0.85 | Good  │ ✅ Continue Export   │       │
└────────────────────────────────────────────────────────────┘
```

---

## 📝 טיפים ושיפורים

### טיפ 1: איך לבחור פריים טוב לזיהוי?
- בחר פריים שבו כל הדמויות **נראות בבירור**
- לא מטושטשות, לא חסומות
- כך YOLO יזהה אותן בקלות

### טיפ 2: איך לחסוך זמן?
- אם הדמות נכנסת רק בפריים 100:
  - עבור לפריים 100
  - "Set Current as Start"
  - עכשיו המעקב יתחיל מפריים 100 ולא מ-0

### טיפ 3: מה עושים אם YOLO לא מזהה?
- נסה פריים אחר
- או הורד את ה-confidence threshold ב-code:
  ```python
  self.person_detector.detect_people(frame, confidence_threshold=0.15)
  ```

### טיפ 4: איך לעקוב אחרי שתי דמויות?
1. "Detect People" → קליק על דמות 1 → שם "Messi"
2. "Detect People" → קליק על דמות 2 → שם "Ronaldo"
3. סמן את שתי ה-checkboxes
4. "Start Tracking"

---

## 🔧 קוד דוגמה

```python
from PyQt6.QtWidgets import QApplication
from src.tracking.tracker_manager import TrackerManager
from src.ui.two_phase_ui import TwoPhaseTrackingUI

app = QApplication([])

# Create tracker manager
tracker_manager = TrackerManager()
tracker_manager.load_video("my_video.mp4")

# Show UI
dialog = TwoPhaseTrackingUI(tracker_manager)

if dialog.exec():
    # Get tracking data
    tracking_data = dialog.get_tracking_data()

    # Now export with markers...
    print(f"Tracking complete for {len(tracking_data)} players")
```

---

## ⚙️ קבצים חדשים

| File | Purpose |
|------|---------|
| `src/ui/two_phase_ui.py` | ה-UI החדש (880 שורות) |
| `test_new_ui.py` | סקריפט בדיקה |
| `docs/NEW_TWO_PHASE_UI.md` | המדריך הזה |

---

## 🐛 Troubleshooting

### "YOLO Not Available"
```bash
pip install ultralytics
```

### "No people detected"
- נסה פריים אחר
- או הורד confidence threshold

### החלון לא נכנס במסך
- המסך מתאים ל-1500x900
- אם המסך שלך קטן יותר - הממשק יתכווץ אוטומטית
- מינימום: 1400x800

---

## ✅ מה השתפר?

| Before (Old UI) | After (New UI) |
|----------------|---------------|
| ציור ידני של bbox | קליק על דמות מזוהה |
| מספר חלונות | הכל במסך אחד |
| מעקב על כל הסרטון | בחר טווח (חוסך זמן) |
| לא ברור מי מי | שמות + אייקונים |
| לא יודע מתי לעצור | כפתור Stop |
| גרף מסובך | פס קומפקטי |

---

**בהצלחה! 🎬**
