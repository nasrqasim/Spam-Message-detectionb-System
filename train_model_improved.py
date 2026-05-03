import pandas as pd
import numpy as np
import re
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Download NLTK data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

class SpamDetectorTrainer:
    def __init__(self):
        """Initialize the spam detector trainer with all necessary components"""
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Add custom spam-related stopwords to keep
        self.spam_keywords = {
            'free', 'win', 'click', 'offer', 'urgent', 'claim', 'prize', 
            'money', 'cash', 'discount', 'limited', 'exclusive', 'bonus',
            'congratulations', 'winner', 'selected', 'immediately', 'now',
            'today', 'guaranteed', 'risk', 'save', 'deal', 'special'
        }
        
        # Remove spam keywords from stopwords
        self.stop_words = self.stop_words - self.spam_keywords
        
        self.models = {}
        self.vectorizers = {}
        self.scalers = {}
        self.best_model = None
        self.best_model_name = None
        
    def advanced_preprocess_text(self, text):
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
    
    def analyze_dataset_balance(self, df):
        """Analyze and display dataset balance"""
        print("=" * 60)
        print("DATASET ANALYSIS")
        print("=" * 60)
        print(f"Total samples: {len(df)}")
        print(f"Class distribution:")
        print(df['spam'].value_counts())
        
        spam_ratio = df['spam'].value_counts()[1] / len(df)
        ham_ratio = df['spam'].value_counts()[0] / len(df)
        
        print(f"\nSpam ratio: {spam_ratio:.2%}")
        print(f"Ham ratio: {ham_ratio:.2%}")
        
        if spam_ratio < 0.3 or spam_ratio > 0.7:
            print("⚠️  Dataset is imbalanced. Resampling will be applied.")
            return True
        else:
            print("✅ Dataset is reasonably balanced.")
            return False
    
    def handle_imbalanced_data(self, X, y, method='smote'):
        """
        Handle imbalanced dataset using various resampling techniques
        """
        print(f"\nApplying {method.upper()} resampling...")
        
        if method == 'smote':
            resampler = SMOTE(random_state=42)
        elif method == 'oversample':
            resampler = RandomOverSampler(random_state=42)
        elif method == 'undersample':
            resampler = RandomUnderSampler(random_state=42)
        else:
            print("No resampling applied")
            return X, y
        
        X_resampled, y_resampled = resampler.fit_resample(X, y)
        
        print(f"Original dataset shape: {X.shape}")
        print(f"Resampled dataset shape: {X_resampled.shape}")
        print(f"Resampled class distribution: {np.bincount(y_resampled)}")
        
        return X_resampled, y_resampled
    
    def create_enhanced_features(self, texts):
        """
        Create enhanced TF-IDF features with spam keyword emphasis
        """
        # Enhanced TF-IDF Vectorizer
        vectorizer = TfidfVectorizer(
            max_features=8000,           # Increased feature count
            ngram_range=(1, 3),          # Use 1-3 grams for better context
            min_df=2,                     # Minimum document frequency
            max_df=0.95,                  # Maximum document frequency
            sublinear_tf=True,            # Apply sublinear TF scaling
            stop_words=None               # We handle stopwords manually
        )
        
        # Fit and transform
        X_tfidf = vectorizer.fit_transform(texts)
        
        return vectorizer, X_tfidf
    
    def train_multiple_models(self, X_train, y_train, X_test, y_test):
        """
        Train multiple models and compare their performance
        """
        print("\n" + "=" * 60)
        print("TRAINING MULTIPLE MODELS")
        print("=" * 60)
        
        # Define models with optimized parameters
        models = {
            'Naive Bayes': MultinomialNB(alpha=0.1),
            'Logistic Regression': LogisticRegression(
                random_state=42, 
                max_iter=1000,
                C=1.0,
                penalty='l2',
                solver='liblinear'
            ),
            'Support Vector Machine': SVC(
                random_state=42,
                probability=True,
                C=1.0,
                kernel='linear'
            ),
            'Random Forest': RandomForestClassifier(
                random_state=42,
                n_estimators=100,
                max_depth=10,
                min_samples_split=5
            )
        }
        
        results = {}
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'cv_score': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'predictions': y_pred,
                'probabilities': y_proba
            }
            
            print(f"  Accuracy: {accuracy:.4f}")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall: {recall:.4f}")
            print(f"  F1-Score: {f1:.4f}")
            print(f"  CV F1-Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Find best model based on F1-score
        best_model_name = max(results.keys(), key=lambda k: results[k]['f1'])
        self.best_model = results[best_model_name]['model']
        self.best_model_name = best_model_name
        
        print(f"\n🏆 BEST MODEL: {best_model_name}")
        print(f"   F1-Score: {results[best_model_name]['f1']:.4f}")
        print(f"   Accuracy: {results[best_model_name]['accuracy']:.4f}")
        print(f"   Precision: {results[best_model_name]['precision']:.4f}")
        print(f"   Recall: {results[best_model_name]['recall']:.4f}")
        
        return results
    
    def evaluate_best_model(self, results, y_test):
        """
        Detailed evaluation of the best model
        """
        print("\n" + "=" * 60)
        print("DETAILED EVALUATION OF BEST MODEL")
        print("=" * 60)
        
        best_result = results[self.best_model_name]
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, best_result['predictions'], 
                                  target_names=['Not Spam', 'Spam']))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, best_result['predictions'])
        print("\nConfusion Matrix:")
        print(cm)
        
        print("\nConfusion Matrix Interpretation:")
        tn, fp, fn, tp = cm.ravel()
        print(f"True Negatives (Not Spam correctly identified): {tn}")
        print(f"False Positives (Not Spam incorrectly labeled as Spam): {fp}")
        print(f"False Negatives (Spam incorrectly labeled as Not Spam): {fn}")
        print(f"True Positives (Spam correctly identified): {tp}")
        
        # Calculate additional metrics
        specificity = tn / (tn + fp)
        sensitivity = tp / (tp + fn)
        
        print(f"\nSpecificity (True Negative Rate): {specificity:.4f}")
        print(f"Sensitivity (True Positive Rate): {sensitivity:.4f}")
        
        return cm
    
    def save_model_artifacts(self, vectorizer, results):
        """
        Save the best model and preprocessing artifacts
        """
        print("\n" + "=" * 60)
        print("SAVING MODEL ARTIFACTS")
        print("=" * 60)
        
        # Save best model
        with open('best_model.pkl', 'wb') as f:
            pickle.dump(self.best_model, f)
        
        # Save vectorizer
        with open('vectorizer.pkl', 'wb') as f:
            pickle.dump(vectorizer, f)
        
        # Save preprocessing info
        with open('preprocess_info.pkl', 'wb') as f:
            pickle.dump({
                'stemmer': self.stemmer,
                'lemmatizer': self.lemmatizer,
                'stop_words': self.stop_words,
                'spam_keywords': self.spam_keywords,
                'best_model_name': self.best_model_name
            }, f)
        
        # Save all model results for comparison
        with open('model_results.pkl', 'wb') as f:
            pickle.dump(results, f)
        
        print("✅ Model artifacts saved successfully:")
        print("   - best_model.pkl (Best trained model)")
        print("   - vectorizer.pkl (TF-IDF vectorizer)")
        print("   - preprocess_info.pkl (Preprocessing configuration)")
        print("   - model_results.pkl (All model results)")
    
    def train_complete_pipeline(self, csv_path='../archive/emails.csv', resampling_method='smote'):
        """
        Complete training pipeline from data loading to model saving
        """
        print("🚀 STARTING IMPROVED SPAM DETECTOR TRAINING")
        print("=" * 60)
        
        # 1. Load dataset
        print("Loading dataset...")
        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            print(f"❌ Dataset not found at {csv_path}")
            return None
        
        print(f"Dataset loaded: {df.shape}")
        
        # 2. Analyze dataset balance
        is_imbalanced = self.analyze_dataset_balance(df)
        
        # 3. Advanced preprocessing
        print("\n" + "=" * 60)
        print("ADVANCED TEXT PREPROCESSING")
        print("=" * 60)
        print("Cleaning and preprocessing text data...")
        
        df['processed_text'] = df['text'].apply(self.advanced_preprocess_text)
        
        # Show some examples
        print("\nPreprocessing examples:")
        for i in range(min(3, len(df))):
            print(f"\nOriginal: {df['text'].iloc[i][:100]}...")
            print(f"Processed: {df['processed_text'].iloc[i][:100]}...")
        
        # 4. Feature engineering
        print("\n" + "=" * 60)
        print("FEATURE ENGINEERING")
        print("=" * 60)
        print("Creating enhanced TF-IDF features...")
        
        vectorizer, X_tfidf = self.create_enhanced_features(df['processed_text'])
        y = df['spam']
        
        print(f"Feature matrix shape: {X_tfidf.shape}")
        print(f"Number of features: {len(vectorizer.get_feature_names_out())}")
        
        # 5. Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_tfidf, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\nData split:")
        print(f"Training set: {X_train.shape}")
        print(f"Test set: {X_test.shape}")
        
        # 6. Handle imbalanced data
        if is_imbalanced:
            X_train_resampled, y_train_resampled = self.handle_imbalanced_data(
                X_train, y_train, resampling_method
            )
        else:
            X_train_resampled, y_train_resampled = X_train, y_train
        
        # 7. Train multiple models
        results = self.train_multiple_models(
            X_train_resampled, y_train_resampled, X_test, y_test
        )
        
        # 8. Evaluate best model
        confusion_mat = self.evaluate_best_model(results, y_test)
        
        # 9. Save model artifacts
        self.save_model_artifacts(vectorizer, results)
        
        print("\n🎉 TRAINING COMPLETED SUCCESSFULLY!")
        print(f"Best model: {self.best_model_name}")
        print(f"Test F1-Score: {results[self.best_model_name]['f1']:.4f}")
        print(f"Test Accuracy: {results[self.best_model_name]['accuracy']:.4f}")
        
        return results, confusion_mat

def main():
    """Main function to run the improved training pipeline"""
    trainer = SpamDetectorTrainer()
    
    # Train the complete pipeline
    results, confusion_mat = trainer.train_complete_pipeline(
        csv_path='../archive/emails.csv',
        resampling_method='smote'  # Options: 'smote', 'oversample', 'undersample', None
    )
    
    if results:
        print("\n📊 FINAL MODEL COMPARISON:")
        print("-" * 40)
        for name, result in results.items():
            marker = "🏆" if name == trainer.best_model_name else "  "
            print(f"{marker} {name}:")
            print(f"     F1-Score: {result['f1']:.4f}")
            print(f"     Accuracy: {result['accuracy']:.4f}")
            print(f"     Precision: {result['precision']:.4f}")
            print(f"     Recall: {result['recall']:.4f}")
    
    return trainer, results

if __name__ == "__main__":
    trainer, results = main()
