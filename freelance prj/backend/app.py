from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
from services.instagram_scraper import InstagramScraper
from services.facebook_scraper import FacebookScraper
from services.sentiment_analyzer import SentimentAnalyzer
from services.topic_classifier import TopicClassifier
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Get API key from environment
APIFY_API_KEY = os.getenv('APIFY_API_KEY')
if not APIFY_API_KEY:
    logger.error("APIFY_API_KEY not found in environment variables!")
    logger.info("Please set APIFY_API_KEY in your .env file")

# Initialize services
instagram_scraper = InstagramScraper(api_key=APIFY_API_KEY)
facebook_scraper = FacebookScraper(api_key=APIFY_API_KEY)
sentiment_analyzer = SentimentAnalyzer()
topic_classifier = TopicClassifier()

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        'message': 'Social Media Comment Analyzer API',
        'version': '3.0',
        'platforms': ['Instagram', 'Facebook Groups'],
        'endpoints': {
            'health': '/api/health',
            'analyze': '/api/analyze (POST) - Single Instagram post analysis',
            'analyze-profile': '/api/analyze-profile (POST) - Bulk Instagram profile analysis from date',
            'analyze-facebook-group': '/api/analyze-facebook-group (POST) - Bulk Facebook group analysis from date',
            'stats': '/api/stats (POST)'
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    api_key = os.getenv('APIFY_API_KEY')
    api_key_status = 'configured' if api_key and len(api_key) > 10 else 'missing'
    
    return jsonify({
        'status': 'healthy',
        'message': 'Social Media Comment Analysis API is running',
        'apify_api_key': api_key_status,
        'python_version': '3.x',
        'platforms': ['Instagram', 'Facebook Groups'],
        'services': {
            'instagram_scraper': 'initialized',
            'facebook_scraper': 'initialized',
            'sentiment_analyzer': 'initialized',
            'topic_classifier': 'initialized'
        }
    }), 200

# Serve React App
@app.route('/')
def serve_react_app():
    """Serve the React application"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files for React app"""
    try:
        return send_from_directory(app.static_folder, path)
    except:
        # If file doesn't exist, serve index.html for React Router
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/test-scraper', methods=['POST'])
def test_scraper():
    """Test endpoint to verify scraper is working"""
    try:
        data = request.get_json()
        test_url = data.get('url', 'https://www.instagram.com/p/test/')
        
        logger.info(f"Testing scraper with URL: {test_url}")
        
        # Try to scrape just a few comments as a test
        comments = instagram_scraper.scrape_comments(test_url, max_comments=10)
        
        return jsonify({
            'success': True,
            'test_url': test_url,
            'comments_found': len(comments),
            'sample_comment': comments[0] if comments else None,
            'message': f'Scraper is working! Found {len(comments)} comments.'
        }), 200
        
    except Exception as e:
        logger.error(f"Scraper test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Scraper test failed. Check API key and actor configuration.'
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_post():
    """
    Analyze Instagram or Facebook post comments
    Expected JSON body: { "url": "post_url", "platform": "instagram" or "facebook" (optional) }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'error': 'Post URL is required',
                'success': False
            }), 400
        
        post_url = data['url']
        
        # Auto-detect platform or use provided platform
        platform = data.get('platform', '')
        if not platform:
            if 'instagram.com' in post_url:
                platform = 'instagram'
            elif 'facebook.com' in post_url:
                platform = 'facebook'
            else:
                return jsonify({
                    'error': 'Unable to detect platform. URL must be from Instagram or Facebook',
                    'success': False
                }), 400
        
        logger.info(f"Starting {platform} analysis for URL: {post_url}")
        
        # Step 1: Scrape comments based on platform
        logger.info("Step 1: Scraping comments...")
        
        if platform == 'instagram':
            comments_data = instagram_scraper.scrape_comments(post_url)
        else:  # facebook
            try:
                comments_data = facebook_scraper.scrape_single_post(post_url)
            except Exception as fb_error:
                error_msg = str(fb_error)
                logger.error(f"Facebook scraping failed: {error_msg}")
                
                # Check if it's a privacy/access issue
                if 'not_available' in error_msg.lower() or 'cannot access' in error_msg.lower():
                    return jsonify({
                        'error': 'Cannot access this Facebook post',
                        'success': False,
                        'details': {
                            'url': post_url,
                            'reason': 'The post is private, restricted, or deleted',
                            'explanation': error_msg,
                            'solutions': [
                                '⚠️ Facebook requires authentication to access most posts',
                                '✓ Try a PUBLIC post from a public page (e.g., NASA, Tesla, news outlets)',
                                '✓ Ensure the post is not deleted or restricted',
                                '✓ For groups: The group must be PUBLIC',
                                '⚠️ Note: Personal profiles and private groups cannot be scraped without login'
                            ]
                        }
                    }), 403
                else:
                    # Other scraping errors
                    raise fb_error
        
        if not comments_data or len(comments_data) == 0:
            logger.warning(f"No comments found for URL: {post_url}")
            return jsonify({
                'error': 'No comments found',
                'success': False,
                'details': {
                    'url': post_url,
                    'comments_found': 0,
                    'platform': platform,
                    'suggestions': [
                        'The post may have zero comments',
                        'Verify the post URL is correct',
                        'For Facebook: Use public pages/groups only (e.g., NASA, BBC News)',
                        'For Instagram: Ensure the post is public',
                        'Check your Apify API credits at https://console.apify.com'
                    ]
                }
            }), 404
        
        logger.info(f"Scraped {len(comments_data)} comments")
        
        # Step 2: Perform sentiment analysis on all comments
        logger.info("Step 2: Performing sentiment analysis...")
        analyzed_comments = sentiment_analyzer.analyze_batch(comments_data)
        
        # Step 3: Classify topics for negative comments
        logger.info("Step 3: Classifying topics for negative comments...")
        negative_comments = [c for c in analyzed_comments if c['sentiment'] == 'negative']
        
        if negative_comments:
            negative_comments = topic_classifier.classify_topics(negative_comments)
        
        # Prepare response
        positive_comments = [c for c in analyzed_comments if c['sentiment'] == 'positive']
        neutral_comments = [c for c in analyzed_comments if c['sentiment'] == 'neutral']
        
        # Calculate statistics
        total_comments = len(analyzed_comments)
        sentiment_stats = {
            'positive': len(positive_comments),
            'negative': len(negative_comments),
            'neutral': len(neutral_comments),
            'positive_percentage': round((len(positive_comments) / total_comments) * 100, 2),
            'negative_percentage': round((len(negative_comments) / total_comments) * 100, 2),
            'neutral_percentage': round((len(neutral_comments) / total_comments) * 100, 2)
        }
        
        # Get topic distribution for negative comments
        topic_stats = {}
        if negative_comments:
            for comment in negative_comments:
                topic = comment.get('topic', 'Other')
                topic_stats[topic] = topic_stats.get(topic, 0) + 1
        
        logger.info("Analysis completed successfully")
        
        return jsonify({
            'success': True,
            'data': {
                'post_url': post_url,
                'platform': platform,
                'total_comments': total_comments,
                'sentiment_stats': sentiment_stats,
                'topic_stats': topic_stats,
                'all_comments': {
                    'positive': positive_comments,
                    'negative': negative_comments,
                    'neutral': neutral_comments
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'success': False,
            'details': {
                'error_type': type(e).__name__,
                'message': 'An error occurred during analysis. Check server logs for details.'
            }
        }), 500

@app.route('/api/analyze-profile', methods=['POST'])
def analyze_profile():
    """
    Analyze all posts from an Instagram profile from a given date onwards
    Expected JSON body: { 
        "profile_url": "instagram_profile_url",
        "from_date": "YYYY-MM-DD" (optional),
        "max_posts": 50 (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'profile_url' not in data:
            return jsonify({
                'error': 'Profile URL is required',
                'success': False
            }), 400
        
        profile_url = data['profile_url']
        from_date = data.get('from_date', None)
        max_posts = data.get('max_posts', 50)
        
        logger.info(f"Starting bulk analysis for profile: {profile_url} from date: {from_date}")
        logger.info(f"Max posts: {max_posts}")
        
        # Step 1: Scrape all posts and their comments
        logger.info("Step 1: Scraping posts and comments...")
        try:
            bulk_data = instagram_scraper.scrape_posts_comments_bulk(
                profile_url, 
                from_date, 
                max_posts
            )
        except Exception as scrape_error:
            logger.error(f"Scraping failed: {str(scrape_error)}", exc_info=True)
            return jsonify({
                'error': f'Failed to scrape profile: {str(scrape_error)}',
                'success': False,
                'details': {
                    'profile_url': profile_url,
                    'from_date': from_date,
                    'suggestions': [
                        'Check if the profile URL is correct',
                        'Verify the profile is public',
                        'Check your Apify API key and credits',
                        'Try a different profile URL'
                    ]
                }
            }), 500
        
        if bulk_data['total_posts'] == 0:
            logger.warning(f"No posts found for {profile_url} from {from_date}")
            return jsonify({
                'error': 'No posts found or unable to scrape',
                'success': False,
                'details': {
                    'profile_url': profile_url,
                    'from_date': from_date,
                    'posts_found': 0,
                    'suggestions': [
                        'Check if the profile URL is correct (should end with /)',
                        'Verify the profile is public and has posts',
                        'Try a different or earlier date',
                        'Check your Apify API credits at https://console.apify.com'
                    ]
                }
            }), 404
        
        logger.info(f"Scraped {bulk_data['total_posts']} posts with {bulk_data['total_comments']} total comments")
        
        # Step 2: Analyze all comments from all posts
        logger.info("Step 2: Analyzing all comments...")
        all_comments = []
        for post in bulk_data['posts']:
            all_comments.extend(post['comments'])
        
        if not all_comments:
            return jsonify({
                'error': 'No comments found in the posts',
                'success': False
            }), 404
        
        # Perform sentiment analysis on all comments
        analyzed_comments = sentiment_analyzer.analyze_batch(all_comments)
        
        # Step 3: Classify topics for negative comments
        logger.info("Step 3: Classifying topics for negative comments...")
        negative_comments = [c for c in analyzed_comments if c['sentiment'] == 'negative']
        positive_comments = [c for c in analyzed_comments if c['sentiment'] == 'positive']
        neutral_comments = [c for c in analyzed_comments if c['sentiment'] == 'neutral']
        
        if negative_comments:
            negative_comments = topic_classifier.classify_topics(negative_comments)
        
        # Calculate overall statistics
        total_comments = len(analyzed_comments)
        sentiment_stats = {
            'positive': len(positive_comments),
            'negative': len(negative_comments),
            'neutral': len(neutral_comments),
            'positive_percentage': round((len(positive_comments) / total_comments) * 100, 2) if total_comments > 0 else 0,
            'negative_percentage': round((len(negative_comments) / total_comments) * 100, 2) if total_comments > 0 else 0,
            'neutral_percentage': round((len(neutral_comments) / total_comments) * 100, 2) if total_comments > 0 else 0
        }
        
        # Get topic distribution for negative comments
        topic_stats = {}
        if negative_comments:
            for comment in negative_comments:
                topic = comment.get('topic', 'Other')
                topic_stats[topic] = topic_stats.get(topic, 0) + 1
        
        # Organize comments by post
        posts_analysis = []
        for post in bulk_data['posts']:
            post_comments = post['comments']
            post_analyzed = [c for c in analyzed_comments if c.get('id') in [pc.get('id') for pc in post_comments]]
            
            post_negative = [c for c in post_analyzed if c['sentiment'] == 'negative']
            post_positive = [c for c in post_analyzed if c['sentiment'] == 'positive']
            post_neutral = [c for c in post_analyzed if c['sentiment'] == 'neutral']
            
            posts_analysis.append({
                'post_url': post['post_url'],
                'post_date': post['post_date'],
                'total_comments': len(post_analyzed),
                'sentiment_breakdown': {
                    'positive': len(post_positive),
                    'negative': len(post_negative),
                    'neutral': len(post_neutral)
                }
            })
        
        logger.info("Bulk analysis completed successfully")
        
        return jsonify({
            'success': True,
            'data': {
                'profile_url': profile_url,
                'from_date': from_date,
                'total_posts': bulk_data['total_posts'],
                'total_comments': total_comments,
                'sentiment_stats': sentiment_stats,
                'topic_stats': topic_stats,
                'posts_analysis': posts_analysis,
                'negative_comments_details': negative_comments,
                'all_comments': {
                    'positive': positive_comments,
                    'negative': negative_comments,
                    'neutral': neutral_comments
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error during bulk analysis: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'success': False,
            'details': {
                'error_type': type(e).__name__,
                'message': 'An error occurred during profile analysis. Check server logs for details.',
                'profile_url': data.get('profile_url') if 'data' in locals() else None
            }
        }), 500

@app.route('/api/analyze-facebook-group', methods=['POST'])
def analyze_facebook_group():
    """
    Analyze all posts from Facebook (groups, pages, or profiles) from a given date onwards
    Expected JSON body: { 
        "group_url": "facebook_url",  (also accepts page_url or profile_url)
        "from_date": "YYYY-MM-DD" (optional),
        "max_posts": 50 (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Accept group_url, page_url, profile_url, or url
        facebook_url = data.get('group_url') or data.get('page_url') or data.get('profile_url') or data.get('url')
        
        if not facebook_url:
            return jsonify({
                'error': 'Facebook URL is required (group, page, or profile)',
                'success': False
            }), 400
        
        from_date = data.get('from_date', None)
        max_posts = data.get('max_posts', 50)
        
        logger.info(f"Starting Facebook analysis: {facebook_url} from date: {from_date}")
        
        # Step 1: Scrape all posts and their comments from Facebook
        logger.info("Step 1: Scraping Facebook posts and comments...")
        bulk_data = facebook_scraper.scrape_posts_comments_bulk(
            facebook_url, 
            from_date, 
            max_posts
        )
        
        if bulk_data['total_posts'] == 0:
            return jsonify({
                'error': 'No posts found or unable to scrape Facebook URL',
                'success': False
            }), 404
        
        logger.info(f"Scraped {bulk_data['total_posts']} posts with {bulk_data['total_comments']} total comments")
        
        # Step 2: Analyze all comments from all posts
        logger.info("Step 2: Analyzing all comments...")
        all_comments = []
        for post in bulk_data['posts']:
            all_comments.extend(post['comments'])
        
        if not all_comments:
            return jsonify({
                'error': 'No comments found in the posts',
                'success': False
            }), 404
        
        # Perform sentiment analysis on all comments
        analyzed_comments = sentiment_analyzer.analyze_batch(all_comments)
        
        # Step 3: Classify topics for negative comments
        logger.info("Step 3: Classifying topics for negative comments...")
        negative_comments = [c for c in analyzed_comments if c['sentiment'] == 'negative']
        positive_comments = [c for c in analyzed_comments if c['sentiment'] == 'positive']
        neutral_comments = [c for c in analyzed_comments if c['sentiment'] == 'neutral']
        
        if negative_comments:
            negative_comments = topic_classifier.classify_topics(negative_comments)
        
        # Calculate overall statistics
        total_comments = len(analyzed_comments)
        sentiment_stats = {
            'positive': len(positive_comments),
            'negative': len(negative_comments),
            'neutral': len(neutral_comments),
            'positive_percentage': round((len(positive_comments) / total_comments) * 100, 2) if total_comments > 0 else 0,
            'negative_percentage': round((len(negative_comments) / total_comments) * 100, 2) if total_comments > 0 else 0,
            'neutral_percentage': round((len(neutral_comments) / total_comments) * 100, 2) if total_comments > 0 else 0
        }
        
        # Get topic distribution for negative comments
        topic_stats = {}
        if negative_comments:
            for comment in negative_comments:
                topic = comment.get('topic', 'Other')
                topic_stats[topic] = topic_stats.get(topic, 0) + 1
        
        # Organize comments by post
        posts_analysis = []
        for post in bulk_data['posts']:
            post_comments = post['comments']
            post_analyzed = [c for c in analyzed_comments if c.get('id') in [pc.get('id') for pc in post_comments]]
            
            post_negative = [c for c in post_analyzed if c['sentiment'] == 'negative']
            post_positive = [c for c in post_analyzed if c['sentiment'] == 'positive']
            post_neutral = [c for c in post_analyzed if c['sentiment'] == 'neutral']
            
            posts_analysis.append({
                'post_url': post['post_url'],
                'post_date': post['post_date'],
                'total_comments': len(post_analyzed),
                'sentiment_breakdown': {
                    'positive': len(post_positive),
                    'negative': len(post_negative),
                    'neutral': len(post_neutral)
                }
            })
        
        logger.info("Facebook analysis completed successfully")
        
        return jsonify({
            'success': True,
            'data': {
                'type': 'profile',
                'url': facebook_url,
                'from_date': from_date,
                'total_posts': bulk_data['total_posts'],
                'total_comments': total_comments,
                'sentiment_stats': sentiment_stats,
                'topic_stats': topic_stats,
                'posts_analysis': posts_analysis,
                'negative_comments_details': negative_comments,
                'all_comments': {
                    'positive': positive_comments,
                    'negative': negative_comments,
                    'neutral': neutral_comments
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error during Facebook group analysis: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/stats', methods=['POST'])
def get_stats_only():
    """
    Get only statistics without full comment details
    Expected JSON body: { "url": "instagram_post_url" }
    """
    try:
        data = request.get_json()
        instagram_url = data.get('url')
        
        if not instagram_url:
            return jsonify({'error': 'URL is required', 'success': False}), 400
        
        # Scrape and analyze
        comments_data = instagram_scraper.scrape_comments(instagram_url)
        analyzed_comments = sentiment_analyzer.analyze_batch(comments_data)
        
        negative_comments = [c for c in analyzed_comments if c['sentiment'] == 'negative']
        if negative_comments:
            negative_comments = topic_classifier.classify_topics(negative_comments)
        
        # Calculate stats
        total = len(analyzed_comments)
        stats = {
            'total_comments': total,
            'positive': len([c for c in analyzed_comments if c['sentiment'] == 'positive']),
            'negative': len(negative_comments),
            'neutral': len([c for c in analyzed_comments if c['sentiment'] == 'neutral'])
        }
        
        # Topic distribution
        topic_distribution = {}
        for comment in negative_comments:
            topic = comment.get('topic', 'Other')
            topic_distribution[topic] = topic_distribution.get(topic, 0) + 1
        
        return jsonify({
            'success': True,
            'data': {
                'stats': stats,
                'topics': topic_distribution
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
