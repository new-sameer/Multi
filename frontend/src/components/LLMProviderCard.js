import React from 'react';

const LLMProviderCard = ({ name, status, onRefresh }) => {
  const getStatusColor = (statusStr) => {
    switch (statusStr) {
      case 'healthy':
        return 'bg-green-100 border-green-200 text-green-800';
      case 'unhealthy':
        return 'bg-red-100 border-red-200 text-red-800';
      case 'unavailable':
        return 'bg-gray-100 border-gray-200 text-gray-800';
      default:
        return 'bg-yellow-100 border-yellow-200 text-yellow-800';
    }
  };

  const getStatusIcon = (statusStr) => {
    switch (statusStr) {
      case 'healthy':
        return '✅';
      case 'unhealthy':
        return '❌';
      case 'unavailable':
        return '⚪';
      default:
        return '⚠️';
    }
  };

  const getProviderIcon = (providerName) => {
    const icons = {
      ollama: '🦙',
      groq: '⚡',
      openai: '🤖',
      claude: '🧠',
      perplexity: '🔍'
    };
    return icons[providerName] || '🔧';
  };

  const formatProviderName = (name) => {
    return name.charAt(0).toUpperCase() + name.slice(1);
  };

  return (
    <div className={`p-6 rounded-lg border-2 ${getStatusColor(status.status)} transition-all hover:shadow-md`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getProviderIcon(name)}</span>
          <div>
            <h3 className="text-lg font-semibold">{formatProviderName(name)}</h3>
            <p className="text-sm opacity-75">
              {name === 'ollama' && 'Local Models'}
              {name === 'groq' && 'Fast Inference'}
              {name === 'openai' && 'GPT Models'}
              {name === 'claude' && 'Anthropic AI'}
              {name === 'perplexity' && 'Web Search'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="text-xl">{getStatusIcon(status.status)}</span>
          <span className="text-sm font-medium">
            {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Status Details */}
      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="opacity-75">Connection:</span>
          <span className={`font-medium ${
            status.connection === 'active' ? 'text-green-700' : 
            status.connection === 'failed' ? 'text-red-700' : 'text-gray-700'
          }`}>
            {status.connection}
          </span>
        </div>
        
        {status.models_available !== undefined && (
          <div className="flex justify-between text-sm">
            <span className="opacity-75">Models Available:</span>
            <span className="font-medium">{status.models_available}</span>
          </div>
        )}
        
        {status.reason && (
          <div className="mt-2 p-2 rounded bg-white bg-opacity-50">
            <p className="text-xs opacity-75">{status.reason}</p>
          </div>
        )}
        
        {status.error && (
          <div className="mt-2 p-2 rounded bg-red-50 border border-red-200">
            <p className="text-xs text-red-700">Error: {status.error}</p>
          </div>
        )}
      </div>

      {/* Cost Information */}
      <div className="mt-4 pt-4 border-t border-white border-opacity-30">
        <div className="flex justify-between text-sm">
          <span className="opacity-75">Cost:</span>
          <span className="font-medium">
            {name === 'ollama' ? 'Free (Local)' : 'Pay per Token'}
          </span>
        </div>
        
        {name !== 'ollama' && (
          <div className="flex justify-between text-xs mt-1">
            <span className="opacity-60">Priority:</span>
            <span>{name === 'groq' ? 'Fallback' : 'Available'}</span>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      {status.status === 'unavailable' && status.reason && (
        <div className="mt-4 pt-4 border-t border-white border-opacity-30">
          <div className="text-xs opacity-75">
            {name === 'ollama' && '💡 Install Ollama locally for free models'}
            {name !== 'ollama' && '💡 Add API key in settings to enable'}
          </div>
        </div>
      )}
    </div>
  );
};

export default LLMProviderCard;