import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from collections import Counter

logger = logging.getLogger(__name__)

class TopicClassifier:
    """
    Topic classification for negative comments using NLP techniques
    """
    
    def __init__(self):
        """
        Initialize topic classifier with predefined categories
        """
        # Predefined topic categories with extensive keywords
        self.topic_keywords = {
            'Delivery': [
                'delivery', 'late', 'delayed', 'shipping', 'ship', 'arrive', 
                'arrived', 'waiting', 'never received', 'where is', 'not delivered',
                'slow delivery', 'tracking', 'package', 'courier', 'shipment',
                'transit', 'dispatch', 'order', 'missing', 'lost', 'stuck',
                'still waiting', 'not arrived', 'hasnt arrived', 'taking forever',
                'weeks', 'month', 'days', 'when will', 'eta', 'delivery time'
            ],
            'Bad Quality': [
                'quality', 'poor', 'broken', 'damaged', 'defective', 'cheap',
                'terrible', 'horrible', 'trash', 'garbage', 'waste', 'bad quality',
                'low quality', 'fake', 'counterfeit', 'not original', 'durability',
                'poorly made', 'falls apart', 'flimsy', 'weak', 'fragile',
                'disappointing', 'substandard', 'inferior', 'shoddy', 'rubbish',
                'awful', 'pathetic', 'useless', 'worthless', 'junk', 'crap'
            ],
            'Customer Service': [
                'customer service', 'support', 'service', 'representative', 'staff',
                'rude', 'unprofessional', 'no response', 'ignored', 'unhelpful',
                'poor service', 'no help', 'attitude', 'disrespectful', 'agent',
                'customer care', 'help desk', 'support team', 'service team',
                'no reply', 'dont respond', 'wont help', 'bad service', 'worst service',
                'horrible service', 'terrible support', 'useless support', 'no support'
            ],
            'Pricing': [
                'price', 'expensive', 'costly', 'overpriced', 'too much', 'money',
                'refund', 'cost', 'cheap', 'not worth', 'value', 'rip off',
                'scam', 'waste of money', 'overcharge', 'ripoff', 'rip-off',
                'too expensive', 'so expensive', 'very expensive', 'highly priced',
                'charges', 'charged', 'payment', 'paid', 'overpaid', 'not worth it',
                'not worth the price', 'poor value', 'bad value', 'money back'
            ],
            'Product Issues': [
                'not working', 'broken', 'malfunction', 'issue', 'problem', 'error',
                'bug', 'glitch', 'fault', 'defect', 'doesnt work', 'stopped working',
                'not functioning', 'fail', 'failed', 'failure', 'crashes',
                'crash', 'freezes', 'freeze', 'wont work', 'cant use', 'unusable',
                'malfunctioning', 'problems', 'issues', 'technical', 'technical issue',
                'not functional', 'dysfunction', 'broke', 'broke down', 'dead'
            ],
            'False Advertising': [
                'advertised', 'misleading', 'false', 'lie', 'lied', 'not as shown',
                'different', 'not same', 'deceiving', 'fraud', 'scam', 'fake',
                'not as described', 'misleading ad', 'false advertising', 'lies',
                'deceptive', 'not what shown', 'looks different', 'doesnt match',
                'wrong product', 'different product', 'bait and switch', 'scammed',
                'misleading description', 'incorrect description', 'not authentic'
            ]
        }
        
        # Initialize stopwords
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
    
    def extract_keywords(self, text):
        """
        Extract important keywords from text
        
        Args:
            text (str): Comment text
            
        Returns:
            list: List of keywords
        """
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        try:
            words = word_tokenize(text)
        except:
            words = text.split()
        
        # Remove stopwords and short words
        keywords = [
            word for word in words 
            if word not in self.stop_words 
            and len(word) > 2
            and word.isalpha()
        ]
        
        return keywords
    
    def detect_strong_negative_words(self, text):
        """
        Detect strong negative words across multiple languages
        
        Args:
            text (str): Comment text
            
        Returns:
            bool: True if strong negative indicators found
        """
        text_lower = text.lower()
        
        # Strong negative words (English and transliterated)
        strong_negatives = [
            # English
            'hate', 'worst', 'terrible', 'horrible', 'awful', 'disgusting',
            'pathetic', 'useless', 'trash', 'garbage', 'scam', 'fraud', 'fake',
            'shit', 'crap', 'sucks', 'suck', 'damn', 'hell', 'never',
            # Urdu/Hindi transliterations
            'bakwas', 'bekar', 'kharab', 'ganda', 'bura', 'kachra',
            # Arabic/Urdu
            'wahshat', 'kharaab', 'ghalat', 
        ]
        
        return any(word in text_lower for word in strong_negatives)
    
    def analyze_sentiment_context(self, text):
        """
        Analyze the context and semantic meaning when keywords don't match
        Uses pattern recognition and semantic analysis
        
        Args:
            text (str): Comment text
            
        Returns:
            str: Best guess topic based on context
        """
        text_lower = text.lower()
        
        # Quality-related patterns (expanded with multilingual)
        quality_patterns = ['bad', 'worst', 'terrible', 'horrible', 'awful', 'poor', 
                           'disappointing', 'disappointed', 'not good', 'useless',
                           'trash', 'garbage', 'waste', 'pathetic', 'yomon', 'kharab']
        
        # Service-related patterns
        service_patterns = ['service', 'staff', 'support', 'help', 'response', 
                           'rude', 'unprofessional', 'ignored', 'attitude', 'xizmat']
        
        # Product functionality patterns
        function_patterns = ['work', 'working', 'broken', 'issue', 'problem', 
                            'error', 'bug', 'crash', 'fail', 'buzilgan', 'ishlamaydi']
        
        # Price-related patterns (expanded)
        price_patterns = ['price', 'money', 'expensive', 'cost', 'paid', 
                         'refund', 'worth', 'value', 'qimmat', 'narx', 'pul',
                         'mehnga', 'paisa', 'rupee']
        
        # Delivery-related patterns
        delivery_patterns = ['deliver', 'ship', 'order', 'receive', 'arrive',
                            'wait', 'late', 'delay', 'package', 'yetkazib', 'buyurtma']
        
        # Check each pattern category with priority
        if any(pattern in text_lower for pattern in delivery_patterns):
            return 'Delivery'
        if any(pattern in text_lower for pattern in price_patterns):
            return 'Pricing'
        if any(pattern in text_lower for pattern in service_patterns):
            return 'Customer Service'
        if any(pattern in text_lower for pattern in function_patterns):
            return 'Product Issues'
        if any(pattern in text_lower for pattern in quality_patterns):
            return 'Bad Quality'
        
        # Check for strong negative words
        if self.detect_strong_negative_words(text):
            return 'Bad Quality'
        
        # If still no match, analyze comment length and structure
        words = text_lower.split()
        if len(words) <= 3:
            # Very short negative comments are usually about quality
            return 'Bad Quality'
        elif len(words) <= 10:
            # Medium comments might be about product issues
            return 'Product Issues'
        else:
            # Longer complaints are often about service or experience
            return 'Customer Service'
    
    def classify_topic_by_keywords(self, text):
        """
        Classify topic based on keyword matching with weighted scoring
        
        Args:
            text (str): Comment text
            
        Returns:
            str: Topic category
        """
        text_lower = text.lower()
        
        # Score each topic category with weighted matching
        topic_scores = {}
        for topic, keywords in self.topic_keywords.items():
            score = 0
            for keyword in keywords:
                # Multi-word phrase matching gets higher weight
                if ' ' in keyword and keyword in text_lower:
                    score += 3  # Higher weight for phrase matches
                elif keyword in text_lower:
                    # Check for whole word match
                    words_in_text = text_lower.split()
                    if keyword in words_in_text:
                        score += 2  # Full word match
                    else:
                        score += 1  # Partial match
            topic_scores[topic] = score
        
        # Get topic with highest score
        max_score = max(topic_scores.values())
        if max_score > 0:
            best_topic = max(topic_scores, key=topic_scores.get)
            return best_topic
        
        # If no keywords matched, use semantic analysis
        return self.analyze_sentiment_context(text)
    
    def classify_topics(self, negative_comments):
        """
        Classify topics for all negative comments with intelligent fallback
        
        Args:
            negative_comments (list): List of negative comment dictionaries
            
        Returns:
            list: Comments with topic classification added
        """
        logger.info(f"Classifying topics for {len(negative_comments)} negative comments...")
        
        if len(negative_comments) == 0:
            return negative_comments
        
        # Classify each comment
        for comment in negative_comments:
            text = comment.get('cleaned_text', comment.get('text', ''))
            
            if not text or len(text.strip()) == 0:
                # Even empty comments get a topic based on context
                comment['topic'] = 'Bad Quality'
                comment['keywords'] = []
                continue
            
            # Classify topic using keyword matching (with semantic fallback)
            topic = self.classify_topic_by_keywords(text)
            comment['topic'] = topic
            
            # Extract key phrases for this comment
            keywords = self.extract_keywords(text)
            comment['keywords'] = keywords[:5]  # Top 5 keywords
            
            # Log individual classification for debugging
            logger.debug(f"Comment: '{text[:50]}...' -> Topic: {topic}")
        
        # Log topic distribution
        topic_counts = Counter([c['topic'] for c in negative_comments])
        logger.info(f"Topic distribution: {dict(topic_counts)}")
        
        return negative_comments
    
    def get_topic_summary(self, negative_comments):
        """
        Get summary of topics found in negative comments
        
        Args:
            negative_comments (list): List of classified negative comments
            
        Returns:
            dict: Topic summary with counts and percentages
        """
        if not negative_comments:
            return {}
        
        total = len(negative_comments)
        topic_counts = Counter([c.get('topic', 'Other') for c in negative_comments])
        
        summary = {}
        for topic, count in topic_counts.items():
            summary[topic] = {
                'count': count,
                'percentage': round((count / total) * 100, 2)
            }
        
        return summary
