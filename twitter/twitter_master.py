#!/usr/bin/env python3
"""
Twitter Master for SPZ
Uses Twitter API v2 to fetch tweets and create 5 category XML files
Author: shpitz (Twitter Master)
"""

import urllib.request
import urllib.error
import json
import base64
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone
import time
import os

# ===== TWITTER API CREDENTIALS =====
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAJpO7gEAAAAAdITXzJi0y9gbK%2FSVJMb1w55Wtsg%3DLWVAfOiRvtJkNQpqyekImzZ3iVHvPLTncX5k9CZmOWphr0zsgy"
API_KEY = "aTO7amldSWKWAtDWqOYUUDFQc"
API_SECRET = "zmb3dVB6uccajCs03CpAqlEwK974ikaI7mq8l1Ubs4fREo9jjF"
ACCESS_TOKEN = "146754330-wVLRdPrK8v5oCkd9L9Z8rrcvarqF25wxyTSgaSl6"
ACCESS_SECRET = "UdIdg0zu3IG5JZDqVcMCjWgZexAEXB0sd4tKPEdMU8Xcl"

# ===== 11 TWITTER ACCOUNTS TO MONITOR =====
TWITTER_ACCOUNTS = [
    {"username": "netanyahu", "priority": 1, "category": "israel"},
    {"username": "IsraeliPM", "priority": 1, "category": "israel"},
    {"username": "IDF", "priority": 1, "category": "war"},
    {"username": "IsraelHayom", "priority": 2, "category": "israel"},
    {"username": "ynetalerts", "priority": 1, "category": "breaking"},
    {"username": "BBCWorld", "priority": 2, "category": "world"},
    {"username": "CNN", "priority": 2, "category": "world"},
    {"username": "Reuters", "priority": 2, "category": "world"},
    {"username": "AP", "priority": 2, "category": "world"},
    {"username": "elonmusk", "priority": 3, "category": "tech"},
    {"username": "TechCrunch", "priority": 3, "category": "tech"}
]

OUTPUT_DIR = "twitter_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class TwitterMaster:
    """Fetches tweets from Twitter API v2 and creates 5 category XML files"""
    
    def __init__(self):
        self.bearer_token = BEARER_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': 'SPZ-TwitterBot/1.0'
        }
        self.all_tweets = []
    
    def get_user_id(self, username):
        """Get user ID from username"""
        url = f"https://api.twitter.com/2/users/by/username/{username}"
        
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('data', {}).get('id')
        except Exception as e:
            print(f"  ERR getting user {username}: {str(e)[:40]}")
            return None
    
    def fetch_user_tweets(self, user_id, username, max_results=10):
        """Fetch recent tweets from user"""
        url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results={max_results}&tweet.fields=created_at,public_metrics,context_annotations"
        
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                tweets = data.get('data', [])
                print(f"  OK {len(tweets)} tweets")
                return tweets
        except Exception as e:
            print(f"  ERR: {str(e)[:40]}")
            return []
    
    def calculate_ben_score(self, tweet, account_info):
        """Ben ranking for tweets (1-10)"""
        score = 5.0
        
        metrics = tweet.get('public_metrics', {})
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        # Engagement
        if likes > 10000:
            score += 2.0
        elif likes > 1000:
            score += 1.5
        elif likes > 100:
            score += 1.0
        
        # Retweets (viral potential)
        if retweets > 5000:
            score += 1.5
        elif retweets > 500:
            score += 1.0
        
        # Replies (discussion)
        if replies > 1000:
            score += 1.0
        elif replies > 100:
            score += 0.5
        
        # Priority boost
        if account_info['priority'] == 1:
            score += 0.5
        
        # Israel keywords
        text = tweet.get('text', '').lower()
        israel_keywords = ['israel', 'gaza', 'hamas', 'idf', 'jerusalem', 'netanyahu']
        if any(kw in text for kw in israel_keywords):
            score += 1.0
        
        return min(round(score, 1), 10.0)
    
    def scrape_all(self):
        """Scrape all Twitter accounts"""
        print("=" * 60)
        print("TWITTER MASTER - 11 Accounts")
        print("=" * 60)
        
        for i, account in enumerate(TWITTER_ACCOUNTS, 1):
            print(f"\n[{i}/11] @{account['username']}...")
            
            user_id = self.get_user_id(account['username'])
            if not user_id:
                continue
            
            tweets = self.fetch_user_tweets(user_id, account['username'])
            
            for tweet in tweets:
                tweet['ben_score'] = self.calculate_ben_score(tweet, account)
                tweet['username'] = account['username']
                tweet['category'] = account['category']
                tweet['priority'] = account['priority']
                self.all_tweets.append(tweet)
            
            time.sleep(1)  # Rate limiting
        
        print(f"\nTotal tweets: {len(self.all_tweets)}")
    
    def categorize_and_generate(self):
        """Generate 5 XML files"""
        print("\n" + "=" * 60)
        print("Generating 5 Category XML Files")
        print("=" * 60)
        
        # 1. TOP10 BREAKING
        breaking = sorted(self.all_tweets, key=lambda x: x.get('ben_score', 0), reverse=True)[:10]
        self.generate_xml("twitter_top10_breaking", breaking, "Top 10 Breaking")
        
        # 2. TRENDING NOW (high engagement)
        trending = sorted(self.all_tweets, key=lambda x: x.get('public_metrics', {}).get('like_count', 0), reverse=True)[:10]
        self.generate_xml("twitter_trending_now", trending, "Trending Now")
        
        # 3. ISRAEL
        israel = [t for t in self.all_tweets if t.get('category') == 'israel']
        israel = sorted(israel, key=lambda x: x.get('ben_score', 0), reverse=True)[:10]
        self.generate_xml("twitter_israel", israel, "Israel Related")
        
        # 4. WAR/DEFENSE
        war = [t for t in self.all_tweets if t.get('category') == 'war']
        war = sorted(war, key=lambda x: x.get('ben_score', 0), reverse=True)[:10]
        self.generate_xml("twitter_war", war, "War & Defense")
        
        # 5. WORLD NEWS
        world = [t for t in self.all_tweets if t.get('category') == 'world']
        world = sorted(world, key=lambda x: x.get('ben_score', 0), reverse=True)[:10]
        self.generate_xml("twitter_world", world, "World News")
        
        print("\nDone! 5 files generated.")
    
    def generate_xml(self, filename, tweets, description):
        """Generate XML file"""
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        
        ET.SubElement(channel, "title").text = f"SPZ {description}"
        ET.SubElement(channel, "link").text = f"https://spz.agents/twitter/{filename}"
        ET.SubElement(channel, "description").text = f"{description} - 11 Twitter accounts"
        ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        ET.SubElement(channel, "language").text = "en"
        ET.SubElement(channel, "generator").text = "Twitter Master by shpitz"
        
        for tweet in tweets:
            item = ET.SubElement(channel, "item")
            
            score = tweet.get('ben_score', 5.0)
            text = tweet.get('text', '')
            username = tweet.get('username', '')
            tweet_id = tweet.get('id', '')
            
            ET.SubElement(item, "title").text = f"[{score}/10] @{username}: {text[:100]}..."
            ET.SubElement(item, "link").text = f"https://twitter.com/{username}/status/{tweet_id}"
            ET.SubElement(item, "description").text = text[:280]
            ET.SubElement(item, "twitter_summary").text = f"@{username}: {text[:200]}"
            ET.SubElement(item, "author").text = f"@{username}"
            
            metrics = tweet.get('public_metrics', {})
            ET.SubElement(item, "likes").text = str(metrics.get('like_count', 0))
            ET.SubElement(item, "retweets").text = str(metrics.get('retweet_count', 0))
            ET.SubElement(item, "ben_score").text = str(score)
            
            pub_date = tweet.get('created_at', '')
            if pub_date:
                try:
                    dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    ET.SubElement(item, "pubDate").text = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
                except:
                    pass
            
            ET.SubElement(item, "guid").text = tweet_id
        
        # Pretty print
        rough_string = ET.tostring(rss, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="  ")
        lines = [line for line in pretty.split("\n") if line.strip()]
        
        filepath = f"{OUTPUT_DIR}/{filename}.xml"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"  + {filename}.xml ({len(tweets)} items)")
    
    def run(self):
        """Main execution"""
        try:
            self.scrape_all()
            self.categorize_and_generate()
            
            print("\n" + "=" * 60)
            print(f"Twitter Master Complete!")
            print(f"Tweets scraped: {len(self.all_tweets)}")
            print(f"Output: {OUTPUT_DIR}/")
            print("=" * 60)
        except Exception as e:
            print(f"\nError: {e}")
            print("Note: Twitter API may require elevated access")


def main():
    master = TwitterMaster()
    master.run()


if __name__ == "__main__":
    main()
