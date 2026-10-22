"""Measure semantic-query latency and show example recommendations on the local ChromaDB index.

    python scripts/benchmark_queries.py            # 5 queries x 20 iterations
Run `python ingest_data.py` first. Numbers depend on the machine; paste your own results rather than quoting others.
"""
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import database  # noqa: E402

QUERIES = [
    "a thriller about artificial intelligence",
    "heartwarming animated family adventure",
    "space exploration and survival",
    "gritty crime drama set in a big city",
    "romantic comedy in Paris",
]


def main(iterations: int = 20):
    collection = database.connect_to_collection()
    print(f"collection size: {database.get_collection_count(collection)}")
    collection.query(query_texts=[QUERIES[0]], n_results=6)  # warm-up (model load)
    times = []
    for q in QUERIES:
        for _ in range(iterations):
            t0 = time.perf_counter()
            res = collection.query(query_texts=[q], n_results=6)
            times.append((time.perf_counter() - t0) * 1000)
        titles = [m["title"] for m in res["metadatas"][0]]
        print(f"- {q!r}: {titles}")
    times.sort()
    p95 = times[int(0.95 * (len(times) - 1))]
    print(f"queries: {len(times)}  mean {statistics.mean(times):.1f} ms  median {statistics.median(times):.1f} ms  "
          f"p95 {p95:.1f} ms  max {times[-1]:.1f} ms")


if __name__ == "__main__":
    main()
