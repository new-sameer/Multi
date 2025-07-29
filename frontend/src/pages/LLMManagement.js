import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import LLMProviderCard from '../components/LLMProviderCard';
import ModelComparisonTable from '../components/ModelComparisonTable';
import UsageStatistics from '../components/UsageStatistics';
import LLMTestConsole from '../components/LLMTestConsole';

const LLMManagement = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('providers');
  const [providerHealth, setProviderHealth] = useState({});
  const [availableModels, setAvailableModels] = useState([]);
  const [usageStats, setUsageStats] = useState({});
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadLLMData();
  }, []);

  const loadLLMData = async () => {
    try {
      setLoading(true);
      
      // Load provider health status
      const healthResponse = await api.get('/api/v1/llm/providers/status');
      setProviderHealth(healthResponse.data);
      
      // Load available models
      const modelsResponse = await api.get('/api/v1/llm/models');
      setAvailableModels(modelsResponse.data);
      
      // Load usage statistics
      const statsResponse = await api.get('/api/v1/llm/usage-statistics?days=30');
      setUsageStats(statsResponse.data);
      
    } catch (error) {
      console.error('Error loading LLM data:', error);
      toast.error('Failed to load LLM data');
    } finally {
      setLoading(false);
    }
  };

  const refreshHealth = async () => {
    try {
      setRefreshing(true);
      const response = await api.get('/api/v1/llm/providers/status');
      setProviderHealth(response.data);
      toast.success('Provider health refreshed');
    } catch (error) {
      toast.error('Failed to refresh provider health');
    } finally {
      setRefreshing(false);
    }
  };

  const tabs = [
    { id: 'providers', name: 'Providers', icon: '🔧' },
    { id: 'models', name: 'Models', icon: '🤖' },
    { id: 'usage', name: 'Usage Stats', icon: '📊' },
    { id: 'console', name: 'Test Console', icon: '🧪' }
  ];

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">LLM Management</h1>
        <p className="mt-2 text-gray-600">
          Manage your AI providers, models, and usage statistics
        </p>
        
        {/* Overall Status */}
        <div className="mt-4 p-4 rounded-lg border-2 border-dashed border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                providerHealth?.providers && Object.values(providerHealth.providers)
                  .some(p => p.status === 'healthy') 
                  ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-sm font-medium text-gray-700">
                System Status: {
                  providerHealth?.providers && Object.values(providerHealth.providers)
                    .some(p => p.status === 'healthy') 
                    ? 'Healthy' : 'Degraded'
                }
              </span>
            </div>
            
            <button
              onClick={refreshHealth}
              disabled={refreshing}
              className="flex items-center px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
            >
              <span className={`mr-1 ${refreshing ? 'animate-spin' : ''}`}>🔄</span>
              Refresh
            </button>
          </div>
          
          {providerHealth?.recommendation && (
            <p className="mt-2 text-sm text-gray-600">
              💡 {providerHealth.recommendation}
            </p>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'providers' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Provider Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {providerHealth?.providers && Object.entries(providerHealth.providers).map(([name, status]) => (
                <LLMProviderCard 
                  key={name}
                  name={name}
                  status={status}
                  onRefresh={refreshHealth}
                />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'models' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Available Models</h2>
            <ModelComparisonTable models={availableModels} />
          </div>
        )}

        {activeTab === 'usage' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Usage Statistics</h2>
            <UsageStatistics data={usageStats} />
          </div>
        )}

        {activeTab === 'console' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Test Console</h2>
            <LLMTestConsole availableModels={availableModels} />
          </div>
        )}
      </div>
    </div>
  );
};

export default LLMManagement;