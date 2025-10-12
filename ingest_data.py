import pandas as pd
import chromadb
import ast
from typing import List
from chromadb.types import Metadata

from config import (
    MOVIES_CSV_FILE_PATH,
    CREDITS_CSV_FILE_PATH,
    DB_PATH,
    COLLECTION_NAME,
    BATCH_SIZE
)

# --- Helper Functions ---
def parse_json_column(data, column_name):
    """Safely parses a JSON string in a DataFrame column."""
    parsed_data = []
    for item in data[column_name]:
        try:
            parsed_list = [d['name'] for d in ast.literal_eval(item)]
            parsed_data.append(parsed_list)
        except (ValueError, SyntaxError, TypeError):
            parsed_data.append([])
    return parsed_data

def get_cast(data, column_name):
    """Safely gets the cast names from the 'cast' column."""
    cast_data = []
    for item in data[column_name]:
        try:
            cast_list = [d['name'] for d in ast.literal_eval(item)[:5]] # Get top 5 actors
            cast_data.append(cast_list)
        except (ValueError, SyntaxError, TypeError):
            cast_data.append([])
    return cast_data


def get_director(data, column_name):
    """Safely extracts the director's name from the 'crew' column."""
    director_data = []
    for item in data[column_name]:
        try:
            crew_list = ast.literal_eval(item)
            director = next((d['name'] for d in crew_list if d.get('job') == 'Director'), 'Unknown')
            director_data.append(director)
        except (ValueError, SyntaxError, TypeError):
            director_data.append('Unknown')
    return director_data


def create_rich_document(row):
    """Creates a detailed text document for embedding."""
    title = row.get('title_x', 'Unknown Title')
    overview = row.get('overview', 'No overview available.')
    genres_str = ", ".join(row.get('genres_list', []))
    cast_str = ", ".join(row.get('cast_list', []))
    director = row.get('director', 'Unknown')
    return f"Title: {title}. Overview: {overview}. Genres: {genres_str}. Cast: {cast_str}. Director: {director}."

# --- Main Ingestion Logic ---
def ingest_data(distance_function: str = "cosine", progress_callback=None):
    """
    Callable function to read, process, and ingest movie data into ChromaDB.
    
    Args:
        distance_function: Distance metric to use ('cosine', 'l2', or 'ip')
        progress_callback: Optional callback function for progress updates
                          Should accept (current, total, message) parameters
    
    Returns:
        Tuple of (success: bool, total_records: int, error_message: str or None)
    """
    try:
        if progress_callback:
            progress_callback(0, 100, "Loading CSV files...")
        
        movies_df = pd.read_csv(MOVIES_CSV_FILE_PATH)
        credits_df = pd.read_csv(CREDITS_CSV_FILE_PATH)
    except FileNotFoundError as e:
        return False, 0, f"CSV files not found: {e}"

    movies_df = movies_df.rename(columns={'id': 'movie_id'})
    df = pd.merge(movies_df, credits_df, on='movie_id')

    try:
        required_columns = ['overview', 'title_x', 'genres', 'cast', 'crew']
        df.dropna(subset=required_columns, inplace=True)
        df.reset_index(drop=True, inplace=True)
    except KeyError as e:
        return False, 0, f"Required column not found: {e}"

    if progress_callback:
        progress_callback(10, 100, "Connecting to ChromaDB...")
    
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": distance_function}
    )

    if progress_callback:
        progress_callback(20, 100, "Parsing movie data...")
    
    df['genres_list'] = parse_json_column(df, 'genres')
    df['cast_list'] = get_cast(df, 'cast')
    df['director'] = get_director(df, 'crew')
    
    if progress_callback:
        progress_callback(30, 100, "Creating embeddings...")
    
    documents = [create_rich_document(row) for _, row in df.iterrows()]

    metadatas: List[Metadata] = []
    for _, row in df.iterrows():
        item: Metadata = {
            "title": str(row.get('title_x', '')),
            "overview": str(row.get('overview', '')),
            "genres": ", ".join(row.get('genres_list', [])),
            "release_date": str(row.get('release_date', 'N/A')),
            "vote_average": float(row.get('vote_average', 0.0)),
            "runtime": int(row.get('runtime', 0)),
            "director": str(row.get('director', 'Unknown')),
            "id": str(row.get('movie_id'))
        }
        metadatas.append(item)

    ids = [str(i) for i in df.index]
    total_batches = (len(ids) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[i:i + BATCH_SIZE]
        batch_documents = documents[i:i + BATCH_SIZE]
        batch_metadatas = metadatas[i:i + BATCH_SIZE]

        collection.add(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas
        )
        
        if progress_callback:
            batch_num = i // BATCH_SIZE + 1
            progress_pct = 30 + int((batch_num / total_batches) * 70)
            progress_callback(progress_pct, 100, f"Ingesting batch {batch_num}/{total_batches}...")
    
    if progress_callback:
        progress_callback(100, 100, "Ingestion complete!")
    
    return True, len(ids), None


def main():
    """
    Main function for command-line ingestion.
    """
    print("Starting data ingestion process...")
    
    def print_progress(current, total, message):
        print(f"[{current}/{total}] {message}")
    
    success, count, error = ingest_data("cosine", print_progress)
    
    if success:
        print(f"\n✓ Data ingestion complete! Total movies ingested: {count}")
    else:
        print(f"\n✗ Data ingestion failed: {error}")

if __name__ == "__main__":
    main()