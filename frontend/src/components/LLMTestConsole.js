import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import api from '../utils/api';

const LLMTestConsole = ({ availableModels }) => {
  const [prompt, setPrompt] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('');
  const [taskType, setTaskType] = useState('general');
  const [maxTokens, setMaxTokens] = useState(500);
  const [temperature, setTemperature] = useState(0.7);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const providers = [...new Set(availableModels.map(m => m.provider))];
  const taskTypes = [
    { value: 'general', label: 'General' },
    { value: 'content_generation', label: 'Content Generation' },
    { value: 'success_coaching', label: 'Success Coaching' },
    { value: 'content_adaptation', label: 'Content Adaptation' }
  ];

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    setGenerating(true);
    const startTime = Date.now();

    try {
      const requestData = {
        prompt: prompt.trim(),
        task_type: taskType,
        max_tokens: maxTokens,
        temperature: temperature
      };

      if (selectedProvider) {
        requestData.preferred_provider = selectedProvider;
      }

      const response = await api.post('/api/v1/llm/generate', requestData);
      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;

      const testResult = {
        id: Date.now(),
        timestamp: new Date(),
        prompt: prompt.trim(),
        response: response.data,
        duration: duration,
        settings: {
          provider: selectedProvider || 'auto',
          task_type: taskType,
          max_tokens: maxTokens,
          temperature: temperature
        }
      };

      setResult(testResult);
      setHistory(prev => [testResult, ...prev.slice(0, 9)]); // Keep last 10 results
      toast.success(`Generated in ${duration.toFixed(2)}s using ${response.data.provider}`);

    } catch (error) {
      console.error('Generation failed:', error);
      toast.error(error.response?.data?.detail || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const clearHistory = () => {
    setHistory([]);
    setResult(null);
  };

  const loadFromHistory = (historyItem) => {
    setPrompt(historyItem.prompt);
    setSelectedProvider(historyItem.settings.provider === 'auto' ? '' : historyItem.settings.provider);
    setTaskType(historyItem.settings.task_type);
    setMaxTokens(historyItem.settings.max_tokens);
    setTemperature(historyItem.settings.temperature);
    setResult(historyItem);
  };

  const formatCost = (cost) => {
    if (cost === 0) return 'Free';
    return `$${cost.toFixed(6)}`;
  };

  const getProviderIcon = (provider) => {
    const icons = {
      ollama: '🦙',
      groq: '⚡',
      openai: '🤖',
      claude: '🧠',
      perplexity: '🔍'
    };
    return icons[provider] || '🔧';
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Prompt Input */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your prompt here..."
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Settings */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Generation Settings</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Provider (Optional)
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Auto Select</option>
                  {providers.map(provider => (
                    <option key={provider} value={provider}>
                      {getProviderIcon(provider)} {provider.charAt(0).toUpperCase() + provider.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Task Type
                </label>
                <select
                  value={taskType}
                  onChange={(e) => setTaskType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {taskTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Tokens: {maxTokens}
                </label>
                <input
                  type="range"
                  min={50}
                  max={2000}
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Temperature: {temperature}
                </label>
                <input
                  type="range"
                  min={0}
                  max={2}
                  step={0.1}
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={generating || !prompt.trim()}
              className={`mt-4 w-full px-4 py-2 rounded-md font-medium transition-colors ${
                generating || !prompt.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {generating ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating...
                </span>
              ) : (
                'Generate Content'
              )}
            </button>
          </div>
        </div>

        {/* History Panel */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">History</h3>
              {history.length > 0 && (
                <button
                  onClick={clearHistory}
                  className="text-sm text-red-600 hover:text-red-700"
                >
                  Clear All
                </button>
              )}
            </div>

            {history.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">
                No test history yet
              </p>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {history.map(item => (
                  <div
                    key={item.id}
                    className="p-3 border rounded-md cursor-pointer hover:bg-gray-50 transition-colors"
                    onClick={() => loadFromHistory(item)}
                  >
                    <div className="text-xs text-gray-500 mb-1">
                      {item.timestamp.toLocaleTimeString()}
                    </div>
                    <div className="text-sm text-gray-900 truncate">
                      {item.prompt}
                    </div>
                    <div className="flex justify-between text-xs text-gray-600 mt-1">
                      <span>{getProviderIcon(item.response.provider)} {item.response.provider}</span>
                      <span>{item.duration.toFixed(2)}s</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Result Panel */}
      {result && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Result</h3>
          
          {/* Metadata */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
            <div>
              <span className="text-xs text-gray-500">Provider</span>
              <div className="text-sm font-medium">
                {getProviderIcon(result.response.provider)} {result.response.provider}
              </div>
            </div>
            <div>
              <span className="text-xs text-gray-500">Model</span>
              <div className="text-sm font-medium">{result.response.model}</div>
            </div>
            <div>
              <span className="text-xs text-gray-500">Tokens</span>
              <div className="text-sm font-medium">{result.response.tokens_used}</div>
            </div>
            <div>
              <span className="text-xs text-gray-500">Time</span>
              <div className="text-sm font-medium">{result.response.response_time.toFixed(2)}s</div>
            </div>
            <div>
              <span className="text-xs text-gray-500">Cost</span>
              <div className="text-sm font-medium">{formatCost(result.response.cost)}</div>
            </div>
          </div>

          {/* Generated Content */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Generated Content
            </label>
            <div className="p-4 bg-gray-50 rounded-lg border-l-4 border-blue-500">
              <pre className="whitespace-pre-wrap text-sm text-gray-900">
                {result.response.content}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LLMTestConsole;