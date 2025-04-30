import React from 'react';
import Layout from '@/components/Layout';
import { FaWifi, FaSync } from 'react-icons/fa';
import Head from 'next/head';
import TransitionEffect from "@/components/TransitionEffect";

/**
 * Offline page displayed when user has no internet connection
 * but has previously visited the site (service worker active)
 */
const OfflinePage = () => {
  const handleRefresh = () => {
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
  };

  return (
    <>
      <Head>
        <title>Offline | Four Sided Triangle</title>
        <meta name="description" content="You are currently offline. Please check your connection." />
      </Head>
      <TransitionEffect />

      <article className="w-full flex items-center justify-center">
        <Layout className="pt-0">
          <div className="flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="p-6 bg-light/10 dark:bg-dark/30 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 max-w-md w-full">
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mb-6">
                  <FaWifi className="text-blue-600 dark:text-blue-300 text-4xl" />
                </div>
                
                <h1 className="text-2xl font-bold text-dark dark:text-light mb-2">
                  You're Offline
                </h1>
                
                <p className="text-gray-600 dark:text-gray-400 mb-8">
                  It looks like you're not connected to the internet. 
                  Some features and content may be unavailable until you're back online.
                </p>
                
                <div className="space-y-4 w-full">
                  <button
                    onClick={handleRefresh}
                    className="w-full flex items-center justify-center px-4 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors"
                  >
                    <FaSync className="mr-2" /> Check Connection
                  </button>
                  
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    <p>You still have access to previously visited pages</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Layout>
      </article>
    </>
  );
};

export default OfflinePage;
