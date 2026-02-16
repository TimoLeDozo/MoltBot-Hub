#!/usr/bin/env node
/**
 * Brave Search API Skill for Clawdbot
 * Provides web search capabilities using Brave Search API
 */

const { execSync } = require('child_process');
const path = require('path');

// Export the search function for programmatic use
module.exports = async function search(query) {
  const searchScript = path.join(__dirname, 'search.js');
  try {
    const result = execSync(`node "${searchScript}" ${JSON.stringify(query)}`, {
      encoding: 'utf-8',
      maxBuffer: 10 * 1024 * 1024,
      timeout: 45000 // 45s hard kill - prevents infinite hang
    });
    // Truncate to 3000 chars to prevent Qwen 7B from choking on large tool output
    if (result.length > 3000) {
      return result.substring(0, 3000) + '\n\n[... resultats tronques a 3000 caracteres]';
    }
    return result;
  } catch (error) {
    if (error.killed) {
      throw new Error('Search timed out after 45 seconds. The search service may be unreachable.');
    }
    // Return stderr as the error message if available (contains our descriptive errors)
    const stderr = error.stderr ? error.stderr.trim() : '';
    throw new Error(stderr || `Search failed: ${error.message}`);
  }
};

// CLI support
if (require.main === module) {
  const query = process.argv.slice(2).join(' ');
  if (!query) {
    console.log('Usage: brave-search <query>');
    process.exit(1);
  }
  module.exports(query).then(console.log).catch(err => {
    console.error(err.message);
    process.exit(1);
  });
}
