from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import torch
import logging
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class SentimentAnalyzer:
    """
    Sentiment analysis using BERT model and NLTK
    """
    
    def __init__(self):
        """
        Initialize lightweight multilingual sentiment analysis model
        """
        try:
            logger.info("Loading lightweight sentiment analysis model...")
            
            # Use small, fast multilingual model (only ~120MB, supports 50+ languages)
            try:
                self.model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.model_name,
                    tokenizer=self.model_name
                )
                logger.info("Lightweight multilingual BERT model loaded successfully (supports English, Arabic, Turkish, etc.)")
                self.is_multilingual = True
            except:
                # Fallback to English-only model (already downloaded, very small)
                logger.info("Using English model with enhanced rule-based detection...")
                self.model_name = "distilbert-base-uncased-finetuned-sst-2-english"
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.model_name,
                    tokenizer=self.model_name
                )
                logger.info("DistilBERT model loaded successfully")
                self.is_multilingual = False
            
        except Exception as e:
            logger.error(f"Error loading sentiment model: {str(e)}")
            logger.info("Falling back to TextBlob for sentiment analysis")
            self.sentiment_pipeline = None
            self.is_multilingual = False
    
    def preprocess_text(self, text):
        """
        Clean and preprocess text for analysis
        
        Args:
            text (str): Raw comment text
            
        Returns:
            str: Cleaned text
        """
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags (keep the text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def analyze_sentiment_bert(self, text):
        """
        Analyze sentiment using BERT/XLM-RoBERTa model
        
        Args:
            text (str): Comment text
            
        Returns:
            dict: Sentiment result with label and confidence
        """
        try:
            # Truncate text if too long (BERT has max token limit)
            if len(text) > 512:
                text = text[:512]
            
            result = self.sentiment_pipeline(text)[0]
            
            # Handle different model outputs
            label = result['label']
            score = result['score']
            
            # Map model labels to our sentiment categories
            if self.is_multilingual:
                # nlptown model returns: 1 star, 2 stars, 3 stars, 4 stars, 5 stars
                if '1 star' in label or '2 stars' in label:
                    sentiment = 'negative'
                elif '3 stars' in label:
                    sentiment = 'neutral'
                elif '4 stars' in label or '5 stars' in label:
                    sentiment = 'positive'
                else:
                    # Fallback based on score
                    sentiment = 'neutral' if score < 0.6 else 'positive'
            else:
                # DistilBERT returns: POSITIVE or NEGATIVE
                label_upper = label.upper()
                if 'POSITIVE' in label_upper:
                    sentiment = 'positive'
                elif 'NEGATIVE' in label_upper:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral' if score < 0.6 else 'positive'
            
            # Override to neutral if confidence is too low
            if score < 0.55 and sentiment != 'neutral':
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'confidence': round(score, 4),
                'raw_label': label
            }
            
        except Exception as e:
            logger.error(f"Model analysis error: {str(e)}")
            return self.analyze_sentiment_textblob(text)
    
    def analyze_sentiment_textblob(self, text):
        """
        Fallback sentiment analysis using TextBlob
        
        Args:
            text (str): Comment text
            
        Returns:
            dict: Sentiment result
        """
        try:
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'confidence': round(abs(polarity), 4),
                'raw_label': f'polarity_{polarity}'
            }
            
        except Exception as e:
            logger.error(f"TextBlob analysis error: {str(e)}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'raw_label': 'error'
            }
    
    def detect_neutral_questions(self, text):
        """
        Detect neutral questions and inquiries
        
        Args:
            text (str): Comment text
            
        Returns:
            bool: True if neutral question detected
        """
        text_lower = text.lower().strip()
        
        # Question marks are strong neutral indicators
        if '?' in text:
            # Common neutral question patterns
            neutral_patterns = [
                # Price/availability questions
                'price', 'cost', 'how much', 'available', 'stock', 'buy',
                'where', 'when', 'what', 'which', 'who', 'how',
                # Multi-language price questions
                'nechi', 'necha', 'qancha', 'narxi', 'kvm', 'som',
                'kitna', 'kaise', 'kab', 'kaha', 'kya',
                'kaç', 'ne kadar', 'nerede', 'ne zaman',
                # Short questions (usually neutral)
            ]
            
            # Very short questions are usually neutral
            words = text_lower.split()
            if len(words) <= 5:
                return True
            
            # Check for neutral question patterns
            if any(pattern in text_lower for pattern in neutral_patterns):
                return True
        
        # Comments asking for information (no question mark)
        info_requests = [
            'tell me', 'let me know', 'can you', 'could you',
            'please', 'info', 'information', 'details', 'link'
        ]
        
        if any(request in text_lower for request in info_requests):
            return True
        
        return False
    
    def detect_positive_indicators(self, text):
        """
        Detect positive indicators like emojis, prayers, blessings
        
        Args:
            text (str): Comment text
            
        Returns:
            bool: True if positive indicators found
        """
        # Positive emojis
        positive_emojis = ['❤', '♥', '💕', '💖', '💗', '💓', '💝', '😊', '😍', 
                          '🥰', '😘', '🙏', '👍', '👏', '🎉', '✨', '⭐', '🌟',
                          '💯', '🔥', '😁', '😄', '😃', '🤗', '💪', '🎊']
        
        # Check for positive emojis
        if any(emoji in text for emoji in positive_emojis):
            return True
        
        # Common positive words in multiple languages
        positive_words = [
            # English
            'love', 'great', 'amazing', 'wonderful', 'excellent', 'best', 
            'good', 'nice', 'beautiful', 'perfect', 'awesome', 'fantastic',
            # Arabic/Urdu/Turkish
            'mashallah', 'alhamdulillah', 'inshaallah', 'inshallah', 'masha allah',
            'alhamdu lillah', 'in sha allah', 'allah', 'shukr', 'baraka',
            # Uzbek/Turkish
            'olloh', 'alloh', 'raxmat', 'yaxshi', 'zoʻr', 'ajoyib', 'nasib',
            # General blessings
            'bless', 'blessing', 'blessed', 'congrats', 'congratulations'
        ]
        
        text_lower = text.lower()
        if any(word in text_lower for word in positive_words):
            return True
        
        return False
    
    def analyze_single(self, comment_data):
        """
        Analyze sentiment for a single comment with multilingual support
        
        Args:
            comment_data (dict): Comment dictionary with 'text' field
            
        Returns:
            dict: Comment data with sentiment added
        """
        text = comment_data.get('text', '')
        
        if not text or len(text.strip()) == 0:
            comment_data['sentiment'] = 'neutral'
            comment_data['confidence'] = 0.0
            return comment_data
        
        # Priority 1: Check for neutral questions first
        if self.detect_neutral_questions(text):
            comment_data['sentiment'] = 'neutral'
            comment_data['confidence'] = 0.90
            comment_data['cleaned_text'] = text
            return comment_data
        
        # Priority 2: Check for positive indicators (emojis, blessings, prayers)
        if self.detect_positive_indicators(text):
            comment_data['sentiment'] = 'positive'
            comment_data['confidence'] = 0.85
            comment_data['cleaned_text'] = text
            return comment_data
        
        # Preprocess text
        cleaned_text = self.preprocess_text(text)
        
        # Priority 3: Analyze sentiment with BERT/TextBlob
        if self.sentiment_pipeline:
            result = self.analyze_sentiment_bert(cleaned_text)
        else:
            result = self.analyze_sentiment_textblob(cleaned_text)
        
        # Add sentiment data to comment
        comment_data['sentiment'] = result['sentiment']
        comment_data['confidence'] = result['confidence']
        comment_data['cleaned_text'] = cleaned_text
        
        return comment_data
    
    def analyze_batch(self, comments_list):
        """
        Analyze sentiment for multiple comments
        
        Args:
            comments_list (list): List of comment dictionaries
            
        Returns:
            list: Comments with sentiment analysis added
        """
        logger.info(f"Analyzing sentiment for {len(comments_list)} comments...")
        
        analyzed_comments = []
        for i, comment in enumerate(comments_list):
            try:
                analyzed_comment = self.analyze_single(comment)
                analyzed_comments.append(analyzed_comment)
                
                # Log progress every 50 comments
                if (i + 1) % 50 == 0:
                    logger.info(f"Analyzed {i + 1}/{len(comments_list)} comments")
                    
            except Exception as e:
                logger.error(f"Error analyzing comment {i}: {str(e)}")
                # Add comment with neutral sentiment on error
                comment['sentiment'] = 'neutral'
                comment['confidence'] = 0.0
                analyzed_comments.append(comment)
        
        logger.info("Sentiment analysis completed")
        return analyzed_comments
