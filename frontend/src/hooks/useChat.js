import { useState, useCallback, useRef } from 'react';
import { api } from '../services/api';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const sendMessage = useCallback(async (content, model, options = {}) => {
    if (!content.trim() || !model) return;

    setError(null);

    const userMessage = { role: 'user', content: content.trim() };
    const newMessages = [...messages, userMessage];

    setMessages(newMessages);
    setIsLoading(true);

    try {
      // Create assistant message placeholder
      const assistantMessage = { role: 'assistant', content: '' };
      setMessages([...newMessages, assistantMessage]);

      // Stream the response
      let fullContent = '';
      for await (const chunk of api.streamChat(newMessages, model, options)) {
        fullContent += chunk;
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: 'assistant', content: fullContent };
          return updated;
        });
      }

      // If no content was received, show an error
      if (!fullContent) {
        throw new Error('No response received from the model');
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
        // Remove the empty assistant message on error
        setMessages(newMessages);
      }
    } finally {
      setIsLoading(false);
    }
  }, [messages]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    stopGeneration,
    setError
  };
}
