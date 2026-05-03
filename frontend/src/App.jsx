import React, { useState } from 'react';
import axios from 'axios';
import SpamDetectorImproved from './components/SpamDetectorImproved';
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8">
        <SpamDetectorImproved />
      </main>
      <Footer />
    </div>
  );
}

export default App;
