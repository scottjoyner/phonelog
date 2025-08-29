import argparse, pathlib
from neo4j import GraphDatabase
import sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uri", required=True)
    ap.add_argument("--user", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--database", default=None)
    ap.add_argument("--cypher-file", default="db/phlog_normalize.cypher")
    args = ap.parse_args()

    cypher_path = pathlib.Path(args.cypher_file)
    if not cypher_path.exists():
        print(f"Missing {cypher_path}", file=sys.stderr)
        sys.exit(1)

    with open(cypher_path, "r", encoding="utf-8") as f:
        cypher = f.read()

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    with driver.session(database=args.database) as s:
        res = s.run(cypher)
        list(res)
    print("Normalization job executed.")

if __name__ == "__main__":
    main()
