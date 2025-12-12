#!/usr/bin/env python3
"""
Test script to verify zero_num parameter is present in GUI.
This test checks the GUI code for the presence of the zero_num spinbox.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_gui_code_verification():
    """Verify that zero_num spinbox exists in GUI code."""
    gui_path = Path(__file__).parent.parent / "gui.py"

    print("Testing GUI code for zero_num parameter")
    print("=" * 60)
    print(f"Reading file: {gui_path}")

    with open(gui_path, 'r', encoding='utf-8') as f:
        gui_code = f.read()

    # Check for key elements
    checks = [
        ("rename_zero_num_spinbox", "Zero num spinbox widget"),
        ("self.rename_zero_num_spinbox.value()", "Getting zero_num value"),
        ("zero_num", "zero_num parameter"),
        ("Дополнение нулями", "Russian label for zero padding"),
        ("(0 = не используется, 1 = 09, 2 = 009)", "Help text for zero_num"),
    ]

    all_passed = True
    for search_str, description in checks:
        if search_str in gui_code:
            print(f"✓ Found: {description}")
        else:
            print(f"✗ Missing: {description}")
            all_passed = False

    # Check FileRenamerThread __init__ signature
    if "zero_num: int = 0" in gui_code:
        print("✓ Found: zero_num parameter in FileRenamerThread.__init__")
    else:
        print("✗ Missing: zero_num parameter in FileRenamerThread.__init__")
        all_passed = False

    # Check that zero_num is passed to generate_new_filename
    if "self.zero_num" in gui_code:
        print("✓ Found: self.zero_num in FileRenamerThread")
    else:
        print("✗ Missing: self.zero_num in FileRenamerThread")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All GUI code checks PASSED!")
        return True
    else:
        print("✗ Some GUI code checks FAILED!")
        return False


if __name__ == "__main__":
    passed = test_gui_code_verification()
    sys.exit(0 if passed else 1)
