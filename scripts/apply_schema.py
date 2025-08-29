import argparse, pathlib, sys
from neo4j import GraphDatabase

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uri", required=True)
    ap.add_argument("--user", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--database", default=None)
    ap.add_argument("--file", default="db/schema.cypher")
    args = ap.parse_args()

    path = pathlib.Path(args.file)
    if not path.exists():
        print(f"Missing {path}", file=sys.stderr)
        sys.exit(1)

    cypher = path.read_text(encoding="utf-8")
    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    with driver.session(database=args.database) as s:
        for stmt in cypher.split(";"):
            st = stmt.strip()
            if not st:
                continue
            s.run(st)
    print("Schema applied.")

if __name__ == "__main__":
    main()
