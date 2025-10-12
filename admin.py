"""
Admin panel functions for database management and insights.
Contains CRUD operations and database analytics.
"""

import uuid
from typing import Dict, Any, Optional
from chromadb.api.models.Collection import Collection
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress

import database
from config import TOP_GENRES_COUNT, BENCHMARK_ITERATIONS, INDEXING_INFO
import operations

console = Console()


def create_movie(collection: Collection, movie_data: Dict[str, Any]) -> None:
    """
    Creates a new movie in the database.
    
    Args:
        collection: ChromaDB collection object.
        movie_data: Dictionary containing movie information.
    """
    try:
        movie_id = movie_data.get('id', str(uuid.uuid4()))
        
        # Create document for embedding
        document = f"Title: {movie_data['title']}. Overview: {movie_data['overview']}. " \
                   f"Genres: {movie_data['genres']}. Director: {movie_data.get('director', 'Unknown')}."
        
        # Create metadata
        metadata = {
            'title': movie_data['title'],
            'overview': movie_data['overview'],
            'genres': movie_data['genres'],
            'release_date': movie_data.get('release_date', 'N/A'),
            'vote_average': float(movie_data.get('vote_average', 0.0)),
            'runtime': int(movie_data.get('runtime', 0)),
            'director': movie_data.get('director', 'Unknown'),
            'id': movie_id
        }
        
        with console.status("[bold green]Adding movie to database...", spinner="dots"):
            database.add_movie(collection, movie_id, document, metadata)
        
        console.print(f"\n[bold green]✓[/bold green] Movie '[cyan]{movie_data['title']}[/cyan]' added successfully!")
        console.print(f"[dim]Movie ID: {movie_id}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error creating movie: {e}[/red]")


def read_movie(collection: Collection, movie_id: str) -> None:
    """
    Reads and displays a movie's details by ID.
    
    Args:
        collection: ChromaDB collection object.
        movie_id: Movie ID to fetch.
    """
    try:
        with console.status(f"[bold green]Fetching movie with ID '{movie_id}'...", spinner="dots"):
            movie = database.get_movie_by_id(collection, movie_id)
        
        if not movie:
            console.print(f"[yellow]Movie with ID '{movie_id}' not found.[/yellow]")
            return
        
        console.print(f"\n[bold green]✓[/bold green] Movie found!\n")
        operations.display_movie_details(movie)
        
    except Exception as e:
        console.print(f"[red]Error reading movie: {e}[/red]")


def update_movie(collection: Collection, movie_id: str, updates: Dict[str, Any]) -> None:
    """
    Updates a movie's information.
    
    Args:
        collection: ChromaDB collection object.
        movie_id: Movie ID to update.
        updates: Dictionary of fields to update.
    """
    try:
        # Fetch existing movie
        with console.status(f"[bold green]Fetching movie...", spinner="dots"):
            movie = database.get_movie_by_id(collection, movie_id)
        
        if not movie:
            console.print(f"[yellow]Movie with ID '{movie_id}' not found.[/yellow]")
            return
        
        # Update metadata
        metadata = movie['metadata'].copy()
        for key, value in updates.items():
            if key in metadata:
                metadata[key] = value
        
        # Recreate document if relevant fields changed
        document = movie['document']
        if any(key in updates for key in ['title', 'overview', 'genres', 'director']):
            document = f"Title: {metadata['title']}. Overview: {metadata['overview']}. " \
                      f"Genres: {metadata['genres']}. Director: {metadata.get('director', 'Unknown')}."
        
        with console.status("[bold green]Updating movie...", spinner="dots"):
            database.update_movie(collection, movie_id, document, metadata)
        
        console.print(f"\n[bold green]✓[/bold green] Movie '[cyan]{metadata['title']}[/cyan]' updated successfully!")
        
    except Exception as e:
        console.print(f"[red]Error updating movie: {e}[/red]")


def delete_movie(collection: Collection, movie_id: str) -> None:
    """
    Deletes a movie from the database.
    
    Args:
        collection: ChromaDB collection object.
        movie_id: Movie ID to delete.
    """
    try:
        # Fetch movie first to show what's being deleted
        movie = database.get_movie_by_id(collection, movie_id)
        
        if not movie:
            console.print(f"[yellow]Movie with ID '{movie_id}' not found.[/yellow]")
            return
        
        title = movie['metadata'].get('title', 'Unknown')
        
        with console.status(f"[bold red]Deleting movie '{title}'...", spinner="dots"):
            database.delete_movie(collection, movie_id)
        
        console.print(f"\n[bold green]✓[/bold green] Movie '[cyan]{title}[/cyan]' deleted successfully!")
        
    except Exception as e:
        console.print(f"[red]Error deleting movie: {e}[/red]")


def show_database_insights(collection: Collection) -> None:
    """
    Displays database insights including count and genre distribution.
    
    Args:
        collection: ChromaDB collection object.
    """
    try:
        console.print("\n[bold cyan]═══ Database Insights ═══[/bold cyan]\n")
        
        # Get total count
        with console.status("[bold green]Analyzing database...", spinner="dots"):
            count = database.get_collection_count(collection)
            genre_dist = database.get_genre_distribution(collection)
        
        console.print(f"[bold]Total Movies:[/bold] [green]{count:,}[/green]")
        
        # Display top genres
        console.print(f"\n[bold]Top {TOP_GENRES_COUNT} Genres:[/bold]\n")
        
        top_genres = dict(list(genre_dist.items())[:TOP_GENRES_COUNT])
        
        # Create a simple bar chart
        max_count = max(top_genres.values()) if top_genres else 1
        
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Genre", style="cyan", width=20)
        table.add_column("Count", justify="right", style="green", width=10)
        table.add_column("Bar", style="yellow", width=40)
        
        for genre, count in top_genres.items():
            bar_length = int((count / max_count) * 30)
            bar = "█" * bar_length
            table.add_row(genre, str(count), bar)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error showing insights: {e}[/red]")


def benchmark_queries(collection: Collection) -> None:
    """
    Runs a benchmark on query performance and displays indexing information.
    
    Args:
        collection: ChromaDB collection object.
    """
    try:
        console.print("\n[bold cyan]═══ Query Performance Benchmark ═══[/bold cyan]\n")
        
        # Sample query
        query_text = "action movie with explosions"
        
        console.print(f"[bold]Running benchmark:[/bold] {BENCHMARK_ITERATIONS} iterations")
        console.print(f"[bold]Query:[/bold] [cyan]'{query_text}'[/cyan]\n")
        
        # Run benchmark with progress bar
        with Progress() as progress:
            task = progress.add_task("[green]Benchmarking...", total=BENCHMARK_ITERATIONS)
            
            stats = database.benchmark_query(
                collection,
                query_text,
                n_results=10,
                iterations=BENCHMARK_ITERATIONS
            )
            
            progress.update(task, completed=BENCHMARK_ITERATIONS)
        
        # Display results
        results_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        results_table.add_column("Metric", style="cyan", width=20)
        results_table.add_column("Value", style="green", justify="right", width=20)
        
        results_table.add_row("Average Time", f"{stats['average']*1000:.2f} ms")
        results_table.add_row("Min Time", f"{stats['min']*1000:.2f} ms")
        results_table.add_row("Max Time", f"{stats['max']*1000:.2f} ms")
        results_table.add_row("Total Time", f"{stats['total']:.2f} s")
        
        console.print(results_table)
        
        # Display indexing information
        console.print("\n" + "="*80 + "\n")
        console.print(INDEXING_INFO)
        
    except Exception as e:
        console.print(f"[red]Error running benchmark: {e}[/red]")


def peek_database(collection: Collection, limit: int = 5) -> None:
    """
    Peeks at the first N records in the database.
    
    Args:
        collection: ChromaDB collection object.
        limit: Number of records to peek at.
    """
    try:
        with console.status(f"[bold green]Peeking at first {limit} records...", spinner="dots"):
            results = database.peek_collection(collection, limit=limit)
        
        console.print(f"\n[bold green]✓[/bold green] First {limit} records:\n")
        
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Title", style="cyan", width=40)
        table.add_column("Year", style="green", width=10)
        table.add_column("Rating", style="yellow", justify="center", width=8)
        
        for i, movie_id in enumerate(results['ids']):
            metadata = results['metadatas'][i]
            title = metadata.get('title', 'Unknown')
            release_date = metadata.get('release_date', 'N/A')
            year = release_date.split('-')[0] if release_date and release_date != 'N/A' else 'N/A'
            rating = f"{metadata.get('vote_average', 0.0):.1f}"
            
            table.add_row(movie_id, title, year, rating)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error peeking database: {e}[/red]")


def search_by_filters(collection: Collection, filters: Dict[str, Any]) -> None:
    """
    Searches movies using metadata filters only (no semantic search).
    
    Args:
        collection: ChromaDB collection object.
        filters: Dictionary of metadata filters.
    """
    try:
        console.print("\n[bold cyan]Searching with filters...[/bold cyan]\n")
        
        # This is a simplified version - in practice, you'd build complex where clauses
        # For demonstration, we'll get all movies and filter in Python
        with console.status("[bold green]Searching...", spinner="dots"):
            all_movies = database.get_all_movies(collection)
        
        filtered_movies = []
        for i, metadata in enumerate(all_movies['metadatas']):
            match = True
            for key, value in filters.items():
                if key not in metadata or metadata[key] != value:
                    match = False
                    break
            
            if match:
                filtered_movies.append({
                    'id': all_movies['ids'][i],
                    'metadata': metadata
                })
        
        if not filtered_movies:
            console.print("[yellow]No movies found matching the filters.[/yellow]")
            return
        
        console.print(f"[bold green]✓[/bold green] Found {len(filtered_movies)} movies\n")
        operations.display_movie_table(filtered_movies, "Filtered Results")
        
    except Exception as e:
        console.print(f"[red]Error searching with filters: {e}[/red]")
