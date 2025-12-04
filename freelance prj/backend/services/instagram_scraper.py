from apify_client import ApifyClient
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class InstagramScraper:
    """
    Instagram comment scraper using Apify API
    """
    
    def __init__(self, api_key):
        """
        Initialize Apify client
        
        Args:
            api_key (str): Apify API key
        """
        self.client = ApifyClient(api_key)
        self.actor_id = 'apify/instagram-comment-scraper'  # Official Apify Instagram scraper
        self.profile_actor_id = 'apify/instagram-scraper'  # For profile scraping
        
    def scrape_comments(self, post_url, max_comments=1000):
        """
        Scrape comments from an Instagram post or reel
        
        Args:
            post_url (str): Instagram post/reel URL
            max_comments (int): Maximum number of comments to scrape
            
        Returns:
            list: List of comment dictionaries
        """
        try:
            logger.info(f"Starting Apify scraper for: {post_url}")
            
            # Prepare input for the actor - Updated configuration for better scraping
            run_input = {
                "directUrls": [post_url],
                "resultsLimit": max_comments,
                "resultsType": "comments",
                "searchLimit": 1,
                "searchType": "hashtag",
                "addParentData": False,
                "maxRequestRetries": 3,
                "maxComments": max_comments,
                "scrapeCommentLikes": True,
                "scrapeCommentReplies": False  # Set to True if you want replies too
            }
            
            # Run the actor and wait for it to finish
            logger.info(f"Requesting up to {max_comments} comments with actor: {self.actor_id}")
            logger.info(f"Post URL: {post_url}")
            
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            # Fetch results from the dataset
            comments = []
            logger.info("Fetching comment data from dataset...")
            
            items_count = 0
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items_count += 1
                
                # Try multiple field names as different actors use different field names
                comment_text = (item.get('text') or 
                               item.get('comment') or 
                               item.get('commentText') or 
                               item.get('ownerComment', {}).get('text', '') or
                               item.get('caption', ''))
                
                # Generate unique ID if not present
                comment_id = (item.get('id') or 
                            item.get('commentId') or 
                            item.get('pk') or 
                            f"comment_{items_count}")
                
                comment_data = {
                    'id': comment_id,
                    'text': comment_text,
                    'username': (item.get('ownerUsername') or 
                                item.get('username') or 
                                item.get('owner', {}).get('username', '') or
                                item.get('user', {}).get('username', 'unknown')),
                    'timestamp': item.get('timestamp', item.get('createdAt', item.get('created_time', ''))),
                    'likes': item.get('likesCount', item.get('likes', item.get('like_count', 0)))
                }
                
                # Only add comments with text
                if comment_data['text'] and len(comment_data['text'].strip()) > 0:
                    comments.append(comment_data)
            
            logger.info(f"Processed {items_count} items from dataset")
            logger.info(f"Successfully scraped {len(comments)} comments with valid text")
            
            # If we got very few comments, try alternative method
            if len(comments) < 10:
                logger.warning(f"Only got {len(comments)} comments, trying alternative scraper...")
                alt_comments = self.scrape_comments_alternative(post_url, max_comments)
                if len(alt_comments) > len(comments):
                    logger.info(f"Alternative scraper got more comments: {len(alt_comments)}")
                    return alt_comments
                else:
                    logger.info(f"Alternative scraper also got few comments: {len(alt_comments)}")
            
            return comments
            
        except Exception as e:
            logger.error(f"Error scraping Instagram comments: {str(e)}")
            # Return empty list on error
            return []
    
    def scrape_comments_alternative(self, post_url, max_comments=1000):
        """
        Alternative scraper using a different Apify actor
        Useful as a fallback option
        
        Args:
            post_url (str): Instagram post/reel URL
            max_comments (int): Maximum number of comments to scrape
            
        Returns:
            list: List of comment dictionaries
        """
        try:
            # Try multiple alternative actors
            alternative_actors = [
                ('zuzka/instagram-scraper', {
                    "directUrls": [post_url],
                    "resultsType": "comments",
                    "resultsLimit": max_comments,
                    "maxComments": max_comments
                }),
                ('apify/instagram-scraper', {
                    "directUrls": [post_url],
                    "resultsType": "comments", 
                    "resultsLimit": max_comments
                })
            ]
            
            for actor_name, run_input in alternative_actors:
                try:
                    logger.info(f"Trying alternative actor: {actor_name}")
                    run = self.client.actor(actor_name).call(run_input=run_input)
                    
                    comments = []
                    for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                        comment_text = (item.get('text') or 
                                       item.get('comment') or 
                                       item.get('commentText') or '')
                        
                        comment_data = {
                            'id': item.get('id', item.get('commentId', '')),
                            'text': comment_text,
                            'username': item.get('username', item.get('ownerUsername', 'unknown')),
                            'timestamp': item.get('timestamp', item.get('createdAt', '')),
                            'likes': item.get('likes', item.get('likesCount', 0))
                        }
                        
                        if comment_data['text'] and len(comment_data['text'].strip()) > 0:
                            comments.append(comment_data)
                    
                    if len(comments) > 0:
                        logger.info(f"{actor_name}: Successfully scraped {len(comments)} comments")
                        return comments
                except Exception as actor_error:
                    logger.warning(f"{actor_name} failed: {str(actor_error)}")
                    continue
            
            logger.warning("All alternative scrapers failed")
            return []
            
        except Exception as e:
            logger.error(f"Alternative scraper error: {str(e)}")
            return []
    
    def scrape_profile_posts(self, profile_url, from_date=None, max_posts=50):
        """
        Scrape posts from an Instagram profile from a specific date onwards
        
        Args:
            profile_url (str): Instagram profile URL (e.g., https://www.instagram.com/username/)
            from_date (str): Start date in format 'YYYY-MM-DD' (e.g., '2024-01-15')
            max_posts (int): Maximum number of posts to scrape
            
        Returns:
            list: List of post URLs from the specified date onwards
        """
        try:
            logger.info(f"Scraping profile: {profile_url} from date: {from_date}")
            
            # Parse the from_date if provided
            cutoff_date = None
            if from_date:
                try:
                    # Parse as naive datetime first
                    cutoff_date = datetime.strptime(from_date, '%Y-%m-%d')
                    # Make it timezone-aware (assume UTC)
                    from datetime import timezone
                    cutoff_date = cutoff_date.replace(tzinfo=timezone.utc)
                    logger.info(f"Filtering posts from {cutoff_date.strftime('%Y-%m-%d')} onwards")
                except ValueError:
                    logger.error(f"Invalid date format: {from_date}. Expected YYYY-MM-DD")
                    return []
            
            # Prepare input for profile scraper with better configuration
            run_input = {
                "directUrls": [profile_url],
                "resultsType": "posts",
                "resultsLimit": max_posts * 3,  # Get more to filter by date
                "searchLimit": 1,
                "searchType": "user",
                "addParentData": True  # Get more post metadata
            }
            
            logger.info(f"Running profile scraper with actor: {self.profile_actor_id}")
            run = self.client.actor(self.profile_actor_id).call(run_input=run_input)
            
            # Fetch posts from dataset
            posts = []
            logger.info("Fetching posts from dataset...")
            
            items_found = 0
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items_found += 1
                
                # Log the first item to see what fields are available
                if items_found == 1:
                    logger.info(f"First item keys: {list(item.keys())}")
                    logger.info(f"Sample item (first 500 chars): {str(item)[:500]}")
                
                # Extract post URL - try multiple field names
                post_url = (item.get('url') or 
                           item.get('postUrl') or 
                           item.get('displayUrl') or 
                           item.get('shortCode'))
                
                # If we got a shortcode, construct the full URL
                if post_url and 'instagram.com' not in post_url:
                    post_url = f"https://www.instagram.com/p/{post_url}/"
                
                if not post_url:
                    logger.warning(f"Item {items_found}: No URL found")
                    continue
                
                # Extract timestamp - try multiple field names and formats
                timestamp = (item.get('timestamp') or 
                           item.get('ownerTimestamp') or 
                           item.get('latestComments', [{}])[0].get('timestamp') if item.get('latestComments') else None or
                           item.get('time'))
                
                logger.debug(f"Item {items_found}: URL={post_url}, timestamp={timestamp}")
                
                # Parse timestamp if available
                post_date = None
                if timestamp:
                    try:
                        from datetime import timezone
                        # Try different timestamp formats
                        if isinstance(timestamp, str):
                            # Try ISO format
                            try:
                                post_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            except:
                                # Try parsing as date string
                                try:
                                    post_date = datetime.strptime(timestamp, '%Y-%m-%d')
                                    # Make it timezone-aware
                                    post_date = post_date.replace(tzinfo=timezone.utc)
                                except:
                                    logger.warning(f"Could not parse string timestamp: {timestamp}")
                        elif isinstance(timestamp, (int, float)):
                            # Unix timestamp - make it timezone-aware
                            post_date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    except Exception as e:
                        logger.warning(f"Error parsing timestamp {timestamp}: {str(e)}")
                
                # Log the post details for debugging
                logger.debug(f"Post URL: {post_url}, Date: {post_date}, Timestamp: {timestamp}")
                
                # Filter by date if cutoff_date is provided
                include_post = False
                if cutoff_date and post_date:
                    if post_date >= cutoff_date:
                        include_post = True
                        logger.info(f"Including post from {post_date.strftime('%Y-%m-%d')} (after cutoff {cutoff_date.strftime('%Y-%m-%d')})")
                    else:
                        logger.debug(f"Skipping post from {post_date.strftime('%Y-%m-%d')} (before cutoff)")
                elif not cutoff_date:
                    # If no date filter, add all posts
                    include_post = True
                else:
                    # If cutoff_date exists but post_date is None, include it (can't filter)
                    logger.warning(f"Post {post_url} has no date, including anyway")
                    include_post = True
                
                if include_post:
                    posts.append({
                        'url': post_url,
                        'timestamp': timestamp,
                        'date': post_date.strftime('%Y-%m-%d') if post_date else 'unknown'
                    })
                
                # Stop if we have enough posts
                if len(posts) >= max_posts:
                    logger.info(f"Reached max_posts limit of {max_posts}")
                    break
            
            logger.info(f"Processed {items_found} items from dataset")
            logger.info(f"Found {len(posts)} posts from {from_date or 'all time'}")
            
            if items_found == 0:
                logger.warning("No items returned from Apify dataset - check actor configuration or API credits")
            elif len(posts) == 0 and items_found > 0:
                logger.warning(f"Received {items_found} items but no valid posts found - check date filter or field mappings")
            
            return posts
            
        except Exception as e:
            logger.error(f"Error scraping profile posts: {str(e)}")
            return []
    
    def scrape_posts_comments_bulk(self, profile_url, from_date=None, max_posts=50, max_comments_per_post=1000):
        """
        Scrape all posts from a profile since a given date and collect all comments
        
        Args:
            profile_url (str): Instagram profile URL
            from_date (str): Start date in format 'YYYY-MM-DD'
            max_posts (int): Maximum number of posts to scrape
            max_comments_per_post (int): Maximum comments per post
            
        Returns:
            dict: Dictionary with posts and their comments
        """
        try:
            # Step 1: Get all posts from the profile
            logger.info(f"Step 1: Getting posts from profile...")
            posts = self.scrape_profile_posts(profile_url, from_date, max_posts)
            
            if not posts:
                logger.warning("No posts found")
                return {
                    'profile_url': profile_url,
                    'from_date': from_date,
                    'total_posts': 0,
                    'posts': []
                }
            
            # Step 2: Scrape comments from each post
            logger.info(f"Step 2: Scraping comments from {len(posts)} posts...")
            results = []
            
            for idx, post in enumerate(posts, 1):
                post_url = post['url']
                logger.info(f"Scraping post {idx}/{len(posts)}: {post_url}")
                
                comments = self.scrape_comments(post_url, max_comments_per_post)
                
                results.append({
                    'post_url': post_url,
                    'post_date': post.get('date', 'unknown'),
                    'comments_count': len(comments),
                    'comments': comments
                })
                
                logger.info(f"  → Scraped {len(comments)} comments")
                
                # Add small delay between posts to avoid rate limiting
                if idx < len(posts):
                    time.sleep(2)
            
            total_comments = sum(post['comments_count'] for post in results)
            logger.info(f"Completed! Total: {len(posts)} posts, {total_comments} comments")
            
            return {
                'profile_url': profile_url,
                'from_date': from_date,
                'total_posts': len(posts),
                'total_comments': total_comments,
                'posts': results
            }
            
        except Exception as e:
            logger.error(f"Error in bulk scraping: {str(e)}")
            return {
                'profile_url': profile_url,
                'from_date': from_date,
                'total_posts': 0,
                'total_comments': 0,
                'posts': [],
                'error': str(e)
            }
