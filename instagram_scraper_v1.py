#!/usr/bin/env python3
"""Instagram Video Scraper - Clean UTF-8 Version"""

import os
import sys
import json
import time
import random
import hashlib
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import instaloader
    INSTALOADER_AVAILABLE = True
except ImportError:
    INSTALOADER_AVAILABLE = False

MIN_DELAY = 2
MAX_DELAY = 8
DAILY_LIMIT = 100

class InstagramScraper:
    def __init__(self, output_dir="instagram_downloads", session_file=None):
        """Initialize with optional session file"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.stats_file = self.output_dir / "stats.json"
        self.stats = self._load_stats()
        self.session_file = session_file
        self.loader = None
        
        
    def _load_stats(self):
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {'total_downloaded': 0, 'transcribed': 0, 'daily_count': {}}
    
    def _save_stats(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
            
    def _human_delay(self, min_sec=MIN_DELAY, max_sec=MAX_DELAY):
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
        
    def _check_daily_limit(self):
        today = datetime.now().strftime('%Y-%m-%d')
        count = self.stats['daily_count'].get(today, 0)
        if count >= DAILY_LIMIT:
            print(f"Daily limit reached")
            return False
        return True
        
    def _get_instaloader(self):
        """Get or create instaloader with session"""
        if self.loader is None:
            self.loader = instaloader.Instaloader(
                download_videos=True,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False
            )
            
            # Try to load session if available
            if self.session_file and Path(self.session_file).exists():
                try:
                    self.loader.load_session_from_file(self.session_file)
                    print(f"Loaded session from {self.session_file}")
                except Exception as e:
                    print(f"Could not load session: {e}")
                    
        return self.loader
    
    def login(self, username, password):
        """Login with username and password"""
        try:
            loader = self._get_instaloader()
            loader.login(username, password)
            
            # Save session for future use
            if self.session_file:
                loader.save_session_to_file(self.session_file)
                print(f"Session saved to {self.session_file}")
                
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False
        
    def _increment_counter(self):
        today = datetime.now().strftime('%Y-%m-%d')
        self.stats['daily_count'][today] = self.stats['daily_count'].get(today, 0) + 1
        self.stats['total_downloaded'] += 1
        self._save_stats()

    def download_video(self, url: str, username: str = "unknown"):
        """Download video using instaloader"""
        if not self._check_daily_limit():
            return {'success': False, 'error': 'daily_limit_reached'}
        
        delay = self._human_delay()
        print(f"Waiting {delay:.1f}s before request...")
        
        if not INSTALOADER_AVAILABLE:
            print("Instaloader not available, using demo mode")
            return self._demo_download(url, username)
        
        try:
            user_dir = self.output_dir / username
            user_dir.mkdir(exist_ok=True)
            
            # Extract shortcode from URL
            shortcode = url.split('/p/')[-1].split('/')[0].split('?')[0]
            if not shortcode:
                return {'success': False, 'error': 'invalid_url'}
            
            print(f"Downloading: {shortcode}")
            
            # Initialize instaloader with session
            loader = self._get_instaloader()
            
            # Get post from shortcode
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            
            if not post.is_video:
                print(f"Not a video (it's a {post.typename})")
                return {'success': False, 'error': 'not_a_video', 'type': post.typename}
            
            # Download post
            loader.download_post(post, target=str(user_dir))
            
            # Find the downloaded video file (search more broadly)
            video_files = list(user_dir.glob("*.mp4"))
            if not video_files:
                # Also check in shortcode subdirectory
                shortcode_dir = user_dir / shortcode
                if shortcode_dir.exists():
                    video_files = list(shortcode_dir.glob("*.mp4"))
            
            if not video_files:
                print(f"Files in {user_dir}: {list(user_dir.iterdir())}")
                return {'success': False, 'error': 'video_not_found', 'dir': str(user_dir)}
            
            video_path = video_files[0]
            size_mb = video_path.stat().st_size / (1024 * 1024)
            
            result = {
                'success': True,
                'filename': str(video_path),
                'video_id': shortcode,
                'username': username,
                'url': url,
                'size_mb': round(size_mb, 2),
                'caption': post.caption[:200] if post.caption else '',
                'likes': post.likes,
                'date': post.date_local.isoformat() if post.date_local else None
            }
            
            self._increment_counter()
            print(f"Downloaded: {video_path.name} ({size_mb:.1f} MB)")
            return result
            
        except Exception as e:
            print(f"Error: {e}")
            self._human_delay(30, 60)
            return {'success': False, 'error': str(e)}
    
    def _demo_download(self, url, username):
        """Demo mode when instaloader not available"""
        user_dir = self.output_dir / username
        user_dir.mkdir(exist_ok=True)
        
        video_id = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"{username}_{video_id}_demo.mp4"
        output_path = user_dir / filename
        
        # Create dummy file
        with open(output_path, 'w') as f:
            f.write("Demo video")
        
        print(f"Created demo: {filename}")
        
        self._increment_counter()
        return {
            'success': True,
            'filename': str(output_path),
            'video_id': video_id,
            'demo_mode': True
        }

    def transcribe_video(self, video_path: str):
        """Transcribe video using Whisper"""
        print(f"Transcribing: {video_path}")
        self._human_delay(1, 3)
        
        try:
            # Simple transcription (placeholder for now)
            # TODO: Add real Whisper integration
            
            result = {
                'success': True,
                'filename': video_path,
                'transcribed_at': datetime.now().isoformat(),
                'language': 'en',  # Will detect with Whisper
                'text': '[Transcription pending - Whisper not yet integrated]',
                'duration': 0
            }
            
            self.stats['total_transcribed'] = self.stats.get('total_transcribed', 0) + 1
            self._save_stats()
            
            return result
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_batch(self, urls: list, username: str = "unknown"):
        """Process a batch of URLs"""
        results = []
        print(f"\nProcessing batch of {len(urls)} videos")
        print(f"User: {username}")
        print("=" * 60)
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing...")
            
            download_result = self.download_video(url, username)
            
            if download_result['success']:
                transcribe_result = self.transcribe_video(download_result['filename'])
                results.append({'download': download_result, 'transcription': transcribe_result})
            else:
                results.append({'download': download_result, 'transcription': None})
            
            # Batch rest every 10 videos
            if i % 10 == 0 and i < len(urls):
                self._batch_rest()
        
        return results
    
    def _batch_rest(self):
        """Rest between batches"""
        rest_time = 60 + random.uniform(-10, 10)
        print(f"Resting for {int(rest_time)}s between batches...")
        time.sleep(rest_time)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Instagram Video Scraper')
    parser.add_argument('--url', '-u', help='Instagram post URL')
    parser.add_argument('--file', '-f', help='File with URLs')
    parser.add_argument('--username', '-n', default='unknown', help='Username')
    parser.add_argument('--output', '-o', default='instagram_downloads', help='Output directory')
    parser.add_argument('--session', '-s', default='instagram_session', help='Session file path')
    parser.add_argument('--login', '-l', help='Login with username:password')
    
    args = parser.parse_args()
    
    scraper = InstagramScraper(output_dir=args.output, session_file=args.session)
    
    # Handle login if requested
    if args.login:
        try:
            username, password = args.login.split(':')
            if scraper.login(username, password):
                print("Login successful!")
            else:
                print("Login failed!")
                sys.exit(1)
        except ValueError:
            print("Error: Use format username:password")
            sys.exit(1)
    
    if args.url:
        result = scraper.download_video(args.url, args.username)
        print("\n" + "="*60)
        print("Result:")
        print(json.dumps(result, indent=2, default=str))
    elif args.file:
        with open(args.file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        results = scraper.process_batch(urls, args.username)
        print("\n" + "="*60)
        print(f"Processed {len(results)} URLs")
    else:
        # Demo mode with sample URLs
        print("Demo mode - processing sample URLs")
        sample_urls = [
            "https://instagram.com/p/sample1",
            "https://instagram.com/p/sample2"
        ]
        results = scraper.process_batch(sample_urls, "demo_user")
        print("\n" + "="*60)
        print(f"Demo complete: {len(results)} URLs processed")


if __name__ == '__main__':
    main()
