#!/usr/bin/env python3
"""
Experiment script to test download.py functionality.
Creates sample CSV, XLSX files with URLs and tests the download script.
"""

import csv
import os
import sys
from pathlib import Path

# Add parent directory to path to import download module
sys.path.insert(0, str(Path(__file__).parent.parent))

import download


def create_sample_csv(output_path: Path):
    """Create a sample CSV file with URLs."""
    data = [
        ['Name', 'URL', 'Description'],
        ['Python Logo', 'https://www.python.org/static/img/python-logo.png', 'Python programming language logo'],
        ['Sample Text', 'https://www.example.com/sample.txt', 'A sample text file'],
        ['GitHub Logo', 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png', 'GitHub mark logo'],
        ['No URL here', 'Just some text', 'This row has no URL'],
        ['Multiple URLs', 'Check https://www.python.org and https://www.github.com', 'Two URLs in one cell'],
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

    print(f"Created sample CSV: {output_path}")


def create_sample_xlsx(output_path: Path):
    """Create a sample XLSX file with URLs."""
    try:
        import openpyxl
        from openpyxl.worksheet.hyperlink import Hyperlink

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "URLs"

        # Add header
        sheet['A1'] = 'Name'
        sheet['B1'] = 'URL'
        sheet['C1'] = 'Description'

        # Add data with URLs
        data = [
            ('Python Logo', 'https://www.python.org/static/img/python-logo.png', 'Python logo'),
            ('Text in cell', 'https://www.example.com/test.txt', 'Sample text'),
            ('Multiple URLs', 'https://httpbin.org/image/png and https://httpbin.org/image/jpeg', 'Two URLs'),
        ]

        for i, (name, url, desc) in enumerate(data, start=2):
            sheet[f'A{i}'] = name
            sheet[f'B{i}'] = url
            sheet[f'C{i}'] = desc

            # Add hyperlink to column B
            sheet[f'B{i}'].hyperlink = url

        workbook.save(output_path)
        print(f"Created sample XLSX: {output_path}")

    except ImportError:
        print("openpyxl not installed, skipping XLSX creation")


def test_url_extraction():
    """Test URL extraction from text."""
    print("\n=== Testing URL Extraction ===")

    test_cases = [
        "Check https://www.python.org for more info",
        "Visit http://github.com and http://gitlab.com",
        "No URLs here",
        "https://example.com/path/to/file.pdf",
        "Mixed content: see https://www.google.com for details",
    ]

    for text in test_cases:
        urls = download.extract_urls_from_text(text)
        print(f"Text: {text}")
        print(f"Found URLs: {urls}\n")


def test_filename_extraction():
    """Test filename extraction from URLs."""
    print("\n=== Testing Filename Extraction ===")

    test_urls = [
        "https://www.example.com/path/to/file.pdf",
        "https://www.example.com/image.png",
        "https://www.example.com/",
        "https://www.example.com/path/to/directory/",
        "https://www.example.com/file%20with%20spaces.txt",
    ]

    for url in test_urls:
        filename = download.get_filename_from_url(url)
        print(f"URL: {url}")
        print(f"Filename: {filename}\n")


def test_csv_reading():
    """Test reading URLs from CSV file."""
    print("\n=== Testing CSV Reading ===")

    # Create temp directory
    temp_dir = Path(__file__).parent / "temp"
    temp_dir.mkdir(exist_ok=True)

    csv_path = temp_dir / "test.csv"
    create_sample_csv(csv_path)

    urls = download.read_csv_file(csv_path)
    print(f"URLs found in CSV: {urls}")
    print(f"Total URLs: {len(urls)}")


def test_xlsx_reading():
    """Test reading URLs from XLSX file."""
    print("\n=== Testing XLSX Reading ===")

    try:
        import openpyxl

        # Create temp directory
        temp_dir = Path(__file__).parent / "temp"
        temp_dir.mkdir(exist_ok=True)

        xlsx_path = temp_dir / "test.xlsx"
        create_sample_xlsx(xlsx_path)

        urls = download.read_xlsx_file(xlsx_path)
        print(f"URLs found in XLSX: {urls}")
        print(f"Total URLs: {len(urls)}")

    except ImportError:
        print("openpyxl not installed, skipping XLSX test")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing download.py functionality")
    print("=" * 60)

    test_url_extraction()
    test_filename_extraction()
    test_csv_reading()
    test_xlsx_reading()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
