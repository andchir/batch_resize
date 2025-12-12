#!/usr/bin/env python3
"""
Test script to verify that numbers_only_at_end option is available in the GUI.
This test checks that the combobox has the correct number of items and the new option is present.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from gui import MainWindow


def test_numbers_only_at_end_option():
    """Test that numbers_only_at_end option is available in GUI."""
    app = QApplication(sys.argv)
    window = MainWindow()

    # Get the rename type combobox
    combo = window.rename_type_combo

    # Check that we have 4 options now (sequential, numbers_only, text_only, numbers_only_at_end)
    assert combo.count() == 4, f"Expected 4 options, got {combo.count()}"

    # Check that numbers_only_at_end option exists
    options = [combo.itemData(i) for i in range(combo.count())]
    assert "numbers_only_at_end" in options, f"numbers_only_at_end not found in options: {options}"

    # Check the display text for the new option
    for i in range(combo.count()):
        if combo.itemData(i) == "numbers_only_at_end":
            text = combo.itemText(i)
            assert "число в конце" in text.lower(), f"Display text incorrect: {text}"
            print(f"✓ Found numbers_only_at_end option with text: '{text}'")
            break

    # Print all options for verification
    print("\nAll available rename options:")
    for i in range(combo.count()):
        data = combo.itemData(i)
        text = combo.itemText(i)
        print(f"  {i+1}. {text} (value: {data})")

    print("\n✓ All tests passed! The numbers_only_at_end option is correctly added to the GUI.")

    # Don't show the window, just test
    app.quit()


if __name__ == "__main__":
    test_numbers_only_at_end_option()
