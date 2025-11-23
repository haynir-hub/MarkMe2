# הוראות התקנה - זיהוי אוטומטי (YOLO)

## התקנת תלויות

לזיהוי אוטומטי של אנשים, המערכת משתמשת ב-YOLO (You Only Look Once).

### שלב 1: התקן את התלויות

```bash
pip install ultralytics>=8.0.0
pip install torch>=2.0.0
pip install torchvision>=0.15.0
```

**או התקן הכל בבת אחת:**
```bash
pip install -r docs/requirements.txt
```

### שלב 2: בדוק שההתקנה עובדת

```bash
python -c "from ultralytics import YOLO; print('YOLO installed successfully')"
```

### הערות

- **גודל המודל**: המערכת משתמשת ב-YOLOv8n (nano) - המודל הקטן והמהיר ביותר
- **הורדה אוטומטית**: המודל יורד אוטומטית בפעם הראשונה (כ-6MB)
- **ביצועים**: זיהוי אוטומטי איטי יותר מסימון ידני, אבל מדויק יותר

## שימוש

1. לחץ על "➕ Add Marker"
2. המערכת תזהה אוטומטית את כל האנשים בפריים הנוכחי
3. לחץ על האדם שברצונך לעקוב אחריו
4. בחר שם וסגנון סימון

## פתרון בעיות

**שגיאת "ultralytics not found":**
```bash
pip install ultralytics
```

**שגיאת "torch not found":**
```bash
pip install torch torchvision
```

**זיהוי איטי:**
- זה נורמלי - YOLO דורש עיבוד
- נסה להשתמש בפריים עם פחות אנשים
- או השתמש בסימון ידני (ציור ריבוע)





