#!/usr/bin/env node
// Brave Search API Skill for Clawdbot
// Usage: node search.js "query"

const API_KEY = process.env.BRAVE_API_KEY || '';
const query = process.argv[2];

if (!query) {
  console.log('Usage: node search.js "query"');
  process.exit(1);
}

if (!API_KEY) {
  console.error('ERROR: BRAVE_API_KEY environment variable is not set.');
  process.exit(1);
}

const url = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=5&search_lang=fr&ui_lang=fr-FR&country=fr`;

// Build fetch options with 20s strict timeout
const fetchOptions = {
  headers: {
    'X-Subscription-Token': API_KEY,
    'Accept': 'application/json'
  },
  signal: AbortSignal.timeout(20000)
};

// Use undici ProxyAgent if HTTPS_PROXY is set (Node native fetch ignores proxy env vars)
async function doSearch() {
  try {
    const proxyUrl = process.env.HTTPS_PROXY || process.env.HTTP_PROXY || process.env.https_proxy || process.env.http_proxy;
    if (proxyUrl) {
      try {
        const { ProxyAgent } = require('undici');
        fetchOptions.dispatcher = new ProxyAgent(proxyUrl);
      } catch (e) {
        // undici not available as require, try global fetch without proxy
        // This is acceptable - direct connection will work if network allows
      }
    }

    const res = await fetch(url, fetchOptions);

    if (!res.ok) {
      console.error(`ERROR: Brave API returned HTTP ${res.status} ${res.statusText}`);
      const body = await res.text().catch(() => '');
      if (body) console.error(`Response: ${body.substring(0, 500)}`);
      process.exit(1);
    }

    const data = await res.json();

    if (data.web && data.web.results && data.web.results.length > 0) {
      data.web.results.forEach(result => {
        console.log(`**${result.title}**`);
        console.log(result.description);
        console.log(`Link: ${result.url}\n`);
      });
    } else if (data.query) {
      console.log(`No web results found for: "${data.query.original}"`);
    } else {
      console.log('No results found.');
    }
  } catch (err) {
    if (err.name === 'TimeoutError' || err.code === 'UND_ERR_CONNECT_TIMEOUT') {
      console.error('ERROR: Search request timed out after 20 seconds. The Brave API may be unreachable.');
    } else if (err.code === 'ECONNREFUSED' || err.code === 'ENOTFOUND') {
      console.error(`ERROR: Cannot reach Brave API (${err.code}). Check proxy/network configuration.`);
    } else {
      console.error(`ERROR: Search failed - ${err.message}`);
    }
    process.exit(1);
  }
}

doSearch();
