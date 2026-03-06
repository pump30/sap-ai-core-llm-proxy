import React, { useState, useEffect } from 'react';
import { ChatContainer } from './components/ChatContainer';
import { MessageInput } from './components/MessageInput';
import { ModelSelector } from './components/ModelSelector';
import { Settings, loadSettings, saveSettings } from './components/Settings';
import { Overview } from './components/Overview';
import { ImageGenerator } from './components/ImageGenerator';
import { useChat } from './hooks/useChat';
import { api } from './services/api';

// Check if running in desktop app (PyWebView)
const isDesktopApp = typeof window.pywebview !== 'undefined';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [selectedModel, setSelectedModel] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settings, setSettings] = useState(loadSettings);
  const [serverStatus, setServerStatus] = useState(null);

  const { messages, isLoading, error, sendMessage, clearMessages, setError } = useChat();

  // Get server status if in desktop app
  useEffect(() => {
    if (isDesktopApp && window.pywebview.api) {
      window.pywebview.api.get_server_status().then(status => {
        setServerStatus(status);
      }).catch(err => {
        console.error('Failed to get server status:', err);
      });
    }
  }, []);

  // Open log window (only available in desktop app)
  const openLogWindow = async () => {
    if (isDesktopApp && window.pywebview.api) {
      try {
        await window.pywebview.api.open_log_window();
      } catch (err) {
        console.error('Failed to open log window:', err);
      }
    }
  };

  // Initialize API key from settings
  useEffect(() => {
    api.setApiKey(settings.apiKey);
  }, [settings.apiKey]);

  const handleSend = (content) => {
    if (!selectedModel) {
      setError('Please select a model first');
      return;
    }
    sendMessage(content, selectedModel, {
      temperature: settings.temperature,
      max_tokens: settings.maxTokens
    });
  };

  const handleSettingsSave = (newSettings) => {
    setSettings(newSettings);
    api.setApiKey(newSettings.apiKey);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1>SAP AI Core LLM Proxy</h1>
          <div className="tab-nav">
            <button
              className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              Chat
            </button>
            <button
              className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button
              className={`tab-btn ${activeTab === 'images' ? 'active' : ''}`}
              onClick={() => setActiveTab('images')}
            >
              Images
            </button>
          </div>
        </div>
        <div className="header-controls">
          {activeTab === 'chat' && (
            <>
              <ModelSelector
                value={selectedModel}
                onChange={setSelectedModel}
                onError={setError}
              />
              <button className="clear-btn" onClick={clearMessages} disabled={messages.length === 0}>
                Clear Chat
              </button>
            </>
          )}
          {isDesktopApp && (
            <button className="logs-btn" onClick={openLogWindow} title="Open Server Logs">
              📋 Logs
            </button>
          )}
          <button className="settings-btn" onClick={() => setSettingsOpen(true)}>
            Settings
          </button>
        </div>
      </header>

      {error && activeTab === 'chat' && (
        <div className="error-message">
          {error}
          <button
            style={{ marginLeft: '12px', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
            onClick={() => setError(null)}
          >
            Dismiss
          </button>
        </div>
      )}

      {activeTab === 'chat' && (
        <>
          <ChatContainer messages={messages} isLoading={isLoading} />
          <MessageInput onSend={handleSend} disabled={isLoading} />
        </>
      )}
      
      {activeTab === 'overview' && <Overview />}
      
      {activeTab === 'images' && <ImageGenerator />}

      <Settings
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onSave={handleSettingsSave}
      />
    </div>
  );
}

export default App;
