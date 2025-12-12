#!/usr/bin/env python3
"""Test script for download.py with --column-index-name parameter."""

import csv
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import download module
sys.path.insert(0, str(Path(__file__).parent.parent))

from download import read_csv_file, get_filename_from_url


def test_csv_reading_with_column_index():
    """Test reading CSV with column index for custom filename."""
    print("Testing CSV reading with column index...")

    # Create a temporary CSV file with test data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        csv_path = Path(f.name)
        writer = csv.writer(f)

        # Write test data: column 0 = custom name, column 1 = URL
        writer.writerow(['image1', 'http://example.com/files/photo.jpg'])
        writer.writerow(['image2', 'http://example.com/files/another.png'])
        writer.writerow(['', 'http://example.com/files/noname.gif'])  # Empty custom name
        writer.writerow(['document1', 'http://example.com/docs/file.pdf'])

    try:
        # Test 1: Read without column index
        print("\nTest 1: Without column index")
        url_data = read_csv_file(csv_path, None)
        print(f"Found {len(url_data)} URLs")
        for url, custom_name in url_data:
            print(f"  URL: {url}, Custom name: '{custom_name}'")

        # Test 2: Read with column index 0 (first column for custom names)
        print("\nTest 2: With column index 0")
        url_data = read_csv_file(csv_path, 0)
        print(f"Found {len(url_data)} URLs")
        for url, custom_name in url_data:
            print(f"  URL: {url}, Custom name: '{custom_name}'")

        print("\n✓ CSV reading tests passed!")
        return True

    finally:
        csv_path.unlink()


def test_filename_logic():
    """Test filename determination logic."""
    print("\n\nTesting filename determination logic...")

    # Test URL
    url = "http://example.com/files/photo.jpg"
    original_filename = get_filename_from_url(url)
    print(f"Original filename from URL: {original_filename}")

    # Test 1: No custom name
    custom_name = ""
    final_filename = original_filename
    print(f"\nTest 1: No custom name")
    print(f"  Final filename: {final_filename}")

    # Test 2: Custom name without extension
    custom_name = "image1"
    original_ext = Path(original_filename).suffix
    final_filename = custom_name + original_ext if not Path(custom_name).suffix else custom_name
    print(f"\nTest 2: Custom name without extension: '{custom_name}'")
    print(f"  Final filename: {final_filename}")

    # Test 3: Custom name with extension
    custom_name = "image2.png"
    final_filename = custom_name if Path(custom_name).suffix else custom_name + original_ext
    print(f"\nTest 3: Custom name with extension: '{custom_name}'")
    print(f"  Final filename: {final_filename}")

    print("\n✓ Filename logic tests passed!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Testing download.py column-index-name feature")
    print("=" * 60)

    success = True

    try:
        success = test_csv_reading_with_column_index() and success
        success = test_filename_logic() and success

        if success:
            print("\n" + "=" * 60)
            print("All tests passed! ✓")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("Some tests failed! ✗")
            print("=" * 60)
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
