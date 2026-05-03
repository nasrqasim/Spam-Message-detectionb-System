from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Load model artifacts
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    
    with open('preprocess_info.pkl', 'rb') as f:
        preprocess_info = pickle.load(f)
    
    stemmer = preprocess_info['stemmer']
    stop_words = preprocess_info['stop_words']
    
    print("Model and vectorizer loaded successfully!")
    
except FileNotFoundError:
    print("Error: Model files not found. Please run train_model.py first.")
    model = None
    vectorizer = None
    stemmer = None
    stop_words = None

def preprocess_text(text):
    """
    Preprocess text data:
    1. Convert to lowercase
    2. Remove punctuation
    3. Remove stopwords
    4. Tokenization and stemming
    """
    if stemmer is None or stop_words is None:
        return text
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and special characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenization
    tokens = nltk.word_tokenize(text)
    
    # Remove stopwords and apply stemming
    tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]
    
    # Join tokens back to string
    return ' '.join(tokens)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'vectorizer_loaded': vectorizer is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict if a message is spam or not spam
    
    Expected input:
    {
        "message": "your text here"
    }
    
    Output:
    {
        "prediction": "Spam" or "Not Spam",
        "confidence": 0.95
    }
    """
    try:
        # Check if model is loaded
        if model is None or vectorizer is None:
            return jsonify({
                'error': 'Model not loaded. Please train the model first.'
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
        
        # Preprocess the message
        processed_message = preprocess_text(message)
        
        # Transform using TF-IDF vectorizer
        message_tfidf = vectorizer.transform([processed_message])
        
        # Make prediction
        prediction = model.predict(message_tfidf)[0]
        
        # Get prediction probabilities
        probabilities = model.predict_proba(message_tfidf)[0]
        confidence = max(probabilities)
        
        # Convert prediction to human-readable format
        result = "Spam" if prediction == 1 else "Not Spam"
        
        return jsonify({
            'prediction': result,
            'confidence': round(float(confidence), 4),
            'message_length': len(message),
            'processed_message': processed_message
        })
        
    except Exception as e:
        return jsonify({
            'error': f'An error occurred during prediction: {str(e)}'
        }), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Predict multiple messages at once
    
    Expected input:
    {
        "messages": ["message1", "message2", "message3"]
    }
    
    Output:
    {
        "predictions": [
            {"prediction": "Spam", "confidence": 0.95},
            {"prediction": "Not Spam", "confidence": 0.87}
        ]
    }
    """
    try:
        # Check if model is loaded
        if model is None or vectorizer is None:
            return jsonify({
                'error': 'Model not loaded. Please train the model first.'
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
        
        for message in messages:
            if not isinstance(message, str) or len(message.strip()) == 0:
                results.append({
                    'prediction': 'Error',
                    'confidence': 0,
                    'error': 'Invalid message'
                })
                continue
            
            # Preprocess the message
            processed_message = preprocess_text(message)
            
            # Transform using TF-IDF vectorizer
            message_tfidf = vectorizer.transform([processed_message])
            
            # Make prediction
            prediction = model.predict(message_tfidf)[0]
            
            # Get prediction probabilities
            probabilities = model.predict_proba(message_tfidf)[0]
            confidence = max(probabilities)
            
            # Convert prediction to human-readable format
            result = "Spam" if prediction == 1 else "Not Spam"
            
            results.append({
                'prediction': result,
                'confidence': round(float(confidence), 4),
                'message_length': len(message)
            })
        
        return jsonify({
            'predictions': results,
            'total_messages': len(messages)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'An error occurred during batch prediction: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Spam Detection API...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /predict - Predict single message")
    print("  POST /predict/batch - Predict multiple messages")
    print("\nExample usage:")
    print("  POST /predict")
    print('  {"message": "Your message here"}')
    print("\nServer running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
