# SPZ XML Generation Guide — Updated 🆕
**Date:** 2026-02-28  
**Version:** 2.0 (overwrite approach)

---

## ⚠️ שינויי מהותיים (2026-02-28)

### מה שונה:
**מבנה הקבצים השתנה!**

| לפני (לא נכון) ❌ | אחרי (נכון) ✅ |
|------------------|---------------|
| `{source}_{YYYYMMDD}_{HHMM}.xml` | `{source}.xml` |
| כפילויות — קובץ חדש כל מחזור | קובץ אחד בלבד |
| 146 קבצים ב-repo | 29 קבצים ב-repo |

---

## 📋 כללי עדכון חדשים

### 1. שם קובץ
```python
# לא נכון ❌
filename = f"ynet-main_{datetime.now().strftime('%Y%m%d_%H%M')}.xml"

# נכון ✅  
filename = "ynet-main.xml"
```

### 2. overwrite במקום create
```python
# לא נכון ❌
# יוצר קובץ חדש בכל ריצה

# נכון ✅
# דורס קובץ קיים (overwrite)
with open(filename, 'w', encoding='utf-8') as f:
    f.write(xml_content)
```

### 3. מספר כתבות
```
✅ חובה: מקסימום 10 כתבות בכל קובץ
✅ חובה: top 10 לפי Ben's Ranking
❌ אסור: יותר מ-10 כתבות
```

### 4. מבנה ה-XML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<content-feed>
  <source>ynet-main</source>
  <source-type>rss</source-type>
  <generated>2026-02-28T06:00:00+02:00</generated>
  <count>10</count>
  
  <item id="1" rank="95">
    <title>...</title>
    <summary>...</summary>
    <link>...</link>
    <published>...</published>
    <original-source>ynet</original-source>
    <category>breaking</category>
    <image>...</image>
  </item>
  
  <!-- עוד 9 items -->
  
</content-feed>
```

---

## 🔧 קוד Python לדוגמה

### פונקציית שמירה נכונה
```python
def save_xml_to_file(source_name, xml_content):
    """
    Save XML file with OVERWRITE approach
    Single file per source, no timestamps
    """
    filename = f"{source_name}.xml"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # overwrite existing file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    return filepath
```

### פונקציית עדכון Git
```python
def commit_to_github():
    """
    Commit with clear message
    """
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run([
        'git', 'commit', 
        '-m', f'Update {source_name}: Top 10 articles for {datetime.now():%Y-%m-%d %H:%M}'
    ], check=True)
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)
```

---

## 📁 מבנה הריפו אחרי ניקוי

```
SPZAGENTS/xmls/
├── arutz-sheva-news.xml     (10 כתבות)
├── bbc-middle-east.xml       (10 כתבות)
├── bbc-news.xml             (10 כתבות)
├── bbc-world-news.xml       (10 כתבות)
├── cnn-top-stories.xml      (10 כתבות)
├── globes-business.xml      (10 כתבות)
├── haaretz-israel-news.xml  (10 כתבות)
├── israel-hayom.xml         (10 כתבות)
├── jerusalem-post.xml       (10 כתבות)
├── maariv-news.xml          (10 כתבות)
├── mako-news.xml            (10 כתבות)
├── nbc-news.xml             (10 כתבות)
├── nyt-homepage.xml         (10 כתבות)
├── the-guardian-world.xml   (10 כתבות)
├── times-of-israel.xml      (10 כתבות)
├── walla-news.xml           (10 כתבות)
├── ynet-breaking.xml        (10 כתבות)
├── ynet-main.xml            (10 כתבות)
├── ynet-tech.xml            (10 כתבות)
├── ... (ועוד 9 קבצים)

סה"כ: 29 קבצים (לא 146!)
```

---

## ⚡ סיכום

| פרמטר | ערך |
|-------|-----|
| קבצים | 29 בלבד |
| עדכון | overwrite (לא חדש) |
| כתבות | 10 לכל קובץ |
| שמות | ללא timestamp |
| Goal | קובץ אחד בלבד למקור |

---

## 🔗 קישורים

- Repo: https://github.com/SPZAGENTS/xmls
- Cleanup Script: `cleanup_xml_duplicates.py`

---

*עודכן על ידי שפיץ 🦔 וקפיץ 🐱 | 2026-02-28*
