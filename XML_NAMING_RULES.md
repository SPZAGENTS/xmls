# 🔴 CRITICAL RULE: XML File Naming Convention

**Repository:** SPZAGENTS/xmls  
**Branch:** main  
**Created:** 2026-03-09  
**By:** Yossi instruction to Shpitzi

---

## ⚠️ NEVER CHANGE RULE

**חוק קבוע לנצח:**

"אסור לשנות שמות קבצים XML! תמיד לעדכן את הקבצים הקיימים בלבד!"

---

## ✅ מותר לעשות:

1. **עדכון תוכן** — החלפת XML בתוכן חדש
2. **Overwrite** — שכתוב קובץ קיים
3. **Commit regular** — עם timestamps עדכניים
4. **Git operations:**
   ```bash
   git checkout main
   git pull origin main
   # עדכן קבצים קיימים
   git add .
   git commit -m "update: [description]"
   git push origin main
   ```

---

## ❌ אסור לגמרי:

1. **שינוי שמות קבצים**
   - ❌ ynet-top.xml → ynet-top-new.xml
   - ❌ bbc_uk.xml → bbc-uk.xml (ללא underscore)

2. **מחיקה ויצירה מחדש**
   - ❌ למחוק וליצור קובץ בשם אחר

3. **העברה לתת-תיקיות**
   - ❌ root/ → international/

4. **יצירת קבצים חדשים במקום עדכון**
   - ❌ במקום לעדכן ynet-top.xml, ליצור ynet-top-v2.xml

---

## 🎯 הסיבה:

**SPZAGENTS systems rely on these URLs being STABLE.**

שינוי שם = שבירת אינטגרציות של מערכות אחרות שמסתמכות על URLs קבועים.

---

## 📁 הקבצים (120+ קבצים קבועים):

### Israeli Sources:
- ynet-top.xml, ynet-all.xml
- israel-hayom-top.xml, israel-hayom-all.xml
- maariv-top.xml, maariv-all.xml
- haaretz-top.xml, haaretz-all.xml
- times-of-israel-top.xml, times-of-israel-all.xml
- arutz-sheva-top.xml, arutz-sheva-all.xml
- ICE-top.xml, ICE-all.xml
- ועוד...

### International Sources:
- bbc_uk.xml, bbc_middle_east.xml, bbc_world.xml
- fox_news.xml, fox_news_world.xml
- nyt_world.xml, nyt_middle_east.xml
- guardian_world.xml, guardian_middle_east.xml
- france24.xml, france24_middle_east.xml
- politico.xml, washington_post.xml, washington_post_politics.xml
- abc_news.xml, abc_news_international.xml
- npr_world.xml, cbc_world.xml
- international-master.xml, international-war.xml
- ועוד...

### Reddit Sources:
- reddit-aggregate.xml, reddit-war.xml, reddit-conflict-war.xml
- reddit-global-news.xml, reddit-israel-jewish.xml
- reddit-middle-east.xml, reddit-military-analysis.xml
- reddit-israel.xml, reddit-palestine.xml
- ועוד 40+ קבצים...

---

## 🔧 GitHub Branch Note:

**CRITICAL:** The repo uses `main`, not `master`!

```bash
# Check current branch
git branch -vv

# Should see:
# * main  [origin/main] ...
#   remotes/origin/HEAD -> origin/main  <-- KEY!

# If on master, switch:
git checkout main
git pull origin main
```

---

## 📍 URL Pattern:

```
https://raw.githubusercontent.com/SPZAGENTS/xmls/main/{filename}.xml
```

Example:
```
https://raw.githubusercontent.com/SPZAGENTS/xmls/main/ynet-top.xml
https://raw.githubusercontent.com/SPZAGENTS/xmls/main/bbc_uk.xml
```

---

## 📝 תיעוד הקבצים המלא:

ראה: `SPZ_XML_URLS_FIXED.md` בריפו — רשימה מלאה של כל ה-120+ קבצים עם URLs.

---

**Last updated:** 2026-03-09 by Shpitzi 🦔
**Rule confirmed by:** Yossi
**Status:** PERMANENT — NEVER TO BE CHANGED
