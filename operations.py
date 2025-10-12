"""
User-facing operations for the movie recommendation system.
Contains functions for recommendations, search, and exploration.
"""

from typing import List, Dict, Any, Optional
from chromadb.api.models.Collection import Collection
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

import database
from config import DEFAULT_RESULTS, MAX_SEARCH_RESULTS

console = Console()


def display_movie_table(movies: List[Dict[str, Any]], title: str = "Movies") -> None:
    """
    Displays a list of movies in a formatted table.
    
    Args:
        movies: List of movie dictionaries with metadata.
        title: Title for the table.
    """
    if not movies:
        console.print("[yellow]No movies found.[/yellow]")
        return
    
    table = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Title", style="cyan", no_wrap=False, width=30)
    table.add_column("Year", style="green", width=10)
    table.add_column("Rating", style="yellow", justify="center", width=8)
    table.add_column("Runtime", style="blue", justify="center", width=10)
    table.add_column("Genres", style="magenta", no_wrap=False, width=25)
    
    for movie in movies:
        metadata = movie.get('metadata', {})
        title_text = metadata.get('title', 'Unknown')
        
        # Extract year from release_date
        release_date = metadata.get('release_date', 'N/A')
        year = release_date.split('-')[0] if release_date and release_date != 'N/A' else 'N/A'
        
        rating = f"{metadata.get('vote_average', 0.0):.1f}"
        runtime = f"{metadata.get('runtime', 0)} min"
        genres = metadata.get('genres', 'N/A')
        
        # Truncate genres if too long
        if len(genres) > 25:
            genres = genres[:22] + "..."
        
        table.add_row(title_text, year, rating, runtime, genres)
    
    console.print(table)


def display_movie_details(movie: Dict[str, Any]) -> None:
    """
    Displays detailed information about a single movie.
    
    Args:
        movie: Movie dictionary with metadata and document.
    """
    metadata = movie.get('metadata', {})
    document = movie.get('document', 'No overview available.')
    
    title = metadata.get('title', 'Unknown Title')
    
    details = f"""
[bold cyan]Title:[/bold cyan] {title}
[bold green]Release Date:[/bold green] {metadata.get('release_date', 'N/A')}
[bold yellow]Rating:[/bold yellow] {metadata.get('vote_average', 0.0)}/10
[bold blue]Runtime:[/bold blue] {metadata.get('runtime', 0)} minutes
[bold magenta]Genres:[/bold magenta] {metadata.get('genres', 'N/A')}
[bold red]Director:[/bold red] {metadata.get('director', 'Unknown')}

[bold white]Overview:[/bold white]
{metadata.get('overview', 'No overview available.')}
    """
    
    panel = Panel(details.strip(), title=f"[bold]{title}[/bold]", border_style="cyan", box=box.DOUBLE)
    console.print(panel)


def get_recommendations(collection: Collection, movie_title: str, n_results: int = DEFAULT_RESULTS) -> None:
    """
    Gets and displays movie recommendations based on a title.
    
    Args:
        collection: ChromaDB collection object.
        movie_title: Title of the movie to base recommendations on.
        n_results: Number of recommendations to return.
    """
    try:
        # First, find the exact movie to get its full document
        with console.status(f"[bold green]Finding '{movie_title}'...", spinner="dots"):
            exact_match = collection.get(
                where={"title": {"$eq": movie_title}},
                include=["documents", "metadatas"],
                limit=1
            )
        
        # If exact match not found, try case-insensitive search
        if not exact_match['ids']:
            # Try with query to find closest match
            temp_results = database.query_movies(collection, movie_title, 1)
            if not temp_results['ids'][0]:
                console.print(f"[yellow]Movie '{movie_title}' not found.[/yellow]")
                return
            
            # Use the closest match
            movie_id = temp_results['ids'][0][0]
            exact_match = collection.get(
                ids=[movie_id],
                include=["documents", "metadatas"]
            )
        
        # Now query using the full document for better semantic matching
        movie_document = exact_match['documents'][0]
        movie_metadata = exact_match['metadatas'][0]
        
        with console.status(f"[bold green]Finding recommendations for '{movie_metadata.get('title', movie_title)}'...", spinner="dots"):
            results = collection.query(
                query_texts=[movie_document],
                n_results=n_results + 1
            )
        
        if not results['ids'][0]:
            console.print(f"[yellow]No recommendations found for '{movie_title}'.[/yellow]")
            return
        
        # Prepare movie list
        movies = []
        for i, movie_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            
            # Convert distance to similarity percentage
            # For cosine distance: 0 = identical, 2 = opposite
            # For L2 distance: use exponential decay
            # We'll handle both cases
            if distance <= 2.0:
                # Likely cosine distance
                similarity = (1 - distance / 2)
            else:
                # Likely L2 distance, use exponential decay
                import math
                similarity = math.exp(-distance / 2)
            
            # Skip the queried movie itself (should be the first result)
            if movie_id == exact_match['ids'][0]:
                continue
            
            movies.append({
                'id': movie_id,
                'metadata': metadata,
                'similarity': similarity,
                'distance': distance
            })
        
        # Limit to requested number
        movies = movies[:n_results]
        
        console.print(f"\n[bold green]✓[/bold green] Found {len(movies)} recommendations for [cyan]'{movie_title}'[/cyan]\n")
        display_movie_table(movies, f"Recommendations for '{movie_title}'")
        
        # Show similarity scores
        console.print("\n[bold]Similarity Scores:[/bold]")
        for i, movie in enumerate(movies, 1):
            title = movie['metadata'].get('title', 'Unknown')
            score = movie['similarity']
            console.print(f"  {i}. [cyan]{title}[/cyan]: [yellow]{score:.2%}[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error getting recommendations: {e}[/red]")


def advanced_search(
    collection: Collection,
    query_text: str,
    year_filter: Optional[str] = None,
    rating_filter: Optional[float] = None,
    runtime_filter: Optional[int] = None
) -> None:
    """
    Performs an advanced search with semantic query and metadata filters.
    
    Args:
        collection: ChromaDB collection object.
        query_text: Semantic search query.
        year_filter: Year filter (e.g., "after 2000", "before 1990").
        rating_filter: Minimum rating filter.
        runtime_filter: Maximum runtime filter in minutes.
    """
    try:
        # Build the where clause
        where_conditions = []
        
        if year_filter:
            if "after" in year_filter.lower():
                year = int(year_filter.lower().replace("after", "").strip())
                where_conditions.append({"release_date": {"$gte": f"{year}-01-01"}})
            elif "before" in year_filter.lower():
                year = int(year_filter.lower().replace("before", "").strip())
                where_conditions.append({"release_date": {"$lte": f"{year}-12-31"}})
        
        if rating_filter is not None:
            where_conditions.append({"vote_average": {"$gte": rating_filter}})
        
        if runtime_filter is not None:
            where_conditions.append({"runtime": {"$lte": runtime_filter}})
        
        # Construct the final where clause
        where_clause = None
        if where_conditions:
            if len(where_conditions) == 1:
                where_clause = where_conditions[0]
            else:
                where_clause = {"$and": where_conditions}
        
        with console.status(f"[bold green]Searching for '{query_text}' with filters...", spinner="dots"):
            results = database.query_movies(
                collection,
                query_text,
                n_results=MAX_SEARCH_RESULTS,
                where=where_clause
            )
        
        if not results['ids'][0]:
            console.print("[yellow]No movies found matching your criteria.[/yellow]")
            return
        
        # Prepare movie list
        movies = []
        for i, movie_id in enumerate(results['ids'][0]):
            movies.append({
                'id': movie_id,
                'metadata': results['metadatas'][0][i]
            })
        
        console.print(f"\n[bold green]✓[/bold green] Found {len(movies)} movies matching your search\n")
        
        # Display filters applied
        filters_text = f"[bold]Query:[/bold] [cyan]{query_text}[/cyan]"
        if year_filter:
            filters_text += f"\n[bold]Year:[/bold] {year_filter}"
        if rating_filter:
            filters_text += f"\n[bold]Min Rating:[/bold] {rating_filter}"
        if runtime_filter:
            filters_text += f"\n[bold]Max Runtime:[/bold] {runtime_filter} minutes"
        
        console.print(Panel(filters_text, title="Search Filters", border_style="green"))
        console.print()
        
        display_movie_table(movies, "Search Results")
        
    except Exception as e:
        console.print(f"[red]Error performing advanced search: {e}[/red]")


def find_movies_by_genre(collection: Collection, genre: str) -> None:
    """
    Finds and displays movies by genre.
    
    Args:
        collection: ChromaDB collection object.
        genre: Genre to search for.
    """
    try:
        with console.status(f"[bold green]Finding movies in '{genre}' genre...", spinner="dots"):
            all_movies = database.get_all_movies(collection)
        
        found_movies = []
        for i, metadata in enumerate(all_movies['metadatas']):
            movie_genres = metadata.get('genres', '')
            if genre.lower() in movie_genres.lower():
                found_movies.append({
                    'id': all_movies['ids'][i],
                    'metadata': metadata
                })
        
        if not found_movies:
            console.print(f"[yellow]No movies found in the '{genre}' genre.[/yellow]")
            return
        
        console.print(f"\n[bold green]✓[/bold green] Found {len(found_movies)} movies in the [cyan]'{genre}'[/cyan] genre\n")
        display_movie_table(found_movies, f"Movies in '{genre}' Genre")
        
    except Exception as e:
        console.print(f"[red]Error finding movies by genre: {e}[/red]")


def explore_by_director(collection: Collection, movie_title: str) -> None:
    """
    Finds all movies by the same director as the given movie.
    This demonstrates a "join-like" operation.
    
    Args:
        collection: ChromaDB collection object.
        movie_title: Title of the movie to find the director from.
    """
    try:
        # First query: Find the movie and get its director
        with console.status(f"[bold green]Finding director of '{movie_title}'...", spinner="dots"):
            results = database.query_movies(collection, movie_title, n_results=1)
        
        if not results['ids'][0]:
            console.print(f"[yellow]Movie '{movie_title}' not found.[/yellow]")
            return
        
        movie_metadata = results['metadatas'][0][0]
        director = movie_metadata.get('director', 'Unknown')
        
        if director == 'Unknown':
            console.print(f"[yellow]Director information not available for '{movie_title}'.[/yellow]")
            return
        
        console.print(f"\n[bold cyan]Director:[/bold cyan] {director}")
        
        # Second query: Find all movies by this director
        with console.status(f"[bold green]Finding all movies by {director}...", spinner="dots"):
            director_movies = database.find_movies_by_director(collection, director)
        
        if not director_movies:
            console.print(f"[yellow]No other movies found by {director}.[/yellow]")
            return
        
        console.print(f"\n[bold green]✓[/bold green] Found {len(director_movies)} movies directed by [cyan]{director}[/cyan]\n")
        display_movie_table(director_movies, f"Movies by {director}")
        
    except Exception as e:
        console.print(f"[red]Error exploring by director: {e}[/red]")


def list_sample_movies(collection: Collection, limit: int = 20) -> None:
    """
    Lists a sample of movies from the database.
    
    Args:
        collection: ChromaDB collection object.
        limit: Number of movies to display.
    """
    try:
        with console.status(f"[bold green]Fetching {limit} movies...", spinner="dots"):
            results = database.get_all_movies(collection, limit=limit)
        
        movies = []
        for i, movie_id in enumerate(results['ids']):
            movies.append({
                'id': movie_id,
                'metadata': results['metadatas'][i]
            })
        
        console.print(f"\n[bold green]✓[/bold green] Displaying {len(movies)} movies from the database\n")
        display_movie_table(movies, f"Sample of {limit} Movies")
        
    except Exception as e:
        console.print(f"[red]Error listing movies: {e}[/red]")
