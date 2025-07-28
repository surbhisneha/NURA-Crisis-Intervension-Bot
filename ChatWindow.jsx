import React, { useState, useEffect } from "react";
import VoiceInput from "./VoiceInput";

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // ✅ Generate or retrieve a persistent user ID
  const getUserId = () => {
    let userId = localStorage.getItem("userId");
    if (!userId) {
      userId = "user-" + Math.random().toString(36).substring(2, 12);
      localStorage.setItem("userId", userId);
    }
    return userId;
  };

  // ✅ Fetch welcome message on page load
  useEffect(() => {
    const userId = getUserId();

    const fetchWelcome = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/welcome", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId }),
        });

        const data = await response.json();

        if (data.response) {
          setMessages([{ from: "bot", text: data.response }]);
        } else {
          setMessages([{ from: "bot", text: "Hi! How can I help you today?" }]);
        }
      } catch (error) {
        console.error("Error fetching welcome message:", error);
        setMessages([{ from: "bot", text: "Hi! How can I help you today?" }]);
      }
    };

    fetchWelcome();
  }, []);

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    setMessages((msgs) => [...msgs, { from: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const userId = getUserId();

      const response = await fetch("http://localhost:5000/api/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: text, user_id: userId }),
      });

      const data = await response.json();

      if (data.response) {
        setMessages((msgs) => [...msgs, { from: "bot", text: data.response }]);
      } else {
        setMessages((msgs) => [...msgs, { from: "bot", text: "Sorry, no response." }]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((msgs) => [...msgs, { from: "bot", text: "Error contacting server." }]);
    }

    setLoading(false);
  };

  const handleVoiceText = (text) => {
    sendMessage(text);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 20 }}>
      <div
        style={{
          border: "1px solid #ccc",
          padding: 10,
          minHeight: 300,
          marginBottom: 10,
          overflowY: "auto",
        }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              textAlign: msg.from === "bot" ? "left" : "right",
              marginBottom: 8,
            }}
          >
            <span
              style={{
                display: "inline-block",
                padding: "8px 12px",
                borderRadius: 15,
                backgroundColor: msg.from === "bot" ? "#eee" : "#007bff",
                color: msg.from === "bot" ? "#000" : "#fff",
              }}
            >
              {msg.text}
            </span>
          </div>
        ))}
        {loading && <div>Bot is typing...</div>}
      </div>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          style={{ flexGrow: 1, padding: 8, fontSize: 16 }}
        />
        <VoiceInput onText={handleVoiceText} />
        <button type="submit" style={{ padding: "8px 16px" }}>
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatWindow;
