from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from cachetools import TTLCache
import openfoodfacts


class OffClient:
    """Thin wrapper around the official Open Food Facts Python SDK.

    Provides:
    - get_product_by_barcode via v2
    - search_filtered via v2 (structured filters)
    - search_fulltext via Search-a-licious (stubbed HTTP to be added later)
    """

    def __init__(
        self,
        user_agent: Optional[str] = None,
        searchalicous_enabled: bool = False,
        cache_ttl_seconds: int = 12 * 60 * 60,
        cache_maxsize: int = 1024,
    ) -> None:
        ua = user_agent or os.getenv("OFF_USER_AGENT", "MindMirrorMeals/1.0 (+support@mindmirror.app)")
        # SDK API client
        self.api = openfoodfacts.API(user_agent=ua)
        # Feature flag for Search-a-licious
        self.searchalicous_enabled = searchalicous_enabled or os.getenv("OFF_SEARCHALICIOUS_ENABLED", "false").lower() == "true"
        # Simple in-process caches
        self._detail_cache: TTLCache[str, dict] = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl_seconds)
        self._search_cache: TTLCache[str, dict] = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl_seconds)

    # ---- Public methods ----

    def get_product_by_barcode(self, code: str, fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch product detail by barcode using v2.

        Returns a dict similar to the SDK output, or None if not found.
        """
        normalized = self._maybe_normalize_barcode(code)
        cache_key = f"detail:{normalized}:{','.join(fields) if fields else ''}"
        if cache_key in self._detail_cache:
            return self._detail_cache[cache_key]

        # SDK call
        try:
            result = self.api.product.get(normalized, fields=fields)
        except Exception:
            result = None

        if not result or (isinstance(result, dict) and result.get("status") == 0):
            return None

        # The SDK returns a dict already filtered by fields when fields is provided
        self._detail_cache[cache_key] = result
        return result

    def search_filtered(self, filters: Dict[str, Any], fields: Optional[List[str]] = None, page_size: int = 10) -> List[Dict[str, Any]]:
        """v2 structured search using SDK.

        Example filters:
        - {"brands_tags": "coca-cola"}
        - {"categories_tags_en": "Orange Juice"}
        - {"nutrition_grades_tags": "c"}
        """
        cache_key = f"searchf:{str(sorted(filters.items()))}:{','.join(fields) if fields else ''}:{page_size}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]  # type: ignore[return-value]

        try:
            # SDK: returns a dict with keys like products, count, etc.
            response = self.api.product.search({**filters, "fields": fields or [], "page_size": page_size})
            products = response.get("products", []) if isinstance(response, dict) else []
        except Exception:
            products = []

        self._search_cache[cache_key] = products
        return products

    def search_fulltext(self, query: str, page_size: int = 10) -> List[Dict[str, Any]]:
        """Search-a-licious full-text search (beta).

        Currently a stub; returns empty list unless OFF_SEARCHALICIOUS_ENABLED=true.
        The HTTP implementation can be added later.
        Docs: https://search.openfoodfacts.org/docs
        """
        if not self.searchalicous_enabled:
            return []
        cache_key = f"searcht:{query}:{page_size}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]  # type: ignore[return-value]

        # TODO: implement HTTP call to Search-a-licious API endpoint
        # Keep as empty for now; wire later behind feature flag
        results: List[Dict[str, Any]] = []
        self._search_cache[cache_key] = results
        return results

    # ---- Internal helpers ----

    def _maybe_normalize_barcode(self, code: str) -> str:
        """Optionally normalize barcodes.

        Note: OFF endpoints often accept standard EAN/UPC directly. We keep a no-op for now,
        and can implement stricter normalization later if needed. See:
        https://openfoodfacts.github.io/openfoodfacts-server/api/ref-barcode-normalization/
        """
        # No-op for now; return input
        return code.strip() 