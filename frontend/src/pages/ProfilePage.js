import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import { 
  UserCircleIcon,
  Cog6ToothIcon,
  CreditCardIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  BellIcon,
  KeyIcon
} from '@heroicons/react/24/outline';

const subscriptionTiers = {
  starter: {
    name: 'Starter',
    price: '$29/month',
    color: 'text-blue-600 bg-blue-100',
    features: ['Basic content generation', '2 platforms', 'Ollama models only']
  },
  professional: {
    name: 'Professional', 
    price: '$79/month',
    color: 'text-purple-600 bg-purple-100',
    features: ['Advanced content generation', '6 platforms', 'All LLM providers', 'Viral content replication']
  },
  business: {
    name: 'Business',
    price: '$199/month', 
    color: 'text-green-600 bg-green-100',
    features: ['Enterprise features', 'Unlimited platforms', 'Personal AI coach', 'Team collaboration']
  }
};

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const { user, updateUser } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue
  } = useForm({
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
      niche: user?.niche || '',
      target_audience: user?.target_audience || ''
    }
  });

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      const response = await authAPI.updateProfile({
        first_name: data.first_name,
        last_name: data.last_name,
        niche: data.niche,
        target_audience: data.target_audience
      });
      
      updateUser(response.data);
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error(error.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserCircleIcon },
    { id: 'subscription', name: 'Subscription', icon: CreditCardIcon },
    { id: 'settings', name: 'Settings', icon: Cog6ToothIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
  ];

  const currentTier = subscriptionTiers[user?.subscription_tier] || subscriptionTiers.starter;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 py-6 sm:px-0">
          <div className="flex items-center space-x-4">
            <div className="h-16 w-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-2xl">
                {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
              </span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {user?.first_name} {user?.last_name}
              </h1>
              <p className="mt-1 text-gray-600">
                {user?.email} • <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${currentTier.color}`}>
                  {currentTier.name} Plan
                </span>
              </p>
            </div>
          </div>
        </div>

        <div className="px-4 sm:px-0">
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-4">
            {/* Sidebar */}
            <div className="lg:col-span-1">
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                        activeTab === tab.id
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="h-5 w-5 mr-3" />
                      {tab.name}
                    </button>
                  );
                })}
              </nav>

              {/* Success Stats */}
              <div className="mt-8 card">
                <div className="card-header">
                  <h3 className="card-title flex items-center">
                    <ChartBarIcon className="h-5 w-5 mr-2" />
                    Success Stats
                  </h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Success Score</span>
                    <span className="font-semibold text-blue-600">
                      {user?.success_score?.toFixed(1) || '0.0'}/10
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Total Earnings</span>
                    <span className="font-semibold text-green-600">
                      ${user?.total_earnings?.toFixed(2) || '0.00'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Success Level</span>
                    <span className="font-semibold text-purple-600 capitalize">
                      {user?.success_level || 'Beginner'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Days Active</span>
                    <span className="font-semibold">
                      {user?.created_at ? Math.floor((new Date() - new Date(user.created_at)) / (1000 * 60 * 60 * 24)) : 0}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Content */}
            <div className="lg:col-span-3">
              {/* Profile Tab */}
              {activeTab === 'profile' && (
                <div className="card">
                  <div className="card-header">
                    <h3 className="card-title">Profile Information</h3>
                    <p className="card-subtitle">
                      Update your personal information and preferences
                    </p>
                  </div>

                  <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                      <div>
                        <label htmlFor="first_name" className="form-label">
                          First name
                        </label>
                        <input
                          id="first_name"
                          type="text"
                          className="form-input"
                          {...register('first_name', {
                            required: 'First name is required'
                          })}
                        />
                        {errors.first_name && (
                          <p className="form-error">{errors.first_name.message}</p>
                        )}
                      </div>

                      <div>
                        <label htmlFor="last_name" className="form-label">
                          Last name
                        </label>
                        <input
                          id="last_name"
                          type="text"
                          className="form-input"
                          {...register('last_name', {
                            required: 'Last name is required'
                          })}
                        />
                        {errors.last_name && (
                          <p className="form-error">{errors.last_name.message}</p>
                        )}
                      </div>
                    </div>

                    <div>
                      <label htmlFor="email" className="form-label">
                        Email address
                      </label>
                      <input
                        id="email"
                        type="email"
                        className="form-input bg-gray-100 cursor-not-allowed"
                        disabled
                        {...register('email')}
                      />
                      <p className="text-sm text-gray-500 mt-1">
                        Email cannot be changed. Contact support if you need to update it.
                      </p>
                    </div>

                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                      <div>
                        <label htmlFor="niche" className="form-label">
                          Your Niche
                        </label>
                        <select
                          id="niche"
                          className="form-select"
                          {...register('niche')}
                        >
                          <option value="">Select your niche</option>
                          <option value="fitness">Fitness & Health</option>
                          <option value="business">Business & Entrepreneurship</option>
                          <option value="lifestyle">Lifestyle</option>
                          <option value="technology">Technology</option>
                          <option value="education">Education</option>
                          <option value="entertainment">Entertainment</option>
                          <option value="food">Food & Cooking</option>
                          <option value="travel">Travel</option>
                          <option value="fashion">Fashion & Beauty</option>
                          <option value="finance">Finance & Investment</option>
                          <option value="other">Other</option>
                        </select>
                      </div>

                      <div>
                        <label htmlFor="target_audience" className="form-label">
                          Target Audience
                        </label>
                        <input
                          id="target_audience"
                          type="text"
                          className="form-input"
                          placeholder="e.g., Young professionals"
                          {...register('target_audience')}
                        />
                      </div>
                    </div>

                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary flex items-center"
                      >
                        {loading ? (
                          <LoadingSpinner size="small" text="" />
                        ) : (
                          'Save Changes'
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {/* Subscription Tab */}
              {activeTab === 'subscription' && (
                <div className="space-y-6">
                  {/* Current Plan */}
                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title">Current Plan</h3>
                      <p className="card-subtitle">
                        You are currently on the {currentTier.name} plan
                      </p>
                    </div>
                    
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h4 className="text-xl font-bold text-gray-900">{currentTier.name}</h4>
                          <p className="text-2xl font-bold text-blue-600">{currentTier.price}</p>
                        </div>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${currentTier.color}`}>
                          Current Plan
                        </span>
                      </div>
                      
                      <ul className="space-y-2">
                        {currentTier.features.map((feature, index) => (
                          <li key={index} className="flex items-center text-sm text-gray-700">
                            <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Upgrade Options */}
                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title">Upgrade Your Plan</h3>
                      <p className="card-subtitle">
                        Unlock more features and accelerate your success
                      </p>
                    </div>
                    
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                      {Object.entries(subscriptionTiers).map(([key, tier]) => (
                        <div key={key} className={`border-2 rounded-lg p-4 ${
                          user?.subscription_tier === key 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-gray-200 hover:border-blue-300'
                        } transition-colors`}>
                          <h4 className="font-bold text-lg text-gray-900">{tier.name}</h4>
                          <p className="text-xl font-bold text-blue-600 mb-3">{tier.price}</p>
                          
                          <ul className="space-y-1 mb-4">
                            {tier.features.map((feature, index) => (
                              <li key={index} className="text-xs text-gray-600 flex items-center">
                                <div className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></div>
                                {feature}
                              </li>
                            ))}
                          </ul>
                          
                          {user?.subscription_tier === key ? (
                            <button disabled className="w-full btn-secondary opacity-50 text-xs">
                              Current Plan
                            </button>
                          ) : (
                            <button className="w-full btn-primary text-xs">
                              Upgrade Now
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Settings Tab */}
              {activeTab === 'settings' && (
                <div className="card">
                  <div className="card-header">
                    <h3 className="card-title">Preferences & Settings</h3>
                    <p className="card-subtitle">
                      Customize your automation preferences
                    </p>
                  </div>

                  <div className="space-y-6">
                    {/* Notifications */}
                    <div>
                      <h4 className="flex items-center text-lg font-semibold text-gray-900 mb-3">
                        <BellIcon className="h-5 w-5 mr-2" />
                        Notifications
                      </h4>
                      <div className="space-y-3">
                        <label className="flex items-center">
                          <input type="checkbox" className="form-checkbox" defaultChecked />
                          <span className="ml-2 text-sm text-gray-700">
                            Email notifications for content performance
                          </span>
                        </label>
                        <label className="flex items-center">
                          <input type="checkbox" className="form-checkbox" defaultChecked />
                          <span className="ml-2 text-sm text-gray-700">
                            Success coaching reminders
                          </span>
                        </label>
                        <label className="flex items-center">
                          <input type="checkbox" className="form-checkbox" />
                          <span className="ml-2 text-sm text-gray-700">
                            Weekly analytics reports
                          </span>
                        </label>
                      </div>
                    </div>

                    {/* Voice Features */}
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Voice Features</h4>
                      <div className="space-y-3">
                        <label className="flex items-center">
                          <input 
                            type="checkbox" 
                            className="form-checkbox" 
                            defaultChecked={user?.voice_enabled}
                          />
                          <span className="ml-2 text-sm text-gray-700">
                            Enable voice control
                          </span>
                        </label>
                        <label className="flex items-center">
                          <input type="checkbox" className="form-checkbox" />
                          <span className="ml-2 text-sm text-gray-700">
                            Voice response feedback
                          </span>
                        </label>
                      </div>
                    </div>

                    {/* Automation Settings */}
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Automation</h4>
                      <div className="space-y-3">
                        <label className="flex items-center">
                          <input type="checkbox" className="form-checkbox" defaultChecked />
                          <span className="ml-2 text-sm text-gray-700">
                            Auto-optimize posting times
                          </span>
                        </label>
                        <label className="flex items-center">
                          <input type="checkbox" className="form-checkbox" />
                          <span className="ml-2 text-sm text-gray-700">
                            Auto-generate hashtags
                          </span>
                        </label>
                        <label className="flex items-center">
                          <input type="checkbox" className="form-checkbox" />
                          <span className="ml-2 text-sm text-gray-700">
                            Enable viral content replication
                          </span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Security Tab */}
              {activeTab === 'security' && (
                <div className="space-y-6">
                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title flex items-center">
                        <KeyIcon className="h-5 w-5 mr-2" />
                        Change Password
                      </h3>
                      <p className="card-subtitle">
                        Update your password to keep your account secure
                      </p>
                    </div>

                    <form className="space-y-4">
                      <div>
                        <label className="form-label">Current Password</label>
                        <input type="password" className="form-input" />
                      </div>
                      <div>
                        <label className="form-label">New Password</label>
                        <input type="password" className="form-input" />
                      </div>
                      <div>
                        <label className="form-label">Confirm New Password</label>
                        <input type="password" className="form-input" />
                      </div>
                      <button type="submit" className="btn-primary">
                        Update Password
                      </button>
                    </form>
                  </div>

                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title">Account Security</h3>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold">Two-Factor Authentication</h4>
                          <p className="text-sm text-gray-600">Add an extra layer of security</p>
                        </div>
                        <button className="btn-outline text-sm">Enable</button>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold">Login Sessions</h4>
                          <p className="text-sm text-gray-600">Manage your active sessions</p>
                        </div>
                        <button className="btn-outline text-sm">Manage</button>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold">Download Data</h4>
                          <p className="text-sm text-gray-600">Export your account data</p>
                        </div>
                        <button className="btn-outline text-sm">Download</button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}