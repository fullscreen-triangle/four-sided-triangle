import { OpenAI } from 'openai';
import { Anthropic } from '@anthropic-ai/sdk';

// Load environment variables
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
const DEFAULT_MODEL = process.env.DEFAULT_LLM_MODEL || 'gpt-4';
const LLM_PROVIDER = process.env.LLM_PROVIDER || 'openai'; // 'openai' or 'anthropic'

// Initialize clients based on available API keys
const openai = OPENAI_API_KEY ? new OpenAI({ apiKey: OPENAI_API_KEY }) : null;
const anthropic = ANTHROPIC_API_KEY ? new Anthropic({ apiKey: ANTHROPIC_API_KEY }) : null;

/**
 * API route for LLM interactions
 * Supports both OpenAI and Anthropic Claude models
 */
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({
      error: 'Method not allowed',
      message: 'Only POST requests are supported'
    });
  }

  try {
    const { model = DEFAULT_MODEL, messages, temperature = 0.7, max_tokens = 800 } = req.body;

    // Validate request payload
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({
        error: 'Invalid request',
        message: 'Messages array is required'
      });
    }

    let response;

    // Determine which provider to use based on model or configured provider
    const provider = model.includes('claude') ? 'anthropic' : LLM_PROVIDER;

    if (provider === 'anthropic' && anthropic) {
      // Use Anthropic Claude
      const prompt = formatForAnthropic(messages);
      
      response = await anthropic.completions.create({
        model: model.includes('claude') ? model : 'claude-2',
        prompt,
        max_tokens_to_sample: max_tokens,
        temperature,
      });

      // Format the response to match OpenAI structure
      return res.status(200).json({
        id: response.id,
        choices: [
          {
            message: {
              role: 'assistant',
              content: response.completion,
            },
            finish_reason: 'stop',
          },
        ],
        usage: {
          prompt_tokens: 0, // Anthropic doesn't provide this
          completion_tokens: 0, // Anthropic doesn't provide this
          total_tokens: 0, // Anthropic doesn't provide this
        },
      });
    } else if (openai) {
      // Use OpenAI
      response = await openai.chat.completions.create({
        model: model.includes('gpt') ? model : DEFAULT_MODEL,
        messages,
        temperature,
        max_tokens,
      });

      // Return the OpenAI response directly
      return res.status(200).json(response);
    } else {
      // No valid provider available
      return res.status(500).json({
        error: 'Configuration error',
        message: 'No LLM provider configured. Please add API keys in environment variables.'
      });
    }
  } catch (error) {
    console.error('LLM API Error:', error);
    
    // Handle different error types
    if (error.response) {
      // OpenAI error with response
      return res.status(error.response.status).json({
        error: 'LLM provider error',
        message: error.response.data.error.message || 'Error from LLM provider',
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
 * Format OpenAI-style messages for Anthropic Claude
 * 
 * @param {Array} messages - Array of message objects {role, content}
 * @returns {string} - Formatted Claude prompt
 */
function formatForAnthropic(messages) {
  let prompt = '\n\nHuman: ';
  let systemPrompt = '';
  
  // Extract system prompt if present
  const systemMessage = messages.find(m => m.role === 'system');
  if (systemMessage) {
    systemPrompt = systemMessage.content;
  }
  
  // Format the conversation
  const conversationMessages = messages.filter(m => m.role !== 'system');
  
  for (let i = 0; i < conversationMessages.length; i++) {
    const message = conversationMessages[i];
    
    if (i === 0 && systemPrompt) {
      // Prepend system prompt to first user message
      prompt += `${systemPrompt}\n\n${message.content}\n\nAssistant: `;
    } else if (message.role === 'user') {
      prompt += `${message.content}\n\nAssistant: `;
    } else if (message.role === 'assistant') {
      prompt += `${message.content}\n\nHuman: `;
    }
  }
  
  return prompt;
} 