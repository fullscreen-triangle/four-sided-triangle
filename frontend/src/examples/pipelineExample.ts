/**
 * RAG Pipeline Usage Example
 * 
 * This file demonstrates how to use the RAG pipeline to process a query.
 */

import { RAGPipeline } from '../components/pipeline';
import { UserContext, ExpertiseLevel } from '../types/userContext';

async function runPipelineExample() {
  try {
    // Initialize the pipeline
    const pipeline = new RAGPipeline();
    
    // Sample user query
    const query = "How does muscle fiber composition affect sprint performance?";
    
    // User context (expertise level can be 'beginner', 'intermediate', 'expert', or 'general')
    const userContext: UserContext = {
      expertiseLevel: 'intermediate'
    };
    
    // Process options
    const options = {
      modelingOptions: {
        include_visualization: true,
        validation_level: 'detailed'
      },
      interpreterOptions: {
        includeTechnicalDetails: true,
        formatStyle: 'educational'
      }
    };
    
    console.log("Processing query:", query);
    
    // Run the full pipeline
    const result = await pipeline.process(query, userContext, options);
    
    // Log the results
    console.log("Pipeline processing complete:");
    console.log(`- Processing time: ${result.processingTime.total}ms`);
    console.log(`  - Modeling: ${result.processingTime.modeling}ms`);
    console.log(`  - Solving: ${result.processingTime.solving}ms`);
    console.log(`  - Interpreting: ${result.processingTime.interpreting}ms`);
    
    // Log key results
    console.log("\nModel:");
    console.log(`- Entities: ${result.model.entities.length}`);
    console.log(`- Relationships: ${result.model.relationships.length}`);
    console.log(`- Parameters: ${result.model.parameters.length}`);
    console.log(`- Confidence Score: ${result.model.metadata.confidence_score}`);
    
    console.log("\nSolution:");
    console.log(`- Conclusions: ${result.solution.conclusions.length}`);
    console.log(`- Quality Metrics: ${JSON.stringify(result.solution.qualityMetrics)}`);
    
    console.log("\nInterpretation:");
    console.log(`- Key Insights: ${result.interpretation.interpretedSolution.keyInsights.length}`);
    
    // Handle potentially undefined followUpSuggestions
    const followUpCount = result.interpretation.interpretedSolution.followUpSuggestions?.length || 0;
    console.log(`- Follow-up Suggestions: ${followUpCount}`);
    console.log(`- Quality Metrics: ${JSON.stringify(result.interpretation.qualityMetrics)}`);
    
    // Example of adapting to a different expertise level
    console.log("\nAdapting interpretation for a beginner...");
    const beginnerInterpretation = await pipeline.adaptInterpretation(
      result.interpretation,
      'beginner' as ExpertiseLevel
    );
    
    console.log("Adaptation complete:");
    console.log(`- Original explanation length: ${result.interpretation.interpretedSolution.userFriendlyExplanation.length}`);
    console.log(`- Beginner explanation length: ${beginnerInterpretation.interpretedSolution.userFriendlyExplanation.length}`);
    
    // Example of generating additional follow-up suggestions
    console.log("\nGenerating additional follow-up suggestions...");
    const additionalFollowUps = await pipeline.generateFollowUps(
      result.interpretation,
      userContext
    );
    
    console.log(`Generated ${additionalFollowUps.length} additional follow-up suggestions.`);
    
    return {
      originalResult: result,
      beginnerInterpretation,
      additionalFollowUps
    };
  } catch (error) {
    console.error("Error running pipeline example:", error);
    throw error;
  }
}

// Run the example if this file is executed directly
if (require.main === module) {
  runPipelineExample()
    .then(() => {
      console.log("Example completed successfully!");
    })
    .catch((error) => {
      console.error("Example failed:", error);
      process.exit(1);
    });
}

export default runPipelineExample; 