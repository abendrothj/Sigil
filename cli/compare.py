#!/usr/bin/env python3
"""
Compare two video hashes

Usage:
    python -m cli.compare VIDEO1 VIDEO2 [OPTIONS]
    python -m cli.compare HASH1 HASH2 --hash-input [OPTIONS]

Example:
    python -m cli.compare video1.mp4 video2.mp4 --frames 60
    python -m cli.compare hash1.txt hash2.txt --hash-input
"""

import argparse
import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.perceptual_hash import (
    load_video_frames,
    extract_perceptual_features,
    compute_perceptual_hash,
    hamming_distance
)


def load_hash_from_file(file_path: str) -> np.ndarray:
    """Load hash from text file"""
    hash_str = Path(file_path).read_text().strip()

    # Convert to binary array
    if len(hash_str) == 256 and all(c in '01' for c in hash_str):
        # Binary format
        return np.array([int(c) for c in hash_str])
    elif len(hash_str) == 64 and all(c in '0123456789abcdefABCDEF' for c in hash_str):
        # Hex format
        hash_int = int(hash_str, 16)
        hash_bin = bin(hash_int)[2:].zfill(256)
        return np.array([int(c) for c in hash_bin])
    else:
        raise ValueError(f"Invalid hash format in {file_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare two video perceptual hashes (Hamming distance)"
    )
    parser.add_argument(
        "input1",
        type=str,
        help="First video file or hash file"
    )
    parser.add_argument(
        "input2",
        type=str,
        help="Second video file or hash file"
    )
    parser.add_argument(
        "--target",
        type=str,
        help="Direct target hash bit string (256 chars of 0s and 1s) to compare against input1"
    )
    parser.add_argument(
        "--hash-input",
        action="store_true",
        help="Inputs are hash files (not videos)"
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=60,
        help="Number of frames to process (default: 60, only for video input)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=30,
        help="Detection threshold in bits (default: 30)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )

    args = parser.parse_args()

    try:
        # Load or extract hashes
        # Load or extract hashes
        if args.target:
            # Hash 2 is direct input
            target_str = args.target.strip()
            if len(target_str) != 256 or not all(c in '01' for c in target_str):
                raise ValueError("Target must be 256-bit binary string")
            hash2 = np.array([int(c) for c in target_str])
            
            # Hash 1 comes from input1 (video or hash file)
            if args.hash_input:
                hash1 = load_hash_from_file(args.input1)
            else:
                 frames1 = load_video_frames(args.input1, max_frames=args.frames)
                 features1 = extract_perceptual_features(frames1)
                 hash1 = compute_perceptual_hash(features1)

        elif args.hash_input:
            # Load from hash files
            if args.verbose:
                print(f"Loading hash from: {args.input1}")
            hash1 = load_hash_from_file(args.input1)

            if args.verbose:
                print(f"Loading hash from: {args.input2}")
            hash2 = load_hash_from_file(args.input2)
        else:
            # Extract from videos
            if args.verbose:
                print(f"Extracting hash from: {args.input1}")
            frames1 = load_video_frames(args.input1, max_frames=args.frames)
            features1 = extract_perceptual_features(frames1)
            hash1 = compute_perceptual_hash(features1)

            if args.verbose:
                print(f"Extracting hash from: {args.input2}")
            frames2 = load_video_frames(args.input2, max_frames=args.frames)
            features2 = extract_perceptual_features(frames2)
            hash2 = compute_perceptual_hash(features2)

        # Calculate Hamming distance
        distance = hamming_distance(hash1, hash2)
        similarity = 100 * (1 - distance / 256)

        # Determine match
        match = distance <= args.threshold

        # Output results
        print(f"\n{'='*60}")
        print(f"Perceptual Hash Comparison")
        print(f"{'='*60}")
        print(f"Hamming Distance: {distance} / 256 bits ({distance/256*100:.1f}%)")
        print(f"Similarity: {similarity:.1f}%")
        print(f"Detection Threshold: {args.threshold} bits ({args.threshold/256*100:.1f}%)")
        print(f"Match: {'✅ YES' if match else '❌ NO'}")
        print(f"{'='*60}")

        if args.verbose:
            print(f"\n📊 Hash Statistics:")
            print(f"   Hash 1 bits set: {np.sum(hash1)} / 256")
            print(f"   Hash 2 bits set: {np.sum(hash2)} / 256")

        # Exit code: 0 if match, 1 if no match
        sys.exit(0 if match else 1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
