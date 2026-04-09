import json
import unittest

from app.agent.tool import get_destinations
from app.agent.types import DestinationFilters


class AgentToolTests(unittest.TestCase):
    def test_graphql_variables_use_existing_argument_names(self) -> None:
        captured = {}

        def fake_execute_request(url: str, payload: bytes) -> dict:
            captured["url"] = url
            captured["payload"] = json.loads(payload.decode("utf-8"))
            return {"data": {"destinations": []}}

        filters = DestinationFilters(country="Spain", max_price=150.0, season="summer")
        get_destinations(
            filters=filters,
            graphql_endpoint_url="http://example.test/graphql",
            execute_request=fake_execute_request,
        )

        self.assertEqual(captured["url"], "http://example.test/graphql")
        self.assertEqual(
            captured["payload"]["variables"],
            {"country": "Spain", "maxPrice": 150.0, "season": "summer"},
        )

    def test_graphql_query_selection_set_remains_minimal(self) -> None:
        captured = {}

        def fake_execute_request(url: str, payload: bytes) -> dict:
            captured["payload"] = json.loads(payload.decode("utf-8"))
            return {"data": {"destinations": []}}

        get_destinations(
            filters=DestinationFilters(),
            graphql_endpoint_url="http://example.test/graphql",
            execute_request=fake_execute_request,
        )

        query = captured["payload"]["query"]
        self.assertIn("destinationName", query)
        self.assertIn("destinationCountry", query)
        self.assertIn("estimatedFromPriceEur", query)
        self.assertIn("priceCategory", query)
        self.assertIn("tripTags", query)
        self.assertIn("bestSeasons", query)

    def test_omits_none_filter_values(self) -> None:
        captured = {}

        def fake_execute_request(url: str, payload: bytes) -> dict:
            captured["payload"] = json.loads(payload.decode("utf-8"))
            return {"data": {"destinations": []}}

        get_destinations(
            filters=DestinationFilters(trip_tag="beach"),
            graphql_endpoint_url="http://example.test/graphql",
            execute_request=fake_execute_request,
        )

        self.assertEqual(captured["payload"]["variables"], {"tripTag": "beach"})


if __name__ == "__main__":
    unittest.main()
