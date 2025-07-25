import React from 'react';

export default function LoadingSpinner({ size = 'default', text = 'Loading...' }) {
  const sizeClasses = {
    small: 'h-4 w-4',
    default: 'h-8 w-8',
    large: 'h-12 w-12',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`loading-spinner ${sizeClasses[size]} border-blue-600`}></div>
      {text && (
        <p className="mt-2 text-sm text-gray-600 animate-pulse">
          {text}
        </p>
      )}
    </div>
  );
}

// Full screen loading component
export function FullScreenLoader({ text = 'Loading...' }) {
  return (
    <div className="fixed inset-0 bg-white bg-opacity-90 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="text-center">
        <div className="h-12 w-12 loading-spinner border-blue-600 mx-auto"></div>
        <p className="mt-4 text-lg font-medium text-gray-700 animate-pulse">
          {text}
        </p>
      </div>
    </div>
  );
}