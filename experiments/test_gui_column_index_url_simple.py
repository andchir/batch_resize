#!/usr/bin/env python3
"""
Simple test script to verify GUI code has column_index_url support.
This test checks the code structure without requiring GUI initialization.
"""

import sys
import inspect
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_translations():
    """Test that translations for column_index_url exist."""
    from translations import get_translator, set_language

    # Test English translations
    set_language('en')
    translator_en = get_translator()

    # Test Russian translations
    set_language('ru')
    translator_ru = get_translator()

    # Check English translations
    set_language('en')
    translator = get_translator()
    required_keys = ['column_index_url', 'column_index_url_tooltip', 'column_index_url_hint', 'check_all_cells']
    for key in required_keys:
        value = translator.get(key)
        assert value != key, f"English translation missing for '{key}' (returned key itself)"
        print(f"  ✓ EN - {key}: '{value}'")

    # Check Russian translations
    set_language('ru')
    translator = get_translator()
    for key in required_keys:
        value = translator.get(key)
        assert value != key, f"Russian translation missing for '{key}' (returned key itself)"
        print(f"  ✓ RU - {key}: '{value}'")

    print("✓ All required translations exist")

    return True


def test_file_downloader_thread_signature():
    """Test that FileDownloaderThread has column_index_url parameter."""
    from gui import FileDownloaderThread

    # Get __init__ signature
    sig = inspect.signature(FileDownloaderThread.__init__)
    params = list(sig.parameters.keys())

    print(f"FileDownloaderThread.__init__ parameters: {params}")

    # Check that column_index_url is in the parameters
    assert 'column_index_url' in params, \
        "FileDownloaderThread.__init__ should have 'column_index_url' parameter"

    # Check parameter order
    expected_params = ['self', 'file_path', 'output_folder', 'column_index_name', 'column_index_url', 'translator']
    assert params == expected_params, \
        f"Expected parameters: {expected_params}, got: {params}"

    print("✓ FileDownloaderThread has correct signature")
    return True


def test_file_downloader_thread_uses_column_index_url():
    """Test that FileDownloaderThread.run uses column_index_url."""
    from gui import FileDownloaderThread
    import inspect

    # Get source code of run method
    source = inspect.getsource(FileDownloaderThread.run)

    # Check that read_file is called with column_index_url
    assert 'read_file' in source, \
        "FileDownloaderThread.run should call read_file"
    assert 'self.column_index_url' in source, \
        "FileDownloaderThread.run should use self.column_index_url"

    print("✓ FileDownloaderThread.run uses column_index_url parameter")
    return True


def test_gui_code_structure():
    """Test that GUI code has the necessary structure for column_index_url."""
    # Read gui.py source
    gui_path = Path(__file__).parent.parent / "gui.py"
    with open(gui_path, 'r') as f:
        source = f.read()

    # Check that download_column_index_url_spinbox is created
    assert 'download_column_index_url_spinbox' in source, \
        "GUI should create download_column_index_url_spinbox widget"

    # Check that column_index_url label and layout exist
    assert 'download_column_index_url_label' in source, \
        "GUI should have download_column_index_url_label"
    assert 'column_index_url_layout' in source, \
        "GUI should have column_index_url_layout"

    # Check that start_downloading uses column_index_url
    assert 'column_index_url = self.download_column_index_url_spinbox.value()' in source, \
        "start_downloading should get value from download_column_index_url_spinbox"

    # Check that FileDownloaderThread is instantiated with column_index_url
    assert 'FileDownloaderThread(file_path, output_folder, column_index_name, column_index_url, self.translator)' in source, \
        "FileDownloaderThread should be instantiated with column_index_url parameter"

    print("✓ GUI code has all necessary column_index_url components")
    return True


def main():
    """Run all tests."""
    print("Testing GUI column_index_url integration (code structure)...\n")

    tests = [
        ("Translations exist", test_translations),
        ("FileDownloaderThread signature", test_file_downloader_thread_signature),
        ("FileDownloaderThread uses parameter", test_file_downloader_thread_uses_column_index_url),
        ("GUI code structure", test_gui_code_structure),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Test: {test_name}")
        print('='*60)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print('='*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
