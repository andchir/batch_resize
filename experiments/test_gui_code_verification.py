#!/usr/bin/env python3
"""
Test script to verify that the gui.py file contains the numbers_only_at_end option.
This test reads the source code directly to verify the changes.
"""

import sys
from pathlib import Path


def test_gui_source_contains_numbers_only_at_end():
    """Test that the gui.py source contains the numbers_only_at_end option."""
    gui_file = Path(__file__).parent.parent / "gui.py"

    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check that numbers_only_at_end is present
    assert 'numbers_only_at_end' in content, "numbers_only_at_end not found in gui.py"
    print("✓ Found 'numbers_only_at_end' in gui.py")

    # Check that the Russian text is present (the display text for the option)
    assert 'Только число в конце имени' in content, "Display text not found in gui.py"
    print("✓ Found display text 'Только число в конце имени' in gui.py")

    # Count how many times addItem appears for rename_type_combo
    # Should be 4 (sequential, numbers_only, text_only, numbers_only_at_end)
    lines = content.split('\n')
    add_item_count = 0
    in_rename_section = False

    for line in lines:
        if 'self.rename_type_combo = QComboBox()' in line:
            in_rename_section = True
        elif in_rename_section:
            if 'self.rename_type_combo.addItem' in line:
                add_item_count += 1
            elif 'rename_type_layout.addWidget(self.rename_type_combo)' in line:
                break

    assert add_item_count == 4, f"Expected 4 addItem calls, got {add_item_count}"
    print(f"✓ Found {add_item_count} rename type options in gui.py")

    # Extract and display all rename options
    print("\nRename type options found in gui.py:")
    for i, line in enumerate(lines):
        if 'self.rename_type_combo.addItem' in line:
            print(f"  {line.strip()}")

    print("\n✓ All tests passed! The GUI code correctly includes the numbers_only_at_end option.")


if __name__ == "__main__":
    test_gui_source_contains_numbers_only_at_end()
