import React, { Component } from 'react';
import { FaBug, FaRedoAlt, FaHome } from 'react-icons/fa';
import Link from 'next/link';

/**
 * ErrorBoundary component to catch JavaScript errors in child component tree
 * and display a fallback UI instead of crashing the whole application
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // You can log the error to an error reporting service here
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
    this.setState({ errorInfo });
    
    // Optional: Send error to error tracking service like Sentry
    // if (typeof window !== 'undefined' && window.Sentry) {
    //   window.Sentry.captureException(error);
    // }
  }

  handleReset = () => {
    // Reset the error boundary state
    this.setState({ 
      hasError: false,
      error: null,
      errorInfo: null
    });
  }

  render() {
    const { fallback, children } = this.props;
    const { hasError, error, errorInfo } = this.state;

    if (hasError) {
      // If a custom fallback is provided, use it
      if (fallback) {
        return React.cloneElement(fallback, { 
          error,
          errorInfo,
          reset: this.handleReset
        });
      }

      // Otherwise use the default fallback UI
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8 rounded-lg bg-light/10 dark:bg-dark/30 border border-red-300 dark:border-red-700">
          <div className="flex items-center justify-center w-20 h-20 rounded-full bg-red-100 dark:bg-red-900 mb-6">
            <FaBug className="text-red-500 dark:text-red-300 text-3xl" />
          </div>
          
          <h2 className="text-xl font-bold text-dark dark:text-light mb-2">Something went wrong</h2>
          
          <p className="text-center text-gray-600 dark:text-gray-400 mb-6 max-w-lg">
            We're sorry, but there was an error rendering this component. The rest of the application should still work.
          </p>
          
          {process.env.NODE_ENV !== 'production' && (
            <div className="w-full max-w-lg bg-gray-100 dark:bg-gray-800 rounded p-4 mb-6 overflow-auto text-xs">
              <details>
                <summary className="cursor-pointer font-medium mb-2">Error details (developers only)</summary>
                <p className="text-red-600 dark:text-red-400 mb-2">{error?.toString()}</p>
                {errorInfo && (
                  <pre className="whitespace-pre-wrap">
                    {errorInfo.componentStack}
                  </pre>
                )}
              </details>
            </div>
          )}
          
          <div className="flex space-x-4">
            <button
              onClick={this.handleReset}
              className="flex items-center justify-center px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors"
            >
              <FaRedoAlt className="mr-2" /> Try Again
            </button>
            
            <Link href="/" legacyBehavior>
              <a className="flex items-center justify-center px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">
                <FaHome className="mr-2" /> Go Home
              </a>
            </Link>
          </div>
        </div>
      );
    }

    // When there's no error, render children normally
    return children;
  }
}

/**
 * Component-specific error boundary that wraps a single component
 */
export const withErrorBoundary = (Component, fallback) => {
  return (props) => (
    <ErrorBoundary fallback={fallback}>
      <Component {...props} />
    </ErrorBoundary>
  );
};

export default ErrorBoundary;
