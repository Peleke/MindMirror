from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from cachetools import TTLCache
import openfoodfacts
import httpx


class OffClient:
    """Thin wrapper around the official Open Food Facts Python SDK.

    Provides:
    - get_product_by_barcode via v2
    - search_filtered via v2 (structured filters)
    - search_fulltext via HTTP v2 search (async)
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
        # Keep UA for raw HTTP calls
        self._ua = ua
        # Feature flag for Search-a-licious/fulltext
        env_flag = os.getenv("OFF_SEARCHALICIOUS_ENABLED", "false").lower() == "true"
        self.searchalicous_enabled = searchalicous_enabled or env_flag
        # Simple in-process caches
        self._detail_cache: TTLCache[str, dict] = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl_seconds)
        self._search_cache: TTLCache[str, dict] = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl_seconds)
        try:
            print(f"[OFF] Initialized API client. UA='{ua}', searchalicous_enabled={self.searchalicous_enabled}")
        except Exception:
            pass

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
            print(f"[OFF] get_product_by_barcode code={normalized} fields={fields}")
            result = self.api.product.get(normalized, fields=fields)
        except Exception as exc:
            print(f"[OFF] get_product_by_barcode error: {exc}")
            result = None

        if not result or (isinstance(result, dict) and result.get("status") == 0):
            print("[OFF] get_product_by_barcode: not found")
            return None

        # The SDK returns a dict already filtered by fields when fields is provided
        self._detail_cache[cache_key] = result
        print("[OFF] get_product_by_barcode: hit")
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
            print(f"[OFF] search_filtered filters={filters} fields={fields} page_size={page_size}")
            # SDK: returns a dict with keys like products, count, etc.
            response = self.api.product.search({**filters, "fields": fields or [], "page_size": page_size})
            products = response.get("products", []) if isinstance(response, dict) else []
        except Exception as exc:
            print(f"[OFF] search_filtered error: {exc}")
            products = []

        self._search_cache[cache_key] = products
        print(f"[OFF] search_filtered results={len(products)}")
        return products

    async def search_fulltext(self, query: str, page_size: int = 10) -> List[Dict[str, Any]]:
        """Full-text style search using OFF v2 HTTP search endpoint (async)."""
        if not self.searchalicous_enabled:
            print("[OFF] search_fulltext disabled by flag")
            return []
        cache_key = f"searcht:{query}:{page_size}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]  # type: ignore[return-value]

        params = {
            "search_terms": query,
            "search_simple": 1,
            "sort_by": "popularity_key",
            "page_size": page_size,
            "lang": "en",
            "fields": ",".join([
                "code",
                "product_name",
                "brands",
                "image_url",
                "nutrition_grades",
                "nutriscore_data",
                "nutriments",
                "serving_size",
                "serving_quantity",
            ]),
        }
        try:
            print(f"[OFF] search_fulltext query='{query}' page_size={page_size} (HTTP v2 async)")
            async with httpx.AsyncClient(timeout=8.0, headers={"User-Agent": self._ua}) as client:
                resp = await client.get("https://world.openfoodfacts.org/api/v2/search", params=params)
                resp.raise_for_status()
                data = resp.json()
            results: List[Dict[str, Any]] = data.get("products", []) if isinstance(data, dict) else []
        except Exception as exc:
            print(f"[OFF] search_fulltext error: {exc}")
            results = []

        self._search_cache[cache_key] = results
        print(f"[OFF] search_fulltext results={len(results)}")
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