# System Features

The Movie Recommendation System offers an extensive suite of engineered features spanning general user searches, deterministic filtering, and database analytics.

## 👤 User Operations

- **Semantic Recommendations (`🎯 Get Movie Recommendations`)**
  - Input any existing movie title as a seed.
  - The system isolates the seed movie's embedding and runs a KNN search on the local index finding structurally similar movie entries relying purely on contextual similarity of the descriptions/crew rather than explicit rule associations.

- **Fuzzy Intent Matching (`🔍 Advanced Search`)**
  - Users are not limited to keywords. Abstract queries like *"an epic journey across the desert"* process natively to return contextual results.

- **Multi-Dimensional Metadata Filtering (`🔍 Advanced Search Options`)**
  - **Temporal Filter:** Isolates results to parameters like `< or > year limit`.
  - **Quality Floor:** Applies `$gte` filters to vote rating averages.
  - **Constraint limits:** Filters for runtime thresholds combining with active vector clustering.

- **Dynamic Genre Extrapolations (`🎭 Find Movies by Genre`)**
  - Uses exact string matching in aggregated metadata for quick genre breakdowns bypassing dense search for optimized speeds where context is unnecessary.

- **Cross-Referential Graph Lookups (`🎬 Explore by Director`)**
  - Executes a multi-step query equivalent to SQL JOIN operations. Extracts the unique metadata constraint attached to a single contextually retrieved movie and searches horizontally across the index for similarly matching nodes.

- **Peek State Viewer (`📋 List Sample Movies`)**
  - Fast limit retrieval functionality acting as a `SELECT * LIMIT X` SQL counterpart for raw view capabilities.

## 🛠️ Administrative Operations

*(Password protected - Default is `admin123` via `config.py`)*

- **Interactive Database Configuration Benchmarker (`🔬 Interactive Indexing Benchmark`)**
  - Enables dynamic teardown and recreation of the entire index via admin UI toggling between `cosine`, `L2 Euclidean`, and `Inner Product (ip)` distance metrics. It subsequently executes queries over exactly mapped datasets and provides an empirical performance analysis (time vs. iteration).

- **Performance Regression Checks (`⚡ Benchmark Queries`)**
  - Triggers repeated sample queries logging average response times, min bounds, and max bounds to calculate query latency decay tracking over time.

- **CRUD Access**
  - **Create:** Validates inputs adding newly vectorized documents.
  - **Read/Peek:** Exposes underlying metadata limits targeting specific sequential items.
  - **Update:** Patches partial modifications over subsets retaining structural vector representations.
  - **Delete:** Nullifies items triggering index rebalancing.

- **Statistical Distillation (`📊 Database Insights`)**
  - Operates aggregation patterns reading string distributions on parameters like 'Genres' charting a rich CLI diagram reflecting dataset topology biases. Minimum boilerplate layout relying on `chromadb` index scans.
