import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setMessages([...messages, { text: input, sender: 'user' }]);
    setInput('');

    try {
      const response = await axios.post('http://localhost:5000/chat', {
        message: input,
        previous_messages: messages,
      });
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: response.data.reply, sender: 'ai' },
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: 'Error getting AI response.', sender: 'ai' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <p className='chat-header'>
        <strong>Gemini flash 1.5</strong>
      </p>
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.sender === 'user' ? 'user' : 'ai'}`}
          >
            {message.text}
          </div>
        ))}
        {loading && <div className="message ai">Thinking...</div>}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}

export default App;