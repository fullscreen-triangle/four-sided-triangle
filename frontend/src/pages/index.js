'use client';
import dynamic from 'next/dynamic';
import { useState, Suspense, useEffect } from 'react';
import Head from 'next/head';
import Layout from '@/components/Layout';
import AnimatedText from '@/components/AnimatedText';
import Loader from '@/components/Loader';
import TurbulanceEditor from '@/components/TurbulanceEditor';
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
    // State for Turbulance protocol and results
    const [protocol, setProtocol] = useState(null);
    const [results, setResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [loadingProgress, setLoadingProgress] = useState(0);

    // Handle Turbulance protocol execution
    const handleExecuteProtocol = async (turbulanceData) => {
        if (!turbulanceData || !turbulanceData.script) {
            setError('Please enter a Turbulance research protocol');
            return;
        }

        // Clear any existing error
        setError(null);

        // Set loading state
        setIsLoading(true);
        setLoadingProgress(0.3); // Start at 30%

        // Validate Turbulance script format
        const script = turbulanceData.script.trim();
        if (!script || script.length < 20) {
            setError('Turbulance script must be a valid research protocol');
            setIsLoading(false);
            return;
        }

        try {
            // Prepare request body for Turbulance execution
            const requestBody = {
                turbulanceScript: turbulanceData.script,
                protocolName: turbulanceData.protocolName || 'UnnamedProtocol',
                executionMode: 'research_protocol',
                generateAuxiliaryFiles: true // Generate .fs, .ghd, .hre files
            };

            // Store the protocol for display
            setProtocol(turbulanceData);
            
            // Simulate progress
            setLoadingProgress(0.5); // Update to 50%

            // Use the new Turbulance execution endpoint
            const response = await fetch('/api/turbulance/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            setLoadingProgress(0.8); // Update to 80%

            const resultData = await response.json();
            
            if (!response.ok) {
                throw new Error(resultData.error || 'Failed to execute Turbulance protocol');
            } else {
                setResults(resultData);
            }
            
            setLoadingProgress(1); // Complete loading
            setTimeout(() => {
                setIsLoading(false);
            }, 500); // Short delay to show completed loader
        } catch (err) {
            console.error('Turbulance execution error:', err);
            setError(err.message || 'An error occurred while executing your research protocol');
            setIsLoading(false);
            setLoadingProgress(0);
        }
    };

    // Reset protocol execution to go back to home
    const resetProtocol = () => {
        setProtocol(null);
        setResults(null);
        setError(null);
    };

    return (
        <>
            <Head>
                <title>Four Sided Triangle - Turbulance Research Platform</title>
                <meta name="description" content="Execute Turbulance research protocols through Four-Sided Triangle's metacognitive orchestrator" />
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
                                    onClick={resetProtocol}
                                    className="flex items-center text-primary-dark dark:text-primary hover:underline"
                                >
                                    <span className="mr-2">←</span> Back to Turbulance Editor
                                </button>
                            </div>
                            
                            {/* Display results using the ResultComponent with ErrorBoundary */}
                            <ErrorBoundary>
                                <ResultComponent interpretationResponse={results.interpretationResponse} />
                            </ErrorBoundary>
                        </div>
                    ) : (
                        <div className="flex w-full flex-col items-center justify-center">
                            <div className="w-full h-[300px] relative block md:h-[250px] sm:h-[200px] xs:h-[150px] overflow-hidden mb-8">
                                <Desk />
                            </div>
                            <div className="flex w-full flex-col items-center self-center lg:w-full lg:text-center">

                                <AnimatedText
                                    text="Turbulance Research Platform"
                                    className="!text-left !text-4xl xl:!text-5xl lg:!text-center lg:!text-6xl md:!text-5xl sm:!text-3xl mt-5 antialiased"
                                />

                                <p className="my-4 text-base text-yellow-600 font-medium md:text-sm sm:!text-xs antialiased mix-blend-normal bg-transparent">
                                    Execute complete research protocols through Four-Sided Triangle's metacognitive orchestrator. 
                                    Write structured scientific methodology instead of fragmented queries.
                                </p>
                                <div className="mt-8 w-full">
                                    <TurbulanceEditor onExecute={handleExecuteProtocol} isLoading={isLoading} />
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
