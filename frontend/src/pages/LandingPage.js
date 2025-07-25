import React from 'react';
import { Link } from 'react-router-dom';
import { 
  SparklesIcon, 
  RocketLaunchIcon, 
  MicrophoneIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  CheckCircleIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const features = [
  {
    name: 'AI Success Coaching',
    description: 'Personal AI coach that guides you to social media success with proven strategies.',
    icon: SparklesIcon,
    color: 'text-blue-600'
  },
  {
    name: 'Voice Control',
    description: 'Control everything with your voice - from content creation to campaign management.',
    icon: MicrophoneIcon,
    color: 'text-purple-600'
  },
  {
    name: 'Viral Content Replication',
    description: 'Analyze and replicate viral content patterns adapted to your niche.',
    icon: RocketLaunchIcon,
    color: 'text-green-600'
  },
  {
    name: 'Multi-Product Affiliate Marketing',
    description: 'Automate promotion of multiple affiliate products simultaneously.',
    icon: CurrencyDollarIcon,
    color: 'text-yellow-600'
  },
  {
    name: 'Advanced Analytics',
    description: 'Track your success with comprehensive analytics and growth predictions.',
    icon: ChartBarIcon,
    color: 'text-red-600'
  },
  {
    name: 'Multi-Platform Management',
    description: 'Manage TikTok, Instagram, LinkedIn, YouTube, Twitter, and Facebook from one place.',
    icon: UserGroupIcon,
    color: 'text-indigo-600'
  }
];

const benefits = [
  'Zero technical knowledge required',
  '99% success rate with AI coaching',
  'Cost-optimized AI (70% free models)',
  'Multi-platform automation',
  'Revenue generation guarantee',
  '24/7 voice-controlled operation'
];

const testimonials = [
  {
    name: 'Sarah Johnson',
    role: 'Content Creator',
    content: 'From 0 to 100K followers in 3 months! The AI coaching and viral content replication is incredible.',
    avatar: 'SJ'
  },
  {
    name: 'Mike Chen',
    role: 'Affiliate Marketer',
    content: 'My affiliate revenue increased by 400% using the multi-product automation. Best investment ever!',
    avatar: 'MC'
  },
  {
    name: 'Lisa Rodriguez',
    role: 'Business Owner',
    content: 'The voice control feature saves me hours daily. I literally run my social media while driving!',
    avatar: 'LR'
  }
];

export default function LandingPage() {
  return (
    <div className="bg-white">
      {/* Header */}
      <header className="absolute inset-x-0 top-0 z-50">
        <nav className="flex items-center justify-between p-6 lg:px-8">
          <div className="flex lg:flex-1">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">SMA</span>
              </div>
              <span className="ml-2 text-xl font-bold text-gray-900">
                Social Media Automation
              </span>
            </div>
          </div>
          <div className="flex lg:flex-1 lg:justify-end space-x-4">
            <Link
              to="/login"
              className="text-sm font-semibold leading-6 text-gray-900 hover:text-blue-600 transition-colors"
            >
              Log in
            </Link>
            <Link
              to="/register"
              className="btn-primary text-sm"
            >
              Get started
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero section */}
      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
          <div className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-blue-600 to-purple-600 opacity-20 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"></div>
        </div>

        <div className="mx-auto max-w-3xl py-32 sm:py-48 lg:py-56">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Transform Into a{' '}
              <span className="text-gradient">Social Media Success</span>{' '}
              with AI Automation
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              AI-powered platform with success coaching, viral content replication, 
              affiliate marketing automation, and voice control. 
              <strong>Guaranteed success or money back.</strong>
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link to="/register" className="btn-primary text-lg px-8 py-4">
                Start Your Success Journey
                <ArrowRightIcon className="ml-2 h-5 w-5 inline" />
              </Link>
              <a
                href="#features"
                className="text-sm font-semibold leading-6 text-gray-900 hover:text-blue-600"
              >
                Learn more <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>
        </div>

        <div className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]">
          <div className="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-purple-600 to-blue-600 opacity-20 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]"></div>
        </div>
      </div>

      {/* Features section */}
      <div id="features" className="py-24 sm:py-32 bg-gray-50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-base font-semibold leading-7 text-blue-600">Everything you need</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              AI-Powered Social Media Mastery
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Revolutionary features that guarantee your social media success through intelligent automation and AI coaching.
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
              {features.map((feature) => (
                <div key={feature.name} className="flex flex-col">
                  <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                    <feature.icon className={`h-5 w-5 flex-none ${feature.color}`} />
                    {feature.name}
                  </dt>
                  <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                    <p className="flex-auto">{feature.description}</p>
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      {/* Benefits section */}
      <div className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:mx-0">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Why Choose Our Platform?
            </h2>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Join thousands of successful creators who transformed their social media presence with our AI-powered platform.
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <div className="grid max-w-xl grid-cols-1 gap-8 lg:max-w-none lg:grid-cols-2">
              <div className="space-y-6">
                {benefits.map((benefit) => (
                  <div key={benefit} className="flex items-start">
                    <CheckCircleIcon className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
                    <span className="ml-3 text-lg text-gray-700">{benefit}</span>
                  </div>
                ))}
              </div>
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 text-white">
                <h3 className="text-2xl font-bold mb-4">Success Guarantee</h3>
                <p className="text-blue-100 mb-6">
                  We guarantee your success with our AI coaching system. 
                  If you don't see results within 90 days, we'll refund your money.
                </p>
                <ul className="space-y-2 text-blue-100">
                  <li>• 90-day success guarantee</li>
                  <li>• 24/7 AI coaching support</li>
                  <li>• Proven success framework</li>
                  <li>• Money-back guarantee</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Testimonials */}
      <div className="py-24 sm:py-32 bg-gray-50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Success Stories
            </h2>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              See how our platform transformed ordinary people into social media success stories.
            </p>
          </div>
          <div className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-8 lg:mx-0 lg:max-w-none lg:grid-cols-3">
            {testimonials.map((testimonial) => (
              <div key={testimonial.name} className="card">
                <div className="flex items-center space-x-4 mb-4">
                  <div className="h-12 w-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">{testimonial.avatar}</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{testimonial.name}</h3>
                    <p className="text-sm text-gray-600">{testimonial.role}</p>
                  </div>
                </div>
                <p className="text-gray-700 italic">"{testimonial.content}"</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA section */}
      <div className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Ready to Transform Your Social Media Success?
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-gray-600">
              Join thousands of successful creators. Start your AI-powered success journey today with our 90-day guarantee.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link to="/register" className="btn-primary text-lg px-8 py-4">
                Get Started Now
                <ArrowRightIcon className="ml-2 h-5 w-5 inline" />
              </Link>
              <Link to="/login" className="btn-outline">
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">SMA</span>
              </div>
              <span className="ml-2 text-xl font-bold">
                Social Media Automation
              </span>
            </div>
            <p className="text-sm text-gray-400">
              © 2024 Social Media Automation Platform. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}