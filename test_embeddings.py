import database
from rich.console import Console
from rich.table import Table
import numpy as np

console = Console()

def find_movie_by_name(collection, movie_name: str):
    """
    Searches for a movie by name in the collection.
    
    Args:
        collection: ChromaDB collection object.
        movie_name: Name of the movie to search for.
        
    Returns:
        Movie data if found, None otherwise.
    """
    try:
        # Get all movies and search for the movie name
        all_movies = collection.get(include=["metadatas", "embeddings"])
        
        for i, metadata in enumerate(all_movies['metadatas']):
            title = metadata.get('title', '')
            if title and movie_name.lower() in title.lower():
                return {
                    'id': all_movies['ids'][i],
                    'metadata': metadata,
                    'embedding': all_movies['embeddings'][i] if all_movies['embeddings'] else None
                }
        
        return None
    except Exception as e:
        console.print(f"[bold red]Error searching for movie: {e}[/bold red]")
        return None


def display_movie_embeddings(movie_name: str):
    """
    Takes a movie name as input and displays its embeddings.
    
    Args:
        movie_name: Name of the movie to search for.
    """
    console.print(f"[bold cyan]--- Searching for Movie: '{movie_name}' ---[/bold cyan]\n")
    
    try:
        # Connect to the ChromaDB collection
        with console.status("[bold green]Connecting to ChromaDB...", spinner="dots"):
            collection = database.connect_to_collection()
        console.print("✓ Connection successful!\n")
        
        if collection is None:
            console.print("[bold red]Error: Failed to connect to the collection.[/bold red]")
            return
        
        # Search for the movie
        with console.status(f"[bold green]Searching for '{movie_name}'...", spinner="dots"):
            movie_data = find_movie_by_name(collection, movie_name)
        
        if movie_data is None:
            console.print(f"[bold red]✗ Movie '{movie_name}' not found in the database.[/bold red]")
            console.print("\n[yellow]Tip: Try searching with a partial name or check the spelling.[/yellow]")
            return
        
        # Display movie information
        console.print("[bold green]✓ Movie Found![/bold green]\n")
        
        # Create a table for movie details
        table = Table(title="Movie Details", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", width=20)
        table.add_column("Value", style="white")
        
        metadata = movie_data['metadata']
        table.add_row("Title", metadata.get('title', 'N/A'))
        table.add_row("Genres", metadata.get('genres', 'N/A'))
        table.add_row("Director", metadata.get('director', 'N/A'))
        
        # Extract year from release_date
        release_date = metadata.get('release_date', 'N/A')
        year = release_date.split('-')[0] if release_date and release_date != 'N/A' else 'N/A'
        table.add_row("Year", year)
        
        table.add_row("Release Date", release_date)
        table.add_row("Rating", str(metadata.get('vote_average', 'N/A')))
        table.add_row("Runtime", f"{metadata.get('runtime', 'N/A')} min" if metadata.get('runtime') else 'N/A')
        
        console.print(table)
        
        # Display embedding information
        console.print("\n[bold cyan]--- Embedding Information ---[/bold cyan]")
        
        embedding = movie_data['embedding']
        if embedding is not None:
            console.print(f"  - Embedding Type: [yellow]{type(embedding)}[/yellow]")
            
            if isinstance(embedding, np.ndarray):
                console.print(f"  - Embedding Shape: [yellow]{embedding.shape}[/yellow]")
                console.print(f"  - Embedding Dimensions: [yellow]{len(embedding)}[/yellow]")
            else:
                console.print(f"  - Embedding Length: [yellow]{len(embedding)}[/yellow]")
            
            # Display embedding statistics
            embedding_array = np.array(embedding)
            console.print(f"  - Min Value: [yellow]{np.min(embedding_array):.6f}[/yellow]")
            console.print(f"  - Max Value: [yellow]{np.max(embedding_array):.6f}[/yellow]")
            console.print(f"  - Mean Value: [yellow]{np.mean(embedding_array):.6f}[/yellow]")
            console.print(f"  - Std Deviation: [yellow]{np.std(embedding_array):.6f}[/yellow]")
            
            # Display first 10 values of the embedding
            console.print(f"\n  - First 10 Embedding Values:")
            console.print(f"    [yellow]{embedding_array[:10]}[/yellow]")
            
            # Optionally display the full embedding
            show_full = console.input("\n[cyan]Display full embedding? (y/n): [/cyan]").strip().lower()
            if show_full == 'y':
                console.print(f"\n[bold cyan]Full Embedding:[/bold cyan]")
                console.print(f"[yellow]{embedding_array}[/yellow]")
        else:
            console.print("[bold red]✗ No embedding found for this movie.[/bold red]")
    
    except Exception as e:
        console.print(f"\n[bold red]An error occurred: {e}[/bold red]")


if __name__ == "__main__":
    # Get movie name from user input
    movie_name = console.input("\n[bold cyan]Enter movie name to search: [/bold cyan]").strip()
    
    if movie_name:
        display_movie_embeddings(movie_name)
    else:
        console.print("[bold red]Error: Please enter a valid movie name.[/bold red]")