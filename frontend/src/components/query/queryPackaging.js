/**
 * Query Packaging Module
 * 
 * Prepares standardized query packages for transfer 
 * to the modeling component
 */

/**
 * Package a processed query with metadata for LLM analysis
 * 
 * @param {Object} options - Query options
 * @param {Object|string} options.query - The processed query text or object
 * @param {string} options.context - The research context
 * @param {Array} options.highlightedTerms - Domain terms highlighted by the user
 * @returns {Object} - The packaged query ready for LLM analysis
 */
export const packageQuery = ({ query, context, highlightedTerms }) => {
  // Get current timestamp for tracking
  const timestamp = new Date().toISOString();
  
  // Extract query text if an object was passed
  let queryText, processedText;
  
  if (typeof query === 'string') {
    queryText = query;
    processedText = query;
  } else if (typeof query === 'object' && query !== null) {
    queryText = query.originalText || query.processedText || query.text || '';
    processedText = query.processedText || query.text || queryText;
  } else {
    queryText = '';
    processedText = '';
  }
  
  // Create the packaged query with all required components
  const packagedQuery = {
    // Query content
    query: queryText,
    processedText: processedText, 
    originalText: queryText,
    
    // Research context and domain terms
    context: context || 'research',
    highlightedTerms: highlightedTerms || [],
    
    // Processing information
    processingSteps: [
      {
        step: 'initial_processing',
        timestamp: timestamp
      },
      {
        step: 'query_packaging',
        timestamp: timestamp
      }
    ],
    
    // Metadata for tracking
    metadata: {
      queryId: generateQueryId(),
      timestamp: timestamp,
      systemVersion: '1.0.0'
    }
  };
  
  return packagedQuery;
};

/**
 * Generate a unique query ID
 * 
 * @returns {string} - A unique ID for the query
 */
const generateQueryId = () => {
  return 'q_' + Date.now() + '_' + Math.random().toString(36).substring(2, 10);
};

/**
 * Get the current user context
 * 
 * @returns {Object} - The user context information
 */
const getUserContext = () => {
  // In a real implementation, this would retrieve user preferences,
  // history, and other relevant information from a user service
  
  return {
    preferredUnits: 'metric',
    expertiseLevel: 'beginner',
    previousQueries: [],
    interests: ['400m sprint', 'biomechanics']
  };
};

/**
 * Get the current session metadata
 * 
 * @returns {Object} - Session metadata
 */
const getSessionMetadata = () => {
  // In a real implementation, this would retrieve information
  // about the current session from a session service
  
  return {
    sessionId: 'sess_' + Date.now(),
    startTime: new Date().toISOString(),
    device: 'web',
    interactionCount: 1
  };
};

/**
 * Get domain-specific context based on the identified subject
 * 
 * @param {string} subject - The key subject identified by the LLM
 * @returns {Object} - Domain-specific context information
 */
const getDomainContext = (subject) => {
  // In a real implementation, this would provide relevant
  // domain-specific context based on the query subject
  
  const domainContextMap = {
    'athlete': {
      relevantMetrics: ['height', 'weight', 'body_fat_percentage', 'muscle_mass'],
      defaultParameters: {
        sport: '400m sprint',
        gender: 'male',
        ageRange: '18-35'
      }
    },
    'body_composition': {
      relevantMetrics: ['segmental_masses', 'segmental_lengths', 'body_fat_distribution'],
      defaultModels: ['Zatsiorsky-Seluyanov', 'Dempster']
    },
    'athletic_performance': {
      relevantMetrics: ['stride_length', 'stride_frequency', 'ground_force', 'power_output'],
      defaultAnalysisTypes: ['biomechanical', 'physiological', 'statistical']
    },
    'general': {
      relevantMetrics: ['basic_anthropometrics', 'performance_metrics'],
      defaultScope: 'comprehensive'
    }
  };
  
  // Return the context for the specific subject, or a default if not found
  return domainContextMap[subject] || domainContextMap['general'];
}; 