from apify_client import ApifyClient
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class FacebookScraper:
    """
    Facebook scraper using Apify API - supports posts, pages, groups, and profiles
    """
    
    def __init__(self, api_key):
        """
        Initialize Apify client
        
        Args:
            api_key (str): Apify API key
        """
        self.client = ApifyClient(api_key)
        # Using the page scraper which works better for public pages
        self.actor_id = 'apify/facebook-pages-scraper'  # Facebook pages scraper actor
    
    def scrape_single_post(self, post_url, max_comments=1000):
        """
        Scrape comments from a single Facebook post (from any source: group, page, profile, public post)
        
        Args:
            post_url (str): Facebook post URL
            max_comments (int): Maximum number of comments to scrape
            
        Returns:
            list: List of comment dictionaries
        """
        try:
            logger.info(f"Starting Apify scraper for Facebook post: {post_url}")
            
            # Prepare input for the actor with proper configuration
            run_input = {
                "startUrls": [post_url],
                "maxPosts": 1,
                "maxPostComments": max_comments,
                "scrapeComments": True,
                "scrapeReviews": False,
                "scrapeServices": False
            }
            
            logger.info(f"Requesting up to {max_comments} comments with actor: {self.actor_id}")
            
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            # Fetch results from the dataset
            comments = []
            logger.info("Fetching comment data from dataset...")
            
            items_count = 0
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items_count += 1
                
                # Check for errors from Apify
                if 'error' in item:
                    error_msg = item.get('errorDescription', item.get('error', 'Unknown error'))
                    logger.error(f"Facebook scraping error: {error_msg}")
                    logger.error(f"This usually means: 1) Post is private/restricted, 2) Post deleted, 3) Need Facebook login cookies")
                    raise Exception(f"Cannot access Facebook post: {error_msg}")
                
                logger.debug(f"Processing dataset item {items_count} with keys: {list(item.keys())}")
                
                # Get comments from the post - try multiple possible structures
                post_comments = item.get('comments', [])
                
                # If no comments at top level, check for posts array
                if not post_comments and 'posts' in item:
                    posts_data = item.get('posts', [])
                    if posts_data and len(posts_data) > 0:
                        post_comments = posts_data[0].get('comments', [])
                
                for comment_item in post_comments:
                    # Handle different comment data structures
                    comment_text = (comment_item.get('text') or 
                                  comment_item.get('comment') or 
                                  comment_item.get('message') or
                                  comment_item.get('commentText') or '')
                    
                    if comment_text and len(comment_text.strip()) > 0:
                        comment_data = {
                            'id': comment_item.get('id', f"fb_comment_{len(comments)}"),
                            'text': comment_text.strip(),
                            'username': (comment_item.get('name') or 
                                       comment_item.get('author', {}).get('name') or
                                       comment_item.get('authorName') or 'Unknown'),
                            'likes': (comment_item.get('likes') or 
                                    comment_item.get('likeCount') or
                                    comment_item.get('likesCount') or 0),
                            'timestamp': (comment_item.get('time') or 
                                        comment_item.get('timestamp') or
                                        comment_item.get('date') or '')
                        }
                        comments.append(comment_data)
            
            if len(comments) == 0:
                logger.warning("No comments extracted. Post may have no comments or is not accessible.")
            else:
                logger.info(f"Successfully scraped {len(comments)} comments from Facebook post")
            
            return comments
            
        except Exception as e:
            logger.error(f"Error scraping Facebook post: {str(e)}")
            raise  # Re-raise to let the API endpoint handle it properly
        
    def scrape_posts_bulk(self, url, from_date=None, max_posts=50):
        """
        Scrape posts from Facebook (groups, pages, or profiles) from a specific date onwards
        
        Args:
            url (str): Facebook URL (group, page, or profile)
            from_date (str): Start date in format 'YYYY-MM-DD' (e.g., '2024-01-15')
            max_posts (int): Maximum number of posts to scrape
            
        Returns:
            list: List of post data with URLs and dates
        """
        try:
            logger.info(f"Scraping Facebook URL: {url} from date: {from_date}")
            
            # Parse the from_date if provided
            cutoff_date = None
            if from_date:
                try:
                    cutoff_date = datetime.strptime(from_date, '%Y-%m-%d')
                    logger.info(f"Filtering posts from {cutoff_date.strftime('%Y-%m-%d')} onwards")
                except ValueError:
                    logger.error(f"Invalid date format: {from_date}. Expected YYYY-MM-DD")
                    return []
            
            # Prepare input for Facebook scraper (works for groups, pages, profiles)
            run_input = {
                "startUrls": [url],
                "maxPosts": max_posts * 2,  # Get more to filter by date
                "maxPostComments": 100,  # Comments per post
                "scrapeComments": True,
                "scrapeReviews": False,
                "scrapeServices": False
            }
            
            logger.info(f"Running Facebook scraper with actor: {self.actor_id}")
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            # Fetch posts from dataset
            posts = []
            logger.info("Fetching posts from dataset...")
            
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                # Extract post URL and timestamp
                post_url = item.get('url', item.get('postUrl', ''))
                timestamp = item.get('time', item.get('timestamp', item.get('created_time', '')))
                comments = item.get('comments', [])
                
                # Parse timestamp if available
                post_date = None
                if timestamp:
                    try:
                        if isinstance(timestamp, str):
                            # Try ISO format
                            try:
                                post_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            except:
                                try:
                                    post_date = datetime.strptime(timestamp, '%Y-%m-%d')
                                except:
                                    logger.warning(f"Could not parse string timestamp: {timestamp}")
                        elif isinstance(timestamp, (int, float)):
                            post_date = datetime.fromtimestamp(timestamp)
                    except Exception as e:
                        logger.warning(f"Error parsing timestamp {timestamp}: {str(e)}")
                
                logger.debug(f"Post URL: {post_url}, Date: {post_date}, Comments: {len(comments)}")
                
                # Filter by date if cutoff_date is provided
                include_post = False
                if cutoff_date and post_date:
                    if post_date >= cutoff_date:
                        include_post = True
                        logger.info(f"Including post from {post_date.strftime('%Y-%m-%d')}")
                    else:
                        logger.debug(f"Skipping post from {post_date.strftime('%Y-%m-%d')}")
                elif not cutoff_date:
                    include_post = True
                else:
                    logger.warning(f"Post {post_url} has no date, including anyway")
                    include_post = True
                
                if include_post:
                    # Process comments
                    processed_comments = []
                    for comment in comments:
                        comment_text = comment.get('text', comment.get('message', ''))
                        if comment_text and len(comment_text.strip()) > 0:
                            processed_comments.append({
                                'id': comment.get('id', f"comment_{len(processed_comments)}"),
                                'text': comment_text,
                                'username': comment.get('author', {}).get('name', comment.get('from', {}).get('name', 'unknown')),
                                'timestamp': comment.get('time', comment.get('created_time', '')),
                                'likes': comment.get('likes', comment.get('like_count', 0))
                            })
                    
                    posts.append({
                        'post_url': post_url,
                        'post_date': post_date.strftime('%Y-%m-%d') if post_date else 'unknown',
                        'comments': processed_comments,
                        'comments_count': len(processed_comments)
                    })
                
                if len(posts) >= max_posts:
                    logger.info(f"Reached max_posts limit of {max_posts}")
                    break
            
            logger.info(f"Found {len(posts)} posts from {from_date or 'all time'}")
            return posts
            
        except Exception as e:
            logger.error(f"Error scraping Facebook group posts: {str(e)}")
            return []
    
    def scrape_posts_comments_bulk(self, url, from_date=None, max_posts=50):
        """
        Scrape all posts from Facebook (groups, pages, profiles) since a given date and collect all comments
        
        Args:
            url (str): Facebook URL (group, page, or profile)
            from_date (str): Start date in format 'YYYY-MM-DD'
            max_posts (int): Maximum number of posts to scrape
            
        Returns:
            dict: Dictionary with posts and their comments
        """
        try:
            # Get all posts with comments
            logger.info(f"Starting bulk Facebook scraping...")
            posts = self.scrape_posts_bulk(url, from_date, max_posts)
            
            if not posts:
                logger.warning("No posts found")
                return {
                    'url': url,
                    'from_date': from_date,
                    'total_posts': 0,
                    'total_comments': 0,
                    'posts': []
                }
            
            # Calculate total comments
            total_comments = sum(post['comments_count'] for post in posts)
            
            logger.info(f"Completed! Total: {len(posts)} posts, {total_comments} comments")
            
            return {
                'url': url,
                'from_date': from_date,
                'total_posts': len(posts),
                'total_comments': total_comments,
                'posts': posts
            }
            
        except Exception as e:
            logger.error(f"Error in bulk Facebook scraping: {str(e)}")
            return {
                'url': url,
                'from_date': from_date,
                'total_posts': 0,
                'total_comments': 0,
                'posts': [],
                'error': str(e)
            }
