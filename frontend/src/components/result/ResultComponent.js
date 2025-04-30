import React, { useState } from 'react';

/**
 * ResultComponent
 * 
 * Renders the final interpretation output from the 7-stage RAG pipeline.
 * Displays the response as readable text paragraphs for human consumption.
 * Includes options to view metacognitive insights and evaluation metrics.
 */
const ResultComponent = ({ pipelineResult }) => {
  const [showDetails, setShowDetails] = useState(false);
  
  // If there's no result, show nothing
  if (!pipelineResult || !pipelineResult.interpretation || !pipelineResult.interpretation.interpretedSolution) {
    return null;
  }

  const { 
    interpretation, 
    evaluation,
    metacognitiveInsights,
    processingTime
  } = pipelineResult;
  
  const { interpretedSolution } = interpretation;
  
  return (
    <div className="w-full max-w-4xl mx-auto bg-light/5 dark:bg-dark/10 rounded-xl p-6 shadow-lg">
      {/* Main explanation section */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-primary-dark dark:text-primary">Results</h2>
        <div className="prose dark:prose-invert prose-sm sm:prose-base lg:prose-lg max-w-none">
          {/* Main explanation - split paragraphs and render */}
          {interpretedSolution.userFriendlyExplanation.split('\n\n').map((paragraph, index) => (
            <p key={index} className="mb-4">{paragraph}</p>
          ))}
        </div>
      </div>
      
      {/* Key insights section */}
      {interpretedSolution.keyInsights && interpretedSolution.keyInsights.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xl font-medium mb-2 text-primary-dark/90 dark:text-primary/90">Key Insights</h3>
          <ul className="list-disc pl-5 space-y-2">
            {interpretedSolution.keyInsights.map((insight, index) => (
              <li key={index} className="text-dark/90 dark:text-light/90">{insight}</li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Sources section - if available */}
      {interpretedSolution.sources && interpretedSolution.sources.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xl font-medium mb-2 text-primary-dark/90 dark:text-primary/90">Sources</h3>
          <ul className="list-disc pl-5 space-y-1 text-sm">
            {interpretedSolution.sources.map((source, index) => (
              <li key={index} className="text-dark/80 dark:text-light/80">
                {source.citation}
                {source.url && (
                  <a 
                    href={source.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="ml-2 text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    [link]
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Follow-up suggestions - if available */}
      {interpretedSolution.followUpSuggestions && interpretedSolution.followUpSuggestions.length > 0 && (
        <div className="mt-8 border-t border-light/10 dark:border-dark/20 pt-4">
          <h3 className="text-lg font-medium mb-2 text-primary-dark/90 dark:text-primary/90">Follow-up Questions</h3>
          <ul className="list-disc pl-5 space-y-1">
            {interpretedSolution.followUpSuggestions.map((suggestion, index) => (
              <li key={index} className="text-dark/90 dark:text-light/90">{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Advanced details toggle */}
      <div className="mt-8 pt-4 border-t border-light/10 dark:border-dark/20">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-blue-600 dark:text-blue-400 hover:underline focus:outline-none"
        >
          {showDetails ? 'Hide advanced details' : 'Show advanced details'}
        </button>
        
        {/* Advanced details panel */}
        {showDetails && (
          <div className="mt-4 text-sm">
            {/* Evaluation metrics */}
            {evaluation && (
              <div className="mb-4 p-3 bg-light/10 dark:bg-dark/20 rounded">
                <h4 className="font-medium mb-2">Response Quality Assessment</h4>
                <div className="grid grid-cols-2 gap-2">
                  <div>Accuracy: {Math.round(evaluation.accuracyScore * 100)}%</div>
                  <div>Completeness: {Math.round(evaluation.completenessScore * 100)}%</div>
                  <div>Relevance: {Math.round(evaluation.relevanceScore * 100)}%</div>
                  <div>Clarity: {Math.round(evaluation.clarityScore * 100)}%</div>
                  <div>Overall quality: {Math.round(evaluation.overallQualityScore * 100)}%</div>
                </div>
                
                {evaluation.improvementSuggestions && evaluation.improvementSuggestions.length > 0 && (
                  <div className="mt-2">
                    <p className="font-medium">Improvement opportunities:</p>
                    <ul className="list-disc pl-5">
                      {evaluation.improvementSuggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            
            {/* Metacognitive insights */}
            {metacognitiveInsights && (
              <div className="mb-4 p-3 bg-light/10 dark:bg-dark/20 rounded">
                <h4 className="font-medium mb-2">System Self-Assessment</h4>
                <div className="grid grid-cols-2 gap-2">
                  <div>Retrieval relevance: {Math.round(metacognitiveInsights.processingQuality.retrievalRelevance * 100)}%</div>
                  <div>Reasoning depth: {Math.round(metacognitiveInsights.processingQuality.reasoningDepth * 100)}%</div>
                  <div>Solution accuracy: {Math.round(metacognitiveInsights.processingQuality.solutionAccuracy * 100)}%</div>
                  <div>Clarity: {Math.round(metacognitiveInsights.processingQuality.interpretationClarity * 100)}%</div>
                  <div>Confidence: {Math.round(metacognitiveInsights.confidenceScore * 100)}%</div>
                </div>
              </div>
            )}
            
            {/* Processing time */}
            {processingTime && (
              <div className="p-3 bg-light/10 dark:bg-dark/20 rounded">
                <h4 className="font-medium mb-2">Processing Times</h4>
                <div className="grid grid-cols-2 gap-2">
                  <div>Query analysis: {processingTime.queryAnalysis}ms</div>
                  <div>Knowledge retrieval: {processingTime.retrieval}ms</div>
                  <div>Modeling: {processingTime.modeling}ms</div>
                  <div>Reasoning: {processingTime.reasoning}ms</div>
                  <div>Solving: {processingTime.solving}ms</div>
                  <div>Interpreting: {processingTime.interpreting}ms</div>
                  <div>Evaluation: {processingTime.evaluation}ms</div>
                  <div className="font-medium">Total time: {processingTime.total}ms</div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultComponent; 