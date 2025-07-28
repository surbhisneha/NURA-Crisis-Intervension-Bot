import React from 'react';
import { Mic } from 'lucide-react';

const VoiceInput = ({ onText }) => {
  const handleVoice = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Sorry, your browser doesn't support Speech Recognition.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onText(transcript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      alert('Speech recognition error: ' + event.error);
    };
  };

  return (
    <button onClick={handleVoice} style={{
      background: 'transparent',
      border: 'none',
      cursor: 'pointer'
    }}>
      <Mic color="#333" size={24} />
    </button>
  );
};

export default VoiceInput;


