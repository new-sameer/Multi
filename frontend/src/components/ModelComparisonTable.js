import React, { useState } from 'react';

const ModelComparisonTable = ({ models }) => {
  const [filterProvider, setFilterProvider] = useState('all');
  const [filterCapability, setFilterCapability] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  const providers = [...new Set(models.map(m => m.provider))];
  const capabilities = [...new Set(models.flatMap(m => m.capabilities || []))];

  const filteredModels = models.filter(model => {
    if (filterProvider !== 'all' && model.provider !== filterProvider) return false;
    if (filterCapability !== 'all' && !(model.capabilities || []).includes(filterCapability)) return false;
    return true;
  });

  const sortedModels = [...filteredModels].sort((a, b) => {
    let aVal, bVal;
    
    switch (sortBy) {
      case 'name':
        aVal = a.name;
        bVal = b.name;
        break;
      case 'provider':
        aVal = a.provider;
        bVal = b.provider;
        break;
      case 'context_length':
        aVal = a.context_length || 0;
        bVal = b.context_length || 0;
        break;
      case 'capabilities':
        aVal = (a.capabilities || []).length;
        bVal = (b.capabilities || []).length;
        break;
      default:
        aVal = a.name;
        bVal = b.name;
    }

    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
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

  const getCapabilityBadge = (capability) => {
    const colors = {
      general: 'bg-blue-100 text-blue-800',
      content_generation: 'bg-green-100 text-green-800',
      coaching: 'bg-purple-100 text-purple-800',
      reasoning: 'bg-orange-100 text-orange-800',
      web_search: 'bg-yellow-100 text-yellow-800'
    };
    
    return (
      <span key={capability} className={`px-2 py-1 text-xs font-medium rounded-full ${colors[capability] || 'bg-gray-100 text-gray-800'}`}>
        {capability.replace('_', ' ')}
      </span>
    );
  };

  const formatContextLength = (length) => {
    if (!length) return 'N/A';
    if (length >= 1000) {
      return `${(length / 1000).toFixed(0)}K`;
    }
    return length.toString();
  };

  return (
    <div className="bg-white shadow-sm rounded-lg overflow-hidden">
      {/* Filters and Controls */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Provider:</label>
            <select
              value={filterProvider}
              onChange={(e) => setFilterProvider(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Providers</option>
              {providers.map(provider => (
                <option key={provider} value={provider}>
                  {provider.charAt(0).toUpperCase() + provider.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Capability:</label>
            <select
              value={filterCapability}
              onChange={(e) => setFilterCapability(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Capabilities</option>
              {capabilities.map(capability => (
                <option key={capability} value={capability}>
                  {capability.replace('_', ' ').charAt(0).toUpperCase() + capability.replace('_', ' ').slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="ml-auto text-sm text-gray-500">
            {sortedModels.length} of {models.length} models
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('name')}
              >
                <div className="flex items-center space-x-1">
                  <span>Model</span>
                  <span className="text-gray-400">
                    {sortBy === 'name' ? (sortOrder === 'asc' ? '↑' : '↓') : '↕'}
                  </span>
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('provider')}
              >
                <div className="flex items-center space-x-1">
                  <span>Provider</span>
                  <span className="text-gray-400">
                    {sortBy === 'provider' ? (sortOrder === 'asc' ? '↑' : '↓') : '↕'}
                  </span>
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('context_length')}
              >
                <div className="flex items-center space-x-1">
                  <span>Context Length</span>
                  <span className="text-gray-400">
                    {sortBy === 'context_length' ? (sortOrder === 'asc' ? '↑' : '↓') : '↕'}
                  </span>
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('capabilities')}
              >
                <div className="flex items-center space-x-1">
                  <span>Capabilities</span>
                  <span className="text-gray-400">
                    {sortBy === 'capabilities' ? (sortOrder === 'asc' ? '↑' : '↓') : '↕'}
                  </span>
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Size
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedModels.map((model, index) => (
              <tr key={`${model.provider}-${model.name}`} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{model.name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className="text-lg mr-2">{getProviderIcon(model.provider)}</span>
                    <span className="text-sm text-gray-900 capitalize">{model.provider}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatContextLength(model.context_length)}
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-wrap gap-1">
                    {(model.capabilities || []).map(capability => getCapabilityBadge(capability))}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    model.available 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {model.available ? 'Available' : 'Unavailable'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {model.size_gb ? `${model.size_gb.toFixed(1)}GB` : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sortedModels.length === 0 && (
        <div className="px-6 py-12 text-center">
          <div className="text-gray-500">
            <span className="text-4xl mb-4 block">🔍</span>
            <p className="text-lg font-medium">No models found</p>
            <p className="text-sm">Try adjusting your filters</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelComparisonTable;