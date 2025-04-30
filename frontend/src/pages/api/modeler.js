import { Configuration, OpenAIApi } from 'openai';
import { rateLimit } from '../../utils/rateLimiter';
import { getSession } from 'next-auth/react';

// Load environment variables
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

// Initialize OpenAI client
const openaiConfig = OPENAI_API_KEY ? new Configuration({ apiKey: OPENAI_API_KEY }) : null;
const openai = openaiConfig ? new OpenAIApi(openaiConfig) : null;

// Rate limiter: 5 requests per minute per IP
const limiter = rateLimit({
  interval: 60 * 1000, // 60 seconds
  uniqueTokenPerInterval: 100, // Max 100 unique IPs per interval
  limit: 5 // 5 requests per interval
});

/**
 * API endpoint for knowledge model generation
 */
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({
      error: 'Method not allowed',
      message: 'Only POST requests are supported'
    });
  }

  // Get user IP for rate limiting
  const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
  
  try {
    // Apply rate limiting
    await limiter.check(res, 10, ip);
    
    // Get user session for authorization
    const session = await getSession({ req });
    
    // Optional: Require authentication
    // if (!session) {
    //   return res.status(401).json({ error: 'Unauthorized', message: 'Authentication required' });
    // }
    
    const { query, intent = 'information', context = {}, parameters = {} } = req.body;

    // Validate request payload
    if (!query) {
      return res.status(400).json({
        error: 'Invalid request',
        message: 'Query is required'
      });
    }

    // Track processing time
    const startTime = Date.now();

    // Process the knowledge model
    const knowledgeModel = await generateKnowledgeModel(query, intent, context, parameters);

    // Calculate processing time in seconds
    const processingTime = (Date.now() - startTime) / 1000;

    // Return the knowledge model
    return res.status(200).json({
      knowledge_model: knowledgeModel,
      metadata: {
        model_id: `model_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`,
        generated_at: new Date().toISOString(),
        intent: intent,
        processing_time: processingTime
      }
    });
  } catch (error) {
    console.error('Modeler API Error:', error);
    
    if (error.code === 'LIMIT_EXCEEDED') {
      return res.status(429).json({
        error: 'Rate limit exceeded',
        message: 'Too many requests, please try again later'
      });
    }
    
    // Handle different error types
    if (error.response) {
      // OpenAI error with response
      return res.status(error.response.status).json({
        error: 'Model generation error',
        message: error.response.data.error.message || 'Error generating knowledge model',
        type: error.response.data.error.type || 'unknown'
      });
    } else {
      // Generic error
      return res.status(500).json({
        error: 'Internal server error',
        message: error.message || 'Unknown error occurred'
      });
    }
  }
}

/**
 * Generate a knowledge model using LLM
 * 
 * @param {string} query - The query text to model
 * @param {string} intent - Query intent
 * @param {Object} context - Query context
 * @param {Object} parameters - Additional parameters
 * @returns {Promise<Object>} - The generated knowledge model
 */
async function generateKnowledgeModel(query, intent, context, parameters) {
  if (!openai) {
    throw new Error('OpenAI client not initialized. Please check API key.');
  }

  // Create system prompt based on intent and parameters
  const systemPrompt = createSystemPrompt(intent, parameters);
  
  // Format the query with context
  const formattedQuery = formatQueryWithContext(query, context);
  
  // Call OpenAI API
  const response = await openai.createChatCompletion({
    model: parameters.model || 'gpt-4',
    messages: [
      {
        role: 'system',
        content: systemPrompt
      },
      {
        role: 'user',
        content: formattedQuery
      }
    ],
    temperature: parameters.temperature || 0.3,
    max_tokens: parameters.max_tokens || 2000,
    response_format: { type: 'json_object' }
  });

  // Parse the response
  const content = response.data.choices[0].message.content;
  let knowledgeModel;
  
  try {
    knowledgeModel = JSON.parse(content);
  } catch (error) {
    console.error('Error parsing LLM response as JSON:', error);
    throw new Error('Failed to parse knowledge model from LLM response');
  }
  
  // Process and validate the model
  return processAndValidateModel(knowledgeModel, intent, parameters);
}

/**
 * Create a system prompt based on intent and parameters
 * 
 * @param {string} intent - Query intent
 * @param {Object} parameters - Additional parameters
 * @returns {string} - System prompt
 */
function createSystemPrompt(intent, parameters) {
  // Base prompt for all intents
  let prompt = `You are a scientific knowledge model generator for the Four Sided Triangle system, specializing in sprint genetics, biomechanics, and athletic performance.

Your task is to analyze the user's query and generate a comprehensive, structured knowledge model in JSON format.`;

  // Intent-specific prompts
  if (intent === 'entity_extraction') {
    prompt += `\n\nFocus on identifying and extracting all domain-relevant entities from the query. For each entity:
1. Determine its type (person, measurement, body_part, performance_metric, genetic_marker, etc.)
2. Extract any attributes or properties mentioned
3. Assign a confidence score based on how clearly it was mentioned
4. Provide a brief description`;
  } else if (intent === 'relationship_mapping') {
    prompt += `\n\nFocus on identifying relationships between entities in the query:
1. Extract all entities first
2. Determine how they relate to each other
3. Map out causal, correlative, or compositional relationships
4. Identify the strength and direction of relationships`;
  } else if (intent === 'computational') {
    prompt += `\n\nFocus on computational aspects of the query:
1. Identify measurements, variables, and parameters
2. Determine what needs to be calculated
3. Extract any constraints or conditions
4. Generate a computational approach with relevant formulas`;
  } else {
    // Default informational intent
    prompt += `\n\nCreate a comprehensive knowledge model that captures:
1. Key entities and concepts
2. Their relationships
3. Relevant scientific principles
4. Domain-specific metrics and measurements`;
  }

  // Add format specifications
  prompt += `\n\nReturn your response as a JSON object with the following structure:
{
  "entities": [
    {
      "id": "string",
      "name": "string",
      "type": "string",
      "description": "string",
      "attributes": ["string"],
      "confidence": number
    }
  ],
  "relationships": [
    {
      "id": "string",
      "source": "entity_id",
      "target": "entity_id",
      "type": "string",
      "description": "string",
      "strength": number
    }
  ],
  "concepts": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "related_entities": ["entity_id"]
    }
  ],
  "metrics": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "unit": "string",
      "applicable_entities": ["entity_id"]
    }
  ]
}`;

  // Add any parameter-specific instructions
  if (parameters.extraction_focus) {
    prompt += `\n\nFocus specifically on extracting ${parameters.extraction_focus} with maximum detail.`;
  }
  
  if (parameters.detailed_attributes) {
    prompt += `\n\nProvide highly detailed attributes for each entity.`;
  }

  return prompt;
}

/**
 * Format query with context information
 * 
 * @param {string} query - The original query
 * @param {Object} context - Context information
 * @returns {string} - Formatted query with context
 */
function formatQueryWithContext(query, context) {
  let formattedQuery = `Query: ${query}\n\n`;
  
  if (context && Object.keys(context).length > 0) {
    formattedQuery += 'Context Information:\n';
    
    Object.entries(context).forEach(([key, value]) => {
      formattedQuery += `- ${key.replace(/_/g, ' ')}: ${JSON.stringify(value)}\n`;
    });
  }
  
  return formattedQuery;
}

/**
 * Process and validate the model generated by the LLM
 * 
 * @param {Object} model - The raw model from LLM
 * @param {string} intent - Query intent
 * @param {Object} parameters - Additional parameters
 * @returns {Object} - Processed and validated model
 */
function processAndValidateModel(model, intent, parameters) {
  // Ensure all expected sections exist
  const processedModel = {
    entities: Array.isArray(model.entities) ? model.entities : [],
    relationships: Array.isArray(model.relationships) ? model.relationships : [],
    concepts: Array.isArray(model.concepts) ? model.concepts : [],
    metrics: Array.isArray(model.metrics) ? model.metrics : []
  };
  
  // Add any missing IDs
  processedModel.entities = processedModel.entities.map(entity => ({
    ...entity,
    id: entity.id || `entity_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`
  }));
  
  processedModel.relationships = processedModel.relationships.map(rel => ({
    ...rel,
    id: rel.id || `rel_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`
  }));
  
  processedModel.concepts = processedModel.concepts.map(concept => ({
    ...concept,
    id: concept.id || `concept_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`
  }));
  
  processedModel.metrics = processedModel.metrics.map(metric => ({
    ...metric,
    id: metric.id || `metric_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`
  }));
  
  return processedModel;
} 