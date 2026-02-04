from ..models.user import User


_DATA = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]


def get_users() -> list[User]:
    """Return example users (in-memory)."""
    return [User(**u) for u in _DATA]
