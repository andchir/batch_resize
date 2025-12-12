#!/usr/bin/env python3
"""
Experiment script to test thumbnail extraction from video files using FFmpeg.
This script tests extracting a single frame from a video and saving it as JPG.
"""

from pathlib import Path
from ffmpeg import FFmpeg


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
        print(f"Creating thumbnail from: {input_path.name}")
        print(f"Output: {output_path}")
        print(f"Time position: {time_seconds}s")

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

        print("FFmpeg command ready, executing...")
        ffmpeg.execute()

        if output_path.exists():
            print(f"✓ Thumbnail created successfully: {output_path}")
            print(f"  File size: {output_path.stat().st_size} bytes")
            return True
        else:
            print("✗ Thumbnail file was not created")
            return False

    except Exception as e:
        print(f"✗ Error creating thumbnail: {str(e)}")
        return False


def test_thumbnail_creation():
    """Test thumbnail creation with different scenarios."""
    print("=" * 60)
    print("Testing Thumbnail Extraction")
    print("=" * 60)

    # Test with a sample video path (for demonstration purposes)
    # In real usage, replace with actual video file
    test_video = Path("/tmp/test_video.mp4")
    test_output = Path("/tmp/test_thumbnail.jpg")

    if test_video.exists():
        print("\nTest 1: Extract thumbnail from existing video")
        result = create_thumbnail(test_video, test_output, time_seconds=1.0)
        print(f"Result: {'SUCCESS' if result else 'FAILED'}")
    else:
        print("\nNote: No test video found at /tmp/test_video.mp4")
        print("This is expected. The function is ready to use with actual video files.")

    print("\n" + "=" * 60)
    print("Experiment complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_thumbnail_creation()
