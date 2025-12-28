"""
Hash Database - SQLite-based storage for perceptual hashes

Provides functionality for storing, querying, and managing perceptual hashes
with associated metadata (platform, video_id, timestamp, etc.)
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np


class HashDatabase:
    """SQLite database for storing and querying perceptual hashes"""

    def __init__(self, db_path: str = "hashes.db"):
        """
        Initialize hash database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._init_database()

    def _init_database(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        cursor = self.conn.cursor()

        # Create hashes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT NOT NULL,
                hash_hex TEXT NOT NULL,
                video_id TEXT,
                platform TEXT,
                upload_date TEXT,
                file_path TEXT,
                frame_count INTEGER,
                metadata TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(hash)
            )
        ''')

        # Create index on hash for fast lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_hash ON hashes(hash)
        ''')

        # Create index on platform for filtering
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_platform ON hashes(platform)
        ''')

        self.conn.commit()

    def store_hash(
        self,
        hash_binary: np.ndarray,
        video_id: Optional[str] = None,
        platform: Optional[str] = None,
        upload_date: Optional[str] = None,
        file_path: Optional[str] = None,
        frame_count: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Store perceptual hash in database

        Args:
            hash_binary: 256-bit numpy array (0s and 1s)
            video_id: Optional video identifier (e.g., YouTube video ID)
            platform: Optional platform name (youtube, tiktok, facebook, etc.)
            upload_date: Optional upload date (ISO8601 format)
            file_path: Optional local file path
            frame_count: Optional number of frames processed
            metadata: Optional additional metadata dictionary

        Returns:
            Database row ID
        """
        cursor = self.conn.cursor()

        # Convert hash to string and hex
        hash_str = ''.join(map(str, hash_binary.astype(int)))
        hash_hex = hex(int(hash_str, 2))[2:].zfill(64)

        # Serialize metadata
        metadata_json = json.dumps(metadata) if metadata else None

        # Insert or update
        try:
            cursor.execute('''
                INSERT INTO hashes (
                    hash, hash_hex, video_id, platform, upload_date,
                    file_path, frame_count, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                hash_str,
                hash_hex,
                video_id,
                platform,
                upload_date,
                file_path,
                frame_count,
                metadata_json,
                datetime.utcnow().isoformat()
            ))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Hash already exists - update metadata
            cursor.execute('''
                UPDATE hashes SET
                    video_id = COALESCE(?, video_id),
                    platform = COALESCE(?, platform),
                    upload_date = COALESCE(?, upload_date),
                    file_path = COALESCE(?, file_path),
                    frame_count = COALESCE(?, frame_count),
                    metadata = COALESCE(?, metadata)
                WHERE hash = ?
            ''', (
                video_id,
                platform,
                upload_date,
                file_path,
                frame_count,
                metadata_json,
                hash_str
            ))
            self.conn.commit()

            # Return existing row ID
            cursor.execute('SELECT id FROM hashes WHERE hash = ?', (hash_str,))
            return cursor.fetchone()[0]

    def query_similar(
        self,
        hash_binary: np.ndarray,
        threshold: int = 30,
        platform: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query database for similar hashes

        Args:
            hash_binary: 256-bit numpy array to query
            threshold: Maximum Hamming distance for match (default: 30 bits)
            platform: Optional platform filter
            limit: Maximum number of results

        Returns:
            List of matching hash records with Hamming distances
        """
        cursor = self.conn.cursor()

        # Query all hashes (with platform filter if specified)
        if platform:
            cursor.execute(
                'SELECT id, hash, hash_hex, video_id, platform, upload_date, file_path, frame_count, metadata, created_at FROM hashes WHERE platform = ?',
                (platform,)
            )
        else:
            cursor.execute(
                'SELECT id, hash, hash_hex, video_id, platform, upload_date, file_path, frame_count, metadata, created_at FROM hashes'
            )

        results = []
        query_hash_str = ''.join(map(str, hash_binary.astype(int)))

        for row in cursor.fetchall():
            stored_hash_str = row[1]

            # Calculate Hamming distance
            distance = sum(c1 != c2 for c1, c2 in zip(query_hash_str, stored_hash_str))

            if distance <= threshold:
                results.append({
                    'id': row[0],
                    'hash': row[1],
                    'hash_hex': row[2],
                    'video_id': row[3],
                    'platform': row[4],
                    'upload_date': row[5],
                    'file_path': row[6],
                    'frame_count': row[7],
                    'metadata': json.loads(row[8]) if row[8] else None,
                    'created_at': row[9],
                    'hamming_distance': distance,
                    'similarity': 100 * (1 - distance / 256)
                })

        # Sort by Hamming distance
        results.sort(key=lambda x: x['hamming_distance'])

        return results[:limit]

    def get_stats(self) -> Dict:
        """
        Get database statistics

        Returns:
            Dictionary with statistics
        """
        cursor = self.conn.cursor()

        # Total hashes
        cursor.execute('SELECT COUNT(*) FROM hashes')
        total_hashes = cursor.fetchone()[0]

        # Hashes by platform
        cursor.execute('SELECT platform, COUNT(*) FROM hashes GROUP BY platform')
        by_platform = {row[0] or 'unknown': row[1] for row in cursor.fetchall()}

        # Date range
        cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM hashes')
        date_range = cursor.fetchone()

        return {
            'total_hashes': total_hashes,
            'by_platform': by_platform,
            'oldest_entry': date_range[0],
            'newest_entry': date_range[1]
        }

    def delete_hash(self, hash_id: int) -> bool:
        """
        Delete hash by ID

        Args:
            hash_id: Database row ID

        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM hashes WHERE id = ?', (hash_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Example usage
    import numpy as np

    # Create database
    db = HashDatabase("test_hashes.db")

    # Store a hash
    test_hash = np.random.randint(0, 2, 256)
    hash_id = db.store_hash(
        test_hash,
        video_id="test_video_123",
        platform="youtube",
        upload_date="2025-12-28",
        metadata={"resolution": "1080p", "duration": 120}
    )
    print(f"Stored hash with ID: {hash_id}")

    # Query similar hashes
    query_hash = test_hash.copy()
    query_hash[:10] = 1 - query_hash[:10]  # Flip 10 bits

    matches = db.query_similar(query_hash, threshold=30)
    print(f"Found {len(matches)} matches:")
    for match in matches:
        print(f"  - {match['platform']}: {match['video_id']} (distance: {match['hamming_distance']} bits)")

    # Get stats
    stats = db.get_stats()
    print(f"\nDatabase stats: {stats}")

    db.close()
