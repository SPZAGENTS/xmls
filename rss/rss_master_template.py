#!/usr/bin/env python3
"""
RSS Master for SPZ - RSS Scraper
Author: shpitz 2.0 (RSS Master)
"""

import urllib.request
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone
import time
import os

# ===== 7 RSS FEEDS =====
RSS_FEEDS = {
    "ynet": {
        "url": "https://www.ynet.co.il/Integration/StoryRss1854.xml",
        "name": "Ynet",
        "category": "israel"
    },
    "timesofisrael": {
        "url": "https://www.timesofisrael.com/feed/",
        "name": "Times of Israel",
        "category": "israel"
    },
    "israelhayom": {
        "url": "https://www.israelhayom.co.il/rss.xml",
        "name": "Israel Hayom",
        "category": "israel"
    },
    "walla": {
        "url": "https://rss.walla.co.il/feed/22",
        "name": "Walla",
        "category": "israel"
    },
    "bbc": {
        "url": "http://feeds.bbci.co.uk/news/middle_east/rss.xml",
        "name": "BBC",
        "category": "world"
    },
    "nyt": {
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "name": "New York Times",
        "category": "world"
    },
    "guardian": {
        "url": "https://www.theguardian.com/world/rss",
        "name": "Guardian",
        "category": "world"
    }
}

OUTPUT_DIR = "rss_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_rss(feed_id, feed_info):
    """Fetch RSS feed and parse items"""
    try:
        print(f"Fetching {feed_info['name']}...")
        req = urllib.request.Request(feed_info['url'], headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
            root = ET.fromstring(data)
            
            items = []
            # Handle RSS 2.0 and Atom formats
            channel = root.find('.//channel') or root
            for item in channel.findall('.//item')[:25]:  # Get top 25
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pub_date = item.find('pubDate')
                
                items.append({
                    'title': title.text if title is not None else '',
                    'link': link.text if link is not None else '',
                    'description': (description.text if description is not None else '')[:500],
                    'pub_date': pub_date.text if pub_date is not None else '',
                    'source': feed_info['name'],
                    'category': feed_info['category']
                })
            
            print(f"  OK {len(items)} items")
            return items
            
    except Exception as e:
        print(f"  ERR {str(e)[:40]}")
        return []
    finally:
        time.sleep(1)


def calculate_ben_score(item):
    """Ben ranking for RSS items (simplified)"""
    score = 5.0
    title = item['title'].lower()
    
    # Israel keywords boost
    israel_keywords = ['israel', 'gaza', 'hamas', 'idf', 'jerusalem', 'netanyahu']
    if any(kw in title for kw in israel_keywords):
        score += 1.5
    
    # Breaking news keywords
    breaking_keywords = ['breaking', 'urgent', 'alert', 'update']
    if any(kw in title for kw in breaking_keywords):
        score += 1.0
    
    # War/conflict keywords
    war_keywords = ['war', 'attack', 'strike', 'military', 'defense']
    if any(kw in title for kw in war_keywords):
        score += 0.5
    
    return min(round(score, 1), 10.0)


def generate_xml(feed_id, items, feed_info):
    """Generate XML file for RSS feed"""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = f"SPZ {feed_info['name']}"
    ET.SubElement(channel, "link").text = feed_info['url']
    ET.SubElement(channel, "description").text = f"Top 10 from {feed_info['name']}"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    ET.SubElement(channel, "language").text = "en"
    ET.SubElement(channel, "generator").text = "SPZ RSS Master"
    
    # Calculate scores and sort
    for item in items:
        item['ben_score'] = calculate_ben_score(item)
    
    sorted_items = sorted(items, key=lambda x: x['ben_score'], reverse=True)[:10]
    
    for item in sorted_items:
        xml_item = ET.SubElement(channel, "item")
        
        ET.SubElement(xml_item, "title").text = f"[{item['ben_score']}/10] {item['title'][:140]}"
        ET.SubElement(xml_item, "link").text = item['link']
        ET.SubElement(xml_item, "description").text = item['description'][:280]
        ET.SubElement(xml_item, "twitter_summary").text = f"{item['source']}: {item['title'][:200]}"
        ET.SubElement(xml_item, "source").text = item['source']
        ET.SubElement(xml_item, "category").text = item['category']
        ET.SubElement(xml_item, "ben_score").text = str(item['ben_score'])
        
        if item['pub_date']:
            ET.SubElement(xml_item, "pubDate").text = item['pub_date']
    
    # Pretty print
    rough_string = ET.tostring(rss, encoding="unicode")
    reparsed = minidom.parseString(rough_string)
    pretty = reparsed.toprettyxml(indent="  ")
    lines = [line for line in pretty.split("\n") if line.strip()]
    
    filename = f"rss_{feed_id}.xml"
    filepath = f"{OUTPUT_DIR}/{filename}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"  + {filename} ({len(sorted_items)} items)")
    return filename


def main():
    """Main execution"""
    print("=" * 60)
    print("RSS MASTER - 7 Feeds")
    print("=" * 60)
    
    generated_files = []
    
    for feed_id, feed_info in RSS_FEEDS.items():
        print(f"\n[{len(generated_files)+1}/7]", end=" ")
        items = fetch_rss(feed_id, feed_info)
        
        if items:
            filename = generate_xml(feed_id, items, feed_info)
            generated_files.append(filename)
    
    print("\n" + "=" * 60)
    print(f"Generated {len(generated_files)} XML files:")
    for f in generated_files:
        print(f"  - {f}")
    print(f"Output: {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
