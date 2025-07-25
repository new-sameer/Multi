import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { contentAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import { 
  PencilSquareIcon,
  SparklesIcon,
  PhotoIcon,
  VideoCameraIcon,
  CalendarIcon,
  HashtagIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

const platforms = [
  { id: 'instagram', name: 'Instagram', color: 'platform-instagram', maxLength: 2200 },
  { id: 'tiktok', name: 'TikTok', color: 'platform-tiktok', maxLength: 300 },
  { id: 'linkedin', name: 'LinkedIn', color: 'platform-linkedin', maxLength: 3000 },
  { id: 'youtube', name: 'YouTube', color: 'platform-youtube', maxLength: 5000 },
  { id: 'twitter', name: 'Twitter/X', color: 'platform-twitter', maxLength: 280 },
  { id: 'facebook', name: 'Facebook', color: 'platform-facebook', maxLength: 63206 },
];

const contentTypes = [
  { id: 'text', name: 'Text Post', icon: PencilSquareIcon },
  { id: 'image', name: 'Image Post', icon: PhotoIcon },
  { id: 'video', name: 'Video Post', icon: VideoCameraIcon },
  { id: 'carousel', name: 'Carousel', icon: PhotoIcon },
];

const contentIdeas = [
  "Share a behind-the-scenes look at your process",
  "Create a tips and tricks post for your niche",
  "Share your journey and lessons learned",
  "Ask an engaging question to your audience",
  "Share a motivational quote with your thoughts",
  "Create a how-to tutorial or guide",
  "Share industry news with your perspective",
  "Create a before/after transformation post",
];

export default function ContentCreator() {
  const [loading, setLoading] = useState(false);
  const [generatingAI, setGeneratingAI] = useState(false);
  const [preview, setPreview] = useState(null);
  const [selectedPlatform, setSelectedPlatform] = useState('instagram');

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    reset
  } = useForm({
    defaultValues: {
      platform: 'instagram',
      content_type: 'text',
      title: '',
      text_content: '',
      hashtags: [],
      scheduled_for: '',
    }
  });

  const watchedFields = watch();
  const currentPlatform = platforms.find(p => p.id === watchedFields.platform);
  const maxLength = currentPlatform?.maxLength || 2200;

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      // Process hashtags
      const hashtagsArray = data.hashtags
        ? data.hashtags.split(' ').filter(tag => tag.trim().startsWith('#'))
        : [];

      const contentData = {
        title: data.title,
        content_type: data.content_type,
        platform: data.platform,
        text_content: data.text_content,
        hashtags: hashtagsArray,
        scheduled_for: data.scheduled_for || null,
      };

      const response = await contentAPI.create(contentData);
      toast.success('Content created successfully!');
      reset();
      setPreview(null);
    } catch (error) {
      console.error('Error creating content:', error);
      toast.error(error.response?.data?.error || 'Failed to create content');
    } finally {
      setLoading(false);
    }
  };

  const generateAIContent = async (prompt) => {
    setGeneratingAI(true);
    try {
      // Mock AI generation for now - in Phase 2 we'll implement real LLM integration
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockContent = `🚀 ${prompt}

Did you know that ${Math.floor(Math.random() * 90 + 10)}% of successful people in this industry follow this exact approach?

Here's what I've learned:
✅ Consistency beats perfection every time
✅ Engage authentically with your audience
✅ Share value before asking for anything
✅ Track your progress and adapt

What's your biggest challenge right now? Drop a comment below! 👇

#motivation #success #entrepreneur #mindset #growth`;

      setValue('text_content', mockContent);
      toast.success('AI content generated!');
    } catch (error) {
      toast.error('Failed to generate AI content');
    } finally {
      setGeneratingAI(false);
    }
  };

  const updatePreview = () => {
    const currentData = watch();
    setPreview({
      platform: currentData.platform,
      title: currentData.title,
      content: currentData.text_content,
      hashtags: currentData.hashtags ? currentData.hashtags.split(' ').filter(tag => tag.trim().startsWith('#')) : [],
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 py-6 sm:px-0">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Create Content</h1>
              <p className="mt-2 text-gray-600">
                Create engaging content for your social media platforms
              </p>
            </div>
            <button
              onClick={updatePreview}
              className="btn-outline flex items-center space-x-2"
            >
              <EyeIcon className="h-5 w-5" />
              <span>Preview</span>
            </button>
          </div>
        </div>

        <div className="px-4 sm:px-0">
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            {/* Main Form */}
            <div className="lg:col-span-2 space-y-6">
              {/* Platform Selection */}
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Select Platform</h3>
                  <p className="card-subtitle">Choose where you want to publish this content</p>
                </div>
                
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                  {platforms.map((platform) => (
                    <label key={platform.id} className="cursor-pointer">
                      <input
                        type="radio"
                        value={platform.id}
                        className="sr-only"
                        {...register('platform')}
                        onChange={() => setSelectedPlatform(platform.id)}
                      />
                      <div className={`platform-pill ${platform.color} ${
                        watchedFields.platform === platform.id 
                          ? 'ring-4 ring-blue-300 ring-opacity-50' 
                          : 'opacity-70 hover:opacity-100'
                      } transition-all cursor-pointer text-center py-3`}>
                        {platform.name}
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Content Type */}
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Content Type</h3>
                  <p className="card-subtitle">What type of content are you creating?</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                  {contentTypes.map((type) => {
                    const Icon = type.icon;
                    return (
                      <label key={type.id} className="cursor-pointer">
                        <input
                          type="radio"
                          value={type.id}
                          className="sr-only"
                          {...register('content_type')}
                        />
                        <div className={`border-2 rounded-lg p-4 text-center transition-all ${
                          watchedFields.content_type === type.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-300 hover:border-gray-400'
                        }`}>
                          <Icon className="h-8 w-8 mx-auto mb-2 text-gray-600" />
                          <span className="text-sm font-medium text-gray-900">{type.name}</span>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Content Creation */}
              <div className="card">
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                  {/* Title */}
                  <div>
                    <label htmlFor="title" className="form-label">
                      Content Title
                    </label>
                    <input
                      id="title"
                      type="text"
                      className="form-input"
                      placeholder="Give your content a catchy title..."
                      {...register('title', {
                        required: 'Title is required',
                        maxLength: {
                          value: 100,
                          message: 'Title must be less than 100 characters'
                        }
                      })}
                    />
                    {errors.title && (
                      <p className="form-error">{errors.title.message}</p>
                    )}
                  </div>

                  {/* AI Content Generation */}
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center space-x-3 mb-3">
                      <SparklesIcon className="h-6 w-6 text-purple-600" />
                      <h4 className="font-semibold text-gray-900">AI Content Ideas</h4>
                    </div>
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                      {contentIdeas.slice(0, 4).map((idea, index) => (
                        <button
                          key={index}
                          type="button"
                          onClick={() => generateAIContent(idea)}
                          disabled={generatingAI}
                          className="text-left p-3 text-sm bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition-all disabled:opacity-50"
                        >
                          {idea}
                        </button>
                      ))}
                    </div>
                    {generatingAI && (
                      <div className="mt-3 flex items-center space-x-2 text-sm text-blue-600">
                        <LoadingSpinner size="small" text="" />
                        <span>Generating AI content...</span>
                      </div>
                    )}
                  </div>

                  {/* Content Text */}
                  <div>
                    <label htmlFor="text_content" className="form-label flex items-center justify-between">
                      <span>Content</span>
                      <span className="text-sm text-gray-500">
                        {watchedFields.text_content?.length || 0} / {maxLength}
                      </span>
                    </label>
                    <textarea
                      id="text_content"
                      rows={8}
                      className="form-textarea"
                      placeholder="Write your content here..."
                      {...register('text_content', {
                        required: 'Content is required',
                        maxLength: {
                          value: maxLength,
                          message: `Content must be less than ${maxLength} characters for ${currentPlatform?.name}`
                        }
                      })}
                    />
                    {errors.text_content && (
                      <p className="form-error">{errors.text_content.message}</p>
                    )}
                  </div>

                  {/* Hashtags */}
                  <div>
                    <label htmlFor="hashtags" className="form-label flex items-center space-x-2">
                      <HashtagIcon className="h-5 w-5" />
                      <span>Hashtags</span>
                    </label>
                    <input
                      id="hashtags"
                      type="text"
                      className="form-input"
                      placeholder="#motivation #success #entrepreneur"
                      {...register('hashtags')}
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      Separate hashtags with spaces. Start each with #
                    </p>
                  </div>

                  {/* Schedule */}
                  <div>
                    <label htmlFor="scheduled_for" className="form-label flex items-center space-x-2">
                      <CalendarIcon className="h-5 w-5" />
                      <span>Schedule for Later (Optional)</span>
                    </label>
                    <input
                      id="scheduled_for"
                      type="datetime-local"
                      className="form-input"
                      {...register('scheduled_for')}
                    />
                  </div>

                  {/* Submit Buttons */}
                  <div className="flex space-x-4">
                    <button
                      type="submit"
                      disabled={loading}
                      className="btn-primary flex-1 flex items-center justify-center"
                    >
                      {loading ? (
                        <LoadingSpinner size="small" text="" />
                      ) : (
                        'Create Content'
                      )}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        reset();
                        setPreview(null);
                      }}
                      className="btn-secondary"
                    >
                      Clear
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Preview */}
              {preview && (
                <div className="card">
                  <div className="card-header">
                    <h3 className="card-title">Preview</h3>
                    <span className={`platform-pill ${currentPlatform?.color} text-xs`}>
                      {currentPlatform?.name}
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    {preview.title && (
                      <h4 className="font-semibold text-gray-900">{preview.title}</h4>
                    )}
                    
                    <div className="text-gray-700 whitespace-pre-wrap text-sm">
                      {preview.content}
                    </div>
                    
                    {preview.hashtags.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {preview.hashtags.map((tag, index) => (
                          <span key={index} className="text-blue-600 text-sm">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Quick Tips */}
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Content Tips</h3>
                </div>
                
                <div className="space-y-3 text-sm">
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-gray-700">
                      Use the first sentence to grab attention with a hook
                    </p>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-gray-700">
                      Include a call-to-action to encourage engagement
                    </p>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-gray-700">
                      Use relevant hashtags to increase discoverability
                    </p>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-gray-700">
                      Post at optimal times for your audience
                    </p>
                  </div>
                </div>
              </div>

              {/* Platform Guidelines */}
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">
                    {currentPlatform?.name} Guidelines
                  </h3>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Character limit:</span>
                    <span className="font-medium">{maxLength.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Optimal hashtags:</span>
                    <span className="font-medium">
                      {watchedFields.platform === 'instagram' ? '5-10' : 
                       watchedFields.platform === 'twitter' ? '1-3' : 
                       watchedFields.platform === 'linkedin' ? '3-5' : '3-10'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Best posting time:</span>
                    <span className="font-medium">
                      {watchedFields.platform === 'instagram' ? '6-9 PM' :
                       watchedFields.platform === 'linkedin' ? '8-10 AM' :
                       watchedFields.platform === 'tiktok' ? '6-10 PM' : '12-3 PM'}
                    </span>
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