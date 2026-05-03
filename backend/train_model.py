import pandas as pd
import numpy as np
import re
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Download NLTK data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

# Initialize stemmer
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """
    Preprocess text data:
    1. Convert to lowercase
    2. Remove punctuation
    3. Remove stopwords
    4. Tokenization and stemming
    """
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

def train_spam_detector():
    """
    Train spam detection model and save artifacts
    """
    print("Loading dataset...")
    
    # Load dataset
    df = pd.read_csv('../archive/emails.csv')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Class distribution:\n{df['spam'].value_counts()}")
    
    # Preprocess text data
    print("Preprocessing text data...")
    df['processed_text'] = df['text'].apply(preprocess_text)
    
    # Prepare features and target
    X = df['processed_text']
    y = df['spam']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Create TF-IDF Vectorizer
    print("Creating TF-IDF features...")
    tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    
    # Fit and transform training data
    X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
    X_test_tfidf = tfidf_vectorizer.transform(X_test)
    
    # Train Naive Bayes model
    print("Training Naive Bayes model...")
    nb_model = MultinomialNB()
    nb_model.fit(X_train_tfidf, y_train)
    
    # Make predictions
    y_pred = nb_model.predict(X_test_tfidf)
    
    # Evaluate model
    print("\n=== MODEL EVALUATION ===")
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    
    # Display confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(cm)
    print("\nConfusion Matrix Interpretation:")
    print(f"True Negatives (Not Spam correctly identified): {cm[0,0]}")
    print(f"False Positives (Not Spam incorrectly labeled as Spam): {cm[0,1]}")
    print(f"False Negatives (Spam incorrectly labeled as Not Spam): {cm[1,0]}")
    print(f"True Positives (Spam correctly identified): {cm[1,1]}")
    
    # Train Logistic Regression as optional model
    print("\nTraining Logistic Regression model...")
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    lr_model.fit(X_train_tfidf, y_train)
    
    # Evaluate Logistic Regression
    y_pred_lr = lr_model.predict(X_test_tfidf)
    lr_accuracy = accuracy_score(y_test, y_pred_lr)
    print(f"Logistic Regression Accuracy: {lr_accuracy:.4f}")
    
    # Save the best model (Naive Bayes) and vectorizer
    print("\nSaving model artifacts...")
    
    # Save Naive Bayes model
    with open('model.pkl', 'wb') as f:
        pickle.dump(nb_model, f)
    
    # Save TF-IDF vectorizer
    with open('vectorizer.pkl', 'wb') as f:
        pickle.dump(tfidf_vectorizer, f)
    
    # Save preprocessing function reference
    with open('preprocess_info.pkl', 'wb') as f:
        pickle.dump({
            'stemmer': stemmer,
            'stop_words': stop_words
        }, f)
    
    print("Model training completed successfully!")
    print("Files saved: model.pkl, vectorizer.pkl, preprocess_info.pkl")
    
    return nb_model, tfidf_vectorizer

if __name__ == "__main__":
    train_spam_detector()
