import database
from rich.console import Console
import numpy as np # Import numpy

console = Console()

def test_embedding_retrieval():
    """
    Tests if vector embeddings are successfully retrieved from the database.
    """
    console.print("[bold cyan]--- Testing Embedding Retrieval ---[/bold cyan]")

    try:
        # 1. Connect to the ChromaDB collection
        with console.status("[bold green]Connecting to ChromaDB...", spinner="dots"):
            collection = database.connect_to_collection()
        console.print("✓ Connection successful!")

        # 2. Test get_movie_by_id
        console.print("\n[bold cyan]--- Testing get_movie_by_id ---[/bold cyan]")
        
        sample_movies = database.get_all_movies(collection, limit=1)
        if not sample_movies or not sample_movies.get('ids'):
            console.print("[red]Error: Could not retrieve a sample movie to test.[/red]")
            return
            
        test_movie_id = sample_movies['ids'][0]
        console.print(f"Fetching movie with ID: [yellow]{test_movie_id}[/yellow]")

        movie_data = database.get_movie_by_id(collection, test_movie_id)

        if movie_data and 'embedding' in movie_data:
            console.print("[bold green]✓ Success![/bold green] Found 'embedding' key.")
            embedding = movie_data['embedding']
            console.print(f"  - Embedding Type: {type(embedding)}")
            console.print(f"  - Embedding Length (Dimensions): {len(embedding)}")
            console.print(f"  - Embedding Preview: {embedding}")
        else:
            console.print("[bold red]✗ Failure![/bold red] 'embedding' key not found in the result.")
            console.print("Full result:", movie_data)


        # 3. Test get_all_movies
        console.print("\n[bold cyan]--- Testing get_all_movies ---[/bold cyan]")
        
        all_movies_data = database.get_all_movies(collection, limit=3)

        # --- MODIFIED SECTION ---
        # Check if embeddings exist and the container is not empty
        if (all_movies_data and
                'embeddings' in all_movies_data and
                all_movies_data['embeddings'] is not None and
                len(all_movies_data['embeddings']) > 0):
            console.print("[bold green]✓ Success![/bold green] Found 'embeddings' key.")
            console.print(f"  - Retrieved embeddings for {len(all_movies_data['embeddings'])} movies.")
            
            first_embedding = all_movies_data['embeddings'][0]
            console.print(f"  - First Embedding Type: {type(first_embedding)}")
            # Use .shape for numpy arrays to get dimensions
            if isinstance(first_embedding, np.ndarray):
                console.print(f"  - First Embedding Shape: {first_embedding.shape}")
            else:
                 console.print(f"  - First Embedding Length: {len(first_embedding)}")
        else:
            console.print("[bold red]✗ Failure![/bold red] 'embeddings' key not found or is empty.")
            console.print("Full result:", all_movies_data)

    except Exception as e:
        console.print(f"\n[bold red]An error occurred during testing: {e}[/bold red]")

if __name__ == "__main__":
    test_embedding_retrieval()