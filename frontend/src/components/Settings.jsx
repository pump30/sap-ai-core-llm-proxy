import React, { useState, useEffect } from 'react';

const STORAGE_KEY = 'sap-ai-proxy-settings';

const DEFAULT_SETTINGS = {
  apiKey: '',
  temperature: 0.7,
  maxTokens: 2048
};

export function loadSettings() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return { ...DEFAULT_SETTINGS, ...JSON.parse(stored) };
    }
  } catch (e) {
    // Ignore parse errors
  }
  return DEFAULT_SETTINGS;
}

export function saveSettings(settings) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
}

export function Settings({ isOpen, onClose, onSave }) {
  const [settings, setSettings] = useState(loadSettings);

  useEffect(() => {
    if (isOpen) {
      setSettings(loadSettings());
    }
  }, [isOpen]);

  const handleSave = () => {
    saveSettings(settings);
    onSave(settings);
    onClose();
  };

  const handleChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-panel" onClick={(e) => e.stopPropagation()}>
        <h2>Settings</h2>

        <div className="settings-group">
          <label htmlFor="apiKey">API Key</label>
          <input
            id="apiKey"
            type="password"
            value={settings.apiKey}
            onChange={(e) => handleChange('apiKey', e.target.value)}
            placeholder="Enter your API key (if required)"
          />
          <p className="hint">Optional. Required if the proxy has authentication enabled.</p>
        </div>

        <div className="settings-group">
          <label htmlFor="temperature">Temperature: {settings.temperature}</label>
          <input
            id="temperature"
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={settings.temperature}
            onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
          />
          <p className="hint">Controls randomness. Lower = more focused, higher = more creative.</p>
        </div>

        <div className="settings-group">
          <label htmlFor="maxTokens">Max Tokens</label>
          <input
            id="maxTokens"
            type="number"
            min="1"
            max="128000"
            value={settings.maxTokens}
            onChange={(e) => handleChange('maxTokens', parseInt(e.target.value) || 2048)}
          />
          <p className="hint">Maximum number of tokens in the response.</p>
        </div>

        <div className="settings-actions">
          <button className="cancel-btn" onClick={onClose}>Cancel</button>
          <button className="save-btn" onClick={handleSave}>Save</button>
        </div>
      </div>
    </div>
  );
}
