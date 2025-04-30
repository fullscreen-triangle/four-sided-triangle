/**
 * Rate Limiter Utility
 * 
 * Implements a token bucket algorithm for API rate limiting
 * Based on Next.js API routes middleware pattern
 */

import { LRUCache } from 'lru-cache';

/**
 * Create a rate limiter
 * 
 * @param {Object} options - Rate limiter options
 * @param {number} options.interval - Time window in milliseconds
 * @param {number} options.limit - Maximum number of requests in the time window
 * @param {number} options.uniqueTokenPerInterval - Maximum number of unique tokens (IPs or users)
 * @returns {Object} - The rate limiter object with check method
 */
export function rateLimit({ interval, limit, uniqueTokenPerInterval }) {
  const tokenCache = new LRUCache({
    max: uniqueTokenPerInterval || 500,
    ttl: interval || 60 * 1000, // Default 1 minute
  });

  return {
    /**
     * Check if a token has exceeded the rate limit
     * 
     * @param {Object} res - Response object
     * @param {number} maxLimit - Maximum limit (overrides default)
     * @param {string} token - Unique token (usually IP or user ID)
     * @returns {Promise<void>} - Resolves if limit not reached, rejects if limit exceeded
     */
    check: (res, maxLimit, token) => {
      const effectiveLimit = maxLimit || limit;
      const tokenCount = tokenCache.get(token) || [0];
      
      if (tokenCount[0] === 0) {
        tokenCache.set(token, tokenCount);
      }
      
      tokenCount[0] += 1;

      const currentUsage = tokenCount[0];
      const isRateLimited = currentUsage > effectiveLimit;

      // Set rate limit headers for transparency
      res.setHeader('X-RateLimit-Limit', effectiveLimit);
      res.setHeader('X-RateLimit-Remaining', Math.max(0, effectiveLimit - currentUsage));
      res.setHeader('X-RateLimit-Reset', new Date(Date.now() + interval).toISOString());

      if (isRateLimited) {
        const error = new Error('Rate limit exceeded');
        error.code = 'LIMIT_EXCEEDED';
        throw error;
      }

      return Promise.resolve();
    },
  };
} 