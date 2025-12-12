#!/usr/bin/env python3
"""
File renaming script for batch renaming files in a folder.
Supports various sorting and renaming strategies with optional prefix/suffix.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


def extract_number_from_filename(filename: str) -> Tuple[int, str]:
    """
    Extract the first number found in filename.

    Args:
        filename: The filename to extract number from

    Returns:
        Tuple of (number, remaining_text). If no number found, returns (0, filename)
    """
    # Search for first sequence of digits
    match = re.search(r'\d+', filename)
    if match:
        number = int(match.group())
        # Remove the number from text
        remaining = filename[:match.start()] + filename[match.end():]
        return (number, remaining)
    return (0, filename)


def natural_sort_key(filename: str) -> List:
    """
    Generate a sort key for natural sorting (comparing numbers as integers).

    Args:
        filename: The filename to generate key from

    Returns:
        List of mixed strings and integers for natural comparison

    Example:
        "file10.txt" -> ["file", 10, ".txt"]
        "file2.txt" -> ["file", 2, ".txt"]
        This way file2.txt comes before file10.txt
    """
    parts = []
    for part in re.split(r'(\d+)', filename):
        if part.isdigit():
            parts.append(int(part))
        else:
            parts.append(part.lower())
    return parts


def extract_number_at_end(filename: str) -> int:
    """
    Extract the last number in the filename (before extension) if it's preceded by a non-digit.

    Args:
        filename: The filename (stem, without extension) to extract number from

    Returns:
        The number at the end, or 0 if no valid number found

    Example:
        "PreviewFemale3D_9" -> 9
        "PreviewFemale3D_10" -> 10
        "file123" -> 0 (no non-digit before the number)
        "abc" -> 0 (no number)
    """
    # Match a non-digit followed by one or more digits at the end
    match = re.search(r'\D(\d+)$', filename)
    if match:
        return int(match.group(1))
    return 0


def extract_text_only(filename: str) -> str:
    """
    Remove all digits from filename, keeping only text and other characters.

    Args:
        filename: The filename to process

    Returns:
        Filename with digits removed
    """
    return re.sub(r'\d+', '', filename)


def extract_numbers_only(filename: str) -> str:
    """
    Extract only digits from filename.

    Args:
        filename: The filename to process

    Returns:
        String containing only the digits found, or empty string if none
    """
    numbers = re.findall(r'\d+', filename)
    return ''.join(numbers)


def get_files_in_folder(folder_path: Path) -> List[Path]:
    """
    Get all files (not directories) from the specified folder.

    Args:
        folder_path: Path to the folder

    Returns:
        List of Path objects for files
    """
    files = []

    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return files

    if not folder_path.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return files

    for item in folder_path.iterdir():
        if item.is_file():
            files.append(item)

    return files


def sort_files(files: List[Path], sort_type: str) -> List[Path]:
    """
    Sort files according to the specified sorting strategy.

    Args:
        files: List of file Path objects
        sort_type: Sorting strategy - 'name' or 'number'

    Returns:
        Sorted list of Path objects
    """
    if sort_type == 'name':
        # Sort by full filename alphabetically (case-insensitive)
        return sorted(files, key=lambda f: f.name.lower())
    elif sort_type == 'number':
        # Sort using natural sorting (numbers compared as integers)
        return sorted(files, key=lambda f: natural_sort_key(f.name))
    else:
        print(f"Warning: Unknown sort type '{sort_type}', using 'name'")
        return sorted(files, key=lambda f: f.name.lower())


def generate_new_filename(
    file_path: Path,
    index: int,
    rename_type: str,
    prefix: str = "",
    suffix: str = "",
    zero_num: int = 0
) -> str:
    """
    Generate new filename based on renaming strategy.

    Args:
        file_path: Original file Path object
        index: Sequential index (1-based) for this file
        rename_type: Renaming strategy - 'sequential', 'numbers_only', 'text_only', or 'numbers_only_at_end'
        prefix: Optional prefix to add
        suffix: Optional suffix to add
        zero_num: Number of zeros for padding (default 0 - no padding)

    Returns:
        New filename string (with extension)
    """
    stem = file_path.stem  # filename without extension
    extension = file_path.suffix  # .ext

    if rename_type == 'sequential':
        # Use sequential number as name
        new_name = str(index)
    elif rename_type == 'numbers_only':
        # Extract only numbers from original filename
        numbers = extract_numbers_only(stem)
        new_name = numbers if numbers else str(index)
    elif rename_type == 'text_only':
        # Extract only text (remove numbers) from original filename
        text = extract_text_only(stem)
        # Clean up multiple spaces and trim
        text = re.sub(r'\s+', ' ', text).strip()
        new_name = text if text else f"file_{index}"
    elif rename_type == 'numbers_only_at_end':
        # Extract the number at the end of filename (if preceded by non-digit)
        # If no such number exists, use sequential index
        number = extract_number_at_end(stem)
        new_name = str(number) if number > 0 else str(index)
    else:
        print(f"Warning: Unknown rename type '{rename_type}', using 'sequential'")
        new_name = str(index)

    # Apply zero padding if zero_num is specified and new_name is numeric
    if zero_num > 0 and new_name.isdigit():
        new_name = new_name.zfill(zero_num + 1)

    # Add prefix and suffix
    final_name = f"{prefix}{new_name}{suffix}{extension}"

    return final_name


def rename_files(
    folder_path: Path,
    sort_type: str,
    rename_type: str,
    prefix: str = "",
    suffix: str = "",
    dry_run: bool = False,
    zero_num: int = 0
) -> Tuple[int, int]:
    """
    Rename all files in folder according to specified strategy.

    Args:
        folder_path: Path to folder containing files
        sort_type: Sorting strategy - 'name' or 'number'
        rename_type: Renaming strategy - 'sequential', 'numbers_only', 'text_only', or 'numbers_only_at_end'
        prefix: Optional prefix to add to filenames
        suffix: Optional suffix to add to filenames
        dry_run: If True, only show what would be done without actually renaming
        zero_num: Number of zeros for padding (default 0 - no padding)

    Returns:
        Tuple of (successful_count, failed_count)
    """
    # Get all files
    files = get_files_in_folder(folder_path)

    if not files:
        print(f"No files found in '{folder_path}'")
        return (0, 0)

    print(f"Found {len(files)} file(s) in '{folder_path}'")

    # Sort files
    sorted_files = sort_files(files, sort_type)

    if dry_run:
        print("\nDry run mode - showing what would be renamed:")
        print("=" * 60)

    successful = 0
    failed = 0

    # Keep track of new names to avoid duplicates
    used_names = set()

    for index, file_path in enumerate(sorted_files, start=1):
        try:
            # Generate new filename
            new_filename = generate_new_filename(
                file_path, index, rename_type, prefix, suffix, zero_num
            )

            # Handle duplicate names by adding a counter
            original_new_filename = new_filename
            counter = 1
            while new_filename in used_names:
                # Insert counter before extension
                stem = Path(original_new_filename).stem
                ext = Path(original_new_filename).suffix
                new_filename = f"{stem}_{counter}{ext}"
                counter += 1

            used_names.add(new_filename)
            new_path = file_path.parent / new_filename

            # Check if target file already exists (and it's not the same file)
            if new_path.exists() and new_path.resolve() != file_path.resolve():
                print(f"Error: Target file already exists: {new_filename}")
                failed += 1
                continue

            if dry_run:
                print(f"[{index}] {file_path.name} -> {new_filename}")
            else:
                # Perform the rename
                file_path.rename(new_path)
                print(f"[{index}] Renamed: {file_path.name} -> {new_filename}")

            successful += 1

        except Exception as e:
            print(f"Error renaming {file_path.name}: {str(e)}")
            failed += 1

    return (successful, failed)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Batch rename files in a folder with various sorting and renaming strategies.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Sort types:
  name      Sort files alphabetically by name
  number    Sort files using natural/numeric sorting (e.g., file2 before file10)

Rename types:
  sequential           Rename files with sequential numbers (1, 2, 3, ...)
  numbers_only         Keep only numbers from original filename (remove text)
  text_only            Keep only text from original filename (remove numbers)
  numbers_only_at_end  Keep only the number at the end of filename (if preceded by non-digit)
                       If no such number exists, use sequential index instead

Examples:
  # Rename files sequentially with prefix
  python rename.py /path/to/folder name sequential --prefix "photo_"

  # Sort by number, keep only text, add suffix
  python rename.py /path/to/folder number text_only --suffix "_edited"

  # Preview changes without renaming (dry run)
  python rename.py /path/to/folder name sequential --dry-run

  # Combine prefix and suffix
  python rename.py /path/to/folder number numbers_only --prefix "img_" --suffix "_final"

  # Extract trailing numbers: file_9.mp4 -> 9.mp4, file_10.mp4 -> 10.mp4
  python rename.py /path/to/folder number numbers_only_at_end
        """
    )

    parser.add_argument(
        "folder",
        type=str,
        help="Path to folder containing files to rename"
    )

    parser.add_argument(
        "sort_type",
        type=str,
        choices=['name', 'number'],
        help="How to sort files before renaming"
    )

    parser.add_argument(
        "rename_type",
        type=str,
        choices=['sequential', 'numbers_only', 'text_only', 'numbers_only_at_end'],
        help="How to generate new filenames"
    )

    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="Optional prefix to add to each filename"
    )

    parser.add_argument(
        "--suffix",
        type=str,
        default="",
        help="Optional suffix to add to each filename (before extension)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be renamed without actually renaming files"
    )

    parser.add_argument(
        "--zero_num",
        type=int,
        default=0,
        help="Number of zeros for padding numbers in filenames (default: 0 - no padding). Example: --zero_num=1 gives 09.mp4, --zero_num=2 gives 009.mp4"
    )

    args = parser.parse_args()

    # Convert folder path to Path object
    folder_path = Path(args.folder).resolve()

    # Validate folder exists
    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        sys.exit(1)

    if not folder_path.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        sys.exit(1)

    # Display configuration
    print(f"Configuration:")
    print(f"  Folder: {folder_path}")
    print(f"  Sort by: {args.sort_type}")
    print(f"  Rename as: {args.rename_type}")
    if args.prefix:
        print(f"  Prefix: '{args.prefix}'")
    if args.suffix:
        print(f"  Suffix: '{args.suffix}'")
    if args.zero_num > 0:
        print(f"  Zero padding: {args.zero_num}")
    if args.dry_run:
        print(f"  Mode: DRY RUN (no actual changes)")
    print()

    # Perform renaming
    successful, failed = rename_files(
        folder_path,
        args.sort_type,
        args.rename_type,
        args.prefix,
        args.suffix,
        args.dry_run,
        args.zero_num
    )

    # Print summary
    print("\n" + "=" * 60)
    if args.dry_run:
        print("Dry run complete! No files were actually renamed.")
    else:
        print("Renaming complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {successful + failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
