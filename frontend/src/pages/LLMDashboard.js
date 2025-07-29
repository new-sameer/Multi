import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import toast from 'react-hot-toast';

const LLMDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [models, setModels] = useState([]);
  const [health, setHealth] = useState({});
  const [stats, setStats] = useState(null);
  const [generating, setGenerating] = useState(false);
  
  // Content generation form state
  const [prompt, setPrompt] = useState('');
  const [taskType, setTaskType] = useState('general');
  const [provider, setProvider] = useState('');
  const [maxTokens, setMaxTokens] = useState(1000);
  const [temperature, setTemperature] = useState(0.7);
  const [generatedContent, setGeneratedContent] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load all dashboard data in parallel
      const [modelsResponse, healthResponse, statsResponse] = await Promise.all([
        api.get('/llm/models'),
        api.get('/llm/health'),
        api.get('/llm/usage-statistics?days=30')
      ]);

      setModels(modelsResponse.data);
      setHealth(healthResponse.data);
      setStats(statsResponse.data);
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load LLM dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    try {
      setGenerating(true);
      
      const response = await api.post('/llm/generate', {
        prompt: prompt.trim(),
        task_type: taskType,
        preferred_provider: provider || undefined,
        max_tokens: maxTokens,
        temperature: temperature
      });

      setGeneratedContent(response.data);
      toast.success('Content generated successfully!');
      
      // Refresh usage stats
      const statsResponse = await api.get('/llm/usage-statistics?days=30');
      setStats(statsResponse.data);
      
    } catch (error) {
      console.error('Content generation failed:', error);
      toast.error('Content generation failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setGenerating(false);
    }
  };

  const getProviderStatusIcon = (providerName) => {
    const providerHealth = health.providers?.[providerName];
    if (!providerHealth) return '❓';
    return providerHealth.status === 'healthy' ? '✅' : '❌';
  };

  const formatCost = (cost) => {
    if (cost === 0) return 'Free';
    return `$${cost.toFixed(6)}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading LLM Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">LLM Management Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Manage your AI language models and generate content with Ollama and Groq
          </p>
        </div>

        {/* Health Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Overall Health */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                {health.overall_status === 'healthy' ? '🟢' : '🔴'}
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">System Status</h3>
                <p className="text-sm text-gray-600 capitalize">{health.overall_status || 'Unknown'}</p>
              </div>
            </div>
          </div>

          {/* Ollama Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                {getProviderStatusIcon('ollama')}
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">Ollama (Local)</h3>
                <p className="text-sm text-gray-600">
                  {health.providers?.ollama?.status || 'Unknown'} • Free
                </p>
              </div>
            </div>
          </div>

          {/* Groq Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                {getProviderStatusIcon('groq')}
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">Groq (Cloud)</h3>
                <p className="text-sm text-gray-600">
                  {health.providers?.groq?.status || 'Unknown'} • Paid
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Content Generation Form */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate Content</h2>
              
              <form onSubmit={handleGenerate} className="space-y-4">
                {/* Prompt */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prompt
                  </label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={4}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your prompt here..."
                  />
                </div>

                {/* Settings Row */}
                <div className="grid grid-cols-2 gap-4">
                  {/* Task Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Task Type
                    </label>
                    <select
                      value={taskType}
                      onChange={(e) => setTaskType(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="general">General</option>
                      <option value="content_generation">Content Generation</option>
                      <option value="success_coaching">Success Coaching</option>
                      <option value="content_adaptation">Content Adaptation</option>
                    </select>
                  </div>

                  {/* Preferred Provider */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Provider (Optional)
                    </label>
                    <select
                      value={provider}
                      onChange={(e) => setProvider(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Auto-select best</option>
                      <option value="ollama">Ollama (Free)</option>
                      <option value="groq">Groq (Fast)</option>
                    </select>
                  </div>
                </div>

                {/* Advanced Settings Row */}
                <div className="grid grid-cols-2 gap-4">
                  {/* Max Tokens */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Tokens: {maxTokens}
                    </label>
                    <input
                      type="range"
                      min="50"
                      max="4000"
                      step="50"
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>

                  {/* Temperature */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Temperature: {temperature}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      value={temperature}
                      onChange={(e) => setTemperature(parseFloat(e.target.value))}
                      className="w-full"
                    />
                  </div>
                </div>

                {/* Generate Button */}
                <button
                  type="submit"
                  disabled={generating}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {generating ? 'Generating...' : 'Generate Content'}
                </button>
              </form>

              {/* Generated Content */}
              {generatedContent && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">Generated Content</h3>
                  <div className="text-sm text-gray-600 mb-2">
                    Provider: {generatedContent.provider} • Model: {generatedContent.model} • 
                    Tokens: {generatedContent.tokens_used} • Cost: {formatCost(generatedContent.cost)} • 
                    Time: {generatedContent.response_time.toFixed(2)}s
                  </div>
                  <div className="bg-white p-3 rounded border">
                    <pre className="whitespace-pre-wrap text-sm">{generatedContent.content}</pre>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Models and Statistics */}
          <div className="space-y-6">
            {/* Available Models */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Available Models</h2>
                <div className="space-y-3">
                  {models.map((model, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <h3 className="font-medium text-gray-900">{model.name}</h3>
                        <p className="text-sm text-gray-600 capitalize">
                          {model.provider} • {model.available ? 'Available' : 'Unavailable'}
                          {model.context_length && ` • ${model.context_length.toLocaleString()} tokens`}
                        </p>
                        {model.capabilities && model.capabilities.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {model.capabilities.map((cap, i) => (
                              <span key={i} className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                {cap.replace('_', ' ')}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="text-2xl">
                        {model.available ? '✅' : '❌'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Usage Statistics */}
            {stats && (
              <div className="bg-white rounded-lg shadow">
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    Usage Statistics ({stats.period_days} days)
                  </h2>
                  {stats.providers && stats.providers.length > 0 ? (
                    <div className="space-y-4">
                      {stats.providers.map((provider, index) => (
                        <div key={index} className="p-4 bg-gray-50 rounded-lg">
                          <h3 className="font-medium text-gray-900 capitalize mb-2">
                            {provider._id}
                          </h3>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">Requests:</span>
                              <span className="ml-2 font-medium">{provider.total_requests}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">Tokens:</span>
                              <span className="ml-2 font-medium">{provider.total_tokens.toLocaleString()}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">Cost:</span>
                              <span className="ml-2 font-medium">{formatCost(provider.total_cost)}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">Avg Response:</span>
                              <span className="ml-2 font-medium">{provider.avg_response_time.toFixed(2)}s</span>
                            </div>
                          </div>
                          {provider.fallback_count > 0 && (
                            <div className="mt-2 text-sm text-orange-600">
                              ⚠️ {provider.fallback_count} fallback requests
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-600">No usage data available yet.</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMDashboard;