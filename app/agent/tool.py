import json
from typing import Callable, List, Optional
from urllib import request

from app.agent.types import DestinationFilters, DestinationResult


GRAPHQL_QUERY = """
query GetDestinations(
  $country: String
  $minPrice: Float
  $maxPrice: Float
  $priceCategory: String
  $tripTag: String
  $season: String
) {
  destinations(
    country: $country
    minPrice: $minPrice
    maxPrice: $maxPrice
    priceCategory: $priceCategory
    tripTag: $tripTag
    season: $season
  ) {
    destinationName
    destinationCountry
    estimatedFromPriceEur
    priceCategory
    tripTags
    bestSeasons
  }
}
""".strip()


def get_destinations(
    filters: DestinationFilters,
    graphql_endpoint_url: str,
    execute_request: Optional[Callable[[str, bytes], dict]] = None,
) -> List[DestinationResult]:
    request_payload = {
        "query": GRAPHQL_QUERY,
        "variables": filters.to_graphql_variables(),
    }
    payload_bytes = json.dumps(request_payload).encode("utf-8")

    if execute_request is None:
        response_data = _execute_graphql_request(graphql_endpoint_url, payload_bytes)
    else:
        response_data = execute_request(graphql_endpoint_url, payload_bytes)

    if "errors" in response_data:
        raise ValueError("GraphQL request returned errors.")

    destinations = response_data.get("data", {}).get("destinations", [])
    return [
        DestinationResult(
            destination_name=item["destinationName"],
            destination_country=item["destinationCountry"],
            estimated_from_price_eur=float(item["estimatedFromPriceEur"]),
            price_category=item["priceCategory"],
            trip_tags=item["tripTags"],
            best_seasons=item["bestSeasons"],
        )
        for item in destinations
    ]


def _execute_graphql_request(graphql_endpoint_url: str, payload_bytes: bytes) -> dict:
    graphql_request = request.Request(
        graphql_endpoint_url,
        data=payload_bytes,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(graphql_request) as response:
        return json.loads(response.read().decode("utf-8"))
