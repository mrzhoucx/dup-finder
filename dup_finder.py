#!/usr/bin/env python3
"""Find duplicate files by content hash.

Usage:
    python3 dup_finder.py [PATH ...] [--min-size BYTES] [--delete --yes]

By default it only reports duplicates: files with identical size and
SHA-256 hash are grouped together, with the wasted bytes per group.
With --delete --yes it deletes every duplicate except the first file
in each group (sorted order). Without --yes it prints what it would
delete and deletes nothing.
"""
import argparse
import hashlib
import os
import sys
from collections import defaultdict


def hash_file(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def collect_files(paths, min_size):
    found = []
    for base in paths:
        if os.path.isfile(base):
            found.append(base)
        elif os.path.isdir(base):
            for root, dirs, files in os.walk(base):
                dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
                for name in files:
                    full = os.path.join(root, name)
                    if os.path.islink(full):
                        continue
                    found.append(full)
        else:
            print(f"skip: not a file or directory: {base}", file=sys.stderr)
    out = []
    for path in found:
        try:
            size = os.path.getsize(path)
        except OSError as exc:
            print(f"skip: {path}: {exc}", file=sys.stderr)
            continue
        if size >= min_size:
            out.append((path, size))
    return out


def find_duplicates(paths, min_size):
    by_size = defaultdict(list)
    for path, size in collect_files(paths, min_size):
        by_size[size].append(path)
    groups = []
    for size, candidates in by_size.items():
        if len(candidates) < 2:
            continue
        by_hash = defaultdict(list)
        for path in sorted(candidates):
            try:
                by_hash[hash_file(path)].append(path)
            except OSError as exc:
                print(f"skip: {path}: {exc}", file=sys.stderr)
        for paths_in_group in by_hash.values():
            if len(paths_in_group) > 1:
                groups.append((size, sorted(paths_in_group)))
    return sorted(groups, key=lambda g: -g[0] * (len(g[1]) - 1))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Find duplicate files by content hash.")
    parser.add_argument("paths", nargs="*", default=["."],
                        help="files or directories to scan (default: current directory)")
    parser.add_argument("--min-size", type=int, default=1,
                        help="ignore files smaller than this many bytes (default: 1)")
    parser.add_argument("--delete", action="store_true",
                        help="delete duplicates, keeping the first file in each group")
    parser.add_argument("--yes", action="store_true",
                        help="required together with --delete to actually delete")
    args = parser.parse_args(argv)

    groups = find_duplicates(args.paths, args.min_size)
    if not groups:
        print("No duplicates found.")
        return 0

    total_wasted = 0
    for i, (size, files) in enumerate(groups, 1):
        wasted = size * (len(files) - 1)
        total_wasted += wasted
        print(f"\nGroup {i}: {len(files)} copies x {size} bytes (wasted: {wasted} bytes)")
        for path in files:
            print(f"  {path}")

    print(f"\n{len(groups)} duplicate group(s), {total_wasted} bytes wasted in total.")

    if args.delete:
        if not args.yes:
            print("\nDry run only: re-run with --delete --yes to actually delete "
                  "all but the first file in each group.")
            return 0
        deleted = 0
        for _size, files in groups:
            for path in files[1:]:
                try:
                    os.remove(path)
                    print(f"deleted: {path}")
                    deleted += 1
                except OSError as exc:
                    print(f"failed to delete {path}: {exc}", file=sys.stderr)
        print(f"Deleted {deleted} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
