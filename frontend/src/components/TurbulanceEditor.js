import React, { useState } from 'react';

const TurbulanceEditor = ({ onExecute, isLoading = false }) => {
    const [script, setScript] = useState('');
    const [protocolName, setProtocolName] = useState('');

    // Default Turbulance template
    const defaultTemplate = `proposition MyResearchHypothesis:
    motion Hypothesis("Your scientific hypothesis here")
    
    sources:
        local("data/your_dataset.csv")
        domain_expert("your_field")
    
    within experiment:
        given sample_size > 20:
            item analysis = pipeline_stage("domain_knowledge", {
                expert_models: ["sprint_expert", "biomechanics_expert"],
                focus: "research_area"
            })
            item optimization = pipeline_stage("reasoning_optimization", {
                objective: "your_optimization_goal"
            })
            ensure statistical_significance(analysis.results) < 0.05

funxn execute_research():
    return complete_analysis()`;

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (!script.trim()) {
            alert('Please enter a Turbulance research protocol');
            return;
        }

        const turbulanceData = {
            script: script.trim(),
            protocolName: protocolName.trim() || 'UnnamedProtocol',
            executionMode: 'research_protocol'
        };

        onExecute(turbulanceData);
    };

    const loadTemplate = () => {
        setScript(defaultTemplate);
        setProtocolName('ExampleResearch');
    };

    const clearEditor = () => {
        setScript('');
        setProtocolName('');
    };

    return (
        <div className="w-full max-w-4xl mx-auto">
            <div className="mb-4">
                <label htmlFor="protocolName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Research Protocol Name
                </label>
                <input
                    type="text"
                    id="protocolName"
                    value={protocolName}
                    onChange={(e) => setProtocolName(e.target.value)}
                    placeholder="Enter protocol name (e.g., SprintOptimization)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    disabled={isLoading}
                />
            </div>

            <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                    <label htmlFor="turbulanceScript" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Turbulance Research Protocol
                    </label>
                    <div className="space-x-2">
                        <button
                            type="button"
                            onClick={loadTemplate}
                            className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                            disabled={isLoading}
                        >
                            Load Template
                        </button>
                        <button
                            type="button"
                            onClick={clearEditor}
                            className="text-xs px-2 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:opacity-50"
                            disabled={isLoading}
                        >
                            Clear
                        </button>
                    </div>
                </div>
                
                <textarea
                    id="turbulanceScript"
                    value={script}
                    onChange={(e) => setScript(e.target.value)}
                    placeholder="Write your Turbulance research protocol here..."
                    rows={20}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary font-mono text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    disabled={isLoading}
                />
            </div>

            <div className="mb-4 text-xs text-gray-600 dark:text-gray-400">
                <p className="mb-1">
                    <strong>Tip:</strong> Use pipeline_stage() to access Four-Sided Triangle's 8-stage pipeline
                </p>
                <p className="mb-1">
                    <strong>Available stages:</strong> query_processor, semantic_atdb, domain_knowledge, reasoning_optimization, 
                    solution_generation, response_scoring, response_comparison, threshold_verification
                </p>
                <p>
                    <strong>Expert models:</strong> sprint_expert, biomechanics_expert, endocrinology_expert, machine_learning_expert
                </p>
            </div>

            <form onSubmit={handleSubmit}>
                <button
                    type="submit"
                    disabled={isLoading || !script.trim()}
                    className="w-full bg-primary text-white py-3 px-6 rounded-md font-semibold hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isLoading ? 'Executing Research Protocol...' : 'Execute Research Protocol'}
                </button>
            </form>

            <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
                <p>
                    Your Turbulance script will be compiled and executed through Four-Sided Triangle's metacognitive orchestrator.
                    The system will automatically generate .fs (visualization), .ghd (dependencies), and .hre (decision memory) files.
                </p>
            </div>
        </div>
    );
};

export default TurbulanceEditor; 