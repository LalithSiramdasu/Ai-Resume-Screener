import { useState, useRef, useEffect } from "react";
import type { ChatMessage } from "../types";
import { askQuestion } from "../services/api";
import "./ChatInterface.css";

interface ChatInterfaceProps {
  sessionId: string;
}

export default function ChatInterface({ sessionId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([]);
    setInput("");
    setIsLoading(false);
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const question = input.trim();
    setInput("");

    // Add user message immediately
    const userMsg: ChatMessage = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);

    setIsLoading(true);
    try {
      const response = await askQuestion(sessionId, question);
      setMessages(response.chat_history);
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Sorry, I encountered an error. Please try again.";

      const errorMsg: ChatMessage = {
        role: "assistant",
        content: errorMessage,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>💬 Ask About Resume</h2>
        <span className="chat-subtitle">RAG-powered Q&A</span>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="empty-icon">🤖</div>
            <p>Ask me anything about this resume!</p>
            <div className="suggestion-chips">
              {[
                "What are the candidate's key skills?",
                "Does this candidate meet the JD requirements?",
                "What is their strongest qualification?",
              ].map((q, i) => (
                <button
                  key={i}
                  className="chip"
                  onClick={() => { setInput(q); }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === "user" ? "👤" : "🤖"}
            </div>
            <div className="message-bubble">
              <p>{msg.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-bubble typing">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the resume..."
          disabled={isLoading}
          className="chat-input"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="send-btn"
        >
          ➤
        </button>
      </div>
    </div>
  );
}
