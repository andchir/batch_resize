#!/usr/bin/env python3
"""
Test script for --preview-only functionality in rename.py.
Tests that --preview-only works correctly and doesn't modify files.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import rename module
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess


def create_test_files(test_folder: Path) -> list:
    """Create test files in the test folder."""
    test_files = [
        "photo_001.jpg",
        "photo_002.jpg",
        "image_010.png",
        "document_05.txt",
        "file123.pdf"
    ]

    for filename in test_files:
        (test_folder / filename).touch()

    return test_files


def get_files_in_folder(folder: Path) -> set:
    """Get all filenames in folder."""
    return {f.name for f in folder.iterdir() if f.is_file()}


def run_rename_script(folder: Path, *args) -> tuple:
    """Run rename.py with given arguments."""
    script_path = Path(__file__).parent.parent / "rename.py"
    cmd = ["python3", str(script_path), str(folder)] + list(args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return result.returncode, result.stdout, result.stderr


def test_preview_only():
    """Test that --preview-only doesn't actually rename files."""
    print("=" * 70)
    print("TEST: --preview-only doesn't modify files")
    print("=" * 70)

    # Create temporary test folder
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_folder = Path(tmp_dir)

        # Create test files
        original_files = create_test_files(test_folder)
        print(f"\nCreated {len(original_files)} test files:")
        for f in sorted(original_files):
            print(f"  - {f}")

        # Get original file list
        files_before = get_files_in_folder(test_folder)

        # Run rename with --preview-only
        print("\nRunning: python rename.py [folder] name sequential --preview-only")
        print("-" * 70)
        returncode, stdout, stderr = run_rename_script(
            test_folder,
            "name",
            "sequential",
            "--preview-only"
        )

        print(stdout)

        if stderr:
            print("STDERR:", stderr)

        # Get file list after preview
        files_after = get_files_in_folder(test_folder)

        # Verify files are unchanged
        if files_before == files_after:
            print("\n✓ PASSED: Files remain unchanged after --preview-only")
            print(f"  Before: {sorted(files_before)}")
            print(f"  After:  {sorted(files_after)}")
            return True
        else:
            print("\n✗ FAILED: Files were modified!")
            print(f"  Before: {sorted(files_before)}")
            print(f"  After:  {sorted(files_after)}")
            return False


def test_preview_only_output():
    """Test that --preview-only shows correct preview output."""
    print("\n" + "=" * 70)
    print("TEST: --preview-only shows correct output")
    print("=" * 70)

    # Create temporary test folder
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_folder = Path(tmp_dir)

        # Create test files
        original_files = create_test_files(test_folder)
        print(f"\nCreated {len(original_files)} test files:")
        for f in sorted(original_files):
            print(f"  - {f}")

        # Run rename with --preview-only and prefix
        print("\nRunning: python rename.py [folder] number sequential --prefix 'file_' --preview-only")
        print("-" * 70)
        returncode, stdout, stderr = run_rename_script(
            test_folder,
            "number",
            "sequential",
            "--prefix", "file_",
            "--preview-only"
        )

        print(stdout)

        # Check that output contains expected strings
        expected_strings = [
            "Preview mode",
            "->",  # Arrow showing rename
            "Preview complete! No files were actually renamed"
        ]

        all_found = True
        for expected in expected_strings:
            if expected not in stdout:
                print(f"\n✗ Missing expected string: '{expected}'")
                all_found = False

        if all_found:
            print("\n✓ PASSED: Output contains all expected strings")
            return True
        else:
            print("\n✗ FAILED: Some expected strings not found in output")
            return False


def test_both_flags():
    """Test that both --dry-run and --preview-only can work (preview-only takes precedence in message)."""
    print("\n" + "=" * 70)
    print("TEST: --preview-only with --dry-run (both flags)")
    print("=" * 70)

    # Create temporary test folder
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_folder = Path(tmp_dir)

        # Create test files
        original_files = create_test_files(test_folder)
        print(f"\nCreated {len(original_files)} test files")

        # Get original file list
        files_before = get_files_in_folder(test_folder)

        # Run rename with both flags
        print("\nRunning: python rename.py [folder] name sequential --dry-run --preview-only")
        print("-" * 70)
        returncode, stdout, stderr = run_rename_script(
            test_folder,
            "name",
            "sequential",
            "--dry-run",
            "--preview-only"
        )

        print(stdout)

        # Get file list after
        files_after = get_files_in_folder(test_folder)

        # Verify files are unchanged
        if files_before == files_after:
            print("\n✓ PASSED: Files remain unchanged with both flags")
            return True
        else:
            print("\n✗ FAILED: Files were modified!")
            return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("TESTING --preview-only FUNCTIONALITY")
    print("=" * 70)

    tests = [
        ("Preview Only No Modification", test_preview_only),
        ("Preview Only Output Format", test_preview_only_output),
        ("Both Flags Together", test_both_flags),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ TEST FAILED WITH EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
