#!/usr/bin/env python3
"""
Batch video resizing script using FFmpeg.
Processes all video files in a folder and saves them to an output folder.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List

from ffmpeg import FFmpeg


# Common video file extensions
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.mpeg', '.mpg'}


def get_video_files(folder_path: Path) -> List[Path]:
    """
    Get all video files from the specified folder.

    Args:
        folder_path: Path to the folder containing video files

    Returns:
        List of Path objects for video files
    """
    video_files = []

    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return video_files

    if not folder_path.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return video_files

    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
            video_files.append(file_path)

    return sorted(video_files)


def create_thumbnail(input_path: Path, output_path: Path, time_seconds: float = 1.0) -> bool:
    """
    Extract a single frame from a video and save it as a JPG thumbnail.

    Args:
        input_path: Path to input video file
        output_path: Path to output JPG file
        time_seconds: Time position in seconds to extract the frame from (default: 1.0)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create FFmpeg instance
        # Use -ss before input for faster seeking (keyframe-based)
        ffmpeg = (
            FFmpeg()
            .option("y")  # Overwrite output file if exists
            .option("ss", time_seconds)  # Seek to specific time
            .input(str(input_path))
            .output(
                str(output_path),
                {"vframes": 1},  # Extract 1 frame
                vf="thumbnail"  # Use thumbnail filter to select best frame
            )
        )

        ffmpeg.execute()
        return True

    except Exception as e:
        print(f"Error creating thumbnail for {input_path.name}: {str(e)}")
        return False


def resize_video(input_path: Path, output_path: Path, height: int, remove_audio: bool = False) -> bool:
    """
    Resize a video file to the specified height while maintaining aspect ratio.

    Args:
        input_path: Path to input video file
        output_path: Path to output video file
        height: Target height in pixels (width will be calculated automatically)
        remove_audio: Whether to remove audio track

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create FFmpeg instance
        ffmpeg = FFmpeg().option("y").input(str(input_path))

        # Build output options
        output_options = {
            "codec:v": "libx264",
            "preset": "medium",
            "crf": 23
        }

        # Set video filter for scaling (maintain aspect ratio)
        vf = f"scale=-2:{height}"

        # Configure audio
        if remove_audio:
            output_options["an"] = None  # Remove audio
        else:
            output_options["codec:a"] = "aac"  # Use AAC codec for audio
            output_options["b:a"] = "128k"  # Audio bitrate

        # Add output with options
        ffmpeg = ffmpeg.output(
            str(output_path),
            output_options,
            vf=vf
        )

        print(f"Processing: {input_path.name}")
        ffmpeg.execute()
        print(f"Completed: {output_path.name}")

        return True

    except Exception as e:
        print(f"Error processing {input_path.name}: {str(e)}")
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Batch resize videos in a folder using FFmpeg.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py /path/to/videos 720
  python main.py /path/to/videos 1080 --remove_audio
  python main.py /path/to/videos 720 --create_thumbs
        """
    )

    parser.add_argument(
        "folder",
        type=str,
        help="Path to folder containing video files"
    )

    parser.add_argument(
        "height",
        type=int,
        help="Target height in pixels (width will be calculated automatically)"
    )

    parser.add_argument(
        "--remove_audio",
        action="store_true",
        help="Remove audio track from output videos"
    )

    parser.add_argument(
        "--create_thumbs",
        action="store_true",
        help="Create JPG thumbnails in 'thumbs' folder (one frame from each video)"
    )

    args = parser.parse_args()

    # Convert folder path to Path object
    folder_path = Path(args.folder).resolve()

    # Get all video files
    video_files = get_video_files(folder_path)

    if not video_files:
        print(f"No video files found in '{folder_path}'")
        sys.exit(1)

    print(f"Found {len(video_files)} video file(s) in '{folder_path}'")

    # Create output directory
    output_dir = folder_path / "output"
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Create thumbs directory if needed
    thumbs_dir = None
    if args.create_thumbs:
        thumbs_dir = folder_path / "thumbs"
        thumbs_dir.mkdir(exist_ok=True)
        print(f"Thumbnails directory: {thumbs_dir}")

    # Process each video file
    successful = 0
    failed = 0
    thumbs_created = 0
    thumbs_failed = 0

    for video_file in video_files:
        output_path = output_dir / video_file.name

        if resize_video(video_file, output_path, args.height, args.remove_audio):
            successful += 1
        else:
            failed += 1

        # Create thumbnail if requested
        if args.create_thumbs:
            thumb_path = thumbs_dir / f"{video_file.stem}.jpg"
            print(f"Creating thumbnail: {thumb_path.name}")
            if create_thumbnail(video_file, thumb_path):
                thumbs_created += 1
                print(f"Thumbnail created: {thumb_path.name}")
            else:
                thumbs_failed += 1

    # Print summary
    print("\n" + "=" * 50)
    print(f"Processing complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(video_files)}")
    if args.create_thumbs:
        print(f"Thumbnails created: {thumbs_created}")
        print(f"Thumbnails failed: {thumbs_failed}")
    print("=" * 50)


if __name__ == "__main__":
    main()
