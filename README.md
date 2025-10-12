# 🎬 Movie Recommendation System

A sophisticated terminal-based movie recommendation system powered by ChromaDB vector database and AI embeddings. Features a modern, interactive CLI with beautiful visualizations and advanced search capabilities.

## ✨ Features

### 🎯 User Features
- **Smart Recommendations**: Get personalized movie recommendations based on semantic similarity
- **Advanced Search**: Combine semantic search with metadata filters (year, rating, runtime)
- **Genre Exploration**: Browse movies by genre with beautiful table displays
- **Director Discovery**: Find all movies by a director (demonstrates join-like operations)
- **Rich UI**: Beautiful terminal interface with colors, tables, and progress indicators

### ⚙️ Admin Features
- **CRUD Operations**: Full Create, Read, Update, Delete functionality for movies
- **Database Insights**: View statistics and genre distribution with terminal bar charts
- **Query Benchmarking**: Test and analyze query performance
- **Indexing Education**: Learn about HNSW vector indexing and tuning parameters
- **Database Peek**: Quick view of database records

## 📁 Project Structure

```
Movie Recommendation System/
├── main.py                 # Entry point with interactive menus
├── database.py            # ChromaDB interaction layer
├── operations.py          # User-facing features
├── admin.py              # Admin panel functions
├── config.py             # Configuration and constants
├── ingest_data.py        # Data ingestion script
├── requirements.txt      # Python dependencies
├── tmdb_5000_movies.csv  # Movie dataset
├── tmdb_5000_credits.csv # Credits dataset
└── movie_db/             # ChromaDB storage (created after ingestion)
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "Movie Recommendation System"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ingest the movie data** (first time only)
   ```bash
   python ingest_data.py
   ```
   This will:
   - Load movie and credits data from CSV files
   - Extract director information from crew data
   - Create rich text documents for embedding
   - Store everything in ChromaDB
   - Takes a few minutes depending on your system

   **If you already have a database without director info:**
   ```bash
   python fix_director_metadata.py
   ```
   This updates existing records with director information.

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Try sample inputs** (see `QUICK_START.md` and `SAMPLE_INPUTS.md`)
   - Quick examples: `QUICK_START.md`
   - Comprehensive guide: `SAMPLE_INPUTS.md`

## 📖 Key Documentation to Read

1. **PROJECT_STATUS.md** - Complete project overview and status
2. **QUICK_START.md** - Quick reference guide
3. **SAMPLE_INPUTS.md** - Best inputs to try
4. **IMPORTANT_NOTES.md** - Understanding recommendation behavior
5. **INTERACTIVE_INDEXING_GUIDE.md** - Advanced indexing benchmark feature (NEW)

## 🎮 Usage Guide

### Main Menu Options

1. **🎯 Get Movie Recommendations**
   - Enter a movie title you like
   - Specify how many recommendations you want
   - View similar movies with similarity scores

2. **🔍 Advanced Search**
   - Enter a semantic search query (e.g., "a thriller about artificial intelligence")
   - Optionally add filters:
     - Release year (after/before a specific year)
     - Minimum rating (0-10)
     - Maximum runtime (in minutes)
   - Combines vector search with metadata filtering

3. **🎭 Find Movies by Genre**
   - Select or type a genre
   - Browse all movies in that genre
   - Autocomplete suggestions for common genres

4. **🎬 Explore by Director**
   - Enter a movie title
   - System finds the director
   - Shows all other movies by that director
   - Demonstrates "join-like" operations in vector DB

5. **📋 List Sample Movies**
   - View a sample of movies from the database
   - Specify how many to display

6. **⚙️ Admin Panel**
   - Password protected (default: `admin123`)
   - Access advanced database operations

### Admin Panel Options

- **➕ Create Movie**: Add a new movie with all details
- **📖 Read Movie by ID**: View full details of a specific movie
- **✏️ Update Movie**: Modify existing movie information
- **🗑️ Delete Movie**: Remove a movie from the database
- **👀 Peek at Database**: Quick view of first N records
- **📊 Database Insights**: 
  - Total movie count
  - Top 10 genres with bar chart visualization
- **⚡ Benchmark Queries**:
  - Run performance tests
  - View average, min, max query times
  - Learn about HNSW indexing and tuning
- **🔬 Interactive Indexing Benchmark** (NEW):
  - Dynamically test different distance functions (cosine, L2, IP)
  - Recreate collection with new settings
  - Real-time progress tracking during re-ingestion
  - Comprehensive performance benchmarking
  - Compare results across different configurations

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Database settings
DB_PATH = "movie_db"
COLLECTION_NAME = "movies"

# Admin password
ADMIN_PASSWORD = "admin123"  # Change this!

# Search settings
DEFAULT_RESULTS = 6
MAX_SEARCH_RESULTS = 50

# Display settings
TOP_GENRES_COUNT = 10
BENCHMARK_ITERATIONS = 10
```

## 🎨 Technical Highlights

### Vector Database Features

1. **Semantic Search**: Uses sentence transformers to create embeddings
2. **Metadata Filtering**: Combines vector search with structured queries
3. **HNSW Indexing**: Fast approximate nearest neighbor search
4. **Batch Processing**: Efficient data ingestion

### Advanced ChromaDB Operations

- **Complex Filters**: `$and`, `$or`, `$gte`, `$lte` operators
- **Hybrid Search**: Semantic + metadata filtering in single query
- **Join Simulation**: Multi-step queries to simulate relational joins
- **Performance Monitoring**: Built-in benchmarking tools

### UI/UX Features

- **Rich Tables**: Beautiful formatted tables with colors
- **Interactive Menus**: Questionary-powered selection menus
- **Progress Indicators**: Visual feedback for long operations
- **Styled Panels**: Information displayed in bordered panels
- **Color Coding**: Consistent color scheme throughout

## 📊 Data Schema

Each movie in the database contains:

```python
{
    "id": "unique_id",
    "metadata": {
        "title": "Movie Title",
        "overview": "Plot summary",
        "genres": "Action, Thriller",
        "release_date": "2024-01-01",
        "vote_average": 7.5,
        "runtime": 120,
        "director": "Director Name"
    },
    "document": "Rich text for embedding..."
}
```

## 🔍 Example Queries

### Semantic Search
```
"a movie about time travel and paradoxes"
"romantic comedy set in New York"
"dark psychological thriller"
```

### Advanced Search with Filters
```
Query: "space exploration"
Filters:
  - After 2010
  - Rating > 7.0
  - Runtime < 150 minutes
```

### Best Sample Inputs for Testing

**Recommendations:**
- `Inception` - Mind-bending sci-fi thriller
- `The Dark Knight` - Superhero/crime film
- `Pulp Fiction` - Tarantino classic
- `The Matrix` - Sci-fi action

**Director Exploration:**
- `Inception` → Christopher Nolan filmography
- `Pulp Fiction` → Quentin Tarantino films
- `Avatar` → James Cameron movies
- `Jurassic Park` → Steven Spielberg films

**See `SAMPLE_INPUTS.md` for comprehensive examples showcasing ChromaDB's full capabilities.**

## 🛠️ Development

### Module Responsibilities

- **`config.py`**: Centralized configuration
- **`database.py`**: Low-level ChromaDB operations
- **`operations.py`**: User-facing features with rich UI
- **`admin.py`**: Admin operations and analytics
- **`main.py`**: Application flow and menu system
- **`ingest_data.py`**: Data loading and preprocessing

### Adding New Features

1. Add database functions to `database.py`
2. Create user-facing wrappers in `operations.py` or `admin.py`
3. Add menu options in `main.py`
4. Update configuration in `config.py` if needed

## 📝 Notes

- **First Run**: Must run `ingest_data.py` before using the application
- **Database Location**: ChromaDB stores data in `./movie_db/` directory
- **Re-ingestion**: Delete `movie_db/` folder to re-ingest data
- **Performance**: Query speed depends on dataset size and system resources
- **Director Data**: Extracted from crew information during ingestion

## 🔐 Security

- Change the default admin password in `config.py`
- Admin panel is password protected
- Destructive operations require confirmation

## 🐛 Troubleshooting

**"Collection not found" error**
- Run `python ingest_data.py` to create the database

**Slow queries**
- Normal for first query (model loading)
- Subsequent queries should be faster
- Check benchmark results in admin panel

**Import errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment if using one

**CSV file not found**
- Ensure `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` are in the project directory

## 📚 Technologies Used

- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Text embedding models
- **Rich**: Terminal formatting and tables
- **Questionary**: Interactive prompts
- **Pandas**: Data processing
- **Python 3.8+**: Core language

## 🎓 Learning Resources

The application includes educational content about:
- Vector database indexing (HNSW algorithm)
- Semantic search vs keyword search
- Metadata filtering in vector databases
- Query performance optimization
- Embedding-based recommendations

Access this through the **Admin Panel → Benchmark Queries** option.

## 📄 License

This project uses the TMDB 5000 Movie Dataset. Please refer to the dataset's license for usage terms.

## 🤝 Contributing

Feel free to enhance this project by:
- Adding new search features
- Improving the UI
- Optimizing query performance
- Adding more analytics
- Expanding the dataset

---

**Enjoy exploring movies with AI-powered recommendations! 🎬🍿**
