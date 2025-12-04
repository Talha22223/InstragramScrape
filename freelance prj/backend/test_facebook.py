"""Test Facebook scraper to debug comment extraction"""
import os
from dotenv import load_dotenv
from services.facebook_scraper import FacebookScraper
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Test URLs - replace with actual Facebook URLs
TEST_POST_URL = "https://www.facebook.com/zuck/posts/10115037706964991"  # Example post

def test_facebook_post():
    """Test single Facebook post scraping"""
    print("\n" + "="*80)
    print("TESTING FACEBOOK SINGLE POST SCRAPER")
    print("="*80 + "\n")
    
    api_key = os.getenv('APIFY_API_KEY')
    if not api_key:
        print("[ERROR] No APIFY_API_KEY found!")
        return
    
    print(f"[OK] API Key found: {api_key[:20]}...")
    print(f"[OK] Test URL: {TEST_POST_URL}\n")
    
    scraper = FacebookScraper(api_key=api_key)
    
    print("Starting scrape...")
    print("-" * 80)
    
    comments = scraper.scrape_single_post(TEST_POST_URL, max_comments=50)
    
    print("-" * 80)
    print(f"\n📊 RESULTS:")
    print(f"   Total comments scraped: {len(comments)}")
    
    if comments:
        print(f"\n[SUCCESS!] Found {len(comments)} comments\n")
        print("First 3 comments:")
        for i, comment in enumerate(comments[:3], 1):
            print(f"\n{i}. User: {comment.get('username', 'N/A')}")
            print(f"   Text: {comment.get('text', 'N/A')[:100]}...")
            print(f"   Likes: {comment.get('likes', 0)}")
    else:
        print("\n[ERROR] NO COMMENTS FOUND!")
        print("\nPossible reasons:")
        print("1. The post has no comments")
        print("2. The post is private/restricted")
        print("3. The Apify actor ID is incorrect")
        print("4. The actor cannot access this post")
        print("5. The comment extraction logic has issues")
        
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_facebook_post()
