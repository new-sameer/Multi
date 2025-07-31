import React, { useState, useEffect } from 'react';
import { Save, Zap, Eye, EyeOff, ExternalLink, CheckCircle, AlertCircle, Loader } from 'lucide-react';

const ProviderConfiguration = () => {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [configuring, setConfiguring] = useState({});
  const [testing, setTesting] = useState({});
  const [testResults, setTestResults] = useState({});
  const [showKeys, setShowKeys] = useState({});
  const [apiKeys, setApiKeys] = useState({});
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(`${BACKEND_URL}/api/v1/providers/list`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProviders(data);
        setError(null);
      } else {
        setError('Failed to load providers');
      }
    } catch (error) {
      console.error('Failed to load providers:', error);
      setError('Failed to load providers');
    } finally {
      setLoading(false);
    }
  };

  const configureProvider = async (providerName) => {
    const apiKey = apiKeys[providerName];
    if (!apiKey || apiKey.trim().length < 10) {
      setError('Please enter a valid API key');
      return;
    }

    try {
      setConfiguring(prev => ({ ...prev, [providerName]: true }));
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/v1/providers/${providerName}/configure`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ api_key: apiKey, enabled: true })
      });

      const result = await response.json();

      if (response.ok) {
        setSuccessMessage(`${providerName} configured successfully`);
        setError(null);
        // Clear the API key field
        setApiKeys(prev => ({ ...prev, [providerName]: '' }));
        // Reload providers to get updated status
        setTimeout(loadProviders, 1000);
      } else {
        setError(result.detail || 'Configuration failed');
      }
    } catch (error) {
      console.error('Provider configuration failed:', error);
      setError('Configuration failed');
    } finally {
      setConfiguring(prev => ({ ...prev, [providerName]: false }));
    }
  };

  const testProvider = async (providerName) => {
    try {
      setTesting(prev => ({ ...prev, [providerName]: true }));
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/v1/providers/${providerName}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ test_prompt: "Hello, this is a test message." })
      });

      const result = await response.json();

      if (response.ok) {
        setTestResults(prev => ({ ...prev, [providerName]: result }));
        setError(null);
      } else {
        setError(result.detail || 'Test failed');
      }
    } catch (error) {
      console.error('Provider test failed:', error);
      setError('Provider test failed');
    } finally {
      setTesting(prev => ({ ...prev, [providerName]: false }));
    }
  };

  const getStatusBadge = (status, connection) => {
    if (status === 'healthy' && connection === 'active') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle size={12} className="mr-1" />
          Active
        </span>
      );
    } else if (status === 'unhealthy' || connection === 'failed') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <AlertCircle size={12} className="mr-1" />
          Inactive
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          <AlertCircle size={12} className="mr-1" />
          Unknown
        </span>
      );
    }
  };

  const getCostTypeBadge = (costType) => {
    const costConfig = {
      free: { color: 'bg-green-100 text-green-800', label: 'Free' },
      pay_per_token: { color: 'bg-blue-100 text-blue-800', label: 'Pay per Token' },
      subscription: { color: 'bg-purple-100 text-purple-800', label: 'Subscription' }
    };

    const config = costConfig[costType] || { color: 'bg-gray-100 text-gray-800', label: 'Unknown' };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const ProviderCard = ({ provider }) => {
    const testResult = testResults[provider.provider];
    
    return (
      <div className="bg-white border rounded-lg p-6 shadow-sm">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 font-semibold text-sm">
                  {provider.display_name.charAt(0)}
                </span>
              </div>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-gray-900">{provider.display_name}</h3>
              <p className="text-sm text-gray-600">{provider.description}</p>
            </div>
          </div>
          <div className="flex space-x-2">
            {getStatusBadge(provider.status, provider.connection)}
            {getCostTypeBadge(provider.cost_type)}
          </div>
        </div>

        {provider.error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{provider.error}</p>
          </div>
        )}

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Models Available:</span>
              <span className="ml-1 font-medium">{provider.models_available}</span>
            </div>
            <div>
              <span className="text-gray-500">Status:</span>
              <span className="ml-1 font-medium capitalize">{provider.connection}</span>
            </div>
          </div>

          {provider.requires_api_key && !provider.configured && (
            <div className="space-y-3">
              <div className="relative">
                <input
                  type={showKeys[provider.provider] ? "text" : "password"}
                  placeholder={`Enter ${provider.display_name} API Key`}
                  value={apiKeys[provider.provider] || ''}
                  onChange={(e) => setApiKeys(prev => ({ ...prev, [provider.provider]: e.target.value }))}
                  className="block w-full pr-10 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
                <button
                  type="button"
                  onClick={() => setShowKeys(prev => ({ ...prev, [provider.provider]: !prev[provider.provider] }))}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showKeys[provider.provider] ? (
                    <EyeOff size={16} className="text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye size={16} className="text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => configureProvider(provider.provider)}
                  disabled={configuring[provider.provider] || !apiKeys[provider.provider]}
                  className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                >
                  {configuring[provider.provider] ? (
                    <>
                      <Loader size={16} className="animate-spin mr-2" />
                      Configuring...
                    </>
                  ) : (
                    <>
                      <Save size={16} className="mr-2" />
                      Save API Key
                    </>
                  )}
                </button>
                
                <a
                  href={provider.setup_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  <ExternalLink size={16} />
                </a>
              </div>
            </div>
          )}

          {(provider.configured || provider.provider === 'ollama') && (
            <div className="space-y-3">
              <button
                onClick={() => testProvider(provider.provider)}
                disabled={testing[provider.provider]}
                className="w-full inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {testing[provider.provider] ? (
                  <>
                    <Loader size={16} className="animate-spin mr-2" />
                    Testing...
                  </>
                ) : (
                  <>
                    <Test size={16} className="mr-2" />
                    Test Connection
                  </>
                )}
              </button>

              {testResult && (
                <div className={`p-3 rounded-md border ${testResult.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-sm font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'}`}>
                      {testResult.success ? 'Test Successful' : 'Test Failed'}
                    </span>
                    <span className="text-xs text-gray-600">
                      {testResult.response_time.toFixed(2)}s
                    </span>
                  </div>
                  {testResult.success ? (
                    <div className="text-xs text-green-700 space-y-1">
                      <p>Model: {testResult.model_used}</p>
                      <p>Tokens: {testResult.tokens_used}</p>
                      {testResult.cost && <p>Cost: ${testResult.cost.toFixed(4)}</p>}
                    </div>
                  ) : (
                    <p className="text-xs text-red-700">{testResult.error}</p>
                  )}
                </div>
              )}
            </div>
          )}

          {provider.configured && provider.provider !== 'ollama' && (
            <div className="pt-3 border-t border-gray-200">
              <p className="text-xs text-green-600 font-medium">✓ API Key Configured</p>
              <p className="text-xs text-gray-500">Provider is ready to use</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Provider Configuration</h2>
          <p className="text-gray-600 mt-1">Configure API keys and settings for LLM providers</p>
        </div>
        <button
          onClick={loadProviders}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Refresh
        </button>
      </div>

      {/* Status Messages */}
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

      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <CheckCircle size={20} className="text-green-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">Success</h3>
              <div className="text-sm text-green-700 mt-2">{successMessage}</div>
            </div>
          </div>
        </div>
      )}

      {/* Provider Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {providers.map(provider => (
          <ProviderCard key={provider.provider} provider={provider} />
        ))}
      </div>
    </div>
  );
};

export default ProviderConfiguration;