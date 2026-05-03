import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-6 mt-12">
      <div className="container mx-auto px-4">
        <div className="text-center">
          <p className="text-sm">
            © 2024 Spam Message Detector. Built with React, Python & Machine Learning.
          </p>
          <p className="text-xs mt-2 text-gray-400">
            Protecting your inbox with AI-powered spam detection.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
