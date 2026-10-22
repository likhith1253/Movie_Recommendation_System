# ChromaDB Integration

ChromaDB is the backbone of the entire search capabilities in the backend replacing traditional search indices (like Elasticsearch or PostgreSQL Full-Text Search) with scalable and purely semantic Vector storage mechanics natively.

## 💡 Why ChromaDB?
- **Lightweight Runtime**: It compiles via SQLite locally running fully embedded without requiring spun-up backend container microservices.
- **Native Embedding Management**: Functions out-of-the-box avoiding complex custom serialization wrappers or dependency on explicit external model APIs.
- **Metadata Tagging**: Essential for Hybrid filtering. Search combines semantic string evaluations side-by-side with literal relational deterministic `$gte` operations.

## 🗄️ Insertion Architecture

Vectors are stored using the `PersistentClient`.

```python
import chromadb
client = chromadb.PersistentClient(path="./movie_db")

# Create collection defining internal KNN calculations.
collection = client.get_or_create_collection(
    name="movies",
    metadata={"hnsw:space": "cosine"} # Toggles NLP semantic matching optimization
)
```

Insertion uses parallel list mapping to bind contextual ID, string documents and attribute constraints respectively:

```python
collection.add(
    ids=["uuid-1", "uuid-2"],
    documents=["Rich text description 1...", "Rich text description 2..."],
    metadatas=[
        {"title": "Movie A", "release_date": "2020-01-01", "vote_average": 8.0},
        {"title": "Movie B", "release_date": "1994-09-23", "vote_average": 9.3}
    ]
)
```

## 🔍 Retrieval & Query Mechanics Layer

A standard `operations.py` flow maps a query to multiple sub-filters simultaneously extracting precise user intents.

### Query Flow Example

**User Intent**: *Find me highly-rated space exploration movies post-2010.*

**Chroma API Representation:**
```python
results = collection.query(
    query_texts=["space exploration"],
    n_results=10,
    where={
        "$and": [
            {"vote_average": {"$gte": 8.0}},
            {"release_date": {"$gte": "2010-01-01"}}
        ]
    }
)
```

1. **Embedding**: "space exploration" converts real-time to a `384-D` vector array.
2. **Pruning**: Chroma filters the index for movies with `vote_average >= 8.0` and `release_date >= 2010`.
3. **Neighbor Search**: An HNSW descent maps the targeted semantic subset checking against the query vector determining Cosine Similarity proximities retrieving exact metadata mappings outputted sequentially backwards.
