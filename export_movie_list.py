"""
Utility script to export all movies with their IDs to a text file.
Movies are organized by ID, with the most recently added at the end.

Usage:
    python export_movie_list.py

Output:
    Creates 'movie_list.txt' with all movies and their IDs.
    Each entry includes: ID, Title, Year, Rating, Genres, and Director.
"""

import database
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def export_movies_to_file(output_file: str = "movie_list.txt") -> None:
    """
    Exports all movies with their IDs to a text file.
    
    Args:
        output_file: Name of the output file.
    """
    try:
        console.print("\n[bold cyan]Exporting Movie List[/bold cyan]\n")
        
        # Connect to database
        with console.status("[bold green]Connecting to database...", spinner="dots"):
            collection = database.connect_to_collection()
        
        console.print("[green]✓[/green] Connected to database\n")
        
        # Get all movies
        with console.status("[bold green]Fetching all movies...", spinner="dots"):
            all_movies = database.get_all_movies(collection)
        
        total_movies = len(all_movies['ids'])
        console.print(f"[green]✓[/green] Found {total_movies:,} movies\n")
        
        # Analyze IDs
        integer_ids = []
        non_integer_ids = []
        for movie_id in all_movies['ids']:
            try:
                integer_ids.append(int(movie_id))
            except ValueError:
                non_integer_ids.append(movie_id)
        
        # Write to file
        with console.status(f"[bold green]Writing to {output_file}...", spinner="dots"):
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("MOVIE LIST - ORGANIZED BY ID\n")
                f.write("=" * 80 + "\n")
                f.write(f"Total Movies: {total_movies:,}\n")
                f.write(f"Integer IDs: {len(integer_ids):,} (Range: 0-{max(integer_ids) if integer_ids else 0})\n")
                f.write(f"Non-Integer IDs: {len(non_integer_ids)}\n")
                f.write("=" * 80 + "\n")
                f.write("NOTE: Serial numbers [#] are just list positions (1-based).\n")
                f.write("      Actual movie IDs are shown after 'ID:' field.\n")
                f.write("=" * 80 + "\n\n")
                
                for i, movie_id in enumerate(all_movies['ids'], 1):
                    metadata = all_movies['metadatas'][i-1]
                    
                    title = metadata.get('title', 'Unknown')
                    year = metadata.get('release_date', 'N/A').split('-')[0] if metadata.get('release_date') else 'N/A'
                    rating = metadata.get('vote_average', 0.0)
                    genres = metadata.get('genres', 'N/A')
                    director = metadata.get('director', 'Unknown')
                    
                    f.write(f"[{i}] ID: {movie_id}\n")
                    f.write(f"    Title: {title} ({year})\n")
                    f.write(f"    Rating: {rating}\n")
                    f.write(f"    Genres: {genres}\n")
                    f.write(f"    Director: {director}\n")
                    f.write("-" * 80 + "\n\n")
        
        console.print(f"[bold green]✓ Successfully exported to '{output_file}'![/bold green]\n")
        console.print(f"[dim]Total movies: {total_movies:,}[/dim]")
        console.print(f"[dim]Most recently added movie is at the end of the file.[/dim]\n")
        
    except Exception as e:
        console.print(f"[red]Error exporting movies: {e}[/red]")


if __name__ == "__main__":
    export_movies_to_file()
