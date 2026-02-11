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
    const result = execSync(`node "${searchScript}" "${query}"`, {
      encoding: 'utf-8',
      maxBuffer: 10 * 1024 * 1024
    });
    return result;
  } catch (error) {
    throw new Error(`Search failed: ${error.message}`);
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
