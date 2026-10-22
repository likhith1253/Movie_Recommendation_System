# Environment Setup and Installation

Follow these steps to deploy and integrate the backend locally.

## Prerequisite Tooling

- **Language Support**: Python `>= 3.9`
- **Memory Requirements**: Minimum 4GB RAM required for localized ML transformer evaluations.
- **Compiler Requirements**: A standard C++ pipeline (Build Tools for Visual Studio on Windows, or `build-essential` on Linux/macOS) is often required implicitly by underlying `hnswlib` integrations utilized during ChromaDB indexing.

## 1. Local Environment Configuration

It is considered good practice to run data pipelines inside isolated virtual environments.

**Windows:**
```shell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```shell
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Dependency Management

The project relies strictly on locked versions for API consistency matching `requirements.txt`.

```shell
pip install -r requirements.txt
```

Core dependencies explained:
- `chromadb (0.5.0)`: Manages the local persistent vector HNSW environment.
- `sentence-transformers (2.7.0)`: Instantiates the PyTorch model for document embeddings.
- `pandas (2.2.2)`: Core processing mechanism for data frame manipulation.
- `rich & questionary`: UI layer implementations.

## 3. Dataset Configuration

1. Procure the TMDb datasets (`tmdb_5000_movies.csv` and `tmdb_5000_credits.csv`).
2. Place them precisely at the root path of the project folder. Ensure filenames match the expectations established inside `config.py`:
   - `MOVIES_CSV_FILE_PATH="tmdb_5000_movies.csv"`
   - `CREDITS_CSV_FILE_PATH="tmdb_5000_credits.csv"`

## 4. Run Vector Engine Initialization

Local deployment requires an initial ingestion cycle to convert raw CSV data into mathematical representations stored inside `./movie_db`.

Run the ingestion tool:

```shell
python ingest_data.py
```

*Note: The first execution pulls the `all-MiniLM-L6-v2` weighing approximately 90MB locally to cache (`~/.cache/huggingface/hub/`). Expect ingestion duration to scale with available hardware processing.*

## 5. Execution

Verify implementation parameters by running the evaluation test suite:
```shell
python test_system.py
```

If it reads `All tests passed!`, run the backend interactive menu:

```shell
python main.py
```

By default, the active ChromaDB persistent instance maps to port utilization within the local Python runtime space only. For administrative tasks triggering updates and configuration patches, the default password is `admin123`.
