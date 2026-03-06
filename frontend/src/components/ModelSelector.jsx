import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

export function ModelSelector({ value, onChange, onError }) {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await api.getModels();
      const modelList = response.data || [];
      setModels(modelList);

      // Auto-select first model if none selected
      if (!value && modelList.length > 0) {
        onChange(modelList[0].id);
      }
    } catch (err) {
      onError?.(`Failed to load models: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="model-selector">
      <label htmlFor="model-select">Model:</label>
      <select
        id="model-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={loading}
      >
        {loading ? (
          <option>Loading models...</option>
        ) : models.length === 0 ? (
          <option>No models available</option>
        ) : (
          models.map((model) => (
            <option key={model.id} value={model.id}>
              {model.id}
            </option>
          ))
        )}
      </select>
    </div>
  );
}
