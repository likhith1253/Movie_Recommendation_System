"""
Database module for ChromaDB interactions.
Contains all functions for connecting to and querying the database.
"""

import chromadb
from typing import Optional, List, Dict, Any
from chromadb.api.models.Collection import Collection
import time

from config import DB_PATH, COLLECTION_NAME


def connect_to_collection() -> Optional[Collection]:
    """
    Connects to the ChromaDB and returns the collection object.
    
    Returns:
        Collection object if successful, None otherwise.
    """
    try:
        client = chromadb.PersistentClient(path=DB_PATH)
        collection = client.get_collection(name=COLLECTION_NAME)
        return collection
    except Exception as e:
        raise ConnectionError(f"Failed to connect to ChromaDB: {e}")


def get_collection_count(collection: Collection) -> int:
    """
    Gets the total number of movies in the collection.
    
    Args:
        collection: ChromaDB collection object.
        
    Returns:
        Total count of movies.
    """
    return collection.count()


def query_movies(
    collection: Collection,
    query_text: str,
    n_results: int = 6,
    where: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Performs a semantic search query on the movie collection.
    
    Args:
        collection: ChromaDB collection object.
        query_text: The search query text.
        n_results: Number of results to return.
        where: Optional metadata filter.
        
    Returns:
        Query results dictionary.
    """
    try:
        if where:
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
        else:
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
        return results
    except Exception as e:
        raise RuntimeError(f"Query failed: {e}")


def get_movie_by_id(collection: Collection, movie_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a movie by its ID.
    
    Args:
        collection: ChromaDB collection object.
        movie_id: The movie ID to fetch.
        
    Returns:
        Dictionary containing movie data or None if not found.
    """
    try:
        result = collection.get(
            ids=[movie_id],
            include=["metadatas", "documents", "embeddings"] # Add "embeddings" here
        )
        if not result['ids']:
            return None
        return {
            'id': result['ids'][0],
            'metadata': result['metadatas'][0],
            'document': result['documents'][0],
            'embedding': result['embeddings'][0] # Add the embedding to the result
        }
    except Exception as e:
        raise RuntimeError(f"Failed to fetch movie: {e}")


def get_all_movies(collection: Collection, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Retrieves all movies from the collection.
    
    Args:
        collection: ChromaDB collection object.
        limit: Optional limit on number of results.
        
    Returns:
        Dictionary containing all movie data.
    """
    try:
        if limit:
            return collection.get(limit=limit, include=["metadatas", "embeddings"]) # Add "embeddings" here
        else:
            return collection.get(include=["metadatas", "embeddings"]) # Add "embeddings" here
    except Exception as e:
        raise RuntimeError(f"Failed to fetch movies: {e}")


def add_movie(
    collection: Collection,
    movie_id: str,
    document: str,
    metadata: Dict[str, Any]
) -> None:
    """
    Adds or updates a movie in the collection.
    
    Args:
        collection: ChromaDB collection object.
        movie_id: Unique movie ID.
        document: Text document for embedding.
        metadata: Movie metadata dictionary.
    """
    try:
        collection.upsert(
            ids=[movie_id],
            documents=[document],
            metadatas=[metadata]
        )
    except Exception as e:
        raise RuntimeError(f"Failed to add movie: {e}")


def update_movie(
    collection: Collection,
    movie_id: str,
    document: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Updates a movie's document and/or metadata.
    
    Args:
        collection: ChromaDB collection object.
        movie_id: Movie ID to update.
        document: Optional new document text.
        metadata: Optional new metadata.
    """
    try:
        # Fetch existing data
        existing = get_movie_by_id(collection, movie_id)
        if not existing:
            raise ValueError(f"Movie with ID '{movie_id}' not found")
        
        # Use existing data if not provided
        final_document = document if document else existing['document']
        final_metadata = metadata if metadata else existing['metadata']
        
        collection.upsert(
            ids=[movie_id],
            documents=[final_document],
            metadatas=[final_metadata]
        )
    except Exception as e:
        raise RuntimeError(f"Failed to update movie: {e}")


def delete_movie(collection: Collection, movie_id: str) -> None:
    """
    Deletes a movie from the collection.
    
    Args:
        collection: ChromaDB collection object.
        movie_id: Movie ID to delete.
    """
    try:
        # Check if movie exists
        if not get_movie_by_id(collection, movie_id):
            raise ValueError(f"Movie with ID '{movie_id}' not found")
        
        collection.delete(ids=[movie_id])
    except Exception as e:
        raise RuntimeError(f"Failed to delete movie: {e}")


def peek_collection(collection: Collection, limit: int = 5) -> Dict[str, Any]:
    """
    Peeks at the first N records in the collection.
    
    Args:
        collection: ChromaDB collection object.
        limit: Number of records to peek at.
        
    Returns:
        Dictionary containing peeked records.
    """
    try:
        return collection.peek(limit=limit)
    except Exception as e:
        raise RuntimeError(f"Failed to peek collection: {e}")


def search_by_metadata(
    collection: Collection,
    field: str,
    value: Any,
    operator: str = "$eq"
) -> List[Dict[str, Any]]:
    """
    Searches movies by metadata field.
    
    Args:
        collection: ChromaDB collection object.
        field: Metadata field to search.
        value: Value to search for.
        operator: Comparison operator ($eq, $ne, $gt, $gte, $lt, $lte, $in, $nin).
        
    Returns:
        List of matching movies.
    """
    try:
        results = collection.get(
            where={field: {operator: value}},
            include=["metadatas"]
        )
        
        movies = []
        for i, movie_id in enumerate(results['ids']):
            movies.append({
                'id': movie_id,
                'metadata': results['metadatas'][i]
            })
        return movies
    except Exception as e:
        raise RuntimeError(f"Metadata search failed: {e}")


def benchmark_query(
    collection: Collection,
    query_text: str,
    n_results: int = 10,
    iterations: int = 10
) -> Dict[str, float]:
    """
    Benchmarks query performance.
    
    Args:
        collection: ChromaDB collection object.
        query_text: Query text to benchmark.
        n_results: Number of results per query.
        iterations: Number of iterations to run.
        
    Returns:
        Dictionary with timing statistics.
    """
    times = []
    
    for _ in range(iterations):
        start_time = time.time()
        collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        end_time = time.time()
        times.append(end_time - start_time)
    
    return {
        'average': sum(times) / len(times),
        'min': min(times),
        'max': max(times),
        'total': sum(times)
    }


def get_genre_distribution(collection: Collection) -> Dict[str, int]:
    """
    Gets the distribution of genres across all movies.
    
    Args:
        collection: ChromaDB collection object.
        
    Returns:
        Dictionary mapping genre names to counts.
    """
    try:
        all_movies = collection.get(include=["metadatas"])
        genre_counts: Dict[str, int] = {}
        
        for metadata in all_movies['metadatas']:
            genres_str = metadata.get('genres', '')
            if genres_str:
                genres = [g.strip() for g in genres_str.split(',')]
                for genre in genres:
                    if genre:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # Sort by count descending
        return dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True))
    except Exception as e:
        raise RuntimeError(f"Failed to get genre distribution: {e}")


def find_movies_by_director(collection: Collection, director: str) -> List[Dict[str, Any]]:
    """
    Finds all movies by a specific director.
    
    Args:
        collection: ChromaDB collection object.
        director: Director name to search for.
        
    Returns:
        List of movies by the director.
    """
    try:
        # Get all movies and filter by director
        all_movies = collection.get(include=["metadatas"])
        director_movies = []
        
        for i, metadata in enumerate(all_movies['metadatas']):
            movie_director = metadata.get('director', '')
            if movie_director and director.lower() in movie_director.lower():
                director_movies.append({
                    'id': all_movies['ids'][i],
                    'metadata': metadata
                })
        
        return director_movies
    except Exception as e:
        raise RuntimeError(f"Failed to find movies by director: {e}")
