import React, { useState, useEffect } from 'react';
import { Play, Download, Trash2, Server, AlertCircle, CheckCircle, Settings, Cpu } from 'lucide-react';

const OllamaManager = () => {
  const [health, setHealth] = useState(null);
  const [availableModels, setAvailableModels] = useState([]);
  const [installedModels, setInstalledModels] = useState([]);
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [installing, setInstalling] = useState({});
  const [removing, setRemoving] = useState({});
  const [activeTab, setActiveTab] = useState('available');
  const [error, setError] = useState(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) return;

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Load health status
      const healthRes = await fetch(`${BACKEND_URL}/api/v1/ollama/health`, { headers });
      if (healthRes.ok) {
        setHealth(await healthRes.json());
      }

      // Load available models
      const availableRes = await fetch(`${BACKEND_URL}/api/v1/ollama/models/available`, { headers });
      if (availableRes.ok) {
        setAvailableModels(await availableRes.json());
      }

      // Load installed models
      const installedRes = await fetch(`${BACKEND_URL}/api/v1/ollama/models/installed`, { headers });
      if (installedRes.ok) {
        setInstalledModels(await installedRes.json());
      }

      // Load system info
      const systemRes = await fetch(`${BACKEND_URL}/api/v1/ollama/system/info`, { headers });
      if (systemRes.ok) {
        setSystemInfo(await systemRes.json());
      }

    } catch (error) {
      console.error('Failed to load Ollama data:', error);
      setError('Failed to load Ollama data');
    } finally {
      setLoading(false);
    }
  };

  const installModel = async (modelName) => {
    try {
      setInstalling(prev => ({ ...prev, [modelName]: true }));
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/v1/ollama/models/install`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ model_name: modelName })
      });

      const result = await response.json();

      if (response.ok) {
        // Refresh the model lists
        await loadData();
        setError(null);
      } else {
        setError(result.detail || 'Failed to install model');
      }
    } catch (error) {
      console.error('Model installation failed:', error);
      setError('Model installation failed');
    } finally {
      setInstalling(prev => ({ ...prev, [modelName]: false }));
    }
  };

  const removeModel = async (modelName) => {
    if (!window.confirm(`Are you sure you want to remove ${modelName}?`)) {
      return;
    }

    try {
      setRemoving(prev => ({ ...prev, [modelName]: true }));
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/v1/ollama/models/${encodeURIComponent(modelName)}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const result = await response.json();

      if (response.ok) {
        // Refresh the model lists
        await loadData();
        setError(null);
      } else {
        setError(result.detail || 'Failed to remove model');
      }
    } catch (error) {
      console.error('Model removal failed:', error);
      setError('Model removal failed');
    } finally {
      setRemoving(prev => ({ ...prev, [modelName]: false }));
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      healthy: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      unhealthy: { color: 'bg-red-100 text-red-800', icon: AlertCircle },
      error: { color: 'bg-red-100 text-red-800', icon: AlertCircle },
      unavailable: { color: 'bg-gray-100 text-gray-800', icon: Server }
    };

    const config = statusConfig[status] || statusConfig.unavailable;
    const IconComponent = config.icon;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        <IconComponent size={12} className="mr-1" />
        {status}
      </span>
    );
  };

  const formatSize = (sizeGb) => {
    if (sizeGb < 1) {
      return `${(sizeGb * 1024).toFixed(0)} MB`;
    }
    return `${sizeGb.toFixed(1)} GB`;
  };

  const ModelCard = ({ model, isInstalled }) => (
    <div className="bg-white border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h4 className="font-medium text-gray-900">{model.name}</h4>
          <p className="text-sm text-gray-600 mt-1">{model.description}</p>
        </div>
        {model.recommended && (
          <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
            Recommended
          </span>
        )}
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {model.capabilities.map(capability => (
          <span
            key={capability}
            className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
          >
            {capability.replace('_', ' ')}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-500">
          {model.size_gb && formatSize(model.size_gb)}
        </div>
        
        {isInstalled ? (
          <button
            onClick={() => removeModel(model.name)}
            disabled={removing[model.name]}
            className="inline-flex items-center px-3 py-1 border border-red-200 text-sm font-medium rounded-md text-red-700 bg-red-50 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {removing[model.name] ? (
              <>
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-red-600 mr-2"></div>
                Removing...
              </>
            ) : (
              <>
                <Trash2 size={14} className="mr-1" />
                Remove
              </>
            )}
          </button>
        ) : (
          <button
            onClick={() => installModel(model.name)}
            disabled={installing[model.name] || health?.status !== 'healthy'}
            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {installing[model.name] ? (
              <>
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-2"></div>
                Installing...
              </>
            ) : (
              <>
                <Download size={14} className="mr-1" />
                Install
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Ollama Manager</h2>
          <p className="text-gray-600 mt-1">Manage local AI models with Ollama</p>
        </div>
        <button
          onClick={loadData}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <Settings size={16} className="mr-2" />
          Refresh
        </button>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center">
            <Server size={20} className="text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">Service Status</p>
              <div className="mt-1">
                {health ? getStatusBadge(health.status) : getStatusBadge('unknown')}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center">
            <Download size={20} className="text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">Installed Models</p>
              <p className="text-2xl font-bold text-gray-900">{installedModels.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center">
            <Cpu size={20} className="text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">System Resources</p>
              <p className="text-sm text-gray-600">
                {systemInfo ? `${systemInfo.memory_available_gb.toFixed(1)} GB RAM` : 'Loading...'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle size={20} className="text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="text-sm text-red-700 mt-2">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Service Unavailable Warning */}
      {health?.status !== 'healthy' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle size={20} className="text-yellow-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Ollama Service Unavailable</h3>
              <div className="text-sm text-yellow-700 mt-2">
                Ollama is not running locally. To use local models, please install and start Ollama on your system.
                <br />
                <a href="https://ollama.ai/" target="_blank" rel="noopener noreferrer" className="font-medium underline">
                  Download Ollama →
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Model Management Tabs */}
      <div>
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('available')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'available'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Available Models ({availableModels.length})
            </button>
            <button
              onClick={() => setActiveTab('installed')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'installed'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Installed Models ({installedModels.length})
            </button>
          </nav>
        </div>

        <div className="mt-6">
          {activeTab === 'available' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableModels.map(model => (
                <ModelCard key={model.name} model={model} isInstalled={false} />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {installedModels.length > 0 ? (
                installedModels.map(model => (
                  <ModelCard key={model.name} model={model} isInstalled={true} />
                ))
              ) : (
                <div className="col-span-full text-center py-8">
                  <Server size={48} className="mx-auto text-gray-400" />
                  <h3 className="mt-4 text-lg font-medium text-gray-900">No models installed</h3>
                  <p className="text-gray-600 mt-2">Install some models from the available tab to get started.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OllamaManager;