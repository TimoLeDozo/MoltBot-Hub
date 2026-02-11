# Brave Search Skill for Clawdbot

Web search capability using Brave Search API (2000 free queries per month).

## Installation

```bash
npm install
```

## Usage

```bash
node search.js "your search query"
```

## API Key

The skill uses the BRAVE_SEARCH_API_KEY environment variable or the hardcoded key in search.js.

## Features

- 10 search results per query
- French language support
- US region default
- Formatted output with titles, descriptions, and URLs
