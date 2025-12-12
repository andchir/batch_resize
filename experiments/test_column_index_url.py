#!/usr/bin/env python3
"""Test script for download.py with --column-index-url parameter."""

import csv
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import download module
sys.path.insert(0, str(Path(__file__).parent.parent))

from download import read_csv_file, read_xlsx_file, read_xls_file


def test_csv_with_column_index_url():
    """Test CSV reading with column-index-url parameter."""
    print("=" * 60)
    print("Testing CSV with --column-index-url")
    print("=" * 60)

    # Create a temporary CSV file with test data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        csv_path = Path(f.name)
        writer = csv.writer(f)

        # Write test data: column 0 = name, column 1 = URL, column 2 = description with URL
        writer.writerow(['Name', 'URL', 'Description'])
        writer.writerow(['image1', 'http://example.com/files/photo.jpg', 'See http://example.com/wrong.png'])
        writer.writerow(['image2', 'http://example.com/files/another.png', 'See http://example.com/wrong2.png'])
        writer.writerow(['no-url', 'not a url', 'This has http://example.com/wrong3.png'])
        writer.writerow(['doc1', 'http://example.com/docs/file.pdf', 'Text here'])

    try:
        # Test 1: Without column_index_url (check all cells)
        print("\nTest 1: Without --column-index-url (default -1, check all cells)")
        url_data = read_csv_file(csv_path, None, -1)
        print(f"Found {len(url_data)} URLs:")
        for url, custom_name in url_data:
            print(f"  URL: {url}")
        # We should find all URLs from all cells (3 from column 1 + 3 from column 2 = 6)
        expected_count = 6
        assert len(url_data) == expected_count, f"Expected {expected_count} URLs, got {len(url_data)}"
        print("✓ Test 1 passed")

        # Test 2: With column_index_url=1 (only check column 1 for URLs)
        print("\nTest 2: With --column-index-url=1 (check only column 1)")
        url_data = read_csv_file(csv_path, None, 1)
        print(f"Found {len(url_data)} URLs:")
        for url, custom_name in url_data:
            print(f"  URL: {url}")
        expected_urls = [
            'http://example.com/files/photo.jpg',
            'http://example.com/files/another.png',
            'http://example.com/docs/file.pdf'
        ]
        assert len(url_data) == len(expected_urls), f"Expected {len(expected_urls)} URLs, got {len(url_data)}"
        for (url, _), expected_url in zip(url_data, expected_urls):
            assert url == expected_url, f"Expected {expected_url}, got {url}"
        print("✓ Test 2 passed")

        # Test 3: With column_index_url=2 (only check column 2 for URLs)
        print("\nTest 3: With --column-index-url=2 (check only column 2)")
        url_data = read_csv_file(csv_path, None, 2)
        print(f"Found {len(url_data)} URLs:")
        for url, custom_name in url_data:
            print(f"  URL: {url}")
        expected_count = 3  # URLs from column 2 only
        assert len(url_data) == expected_count, f"Expected {expected_count} URLs, got {len(url_data)}"
        # Verify these are the "wrong" URLs from column 2
        assert any('wrong.png' in url for url, _ in url_data), "Should find wrong.png from column 2"
        print("✓ Test 3 passed")

        # Test 4: With column_index_url=0 (check column 0, which has no URLs)
        print("\nTest 4: With --column-index-url=0 (check column 0, no URLs)")
        url_data = read_csv_file(csv_path, None, 0)
        print(f"Found {len(url_data)} URLs:")
        assert len(url_data) == 0, f"Expected 0 URLs, got {len(url_data)}"
        print("✓ Test 4 passed")

        # Test 5: Combine with column_index_name
        print("\nTest 5: With both --column-index-url=1 and --column-index-name=0")
        url_data = read_csv_file(csv_path, 0, 1)
        print(f"Found {len(url_data)} URLs:")
        for url, custom_name in url_data:
            print(f"  URL: {url}, Custom name: '{custom_name}'")
        assert len(url_data) == 3, f"Expected 3 URLs, got {len(url_data)}"
        # Check that custom names are set
        assert url_data[0][1] == 'image1', f"Expected custom name 'image1', got '{url_data[0][1]}'"
        assert url_data[1][1] == 'image2', f"Expected custom name 'image2', got '{url_data[1][1]}'"
        print("✓ Test 5 passed")

        print("\n" + "=" * 60)
        print("All CSV tests passed! ✓")
        print("=" * 60)
        return True

    finally:
        csv_path.unlink()


def test_xlsx_with_column_index_url():
    """Test XLSX reading with column-index-url parameter."""
    try:
        import openpyxl
    except ImportError:
        print("\nSkipping XLSX tests (openpyxl not installed)")
        return True

    print("\n" + "=" * 60)
    print("Testing XLSX with --column-index-url")
    print("=" * 60)

    # Create a temporary XLSX file with test data
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        xlsx_path = Path(f.name)

    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Add header and data
    sheet['A1'] = 'Name'
    sheet['B1'] = 'URL'
    sheet['C1'] = 'Description'

    sheet['A2'] = 'image1'
    sheet['B2'] = 'http://example.com/files/photo.jpg'
    sheet['C2'] = 'See http://example.com/wrong.png'

    sheet['A3'] = 'image2'
    sheet['B3'] = 'http://example.com/files/another.png'
    sheet['C3'] = 'See http://example.com/wrong2.png'

    workbook.save(xlsx_path)

    try:
        # Test 1: Without column_index_url
        print("\nTest 1: Without --column-index-url (check all cells)")
        url_data = read_xlsx_file(xlsx_path, None, -1)
        print(f"Found {len(url_data)} URLs:")
        for url, custom_name in url_data:
            print(f"  URL: {url}")
        assert len(url_data) >= 4, f"Expected at least 4 URLs, got {len(url_data)}"
        print("✓ Test 1 passed")

        # Test 2: With column_index_url=1 (column B, 0-based index)
        print("\nTest 2: With --column-index-url=1 (check only column B)")
        url_data = read_xlsx_file(xlsx_path, None, 1)
        print(f"Found {len(url_data)} URLs:")
        for url, custom_name in url_data:
            print(f"  URL: {url}")
        expected_count = 2  # Only URLs from column B
        assert len(url_data) == expected_count, f"Expected {expected_count} URLs, got {len(url_data)}"
        assert 'photo.jpg' in url_data[0][0], "Should find photo.jpg"
        assert 'another.png' in url_data[1][0], "Should find another.png"
        print("✓ Test 2 passed")

        print("\n" + "=" * 60)
        print("All XLSX tests passed! ✓")
        print("=" * 60)
        return True

    finally:
        xlsx_path.unlink()


if __name__ == "__main__":
    print("Testing download.py --column-index-url feature\n")

    success = True

    try:
        success = test_csv_with_column_index_url() and success
        success = test_xlsx_with_column_index_url() and success

        if success:
            print("\n" + "=" * 60)
            print("ALL TESTS PASSED! ✓✓✓")
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
