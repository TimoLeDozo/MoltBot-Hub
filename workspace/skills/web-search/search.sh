#!/bin/bash
# Brave Search API Skill for Clawdbot
# Usage: search.sh "query"

QUERY="$1"
API_KEY="BSAtXC53giNg_egvlOCWC2QLCGz6e3Q"

if [ -z "$QUERY" ]; then
  echo "Usage: search.sh \"query\""
  exit 1
fi

# Call Brave Search API
curl -s -H "X-Subscription-Token: $API_KEY" \
  "https://api.search.brave.com/res/v1/web/search?q=$(echo "$QUERY" | jq -sRr @uri)&count=10&search_lang=fr&country=us" | \
  jq -r '.web.results[] | "**\(.title)**\n\(.description)\n🔗 \(.url)\n"'
