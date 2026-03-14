from enum import Enum


class RepoType(str, Enum):
    """
    Supported repository storage backends.

    Each value represents a persistence strategy used to
    create a concrete repository implementation.
    """
    JSON = "json"
    CSV = "csv"
    SQLITE = "sqlite"
