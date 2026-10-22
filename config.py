"""
Configuration file for the Movie Recommendation System.
Contains all constants and configuration settings.
"""

# Database Configuration
DB_PATH = "movie_db"
COLLECTION_NAME = "movies"

# CSV File Paths
MOVIES_CSV_FILE_PATH = "tmdb_5000_movies.csv"
CREDITS_CSV_FILE_PATH = "tmdb_5000_credits.csv"

# Admin Configuration
import os

# Demo default so the admin panel works out of the box; set MOVIE_ADMIN_PASSWORD to override.
ADMIN_PASSWORD = os.environ.get("MOVIE_ADMIN_PASSWORD", "admin123")

# Application Settings
BATCH_SIZE = 500  # For data ingestion
DEFAULT_RESULTS = 6  # Default number of recommendations
MAX_SEARCH_RESULTS = 50  # Maximum results for advanced search

# Display Settings
TOP_GENRES_COUNT = 10  # Number of genres to show in insights
BENCHMARK_ITERATIONS = 10  # Number of iterations for query benchmarking

# ChromaDB Indexing Information
INDEXING_INFO = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    VECTOR DATABASE INDEXING EXPLAINED                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

ChromaDB uses HNSW (Hierarchical Navigable Small World) indexing for efficient
approximate nearest neighbor search.

🔍 HOW HNSW WORKS:
   • Builds a multi-layer graph structure where each node is a vector
   • Higher layers contain fewer nodes for fast navigation
   • Lower layers contain more nodes for precise search
   • Search starts at the top layer and moves down to find nearest neighbors

⚙️  KEY PARAMETERS:

   M (Max Connections):
   • Number of bi-directional links per node
   • Higher M = Better recall but more memory usage
   • Typical range: 16-64
   • Default: 16

   ef_construction (Construction Time):
   • Size of dynamic candidate list during index building
   • Higher value = Better quality index but slower construction
   • Typical range: 100-500
   • Default: 100

   ef_search (Query Time):
   • Size of dynamic candidate list during search
   • Higher value = Better accuracy but slower queries
   • Typical range: 100-500
   • Default: 10

📊 TRADE-OFFS:
   Speed vs Accuracy: Lower ef_search = faster but less accurate
   Memory vs Recall: Higher M = more memory but better results
   Build Time vs Quality: Higher ef_construction = slower build but better index

💡 TUNING TIPS:
   • For high accuracy: Increase ef_search (e.g., 200-500)
   • For fast queries: Decrease ef_search (e.g., 10-50)
   • For better recall: Increase M (e.g., 32-64)
   • Balance based on your dataset size and query requirements
"""
