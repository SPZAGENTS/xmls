#!/usr/bin/env python3
"""
SPZ Twitter Master - 10 Israeli accounts
Author: קפיץ 🔴🐱
Ranked by Ben Score
"""

import urllib.request
import urllib.error
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone
import time
import os

# Twitter API Key from TOOLS.md
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAJpO7gEAAAAAdITXzJi0y9gbK%2FSVJMb1w55Wtsg%3DLWVAfOiRvtJkNQpqyekImzZ3iVHvPLTncX5k9CZmOWphr0zsgy"

# 10 Israeli Twitter accounts
TWITTER_ACCOUNTS = [
    {"username": "netanyahu", "name": "Benjamin Netanyahu", "priority": 1},
    {"username": "IsraeliPM", "name": "Israeli PM Office", "priority": 1},
    {"username": "IDF", "name": "Israel Defense Forces", "priority": 1},
    {"username": "IsraelHayom", "name": "Israel Hayom", "priority": 2},
    {"username": "ynetalerts", "name": "Ynet Alerts", "priority": 1},
    {"username": "BBCWorld", "name": "BBC World", "priority": 2},
    {"username": "CNN", "name": "CNN", "priority": 2},
    {"username": "Reuters", "name": "Reuters", "priority": 2},
    {"username": "AP", "name": "Associated Press", "priority": 2},
    {"username": "BBCIsrael", "name": "BBC Israel", "priority": 2}
]

OUTPUT_DIR = "twitter_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class TwitterMaster:
    def __init__(self):
        self.bearer_token = BEARER_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': 'SPZ-TwitterBot/1.0'
        }
        self.all_tweets = []
    
    def get_user_id(self, username):
        url = f"https://api.twitter.com/2/users/by/username/{username}"
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                return data.get('data', {}).get('id')
        except Exception as e:
            print(f"ERR {username}: {str(e)[:30]}")
            return None
    
    def fetch_tweets(self, user_id, username, max_results=10):
        url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results={max_results}"
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                tweets = data.get('data', [])
                print(f"  OK {len(tweets)} tweets")
                return tweets
        except Exception as e:
            print(f"  ERR: {str(e)[:30]}")
            return []
    
    def calculate_ben_score(self, tweet, account_info):
        score = 5.0
        
        # Priority boost
        if account_info['priority'] == 1:
            score += 1.0
        
        # Israel keywords
        text = tweet.get('text', '').lower()
        israel_keywords = ['israel', 'gaza', 'hamas', 'idf', 'jerusalem', 'netanyahu']
        if any(kw in text for kw in israel_keywords):
            score += 1.5
        
        # Breaking keywords
        breaking_keywords = ['breaking', 'urgent', 'alert']
        if any(kw in text for kw in breaking_keywords):
            score += 1.0
        
        return min(round(score, 1), 10.0)
    
    def scrape_all(self):
        print("=" * 50)
        print("TWITTER MASTER - 10 Accounts")
        print("=" * 50)
        
        for i, account in enumerate(TWITTER_ACCOUNTS, 1):
            print(f"\n[{i}/10] @{account['username']}...")
            
            user_id = self.get_user_id(account['username'])
            if not user_id:
                continue
            
            tweets = self.fetch_tweets(user_id, account['username'])
            
            for tweet in tweets:
                tweet['ben_score'] = self.calculate_ben_score(tweet, account)
                tweet['username'] = account['username']
                tweet['author_name'] = account['name']
                self.all_tweets.append(tweet)
            
            time.sleep(1)  # Rate limiting
        
        print(f"\nTotal: {len(self.all_tweets)} tweets")
    
    def generate_xml(self):
        print("\n" + "=" * 50)
        print("Generating XML...")
        print("=" * 50)
        
        # Sort by Ben Score
        sorted_tweets = sorted(self.all_tweets, 
                               key=lambda x: x.get('ben_score', 0), 
                               reverse=True)[:10]
        
        # Create RSS
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        
        ET.SubElement(channel, "title").text = "SPZ Twitter Top 10"
        ET.SubElement(channel, "link").text = "https://spz.agents/twitter"
        ET.SubElement(channel, "description").text = "Top 10 Israeli Twitter feeds"
        ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        for tweet in sorted_tweets:
            item = ET.SubElement(channel, "item")
            
            score = tweet.get('ben_score', 5.0)
            text = tweet.get('text', '')
            username = tweet.get('username', '')
            tweet_id = tweet.get('id', '')
            
            ET.SubElement(item, "title").text = f"[{score}/10] @{username}: {text[:80]}..."
            ET.SubElement(item, "link").text = f"https://twitter.com/{username}/status/{tweet_id}"
            ET.SubElement(item, "description").text = text[:200]
            ET.SubElement(item, "twitter_summary").text = f"@{username}: {text[:150]}"
            ET.SubElement(item, "author").text = f"@{username}"
            ET.SubElement(item, "ben_score").text = str(score)
            ET.SubElement(item, "guid").text = tweet_id
        
        # Pretty XML
        rough_string = ET.tostring(rss, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="  ")
        
        filename = f"{OUTPUT_DIR}/twitter_top10.xml"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(pretty)
        
        print(f"+ {filename} ({len(sorted_tweets)} items)")
        
        # Also save JSON
        json_file = f"{OUTPUT_DIR}/twitter_top10.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(sorted_tweets, f, indent=2, ensure_ascii=False)
        print(f"+ {json_file}")
    
    def run(self):
        try:
            self.scrape_all()
            self.generate_xml()
            print("\nTwitter Master Complete!")
        except Exception as e:
            print(f"Error: {e}")

def main():
    master = TwitterMaster()
    master.run()

if __name__ == "__main__":
    main()
