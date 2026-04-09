# airline-destination-agent-poc
PoC: AI agent that queries a structured airline destination dataset via GraphQL and MCP to provide personalized travel recommendations.

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
