"""
Script to add director metadata to existing ChromaDB collection.
This updates the database without requiring a full re-ingestion.
"""

import pandas as pd
import chromadb
import ast
from config import (
    MOVIES_CSV_FILE_PATH,
    CREDITS_CSV_FILE_PATH,
    DB_PATH,
    COLLECTION_NAME,
    BATCH_SIZE
)

def get_director(crew_data):
    """Safely extracts the director's name from the 'crew' column."""
    try:
        crew_list = ast.literal_eval(crew_data)
        director = next((d['name'] for d in crew_list if d.get('job') == 'Director'), 'Unknown')
        return director
    except (ValueError, SyntaxError, TypeError):
        return 'Unknown'

def main():
    """
    Main function to update existing movies with director information.
    """
    print("Starting director metadata update process...")
    
    # Load CSV files
    try:
        print("Loading CSV files...")
        movies_df = pd.read_csv(MOVIES_CSV_FILE_PATH)
        credits_df = pd.read_csv(CREDITS_CSV_FILE_PATH)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Merge dataframes
    print("Merging movie and credits data...")
    movies_df = movies_df.rename(columns={'id': 'movie_id'})
    df = pd.merge(movies_df, credits_df, on='movie_id')
    
    # Extract directors
    print("Extracting director information...")
    df['director'] = df['crew'].apply(get_director)
    
    # Create director mapping: movie_id -> director
    director_map = dict(zip(df['movie_id'].astype(str), df['director']))
    
    print(f"Found director information for {len(director_map)} movies")
    
    # Connect to ChromaDB
    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    
    print(f"Current collection size: {collection.count()} movies")
    
    # Get all existing movies
    print("Fetching existing movies from database...")
    all_movies = collection.get(include=["metadatas", "documents"])
    
    print(f"Processing {len(all_movies['ids'])} movies...")
    
    # Update movies in batches
    updated_count = 0
    skipped_count = 0
    
    for i in range(0, len(all_movies['ids']), BATCH_SIZE):
        batch_ids = all_movies['ids'][i:i + BATCH_SIZE]
        batch_metadatas = all_movies['metadatas'][i:i + BATCH_SIZE]
        batch_documents = all_movies['documents'][i:i + BATCH_SIZE]
        
        # Update metadata with director information
        for j, (db_id, metadata) in enumerate(zip(batch_ids, batch_metadatas)):
            # Use the ChromaDB ID (which is the movie_id) to look up director
            movie_id = db_id
            
            # Check if director already exists
            if 'director' in metadata and metadata['director'] != 'Unknown':
                skipped_count += 1
                continue
            
            # Get director from mapping
            director = director_map.get(movie_id, 'Unknown')
            metadata['director'] = director
            metadata['id'] = movie_id  # Also add the id to metadata for future reference
            
            if director != 'Unknown':
                updated_count += 1
        
        # Upsert the batch
        collection.upsert(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas
        )
        
        print(f"  Processed batch {i // BATCH_SIZE + 1} ({len(batch_ids)} movies)")
    
    print(f"\n✓ Update complete!")
    print(f"  - Movies updated with director info: {updated_count}")
    print(f"  - Movies already had director info: {skipped_count}")
    print(f"  - Movies with 'Unknown' director: {len(all_movies['ids']) - updated_count - skipped_count}")
    
    # Verify the update
    print("\nVerifying update...")
    sample = collection.peek(limit=3)
    print("\nSample metadata after update:")
    for i, metadata in enumerate(sample['metadatas'], 1):
        print(f"\n{i}. {metadata.get('title', 'Unknown')}")
        print(f"   Director: {metadata.get('director', 'NOT FOUND')}")

if __name__ == "__main__":
    main()
