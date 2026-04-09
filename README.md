# airline-destination-agent-poc
PoC: AI agent that queries a structured airline destination dataset via GraphQL and uses an LLM as the conversation and interpretation layer for personalized travel recommendations.

## Python version

This project targets **Python 3.11** (see `.python-version` and `runtime.txt`) and keeps temporary compatibility with **Python 3.9** for local development.

## GraphQL destination filter examples

The `destinations` query remains backward compatible and now supports optional filters:
- `country`
- `minPrice`
- `maxPrice`
- `priceCategory`
- `tripTag`
- `season`

### 1) No filters (existing behavior)

```graphql
query {
  destinations {
    destinationName
    destinationCountry
    estimatedFromPriceEur
  }
}
```

### 2) Country + price range

```graphql
query {
  destinations(country: "Spain", minPrice: 80, maxPrice: 200) {
    destinationName
    destinationCountry
    estimatedFromPriceEur
    priceCategory
  }
}
```

### 3) Tag-based recommendation seed

```graphql
query {
  destinations(tripTag: "beach") {
    destinationName
    tripTags
    bestSeasons
    estimatedFromPriceEur
  }
}
```

### 4) Season + budget category

```graphql
query {
  destinations(season: "spring", priceCategory: "mid") {
    destinationName
    destinationCountry
    priceCategory
    bestSeasons
  }
}
```

## Hybrid agent endpoint

The PoC now includes a hybrid agent flow:
- OpenAI model for intent extraction from natural language
- GraphQL for deterministic structured retrieval
- OpenAI model for result explanation and recommendation wording
- deterministic rules parser as a fallback when the LLM is unavailable

### Environment

Set an API key before using the hybrid mode:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Optional settings:

```bash
export OPENAI_MODEL="gpt-4o-mini"
export AGENT_USE_LLM="true"
```

### Request the agent

`POST /agent/query`

Example body:

```json
{
  "message": "I want a cheap sunny destination in summer",
  "chat_history": [
    { "role": "user", "content": "I want something warm for July" }
  ],
  "limit": 5
}
```

Example response shape:

```json
{
  "original_query": "I want a cheap sunny destination in summer",
  "applied_filters": {
    "max_price": 150,
    "trip_tag": "sunny_escape",
    "season": "summer"
  },
  "matched_terms": ["cheap", "sunny", "summer"],
  "answer": "Here are a few warm-weather options that fit your summer budget.",
  "destinations": [
    {
      "destination_name": "Valencia",
      "destination_country": "Spain",
      "estimated_from_price_eur": 145,
      "price_category": "mid_range",
      "trip_tags": "beach|sunny_escape|foodie",
      "best_seasons": "spring|summer|autumn"
    }
  ]
}
```
