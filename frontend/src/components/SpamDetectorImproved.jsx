import React, { useState } from 'react';
import axios from 'axios';

const SpamDetectorImproved = () => {
  const [message, setMessage] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [charCount, setCharCount] = useState(0);
  const [modelInfo, setModelInfo] = useState(null);

  // Enhanced example messages with difficulty levels
  const exampleMessages = [
    {
      text: "Congratulations! You've won a $1000 Walmart gift card. Click here to claim now!",
      type: "spam",
      difficulty: "easy",
      expectedConfidence: "high"
    },
    {
      text: "URGENT: Your account has been suspended. Please verify your information immediately.",
      type: "spam", 
      difficulty: "medium",
      expectedConfidence: "high"
    },
    {
      text: "Hey, are we still meeting for lunch tomorrow at 12pm?",
      type: "ham",
      difficulty: "easy",
      expectedConfidence: "high"
    },
    {
      text: "Can you send me the project files when you get a chance? Thanks!",
      type: "ham",
      difficulty: "easy", 
      expectedConfidence: "high"
    },
    {
      text: "Limited time offer! Get 50% off on all products. Sale ends tonight!",
      type: "spam",
      difficulty: "medium",
      expectedConfidence: "medium"
    },
    {
      text: "The meeting scheduled for today has been moved to 3 PM. Please confirm your attendance.",
      type: "ham",
      difficulty: "medium",
      expectedConfidence: "high"
    }
  ];

  // Load model information on component mount
  React.useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        const response = await axios.get('/api/model/info');
        setModelInfo(response.data);
      } catch (err) {
        console.warn('Could not fetch model info:', err.message);
      }
    };
    fetchModelInfo();
  }, []);

  const handleInputChange = (e) => {
    const text = e.target.value;
    setMessage(text);
    setCharCount(text.length);
    setError('');
  };

  const checkMessage = async () => {
    if (!message.trim()) {
      setError('Please enter a message to check');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('/api/predict', {
        message: message
      });

      setResult(response.data);
    } catch (err) {
      console.error('Error:', err);
      if (err.response) {
        setError(err.response.data.error || 'Server error occurred');
      } else if (err.request) {
        setError('Unable to connect to server. Please check if the backend is running.');
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleText) => {
    setMessage(exampleText);
    setCharCount(exampleText.length);
    setError('');
  };

  const clearForm = () => {
    setMessage('');
    setResult(null);
    setError('');
    setCharCount(0);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      checkMessage();
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.80) return 'text-green-600';
    if (confidence >= 0.60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceBgColor = (confidence) => {
    if (confidence >= 0.80) return 'bg-green-100 border-green-500';
    if (confidence >= 0.60) return 'bg-yellow-100 border-yellow-500';
    return 'bg-red-100 border-red-500';
  };

  const getConfidenceIcon = (level) => {
    switch (level) {
      case 'High':
        return (
          <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'Medium':
        return (
          <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      case 'Low':
        return (
          <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };

  const getDifficultyBadge = (difficulty) => {
    const colors = {
      easy: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      hard: 'bg-red-100 text-red-800'
    };
    return colors[difficulty] || colors.easy;
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Model Info Banner */}
      {modelInfo && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-blue-800">Model Information</h3>
              <p className="text-blue-700 text-sm mt-1">
                Using: {modelInfo.model_name} | Accuracy: {(modelInfo.performance_metrics?.accuracy * 100).toFixed(1)}% | 
                F1-Score: {(modelInfo.performance_metrics?.f1_score * 100).toFixed(1)}%
              </p>
            </div>
            <div className="text-blue-600 text-sm">
              <span className="bg-blue-100 px-3 py-1 rounded-full">
                Enhanced ML Model
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Card */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            Enhanced Spam Message Detector
          </h2>
          <p className="text-gray-600">
            Advanced AI-powered spam detection with improved accuracy and confidence calibration
          </p>
        </div>

        {/* Input Section */}
        <div className="space-y-4">
          <div className="relative">
            <textarea
              value={message}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Type or paste your message here..."
              className="input-field resize-none h-32"
              disabled={loading}
            />
            <div className="absolute bottom-2 right-2 text-xs text-gray-500">
              {charCount} characters
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-lg">
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={checkMessage}
              disabled={loading || !message.trim()}
              className={`btn-primary flex-1 flex items-center justify-center ${
                (loading || !message.trim()) ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {loading ? (
                <>
                  <div className="loading-spinner mr-2"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Analyze Message
                </>
              )}
            </button>
            <button
              onClick={clearForm}
              disabled={loading}
              className="btn-secondary"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Enhanced Result Display */}
        {result && (
          <div className="mt-8">
            <h3 className="text-xl font-semibold mb-4">Analysis Result</h3>
            
            {/* Main Result Card */}
            <div className={`border-l-4 p-6 rounded-lg ${
              result.prediction === 'Spam' ? 'bg-red-50 border-red-500' : 'bg-green-50 border-green-500'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {result.prediction === 'Spam' ? (
                    <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  )}
                  <div>
                    <div className={`font-bold text-2xl ${
                      result.prediction === 'Spam' ? 'text-red-700' : 'text-green-700'
                    }`}>
                      {result.prediction}
                    </div>
                    <div className="text-sm text-gray-600">
                      Message classified as {result.prediction.toLowerCase()}
                    </div>
                  </div>
                </div>
                
                {/* Confidence Badge */}
                <div className={`px-4 py-2 rounded-full border-2 ${getConfidenceBgColor(result.confidence)}`}>
                  <div className="flex items-center space-x-2">
                    {getConfidenceIcon(result.confidence_level)}
                    <div>
                      <div className={`font-semibold ${getConfidenceColor(result.confidence)}`}>
                        {(result.confidence * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-600">
                        {result.confidence_level} Confidence
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Detailed Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                <div className="text-center p-3 bg-white rounded-lg">
                  <div className="text-2xl font-bold text-gray-800">
                    {(result.spam_probability * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-600">Spam Probability</div>
                </div>
                <div className="text-center p-3 bg-white rounded-lg">
                  <div className="text-2xl font-bold text-gray-800">
                    {result.message_length}
                  </div>
                  <div className="text-xs text-gray-600">Characters</div>
                </div>
                <div className="text-center p-3 bg-white rounded-lg">
                  <div className="text-2xl font-bold text-gray-800">
                    {result.spam_indicators}
                  </div>
                  <div className="text-xs text-gray-600">Spam Indicators</div>
                </div>
                <div className="text-center p-3 bg-white rounded-lg">
                  <div className="text-2xl font-bold text-gray-800">
                    {result.model_used?.split(' ')[0] || 'ML'}
                  </div>
                  <div className="text-xs text-gray-600">Model Type</div>
                </div>
              </div>

              {/* Processing Details */}
              {result.processing_details && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-xs text-gray-600">
                    <span className="font-semibold">Processing:</span> 
                    Raw confidence: {(result.processing_details.raw_confidence * 100).toFixed(1)}% → 
                    Calibrated: {(result.confidence * 100).toFixed(1)}%
                    {result.processing_details.calibrated && ' ✨'}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Example Messages Section */}
      <div className="mt-8 bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-xl font-semibold mb-4">Test Examples</h3>
        <p className="text-gray-600 mb-6">
          Click on any example below to test different types of messages:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {exampleMessages.map((example, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 cursor-pointer transition-all hover:shadow-md"
              onClick={() => handleExampleClick(example.text)}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className={`text-xs font-semibold px-2 py-1 rounded ${
                    example.type === 'spam' 
                      ? 'bg-red-100 text-red-700' 
                      : 'bg-green-100 text-green-700'
                  }`}>
                    {example.type.toUpperCase()}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${getDifficultyBadge(example.difficulty)}`}>
                    {example.difficulty}
                  </span>
                </div>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
              <p className="text-sm text-gray-700 line-clamp-3 mb-2">
                {example.text}
              </p>
              <div className="text-xs text-gray-500">
                Expected confidence: {example.expectedConfidence}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Features Section */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-8">
        <h3 className="text-xl font-semibold mb-4 text-blue-800">Enhanced Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h4 className="font-semibold text-blue-800 mb-2">Advanced Preprocessing</h4>
            <p className="text-sm text-blue-700">HTML removal, URL detection, character normalization, and more</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h4 className="font-semibold text-blue-800 mb-2">Confidence Calibration</h4>
            <p className="text-sm text-blue-700">Improved confidence scores with multi-factor analysis</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h4 className="font-semibold text-blue-800 mb-2">Multiple Models</h4>
            <p className="text-sm text-blue-700">Compares Naive Bayes, Logistic Regression, SVM, and Random Forest</p>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="mt-8 bg-gray-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">How to Use</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
          <div>
            <h4 className="font-semibold mb-2">📝 Input</h4>
            <ul className="space-y-1">
              <li>• Type or paste your message in the text area</li>
              <li>• Use Ctrl+Enter for quick analysis</li>
              <li>• Character counter helps track length</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">📊 Results</h4>
            <ul className="space-y-1">
              <li>• Clear spam/ham classification</li>
              <li>• Confidence levels: High/Medium/Low</li>
              <li>• Detailed metrics and indicators</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpamDetectorImproved;
