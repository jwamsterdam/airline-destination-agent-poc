import unittest

from app.agent.parser import parse_user_query


class AgentParserTests(unittest.TestCase):
    def test_cheap_sunny_destination_in_summer(self) -> None:
        parsed = parse_user_query("I want a cheap sunny destination in summer")

        self.assertEqual(parsed.filters.max_price, 150.0)
        self.assertEqual(parsed.filters.trip_tag, "sunny_escape")
        self.assertEqual(parsed.filters.season, "summer")

    def test_dutch_query_maps_country_and_budget(self) -> None:
        parsed = parse_user_query("Ik wil een goedkope zonnige vakantie in Spanje")

        self.assertEqual(parsed.filters.max_price, 150.0)
        self.assertEqual(parsed.filters.trip_tag, "sunny_escape")
        self.assertEqual(parsed.filters.country, "Spain")

    def test_explicit_budget_is_used(self) -> None:
        parsed = parse_user_query("beach under 200")

        self.assertEqual(parsed.filters.trip_tag, "beach")
        self.assertEqual(parsed.filters.max_price, 200.0)

    def test_generic_winter_does_not_map_to_winter_holiday(self) -> None:
        parsed = parse_user_query("winter in Spain")

        self.assertEqual(parsed.filters.season, "winter")
        self.assertIsNone(parsed.filters.trip_tag)

    def test_explicit_winter_sports_maps_to_winter_holiday(self) -> None:
        parsed = parse_user_query("ski trip in winter")

        self.assertEqual(parsed.filters.season, "winter")
        self.assertEqual(parsed.filters.trip_tag, "winter_holiday")

    def test_trip_tag_priority_is_fixed(self) -> None:
        parsed = parse_user_query("I want a romantic sunny beach holiday")

        self.assertEqual(parsed.filters.trip_tag, "beach")
        self.assertIn("beach", parsed.matched_terms)

    def test_detects_southern_europe_region_constraint(self) -> None:
        parsed = parse_user_query("I want to party in South Europe")

        self.assertEqual(parsed.region_constraint, "southern_europe")


if __name__ == "__main__":
    unittest.main()
