# תיקון בעיית הסאונד - Video Markme

## הבעיה
הקבצים המיוצאים מהמערכת יוצאים ללא סאונד.

## הסיבה
המערכת משתמשת ב-FFmpeg כדי להעתיק את האודיו מהסרטון המקורי לסרטון המעובד.
אם FFmpeg לא מותקן במערכת, הסרטונים יוצאים ללא סאונד.

## הפתרון

### שלב 1: בדוק אם FFmpeg מותקן
פתח טרמינל והרץ:
```bash
ffmpeg -version
```

אם אתה רואה גרסה - FFmpeg מותקן ✅
אם אתה רואה "command not found" - עבור לשלב 2 ❌

### שלב 2: התקן FFmpeg

#### macOS (המערכת שלך):

**אופציה 1 - באמצעות הסקריפט המוכן:**
```bash
cd "/Users/haynir/Documents/My Programs/Video Markme"
chmod +x scripts/install_ffmpeg.sh
./scripts/install_ffmpeg.sh
```

**אופציה 2 - התקנה ידנית:**

אם אין לך Homebrew, התקן אותו תחילה:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

לאחר מכן התקן FFmpeg:
```bash
brew install ffmpeg
```

### שלב 3: ודא שההתקנה הצליחה
```bash
ffmpeg -version
```

אמור להראות משהו כמו:
```
ffmpeg version 6.1.1 Copyright (c) 2000-2023 the FFmpeg developers
...
```

### שלב 4: נסה שוב לייצא וידאו
עכשיו כשתייצא וידאו מהמערכת, הסאונד אמור להישמר! 🎉

## שיפורים שבוצעו

הקוד עודכן עם אסטרטגיות מרובות להוספת אודיו:

1. **אסטרטגיה 1** (הכי מהירה): העתקת stream של הווידאו והאודיו ללא re-encoding
2. **אסטרטגיה 2** (חלופה): re-encode של הווידאו עם שימור איכות האודיו
3. **אסטרטגיה 3** (fallback): שמירת וידאו ללא אודיו אם כל השאר נכשל

כעת המערכת תנסה את כל האסטרטגיות עד שאחת תצליח, ותיתן לך הודעות ברורות על מה קורה.

## פרטים טכניים

הקוד המעודכן נמצא ב-`src/render/video_exporter.py` בפונקציה `_add_audio_with_ffmpeg`.

השיפור כולל:
- שימוש ב-AAC codec לאודיו (תמיכה רחבה)
- Bitrate גבוה לאודיו (192k)
- טיפול בשגיאות משופר
- הודעות ברורות למשתמש
