/**
 * Query Processing Module
 * 
 * Handles all query preprocessing steps:
 * - Standardizes text
 * - Removes noise
 * - Corrects spelling
 * - Normalizes terminology
 */

/**
 * Process the raw query text to standardize and clean it
 * 
 * @param {string} rawQuery - The raw user input text
 * @returns {Object} - Processed query object with standardized text
 */
export const processQuery = (rawQuery) => {
  if (!rawQuery || typeof rawQuery !== 'string') {
    return {
      originalText: '',
      processedText: '',
      timestamp: new Date().toISOString(),
      processingSteps: []
    };
  }
  
  // Create base query object
  const processedQuery = {
    originalText: rawQuery,
    processedText: rawQuery,
    timestamp: new Date().toISOString(),
    processingSteps: []
  };
  
  // Apply text standardization
  const standardizedQuery = standardizeText(processedQuery);
  
  // Apply noise removal
  const cleanedQuery = removeNoise(standardizedQuery);
  
  // Apply spelling correction
  const correctedQuery = correctSpelling(cleanedQuery);
  
  // Apply terminology normalization
  const normalizedQuery = normalizeTerminology(correctedQuery);
  
  return normalizedQuery;
};

/**
 * Standardizes text by trimming, normalizing whitespace,
 * and converting to consistent case format
 * 
 * @param {Object} queryObj - Query object to process
 * @returns {Object} - Query object with standardized text
 */
const standardizeText = (queryObj) => {
  // Create a copy to avoid mutating the original
  const result = { ...queryObj };
  
  // Trim whitespace
  result.processedText = result.processedText.trim();
  
  // Normalize whitespace (replace multiple spaces with single space)
  result.processedText = result.processedText.replace(/\s+/g, ' ');
  
  // Record the processing step
  result.processingSteps.push({
    step: 'standardizeText',
    timestamp: new Date().toISOString()
  });
  
  return result;
};

/**
 * Removes noise from the query text such as
 * special characters, irrelevant punctuation, etc.
 * 
 * @param {Object} queryObj - Query object to process
 * @returns {Object} - Query object with noise removed
 */
const removeNoise = (queryObj) => {
  // Create a copy to avoid mutating the original
  const result = { ...queryObj };
  
  // Remove excessive punctuation but keep essential ones
  result.processedText = result.processedText.replace(/([.!?])\1+/g, '$1');
  
  // Record the processing step
  result.processingSteps.push({
    step: 'removeNoise',
    timestamp: new Date().toISOString()
  });
  
  return result;
};

/**
 * Corrects spelling in the query text
 * In a real implementation, this would use a spelling correction library
 * 
 * @param {Object} queryObj - Query object to process
 * @returns {Object} - Query object with spelling corrected
 */
const correctSpelling = (queryObj) => {
  // Create a copy to avoid mutating the original
  const result = { ...queryObj };
  
  // In a real implementation, we would use a spelling correction library
  // For now, we'll just pass through the text unchanged
  
  // Record the processing step
  result.processingSteps.push({
    step: 'correctSpelling',
    timestamp: new Date().toISOString()
  });
  
  return result;
};

/**
 * Normalizes terminology in the query text by replacing
 * domain-specific synonyms with standard terms
 * 
 * @param {Object} queryObj - Query object to process
 * @returns {Object} - Query object with normalized terminology
 */
const normalizeTerminology = (queryObj) => {
  // Create a copy to avoid mutating the original
  const result = { ...queryObj };
  
  // Example terminology normalization - would be more extensive in real implementation
  // This would normalize domain-specific terms to a standard vocabulary
  const normalizations = {
    // Example: 'fast': 'velocity',
    // 'weight': 'mass',
    // 'height': 'stature'
  };
  
  let processedText = result.processedText;
  Object.entries(normalizations).forEach(([term, replacement]) => {
    const regex = new RegExp(`\\b${term}\\b`, 'gi');
    processedText = processedText.replace(regex, replacement);
  });
  
  result.processedText = processedText;
  
  // Record the processing step
  result.processingSteps.push({
    step: 'normalizeTerminology',
    timestamp: new Date().toISOString()
  });
  
  return result;
}; 