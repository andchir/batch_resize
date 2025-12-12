#!/usr/bin/env python3
"""
Unit tests for rename.py functions.
"""

import sys
from pathlib import Path

# Add parent directory to path to import rename module
sys.path.insert(0, str(Path(__file__).parent.parent))

from rename import (
    natural_sort_key,
    extract_number_at_end,
    extract_numbers_only,
    extract_text_only
)


def test_natural_sort_key():
    """Test natural sorting key generation."""
    print("Testing natural_sort_key()...")

    # Test cases: list of filenames and their expected sort order
    test_files = [
        "file10.txt",
        "file2.txt",
        "file1.txt",
        "file20.txt",
        "gr_20251210_153029_70_PreviewFemale3D_10.mp4",
        "gr_20251210_153029_70_PreviewFemale3D_9.mp4",
        "gr_20251210_153029_70_PreviewFemale3D_2.mp4",
        "gr_20251210_153029_70_PreviewFemale3D_1.mp4",
    ]

    sorted_files = sorted(test_files, key=natural_sort_key)

    expected_order = [
        "file1.txt",
        "file2.txt",
        "file10.txt",
        "file20.txt",
        "gr_20251210_153029_70_PreviewFemale3D_1.mp4",
        "gr_20251210_153029_70_PreviewFemale3D_2.mp4",
        "gr_20251210_153029_70_PreviewFemale3D_9.mp4",
        "gr_20251210_153029_70_PreviewFemale3D_10.mp4",
    ]

    assert sorted_files == expected_order, f"Expected {expected_order}, got {sorted_files}"
    print("  ✓ Natural sorting works correctly")

    # Show the sorting
    print("\n  Sorted order:")
    for i, f in enumerate(sorted_files, 1):
        print(f"    [{i}] {f}")


def test_extract_number_at_end():
    """Test extraction of trailing number from filename."""
    print("\nTesting extract_number_at_end()...")

    test_cases = [
        # (filename, expected_number)
        ("PreviewFemale3D_9", 9),
        ("PreviewFemale3D_10", 10),
        ("file_123", 123),
        ("ending123", 123),
        ("file123456", 123456),
        ("file_no_number", 0),
        ("another_file", 0),
        ("", 0),
        ("test", 0),
        ("a1b2c3", 3),
    ]

    for filename, expected in test_cases:
        result = extract_number_at_end(filename)
        assert result == expected, f"For '{filename}': expected {expected}, got {result}"
        print(f"  ✓ '{filename}' -> {result}")


def test_extract_numbers_only():
    """Test extraction of all numbers from filename."""
    print("\nTesting extract_numbers_only()...")

    test_cases = [
        # (filename, expected_result)
        ("file123abc456", "123456"),
        ("no_numbers", ""),
        ("12345", "12345"),
        ("a1b2c3", "123"),
        ("PreviewFemale3D_9", "39"),  # 3 from "3D" and 9 from "_9"
    ]

    for filename, expected in test_cases:
        result = extract_numbers_only(filename)
        assert result == expected, f"For '{filename}': expected '{expected}', got '{result}'"
        print(f"  ✓ '{filename}' -> '{result}'")


def test_extract_text_only():
    """Test extraction of text (removing numbers) from filename."""
    print("\nTesting extract_text_only()...")

    test_cases = [
        # (filename, expected_result)
        ("file123abc456", "fileabc"),
        ("no_numbers", "no_numbers"),
        ("12345", ""),
        ("a1b2c3", "abc"),
        ("PreviewFemale3D_9", "PreviewFemaleD_"),
    ]

    for filename, expected in test_cases:
        result = extract_text_only(filename)
        assert result == expected, f"For '{filename}': expected '{expected}', got '{result}'"
        print(f"  ✓ '{filename}' -> '{result}'")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Running unit tests for rename.py functions")
    print("=" * 60)

    try:
        test_natural_sort_key()
        test_extract_number_at_end()
        test_extract_numbers_only()
        test_extract_text_only()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
