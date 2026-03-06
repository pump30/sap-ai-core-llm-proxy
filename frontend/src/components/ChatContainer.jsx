import React, { useEffect, useRef } from 'react';
import { Message } from './Message';

export function ChatContainer({ messages, isLoading }) {
  const containerRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="chat-container">
        <div className="empty-state">
          <h2>SAP AI Core LLM Proxy</h2>
          <p>Select a model and start chatting. Your messages will be processed through the SAP AI Core proxy.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container" ref={containerRef}>
      {messages.map((msg, index) => (
        <Message key={index} role={msg.role} content={msg.content} />
      ))}
      {isLoading && messages[messages.length - 1]?.content === '' && (
        <div className="message assistant">
          <span className="message-role">assistant</span>
          <div className="message-content">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
