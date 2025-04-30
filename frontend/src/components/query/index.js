/**
 * Query Component Module
 * 
 * Main export file for the Query component.
 * Exports the Query component and all its associated functionality.
 */

import QueryComponent from './QueryComponent';
import { processQuery } from './queryProcessing';
import { validateQuery } from './queryValidation';
import { packageQuery } from './queryPackaging';
import { sendToLLM } from './llmInteraction';

// For backwards compatibility with code that uses SearchBar
export { QueryComponent as SearchBar };

export {
  QueryComponent,
  processQuery,
  validateQuery,
  packageQuery,
  sendToLLM
};

export default QueryComponent; 