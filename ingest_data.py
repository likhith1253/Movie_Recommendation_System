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
def main():
    """
    Main function to read, process, and ingest movie data into ChromaDB.
    """
    print("Starting data ingestion process...")
    try:
        movies_df = pd.read_csv(MOVIES_CSV_FILE_PATH)
        credits_df = pd.read_csv(CREDITS_CSV_FILE_PATH)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    movies_df = movies_df.rename(columns={'id': 'movie_id'})
    df = pd.merge(movies_df, credits_df, on='movie_id')

    try:
        required_columns = ['overview', 'title_x', 'genres', 'cast', 'crew']
        df.dropna(subset=required_columns, inplace=True)
        df.reset_index(drop=True, inplace=True)
    except KeyError as e:
        print(f"\n[ERROR] A required column was not found: {e}")
        print("This is likely due to a mismatch in your CSV file's column names.")
        print("\nAvailable columns after merge are:")
        print(list(df.columns))
        print("\nPlease check your CSV files and update the 'required_columns' list in the script.")
        return

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity for better semantic search
    )

    print("Parsing genres, cast, and director information...")
    df['genres_list'] = parse_json_column(df, 'genres')
    df['cast_list'] = get_cast(df, 'cast')
    df['director'] = get_director(df, 'crew')
    
    print("Creating rich documents for embedding...")
    documents = [create_rich_document(row) for _, row in df.iterrows()]

    print("Preparing metadata...")
    metadatas: List[Metadata] = []
    for _, row in df.iterrows():
        item: Metadata = {
            "title": str(row.get('title_x', '')),
            "overview": str(row.get('overview', '')),
            "genres": ", ".join(row.get('genres_list', [])), # Stored as a single string
            "release_date": str(row.get('release_date', 'N/A')),
            "vote_average": float(row.get('vote_average', 0.0)),
            "runtime": int(row.get('runtime', 0)),
            "director": str(row.get('director', 'Unknown')),
            "id": str(row.get('movie_id'))
        }
        metadatas.append(item)

    ids = [str(i) for i in df.index]

    print(f"Starting ingestion of {len(ids)} movies in batches of {BATCH_SIZE}...")
    for i in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[i:i + BATCH_SIZE]
        batch_documents = documents[i:i + BATCH_SIZE]
        batch_metadatas = metadatas[i:i + BATCH_SIZE]

        collection.add(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas
        )
        print(f"  Ingested batch {i // BATCH_SIZE + 1} ({len(batch_ids)} movies)")
    
    print(f"\n✓ Data ingestion complete! Total movies ingested: {len(ids)}")

if __name__ == "__main__":
    main()