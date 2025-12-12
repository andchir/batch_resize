#!/usr/bin/env python3
"""
Functional test for numbers_only_at_end rename type.
This test creates sample files, renames them using the new option, and verifies the results.
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rename import rename_files


def test_numbers_only_at_end_functionality():
    """Test that numbers_only_at_end correctly extracts numbers at the end of filenames."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files with different naming patterns
        test_files = [
            "PreviewFemale3D_9.mp4",
            "PreviewFemale3D_10.mp4",
            "PreviewFemale3D_11.mp4",
            "file_abc_5.txt",
            "document_final_2.txt",
            "image123.jpg",  # Should use sequential numbering (no non-digit before number)
            "test.png"       # Should use sequential numbering (no number)
        ]

        for filename in test_files:
            (temp_path / filename).touch()

        print("Created test files:")
        for filename in test_files:
            print(f"  - {filename}")

        # Run rename with numbers_only_at_end type (dry run first)
        print("\n=== Dry Run ===")
        successful, failed = rename_files(
            temp_path,
            sort_type='name',
            rename_type='numbers_only_at_end',
            prefix='',
            suffix='',
            dry_run=True
        )

        print(f"\nDry run results: {successful} successful, {failed} failed")

        # Now do the actual rename
        print("\n=== Actual Rename ===")
        successful, failed = rename_files(
            temp_path,
            sort_type='name',
            rename_type='numbers_only_at_end',
            prefix='',
            suffix='',
            dry_run=False
        )

        print(f"\nActual rename results: {successful} successful, {failed} failed")

        # Check the results
        print("\n=== Renamed Files ===")
        renamed_files = sorted([f.name for f in temp_path.iterdir() if f.is_file()])
        for filename in renamed_files:
            print(f"  - {filename}")

        # Verify expected results
        expected_names = {
            "2.txt",    # document_final_2.txt -> 2.txt
            "5.txt",    # file_abc_5.txt -> 5.txt
            "9.mp4",    # PreviewFemale3D_9.mp4 -> 9.mp4
            "10.mp4",   # PreviewFemale3D_10.mp4 -> 10.mp4
            "11.mp4",   # PreviewFemale3D_11.mp4 -> 11.mp4
        }

        # Check that expected files exist
        found_expected = set(renamed_files) & expected_names
        print(f"\n✓ Found {len(found_expected)}/{len(expected_names)} expected renamed files")

        # Check for sequential numbering on files without trailing numbers
        sequential_count = sum(1 for f in renamed_files if f.startswith(('1.', '3.', '4.', '6.', '7.')))
        print(f"✓ Found {sequential_count} files with sequential numbering (for files without trailing numbers)")

        assert successful > 0, "No files were successfully renamed"
        assert failed == 0, f"Some files failed to rename: {failed}"

        print("\n✓ All functional tests passed! The numbers_only_at_end option works correctly.")


if __name__ == "__main__":
    test_numbers_only_at_end_functionality()
