import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export function Overview() {
  const [data, setData] = useState(null);
  const [tokenUsage, setTokenUsage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const [overviewResult, tokenResult] = await Promise.all([
        api.getOverview(),
        api.getTokenUsage()
      ]);
      setData(overviewResult);
      setTokenUsage(tokenResult);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(2) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
  };

  const formatCost = (cost) => {
    if (cost >= 1) {
      return '$' + cost.toFixed(2);
    } else if (cost >= 0.01) {
      return '$' + cost.toFixed(3);
    } else if (cost > 0) {
      return '$' + cost.toFixed(4);
    }
    return '$0.00';
  };

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

        {/* Token Usage Card */}
        {tokenUsage && (
          <div className="overview-card token-usage-card">
            <h3>Token Usage</h3>
            <div className="card-content">
              <div className="info-row">
                <span className="label">Total Requests:</span>
                <span className="value">{formatNumber(tokenUsage.total_requests)}</span>
              </div>
              <div className="info-row">
                <span className="label">Prompt Tokens:</span>
                <span className="value">{formatNumber(tokenUsage.total_prompt_tokens)}</span>
              </div>
              <div className="info-row">
                <span className="label">Completion Tokens:</span>
                <span className="value">{formatNumber(tokenUsage.total_completion_tokens)}</span>
              </div>
              <div className="info-row">
                <span className="label">Total Tokens:</span>
                <span className="value">{formatNumber(tokenUsage.total_tokens)}</span>
              </div>
              <div className="info-row total-cost-row">
                <span className="label">💰 Total Cost:</span>
                <span className="value cost-value">{formatCost(tokenUsage.total_cost)}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Token Usage by Model */}
      {tokenUsage && Object.keys(tokenUsage.by_model).length > 0 && (
        <div className="overview-section">
          <h3>Token Usage by Model</h3>
          <div className="overview-table-wrapper">
            <table className="overview-table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>Requests</th>
                  <th>Prompt</th>
                  <th>Completion</th>
                  <th>Total</th>
                  <th>Cost</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(tokenUsage.by_model)
                  .sort((a, b) => b[1].cost - a[1].cost)
                  .map(([model, stats]) => (
                    <tr key={model}>
                      <td className="model-id">{model}</td>
                      <td>{formatNumber(stats.requests)}</td>
                      <td>{formatNumber(stats.prompt_tokens)}</td>
                      <td>{formatNumber(stats.completion_tokens)}</td>
                      <td>{formatNumber(stats.total_tokens)}</td>
                      <td className="cost-cell">{formatCost(stats.cost)}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent Requests */}
      {tokenUsage && tokenUsage.recent_requests.length > 0 && (
        <div className="overview-section">
          <h3>Recent Requests</h3>
          <div className="overview-table-wrapper">
            <table className="overview-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Model</th>
                  <th>Prompt</th>
                  <th>Completion</th>
                  <th>Total</th>
                  <th>Duration</th>
                  <th>Cost</th>
                </tr>
              </thead>
              <tbody>
                {tokenUsage.recent_requests.map((req, index) => (
                  <tr key={index}>
                    <td className="timestamp">{req.timestamp.split(',')[1] || req.timestamp}</td>
                    <td className="model-id">{req.model}</td>
                    <td>{formatNumber(req.prompt_tokens)}</td>
                    <td>{formatNumber(req.completion_tokens)}</td>
                    <td>{formatNumber(req.total_tokens)}</td>
                    <td>{req.duration}</td>
                    <td className="cost-cell">{formatCost(req.cost)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

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