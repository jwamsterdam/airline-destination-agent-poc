from collections.abc import Sequence

from app.db.models import Destination


def resolve_destinations() -> Sequence[Destination]:
    """Placeholder resolver; data-access logic is intentionally not implemented yet."""
    return []
