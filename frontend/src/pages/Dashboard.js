import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  ChartBarIcon, 
  PencilSquareIcon, 
  DocumentDuplicateIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  CalendarIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

export default function Dashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalContent: 0,
    totalFollowers: 0,
    engagementRate: 0,
    totalEarnings: 0,
    successScore: 0
  });

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
      try {
        // In a real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data based on user's current state
        setStats({
          totalContent: 12,
          totalFollowers: 1250,
          engagementRate: 3.2,
          totalEarnings: user?.total_earnings || 0,
          successScore: user?.success_score || 0
        });
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="large" text="Loading your dashboard..." />
      </div>
    );
  }

  // Check if user needs onboarding
  if (!user?.onboarding_completed) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full card text-center">
          <SparklesIcon className="h-16 w-16 text-blue-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Welcome to Your Success Journey!
          </h2>
          <p className="text-gray-600 mb-6">
            Let's set up your goals and preferences to get you started on the path to social media success.
          </p>
          <Link to="/onboarding" className="btn-primary w-full">
            Complete Setup
          </Link>
        </div>
      </div>
    );
  }

  const quickActions = [
    {
      name: 'Create Content',
      description: 'Generate AI-powered content for your platforms',
      href: '/create-content',
      icon: PencilSquareIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'View Library',
      description: 'Browse and manage your content library',
      href: '/content-library',
      icon: DocumentDuplicateIcon,
      color: 'bg-purple-500',
    },
    {
      name: 'Analytics',
      description: 'View your performance metrics and insights',
      href: '/analytics',
      icon: ChartBarIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Success Coaching',
      description: 'Get personalized AI coaching for growth',
      href: '/coaching',
      icon: SparklesIcon,
      color: 'bg-yellow-500',
    },
  ];

  const statCards = [
    {
      name: 'Total Content',
      value: stats.totalContent,
      unit: 'posts',
      change: '+2.5%',
      changeType: 'positive',
      icon: DocumentDuplicateIcon,
    },
    {
      name: 'Total Followers',
      value: stats.totalFollowers.toLocaleString(),
      unit: '',
      change: '+12.3%',
      changeType: 'positive',
      icon: UserGroupIcon,
    },
    {
      name: 'Engagement Rate',
      value: stats.engagementRate,
      unit: '%',
      change: '+0.8%',
      changeType: 'positive',
      icon: ArrowTrendingUpIcon,
    },
    {
      name: 'Total Earnings',
      value: `$${stats.totalEarnings.toFixed(2)}`,
      unit: '',
      change: '+15.2%',
      changeType: 'positive',
      icon: CurrencyDollarIcon,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 py-6 sm:px-0">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {user?.first_name}!
              </h1>
              <p className="mt-2 text-gray-600">
                Here's your social media automation dashboard
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-500">Success Score</p>
                <p className="text-2xl font-bold text-blue-600">
                  {stats.successScore.toFixed(1)}/10
                </p>
              </div>
              <div className="h-16 w-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xl">
                  {user?.success_level?.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="px-4 sm:px-0">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            {statCards.map((stat) => {
              const Icon = stat.icon;
              return (
                <div key={stat.name} className="stat-card">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Icon className="h-8 w-8 text-gray-400" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="stat-label truncate">
                          {stat.name}
                        </dt>
                        <dd className="flex items-baseline">
                          <div className="stat-value">
                            {stat.value}
                            {stat.unit && (
                              <span className="text-lg font-medium text-gray-500 ml-1">
                                {stat.unit}
                              </span>
                            )}
                          </div>
                          <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                            stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {stat.change}
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="px-4 sm:px-0">
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            {/* Quick Actions */}
            <div className="lg:col-span-2">
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Quick Actions</h3>
                  <p className="card-subtitle">
                    Get started with these powerful features
                  </p>
                </div>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {quickActions.map((action) => {
                    const Icon = action.icon;
                    return (
                      <Link
                        key={action.name}
                        to={action.href}
                        className="group relative rounded-lg border border-gray-300 bg-white p-6 hover:shadow-lg transition-all duration-200 hover:border-blue-300"
                      >
                        <div>
                          <span className={`inline-flex p-3 rounded-lg ${action.color}`}>
                            <Icon className="h-6 w-6 text-white" />
                          </span>
                        </div>
                        <div className="mt-4">
                          <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600">
                            {action.name}
                          </h3>
                          <p className="mt-2 text-sm text-gray-500">
                            {action.description}
                          </p>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Success Journey */}
            <div className="space-y-6">
              {/* Success Progress */}
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Success Journey</h3>
                  <p className="card-subtitle">Your progress to success</p>
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">
                        Overall Progress
                      </span>
                      <span className="text-sm text-gray-500">
                        {Math.round(stats.successScore * 10)}%
                      </span>
                    </div>
                    <div className="progress-bar mt-2">
                      <div 
                        className="progress-bar-fill"
                        style={{ width: `${Math.round(stats.successScore * 10)}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">✅ Profile Setup</span>
                      <span className="text-green-600">Complete</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">📝 First Content Created</span>
                      <span className="text-blue-600">In Progress</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">🎯 Goals Achievement</span>
                      <span className="text-gray-400">Pending</span>
                    </div>
                  </div>
                  
                  <Link to="/coaching" className="btn-outline w-full mt-4">
                    Get AI Coaching
                  </Link>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Recent Activity</h3>
                </div>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <CalendarIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900">Account created</p>
                      <p className="text-sm text-gray-500">
                        {new Date(user?.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="text-center py-4">
                    <p className="text-sm text-gray-500">
                      Start creating content to see more activity
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}