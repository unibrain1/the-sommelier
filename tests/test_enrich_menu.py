"""Tests for enrich_menu.py — prompt building, JSON extraction, cache."""

import json
from unittest.mock import patch

from enrich_menu import (
    _normalize_enriched,
    build_enrichment_prompt,
    enrich_menu,
    load_cache,
    text_hash,
)
from wine_utils import extract_json


class TestTextHash:
    def test_deterministic(self):
        assert text_hash("Grilled chicken") == text_hash("Grilled chicken")

    def test_case_insensitive(self):
        assert text_hash("Grilled Chicken") == text_hash("grilled chicken")

    def test_strips_whitespace(self):
        assert text_hash("  chicken  ") == text_hash("chicken")

    def test_different_text_different_hash(self):
        assert text_hash("chicken") != text_hash("beef")

    def test_returns_16_chars(self):
        assert len(text_hash("anything")) == 16


class TestBuildEnrichmentPrompt:
    def test_includes_all_entries(self):
        entries = [
            {"meal": "Grilled chicken"},
            {"meal": "Pasta primavera"},
        ]
        prompt = build_enrichment_prompt(entries)
        assert "Grilled chicken" in prompt
        assert "Pasta primavera" in prompt

    def test_entries_are_indexed(self):
        entries = [{"meal": "Steak"}, {"meal": "Fish"}]
        prompt = build_enrichment_prompt(entries)
        assert '0: "Steak"' in prompt
        assert '1: "Fish"' in prompt

    def test_mentions_required_fields(self):
        prompt = build_enrichment_prompt([{"meal": "test"}])
        assert "protein" in prompt
        assert "preparation" in prompt
        assert "richness" in prompt
        assert "spice_heat" in prompt
        assert "pairing_priorities" in prompt


class TestExtractJson:
    def test_extracts_json_from_text(self):
        text = 'Here is the result: {"0": {"protein": "chicken"}} done.'
        result = extract_json(text)
        assert result == {"0": {"protein": "chicken"}}

    def test_handles_no_json(self):
        assert extract_json("no json here") == {}

    def test_handles_invalid_json(self):
        assert extract_json("{invalid: json}") == {}

    def test_handles_nested_json(self):
        text = '{"0": {"protein": "pork", "sides": ["kale", "potatoes"]}}'
        result = extract_json(text)
        assert result["0"]["sides"] == ["kale", "potatoes"]


class TestLoadCache:
    def test_missing_file_returns_empty(self, tmp_path):
        assert load_cache(tmp_path / "nonexistent.json") == {}

    def test_empty_file_returns_empty(self, tmp_path):
        p = tmp_path / "empty.json"
        p.write_text("")
        assert load_cache(p) == {}

    def test_valid_cache(self, tmp_path):
        p = tmp_path / "cache.json"
        data = {"abc123": {"protein": "chicken"}}
        p.write_text(json.dumps(data))
        assert load_cache(p) == data

    def test_invalid_json_returns_empty(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("{bad")
        assert load_cache(p) == {}


class TestNormalizeEnriched:
    """Unit tests for _normalize_enriched — scalar-field coercion before caching."""

    def test_scalar_list_coerced_to_first_string(self):
        result = _normalize_enriched({"protein": ["chicken", "shrimp"]})
        assert result["protein"] == "chicken"

    def test_scalar_single_element_list_coerced(self):
        result = _normalize_enriched({"richness": ["medium"]})
        assert result["richness"] == "medium"

    def test_all_ten_scalar_fields_coerced(self):
        scalar_fields = [
            "protein",
            "cut",
            "preparation",
            "sauce",
            "sauce_intensity",
            "cuisine",
            "richness",
            "acidity",
            "sweetness",
            "spice_heat",
        ]
        payload = {f: ["x"] for f in scalar_fields}
        result = _normalize_enriched(payload)
        for field in scalar_fields:
            assert result[field] == "x", (
                f"Expected '{field}' to be coerced to 'x', got {result[field]!r}"
            )

    def test_scalar_already_string_unchanged(self):
        result = _normalize_enriched({"protein": "beef"})
        assert result["protein"] == "beef"

    def test_scalar_int_coerced_to_string(self):
        result = _normalize_enriched({"richness": 3})
        assert result["richness"] == "3"

    def test_scalar_float_coerced_to_string(self):
        result = _normalize_enriched({"acidity": 0.7})
        assert result["acidity"] == "0.7"

    def test_scalar_none_unchanged(self):
        result = _normalize_enriched({"protein": None})
        assert "protein" in result
        assert result["protein"] is None

    def test_scalar_empty_list_field_omitted(self):
        result = _normalize_enriched({"protein": []})
        assert "protein" not in result

    def test_scalar_list_no_string_elements_field_omitted(self):
        # A list of ints contains no string elements, so the field should be omitted.
        result = _normalize_enriched({"protein": [42, 99]})
        assert "protein" not in result

    def test_array_field_sides_untouched(self):
        result = _normalize_enriched({"sides": ["potatoes", "kale"]})
        assert result["sides"] == ["potatoes", "kale"]

    def test_array_field_dominant_flavor_axis_untouched(self):
        # Single-element list on an array field must NOT be coerced to a bare string.
        result = _normalize_enriched({"dominant_flavor_axis": ["savory"]})
        assert result["dominant_flavor_axis"] == ["savory"]

    def test_array_field_pairing_priorities_untouched(self):
        result = _normalize_enriched({"pairing_priorities": ["match acidity"]})
        assert result["pairing_priorities"] == ["match acidity"]

    def test_array_single_element_not_coerced(self):
        # Critical boundary: single-element array fields must never be coerced to strings.
        result = _normalize_enriched({"sides": ["potatoes"]})
        assert result["sides"] == ["potatoes"]

    def test_mixed_realistic_payload(self):
        payload = {
            "protein": ["pork"],
            "preparation": ["grilled"],
            "richness": "medium",
            "sides": ["fingerlings", "kale"],
            "dominant_flavor_axis": ["savory", "smoky"],
            "pairing_priorities": ["match weight"],
        }
        result = _normalize_enriched(payload)
        assert result["protein"] == "pork"
        assert result["preparation"] == "grilled"
        assert result["richness"] == "medium"
        assert result["sides"] == ["fingerlings", "kale"]
        assert result["dominant_flavor_axis"] == ["savory", "smoky"]
        assert result["pairing_priorities"] == ["match weight"]

    def test_empty_dict_returns_empty_dict(self):
        assert _normalize_enriched({}) == {}

    def test_unknown_field_untouched(self):
        # Unrecognized fields that aren't in SCALAR_FIELDS pass through unchanged.
        result = _normalize_enriched({"future_field": ["val"]})
        assert result["future_field"] == ["val"]

    def test_returns_new_dict_not_mutates_input(self):
        original = {"protein": ["beef"]}
        _normalize_enriched(original)
        assert original["protein"] == ["beef"]


class TestEnrichMenuNormalizesBeforeCache:
    """Integration test: enrich_menu() applies _normalize_enriched before writing the cache."""

    def test_normalized_values_written_to_cache(self, tmp_path):
        menu_path = tmp_path / "menu.json"
        cache_path = tmp_path / "cache.json"

        menu_entry_text = "Grilled pork chop with potatoes"
        menu_path.write_text(
            json.dumps([{"date": "2026-06-01", "meal": menu_entry_text}]),
            encoding="utf-8",
        )

        # Simulate Claude returning a scalar field (protein) as a list, and an array field intact.
        mock_response = json.dumps(
            {
                "0": {
                    "protein": ["pork"],
                    "preparation": "grilled",
                    "sides": ["potatoes", "kale"],
                }
            }
        )

        with patch("enrich_menu.call_claude", return_value=mock_response):
            enrich_menu(menu_path, cache_path)

        assert cache_path.exists(), "Cache file was not written"
        cache = json.loads(cache_path.read_text(encoding="utf-8"))

        # Locate the cache entry by hashing the menu text the same way the module does.
        entry_hash = text_hash(menu_entry_text)
        assert entry_hash in cache, (
            f"Hash {entry_hash!r} not found in cache; keys: {list(cache)}"
        )

        entry = cache[entry_hash]
        assert entry["protein"] == "pork", (
            f"Expected protein coerced to 'pork' (string), got {entry['protein']!r}"
        )
        assert entry["preparation"] == "grilled", (
            f"Expected preparation 'grilled' unchanged, got {entry['preparation']!r}"
        )
        assert entry["sides"] == ["potatoes", "kale"], (
            f"Expected sides array preserved, got {entry['sides']!r}"
        )
