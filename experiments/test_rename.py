#!/usr/bin/env python3
"""
Test script for rename.py functionality.
Creates test files and tests all sorting and renaming modes.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import rename module
sys.path.insert(0, str(Path(__file__).parent.parent))

import rename


def create_test_files(test_dir: Path) -> None:
    """
    Create test files with various naming patterns.

    Args:
        test_dir: Directory where to create test files
    """
    test_files = [
        "photo_001.jpg",
        "photo_010.jpg",
        "photo_002.jpg",
        "image100text.png",
        "document25.txt",
        "file_5_final.pdf",
        "test.doc",
        "abc123def456.txt",
        "noNumbers.jpg",
        "123.png",
        "file 50 with spaces.txt",
    ]

    for filename in test_files:
        file_path = test_dir / filename
        file_path.write_text(f"Test content for {filename}")

    print(f"✓ Created {len(test_files)} test files")


def list_files(test_dir: Path, title: str) -> None:
    """
    List all files in directory.

    Args:
        test_dir: Directory to list
        title: Title to print
    """
    print(f"\n{title}")
    print("-" * 60)
    files = sorted([f.name for f in test_dir.iterdir() if f.is_file()])
    for i, filename in enumerate(files, 1):
        print(f"  [{i}] {filename}")
    print()


def test_extract_number():
    """Test number extraction from filenames."""
    print("\n" + "=" * 60)
    print("TEST 1: Extract Number from Filename")
    print("=" * 60)

    test_cases = [
        ("photo_001.jpg", (1, "photo_.jpg")),
        ("image100text.png", (100, "imagetext.png")),
        ("noNumbers.jpg", (0, "noNumbers.jpg")),
        ("123.png", (123, ".png")),
        ("file 50 with spaces.txt", (50, "file  with spaces.txt")),
    ]

    passed = 0
    failed = 0

    for filename, expected in test_cases:
        result = rename.extract_number_from_filename(filename)
        if result == expected:
            print(f"✓ '{filename}' -> number={result[0]}, text='{result[1]}'")
            passed += 1
        else:
            print(f"✗ '{filename}' -> Expected {expected}, got {result}")
            failed += 1

    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


def test_extract_text_only():
    """Test text-only extraction from filenames."""
    print("\n" + "=" * 60)
    print("TEST 2: Extract Text Only from Filename")
    print("=" * 60)

    test_cases = [
        ("photo_001.jpg", "photo_.jpg"),
        ("image100text.png", "imagetext.png"),
        ("abc123def456.txt", "abcdef.txt"),
        ("123.png", ".png"),
        ("noNumbers.jpg", "noNumbers.jpg"),
    ]

    passed = 0
    failed = 0

    for filename, expected in test_cases:
        result = rename.extract_text_only(filename)
        if result == expected:
            print(f"✓ '{filename}' -> '{result}'")
            passed += 1
        else:
            print(f"✗ '{filename}' -> Expected '{expected}', got '{result}'")
            failed += 1

    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


def test_extract_numbers_only():
    """Test numbers-only extraction from filenames."""
    print("\n" + "=" * 60)
    print("TEST 3: Extract Numbers Only from Filename")
    print("=" * 60)

    test_cases = [
        ("photo_001.jpg", "001"),
        ("image100text.png", "100"),
        ("abc123def456.txt", "123456"),
        ("noNumbers.jpg", ""),
        ("123.png", "123"),
    ]

    passed = 0
    failed = 0

    for filename, expected in test_cases:
        result = rename.extract_numbers_only(filename)
        if result == expected:
            print(f"✓ '{filename}' -> '{result}'")
            passed += 1
        else:
            print(f"✗ '{filename}' -> Expected '{expected}', got '{result}'")
            failed += 1

    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


def test_sorting(test_dir: Path):
    """Test file sorting functionality."""
    print("\n" + "=" * 60)
    print("TEST 4: File Sorting")
    print("=" * 60)

    files = rename.get_files_in_folder(test_dir)

    print("\nOriginal order:")
    for f in files[:5]:
        print(f"  {f.name}")
    print("  ...")

    # Test sort by name
    print("\nSort by name:")
    sorted_by_name = rename.sort_files(files, 'name')
    for f in sorted_by_name[:5]:
        print(f"  {f.name}")

    # Test sort by number
    print("\nSort by number:")
    sorted_by_number = rename.sort_files(files, 'number')
    for f in sorted_by_number[:5]:
        number, _ = rename.extract_number_from_filename(f.stem)
        print(f"  {f.name} (number: {number})")

    return True


def test_renaming_dry_run(test_dir: Path):
    """Test all renaming modes in dry-run."""
    print("\n" + "=" * 60)
    print("TEST 5: Renaming Modes (Dry Run)")
    print("=" * 60)

    # Test 5a: Sequential renaming
    print("\n--- Sequential Renaming (sort by name) ---")
    rename.rename_files(test_dir, 'name', 'sequential', dry_run=True)

    # Test 5b: Sequential with prefix/suffix
    print("\n--- Sequential with Prefix and Suffix ---")
    rename.rename_files(test_dir, 'name', 'sequential',
                       prefix='img_', suffix='_final', dry_run=True)

    # Test 5c: Numbers only
    print("\n--- Numbers Only (sort by number) ---")
    rename.rename_files(test_dir, 'number', 'numbers_only', dry_run=True)

    # Test 5d: Text only
    print("\n--- Text Only (sort by name) ---")
    rename.rename_files(test_dir, 'name', 'text_only', dry_run=True)

    return True


def test_actual_renaming():
    """Test actual file renaming in a temporary directory."""
    print("\n" + "=" * 60)
    print("TEST 6: Actual File Renaming")
    print("=" * 60)

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        test_files = [
            "photo_003.jpg",
            "photo_001.jpg",
            "photo_002.jpg",
        ]

        for filename in test_files:
            (temp_path / filename).write_text(f"Content: {filename}")

        print("\nBefore renaming:")
        list_files(temp_path, "Files in directory:")

        # Perform actual renaming
        print("Performing renaming (sequential with prefix)...")
        successful, failed = rename.rename_files(
            temp_path,
            'name',
            'sequential',
            prefix='image_',
            dry_run=False
        )

        print(f"\nRenaming result: {successful} successful, {failed} failed")

        print("\nAfter renaming:")
        list_files(temp_path, "Files in directory:")

        # Verify files were renamed
        files_after = list(temp_path.iterdir())
        expected_names = {'image_1.jpg', 'image_2.jpg', 'image_3.jpg'}
        actual_names = {f.name for f in files_after}

        if expected_names == actual_names:
            print("✓ Files renamed correctly!")
            return True
        else:
            print(f"✗ Unexpected filenames: {actual_names}")
            return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "=" * 60)
    print("TEST 7: Edge Cases")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test with files that would have duplicate names
        print("\n--- Testing duplicate name handling ---")
        (temp_path / "file1.txt").write_text("content1")
        (temp_path / "file2.txt").write_text("content2")
        (temp_path / "file3.txt").write_text("content3")

        list_files(temp_path, "Before renaming:")

        # Rename with text_only (all should get same base name)
        rename.rename_files(temp_path, 'name', 'text_only', dry_run=False)

        list_files(temp_path, "After renaming (duplicates handled):")

        # Check that all files still exist and have unique names
        files = list(temp_path.iterdir())
        if len(files) == 3 and len(set(f.name for f in files)) == 3:
            print("✓ Duplicate names handled correctly!")
            return True
        else:
            print("✗ Duplicate handling failed")
            return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RENAME.PY TEST SUITE")
    print("=" * 60)

    test_results = []

    # Run unit tests
    test_results.append(("Extract Number", test_extract_number()))
    test_results.append(("Extract Text Only", test_extract_text_only()))
    test_results.append(("Extract Numbers Only", test_extract_numbers_only()))

    # Create temporary test directory for integration tests
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        create_test_files(test_dir)

        list_files(test_dir, "Initial test files:")

        test_results.append(("Sorting", test_sorting(test_dir)))
        test_results.append(("Renaming Dry Run", test_renaming_dry_run(test_dir)))

    # Run actual renaming tests
    test_results.append(("Actual Renaming", test_actual_renaming()))
    test_results.append(("Edge Cases", test_edge_cases()))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
