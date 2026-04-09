import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.agent.types import DestinationResult
from app.main import app


class AgentEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_endpoint_returns_agent_response_shape(self) -> None:
        fake_destinations = [
            DestinationResult(
                destination_name="Valencia",
                destination_country="Spain",
                estimated_from_price_eur=145.0,
                price_category="mid_range",
                trip_tags="beach|sunny_escape|foodie",
                best_seasons="spring|summer|autumn",
            )
        ]

        with patch(
            "app.main.get_agent_service"
        ) as mocked_service_factory:
            mocked_service_factory.return_value.run.return_value = {
                "original_query": "I want a cheap sunny destination in summer",
                "applied_filters": {
                    "max_price": 150.0,
                    "trip_tag": "sunny_escape",
                    "season": "summer",
                },
                "matched_terms": ["cheap", "summer", "sunny"],
                "answer": "I interpreted your request as summer travel and sunny escape preferences.",
                "destinations": [item.model_dump() for item in fake_destinations],
            }

            response = self.client.post(
                "/agent/query",
                json={
                    "message": "I want a cheap sunny destination in summer",
                    "chat_history": [{"role": "user", "content": "I want something for July"}],
                    "response_language": "nl",
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("applied_filters", data)
        self.assertIn("matched_terms", data)
        self.assertIn("answer", data)
        self.assertIn("destinations", data)


if __name__ == "__main__":
    unittest.main()
