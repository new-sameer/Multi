import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const UsageStatistics = ({ data }) => {
  if (!data || !data.providers || data.providers.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-8 text-center">
        <div className="text-gray-500">
          <span className="text-4xl mb-4 block">📊</span>
          <p className="text-lg font-medium">No usage data available</p>
          <p className="text-sm">Start generating content to see your usage statistics</p>
        </div>
      </div>
    );
  }

  const providers = data.providers || [];
  const totalTokens = providers.reduce((sum, p) => sum + (p.total_tokens || 0), 0);
  const totalCost = providers.reduce((sum, p) => sum + (p.total_cost || 0), 0);
  const totalRequests = providers.reduce((sum, p) => sum + (p.total_requests || 0), 0);
  const totalFallbacks = providers.reduce((sum, p) => sum + (p.fallback_count || 0), 0);

  // Prepare data for charts
  const barChartData = providers.map(provider => ({
    name: provider._id.charAt(0).toUpperCase() + provider._id.slice(1),
    tokens: provider.total_tokens || 0,
    requests: provider.total_requests || 0,
    cost: provider.total_cost || 0,
    avgResponseTime: provider.avg_response_time || 0
  }));

  const pieChartData = providers.map(provider => ({
    name: provider._id.charAt(0).toUpperCase() + provider._id.slice(1),
    value: provider.total_requests || 0
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const getProviderIcon = (provider) => {
    const icons = {
      ollama: '🦙',
      groq: '⚡',
      openai: '🤖',
      claude: '🧠',
      perplexity: '🔍'
    };
    return icons[provider.toLowerCase()] || '🔧';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 4
    }).format(amount);
  };

  const formatNumber = (number) => {
    if (number >= 1000000) {
      return `${(number / 1000000).toFixed(1)}M`;
    } else if (number >= 1000) {
      return `${(number / 1000).toFixed(1)}K`;
    }
    return number.toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100">
              <span className="text-2xl">🔤</span>
            </div>
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{formatNumber(totalTokens)}</p>
              <p className="text-sm text-gray-600">Total Tokens</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100">
              <span className="text-2xl">📝</span>
            </div>
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{formatNumber(totalRequests)}</p>
              <p className="text-sm text-gray-600">Total Requests</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-yellow-100">
              <span className="text-2xl">💰</span>
            </div>
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{formatCurrency(totalCost)}</p>
              <p className="text-sm text-gray-600">Total Cost</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-red-100">
              <span className="text-2xl">🔄</span>
            </div>
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{totalFallbacks}</p>
              <p className="text-sm text-gray-600">Fallbacks</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Token Usage by Provider */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Token Usage by Provider</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barChartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value, name) => [formatNumber(value), name]} />
              <Bar dataKey="tokens" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Request Distribution */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Request Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Provider Stats */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Provider Details</h3>
          <p className="text-sm text-gray-600">Last {data.period_days} days</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Provider
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Requests
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tokens
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Response Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cost
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fallbacks
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {providers.map((provider, index) => (
                <tr key={provider._id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-lg mr-2">{getProviderIcon(provider._id)}</span>
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {provider._id}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatNumber(provider.total_requests || 0)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatNumber(provider.total_tokens || 0)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {provider.avg_response_time ? `${provider.avg_response_time.toFixed(2)}s` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrency(provider.total_cost || 0)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      (provider.fallback_count || 0) === 0 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {provider.fallback_count || 0}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default UsageStatistics;