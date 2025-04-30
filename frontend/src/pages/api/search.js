/**
 * API handler for search queries
 * This route coordinates the full pipeline:
 * 1. Query reception and preprocessing
 * 2. Modeling in domain context
 * 3. Solution computation
 * 4. Interpretation of results
 */
import axios from 'axios';

// Endpoint configuration
const API_BASE_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';
const QUERY_ENDPOINT = `${API_BASE_URL}/api/query`;
const MODEL_ENDPOINT = `${API_BASE_URL}/api/modeler`;
const SOLVER_ENDPOINT = `${API_BASE_URL}/api/solver/compute`;
const INTERPRETER_ENDPOINT = `${API_BASE_URL}/api/interpreter/interpret`;

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { query, highlightedTerms, researchContext, testMode } = req.body;
    const startTime = Date.now();

    console.log('Processing query:', query);
    console.log('Research context:', researchContext);
    console.log('Test mode:', testMode ? 'enabled' : 'disabled');

    // 1. Query processing
    const queryPackage = await processQuery(query, highlightedTerms, researchContext);
    
    // 2. Modeling in domain context
    const knowledgeModel = await createModel(queryPackage);
    
    // 3. Computation
    const solutionPackage = await solveProblem(knowledgeModel, {
      contextLevel: researchContext || 'research',
      testMode: testMode
    });
    
    // 4. Interpretation
    const interpretationResponse = await interpretSolution(solutionPackage, queryPackage);
    
    // Calculate total processing time
    const processingTime = (Date.now() - startTime) / 1000;
    
    // Prepare final response
    const response = {
      queryInfo: {
        originalText: query,
        processedText: queryPackage.query || query,
        context: researchContext,
        timestamp: new Date().toISOString()
      },
      interpretationResponse,
      debug: {
        pipelineStages: ["query", "model", "solve", "interpret", "result"],
        executionTime: {
          total: processingTime
        }
      }
    };

    return res.status(200).json(response);
  } catch (error) {
    console.error('Search API error:', error);
    return res.status(500).json({
      error: 'An error occurred while processing your request',
      details: error.message,
      path: req.url
    });
  }
}

/**
 * Process the raw query
 */
async function processQuery(query, highlightedTerms, context) {
  try {
    const response = await axios.post(QUERY_ENDPOINT, {
      query,
      highlightedTerms: highlightedTerms || [],
      context: context || 'research'
    });
    
    return response.data;
  } catch (error) {
    console.error('Error in query processing:', error);
    throw new Error('Failed to process query: ' + error.message);
  }
}

/**
 * Create a knowledge model from the query package
 */
async function createModel(queryPackage) {
  try {
    const response = await axios.post(MODEL_ENDPOINT, queryPackage);
    return response.data;
  } catch (error) {
    console.error('Error in model creation:', error);
    throw new Error('Failed to create knowledge model: ' + error.message);
  }
}

/**
 * Solve the problem using the knowledge model
 */
async function solveProblem(knowledgeModel, parameters) {
  try {
    const response = await axios.post(SOLVER_ENDPOINT, {
      query_data: knowledgeModel,
      parameters
    });
    
    return response.data.result;
  } catch (error) {
    console.error('Error in problem solving:', error);
    throw new Error('Failed to solve problem: ' + error.message);
  }
}

/**
 * Interpret the solution for user presentation
 */
async function interpretSolution(solutionPackage, queryPackage) {
  try {
    const response = await axios.post(INTERPRETER_ENDPOINT, {
      solution: solutionPackage,
      query: queryPackage
    });
    
    return response.data;
  } catch (error) {
    console.error('Error in solution interpretation:', error);
    throw new Error('Failed to interpret solution: ' + error.message);
  }
} 