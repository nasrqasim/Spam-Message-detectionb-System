import React from 'react';

const Header = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-2xl font-bold">Enhanced Spam Detector</h1>
              <p className="text-xs text-blue-100">Advanced AI-Powered Protection</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-semibold">v2.0</div>
            <div className="text-xs text-blue-100">Improved Accuracy</div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
