+++
date = "2025-11-22T16:23:09+01:00"
draft = false
title = "Using SQLite for file and directory information"
tags = ["python", "sqlite3", "sysadmin"]
+++
Did you ever have a directory tree with thousands of directories and wondered which folder is the largest? Ever tried the _Windows Explorer_ on a folder with millions of files and see it chug along without really showing anything? This article describes a simple Python script which enables you to throw the file information in a [SQLite][sqlite] database and query using the power of SQL.

<!--more-->
## Table of Contents <!-- omit in toc -->

- [Script `fileinfo_to_sqlite.py`](#script-fileinfo_to_sqlitepy)
- [Querying the database](#querying-the-database)
- [Additional notes](#additional-notes)

## Script `fileinfo_to_sqlite.py`

The script shown below ([`fileinfo_to_sqlite.py`][fileinfo_to_sqlite.py]) starts at a root folder and then walks down the underlying tree. For each encountered file an entry is created in a `files` table in a [SQLite][sqlite] database. Table columns are (one row per file):

- `folder`: parent folder, the file with `name` was found in this folder
- `name`: name of the file
- `mtime`: file modification time as [Unix time][unix_time] (seconds since January 1, 1970)
- `size` file size in bytes
- `timestamp`: row creation time as [Unix time][unix_time]

Timestamps are in [Unix time][unix_time] which is fine for sorting but not really readable. Use the SQLite [Date And Time Functions][datetime_functions] to convert from and to your local timezone:

```sql
SELECT DATETIME(mtime, 'unixepoch', 'localtime') FROM files;
```

Use `strftime` to go from local time to Unix:

```sql
SELECT strftime('%s', '2025-11-22 15:45:12');
```

Or, a bit more advanced, get a Unix timestamp 12 hours in the past:

```sql
SELECT strftime('%s', 'now', '-12 hours');
```

The script ([`fileinfo_to_sqlite.py`][fileinfo_to_sqlite.py]):
{{< code file="/posts/202511/using_sqlite_for_file_and_directory_information/fileinfo_to_sqlite.py" language="python" >}}

It uses only basic functionality from the standard library; you do not need additional libraries or a virtual environment. If you have [Python installed][installing_python] you can run it like this:

```bash
python3 fileinfo_to_sqlite.py database.db folder_to_index
```

It contains a [shebang][shebang], on Linux you can make it executable and run it directly:

```bash
chmod +x fileinfo_to_sqlite.py
./fileinfo_to_sqlite.py database.db folder_to_index
```

During execution, a dot (`.`) is printed for each commit (default is every 10.000 files). After processing it will print the number of files found. For example:

```text
user@hostname:~/blog$ ./fileinfo_to_sqlite.py database.db ..
...................
Files processed: 183020
```

## Querying the database

And there you have it: you can now query a directory tree. Fire up your favorite database tool (I like [DBeaver][dbeaver]) and query away. Some examples...

Get the 10 largest files:

```sql
SELECT folder, name, size
FROM files
ORDER BY size DESC
LIMIT 10;
```

Get the 10 largest folders:

```sql
SELECT folder, sum(size) FROM files
GROUP BY folder
ORDER BY 2 DESC
LIMIT 10;
```

Get all files with a `.py` extension:

```sql
SELECT folder, name, size FROM files
WHERE name LIKE '%.py'
ORDER BY folder, name;
```

Show 10 oldest files (and convert `mtime` to a normal human readable format in your local timezone):

```sql
SELECT folder, name, size, DATETIME(mtime, 'unixepoch', 'localtime') FROM files
ORDER BY mtime ASC
LIMIT 10;
```

Create a script to delete all files modified in the last 12 hours:

```sql
SELECT 'rm ' || folder || '/' || name FROM files
WHERE mtime >= strftime('%s', 'now', '-12 hours');
```

## Additional notes

This script is definitely not the fastest way of getting file information. If you want speed you might need a dedicated tool. This is meant as an option when you cannot really install software but have a somewhat recent Python interpreter installed. Copy paste this script, run it (drink coffee) and when you come back you have a database with file information.

Did you know you can use the Python [sqlite3][sqlite3] module to query SQLite databases as well? Just call it as a module:

```bash
python -m sqlite3 database.db
```

Although not always required... If you have a very large set of files and / or have complicated queries you can create additional indices on the `files` table. For example:

```sql
CREATE INDEX IF NOT EXISTS ix_files_folder ON files (folder);
CREATE INDEX IF NOT EXISTS ix_files_name ON files (name);
CREATE INDEX IF NOT EXISTS ix_files_folder_name ON files (folder, name);
CREATE INDEX IF NOT EXISTS ix_files_mtime ON files (mtime);
CREATE INDEX IF NOT EXISTS ix_files_size ON files (size);
```

[datetime_functions]: https://sqlite.org/lang_datefunc.html
[dbeaver]: https://dbeaver.io/
[fileinfo_to_sqlite.py]: /posts/202511/using_sqlite_for_file_and_directory_information/fileinfo_to_sqlite.py
[installing_python]: https://realpython.com/installing-python/
[shebang]: https://en.wikipedia.org/wiki/Shebang_(Unix)
[sqlite]: https://www.sqlite.org/
[sqlite3]: https://docs.python.org/3/library/sqlite3.html
[unix_time]: https://en.wikipedia.org/wiki/Unix_time
