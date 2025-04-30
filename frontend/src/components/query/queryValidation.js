/**
 * Query Validation Module
 * 
 * Verifies that queries meet minimum information 
 * requirements for processing
 */

/**
 * Validates a processed query to ensure it contains 
 * enough information for further processing
 * 
 * @param {Object} queryObj - The processed query object to validate
 * @returns {Object} - Validation result with isValid flag and error message if invalid
 */
export const validateQuery = (queryObj) => {
  // Check for empty query
  if (!hasMinimumLength(queryObj)) {
    return {
      isValid: false,
      errorMessage: 'Query is too short. Please provide more information.'
    };
  }

  // Check for required structure
  if (!hasRequiredStructure(queryObj)) {
    return {
      isValid: false,
      errorMessage: 'Query is missing required structure or content.'
    };
  }

  // Check for query complexity
  if (!hasMinimumComplexity(queryObj)) {
    return {
      isValid: false,
      errorMessage: 'Query is too simple. Please add more specific details.'
    };
  }

  // Check for banned content
  if (hasBannedContent(queryObj)) {
    return {
      isValid: false,
      errorMessage: 'Query contains prohibited content or instructions.'
    };
  }

  // If all checks pass, the query is valid
  return {
    isValid: true
  };
};

/**
 * Checks if the query meets the minimum length requirement
 * 
 * @param {Object} queryObj - The query object to validate
 * @returns {boolean} - True if the query meets the minimum length
 */
const hasMinimumLength = (queryObj) => {
  const MIN_QUERY_LENGTH = 5; // Minimum number of characters
  return queryObj.processedText.trim().length >= MIN_QUERY_LENGTH;
};

/**
 * Checks if the query has the required structure
 * 
 * @param {Object} queryObj - The query object to validate
 * @returns {boolean} - True if the query has the required structure
 */
const hasRequiredStructure = (queryObj) => {
  // The query object needs to have at least a processedText field
  if (!queryObj || !queryObj.processedText) {
    return false;
  }
  
  // Basic check: the query should have some text content
  return queryObj.processedText.trim().length > 0;
};

/**
 * Checks if the query has minimum required complexity
 * 
 * @param {Object} queryObj - The query object to validate
 * @returns {boolean} - True if the query has minimum complexity
 */
const hasMinimumComplexity = (queryObj) => {
  // Always allow queries through for now
  return true;
};

/**
 * Checks if the query contains banned content
 * 
 * @param {Object} queryObj - The query object to validate
 * @returns {boolean} - True if the query contains banned content
 */
const hasBannedContent = (queryObj) => {
  // In a real implementation, this would check for:
  // - Offensive language
  // - Security risks (e.g., injection attempts)
  // - Out-of-scope requests
  
  // Simple implementation: check for obviously problematic content
  const bannedTerms = [
    'hack', 'exploit', 'bypass', 'sql', 'injection', 
    '<script', 'function()', 'eval('
  ];
  
  return bannedTerms.some(term => 
    queryObj.processedText.toLowerCase().includes(term)
  );
}; 