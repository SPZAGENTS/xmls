#!/usr/bin/env python3
"""
Ground Zero Complete Codebook - Viral Content Analyzer
Scans 295 Reddit posts and assigns 0-100 scores based on 6 weighted metrics
Categories: PRIORITY_ALERT (≥80), CANDIDATE (≥60), INTERESTING (≥40)
Author: Pitzi 🐱
"""

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone
from collections import Counter
import re
import os
import glob

# ===== CONFIGURATION =====
INPUT_DIR = "spz-config/reddit_outputs_v3"  # Source XML files
OUTPUT_DIR = "ground_zero_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== 6 WEIGHTED METRICS =====
METRICS = {
    'language_diversity': 0.20,      # 20%
    'keyword_richness': 0.25,        # 25%
    'authenticity': 0.20,             # 20%
    'viral_velocity': 0.15,         # 15%
    'account_signals': 0.10,        # 10%
    'geolocation': 0.10               # 10%
}

# ===== THRESHOLDS =====
THRESHOLDS = {
    'PRIORITY_ALERT': 80,
    'CANDIDATE': 60,
    'INTERESTING': 40
}

# ===== KEYWORD DICTIONARIES =====
ISRAEL_KEYWORDS = [
    'israel', 'israeli', 'palestine', 'palestinian', 'gaza', 'gazan',
    'hamas', 'hezbollah', 'iran', 'iranian', 'netanyahu', 'jerusalem',
    'tel aviv', 'west bank', 'idf', 'defense forces', 'mossad',
    'zionist', 'zionism', 'jewish', 'jew', 'jews', 'antisemitism',
    'kibbutz', 'settlements', 'two state', 'ceasefire', 'hostage',
    'hostages', 'war', 'conflict', 'missile', 'rocket', 'attack',
    'terror', 'terrorist', 'security', 'defense', 'military'
]

ENGAGEMENT_KEYWORDS = [
    'breaking', 'exclusive', 'urgent', 'alert', 'update',
    'developing', 'live', 'just', 'now', 'happening',
    'shocking', 'massive', 'huge', 'major', 'critical'
]

HIGH_VALUE_SOURCES = [
    'reuters', 'ap', 'associated press', 'bbc', 'cnn', 'nyt',
    'wsj', 'ft', 'bloomberg', 'al jazeera', 'haaretz',
    'times of israel', 'jerusalem post', 'ynet'
]

class GroundZeroAnalyzer:
    """Analyzes posts for viral potential"""
    
    def __init__(self):
        self.all_posts = []
        self.scored_posts = []
    
    def load_posts_from_xml(self, xml_file):
        """Load posts from XML file"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            posts = []
            for item in root.findall('.//item'):
                post = {
                    'title': item.findtext('title', ''),
                    'link': item.findtext('link', ''),
                    'description': item.findtext('description', ''),
                    'author': item.findtext('author', ''),
                    'pubDate': item.findtext('pubDate', ''),
                    'score': self._extract_score(item.findtext('score', '0')),
                    'comments': self._extract_score(item.findtext('comments', '0')),
                    'source': item.findtext('source', ''),
                    'reddit_permalink': item.findtext('reddit_permalink', '')
                }
                posts.append(post)
            
            return posts
        except Exception as e:
            print(f"  ✗ Error loading {xml_file}: {e}")
            return []
    
    def _extract_score(self, text):
        """Extract numeric score from text"""
        try:
            return int(re.findall(r'\d+', str(text))[0]) if text else 0
        except:
            return 0
    
    def calculate_language_diversity(self, post):
        """Score based on diverse vocabulary and sentence structure"""
        title = post['title'].lower()
        desc = post['description'].lower()
        text = f"{title} {desc}"
        
        # Count unique words
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return 0
        
        unique_words = len(set(words))
        total_words = len(words)
        diversity_ratio = unique_words / total_words if total_words > 0 else 0
        
        # Bonus for varied sentence lengths
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        length_variance = max(sentence_lengths) - min(sentence_lengths) if len(sentence_lengths) > 1 else 0
        
        score = (diversity_ratio * 50) + (min(length_variance, 10) * 2)
        return min(round(score), 20)  # Cap at 20 (for 20% weight)
    
    def calculate_keyword_richness(self, post):
        """Score based on relevant keywords"""
        title = post['title'].lower()
        desc = post['description'].lower()
        text = f"{title} {desc}"
        
        score = 0
        
        # Israel/ME keywords (high value)
        israel_matches = sum(1 for kw in ISRAEL_KEYWORDS if kw in text)
        score += min(israel_matches * 2, 15)
        
        # Engagement keywords
        engagement_matches = sum(1 for kw in ENGAGEMENT_KEYWORDS if kw in text)
        score += min(engagement_matches * 1.5, 10)
        
        return min(round(score), 25)  # Cap at 25 (for 25% weight)
    
    def calculate_authenticity(self, post):
        """Score based on source credibility and content markers"""
        score = 10  # Base score
        
        # Check for high-value sources
        combined_text = f"{post['title']} {post['description']}".lower()
        for source in HIGH_VALUE_SOURCES:
            if source in combined_text:
                score += 5
        
        # Bonus for substantial content
        if len(post['description']) > 200:
            score += 3
        
        # Check for quotes (indicates reporting)
        if '"' in post['description'] or '"' in post['title']:
            score += 2
        
        return min(score, 20)  # Cap at 20 (for 20% weight)
    
    def calculate_viral_velocity(self, post):
        """Score based on engagement velocity indicators"""
        score = 0
        
        # Reddit score
        reddit_score = post.get('score', 0)
        if reddit_score > 1000:
            score += 10
        elif reddit_score > 500:
            score += 7
        elif reddit_score > 100:
            score += 5
        elif reddit_score > 50:
            score += 3
        
        # Comments (higher ratio = more engagement)
        comments = post.get('comments', 0)
        if comments > 500:
            score += 5
        elif comments > 200:
            score += 3
        elif comments > 50:
            score += 1
        
        return min(score, 15)  # Cap at 15 (for 15% weight)
    
    def calculate_account_signals(self, post):
        """Score based on account/post metadata signals"""
        score = 5  # Base score
        
        # Check if has author
        if post.get('author') and post['author'] not in ['', '[deleted]']:
            score += 3
        
        # Has source attribution
        if post.get('source'):
            score += 2
        
        return min(score, 10)  # Cap at 10 (for 10% weight)
    
    def calculate_geolocation(self, post):
        """Score based on geographic relevance"""
        text = f"{post['title']} {post['description']}".lower()
        score = 0
        
        # Israel/Palestine locations
        locations = [
            'israel', 'palestine', 'gaza', 'jerusalem', 'tel aviv',
            'west bank', 'haifa', 'beirut', 'damascus', 'tehran',
            'cairo', 'amman', 'baghdad', 'riyadh', 'dubai'
        ]
        
        for loc in locations:
            if loc in text:
                score += 2
        
        return min(score, 10)  # Cap at 10 (for 10% weight)
    
    def calculate_total_score(self, post):
        """Calculate weighted total score (0-100)"""
        scores = {
            'language_diversity': self.calculate_language_diversity(post),
            'keyword_richness': self.calculate_keyword_richness(post),
            'authenticity': self.calculate_authenticity(post),
            'viral_velocity': self.calculate_viral_velocity(post),
            'account_signals': self.calculate_account_signals(post),
            'geolocation': self.calculate_geolocation(post)
        }
        
        # Apply weights
        total = 0
        for metric, score in scores.items():
            weight = METRICS[metric]
            # Score is already capped for the weight, just sum
            total += score * (100 / 20)  # Normalize back
        
        # Re-normalize to 0-100
        final_score = round(total * 0.2)  # 20% from each metric cap
        
        return min(final_score, 100), scores
    
    def categorize_post(self, score):
        """Categorize post based on score"""
        if score >= THRESHOLDS['PRIORITY_ALERT']:
            return 'PRIORITY_ALERT'
        elif score >= THRESHOLDS['CANDIDATE']:
            return 'CANDIDATE'
        elif score >= THRESHOLDS['INTERESTING']:
            return 'INTERESTING'
        else:
            return 'LOW'
    
    def process_all_posts(self):
        """Main processing loop"""
        print("=" * 70)
        print("GROUND ZERO - VIRAL CONTENT ANALYZER")
        print("=" * 70)
        
        # Load all XML files
        xml_files = glob.glob(f"{INPUT_DIR}/*.xml")
        print(f"\nFound {len(xml_files)} XML files to analyze\n")
        
        # Load all posts
        for xml_file in xml_files:
            print(f"Loading: {os.path.basename(xml_file)}")
            posts = self.load_posts_from_xml(xml_file)
            self.all_posts.extend(posts)
        
        print(f"\nTotal posts loaded: {len(self.all_posts)}")
        
        # Score each post
        print("\nAnalyzing posts...")
        for post in self.all_posts:
            total_score, metric_scores = self.calculate_total_score(post)
            category = self.categorize_post(total_score)
            
            scored_post = {
                **post,
                'ground_zero_score': total_score,
                'category': category,
                'metric_breakdown': metric_scores
            }
            self.scored_posts.append(scored_post)
        
        # Sort by score
        self.scored_posts.sort(key=lambda x: x['ground_zero_score'], reverse=True)
        
        # Categorize
        priority = [p for p in self.scored_posts if p['category'] == 'PRIORITY_ALERT']
        candidates = [p for p in self.scored_posts if p['category'] == 'CANDIDATE']
        interesting = [p for p in self.scored_posts if p['category'] == 'INTERESTING']
        
        print(f"\n{'='*70}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*70}")
        print(f"PRIORITY_ALERT (>=80): {len(priority)} posts")
        print(f"CANDIDATE (>=60): {len(candidates)} posts")
        print(f"INTERESTING (>=40): {len(interesting)} posts")
        print(f"Total analyzed: {len(self.scored_posts)} posts")
        
        # Generate outputs
        self.generate_outputs(priority, candidates, interesting)
    
    def generate_outputs(self, priority, candidates, interesting):
        """Generate JSON and XML outputs"""
        
        # JSON output
        output_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_posts': len(self.scored_posts),
            'thresholds': THRESHOLDS,
            'metrics': METRICS,
            'categories': {
                'priority_alert': priority,
                'candidates': candidates,
                'interesting': interesting
            },
            'top_10': self.scored_posts[:10]
        }
        
        json_file = f"{OUTPUT_DIR}/ground_zero_analysis.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] JSON saved: {json_file}")
        
        # XML output
        self.generate_xml(priority, candidates, interesting)
    
    def generate_xml(self, priority, candidates, interesting):
        """Generate RSS-style XML for all categories"""
        rss = ET.Element("rss", version="2.0")
        rss.set("xmlns:media", "http://search.yahoo.com/mrss/")
        
        channel = ET.SubElement(rss, "channel")
        
        # Channel metadata
        ET.SubElement(channel, "title").text = "Ground Zero - Viral Content Analysis"
        ET.SubElement(channel, "link").text = "https://github.com/SPZAGENTS"
        ET.SubElement(channel, "description").text = "AI-detected viral content from under the radar"
        ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        ET.SubElement(channel, "language").text = "en"
        ET.SubElement(channel, "generator").text = "Ground Zero Analyzer v1.0 by Pitzi"
        
        # Add all scored posts as items
        all_ranked = priority + candidates + interesting
        
        for rank, post in enumerate(all_ranked, 1):
            item = ET.SubElement(channel, "item")
            
            # Title with score and category
            category_icon = "[RED]" if post['category'] == 'PRIORITY_ALERT' else "[YEL]" if post['category'] == 'CANDIDATE' else "[GRN]"
            ET.SubElement(item, "title").text = f"{category_icon} [{post['ground_zero_score']}/100] {post['title'][:100]}"
            
            # Link
            ET.SubElement(item, "link").text = post.get('link', '')
            
            # Description
            desc = post.get('description', '')
            if not desc:
                desc = f"Score: {post['ground_zero_score']}/100 | Category: {post['category']}"
            ET.SubElement(item, "description").text = desc[:280]
            
            # Category
            ET.SubElement(item, "category").text = post['category']
            
            # Score elements
            score_elem = ET.SubElement(item, "ground_zero_score")
            score_elem.text = str(post['ground_zero_score'])
            
            # Metrics breakdown
            metrics_elem = ET.SubElement(item, "metrics")
            for metric, score in post['metric_breakdown'].items():
                m_elem = ET.SubElement(metrics_elem, metric)
                m_elem.text = str(score)
            
            # Source
            ET.SubElement(item, "source").text = post.get('source', 'Unknown')
            ET.SubElement(item, "reddit_permalink").text = post.get('reddit_permalink', '')
            
            # Rank
            ET.SubElement(item, "ground_zero_rank").text = str(rank)
            
            # GUID
            guid = ET.SubElement(item, "guid")
            guid.text = f"gz-{rank}-{post.get('ground_zero_score', 0)}"
            guid.set("isPermaLink", "false")
        
        # Pretty print XML
        rough_string = ET.tostring(rss, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="  ")
        lines = [line for line in pretty.split("\n") if line.strip()]
        
        xml_file = f"{OUTPUT_DIR}/ground_zero_feed.xml"
        with open(xml_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"[OK] XML saved: {xml_file}")
        print(f"\nTop 10 posts:")
        for i, p in enumerate(self.scored_posts[:10], 1):
            icon = "[RED]" if p['category'] == 'PRIORITY_ALERT' else "[YEL]" if p['category'] == 'CANDIDATE' else "[GRN]"
            print(f"  {i}. {icon} [{p['ground_zero_score']}/100] {p['title'][:60]}...")


def main():
    analyzer = GroundZeroAnalyzer()
    analyzer.process_all_posts()


if __name__ == "__main__":
    main()
