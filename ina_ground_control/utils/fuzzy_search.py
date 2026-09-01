"""
Fuzzy search utilities for task searching using rapidfuzz.

This module provides fuzzy string matching capabilities to improve search functionality
by allowing for typos, partial matches, accent-insensitive matching, and similar variations.
"""

import logging
import unicodedata
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from rapidfuzz import fuzz

logger = logging.getLogger(__name__)


def strip_accents(text: str) -> str:
    """Remove accents/diacritics from a string (é -> e, ç -> c, etc.)."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


@dataclass
class FuzzySearchResult:
    """Container for fuzzy search results with scoring information."""

    item: Any
    score: float
    matched_field: str


class FuzzySearchEngine:
    """
    Engine for performing fuzzy search operations on tasks.

    Handles fuzzy string matching with accent normalization,
    allowing for typos and partial matches.
    """

    # Task fields that can be fuzzy-searched (and the default when none is given).
    SEARCHABLE_FIELDS: Tuple[str, ...] = ("name", "instruction", "documentation")

    def __init__(self, min_score: float = 75.0):
        self.min_score = min_score

    def _resolve_search_fields(
        self, search_fields: Optional[List[str]]
    ) -> Tuple[str, ...]:
        """Validate ``search_fields`` and fall back to all searchable fields.

        Args:
            search_fields: Subset of :data:`SEARCHABLE_FIELDS` to search, or
                ``None`` to search them all.

        Returns:
            The tuple of fields to search (all of them when ``None``).

        Raises:
            ValueError: If any provided field is not searchable.
        """
        if search_fields is None:
            return self.SEARCHABLE_FIELDS

        invalid = [f for f in search_fields if f not in self.SEARCHABLE_FIELDS]
        if invalid:
            raise ValueError(
                f"Invalid search field(s): {invalid}. "
                f"Allowed fields: {list(self.SEARCHABLE_FIELDS)}"
            )
        return tuple(search_fields)

    def search_tasks(
        self,
        tasks: List[Any],
        search_query: str,
        search_fields: Optional[List[str]] = None,
    ) -> List[FuzzySearchResult]:
        """
        Search through the tasks' textual fields using fuzzy matching.

        Args:
            tasks: The tasks to search.
            search_query: The query string.
            search_fields: Subset of ``name``/``instruction``/``documentation`` to
                search. When ``None`` (default) all three are searched.

        Returns:
            FuzzySearchResult list sorted by score (highest first).

        Raises:
            ValueError: If ``search_fields`` contains an unsupported field name.
        """
        fields = self._resolve_search_fields(search_fields)
        if not search_query or not tasks:
            return []

        results = []
        search_query_lower = search_query.lower().strip()

        for task in tasks:
            best_score = 0
            best_field = None

            # Search across the requested textual fields.
            for field in fields:
                value = getattr(task, field, None)
                if not value:
                    continue
                score = self._best_score(search_query_lower, value.lower())
                if score > best_score:
                    best_score = score
                    best_field = field

            if best_score >= self.min_score:
                results.append(
                    FuzzySearchResult(
                        item=task, score=best_score, matched_field=best_field
                    )
                )

        results.sort(key=lambda x: x.score, reverse=True)

        logger.debug(
            "Fuzzy search for '%s' found %d results (threshold: %.1f)",
            search_query,
            len(results),
            self.min_score,
        )

        return results

    def _best_score(self, query: str, target: str) -> float:
        """Return the best fuzzy score across multiple strategies, with accent normalization.

        partial_ratio and token_set_ratio are intentionally excluded: they are too
        permissive for short queries (e.g. "re" scores ~100 against "résumé" via
        partial_ratio), producing results that are too loosely related to the query.
        """
        query = strip_accents(query)
        target = strip_accents(target)
        return max(
            fuzz.ratio(query, target),
            fuzz.token_sort_ratio(query, target),
            fuzz.WRatio(query, target),
        )


class TaskSearchService:
    """
    Applies search (exact or fuzzy), sorting and pagination on a list of tasks.

    This separates search logic from the repository's DB query building.
    """

    @staticmethod
    def apply(
        tasks: List[Any],
        search: str | None = None,
        search_mode: str = "exact",
        min_score: float = 75.0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 0,
        size: int = 10,
    ) -> Tuple[List[Any], int]:
        """
        Filter, sort and paginate tasks.

        Args:
            tasks: Pre-filtered task list from the repository.
            search: Search query string.
            search_mode: 'exact' or 'fuzzy'.
            min_score: Minimum similarity score for fuzzy search (0-100).
            sort_by: 'name', 'created_at', or 'score' (fuzzy only).
            sort_order: 'asc' or 'desc'.
            page: Page number (0-based).
            size: Page size.

        Returns:
            (paginated_tasks, total_count)
        """
        if search and search_mode == "fuzzy":
            engine = FuzzySearchEngine(min_score=min_score)
            fuzzy_results = engine.search_tasks(tasks, search)
            filtered = [r.item for r in fuzzy_results]
        else:
            filtered = list(tasks)

        total = len(filtered)

        # Sort
        if sort_by != "score":
            reverse = sort_order == "desc"
            if sort_by == "name":
                filtered.sort(key=lambda t: t.name, reverse=reverse)
            else:
                filtered.sort(key=lambda t: t.created_at, reverse=reverse)

        # Paginate
        offset = page * size
        return filtered[offset : offset + size], total
