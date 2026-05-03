from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Load improved model artifacts
try:
    with open('best_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    
    with open('preprocess_info.pkl', 'rb') as f:
        preprocess_info = pickle.load(f)
    
    # Load model results for additional info
    try:
        with open('model_results.pkl', 'rb') as f:
            model_results = pickle.load(f)
    except FileNotFoundError:
        model_results = {}
    
    stemmer = preprocess_info['stemmer']
    lemmatizer = preprocess_info['lemmatizer']
    stop_words = preprocess_info['stop_words']
    spam_keywords = preprocess_info['spam_keywords']
    best_model_name = preprocess_info.get('best_model_name', 'Unknown')
    
    print(f"✅ Improved model loaded successfully!")
    print(f"   Best model: {best_model_name}")
    print(f"   Vectorizer features: {len(vectorizer.get_feature_names_out())}")
    
except FileNotFoundError as e:
    print(f"❌ Error loading model files: {e}")
    print("Please run train_model_improved.py first.")
    model = None
    vectorizer = None
    stemmer = None
    lemmatizer = None
    stop_words = None
    spam_keywords = set()
    best_model_name = None
    model_results = {}

class ImprovedPreprocessor:
    """Advanced text preprocessing matching the training pipeline"""
    
    def __init__(self, stemmer, lemmatizer, stop_words, spam_keywords):
        self.stemmer = stemmer
        self.lemmatizer = lemmatizer
        self.stop_words = stop_words
        self.spam_keywords = spam_keywords
    
    def preprocess_text(self, text):
        """
        Advanced text preprocessing with multiple cleaning steps
        """
        if not isinstance(text, str):
            return ""
        
        # 1. Convert to lowercase
        text = text.lower()
        
        # 2. Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # 3. Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', text)
        
        # 4. Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' ', text)
        
        # 5. Remove numbers (keep them if they're part of spam indicators)
        text = re.sub(r'\b\d+\b', ' ', text)
        
        # 6. Remove punctuation and special characters (except spaces)
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 7. Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 8. Tokenization
        tokens = word_tokenize(text)
        
        # 9. Normalize repeated characters (e.g., "FREEEEE" → "free")
        normalized_tokens = []
        for token in tokens:
            # Reduce repeated characters to max 2
            token = re.sub(r'(.)\1{2,}', r'\1\1', token)
            normalized_tokens.append(token)
        
        # 10. Remove stopwords and apply stemming/lemmatization
        processed_tokens = []
        for token in normalized_tokens:
            if token not in self.stop_words and len(token) > 2:
                # Apply lemmatization first, then stemming
                token = self.lemmatizer.lemmatize(token)
                token = self.stemmer.stem(token)
                processed_tokens.append(token)
        
        # 11. Join tokens back to string
        return ' '.join(processed_tokens)

# Initialize preprocessor
preprocessor = ImprovedPreprocessor(stemmer, lemmatizer, stop_words, spam_keywords)

def calibrate_confidence(raw_confidence, prediction, text_length, spam_word_count):
    """
    Calibrate confidence based on multiple factors for better reliability
    """
    # Base confidence from model
    calibrated_conf = raw_confidence
    
    # Boost confidence for obvious spam indicators
    if prediction == 1:  # Spam
        # Boost for longer spam messages
        if text_length > 100:
            calibrated_conf += 0.05
        
        # Boost for high spam keyword density
        spam_density = spam_word_count / max(text_length / 10, 1)
        if spam_density > 0.3:
            calibrated_conf += 0.1
        elif spam_density > 0.2:
            calibrated_conf += 0.05
        
        # Boost for very high raw confidence
        if raw_confidence > 0.9:
            calibrated_conf = min(0.98, calibrated_conf + 0.05)
        elif raw_confidence > 0.8:
            calibrated_conf = min(0.92, calibrated_conf + 0.03)
    
    else:  # Not Spam
        # Slightly reduce confidence for ham to be more conservative
        if raw_confidence > 0.95:
            calibrated_conf = min(0.98, raw_confidence - 0.02)
    
    # Ensure confidence stays within valid range
    calibrated_conf = max(0.5, min(0.99, calibrated_conf))
    
    return calibrated_conf

def get_spam_indicators(text):
    """Count spam indicators in text"""
    spam_indicators = 0
    text_lower = text.lower()
    
    # Count spam keywords
    for keyword in spam_keywords:
        if keyword in text_lower:
            spam_indicators += text_lower.count(keyword)
    
    # Check for typical spam patterns
    if re.search(r'free|win|click|offer|urgent|claim|prize|money|cash|discount|limited|exclusive|bonus', text_lower):
        spam_indicators += 2
    
    # Check for excessive punctuation
    if re.search(r'[!]{3,}', text):
        spam_indicators += 1
    
    # Check for all caps
    if len([c for c in text if c.isupper()]) > len(text) * 0.3:
        spam_indicators += 1
    
    return spam_indicators

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    health_data = {
        'status': 'healthy',
        'model_loaded': model is not None,
        'vectorizer_loaded': vectorizer is not None,
        'best_model_name': best_model_name,
        'model_type': type(model).__name__ if model else None,
        'feature_count': len(vectorizer.get_feature_names_out()) if vectorizer else 0,
        'spam_keywords_count': len(spam_keywords) if spam_keywords else 0
    }
    
    # Add model performance info if available
    if model_results and best_model_name in model_results:
        result = model_results[best_model_name]
        health_data.update({
            'model_performance': {
                'accuracy': result['accuracy'],
                'precision': result['precision'],
                'recall': result['recall'],
                'f1_score': result['f1']
            }
        })
    
    return jsonify(health_data)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Enhanced prediction endpoint with improved confidence calibration
    """
    try:
        # Check if model is loaded
        if model is None or vectorizer is None:
            return jsonify({
                'error': 'Model not loaded. Please train the improved model first.'
            }), 500
        
        # Get message from request
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing "message" field in request'
            }), 400
        
        message = data['message']
        
        # Validate message
        if not isinstance(message, str) or len(message.strip()) == 0:
            return jsonify({
                'error': 'Message must be a non-empty string'
            }), 400
        
        # Preprocess the message using improved preprocessing
        processed_message = preprocessor.preprocess_text(message)
        
        # Transform using TF-IDF vectorizer
        message_tfidf = vectorizer.transform([processed_message])
        
        # Make prediction
        prediction = model.predict(message_tfidf)[0]
        
        # Get prediction probabilities
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(message_tfidf)[0]
            raw_confidence = max(probabilities)
            spam_probability = probabilities[1] if len(probabilities) > 1 else probabilities[0]
        else:
            # Fallback for models without predict_proba
            raw_confidence = 0.85  # Default high confidence
            spam_probability = 0.85 if prediction == 1 else 0.15
        
        # Get spam indicators for confidence calibration
        spam_indicators = get_spam_indicators(message)
        
        # Calibrate confidence
        calibrated_confidence = calibrate_confidence(
            raw_confidence, prediction, len(message), spam_indicators
        )
        
        # Convert prediction to human-readable format
        result = "Spam" if prediction == 1 else "Not Spam"
        
        # Determine confidence level
        if calibrated_confidence >= 0.80:
            confidence_level = "High"
        elif calibrated_confidence >= 0.60:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
        
        return jsonify({
            'prediction': result,
            'confidence': round(calibrated_confidence, 4),
            'confidence_level': confidence_level,
            'spam_probability': round(spam_probability, 4),
            'message_length': len(message),
            'processed_message': processed_message,
            'spam_indicators': spam_indicators,
            'model_used': best_model_name,
            'processing_details': {
                'raw_confidence': round(raw_confidence, 4),
                'calibrated': True
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'An error occurred during prediction: {str(e)}'
        }), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Enhanced batch prediction endpoint
    """
    try:
        # Check if model is loaded
        if model is None or vectorizer is None:
            return jsonify({
                'error': 'Model not loaded. Please train the improved model first.'
            }), 500
        
        # Get messages from request
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({
                'error': 'Missing "messages" field in request'
            }), 400
        
        messages = data['messages']
        
        # Validate messages
        if not isinstance(messages, list) or len(messages) == 0:
            return jsonify({
                'error': 'Messages must be a non-empty list'
            }), 400
        
        results = []
        
        for i, message in enumerate(messages):
            try:
                if not isinstance(message, str) or len(message.strip()) == 0:
                    results.append({
                        'index': i,
                        'prediction': 'Error',
                        'confidence': 0,
                        'error': 'Invalid message'
                    })
                    continue
                
                # Preprocess the message
                processed_message = preprocessor.preprocess_text(message)
                
                # Transform using TF-IDF vectorizer
                message_tfidf = vectorizer.transform([processed_message])
                
                # Make prediction
                prediction = model.predict(message_tfidf)[0]
                
                # Get prediction probabilities
                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(message_tfidf)[0]
                    raw_confidence = max(probabilities)
                    spam_probability = probabilities[1] if len(probabilities) > 1 else probabilities[0]
                else:
                    raw_confidence = 0.85
                    spam_probability = 0.85 if prediction == 1 else 0.15
                
                # Get spam indicators
                spam_indicators = get_spam_indicators(message)
                
                # Calibrate confidence
                calibrated_confidence = calibrate_confidence(
                    raw_confidence, prediction, len(message), spam_indicators
                )
                
                # Convert prediction to human-readable format
                result = "Spam" if prediction == 1 else "Not Spam"
                
                # Determine confidence level
                if calibrated_confidence >= 0.80:
                    confidence_level = "High"
                elif calibrated_confidence >= 0.60:
                    confidence_level = "Medium"
                else:
                    confidence_level = "Low"
                
                results.append({
                    'index': i,
                    'prediction': result,
                    'confidence': round(calibrated_confidence, 4),
                    'confidence_level': confidence_level,
                    'spam_probability': round(spam_probability, 4),
                    'message_length': len(message),
                    'spam_indicators': spam_indicators,
                    'processing_details': {
                        'raw_confidence': round(raw_confidence, 4),
                        'calibrated': True
                    }
                })
                
            except Exception as e:
                results.append({
                    'index': i,
                    'prediction': 'Error',
                    'confidence': 0,
                    'error': str(e)
                })
        
        # Calculate batch statistics
        successful_predictions = [r for r in results if 'error' not in r]
        spam_count = sum(1 for r in successful_predictions if r['prediction'] == 'Spam')
        avg_confidence = np.mean([r['confidence'] for r in successful_predictions]) if successful_predictions else 0
        
        return jsonify({
            'predictions': results,
            'batch_statistics': {
                'total_messages': len(messages),
                'successful_predictions': len(successful_predictions),
                'spam_messages': spam_count,
                'ham_messages': len(successful_predictions) - spam_count,
                'average_confidence': round(avg_confidence, 4)
            },
            'model_used': best_model_name
        })
        
    except Exception as e:
        return jsonify({
            'error': f'An error occurred during batch prediction: {str(e)}'
        }), 500

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get detailed information about the loaded model"""
    if not model_results or best_model_name not in model_results:
        return jsonify({'error': 'Model results not available'}), 404
    
    result = model_results[best_model_name]
    
    return jsonify({
        'model_name': best_model_name,
        'model_type': type(model).__name__,
        'performance_metrics': {
            'accuracy': result['accuracy'],
            'precision': result['precision'],
            'recall': result['recall'],
            'f1_score': result['f1'],
            'cv_score': result['cv_score'],
            'cv_std': result['cv_std']
        },
        'feature_count': len(vectorizer.get_feature_names_out()) if vectorizer else 0,
        'spam_keywords_count': len(spam_keywords) if spam_keywords else 0,
        'preprocessing_features': [
            'HTML tag removal',
            'URL removal',
            'Email removal',
            'Number removal',
            'Punctuation removal',
            'Character normalization',
            'Stopword removal',
            'Stemming & Lemmatization',
            'N-gram features (1-3)',
            'TF-IDF weighting'
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Improved Spam Detection API...")
    print("=" * 50)
    print("Available endpoints:")
    print("  GET  /health - Enhanced health check")
    print("  GET  /model/info - Detailed model information")
    print("  POST /predict - Enhanced single prediction")
    print("  POST /predict/batch - Enhanced batch prediction")
    print("\nFeatures:")
    print("  ✅ Advanced text preprocessing")
    print("  ✅ Confidence calibration")
    print("  ✅ Spam indicator analysis")
    print("  ✅ Multiple model support")
    print("  ✅ Enhanced error handling")
    print("\nExample usage:")
    print("  POST /predict")
    print('  {"message": "Your message here"}')
    print("\nServer running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
