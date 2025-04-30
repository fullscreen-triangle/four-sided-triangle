'use client';
import dynamic from 'next/dynamic';
import { useState, Suspense, useEffect } from 'react';
import Head from 'next/head';
import Layout from '@/components/Layout';
import AnimatedText from '@/components/AnimatedText';
import Loader from '@/components/Loader';
import SearchBar from '@/components/query/SearchBar';
import ResultComponent from '@/components/result/ResultComponent';
import TransitionEffect from "@/components/TransitionEffect";
import ErrorBoundary from '@/components/ErrorBoundary';
import { useBreakpoint } from '@/utils/responsive';

// Dynamic import the Desk component without a redundant loader
const Desk = dynamic(
    () => import('@/components/Desk'),
    {
        ssr: false,
        loading: () => <div className="w-full h-full flex items-center justify-center">Loading desk...</div>
    }
);

export default function Home() {
    // State for search query and results
    const [query, setQuery] = useState('');
    const [results, setResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [loadingProgress, setLoadingProgress] = useState(0);

    // Handle search submissions
    const handleSearch = async (searchData) => {
        if (!searchData || !searchData.text) {
            setError('Please enter a search query');
            return;
        }

        // Clear any existing error
        setError(null);

        // Set loading state
        setIsLoading(true);
        setLoadingProgress(0.3); // Start at 30%

        // Validate search query format
        const query = searchData.text.trim();
        if (!query || query.length < 3) {
            setError('Search query must be at least 3 characters');
            setIsLoading(false);
            return;
        }

        try {
            // Prepare request body
            const requestBody = {
                query: searchData.text,
                highlightedTerms: searchData.highlightedTerms || [],
                researchContext: searchData.researchContext || 'research',
                testMode: searchData.testMode !== undefined ? searchData.testMode : true // Default to test mode
            };

            // Store the query for display
            setQuery(searchData);
            
            // Simulate progress
            setLoadingProgress(0.5); // Update to 50%

            // Use the new unified search endpoint
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            setLoadingProgress(0.8); // Update to 80%

            const resultData = await response.json();
            
            if (!response.ok) {
                throw new Error(resultData.error || 'Failed to get search results');
            } else {
                setResults(resultData);
            }
            
            setLoadingProgress(1); // Complete loading
            setTimeout(() => {
                setIsLoading(false);
            }, 500); // Short delay to show completed loader
        } catch (err) {
            console.error('Search error:', err);
            setError(err.message || 'An error occurred while processing your search');
            setIsLoading(false);
            setLoadingProgress(0);
        }
    };

    // Reset search to go back to home
    const resetSearch = () => {
        setQuery('');
        setResults(null);
        setError(null);
    };

    return (
        <>
            <Head>
                <title>Four Sided Triangle</title>
                <meta name="description" content="Fullscreen Triangle Domain Expert LLM" />
            </Head>
            <TransitionEffect />

            <article className="w-full flex items-center justify-center">
                <Layout className="pt-0">
                    {isLoading ? (
                        <div className="w-full h-[600px] flex items-center justify-center">
                            <Loader isLoading={true} progress={loadingProgress} />
                        </div>
                    ) : results ? (
                        <div className="w-full">
                            <div className="mb-8">
                                <button
                                    onClick={resetSearch}
                                    className="flex items-center text-primary-dark dark:text-primary hover:underline"
                                >
                                    <span className="mr-2">←</span> Back to Search
                                </button>
                            </div>
                            
                            {/* Display results using the ResultComponent with ErrorBoundary */}
                            <ErrorBoundary>
                                <ResultComponent interpretationResponse={results.interpretationResponse} />
                            </ErrorBoundary>
                        </div>
                    ) : (
                        <div className="flex w-full items-start justify-between md:flex-col">
                            <div className="w-1/2 h-[500px] relative block md:w-full md:h-[400px] sm:h-[300px] xs:h-[250px] overflow-hidden">
                                <Desk />
                            </div>
                            <div className="flex w-1/2 flex-col items-center self-center lg:w-full lg:text-center md:mt-8">

                                <AnimatedText
                                    text="Federated retrieval augmentation"
                                    className="!text-left !text-4xl xl:!text-5xl lg:!text-center lg:!text-6xl md:!text-5xl sm:!text-3xl mt-5 antialiased"
                                />

                                <p className="my-4 text-base text-yellow-600 font-medium md:text-sm sm:!text-xs antialiased mix-blend-normal bg-transparent">
                                    Gain deep insight on personal health and activity metrics through domain expert AI models and comparisons with established models. Know where you stand.
                                </p>
                                <div className="mt-2 flex items-center self-start lg:self-center">
                                    {/* The search bar is supposed to be here */}
                                    <SearchBar onSearch={handleSearch} />
                                </div>
                                {error && (
                                    <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
                                        {error}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </Layout>
            </article>
        </>
    );
}
