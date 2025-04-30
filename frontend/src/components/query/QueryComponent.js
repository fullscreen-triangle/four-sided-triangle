import React, { useState, useRef, useEffect } from 'react';
import { FaSearch, FaRegLightbulb, FaCheck, FaTimes, FaHighlighter } from 'react-icons/fa';
import Loader from '../Loader';
import { processQuery } from './queryProcessing';
import { validateQuery } from './queryValidation';
import { packageQuery } from './queryPackaging';
import { sendToLLM } from './llmInteraction';
import SyntaxHighlighter from './SyntaxHighlighter.tsx';
import technicalTerms from './technicalTerms';

/**
 * QueryComponent (formerly SearchBar)
 * 
 * A sophisticated search bar with term highlighting and query reformulation.
 * Supports a workflow where:
 * 1. First query => reformulation with echo
 * 2. Second query (after reformulation) => score preview 
 * 
 * Supports research context specification (research/validation/confirmation/analysis)
 */
const QueryComponent = ({ onSearch, query, isLoading }) => {
  // Base state for search bar
  const [searchText, setSearchText] = useState('I need to know all the possible predicted body segments and metrics for a given a caucasian male from Dunbury Connecticut, 31 years old, weighs 79kg and is 172cm tall.');
  const [highlightedTerms, setHighlightedTerms] = useState([]);
  const [isEchoMode, setIsEchoMode] = useState(false);
  const [hasBeenReformulated, setHasBeenReformulated] = useState(false);
  const [reformulatedOnce, setReformulatedOnce] = useState(false);
  const [researchContext, setResearchContext] = useState('research');

  // State for handling user highlighting
  const [isHighlightMode, setIsHighlightMode] = useState(false);
  const [selectionStart, setSelectionStart] = useState(0);
  const [selectionEnd, setSelectionEnd] = useState(0);

  // Internal processing state
  const [error, setError] = useState(null);

  const textareaRef = useRef(null);

  // Track reformulated query
  const [reformulatedQuery, setReformulatedQuery] = useState('');
  const [originalQuery, setOriginalQuery] = useState('');

  // Research context options
  const contextOptions = [
    { value: 'research', label: 'Research', description: 'Generate new knowledge and insights' },
    { value: 'validation', label: 'Validation', description: 'Verify existing claims or hypotheses' },
    { value: 'confirmation', label: 'Confirmation', description: 'Seek consensus across multiple studies' },
    { value: 'analysis', label: 'Analysis', description: 'Statistical evaluation of scientific data' },
    { value: 'modeling', label: 'Modeling', description: 'Build predictive models from scientific data' }
  ];

  // Update local state when query prop changes
  useEffect(() => {
    if (query && typeof query === 'object') {
      setSearchText(query.text || '');
      setHighlightedTerms(query.highlightedTerms || []);
      setIsEchoMode(query.isEchoMode || false);
      setReformulatedQuery(query.text || '');
      setOriginalQuery(query.originalText || '');
      setResearchContext(query.researchContext || 'research');

      // If we have a reformulated query from the server, mark as reformulated
      if (query.isReformulated) {
        setHasBeenReformulated(true);
        setReformulatedOnce(true);
      }
    } else if (query && typeof query === 'string') {
      setSearchText(query);
    }
  }, [query]);

  // Handle text changes
  const handleTextChange = (e) => {
    const text = e.target.value;
    setSearchText(text);
    setError(null);

    // Reset echo mode when user edits text
    if (isEchoMode) {
      setIsEchoMode(false);
    }
  };

  // Handle selection for highlighting domain terms
  const handleTextSelection = () => {
    if (!isHighlightMode || !textareaRef.current) return;

    const start = textareaRef.current.selectionStart;
    const end = textareaRef.current.selectionEnd;

    // Only process if there's an actual selection
    if (start !== end) {
      setSelectionStart(start);
      setSelectionEnd(end);

      // Get the selected text
      const selectedText = searchText.substring(start, end).trim();

      // Add to highlighted terms if not already there
      if (selectedText && !highlightedTerms.includes(selectedText)) {
        setHighlightedTerms([...highlightedTerms, selectedText]);
      }
    }
  };

  // Toggle highlight mode
  const toggleHighlightMode = () => {
    setIsHighlightMode(!isHighlightMode);
    // Focus the textarea when entering highlight mode
    if (!isHighlightMode) {
      textareaRef.current.focus();
    }
  };

  // Remove a highlighted term
  const removeHighlightedTerm = (termToRemove) => {
    setHighlightedTerms(highlightedTerms.filter(term => term !== termToRemove));
  };

  // Handle research context change
  const handleContextChange = (e) => {
    setResearchContext(e.target.value);
  };

  // Handle search submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLoading || !searchText.trim()) return;

    // The query object to pass to the parent
    let queryObj = {
      text: searchText.trim(),
      highlightedTerms: highlightedTerms,
      researchContext: researchContext
    };

    // Handle echo mode confirmation
    if (isEchoMode) {
      queryObj.isConfirmed = true;
      queryObj.skipReformulation = true; // Skip reformulation after confirmation
      setIsEchoMode(false);
      setHasBeenReformulated(true);

      onSearch(queryObj);
      return;
    } 
    // Skip reformulation if we've already reformed once before
    else if (reformulatedOnce) {
      queryObj.skipReformulation = true;
      onSearch(queryObj);
      return;
    }

    try {
      // Process the query using our processing pipeline
      const processedQuery = processQuery(searchText);

      // Validate the query
      const validationResult = validateQuery(processedQuery);
      if (!validationResult.isValid) {
        setError(validationResult.errorMessage);
        return;
      }

      // Package the query for LLM processing
      const packagedQuery = packageQuery({
        query: processedQuery,
        context: researchContext,
        highlightedTerms: highlightedTerms
      });

      try {
        // Send to LLM for reformulation
        const reformulationResult = await sendToLLM(packagedQuery);

        if (reformulationResult && reformulationResult.reformulatedQuery) {
          setReformulatedQuery(reformulationResult.reformulatedQuery);
          setOriginalQuery(searchText);
          setIsEchoMode(true);
        } else {
          // If reformulation fails, still continue with search
          console.warn('Reformulation did not return expected data. Proceeding with original query.');
          queryObj.skipReformulation = true;
          onSearch(queryObj);
        }
      } catch (reformError) {
        // If the LLM call fails, still proceed with the search
        console.error('Error in LLM reformulation:', reformError);
        queryObj.skipReformulation = true;
        onSearch(queryObj);
      }
    } catch (err) {
      console.error('Error in query processing:', err);
      setError(err.message || 'Error processing query');

      // Fallback: try to search with the raw query if processing fails
      if (searchText.trim().length > 3) {
        const fallbackQueryObj = {
          text: searchText.trim(),
          highlightedTerms: highlightedTerms,
          researchContext: researchContext,
          skipReformulation: true
        };

        onSearch(fallbackQueryObj);
      }
    }
  };

  // Handle cancellation in echo mode
  const handleCancelEcho = () => {
    setSearchText(originalQuery);
    setIsEchoMode(false);
    setReformulatedQuery('');
  };

  // Handle getting query ideas
  const handleGetQueryIdeas = () => {
    if (isLoading) return;

    // Create a random set of query ideas based on domain
    const queryIdeas = [
      "How does the ACTN3 gene affect sprint performance?",
      "What is the role of fast-twitch muscle fibers in 100m sprinting?",
      "Relationship between genetics and elite sprint performances",
      "Compare sprinter body types between Olympic champions",
      "How do ACE gene variants influence power vs endurance?",
      "Biomechanical analysis of elite sprinters' stride patterns",
      "Genetic factors that contribute to explosive power in sprinting"
    ];

    // Randomly select one
    const randomIdea = queryIdeas[Math.floor(Math.random() * queryIdeas.length)];
    setSearchText(randomIdea);

    // Focus the textarea
    textareaRef.current.focus();
  };

  // Handle reset button
  const handleReset = () => {
    setSearchText('');
    setHighlightedTerms([]);
    setIsEchoMode(false);
    setHasBeenReformulated(false);
    setReformulatedOnce(false);
    setReformulatedQuery('');
    setOriginalQuery('');
    setResearchContext('research');
    setError(null);
    setIsHighlightMode(false);

    // Focus the textarea
    textareaRef.current.focus();
  };

  // Import the useBreakpoint hook
  const breakpoint = useBreakpoint();
  
  return (
    <div className={`mt-4 mb-8 w-full mx-auto ${breakpoint.isMobile ? 'max-w-full px-4' : 'max-w-5xl'}`}>
      <form 
        onSubmit={handleSubmit} 
        className={`relative bg-light/10 dark:bg-dark/30 rounded-xl shadow-lg border border-light/5 dark:border-dark/20 
          ${breakpoint.isMobile ? 'p-3' : 'p-4'}`}
      >
        <div className="flex flex-col space-y-4">
          {/* Research context selector */}
          <div className="flex flex-wrap gap-2 text-light/80">
            <span className="text-xs pt-1">Context:</span>
            <div className="flex flex-wrap gap-2">
              {contextOptions.map(option => (
                <label 
                  key={option.value}
                  className={`
                    cursor-pointer text-xs px-2 py-1 rounded-full
                    ${researchContext === option.value 
                      ? 'bg-blue-600 text-white font-medium' 
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'}
                    hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors
                  `}
                >
                  <input
                    type="radio"
                    name="researchContext"
                    value={option.value}
                    checked={researchContext === option.value}
                    onChange={handleContextChange}
                    className="sr-only"
                  />
                  {option.label}
                  <span className="hidden sm:inline-block ml-1 opacity-60">{option.description && ` · ${option.description}`}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Search textarea with syntax highlighting and floating controls */}
          <div className="relative">
            <SyntaxHighlighter
              ref={textareaRef}
              value={searchText}
              onChange={handleTextChange}
              onMouseUp={handleTextSelection}
              onKeyUp={handleTextSelection}
              className="w-full px-4 py-3 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                      placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none resize-none border border-gray-300 dark:border-gray-700"
              placeholder="Ask your scientific question..."
              rows={4}
              style={{ resize: 'vertical', minHeight: '120px' }}
              technicalTerms={technicalTerms}
            />

            <div className="absolute top-2 right-2 flex space-x-2">
              <button
                type="button"
                onClick={toggleHighlightMode}
                className={`
                  text-xs p-2 rounded-full
                  ${isHighlightMode 
                    ? 'bg-blue-500/20 text-blue-400' 
                    : 'text-light/70 hover:text-light/100 hover:bg-light/10'}
                  transition-colors
                `}
                title="Highlight domain terms (select text first)"
              >
                <FaHighlighter />
              </button>
              <button
                type="button"
                onClick={handleGetQueryIdeas}
                className="text-xs p-2 rounded-full text-light/70 hover:text-light/100 hover:bg-light/10 transition-colors"
                title="Get query ideas"
              >
                <FaRegLightbulb />
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="text-xs p-2 rounded-full text-light/70 hover:text-light/100 hover:bg-light/10 transition-colors"
                title="Reset"
              >
                <FaTimes />
              </button>
            </div>

            {isHighlightMode && (
              <div className="absolute bottom-2 left-2 bg-blue-500/10 text-blue-400 text-xs rounded-lg px-2 py-1">
                Highlight Mode: Select text to mark domain terms
              </div>
            )}
          </div>

          {/* User highlighted domain terms */}
          {highlightedTerms.length > 0 && (
            <div className="flex flex-wrap gap-2 items-center">
              <span className="text-xs text-light/60">Domain terms:</span>
              <div className="flex flex-wrap gap-2">
                {highlightedTerms.map(term => (
                  <div 
                    key={term}
                    className="flex items-center gap-1 text-xs px-2 py-1 rounded-full 
                              bg-blue-500/20 text-blue-400 group"
                  >
                    <span>{term}</span>
                    <button
                      type="button"
                      onClick={() => removeHighlightedTerm(term)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <FaTimes size={10} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error message display */}
          {error && (
            <div className="p-2 bg-red-500/10 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Echo mode: Show reformulated query with confirm/cancel */}
          {isEchoMode && (
            <div className="p-3 bg-green-500/10 rounded-lg border border-green-500/20">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm text-green-400 font-medium mb-1">Reformulated Query:</p>
                  <p className="text-light/90">{reformulatedQuery}</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    type="button"
                    onClick={handleCancelEcho}
                    className="p-2 rounded-full bg-light/5 text-light/70 hover:bg-light/10 hover:text-light transition-colors"
                  >
                    <FaTimes />
                  </button>
                  <button
                    type="submit"
                    className="p-2 rounded-full bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                  >
                    <FaCheck />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Submit button */}
          {!isEchoMode && (
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isLoading || !searchText.trim()}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg
                  ${isLoading || !searchText.trim() 
                    ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
                    : 'bg-blue-600 text-white hover:bg-blue-700 transition-colors'}
                `}
              >
                {isLoading ? (
                  <>
                    <Loader /> 
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <FaSearch /> 
                    <span>Search</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </form>
    </div>
  );
};

import { withErrorBoundary } from '../ErrorBoundary';

// Custom fallback for QueryComponent errors
const QueryErrorFallback = ({ reset }) => (
  <div className="mt-4 mb-8 w-full max-w-5xl mx-auto">
    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 rounded-lg text-center">
      <h3 className="text-lg font-medium text-red-800 dark:text-red-300 mb-2">
        Query Component Error
      </h3>
      <p className="text-red-600 dark:text-red-400 mb-4">
        There was an error loading the query interface. Your search experience may be limited.
      </p>
      <button
        onClick={reset}
        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
      >
        Try Again
      </button>
    </div>
  </div>
);

export default withErrorBoundary(QueryComponent, <QueryErrorFallback />);
