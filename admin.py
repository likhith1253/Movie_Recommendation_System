"""
Admin panel functions for database management and insights.
Contains CRUD operations and database analytics.
"""

import uuid
import time
import chromadb
import questionary
from typing import Dict, Any, Optional
from chromadb.api.models.Collection import Collection
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

import database
from config import TOP_GENRES_COUNT, BENCHMARK_ITERATIONS, INDEXING_INFO, DB_PATH, COLLECTION_NAME
import operations
import ingest_data

console = Console()


def get_next_movie_id(collection: Collection) -> str:
    """
    Gets the next available integer movie ID.
    
    Args:
        collection: ChromaDB collection object.
        
    Returns:
        Next available movie ID as string.
    """
    try:
        all_movies = database.get_all_movies(collection)
        if not all_movies['ids']:
            return "0"
        
        # Find the highest integer ID
        max_id = -1
        for movie_id in all_movies['ids']:
            try:
                id_int = int(movie_id)
                if id_int > max_id:
                    max_id = id_int
            except ValueError:
                # Skip non-integer IDs (UUIDs)
                continue
        
        return str(max_id + 1)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not determine next ID, using UUID: {e}[/yellow]")
        return str(uuid.uuid4())


def create_movie(collection: Collection, movie_data: Dict[str, Any]) -> None:
    """
    Creates a new movie in the database.
    
    Args:
        collection: ChromaDB collection object.
        movie_data: Dictionary containing movie information.
    """
    try:
        # Get next sequential integer ID if not provided
        movie_id = movie_data.get('id', get_next_movie_id(collection))
        
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


def benchmark_queries(collection: Collection, query_text: Optional[str] = None) -> None:
    """
    Runs a benchmark on query performance and displays indexing information.
    
    Args:
        collection: ChromaDB collection object.
        query_text: Optional query text. If None, user will be prompted.
    """
    try:
        console.print("\n[bold cyan]═══ Query Performance Benchmark ═══[/bold cyan]\n")
        
        # Get query from user if not provided
        if query_text is None:
            query_text = questionary.text(
                "Enter your search query:",
                default="action movie with explosions",
                style=questionary.Style([('question', 'fg:cyan bold')])
            ).ask()
            
            if not query_text:
                console.print("[yellow]Query cannot be empty.[/yellow]")
                return
        
        console.print(f"\n[bold]Running benchmark:[/bold] {BENCHMARK_ITERATIONS} iterations")
        console.print(f"[bold]Query:[/bold] [cyan]'{query_text}'[/cyan]\n")
        
        # First, get sample results to show what the query returns
        console.print("[bold]Sample Results:[/bold]\n")
        with console.status("[bold green]Fetching sample results...", spinner="dots"):
            sample_results = database.query_movies(collection, query_text, n_results=5)
        
        # Display sample results
        if sample_results['ids'] and len(sample_results['ids'][0]) > 0:
            sample_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
            sample_table.add_column("#", style="dim", width=3)
            sample_table.add_column("Title", style="cyan", width=35)
            sample_table.add_column("Year", style="green", width=6)
            sample_table.add_column("Rating", style="yellow", justify="center", width=7)
            sample_table.add_column("Similarity", style="magenta", justify="right", width=10)
            
            for i, movie_id in enumerate(sample_results['ids'][0], 1):
                metadata = sample_results['metadatas'][0][i-1]
                distance = sample_results['distances'][0][i-1] if 'distances' in sample_results else 0
                similarity = f"{(1 - distance) * 100:.1f}%" if 'distances' in sample_results else "N/A"
                
                title = metadata.get('title', 'Unknown')
                year = metadata.get('release_date', 'N/A').split('-')[0] if metadata.get('release_date') else 'N/A'
                rating = f"{metadata.get('vote_average', 0.0):.1f}"
                
                sample_table.add_row(str(i), title, year, rating, similarity)
            
            console.print(sample_table)
        else:
            console.print("[yellow]No results found for this query.[/yellow]")
        
        console.print()
        
        # Run benchmark with progress bar
        with Progress() as progress:
            task = progress.add_task("[green]Benchmarking performance...", total=BENCHMARK_ITERATIONS)
            
            stats = database.benchmark_query(
                collection,
                query_text,
                n_results=10,
                iterations=BENCHMARK_ITERATIONS
            )
            
            progress.update(task, completed=BENCHMARK_ITERATIONS)
        
        # Display performance results
        console.print("\n[bold]Performance Metrics:[/bold]\n")
        results_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        results_table.add_column("Metric", style="cyan", width=20)
        results_table.add_column("Value", style="green", justify="right", width=20)
        
        results_table.add_row("Average Time", f"{stats['average']*1000:.2f} ms")
        results_table.add_row("Min Time", f"{stats['min']*1000:.2f} ms")
        results_table.add_row("Max Time", f"{stats['max']*1000:.2f} ms")
        results_table.add_row("Total Time", f"{stats['total']:.2f} s")
        results_table.add_row("Iterations", str(BENCHMARK_ITERATIONS))
        
        console.print(results_table)
        
        # Performance insights
        console.print("\n[bold]Performance Insights:[/bold]")
        avg_time = stats['average']
        if avg_time < 0.05:
            console.print("  [green]✓[/green] Excellent performance! Queries are very fast.")
        elif avg_time < 0.1:
            console.print("  [green]✓[/green] Good performance. Suitable for real-time applications.")
        elif avg_time < 0.5:
            console.print("  [yellow]✓[/yellow] Acceptable performance for most use cases.")
        else:
            console.print("  [red]⚠[/red] Slower performance. Consider optimizing or reducing dataset size.")
        
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


def interactive_indexing_benchmark() -> Optional[Collection]:
    """
    Interactive indexing and performance demonstration.
    Allows users to recreate the collection with different distance functions
    and benchmark the performance impact.
    
    Returns:
        New collection object if successful, None otherwise.
    """
    try:
        console.print("\n[bold cyan]═══ Interactive Indexing Benchmark ═══[/bold cyan]\n")
        
        # Step 1: Present Configuration Options
        console.print("[bold]Select a distance function for the collection:[/bold]\n")
        
        distance_choice = questionary.select(
            "Distance Function:",
            choices=[
                questionary.Choice("cosine (Cosine Similarity) - Best for semantic search", value="cosine"),
                questionary.Choice("l2 (Euclidean Distance) - Traditional vector distance", value="l2"),
                questionary.Choice("ip (Inner Product) - Dot product similarity", value="ip")
            ],
            style=questionary.Style([
                ('selected', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
                ('question', 'fg:yellow bold')
            ])
        ).ask()
        
        if not distance_choice:
            console.print("[yellow]Operation cancelled.[/yellow]")
            return None
        
        # Display information about the selected distance function
        distance_info = {
            "cosine": "Measures angle between vectors (0-2 range). Best for semantic similarity.",
            "l2": "Measures Euclidean distance between vectors. Traditional metric.",
            "ip": "Measures inner product (dot product). Good for normalized vectors."
        }
        
        console.print(f"\n[bold]Selected:[/bold] [cyan]{distance_choice}[/cyan]")
        console.print(f"[dim]{distance_info[distance_choice]}[/dim]\n")
        
        # Step 2: Warn and Confirm
        warning_text = f"""[bold red]⚠️  WARNING[/bold red]

This will [bold]DELETE[/bold] the existing '[cyan]{COLLECTION_NAME}[/cyan]' collection 
and [bold]RE-INGEST[/bold] all data with the new settings.

[bold yellow]What will happen:[/bold yellow]
  • Current collection will be deleted
  • New collection created with [cyan]{distance_choice}[/cyan] distance function
  • All ~4,800 movies will be re-ingested
  • Process may take [bold]2-5 minutes[/bold]

[bold]Do you want to proceed?[/bold]"""
        
        warning_panel = Panel(
            warning_text,
            title="[bold red]⚠️  Confirmation Required[/bold red]",
            border_style="red",
            box=box.DOUBLE
        )
        
        console.print(warning_panel)
        console.print()
        
        confirm = questionary.confirm(
            "Proceed with collection recreation?",
            default=False,
            style=questionary.Style([('question', 'fg:red bold')])
        ).ask()
        
        if not confirm:
            console.print("\n[yellow]Operation cancelled. No changes made.[/yellow]")
            return None
        
        # Step 3: Recreate and Re-ingest
        console.print("\n[bold green]Starting collection recreation...[/bold green]\n")
        
        # Delete existing collection
        console.print("[bold]Step 1/3:[/bold] Deleting existing collection...")
        try:
            client = chromadb.PersistentClient(path=DB_PATH)
            client.delete_collection(name=COLLECTION_NAME)
            console.print("[green]✓[/green] Collection deleted\n")
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Collection may not exist: {e}\n")
        
        # Create new collection
        console.print(f"[bold]Step 2/3:[/bold] Creating new collection with [cyan]{distance_choice}[/cyan] distance...")
        try:
            new_collection = client.create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": distance_choice}
            )
            console.print(f"[green]✓[/green] Collection created with distance function: [cyan]{distance_choice}[/cyan]\n")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to create collection: {e}")
            return None
        
        # Re-ingest data with progress bar
        console.print("[bold]Step 3/3:[/bold] Re-ingesting movie data...\n")
        
        progress_data = {"current": 0, "message": "Starting..."}
        
        def progress_callback(current, total, message):
            progress_data["current"] = current
            progress_data["message"] = message
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Ingesting data...", total=100)
            
            # Start ingestion in a way that allows progress updates
            success, total_records, error = ingest_data.ingest_data(
                distance_function=distance_choice,
                progress_callback=lambda c, t, m: progress.update(task, completed=c, description=f"[cyan]{m}")
            )
        
        if not success:
            console.print(f"\n[red]✗[/red] Ingestion failed: {error}")
            return None
        
        console.print(f"\n[green]✓[/green] Successfully ingested [bold]{total_records:,}[/bold] movies!\n")
        
        # Step 4: Benchmark and Display Results
        console.print("[bold cyan]═══ Running Performance Benchmark ═══[/bold cyan]\n")
        
        benchmark_query = "Inception"
        iterations = 10
        
        console.print(f"[bold]Benchmark Query:[/bold] Find recommendations for '[cyan]{benchmark_query}[/cyan]'")
        console.print(f"[bold]Iterations:[/bold] {iterations}\n")
        
        # Get the movie document for benchmarking
        inception_data = new_collection.get(
            where={"title": {"$eq": benchmark_query}},
            include=["documents"],
            limit=1
        )
        
        if not inception_data['ids']:
            console.print("[yellow]⚠ Benchmark movie not found, using text query instead[/yellow]\n")
            query_text = benchmark_query
        else:
            query_text = inception_data['documents'][0]
        
        # Run benchmark
        times = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[green]Benchmarking queries...", total=iterations)
            
            for i in range(iterations):
                start_time = time.time()
                new_collection.query(
                    query_texts=[query_text],
                    n_results=10
                )
                end_time = time.time()
                times.append(end_time - start_time)
                progress.update(task, advance=1)
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        # Display results in a formatted table
        console.print("\n[bold green]✓ Benchmark Complete![/bold green]\n")
        
        results_table = Table(
            title="[bold]Performance Results[/bold]",
            show_header=True,
            header_style="bold magenta",
            box=box.DOUBLE,
            border_style="cyan"
        )
        results_table.add_column("Parameter", style="cyan", width=30)
        results_table.add_column("Value", style="green", justify="right", width=30)
        
        results_table.add_row("Distance Function", f"[bold]{distance_choice.upper()}[/bold]")
        results_table.add_row("Total Records", f"{total_records:,} movies")
        results_table.add_row("Average Query Time", f"[bold]{avg_time*1000:.2f} ms[/bold]")
        results_table.add_row("Min Query Time", f"{min_time*1000:.2f} ms")
        results_table.add_row("Max Query Time", f"{max_time*1000:.2f} ms")
        results_table.add_row("Total Benchmark Time", f"{sum(times):.2f} s")
        results_table.add_row("Iterations", f"{iterations}")
        
        console.print(results_table)
        
        # Display additional insights
        console.print("\n[bold]Performance Insights:[/bold]")
        if avg_time < 0.1:
            console.print("  [green]✓[/green] Excellent performance! Queries are very fast.")
        elif avg_time < 0.5:
            console.print("  [yellow]✓[/yellow] Good performance. Acceptable for real-time use.")
        else:
            console.print("  [red]⚠[/red] Slower performance. Consider optimizing or reducing dataset size.")
        
        console.print(f"\n[dim]Note: First query may be slower due to model loading.[/dim]\n")
        
        return new_collection
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user.[/yellow]")
        return None
    except Exception as e:
        console.print(f"\n[red]Error during interactive benchmark: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return None
