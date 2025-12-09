# הוראות העלאה ל-GitHub

## שלב 1: יצירת Repository ב-GitHub

1. היכנס ל-https://github.com/new
2. מלא:
   - **Repository name**: `video-markme` (או שם אחר)
   - **Description**: "Video player tracking and marking system with YOLO detection"
   - בחר **Public** או **Private**
   - **אל תסמן** "Add a README file", "Add .gitignore", או "Choose a license"
3. לחץ על **"Create repository"**

## שלב 2: חיבור ודחיפה

לאחר יצירת ה-repository, GitHub יציג לך הוראות. הנה הפקודות:

### אם זה repository חדש (ריק):

```bash
git remote add origin https://github.com/YOUR_USERNAME/video-markme.git
git branch -M main
git push -u origin main
```

### אם כבר יש לך repository אחר:

```bash
git remote add origin https://github.com/YOUR_USERNAME/video-markme.git
git branch -M main
git push -u origin main
```

**החלף `YOUR_USERNAME` בשם המשתמש שלך ב-GitHub!**

## שלב 3: אימות

אם GitHub יבקש אימות:
- **אם יש לך SSH key**: השתמש ב-SSH URL במקום HTTPS
- **אם אין לך SSH key**: GitHub יבקש ממך שם משתמש וסיסמה (או Personal Access Token)

### יצירת Personal Access Token (אם צריך):

1. היכנס ל-GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. לחץ "Generate new token"
3. בחר הרשאות: `repo` (כל התת-הרשאות)
4. העתק את ה-Token
5. כשתדחוף, השתמש ב-Token במקום הסיסמה

## הערות חשובות:

- ✅ הקובץ `yolov8n.pt` לא יועלה (נמצא ב-.gitignore)
- ✅ קבצי וידאו לא יועלו (נמצאים ב-.gitignore)
- ✅ כל הקבצים האחרים יועלו

## בדיקה שהכל עבד:

לאחר הדחיפה, בדוק ב-GitHub:
- כל הקבצים מופיעים
- ה-README.md נטען כראוי
- הקוד זמין




