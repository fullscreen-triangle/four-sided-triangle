/**
 * Model Validation Module
 * 
 * Handles validation of queries before they are processed for modeling.
 * Ensures the query meets minimum requirements for effective modeling.
 */

/**
 * Validate a query for modeling.
 * 
 * @param {Object} options - Validation options
 * @param {string} options.query - The query text to validate
 * @param {string} [options.context="default"] - The modeling context
 * @returns {Promise<boolean>} - True if the query is valid for modeling
 */
export const validateModel = async ({ query, context = "default" }) => {
  // Basic validation checks
  if (!query) {
    console.error('Query is required for modeling');
    return false;
  }
  
  if (query.trim().length < 10) {
    console.error('Query is too short for effective modeling');
    return false;
  }
  
  // Check for minimum content requirements
  const contentChecks = [
    // Check if query contains potential entities
    {
      check: /\b[A-Z][a-z]+\b|\b[a-z]+\s+[a-z]+\b/i.test(query),
      error: 'Query does not contain identifiable entities'
    },
    // Check if query contains potential relationships
    {
      check: /\b(is|are|has|have|affects|causes|relates|connects|impacts)\b/i.test(query),
      error: 'Query does not describe relationships between entities'
    },
    // Check if query implies a request for structured knowledge
    {
      check: /\b(model|relationship|connection|parameter|variable|factor|influence|dependency|formula|equation)\b/i.test(query),
      requirement: context !== 'simplified' // Only apply this check for non-simplified contexts
    }
  ];
  
  // For simplified context, we're less strict with requirements
  const relevantChecks = contentChecks.filter(check => 
    check.requirement === undefined || check.requirement
  );
  
  // If any check fails, log the first error and return false
  for (const { check, error } of relevantChecks) {
    if (!check && error) {
      console.error(error);
      return false;
    }
  }
  
  // Additional context-specific validation
  if (context === 'mathematical') {
    // For mathematical context, we expect terms related to calculation or formulas
    const hasMathematicalTerms = /\b(calculate|formula|equation|compute|value|variable|parameter|function)\b/i.test(query);
    
    if (!hasMathematicalTerms) {
      console.error('Query does not contain mathematical terms required for mathematical modeling');
      return false;
    }
  }
  
  return true;
};

/**
 * Calculate modeling suitability score.
 * 
 * @param {string} query - The query text to evaluate
 * @returns {Object} - An object containing the score and reasoning
 */
export const calculateModelingSuitabilityScore = (query) => {
  if (!query) {
    return { score: 0, reasoning: 'Empty query' };
  }
  
  let score = 0;
  const reasons = [];
  
  // Check for query length
  if (query.length > 20) score += 10;
  if (query.length > 50) score += 10;
  if (query.length > 100) score += 10;
  
  // Check for potential entities (nouns)
  const potentialEntities = query.match(/\b[A-Z][a-z]+\b|\b[a-z]+\s+[a-z]+\b/gi) || [];
  score += Math.min(potentialEntities.length * 5, 20);
  
  if (potentialEntities.length > 0) {
    reasons.push(`Contains ${potentialEntities.length} potential entities`);
  }
  
  // Check for relationship terms
  const relationshipTerms = [
    'is', 'are', 'has', 'have', 'affects', 'causes', 'relates', 
    'connects', 'impacts', 'influences', 'depends', 'correlates'
  ];
  
  const foundRelationshipTerms = relationshipTerms.filter(term => 
    new RegExp(`\\b${term}\\b`, 'i').test(query)
  );
  
  score += Math.min(foundRelationshipTerms.length * 5, 20);
  
  if (foundRelationshipTerms.length > 0) {
    reasons.push(`Contains ${foundRelationshipTerms.length} relationship terms`);
  }
  
  // Check for modeling-specific terms
  const modelingTerms = [
    'model', 'relationship', 'connection', 'parameter', 'variable',
    'factor', 'influence', 'dependency', 'formula', 'equation'
  ];
  
  const foundModelingTerms = modelingTerms.filter(term => 
    new RegExp(`\\b${term}\\b`, 'i').test(query)
  );
  
  score += Math.min(foundModelingTerms.length * 7, 28);
  
  if (foundModelingTerms.length > 0) {
    reasons.push(`Contains ${foundModelingTerms.length} modeling-specific terms`);
  }
  
  // Cap the score at 100
  score = Math.min(score, 100);
  
  return {
    score,
    reasoning: reasons.join('. ')
  };
}; 