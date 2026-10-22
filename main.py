"""
Main entry point for the Movie Recommendation System.
Provides an interactive terminal interface using rich and questionary.
"""

import sys
import questionary
from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.text import Text

import database
import operations
import admin
from config import ADMIN_PASSWORD

console = Console()


def display_welcome() -> None:
    """Displays the welcome banner."""
    welcome_text = Text()
    welcome_text.append("🎬 ", style="bold red")
    welcome_text.append("Movie Recommendation System", style="bold cyan")
    welcome_text.append(" 🎬", style="bold red")
    
    subtitle = "Powered by ChromaDB & AI Embeddings"
    
    panel = Panel(
        f"{welcome_text}\n\n{subtitle}",
        box=box.DOUBLE,
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)


def main_menu(collection) -> None:
    """
    Displays the main menu and handles user interactions.
    
    Args:
        collection: ChromaDB collection object.
    """
    while True:
        console.print()
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "🎯 Get Movie Recommendations",
                "🔍 Advanced Search",
                "🎭 Find Movies by Genre",
                "🎬 Explore by Director",
                "📋 List Sample Movies",
                "⚙️  Admin Panel",
                "❌ Exit"
            ],
            style=questionary.Style([
                ('selected', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
                ('question', 'fg:yellow bold')
            ])
        ).ask()
        
        if not choice or choice == "❌ Exit":
            console.print("\n[bold cyan]Thank you for using the Movie Recommendation System! 🎬[/bold cyan]")
            break
        
        elif choice == "🎯 Get Movie Recommendations":
            get_recommendations_flow(collection)
        
        elif choice == "🔍 Advanced Search":
            advanced_search_flow(collection)
        
        elif choice == "🎭 Find Movies by Genre":
            find_by_genre_flow(collection)
        
        elif choice == "🎬 Explore by Director":
            explore_by_director_flow(collection)
        
        elif choice == "📋 List Sample Movies":
            list_movies_flow(collection)
        
        elif choice == "⚙️  Admin Panel":
            admin_panel_flow(collection)


def get_recommendations_flow(collection) -> None:
    """Flow for getting movie recommendations."""
    console.print()
    movie_title = questionary.text(
        "Enter a movie title:",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    if not movie_title:
        console.print("[yellow]Movie title cannot be empty.[/yellow]")
        return
    
    n_results = questionary.text(
        "How many recommendations? (default: 6)",
        default="6",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    try:
        n_results = int(n_results) if n_results else 6
    except ValueError:
        n_results = 6
    
    operations.get_recommendations(collection, movie_title, n_results)


def advanced_search_flow(collection) -> None:
    """Flow for advanced search with filters."""
    console.print()
    console.print("[bold cyan]Advanced Search[/bold cyan]")
    console.print("[dim]Combine semantic search with metadata filters[/dim]\n")
    
    # Get search query
    query_text = questionary.text(
        "Enter your search query (e.g., 'a movie about space exploration'):",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    if not query_text:
        console.print("[yellow]Search query cannot be empty.[/yellow]")
        return
    
    # Ask if user wants to add filters
    add_filters = questionary.confirm(
        "Do you want to add filters?",
        default=False,
        style=questionary.Style([('question', 'fg:yellow bold')])
    ).ask()
    
    year_filter = None
    rating_filter = None
    runtime_filter = None
    
    if add_filters:
        # Year filter
        year_choice = questionary.select(
            "Filter by release year?",
            choices=["No filter", "After a year", "Before a year"],
            style=questionary.Style([('selected', 'fg:cyan bold')])
        ).ask()
        
        if year_choice == "After a year":
            year = questionary.text(
                "Enter year (e.g., 2000):",
                style=questionary.Style([('question', 'fg:cyan bold')])
            ).ask()
            if year:
                year_filter = f"after {year}"
        
        elif year_choice == "Before a year":
            year = questionary.text(
                "Enter year (e.g., 1990):",
                style=questionary.Style([('question', 'fg:cyan bold')])
            ).ask()
            if year:
                year_filter = f"before {year}"
        
        # Rating filter
        rating = questionary.text(
            "Minimum rating (0-10, leave empty for no filter):",
            style=questionary.Style([('question', 'fg:cyan bold')])
        ).ask()
        
        if rating:
            try:
                rating_filter = float(rating)
            except ValueError:
                console.print("[yellow]Invalid rating, skipping filter.[/yellow]")
        
        # Runtime filter
        runtime = questionary.text(
            "Maximum runtime in minutes (leave empty for no filter):",
            style=questionary.Style([('question', 'fg:cyan bold')])
        ).ask()
        
        if runtime:
            try:
                runtime_filter = int(runtime)
            except ValueError:
                console.print("[yellow]Invalid runtime, skipping filter.[/yellow]")
    
    operations.advanced_search(collection, query_text, year_filter, rating_filter, runtime_filter)


def find_by_genre_flow(collection) -> None:
    """Flow for finding movies by genre."""
    console.print()
    
    # Suggest common genres
    common_genres = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller", "Animation"]
    
    genre = questionary.autocomplete(
        "Enter a genre:",
        choices=common_genres,
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    if not genre:
        console.print("[yellow]Genre cannot be empty.[/yellow]")
        return
    
    operations.find_movies_by_genre(collection, genre)


def explore_by_director_flow(collection) -> None:
    """Flow for exploring movies by director (join-like operation)."""
    console.print()
    console.print("[bold cyan]Explore by Director[/bold cyan]")
    console.print("[dim]Find all movies by the same director[/dim]\n")
    
    movie_title = questionary.text(
        "Enter a movie title to find its director:",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    if not movie_title:
        console.print("[yellow]Movie title cannot be empty.[/yellow]")
        return
    
    operations.explore_by_director(collection, movie_title)


def list_movies_flow(collection) -> None:
    """Flow for listing sample movies."""
    console.print()
    
    limit = questionary.text(
        "How many movies to display? (default: 20)",
        default="20",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    try:
        limit = int(limit) if limit else 20
    except ValueError:
        limit = 20
    
    operations.list_sample_movies(collection, limit)


def admin_panel_flow(collection) -> None:
    """Flow for admin panel with password protection."""
    console.print()
    
    password = questionary.password(
        "Enter admin password:",
        style=questionary.Style([('question', 'fg:red bold')])
    ).ask()
    
    if password != ADMIN_PASSWORD:
        console.print("[red]❌ Incorrect password![/red]")
        return
    
    console.print("[green]✓ Access granted![/green]")
    
    while True:
        console.print()
        choice = questionary.select(
            "Admin Panel - Select an option:",
            choices=[
                "➕ Create Movie",
                "📖 Read Movie by ID",
                "✏️  Update Movie",
                "🗑️  Delete Movie",
                "👀 Peek at Database",
                "📊 Database Insights",
                "⚡ Benchmark Queries",
                "🔬 Interactive Indexing Benchmark",
                "🔙 Back to Main Menu"
            ],
            style=questionary.Style([
                ('selected', 'fg:magenta bold'),
                ('pointer', 'fg:magenta bold'),
                ('question', 'fg:red bold')
            ])
        ).ask()
        
        if not choice or choice == "🔙 Back to Main Menu":
            break
        
        elif choice == "➕ Create Movie":
            create_movie_flow(collection)
        
        elif choice == "📖 Read Movie by ID":
            read_movie_flow(collection)
        
        elif choice == "✏️  Update Movie":
            update_movie_flow(collection)
        
        elif choice == "🗑️  Delete Movie":
            delete_movie_flow(collection)
        
        elif choice == "👀 Peek at Database":
            peek_database_flow(collection)
        
        elif choice == "📊 Database Insights":
            admin.show_database_insights(collection)
        
        elif choice == "⚡ Benchmark Queries":
            admin.benchmark_queries(collection)
        
        elif choice == "🔬 Interactive Indexing Benchmark":
            new_collection = admin.interactive_indexing_benchmark()
            if new_collection:
                collection = new_collection
                console.print("[bold green]✓ Collection updated! You can now use the new collection.[/bold green]")


def create_movie_flow(collection) -> None:
    """Flow for creating a new movie."""
    console.print()
    console.print("[bold magenta]Create New Movie[/bold magenta]\n")
    
    title = questionary.text("Movie title:", style=questionary.Style([('question', 'fg:cyan bold')])).ask()
    if not title:
        console.print("[yellow]Title is required.[/yellow]")
        return
    
    overview = questionary.text("Overview:", style=questionary.Style([('question', 'fg:cyan bold')])).ask()
    if not overview:
        console.print("[yellow]Overview is required.[/yellow]")
        return
    
    genres = questionary.text(
        "Genres (comma-separated):",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    if not genres:
        console.print("[yellow]Genres are required.[/yellow]")
        return
    
    release_date = questionary.text(
        "Release date (YYYY-MM-DD):",
        default="2024-01-01",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    vote_average = questionary.text(
        "Vote average (0-10):",
        default="7.0",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    runtime = questionary.text(
        "Runtime (minutes):",
        default="120",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    director = questionary.text(
        "Director:",
        default="Unknown",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    movie_data = {
        'title': title,
        'overview': overview,
        'genres': genres,
        'release_date': release_date,
        'vote_average': float(vote_average) if vote_average else 7.0,
        'runtime': int(runtime) if runtime else 120,
        'director': director if director else "Unknown"
    }
    
    admin.create_movie(collection, movie_data)


def read_movie_flow(collection) -> None:
    """Flow for reading a movie by ID."""
    console.print()
    
    movie_id = questionary.text(
        "Enter movie ID:",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    if not movie_id:
        console.print("[yellow]Movie ID cannot be empty.[/yellow]")
        return
    
    admin.read_movie(collection, movie_id)


def update_movie_flow(collection) -> None:
    """Flow for updating a movie."""
    console.print()
    console.print("[bold magenta]Update Movie[/bold magenta]\n")
    
    movie_name = questionary.text(
        "Enter movie name to search:",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    if not movie_name:
        console.print("[yellow]Movie name cannot be empty.[/yellow]")
        return
    
    # Search for movies by name
    with console.status(f"[bold green]Searching for '{movie_name}'...", spinner="dots"):
        matching_movies = database.search_by_metadata(collection, "title", movie_name, "$eq")
    
    if not matching_movies:
        console.print(f"[yellow]No exact match found for '{movie_name}'. Trying partial match...[/yellow]")
        # Try to find partial matches
        all_movies = database.get_all_movies(collection)
        matching_movies = []
        for i, metadata in enumerate(all_movies['metadatas']):
            title = metadata.get('title', '')
            if movie_name.lower() in title.lower():
                matching_movies.append({
                    'id': all_movies['ids'][i],
                    'metadata': metadata
                })
    
    if not matching_movies:
        console.print(f"[red]No movies found matching '{movie_name}'.[/red]")
        return
    
    # If multiple matches, let user select
    if len(matching_movies) > 1:
        console.print(f"\n[cyan]Found {len(matching_movies)} matching movies:[/cyan]\n")
        choices = []
        for movie in matching_movies:
            title = movie['metadata'].get('title', 'Unknown')
            year = movie['metadata'].get('release_date', 'N/A').split('-')[0] if movie['metadata'].get('release_date') else 'N/A'
            rating = movie['metadata'].get('vote_average', 0.0)
            choices.append(questionary.Choice(
                f"{title} ({year}) - Rating: {rating}",
                value=movie['id']
            ))
        
        movie_id = questionary.select(
            "Select the movie to update:",
            choices=choices,
            style=questionary.Style([
                ('selected', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
                ('question', 'fg:yellow bold')
            ])
        ).ask()
        
        if not movie_id:
            console.print("[yellow]No movie selected.[/yellow]")
            return
    else:
        movie_id = matching_movies[0]['id']
        console.print(f"[green]Found movie: {matching_movies[0]['metadata'].get('title', 'Unknown')}[/green]\n")
    
    # Display the current movie
    admin.read_movie(collection, movie_id)
    
    console.print("\n[dim]Leave fields empty to keep current values[/dim]\n")
    
    updates = {}
    
    title = questionary.text(
        "New title (or press Enter to skip):",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    if title:
        updates['title'] = title
    
    overview = questionary.text(
        "New overview (or press Enter to skip):",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    if overview:
        updates['overview'] = overview
    
    genres = questionary.text(
        "New genres (or press Enter to skip):",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    if genres:
        updates['genres'] = genres
    
    director = questionary.text(
        "New director (or press Enter to skip):",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    if director:
        updates['director'] = director
    
    if not updates:
        console.print("[yellow]No updates provided.[/yellow]")
        return
    
    admin.update_movie(collection, movie_id, updates)


def delete_movie_flow(collection) -> None:
    """Flow for deleting a movie."""
    console.print()
    console.print("[bold red]Delete Movie[/bold red]\n")
    
    movie_id = questionary.text(
        "Enter movie ID to delete:",
        style=questionary.Style([('question', 'fg:red bold')])
    ).ask()
    
    if not movie_id:
        console.print("[yellow]Movie ID cannot be empty.[/yellow]")
        return
    
    # Show the movie first
    admin.read_movie(collection, movie_id)
    
    # Confirm deletion
    confirm = questionary.confirm(
        f"Are you sure you want to delete movie with ID '{movie_id}'?",
        default=False,
        style=questionary.Style([('question', 'fg:red bold')])
    ).ask()
    
    if not confirm:
        console.print("[yellow]Deletion cancelled.[/yellow]")
        return
    
    admin.delete_movie(collection, movie_id)


def peek_database_flow(collection) -> None:
    """Flow for peeking at database records."""
    console.print()
    
    limit = questionary.text(
        "How many records to peek? (default: 5)",
        default="5",
        style=questionary.Style([('question', 'fg:cyan bold')])
    ).ask()
    
    try:
        limit = int(limit) if limit else 5
    except ValueError:
        limit = 5
    
    admin.peek_database(collection, limit)


def main():
    """Main entry point of the application."""
    try:
        display_welcome()
        
        # Connect to database
        with console.status("[bold green]Connecting to database...", spinner="dots"):
            collection = database.connect_to_collection()
            if collection is None:
                raise ConnectionError("Failed to connect to ChromaDB collection (received None).")
        
        console.print("[bold green]✓[/bold green] Connected to ChromaDB successfully!\n")
        
        # Show database info
        count = database.get_collection_count(collection)
        console.print(f"[dim]Database contains {count:,} movies[/dim]")
        

        # Start main menu
        main_menu(collection)

        
    except ConnectionError as e:
        console.print(f"\n[bold red]❌ Database Connection Error:[/bold red]")
        console.print(f"[red]{e}[/red]")
        console.print("\n[yellow]Please ensure the database has been initialized by running:[/yellow]")
        console.print("[cyan]python ingest_data.py[/cyan]")
        sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n\n[bold cyan]Interrupted by user. Goodbye! 🎬[/bold cyan]")
        sys.exit(0)
    
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected Error:[/bold red]")
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
