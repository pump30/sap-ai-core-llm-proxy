import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export function Overview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await api.getOverview();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  if (loading) {
    return (
      <div className="overview-container">
        <div className="loading">Loading overview...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="overview-container">
        <div className="overview-error">
          <p>Failed to load overview: {error}</p>
          <button onClick={fetchOverview}>Retry</button>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="overview-container">
      <div className="overview-header">
        <h2>Proxy Overview</h2>
        <button className="refresh-btn" onClick={fetchOverview}>
          Refresh
        </button>
      </div>

      <div className="overview-cards">
        <div className="overview-card">
          <h3>Server Info</h3>
          <div className="card-content">
            <div className="info-row">
              <span className="label">Host:</span>
              <span className="value">{data.server.host}</span>
            </div>
            <div className="info-row">
              <span className="label">Port:</span>
              <span className="value">{data.server.port}</span>
            </div>
            <div className="info-row">
              <span className="label">Status:</span>
              <span className="value">
                <span className="status-indicator status-running"></span>
                {data.server.status}
              </span>
            </div>
          </div>
        </div>

        <div className="overview-card">
          <h3>Statistics</h3>
          <div className="card-content">
            <div className="info-row">
              <span className="label">Total Models:</span>
              <span className="value">{data.statistics.total_models}</span>
            </div>
            <div className="info-row">
              <span className="label">SubAccounts:</span>
              <span className="value">{data.statistics.total_subaccounts}</span>
            </div>
            <div className="info-row">
              <span className="label">Authentication:</span>
              <span className="value">
                {data.statistics.authentication_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="overview-section">
        <h3>SubAccounts</h3>
        {data.subaccounts.length === 0 ? (
          <p className="no-data">No subaccounts configured</p>
        ) : (
          <div className="overview-table-wrapper">
            <table className="overview-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Resource Group</th>
                  <th>Models</th>
                  <th>Token</th>
                </tr>
              </thead>
              <tbody>
                {data.subaccounts.map((account) => (
                  <tr key={account.name}>
                    <td>{account.name}</td>
                    <td>{account.resource_group}</td>
                    <td>{account.models_count}</td>
                    <td>
                      <span
                        className={`status-indicator ${
                          account.token_valid ? 'status-valid' : 'status-invalid'
                        }`}
                      ></span>
                      {account.token_valid ? 'Valid' : 'Invalid'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="overview-section">
        <h3>Available Models</h3>
        {data.models.length === 0 ? (
          <p className="no-data">No models available</p>
        ) : (
          <div className="overview-table-wrapper">
            <table className="overview-table">
              <thead>
                <tr>
                  <th>Model ID</th>
                  <th>SubAccounts</th>
                  <th>Deployments</th>
                </tr>
              </thead>
              <tbody>
                {data.models.map((model) => (
                  <tr key={model.id}>
                    <td className="model-id">{model.id}</td>
                    <td>{model.subaccounts.join(', ')}</td>
                    <td>{model.deployment_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
