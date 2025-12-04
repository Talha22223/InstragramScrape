"""
Test script to verify Instagram scraper is working properly
Run this to debug scraping issues
"""

import os
from dotenv import load_dotenv
from services.instagram_scraper import InstagramScraper
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_single_post_scraping():
    """Test scraping comments from a single post"""
    print("\n" + "="*60)
    print("TEST 1: Single Post Comment Scraping")
    print("="*60)
    
    api_key = os.getenv('APIFY_API_KEY')
    
    if not api_key or len(api_key) < 10:
        print("❌ ERROR: APIFY_API_KEY not found in .env file")
        print("Please add your API key to backend/.env file")
        return False
    
    print(f"✓ API Key found: {api_key[:15]}...")
    
    # Initialize scraper
    scraper = InstagramScraper(api_key=api_key)
    print("✓ Scraper initialized")
    
    # Test URL - use a popular Instagram post
    test_url = input("\nEnter Instagram post URL to test (or press Enter for default): ").strip()
    if not test_url:
        test_url = "https://www.instagram.com/p/C0_test/"  # Default test URL
        print(f"Using test URL: {test_url}")
    
    print(f"\nScraping comments from: {test_url}")
    print("This may take 30-60 seconds...\n")
    
    try:
        comments = scraper.scrape_comments(test_url, max_comments=50)
        
        print(f"\n✅ SUCCESS! Scraped {len(comments)} comments")
        
        if comments:
            print("\n" + "-"*60)
            print("Sample comments:")
            print("-"*60)
            for i, comment in enumerate(comments[:3], 1):
                print(f"\n{i}. @{comment.get('username', 'unknown')}")
                print(f"   Text: {comment.get('text', 'N/A')[:100]}...")
                print(f"   Likes: {comment.get('likes', 0)}")
        else:
            print("⚠ Warning: No comments found")
            print("Possible reasons:")
            print("- Post has no comments")
            print("- Post is private")
            print("- URL is incorrect")
            print("- Apify actor issue")
        
        return len(comments) > 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if API key is valid")
        print("2. Verify post URL is correct")
        print("3. Make sure post is public")
        print("4. Check Apify account credits")
        return False

def test_profile_scraping():
    """Test scraping posts from a profile"""
    print("\n" + "="*60)
    print("TEST 2: Profile Post Scraping (with Date Filter)")
    print("="*60)
    
    api_key = os.getenv('APIFY_API_KEY')
    scraper = InstagramScraper(api_key=api_key)
    
    profile_url = input("\nEnter Instagram profile URL (e.g., https://www.instagram.com/nike/): ").strip()
    if not profile_url:
        print("❌ No profile URL provided, skipping test")
        return False
    
    from_date = input("Enter start date (YYYY-MM-DD, e.g., 2024-01-01): ").strip()
    if not from_date:
        from_date = "2024-01-01"
        print(f"Using default date: {from_date}")
    
    print(f"\nScraping posts from profile: {profile_url}")
    print(f"From date: {from_date}")
    print("This may take 30-90 seconds...\n")
    
    try:
        posts = scraper.scrape_profile_posts(profile_url, from_date, max_posts=5)
        
        print(f"\n✅ SUCCESS! Found {len(posts)} posts")
        
        if posts:
            print("\n" + "-"*60)
            print("Posts found:")
            print("-"*60)
            for i, post in enumerate(posts, 1):
                print(f"\n{i}. Date: {post.get('date', 'unknown')}")
                print(f"   URL: {post.get('url', 'N/A')}")
        else:
            print("⚠ Warning: No posts found")
            print("Possible reasons:")
            print("- No posts after the specified date")
            print("- Profile is private")
            print("- Profile URL is incorrect")
        
        return len(posts) > 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_bulk_analysis():
    """Test bulk analysis (profile + comments)"""
    print("\n" + "="*60)
    print("TEST 3: Bulk Profile + Comments Analysis")
    print("="*60)
    
    api_key = os.getenv('APIFY_API_KEY')
    scraper = InstagramScraper(api_key=api_key)
    
    profile_url = input("\nEnter Instagram profile URL: ").strip()
    if not profile_url:
        print("❌ No profile URL provided, skipping test")
        return False
    
    from_date = input("Enter start date (YYYY-MM-DD): ").strip()
    if not from_date:
        from_date = "2024-11-01"
        print(f"Using default date: {from_date}")
    
    print(f"\nAnalyzing profile: {profile_url}")
    print(f"From date: {from_date}")
    print("Scraping 3 posts as a test...")
    print("This may take 2-3 minutes...\n")
    
    try:
        result = scraper.scrape_posts_comments_bulk(
            profile_url, 
            from_date, 
            max_posts=3,
            max_comments_per_post=30
        )
        
        print(f"\n✅ SUCCESS!")
        print(f"Posts analyzed: {result.get('total_posts', 0)}")
        print(f"Total comments: {result.get('total_comments', 0)}")
        
        if result.get('posts'):
            print("\n" + "-"*60)
            print("Posts breakdown:")
            print("-"*60)
            for i, post in enumerate(result['posts'], 1):
                print(f"\n{i}. {post.get('post_url', 'N/A')}")
                print(f"   Date: {post.get('post_date', 'unknown')}")
                print(f"   Comments: {post.get('comments_count', 0)}")
        
        return result.get('total_posts', 0) > 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Instagram Scraper Test Suite")
    print("="*60)
    
    # Run tests
    test1_passed = test_single_post_scraping()
    
    if test1_passed:
        run_test2 = input("\n\nRun profile scraping test? (y/n): ").strip().lower()
        if run_test2 == 'y':
            test2_passed = test_profile_scraping()
            
            if test2_passed:
                run_test3 = input("\n\nRun bulk analysis test? (y/n): ").strip().lower()
                if run_test3 == 'y':
                    test_bulk_analysis()
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
    
    if test1_passed:
        print("\n✅ Your scraper is configured correctly!")
        print("\nYou can now run the Flask app:")
        print("  python app.py")
    else:
        print("\n⚠ Scraper test failed. Please check:")
        print("1. APIFY_API_KEY in .env file")
        print("2. Apify account has credits")
        print("3. Test with a public Instagram post URL")
