# Movie Recommendation System

[![tests](https://github.com/likhith1253/Movie_Recommendation_System/actions/workflows/ci.yml/badge.svg)](https://github.com/likhith1253/Movie_Recommendation_System/actions/workflows/ci.yml)

A terminal-based, content-based movie recommender. Every movie is turned into a text document (title, overview, genres, top cast, director), embedded, and stored in a ChromaDB vector index; recommendations are the nearest neighbours of a movie or a free-text query, optionally combined with metadata filters. Built as a vector-database course project.

## Problem

Collaborative filtering needs user histories that a small project does not have. Content-based search over text embeddings works from the movie metadata alone and can answer queries such as "a thriller about artificial intelligence" that keyword matching cannot.

## What is implemented

* **Ingestion** (`ingest_data.py`): merges the TMDb 5000 movies and credits CSVs, parses the JSON-style columns, extracts the director from the crew list, builds one document per movie and writes them to a persistent ChromaDB collection (cosine space, batches of 500). 4,803 TMDb rows become 4,800 indexed movies after dropping rows with missing overview, genres, cast or crew.
* **Embeddings**: ChromaDB's default embedding function (`all-MiniLM-L6-v2`, run through ONNX, 384 dimensions). No model is trained or fine-tuned here.
* **User features** (`operations.py`, `main.py`): recommendations for a movie title with a similarity score, semantic search with filters on year, rating and runtime, genre browsing, and "more by this director".
* **Admin panel** (`admin.py`): create/read/update/delete movies, database statistics, query benchmarking and an interactive indexing benchmark (cosine vs L2 vs inner product). The admin password defaults to a demo value; set the `MOVIE_ADMIN_PASSWORD` environment variable to change it.
* **Interface**: Rich tables and Questionary prompts in the terminal.

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate            # source .venv/bin/activate on Linux/macOS
pip install -r requirements.txt   # chromadb 0.5.0 needs numpy < 2, which is pinned
python ingest_data.py             # builds ./movie_db (first run downloads the ~80 MB ONNX model; about 7 minutes on a laptop CPU)
python main.py                    # interactive menu
```

Tests (no database or model needed): `pip install -r requirements-dev.txt && python -m pytest`.
Latency benchmark and example queries after ingestion: `python scripts/benchmark_queries.py`.

## Results

There are no relevance labels, so recommendation quality is not scored (no precision, recall or NDCG). What was measured on a Windows laptop CPU, 4,800 movies, top-6 queries, including query embedding time:

| Measure | Value |
|---|---|
| Indexed movies | 4,800 |
| `movie_db/` size on disk | about 80 MB |
| Query latency, mean / median / p95 | about 205-226 ms / 232 ms / 259-270 ms (two runs of 100 queries each) |

Example results for the free-text query "a thriller about artificial intelligence": A.I. Artificial Intelligence, Ex Machina, I Robot, Species, Listening, Robot & Frank. Full details and caveats are in [docs/evaluation.md](docs/evaluation.md).

## Limitations

* Recommendations are purely content-based; there is no user personalisation, and no offline evaluation against ground truth.
* Query time is dominated by embedding the query text on CPU (a couple of hundred milliseconds), not by the vector search.
* The TMDb 5000 dataset is from 2017 and mostly English-language films; the CSVs are included for convenience and keep their original licence terms (originally distributed via Kaggle).
* The admin panel is a demo feature protected by a shared password, not real authentication.

## Repository layout

```
main.py, operations.py, admin.py   menus and features
database.py, config.py             ChromaDB access and settings
ingest_data.py                     CSV -> ChromaDB
scripts/benchmark_queries.py       latency benchmark
tests/                             unit tests for the ingestion helpers
docs/                              architecture, data pipeline, evaluation, setup; docs/guides has the original usage notes
```

## Roadmap

Ideas, not implemented: a FastAPI layer over `operations.py`, hybrid BM25 + vector search for exact titles, and a labelled evaluation set.

## License

MIT for the code, see [LICENSE](LICENSE). The TMDb data files keep their own terms.
