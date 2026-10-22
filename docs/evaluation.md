# System Evaluation

Evaluation within embedding-based semantic search workflows differs from traditional categorical ML output assessments as classifications aren't binary but dimensional.

## ⚖️ Evaluation Metrics

The system continuously assesses index performance and latency decay relying on algorithmic benchmarks included implicitly inside `admin.py`.

- **Latencies (`ms`)**: Average latency required to hit query parameters, serialize outputs locally, and map string boundaries over dense datasets.
- **Relative Distance Analysis**: Contextual drift calculated by absolute distance `d <= 2`. `1.0` distance reflects neutral relationships whereas bounded metrics around `0.1` map nearly exactly duplicated entries.
- **Semantic Efficacy Comparison**: Interactive benchmarking dynamically builds test indices assigning specific `hnsw:space` criteria scaling between `L2` and `Cosine` matching metrics evaluating subjective query drift context ranges.

## 📊 Measured Query Latency

Measured with `python scripts/benchmark_queries.py` (5 natural-language queries x 20 repetitions, top-6 results, after a warm-up query) on a Windows laptop CPU with chromadb 0.5.0 and the default embedding model. Each latency includes embedding the query text, so it is dominated by the embedding step rather than the HNSW search.

| Run | Mean | Median | p95 | Max |
|---|---|---|---|---|
| 1 | 204.6 ms | 232.8 ms | 270.3 ms | 296.4 ms |
| 2 | 225.9 ms | 231.9 ms | 259.1 ms | 277.7 ms |

| Fact | Value |
|---|---|
| Movies in the collection after `ingest_data.py` | 4,800 (4,803 TMDb rows minus rows with missing overview/genres/cast/crew) |
| On-disk size of `movie_db/` | about 80 MB |
| Ingestion time (first run, including model download) | about 6.7 minutes |

Earlier versions of this page quoted ~12 ms average latency and ~60 MB; those figures could not be reproduced and were removed. Latency varies by machine, so re-run the script for your own numbers.

## 🔎 Qualitative check (no ground truth)

There are no relevance labels in this project, so recommendation quality is not scored (no precision/recall/NDCG). Example top results from the benchmark script:

| Query | Top results |
|---|---|
| a thriller about artificial intelligence | A.I. Artificial Intelligence, Ex Machina, I, Robot, Species, Listening, Robot & Frank |
| space exploration and survival | Lost in Space, Gravity, Red Planet, Mission to Mars, Star Trek, The Inhabited Island |
| romantic comedy in Paris | Midnight in Paris, Paris, je t'aime, About Last Night, Cheri, Jefferson in Paris, Irreversible |

The first two look plausible; the Paris query shows the semantic search matching the city name (and returning one film, Irreversible, that is neither romantic nor a comedy). Judge for yourself with `python main.py`.

## Model Toggling Review

1. **Cosine Calculation:** `d = 1.0 - (u \cdot v) / (||u||_2 ||v||_2)` 
   - Proved exponentially better mapping abstract text like "action movie."
2. **L2 Euclidean Calculation:** `d = ||u - v||_2^2` 
   - Evaluated lower contextual relativity handling broad prompt sentences scaling incorrectly without strict input vector normalization.
