import re
import unicodedata
from typing import Dict, List, Optional, Sequence, Tuple

from app.agent.types import DestinationFilters, ParsedQuery


COUNTRY_ALIASES = {
    "albania": "Albania",
    "austria": "Austria",
    "croatia": "Croatia",
    "cyprus": "Cyprus",
    "czech republic": "Czech Republic",
    "denmark": "Denmark",
    "egypt": "Egypt",
    "france": "France",
    "georgia": "Georgia",
    "greece": "Greece",
    "iceland": "Iceland",
    "italy": "Italy",
    "morocco": "Morocco",
    "norway": "Norway",
    "portugal": "Portugal",
    "spain": "Spain",
    "turkey": "Turkey",
    "united kingdom": "United Kingdom",
    "spanje": "Spain",
    "griekenland": "Greece",
    "italie": "Italy",
    "marokko": "Morocco",
    "frankrijk": "France",
    "oostenrijk": "Austria",
    "verenigd koninkrijk": "United Kingdom",
    "uk": "United Kingdom",
    "engeland": "United Kingdom",
}

SEASON_KEYWORDS = {
    "spring": ("spring", "lente"),
    "summer": ("summer", "zomer"),
    "autumn": ("autumn", "fall", "herfst"),
    "winter": ("winter",),
}

PRICE_CATEGORY_KEYWORDS = {
    "premium": ("premium", "luxury", "luxe"),
}

GENERIC_MAX_PRICE_KEYWORDS = (
    "cheap",
    "budget",
    "affordable",
    "goedkoop",
    "goedkope",
    "betaalbaar",
)

TRIP_TAG_PRIORITY = (
    "beach",
    "sunny_escape",
    "citytrip",
    "cultural",
    "nature",
    "active",
    "family_friendly",
    "romantic",
    "foodie",
    "nightlife",
    "island",
    "winter_holiday",
)

TRIP_TAG_KEYWORDS = {
    "beach": ("beach", "strand"),
    "sunny_escape": ("sunny", "sun", "zonnig", "zonnige", "zon"),
    "citytrip": ("city trip", "citytrip", "stedentrip"),
    "cultural": ("culture", "cultural", "cultuur"),
    "nature": ("nature", "natuur"),
    "active": ("active", "actief", "hiking", "adventure"),
    "family_friendly": ("family", "gezin", "kids", "family friendly"),
    "romantic": ("romantic", "romantisch"),
    "foodie": ("food", "foodie", "culinary", "eten"),
    "nightlife": ("nightlife", "party", "uitgaan"),
    "island": ("island", "eiland"),
    "winter_holiday": (
        "ski",
        "skiing",
        "snowboard",
        "snowboarding",
        "winter sports",
        "wintersport",
    ),
}

MAX_PRICE_PATTERNS = (
    r"\bunder\s+(\d+)\b",
    r"\bbelow\s+(\d+)\b",
    r"\bmax\s+(\d+)\b",
    r"\bonder\s+(\d+)\b",
    r"\btot\s+(\d+)\b",
)

MIN_PRICE_PATTERNS = (
    r"\babove\s+(\d+)\b",
    r"\bover\s+(\d+)\b",
    r"\bmin\s+(\d+)\b",
    r"\bat least\s+(\d+)\b",
    r"\bvanaf\s+(\d+)\b",
)


def parse_user_query(message: str) -> ParsedQuery:
    normalized_message = normalize_text(message)
    matched_terms: List[str] = []

    filters = DestinationFilters(
        country=detect_country(normalized_message, matched_terms),
        min_price=detect_numeric_value(normalized_message, MIN_PRICE_PATTERNS, matched_terms),
        max_price=detect_numeric_value(normalized_message, MAX_PRICE_PATTERNS, matched_terms),
        price_category=detect_price_category(normalized_message, matched_terms),
        season=detect_season(normalized_message, matched_terms),
        trip_tag=detect_trip_tag(normalized_message, matched_terms),
    )

    if filters.max_price is None:
        filters.max_price = detect_generic_max_price(normalized_message, matched_terms)

    return ParsedQuery(filters=filters, matched_terms=matched_terms)


def normalize_text(message: str) -> str:
    normalized = unicodedata.normalize("NFKD", message)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower().strip()
    no_punctuation = re.sub(r"[^\w\s]", " ", lowered)
    return re.sub(r"\s+", " ", no_punctuation).strip()


def detect_country(normalized_message: str, matched_terms: List[str]) -> Optional[str]:
    for alias, country in COUNTRY_ALIASES.items():
        if contains_term(normalized_message, alias):
            add_unique(matched_terms, alias)
            return country
    return None


def detect_numeric_value(
    normalized_message: str,
    patterns: Sequence[str],
    matched_terms: List[str],
) -> Optional[float]:
    for pattern in patterns:
        match = re.search(pattern, normalized_message)
        if match:
            add_unique(matched_terms, match.group(0))
            return float(match.group(1))
    return None


def detect_generic_max_price(normalized_message: str, matched_terms: List[str]) -> Optional[float]:
    for keyword in GENERIC_MAX_PRICE_KEYWORDS:
        if contains_term(normalized_message, keyword):
            add_unique(matched_terms, keyword)
            return 150.0
    return None


def detect_price_category(normalized_message: str, matched_terms: List[str]) -> Optional[str]:
    for category, keywords in PRICE_CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if contains_term(normalized_message, keyword):
                add_unique(matched_terms, keyword)
                return category
    return None


def detect_season(normalized_message: str, matched_terms: List[str]) -> Optional[str]:
    for season, keywords in SEASON_KEYWORDS.items():
        for keyword in keywords:
            if contains_term(normalized_message, keyword):
                add_unique(matched_terms, keyword)
                return season
    return None


def detect_trip_tag(normalized_message: str, matched_terms: List[str]) -> Optional[str]:
    tag_matches: Dict[str, str] = {}

    for trip_tag, keywords in TRIP_TAG_KEYWORDS.items():
        for keyword in keywords:
            if contains_term(normalized_message, keyword):
                tag_matches[trip_tag] = keyword
                break

    for trip_tag in TRIP_TAG_PRIORITY:
        if trip_tag in tag_matches:
            add_unique(matched_terms, tag_matches[trip_tag])
            return trip_tag
    return None


def contains_term(normalized_message: str, term: str) -> bool:
    pattern = r"(^|\s){term}(\s|$)".format(term=re.escape(term))
    return re.search(pattern, normalized_message) is not None


def add_unique(values: List[str], value: str) -> None:
    if value not in values:
        values.append(value)
