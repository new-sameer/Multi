import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import { 
  CheckCircleIcon, 
  SparklesIcon,
  TrophyIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  UserGroupIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const steps = [
  {
    id: 1,
    name: 'Success Goals',
    description: 'Define your social media success targets',
    icon: TrophyIcon,
  },
  {
    id: 2,
    name: 'Preferences',
    description: 'Customize your automation preferences',
    icon: SparklesIcon,
  },
  {
    id: 3,
    name: 'Ready to Go!',
    description: 'Your success journey begins now',
    icon: CheckCircleIcon,
  },
];

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const { user, updateUser } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm({
    defaultValues: {
      followersTarget: 1000,
      engagementRateTarget: 3.0,
      revenueTarget: 100,
      timeframeDays: 90,
      contentTypes: [],
      platforms: [],
      voiceEnabled: false,
    }
  });

  const watchedFields = watch();

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      // Set success goals
      const goalsData = {
        followers_target: parseInt(data.followersTarget),
        engagement_rate_target: parseFloat(data.engagementRateTarget) / 100,
        revenue_target: parseFloat(data.revenueTarget),
        timeframe_days: parseInt(data.timeframeDays),
      };

      await authAPI.setSuccessGoals(goalsData);
      
      // Update user preferences (mock for now)
      const updatedUser = {
        ...user,
        onboarding_completed: true,
        voice_enabled: data.voiceEnabled,
        preferred_platforms: data.platforms,
        preferred_content_types: data.contentTypes,
      };

      updateUser(updatedUser);
      toast.success('Welcome to your success journey!');
      navigate('/dashboard');
      
    } catch (error) {
      console.error('Onboarding error:', error);
      toast.error('Failed to complete setup. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const isStepComplete = (stepId) => {
    switch (stepId) {
      case 1:
        return watchedFields.followersTarget && watchedFields.engagementRateTarget && watchedFields.revenueTarget;
      case 2:
        return watchedFields.platforms && watchedFields.platforms.length > 0;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100">
      <div className="max-w-3xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto h-16 w-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mb-4">
            <span className="text-white font-bold text-xl">SMA</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome to Your Success Journey!
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Let's set up your goals and preferences to maximize your social media success
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center">
            {steps.map((step, stepIdx) => (
              <div key={step.id} className="flex items-center">
                <div
                  className={`flex items-center justify-center w-12 h-12 rounded-full border-2 ${
                    currentStep >= step.id
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-white border-gray-300 text-gray-500'
                  }`}
                >
                  {currentStep > step.id ? (
                    <CheckCircleIcon className="w-6 h-6" />
                  ) : (
                    <span className="text-sm font-semibold">{step.id}</span>
                  )}
                </div>
                {stepIdx < steps.length - 1 && (
                  <div
                    className={`w-16 h-1 mx-4 ${
                      currentStep > step.id ? 'bg-blue-600' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-center mt-4">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900">
                {steps[currentStep - 1].name}
              </h3>
              <p className="text-sm text-gray-600">
                {steps[currentStep - 1].description}
              </p>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="card">
          <form onSubmit={handleSubmit(onSubmit)}>
            {/* Step 1: Success Goals */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div className="text-center mb-6">
                  <TrophyIcon className="h-12 w-12 text-yellow-500 mx-auto mb-3" />
                  <h2 className="text-2xl font-bold text-gray-900">Set Your Success Goals</h2>
                  <p className="text-gray-600 mt-2">
                    Define what success looks like for you. These goals will help our AI coach guide your journey.
                  </p>
                </div>

                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <label className="form-label">
                      <UserGroupIcon className="w-5 h-5 inline mr-2" />
                      Followers Target
                    </label>
                    <input
                      type="number"
                      className="form-input"
                      min="100"
                      max="1000000"
                      {...register('followersTarget', {
                        required: 'Followers target is required',
                        min: { value: 100, message: 'Minimum 100 followers' },
                      })}
                    />
                    {errors.followersTarget && (
                      <p className="form-error">{errors.followersTarget.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="form-label">
                      <ChartBarIcon className="w-5 h-5 inline mr-2" />
                      Engagement Rate Target (%)
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-input"
                      min="1"
                      max="20"
                      {...register('engagementRateTarget', {
                        required: 'Engagement rate target is required',
                        min: { value: 1, message: 'Minimum 1%' },
                      })}
                    />
                    {errors.engagementRateTarget && (
                      <p className="form-error">{errors.engagementRateTarget.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="form-label">
                      <CurrencyDollarIcon className="w-5 h-5 inline mr-2" />
                      Revenue Target ($)
                    </label>
                    <input
                      type="number"
                      className="form-input"
                      min="0"
                      {...register('revenueTarget', {
                        required: 'Revenue target is required',
                        min: { value: 0, message: 'Cannot be negative' },
                      })}
                    />
                    {errors.revenueTarget && (
                      <p className="form-error">{errors.revenueTarget.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="form-label">
                      <CalendarIcon className="w-5 h-5 inline mr-2" />
                      Timeframe (days)
                    </label>
                    <select className="form-select" {...register('timeframeDays')}>
                      <option value="30">30 days</option>
                      <option value="60">60 days</option>
                      <option value="90">90 days</option>
                      <option value="180">6 months</option>
                      <option value="365">1 year</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Preferences */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <div className="text-center mb-6">
                  <SparklesIcon className="h-12 w-12 text-purple-500 mx-auto mb-3" />
                  <h2 className="text-2xl font-bold text-gray-900">Customize Your Experience</h2>
                  <p className="text-gray-600 mt-2">
                    Tell us your preferences so we can personalize your automation experience.
                  </p>
                </div>

                {/* Platforms */}
                <div>
                  <label className="form-label">Preferred Platforms</label>
                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                    {[
                      { id: 'instagram', name: 'Instagram', color: 'bg-gradient-to-r from-purple-500 to-pink-500' },
                      { id: 'tiktok', name: 'TikTok', color: 'bg-black' },
                      { id: 'linkedin', name: 'LinkedIn', color: 'bg-blue-600' },
                      { id: 'youtube', name: 'YouTube', color: 'bg-red-600' },
                      { id: 'twitter', name: 'Twitter', color: 'bg-blue-400' },
                      { id: 'facebook', name: 'Facebook', color: 'bg-blue-800' },
                    ].map((platform) => (
                      <label key={platform.id} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          className="form-checkbox h-4 w-4 text-blue-600"
                          value={platform.id}
                          {...register('platforms')}
                        />
                        <span className={`px-3 py-1 rounded-full text-white text-sm ${platform.color}`}>
                          {platform.name}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Content Types */}
                <div>
                  <label className="form-label">Preferred Content Types</label>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      'Educational',
                      'Entertainment',
                      'Promotional',
                      'Behind-the-scenes',
                      'User-generated',
                      'Trending topics',
                    ].map((type) => (
                      <label key={type} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          className="form-checkbox h-4 w-4 text-blue-600"
                          value={type.toLowerCase().replace(/\s+/g, '_')}
                          {...register('contentTypes')}
                        />
                        <span className="text-sm text-gray-700">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Voice Control */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <label className="flex items-start space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      className="form-checkbox h-5 w-5 text-blue-600 mt-1"
                      {...register('voiceEnabled')}
                    />
                    <div>
                      <h4 className="font-semibold text-blue-900">Enable Voice Control</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        Control your social media automation with voice commands. 
                        This is a premium feature that will revolutionize how you manage your presence.
                      </p>
                    </div>
                  </label>
                </div>
              </div>
            )}

            {/* Step 3: Complete */}
            {currentStep === 3 && (
              <div className="text-center space-y-6">
                <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto" />
                <div>
                  <h2 className="text-3xl font-bold text-gray-900">You're All Set!</h2>
                  <p className="text-lg text-gray-600 mt-2">
                    Your AI-powered social media success journey is about to begin.
                  </p>
                </div>

                <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
                  <h3 className="text-xl font-bold mb-3">Your Success Plan</h3>
                  <div className="grid grid-cols-2 gap-4 text-left">
                    <div>
                      <p className="text-blue-100 text-sm">Followers Goal</p>
                      <p className="font-semibold">{watchedFields.followersTarget?.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-blue-100 text-sm">Engagement Target</p>
                      <p className="font-semibold">{watchedFields.engagementRateTarget}%</p>
                    </div>
                    <div>
                      <p className="text-blue-100 text-sm">Revenue Goal</p>
                      <p className="font-semibold">${watchedFields.revenueTarget}</p>
                    </div>
                    <div>
                      <p className="text-blue-100 text-sm">Timeframe</p>
                      <p className="font-semibold">{watchedFields.timeframeDays} days</p>
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold text-green-800 mb-2">🎯 Success Guarantee Active</h4>
                  <p className="text-sm text-green-700">
                    Our AI will monitor your progress and provide interventions to ensure you reach your goals. 
                    If you don't see results, we'll refund your money.
                  </p>
                </div>
              </div>
            )}

            {/* Navigation */}
            <div className="flex justify-between pt-6 border-t border-gray-200 mt-8">
              {currentStep > 1 ? (
                <button
                  type="button"
                  onClick={handleBack}
                  className="btn-secondary"
                >
                  Back
                </button>
              ) : (
                <div></div>
              )}

              {currentStep < steps.length ? (
                <button
                  type="button"
                  onClick={handleNext}
                  disabled={!isStepComplete(currentStep)}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continue
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary flex items-center"
                >
                  {loading ? (
                    <LoadingSpinner size="small" text="" />
                  ) : (
                    'Start My Success Journey!'
                  )}
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}