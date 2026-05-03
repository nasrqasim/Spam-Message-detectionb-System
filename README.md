# Spam Message Detection Web Application

A full-stack web application that classifies messages as "Spam" or "Not Spam (Ham)" using Machine Learning and NLP techniques.

## Features

- **Machine Learning Model**: Naive Bayes classifier with TF-IDF vectorization
- **Modern UI**: Clean React frontend with Tailwind CSS
- **Real-time Prediction**: Fast API responses with confidence scores
- **Example Messages**: Built-in examples for testing
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
spam-email-detection/
├── backend/
│   ├── app.py              # Flask API server
│   ├── train_model.py      # Model training script
│   ├── requirements.txt    # Python dependencies
│   ├── model.pkl          # Trained model (generated)
│   ├── vectorizer.pkl     # TF-IDF vectorizer (generated)
│   └── preprocess_info.pkl # Preprocessing data (generated)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── archive/
    └── emails.csv         # Dataset
```

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the ML model:**
   ```bash
   python train_model.py
   ```
   This will:
   - Load and preprocess the email dataset
   - Train a Naive Bayes classifier
   - Save model artifacts (model.pkl, vectorizer.pkl, preprocess_info.pkl)
   - Display evaluation metrics

4. **Start the Flask API server:**
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

## API Endpoints

### POST `/predict`
Predict if a message is spam or not spam.

**Request:**
```json
{
  "message": "Your message here"
}
```

**Response:**
```json
{
  "prediction": "Spam" or "Not Spam",
  "confidence": 0.95,
  "message_length": 25,
  "processed_message": "processed text"
}
```

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "vectorizer_loaded": true
}
```

### POST `/predict/batch`
Predict multiple messages at once.

**Request:**
```json
{
  "messages": ["message1", "message2", "message3"]
}
```

**Response:**
```json
{
  "predictions": [
    {"prediction": "Spam", "confidence": 0.95},
    {"prediction": "Not Spam", "confidence": 0.87}
  ],
  "total_messages": 2
}
```

## Model Details

### Data Preprocessing
- Text conversion to lowercase
- Punctuation removal
- Stopword removal using NLTK
- Tokenization and stemming

### Feature Engineering
- TF-IDF Vectorizer with max 5000 features
- N-gram range (1, 2) for better context

### Model Performance
- Naive Bayes classifier
- 80% training, 20% test split
- Metrics: Accuracy, Precision, Recall, F1-Score
- Confusion matrix analysis

## Usage

1. **Start both servers** (backend on port 5000, frontend on port 3000)
2. **Open browser** to `http://localhost:3000`
3. **Enter a message** in the text area or use example messages
4. **Click "Check Message"** to see the prediction
5. **View results** with confidence scores

## Example Messages to Test

**Spam Examples:**
- "Congratulations! You've won a $1000 gift card. Click here to claim now!"
- "URGENT: Your account has been suspended. Please verify your information immediately."

**Ham Examples:**
- "Hey, are we still meeting for lunch tomorrow at 12pm?"
- "Can you send me the project files when you get a chance? Thanks!"

## Technologies Used

### Backend
- **Python** - Programming language
- **Flask** - Web framework
- **scikit-learn** - Machine learning library
- **NLTK** - Natural language processing
- **pandas** - Data manipulation
- **numpy** - Numerical computing

### Frontend
- **React** - JavaScript library
- **Vite** - Build tool
- **Tailwind CSS** - CSS framework
- **Axios** - HTTP client

## Troubleshooting

### Common Issues

1. **Model files not found:**
   - Make sure to run `python train_model.py` before starting the API
   - Check that model.pkl, vectorizer.pkl, and preprocess_info.pkl exist

2. **CORS errors:**
   - The backend includes CORS configuration
   - Make sure both servers are running

3. **Frontend build errors:**
   - Run `npm install` to install dependencies
   - Check Node.js version compatibility

4. **Port conflicts:**
   - Backend uses port 5000
   - Frontend uses port 3000
   - Change ports if needed in configuration files

### Performance Tips

- For large datasets, consider increasing max_features in TF-IDF
- Monitor memory usage with large message batches
- Consider model optimization for production deployment

## Future Enhancements

- Add more ML models (Logistic Regression, SVM, etc.)
- Implement model comparison interface
- Add dark/light mode toggle
- Include message history
- Add export functionality
- Deploy to production environment

## License

This project is for educational purposes. Feel free to use and modify as needed.
