/**
 * LLM Interaction Module
 * 
 * Handles all interactions with Language Models:
 * - Formats queries for LLM consumption
 * - Sends queries to LLMs
 * - Processes LLM responses
 */

/**
 * Send a processed query to the primary LLM for intent classification
 * and structured interpretation
 * 
 * @param {Object} queryObj - The processed query object
 * @returns {Promise<Object>} - The LLM response with classification and structure
 */
export const sendToLLM = async (queryObj) => {
  try {
    console.log('Sending query to LLM:', queryObj);
    
    // Prepare API request parameters
    const requestData = {
      model: "gpt-4", // Use default model
      messages: [
        {
          role: "system",
          content: createSystemPrompt()
        },
        {
          role: "user",
          content: formatQueryForLLM(queryObj)
        }
      ],
      temperature: 0.7,
      max_tokens: 800
    };
    
    // Make the actual API call
    const response = await fetch('/api/llm', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API call failed with status:', response.status, errorText);
      throw new Error(`API call failed with status: ${response.status}. ${errorText}`);
    }
    
    const data = await response.json();
    console.log('LLM response:', data);
    
    // Process the LLM response
    const processedResponse = processLLMResponse(data);
    
    // Add reformulated query to the response
    processedResponse.reformulatedQuery = generateReformulatedQuery(queryObj, processedResponse);
    
    return processedResponse;
  } catch (error) {
    console.error('Error sending query to LLM:', error);
    
    // Create a fallback response when the LLM call fails
    const fallbackResponse = {
      intentClassification: "informational",
      keySubject: "general",
      parametersOfInterest: [],
      confidence: 0.5,
      reasoning: "Query processing failed. Using fallback response.",
      reformulatedQuery: queryObj.query || queryObj.processedText || "No query provided"
    };
    
    return fallbackResponse;
  }
};

/**
 * Format the query for LLM consumption
 * 
 * @param {Object} queryObj - The query object to format
 * @returns {string} - Formatted query for LLM
 */
const formatQueryForLLM = (queryObj) => {
  return `
User Query: ${queryObj.query}
Research Context: ${queryObj.context || 'general research'}
Domain Terms: ${queryObj.highlightedTerms?.join(', ') || 'None specified'}

Please analyze this query and provide a structured response following the format in your instructions.
Additionally, provide a reformulated version of the query that is more specific and targeted.
  `.trim();
};

/**
 * Create the system prompt for the LLM
 * 
 * @returns {string} - The system prompt for intent detection
 */
const createSystemPrompt = () => {
  return `
You are an expert intent classifier for the Four Sided Triangle system, a platform for analyzing genetic and physiological factors in sprint performance.

Analyze the user's query and provide:

1. Intent classification (informational, computational, or comparative)
2. Key subject identification 
3. Expected parameters of interest
4. Confidence score (0-1)
5. A reformulated query that is more specific and targeted

Format your response as a JSON object with the following structure:
{
  "intentClassification": "string",
  "keySubject": "string", 
  "parametersOfInterest": ["string"],
  "confidence": number,
  "reasoning": "string",
  "reformulatedQuery": "string"
}
  `.trim();
};

/**
 * Generate a reformulated query based on the original query and LLM analysis
 * 
 * @param {Object} queryObj - Original query object
 * @param {Object} llmResponse - Processed LLM response
 * @returns {string} - Reformulated query
 */
const generateReformulatedQuery = (queryObj, llmResponse) => {
  // If the LLM already provided a reformulated query, use it
  if (llmResponse.reformulatedQuery) {
    return llmResponse.reformulatedQuery;
  }
  
  // Otherwise construct one based on the LLM analysis
  const subject = llmResponse.keySubject || '';
  const intent = llmResponse.intentClassification || '';
  const params = llmResponse.parametersOfInterest || [];
  
  // Base the reformulation on the original query plus key insights
  let reformulation = queryObj.query;
  
  // Add specificity based on identified parameters if they're not already in the query
  if (params.length > 0) {
    reformulation += ` (with specific focus on ${params.join(', ')})`;
  }
  
  // Add context based on subject if not already in the query
  if (subject && !reformulation.toLowerCase().includes(subject.toLowerCase())) {
    reformulation += ` in the context of ${subject}`;
  }
  
  return reformulation;
};

/**
 * Process and validate the LLM response
 * 
 * @param {Object} apiResponse - The raw API response
 * @returns {Object} - Processed and validated LLM response
 */
const processLLMResponse = (apiResponse) => {
  let llmResponse;
  
  // Extract the actual LLM response content from the API response
  const content = apiResponse.choices?.[0]?.message?.content;
  
  // Try to parse the JSON response
  try {
    // Extract JSON from the content - handle cases where LLM might wrap JSON in markdown
    const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/) || 
                      content.match(/{[\s\S]*?}/);
                      
    const jsonString = jsonMatch ? jsonMatch[0] : content;
    llmResponse = JSON.parse(jsonString.replace(/```json|```/g, '').trim());
  } catch (error) {
    console.error('Error parsing LLM response:', error);
    // If parsing fails, create a default structure
    llmResponse = {
      intentClassification: 'informational',
      keySubject: 'general',
      parametersOfInterest: [],
      confidence: 0.5,
      reasoning: 'Failed to parse LLM response',
      reformulatedQuery: null
    };
  }
  
  // Validate and normalize the response structure
  const validatedResponse = {
    intentClassification: llmResponse.intentClassification || 'informational',
    keySubject: llmResponse.keySubject || 'general',
    parametersOfInterest: Array.isArray(llmResponse.parametersOfInterest) 
      ? llmResponse.parametersOfInterest 
      : [],
    confidence: typeof llmResponse.confidence === 'number' 
      ? Math.max(0, Math.min(1, llmResponse.confidence)) 
      : 0.5,
    reasoning: llmResponse.reasoning || '',
    reformulatedQuery: llmResponse.reformulatedQuery || null
  };
  
  return validatedResponse;
}; 