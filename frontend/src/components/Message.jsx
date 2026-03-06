import React from 'react';
import ReactMarkdown from 'react-markdown';

export function Message({ role, content }) {
  return (
    <div className={`message ${role}`}>
      <span className="message-role">{role}</span>
      <div className="message-content">
        {role === 'assistant' ? (
          <ReactMarkdown>{content}</ReactMarkdown>
        ) : (
          <p>{content}</p>
        )}
      </div>
    </div>
  );
}
