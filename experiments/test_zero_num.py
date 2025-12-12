#!/usr/bin/env python3
"""
Test script for zero_num parameter in rename.py
Tests zero-padding functionality for numbered filenames.
"""

import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path to import rename module
sys.path.insert(0, str(Path(__file__).parent.parent))

from rename import rename_files


def test_zero_num():
    """Test zero_num parameter with different values."""
    # Create a temporary directory for testing
    test_dir = Path(tempfile.mkdtemp(prefix="test_zero_num_"))

    try:
        print(f"Testing in directory: {test_dir}")
        print("=" * 60)

        # Create test files
        test_files = [
            "file_1.mp4",
            "file_2.mp4",
            "file_5.mp4",
            "file_9.mp4",
            "file_10.mp4",
            "file_15.mp4"
        ]

        for filename in test_files:
            (test_dir / filename).touch()

        print(f"\nCreated {len(test_files)} test files")
        print("Original files:", sorted([f.name for f in test_dir.iterdir()]))

        # Test 1: zero_num=0 (no padding - default)
        print("\n" + "=" * 60)
        print("Test 1: zero_num=0 (no padding)")
        print("=" * 60)
        successful, failed = rename_files(
            test_dir,
            sort_type='number',
            rename_type='numbers_only_at_end',
            prefix='',
            suffix='',
            dry_run=True,
            zero_num=0
        )
        print(f"Result: {successful} successful, {failed} failed")

        # Test 2: zero_num=1 (padding to 2 digits: 09, 10)
        print("\n" + "=" * 60)
        print("Test 2: zero_num=1 (padding to 2 digits)")
        print("=" * 60)
        successful, failed = rename_files(
            test_dir,
            sort_type='number',
            rename_type='numbers_only_at_end',
            prefix='',
            suffix='',
            dry_run=True,
            zero_num=1
        )
        print(f"Result: {successful} successful, {failed} failed")

        # Test 3: zero_num=2 (padding to 3 digits: 009, 010)
        print("\n" + "=" * 60)
        print("Test 3: zero_num=2 (padding to 3 digits)")
        print("=" * 60)
        successful, failed = rename_files(
            test_dir,
            sort_type='number',
            rename_type='numbers_only_at_end',
            prefix='',
            suffix='',
            dry_run=True,
            zero_num=2
        )
        print(f"Result: {successful} successful, {failed} failed")

        # Test 4: Actually perform rename with zero_num=1
        print("\n" + "=" * 60)
        print("Test 4: Actual rename with zero_num=1")
        print("=" * 60)
        successful, failed = rename_files(
            test_dir,
            sort_type='number',
            rename_type='numbers_only_at_end',
            prefix='',
            suffix='',
            dry_run=False,
            zero_num=1
        )
        print(f"\nResult: {successful} successful, {failed} failed")
        print("Final files:", sorted([f.name for f in test_dir.iterdir()]))

        # Verify the results
        print("\n" + "=" * 60)
        print("Verification:")
        print("=" * 60)
        final_files = sorted([f.name for f in test_dir.iterdir()])
        expected_files = ['01.mp4', '02.mp4', '05.mp4', '09.mp4', '10.mp4', '15.mp4']

        if final_files == expected_files:
            print("✓ Test PASSED! Files renamed correctly with zero_num=1")
            print(f"  Expected: {expected_files}")
            print(f"  Got:      {final_files}")
            return True
        else:
            print("✗ Test FAILED! Files not renamed as expected")
            print(f"  Expected: {expected_files}")
            print(f"  Got:      {final_files}")
            return False

    finally:
        # Clean up temporary directory
        shutil.rmtree(test_dir)
        print(f"\nCleaned up test directory: {test_dir}")


def test_zero_num_with_sequential():
    """Test zero_num parameter with sequential renaming."""
    test_dir = Path(tempfile.mkdtemp(prefix="test_zero_num_seq_"))

    try:
        print("\n" + "=" * 60)
        print("Test: zero_num with sequential renaming")
        print("=" * 60)
        print(f"Testing in directory: {test_dir}")

        # Create test files
        test_files = ["a.txt", "b.txt", "c.txt"]
        for filename in test_files:
            (test_dir / filename).touch()

        print(f"\nCreated {len(test_files)} test files")
        print("Original files:", sorted([f.name for f in test_dir.iterdir()]))

        # Test with zero_num=2
        print("\nRenaming with sequential and zero_num=2...")
        successful, failed = rename_files(
            test_dir,
            sort_type='name',
            rename_type='sequential',
            prefix='',
            suffix='',
            dry_run=False,
            zero_num=2
        )

        print(f"Result: {successful} successful, {failed} failed")
        final_files = sorted([f.name for f in test_dir.iterdir()])
        print("Final files:", final_files)

        expected_files = ['001.txt', '002.txt', '003.txt']
        if final_files == expected_files:
            print("✓ Test PASSED! Sequential renaming with zero_num=2 works correctly")
            return True
        else:
            print("✗ Test FAILED!")
            print(f"  Expected: {expected_files}")
            print(f"  Got:      {final_files}")
            return False

    finally:
        shutil.rmtree(test_dir)
        print(f"Cleaned up test directory: {test_dir}")


if __name__ == "__main__":
    print("Testing zero_num parameter implementation")
    print("=" * 60)

    test1_passed = test_zero_num()
    test2_passed = test_zero_num_with_sequential()

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"Test 1 (zero_num with numbers_only_at_end): {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Test 2 (zero_num with sequential): {'PASSED' if test2_passed else 'FAILED'}")

    if test1_passed and test2_passed:
        print("\n✓ All tests PASSED!")
        sys.exit(0)
    else:
        print("\n✗ Some tests FAILED!")
        sys.exit(1)
