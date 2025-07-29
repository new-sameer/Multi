import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import toast from 'react-hot-toast';

const AIContentGenerator = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    platform: 'instagram',
    content_type: 'text',
    topic: '',
    target_audience: '',
    tone: 'professional',
    hashtag_count: 5
  });
  const [generatedContent, setGeneratedContent] = useState(null);

  const platformOptions = [
    { value: 'instagram', label: 'Instagram', icon: '📷' },
    { value: 'tiktok', label: 'TikTok', icon: '🎵' },
    { value: 'linkedin', label: 'LinkedIn', icon: '💼' },
    { value: 'youtube', label: 'YouTube', icon: '📺' },
    { value: 'twitter', label: 'Twitter/X', icon: '🐦' },
    { value: 'facebook', label: 'Facebook', icon: '👥' }
  ];

  const contentTypeOptions = [
    { value: 'text', label: 'Text Post', icon: '📝' },
    { value: 'image', label: 'Image Post', icon: '🖼️' },
    { value: 'video', label: 'Video Post', icon: '🎥' },
    { value: 'carousel', label: 'Carousel', icon: '🎠' }
  ];

  const toneOptions = [
    { value: 'professional', label: 'Professional' },
    { value: 'casual', label: 'Casual' },
    { value: 'funny', label: 'Funny' },
    { value: 'inspiring', label: 'Inspiring' },
    { value: 'educational', label: 'Educational' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.topic.trim()) {
      toast.error('Please enter a topic');
      return;
    }

    try {
      setLoading(true);
      
      const response = await api.post('/content/generate', formData);
      
      setGeneratedContent(response.data);
      toast.success('Content generated successfully!');
      
    } catch (error) {
      console.error('Content generation failed:', error);
      toast.error('Content generation failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Content copied to clipboard!');
  };

  const saveContent = async () => {
    if (!generatedContent) return;
    
    try {
      // Content is already saved during generation, just show success
      toast.success('Content saved to your library!');
    } catch (error) {
      toast.error('Failed to save content');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AI Content Generator</h1>
          <p className="mt-2 text-gray-600">
            Create engaging social media content with AI assistance
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Content Generation Form */}
          <div className="bg-white rounded-lg shadow-lg">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Generate New Content</h2>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Platform Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Platform
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {platformOptions.map((platform) => (
                      <label key={platform.value} className="cursor-pointer">
                        <input
                          type="radio"
                          name="platform"
                          value={platform.value}
                          checked={formData.platform === platform.value}
                          onChange={handleInputChange}
                          className="sr-only"
                        />
                        <div className={`p-3 rounded-lg border-2 text-center transition-colors ${
                          formData.platform === platform.value
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}>
                          <div className="text-2xl mb-1">{platform.icon}</div>
                          <div className="text-sm font-medium">{platform.label}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Content Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Content Type
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {contentTypeOptions.map((type) => (
                      <label key={type.value} className="cursor-pointer">
                        <input
                          type="radio"
                          name="content_type"
                          value={type.value}
                          checked={formData.content_type === type.value}
                          onChange={handleInputChange}
                          className="sr-only"
                        />
                        <div className={`p-3 rounded-lg border-2 text-center transition-colors ${
                          formData.content_type === type.value
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}>
                          <div className="text-xl mb-1">{type.icon}</div>
                          <div className="text-sm font-medium">{type.label}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Topic */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Topic or Theme
                  </label>
                  <input
                    type="text"
                    name="topic"
                    value={formData.topic}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., productivity tips, healthy recipes, fitness motivation..."
                  />
                </div>

                {/* Target Audience */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Audience (Optional)
                  </label>
                  <input
                    type="text"
                    name="target_audience"
                    value={formData.target_audience}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., young professionals, fitness enthusiasts, small business owners..."
                  />
                </div>

                {/* Tone and Settings */}
                <div className="grid grid-cols-2 gap-4">
                  {/* Tone */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tone
                    </label>
                    <select
                      name="tone"
                      value={formData.tone}
                      onChange={handleInputChange}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {toneOptions.map((tone) => (
                        <option key={tone.value} value={tone.value}>
                          {tone.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Hashtag Count */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Hashtags: {formData.hashtag_count}
                    </label>
                    <input
                      type="range"
                      name="hashtag_count"
                      min="0"
                      max="30"
                      value={formData.hashtag_count}
                      onChange={handleInputChange}
                      className="w-full"
                    />
                  </div>
                </div>

                {/* Generate Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-lg hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Generating...
                    </div>
                  ) : (
                    '✨ Generate Content'
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Generated Content Display */}
          <div className="bg-white rounded-lg shadow-lg">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Generated Content</h2>
              
              {generatedContent ? (
                <div className="space-y-6">
                  {/* Content Metadata */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-2">Content Details</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                      <div>Platform: <span className="font-medium capitalize">{generatedContent.content.platform}</span></div>
                      <div>Type: <span className="font-medium capitalize">{generatedContent.content.content_type}</span></div>
                      <div>Quality Score: <span className="font-medium">{(generatedContent.content.quality_score * 100).toFixed(0)}%</span></div>
                      <div>Viral Potential: <span className="font-medium">{(generatedContent.content.viral_potential * 100).toFixed(0)}%</span></div>
                    </div>
                  </div>

                  {/* AI Generation Info */}
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-2">Generation Info</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                      <div>Provider: <span className="font-medium capitalize">{generatedContent.generation_info.provider}</span></div>
                      <div>Model: <span className="font-medium">{generatedContent.generation_info.model}</span></div>
                      <div>Tokens: <span className="font-medium">{generatedContent.generation_info.tokens_used}</span></div>
                      <div>Cost: <span className="font-medium">
                        {generatedContent.generation_info.cost === 0 ? 'Free' : `$${generatedContent.generation_info.cost.toFixed(6)}`}
                      </span></div>
                      <div>Time: <span className="font-medium">{generatedContent.generation_info.response_time.toFixed(2)}s</span></div>
                    </div>
                  </div>

                  {/* Generated Text Content */}
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Content</h3>
                    <div className="bg-white border rounded-lg p-4 relative">
                      <pre className="whitespace-pre-wrap text-sm text-gray-900 font-sans">
                        {generatedContent.content.text_content}
                      </pre>
                      <button
                        onClick={() => copyToClipboard(generatedContent.content.text_content)}
                        className="absolute top-2 right-2 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                        title="Copy to clipboard"
                      >
                        📋
                      </button>
                    </div>
                  </div>

                  {/* Hashtags */}
                  {generatedContent.content.hashtags && generatedContent.content.hashtags.length > 0 && (
                    <div>
                      <h3 className="font-medium text-gray-900 mb-2">Hashtags</h3>
                      <div className="bg-white border rounded-lg p-4 relative">
                        <div className="flex flex-wrap gap-2">
                          {generatedContent.content.hashtags.map((hashtag, index) => (
                            <span key={index} className="inline-block bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded">
                              {hashtag}
                            </span>
                          ))}
                        </div>
                        <button
                          onClick={() => copyToClipboard(generatedContent.content.hashtags.join(' '))}
                          className="absolute top-2 right-2 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                          title="Copy hashtags to clipboard"
                        >
                          📋
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <button
                      onClick={() => copyToClipboard(
                        generatedContent.content.text_content + 
                        (generatedContent.content.hashtags?.length ? '\n\n' + generatedContent.content.hashtags.join(' ') : '')
                      )}
                      className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
                    >
                      📋 Copy All
                    </button>
                    <button
                      onClick={saveContent}
                      className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                      💾 Save Content
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🤖</div>
                  <p className="text-gray-500">Generated content will appear here</p>
                  <p className="text-sm text-gray-400 mt-2">Fill out the form and click generate to create AI-powered content</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIContentGenerator;