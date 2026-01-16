#!/usr/bin/env python3
"""
Test script to verify the translation fix for issue #35.

This script tests that the "renamed_count" translation key works correctly
with a single argument, avoiding the IndexError that occurred with "renamed".
"""

import sys
from pathlib import Path

# Add parent directory to path to import translations
sys.path.insert(0, str(Path(__file__).parent.parent))

from translations import Translations


def test_renamed_count_translation():
    """Test that renamed_count translation works with single argument."""
    print("Testing renamed_count translation fix...")

    # Test English translation
    translator_en = Translations("en")
    result_en = translator_en.get("renamed_count", 5)
    expected_en = "Renamed: 5"
    print(f"English: {result_en}")
    assert result_en == expected_en, f"Expected '{expected_en}', got '{result_en}'"

    # Test Russian translation
    translator_ru = Translations("ru")
    result_ru = translator_ru.get("renamed_count", 5)
    expected_ru = "Переименовано: 5"
    print(f"Russian: {result_ru}")
    assert result_ru == expected_ru, f"Expected '{expected_ru}', got '{result_ru}'"

    print("✓ All tests passed!")


def test_renamed_translation_still_works():
    """Test that the original 'renamed' translation still works for individual renames."""
    print("\nTesting original 'renamed' translation...")

    # Test English translation
    translator_en = Translations("en")
    result_en = translator_en.get("renamed", 1, "old.jpg", "new.jpg")
    expected_en = "[1] Renamed: old.jpg -> new.jpg"
    print(f"English: {result_en}")
    assert result_en == expected_en, f"Expected '{expected_en}', got '{result_en}'"

    # Test Russian translation
    translator_ru = Translations("ru")
    result_ru = translator_ru.get("renamed", 1, "old.jpg", "new.jpg")
    expected_ru = "[1] Переименовано: old.jpg -> new.jpg"
    print(f"Russian: {result_ru}")
    assert result_ru == expected_ru, f"Expected '{expected_ru}', got '{result_ru}'"

    print("✓ All tests passed!")


def test_edge_cases():
    """Test edge cases to ensure robustness."""
    print("\nTesting edge cases...")

    translator_en = Translations("en")

    # Test with 0
    result = translator_en.get("renamed_count", 0)
    print(f"Zero count: {result}")
    assert result == "Renamed: 0"

    # Test with large number
    result = translator_en.get("renamed_count", 1000)
    print(f"Large count: {result}")
    assert result == "Renamed: 1000"

    print("✓ All edge case tests passed!")


if __name__ == "__main__":
    try:
        test_renamed_count_translation()
        test_renamed_translation_still_works()
        test_edge_cases()
        print("\n" + "=" * 50)
        print("All tests passed successfully!")
        print("=" * 50)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
