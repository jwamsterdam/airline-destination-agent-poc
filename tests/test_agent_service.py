import unittest
from unittest.mock import Mock

from app.agent.service import AgentService
from app.agent.types import ChatMessage, DestinationResult, ParsedQuery


class AgentServiceTests(unittest.TestCase):
    def test_successful_response_contains_filters_debug_and_destinations(self) -> None:
        fetcher = Mock(
            return_value=[
                DestinationResult(
                    destination_name="Malaga",
                    destination_country="Spain",
                    estimated_from_price_eur=140.0,
                    price_category="mid_range",
                    trip_tags="beach|sunny_escape",
                    best_seasons="spring|summer|autumn",
                )
            ]
        )
        interpreter = Mock()
        interpreter.is_available.return_value = False
        service = AgentService(
            "http://example.test/graphql",
            destination_fetcher=fetcher,
            query_interpreter=interpreter,
        )

        response = service.run("I want a cheap sunny destination in summer")

        self.assertEqual(response.applied_filters.max_price, 150.0)
        self.assertIn("cheap", response.matched_terms)
        self.assertEqual(len(response.destinations), 1)
        self.assertIn("Malaga, Spain", response.answer)
        fetcher.assert_called_once()

    def test_no_recognized_filters_skips_graphql_call(self) -> None:
        fetcher = Mock(return_value=[])
        interpreter = Mock()
        interpreter.is_available.return_value = False
        service = AgentService(
            "http://example.test/graphql",
            destination_fetcher=fetcher,
            query_interpreter=interpreter,
        )

        response = service.run("Surprise me with something nice")

        self.assertEqual(response.destinations, [])
        self.assertFalse(response.applied_filters.has_filters())
        self.assertIn("could not confidently map", response.answer)
        fetcher.assert_not_called()

    def test_no_results_returns_helpful_message(self) -> None:
        fetcher = Mock(return_value=[])
        interpreter = Mock()
        interpreter.is_available.return_value = False
        service = AgentService(
            "http://example.test/graphql",
            destination_fetcher=fetcher,
            query_interpreter=interpreter,
        )

        response = service.run("beach under 50 in winter")

        self.assertEqual(response.destinations, [])
        self.assertIn("no destinations matched", response.answer)
        fetcher.assert_called_once()

    def test_uses_llm_interpreter_and_summary_when_available(self) -> None:
        interpreter = Mock()
        interpreter.is_available.return_value = True
        interpreter.parse_query.return_value = ParsedQuery.model_validate(
            {
                "filters": {
                    "country": "Spain",
                    "trip_tag": "sunny_escape",
                    "season": "summer",
                },
                "matched_terms": ["spain", "sunny", "summer"],
            }
        )
        interpreter.summarize_results.return_value = "Malaga and Valencia are strong sunny summer fits."
        interpreter.describe_destinations.return_value = [
            Mock(destination_name="Malaga", description="Malaga is a sunny coastal match with a lively atmosphere.")
        ]
        fetcher = Mock(
            return_value=[
                DestinationResult(
                    destination_name="Malaga",
                    destination_country="Spain",
                    estimated_from_price_eur=140.0,
                    price_category="mid_range",
                    trip_tags="beach|sunny_escape",
                    best_seasons="spring|summer|autumn",
                )
            ]
        )
        service = AgentService(
            "http://example.test/graphql",
            destination_fetcher=fetcher,
            query_interpreter=interpreter,
        )

        response = service.run(
            "I want a sunny destination in Spain",
            chat_history=[ChatMessage(role="user", content="I want somewhere warm")],
            response_language="nl",
        )

        self.assertEqual(response.applied_filters.country, "Spain")
        self.assertEqual(response.answer, "Malaga and Valencia are strong sunny summer fits.")
        self.assertEqual(
            response.destinations[0].description,
            "Malaga is a sunny coastal match with a lively atmosphere.",
        )
        interpreter.parse_query.assert_called_once()
        interpreter.summarize_results.assert_called_once()
        interpreter.describe_destinations.assert_called_once()
        self.assertEqual(interpreter.summarize_results.call_args.kwargs["response_language"], "nl")

    def test_invalid_llm_filter_values_fall_back_to_rules_parser(self) -> None:
        interpreter = Mock()
        interpreter.is_available.return_value = True
        interpreter.parse_query.return_value = ParsedQuery.model_validate(
            {
                "filters": {
                    "price_category": "cheap",
                    "trip_tag": "sunny_escape",
                    "season": "summer",
                },
                "matched_terms": ["cheap", "sunny", "summer"],
            }
        )
        interpreter.summarize_results.return_value = "Fallback summary."
        fetcher = Mock(return_value=[])
        service = AgentService(
            "http://example.test/graphql",
            destination_fetcher=fetcher,
            query_interpreter=interpreter,
        )

        response = service.run("I want a cheap sunny destination in summer")

        self.assertEqual(response.applied_filters.max_price, 150.0)
        self.assertIsNone(response.applied_filters.price_category)
        self.assertEqual(response.applied_filters.trip_tag, "sunny_escape")
        self.assertIn("no destinations matched", response.answer)
        interpreter.summarize_results.assert_not_called()

    def test_fallback_messages_are_localized(self) -> None:
        interpreter = Mock()
        interpreter.is_available.return_value = False
        service = AgentService(
            "http://example.test/graphql",
            destination_fetcher=Mock(return_value=[]),
            query_interpreter=interpreter,
        )

        response = service.run("Surprise me with something nice", response_language="nl")

        self.assertIn("Ik kon je vraag", response.answer)

    def test_region_constraint_filters_out_non_matching_countries(self) -> None:
        interpreter = Mock()
        interpreter.is_available.return_value = False
        service = AgentService(
            "http://example.test/graphql",
            destination_fetcher=Mock(
                return_value=[
                    DestinationResult(
                        destination_name="Barcelona",
                        destination_country="Spain",
                        estimated_from_price_eur=210.0,
                        price_category="premium",
                        trip_tags="citytrip|nightlife",
                        best_seasons="spring|summer",
                    ),
                    DestinationResult(
                        destination_name="Hurghada",
                        destination_country="Egypt",
                        estimated_from_price_eur=199.0,
                        price_category="mid_range",
                        trip_tags="beach|sunny_escape",
                        best_seasons="spring|summer|autumn",
                    ),
                ]
            ),
            query_interpreter=interpreter,
        )

        response = service.run("I want to party in South Europe")

        self.assertEqual(len(response.destinations), 1)
        self.assertEqual(response.destinations[0].destination_country, "Spain")
        self.assertIn("You are looking for Southern Europe", response.answer)


if __name__ == "__main__":
    unittest.main()
