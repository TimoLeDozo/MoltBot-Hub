#!/usr/bin/env node
// Brave Search API Skill for Clawdbot
// Usage: node search.js "query"

const API_KEY = 'BSAtXC53giNg_egvlOCWC2QLCGz6e3Q';
const query = process.argv[2];

if (!query) {
  console.log('Usage: node search.js "query"');
  process.exit(1);
}

const url = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=10&search_lang=fr&country=us`;

fetch(url, {
  headers: {
    'X-Subscription-Token': API_KEY,
    'Accept': 'application/json'
  }
})
  .then(res => res.json())
  .then(data => {
    if (data.web && data.web.results) {
      data.web.results.forEach(result => {
        console.log(`**${result.title}**`);
        console.log(result.description);
        console.log(`🔗 ${result.url}\n`);
      });
    } else {
      console.log('Aucun résultat trouvé.');
    }
  })
  .catch(err => {
    console.error('Erreur:', err.message);
    process.exit(1);
  });
