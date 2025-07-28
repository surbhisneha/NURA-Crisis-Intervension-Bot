import React from 'react';
import './MessageBubble.css';

const MessageBubble = ({ message }) => {
  const bubbleClass = message.sender === 'user' ? 'user' : 'bot';

  return (
    <div className={`message ${bubbleClass}`}>
      {message.text}
    </div>
  );
};

export default MessageBubble;
