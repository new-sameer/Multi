import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { contentAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import { 
  PencilSquareIcon,
  TrashIcon,
  EyeIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  DocumentDuplicateIcon
} from '@heroicons/react/24/outline';

const platforms = {
  instagram: { name: 'Instagram', color: 'platform-instagram' },
  tiktok: { name: 'TikTok', color: 'platform-tiktok' },
  linkedin: { name: 'LinkedIn', color: 'platform-linkedin' },
  youtube: { name: 'YouTube', color: 'platform-youtube' },
  twitter: { name: 'Twitter/X', color: 'platform-twitter' },
  facebook: { name: 'Facebook', color: 'platform-facebook' },
};

const statusIcons = {
  draft: { icon: PencilSquareIcon, color: 'text-gray-500', bg: 'bg-gray-100' },
  scheduled: { icon: ClockIcon, color: 'text-blue-500', bg: 'bg-blue-100' },
  published: { icon: CheckCircleIcon, color: 'text-green-500', bg: 'bg-green-100' },
  failed: { icon: XCircleIcon, color: 'text-red-500', bg: 'bg-red-100' },
};

export default function ContentLibrary() {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    platform: '',
    status: '',
    search: '',
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadContent();
  }, [filters]);

  const loadContent = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.platform) params.platform = filters.platform;
      if (filters.status) params.status = filters.status;
      
      const response = await contentAPI.list(params);
      let contentData = response.data;

      // Apply search filter on frontend
      if (filters.search) {
        contentData = contentData.filter(item =>
          item.title.toLowerCase().includes(filters.search.toLowerCase()) ||
          item.text_content.toLowerCase().includes(filters.search.toLowerCase())
        );
      }

      setContent(contentData);
    } catch (error) {
      console.error('Error loading content:', error);
      toast.error('Failed to load content library');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (contentId) => {
    if (!window.confirm('Are you sure you want to delete this content?')) {
      return;
    }

    try {
      await contentAPI.delete(contentId);
      toast.success('Content deleted successfully');
      loadContent();
    } catch (error) {
      console.error('Error deleting content:', error);
      toast.error('Failed to delete content');
    }
  };

  const handleDuplicate = async (contentItem) => {
    try {
      const duplicateData = {
        title: `${contentItem.title} (Copy)`,
        content_type: contentItem.content_type,
        platform: contentItem.platform,
        text_content: contentItem.text_content,
        hashtags: contentItem.hashtags,
      };

      await contentAPI.create(duplicateData);
      toast.success('Content duplicated successfully');
      loadContent();
    } catch (error) {
      console.error('Error duplicating content:', error);
      toast.error('Failed to duplicate content');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const truncateText = (text, maxLength = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="large" text="Loading your content library..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 py-6 sm:px-0">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Content Library</h1>
              <p className="mt-2 text-gray-600">
                Manage all your created content in one place
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="btn-outline flex items-center space-x-2"
              >
                <FunnelIcon className="h-5 w-5" />
                <span>Filters</span>
              </button>
              <Link to="/create-content" className="btn-primary flex items-center space-x-2">
                <PlusIcon className="h-5 w-5" />
                <span>Create New</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="px-4 sm:px-0 mb-6">
            <div className="card">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
                {/* Search */}
                <div className="sm:col-span-2">
                  <label className="form-label">Search</label>
                  <div className="relative">
                    <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                    <input
                      type="text"
                      className="form-input pl-10"
                      placeholder="Search content..."
                      value={filters.search}
                      onChange={(e) => setFilters({...filters, search: e.target.value})}
                    />
                  </div>
                </div>

                {/* Platform */}
                <div>
                  <label className="form-label">Platform</label>
                  <select
                    className="form-select"
                    value={filters.platform}
                    onChange={(e) => setFilters({...filters, platform: e.target.value})}
                  >
                    <option value="">All Platforms</option>
                    {Object.entries(platforms).map(([key, platform]) => (
                      <option key={key} value={key}>{platform.name}</option>
                    ))}
                  </select>
                </div>

                {/* Status */}
                <div>
                  <label className="form-label">Status</label>
                  <select
                    className="form-select"
                    value={filters.status}
                    onChange={(e) => setFilters({...filters, status: e.target.value})}
                  >
                    <option value="">All Statuses</option>
                    <option value="draft">Draft</option>
                    <option value="scheduled">Scheduled</option>
                    <option value="published">Published</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        <div className="px-4 sm:px-0 mb-8">
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
            <div className="stat-card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentDuplicateIcon className="h-8 w-8 text-blue-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="stat-label">Total Content</dt>
                    <dd className="stat-value">{content.length}</dd>
                  </dl>
                </div>
              </div>
            </div>

            <div className="stat-card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <PencilSquareIcon className="h-8 w-8 text-gray-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="stat-label">Drafts</dt>
                    <dd className="stat-value">
                      {content.filter(c => c.status === 'draft').length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>

            <div className="stat-card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ClockIcon className="h-8 w-8 text-blue-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="stat-label">Scheduled</dt>
                    <dd className="stat-value">
                      {content.filter(c => c.status === 'scheduled').length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>

            <div className="stat-card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-8 w-8 text-green-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="stat-label">Published</dt>
                    <dd className="stat-value">
                      {content.filter(c => c.status === 'published').length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content Grid */}
        <div className="px-4 sm:px-0">
          {content.length === 0 ? (
            <div className="text-center py-12">
              <DocumentDuplicateIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No content found</h3>
              <p className="text-gray-600 mb-6">
                {filters.search || filters.platform || filters.status 
                  ? "No content matches your current filters."
                  : "Start creating content to see it here."
                }
              </p>
              {!filters.search && !filters.platform && !filters.status && (
                <Link to="/create-content" className="btn-primary">
                  Create Your First Content
                </Link>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {content.map((item) => {
                const platform = platforms[item.platform];
                const status = statusIcons[item.status];
                const StatusIcon = status.icon;

                return (
                  <div key={item.id} className="card hover:shadow-lg transition-shadow">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        <span className={`platform-pill ${platform?.color} text-xs`}>
                          {platform?.name}
                        </span>
                        <div className={`p-1 rounded-full ${status.bg}`}>
                          <StatusIcon className={`h-4 w-4 ${status.color}`} />
                        </div>
                      </div>
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => handleDuplicate(item)}
                          className="p-1 text-gray-400 hover:text-blue-600 rounded"
                          title="Duplicate"
                        >
                          <DocumentDuplicateIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="p-1 text-gray-400 hover:text-red-600 rounded"
                          title="Delete"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="space-y-3">
                      <h3 className="font-semibold text-gray-900 line-clamp-2">
                        {item.title}
                      </h3>
                      
                      <p className="text-sm text-gray-600 line-clamp-3">
                        {truncateText(item.text_content)}
                      </p>

                      {item.hashtags && item.hashtags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {item.hashtags.slice(0, 3).map((hashtag, index) => (
                            <span key={index} className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                              {hashtag}
                            </span>
                          ))}
                          {item.hashtags.length > 3 && (
                            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                              +{item.hashtags.length - 3} more
                            </span>
                          )}
                        </div>
                      )}

                      <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100">
                        <span>Created {formatDate(item.created_at)}</span>
                        <div className="flex items-center space-x-2">
                          <span>Quality: {(item.quality_score * 10 || 0).toFixed(1)}/10</span>
                          <span>•</span>
                          <span>Viral: {(item.viral_potential * 10 || 0).toFixed(1)}/10</span>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-2 mt-4 pt-4 border-t border-gray-100">
                      <button className="btn-outline text-xs flex-1">
                        <EyeIcon className="h-4 w-4 mr-1" />
                        View
                      </button>
                      <button className="btn-primary text-xs flex-1">
                        <PencilSquareIcon className="h-4 w-4 mr-1" />
                        Edit
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}