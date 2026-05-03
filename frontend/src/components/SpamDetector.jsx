import React, { useState } from 'react';
import axios from 'axios';

const SpamDetector = () => {
  const [message, setMessage] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [charCount, setCharCount] = useState(0);

  // Example messages for testing
  const exampleMessages = [
    {
      text: "Congratulations! You've won a $1000 Walmart gift card. Click here to claim now!",
      type: "spam"
    },
    {
      text: "Hey, are we still meeting for lunch tomorrow at 12pm?",
      type: "ham"
    },
    {
      text: "URGENT: Your account has been suspended. Please verify your information immediately.",
      type: "spam"
    },
    {
      text: "Can you send me the project files when you get a chance? Thanks!",
      type: "ham"
    }
  ];

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

  return (
    <div className="max-w-4xl mx-auto">
      {/* Main Content Card */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            Check Your Message
          </h2>
          <p className="text-gray-600">
            Enter a message below to determine if it's spam or legitimate
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
                  Checking...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Check Message
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

        {/* Result Display */}
        {result && (
          <div className="mt-8">
            <h3 className="text-xl font-semibold mb-4">Result</h3>
            <div className={`result-${result.prediction.toLowerCase().replace(' ', '-')}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  {result.prediction === 'Spam' ? (
                    <svg className="w-6 h-6 mr-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="w-6 h-6 mr-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  )}
                  <div>
                    <div className="font-bold text-lg">
                      {result.prediction}
                    </div>
                    <div className="text-sm opacity-75">
                      Confidence: {(result.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Example Messages Section */}
      <div className="mt-8 bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-xl font-semibold mb-4">Example Messages</h3>
        <p className="text-gray-600 mb-4">
          Click on any example below to test it:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {exampleMessages.map((example, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 cursor-pointer transition-colors"
              onClick={() => handleExampleClick(example.text)}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`text-xs font-semibold px-2 py-1 rounded ${
                  example.type === 'spam' 
                    ? 'bg-red-100 text-red-700' 
                    : 'bg-green-100 text-green-700'
                }`}>
                  {example.type.toUpperCase()}
                </span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
              <p className="text-sm text-gray-700 line-clamp-3">
                {example.text}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Instructions */}
      <div className="mt-8 bg-blue-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-blue-800 mb-2">How to Use</h3>
        <ul className="text-blue-700 space-y-1 text-sm">
          <li>• Type or paste your message in the text area above</li>
          <li>• Click "Check Message" or press Ctrl+Enter to analyze</li>
          <li>• View the result with confidence score</li>
          <li>• Try the example messages to test different scenarios</li>
        </ul>
      </div>
    </div>
  );
};

export default SpamDetector;
