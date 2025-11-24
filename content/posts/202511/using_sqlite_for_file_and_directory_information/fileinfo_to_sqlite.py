#!/usr/bin/env python3
"""Build a database with file information"""

import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

# commit to database every COMMIT_LIMIT files
COMMIT_LIMIT = 10_000

# DDL create statements
DDL_STATEMENTS = (
    ("PRAGMA journal_mode=WAL;"),
    (
        "CREATE TABLE IF NOT EXISTS files ("
        "folder TEXT NOT NULL, "
        "name TEXT NOT NULL, "
        "mtime REAL NOT NULL, "
        "size BIGINT NOT NULL, "
        "timestamp REAL NOT NULL);"
    ),
)

# INSERT statement for executemany()
INSERT_SQL = "INSERT INTO files VALUES(:folder, :name, :mtime, :size, :timestamp);"


def commit_to_db(db: sqlite3.Connection, file_info_records: list[dict[str, Any]]) -> int:
    """Commit file information records to the database.

    Args:
        db (sqlite3.Connection): connection to the database.
        file_info_records (list[dict[str, Any]]): list of file info records.

    Returns:
        int: number of records committed.
    """
    result = db.executemany(INSERT_SQL, file_info_records)
    db.commit()
    print(".", end="", flush=True)
    return result.rowcount


def process_folders(
    db: sqlite3.Connection,
    folders: tuple[str, ...],
    commit_limit: int = COMMIT_LIMIT,
) -> int:
    """Read file information and insert into a database.

    Args:
        db (sqlite3.Connection): connection to the database.
        folders (tuple[str, ...]): list of folders to be processed.
        commit_limit (int, optional): commit every n records (default: COMMIT_LIMIT).

    Returns:
        int: total number of files processed
    """
    buffer = []
    counter = 0
    for folder in folders:
        for root, _, files in Path(folder).walk():
            for fname in files:
                try:
                    # lstat() is stat() without following symlinks
                    stats = (root / fname).lstat()
                    buffer.append(
                        {
                            "folder": str(root),
                            "name": fname,
                            "mtime": stats.st_mtime,
                            "size": stats.st_size,
                            "timestamp": time.time(),
                        }
                    )
                except Exception:
                    # (silently) ignore files with issues
                    pass

                if len(buffer) >= commit_limit:
                    counter += commit_to_db(db, buffer)
                    buffer = []
    if buffer:
        counter += commit_to_db(db, buffer)

    if counter > 0:
        print()

    return counter


def main(db_file: str, *folders: str) -> None:
    """Main function.

    Args:
        db_file (str): name of the database file
        folders (tuple[str, ...]): directories to be processed
    """
    with sqlite3.connect(db_file) as db:
        for statement in DDL_STATEMENTS:
            db.execute(statement)
        total_files = process_folders(db, folders)
        print(f"Files processed: {total_files}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {Path(sys.argv[0]).name} database.db folder_1 [.. folder_n]")
        sys.exit(1)
    main(*sys.argv[1:])
