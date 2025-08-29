import argparse, pathlib, gzip, shutil, time, json, sys
from typing import List

def list_wal_files(wal_dir: pathlib.Path) -> List[pathlib.Path]:
    return sorted(wal_dir.glob("events-*.ndjson.gz"))

def file_age_days(p: pathlib.Path) -> float:
    return (time.time() - p.stat().st_mtime) / 86400.0

def human(n):
    for unit in ['','K','M','G','T']:
        if abs(n) < 1024.0:
            return f"{n:3.1f}{unit}B"
        n /= 1024.0
    return f"{n:.1f}PB"

def prune(wal_dir: str, keep_days: int, archive_dir: str = None, dry_run: bool = False):
    wd = pathlib.Path(wal_dir)
    files = list_wal_files(wd)
    archived = deleted = 0
    for f in files:
        age = file_age_days(f)
        if age <= keep_days:
            continue
        if dry_run:
            print(f"DRY-RUN would prune {f.name} age={age:.1f}d size={human(f.stat().st_size)}", file=sys.stderr)
            continue
        if archive_dir:
            ad = pathlib.Path(archive_dir); ad.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(ad / f.name))
            archived += 1
        else:
            f.unlink(missing_ok=True)
            deleted += 1
    return archived, deleted

def compact(wal_dir: str, max_compact_size: int, output_name: str = None, dry_run: bool = False, delete_originals: bool = False):
    wd = pathlib.Path(wal_dir)
    files = [f for f in list_wal_files(wd) if f.stat().st_size <= max_compact_size]
    if not files:
        print("Nothing to compact", file=sys.stderr); return 0, 0
    if output_name is None:
        ts = time.strftime("%Y%m%d-%H%M%S")
        output_name = f"events-compact-{ts}.ndjson.gz"
    out_path = wd / output_name
    if dry_run:
        total = sum(f.stat().st_size for f in files)
        print(f"DRY-RUN would compact {len(files)} files into {out_path.name} total={human(total)}", file=sys.stderr)
        return len(files), 0

    with gzip.open(out_path, 'wt', encoding='utf-8') as out:
        for f in files:
            with gzip.open(f, 'rt', encoding='utf-8') as inp:
                shutil.copyfileobj(inp, out)
    removed = 0
    if delete_originals:
        for f in files:
            f.unlink(missing_ok=True)
            removed += 1
    return len(files), removed

def main():
    ap = argparse.ArgumentParser(description="WAL prune/compact utility")    
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_prune = sub.add_parser("prune", help="Delete or archive old WAL files")    
    ap_prune.add_argument("--wal-dir", required=True)
    ap_prune.add_argument("--keep-days", type=int, default=7)
    ap_prune.add_argument("--archive-dir", default=None)
    ap_prune.add_argument("--dry-run", action="store_true")    

    ap_compact = sub.add_parser("compact", help="Compact small WAL files into one")    
    ap_compact.add_argument("--wal-dir", required=True)
    ap_compact.add_argument("--max-compact-size", type=int, default=5_000_000, help="Max size (bytes) to include per file")    
    ap_compact.add_argument("--output-name", default=None)
    ap_compact.add_argument("--dry-run", action="store_true")
    ap_compact.add_argument("--delete-originals", action="store_true")    

    args = ap.parse_args()

    if args.cmd == "prune":
        a, d = prune(args.wal_dir, args.keep_days, args.archive_dir, args.dry_run)
        print(json.dumps({"archived": a, "deleted": d}))
    elif args.cmd == "compact":
        n, r = compact(args.wal_dir, args.max_compact_size, args.output_name, args.dry_run, args.delete_originals)
        print(json.dumps({"compacted_from": n, "removed_originals": r}))

if __name__ == "__main__":
    main()
