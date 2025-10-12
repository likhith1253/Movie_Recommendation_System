"""
Quick test script to verify the system is working correctly.
"""

import sys
from rich.console import Console

console = Console()

def test_imports():
    """Test that all modules can be imported."""
    console.print("[bold cyan]Testing imports...[/bold cyan]")
    try:
        import config
        import database
        import operations
        import admin
        console.print("[green][OK] All modules imported successfully[/green]")
        return True
    except Exception as e:
        console.print(f"[red][FAIL] Import error: {e}[/red]")
        return False

def test_database_connection():
    """Test database connection."""
    console.print("\n[bold cyan]Testing database connection...[/bold cyan]")
    try:
        import database
        collection = database.connect_to_collection()
        count = database.get_collection_count(collection)
        console.print(f"[green]✓ Connected to database successfully[/green]")
        console.print(f"[dim]  Database contains {count:,} movies[/dim]")
        return True, collection
    except Exception as e:
        console.print(f"[red]✗ Database connection error: {e}[/red]")
        return False, None

def test_query_functionality(collection):
    """Test basic query functionality."""
    console.print("\n[bold cyan]Testing query functionality...[/bold cyan]")
    try:
        import database
        results = database.query_movies(collection, "action movie", n_results=3)
        if results['ids'][0]:
            console.print(f"[green]✓ Query executed successfully[/green]")
            console.print(f"[dim]  Found {len(results['ids'][0])} results[/dim]")
            return True
        else:
            console.print("[yellow]⚠ Query returned no results[/yellow]")
            return False
    except Exception as e:
        console.print(f"[red]✗ Query error: {e}[/red]")
        return False

def test_genre_distribution(collection):
    """Test genre distribution analysis."""
    console.print("\n[bold cyan]Testing genre distribution...[/bold cyan]")
    try:
        import database
        genres = database.get_genre_distribution(collection)
        top_5 = dict(list(genres.items())[:5])
        console.print(f"[green]✓ Genre analysis successful[/green]")
        console.print(f"[dim]  Top 5 genres: {', '.join(top_5.keys())}[/dim]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Genre analysis error: {e}[/red]")
        return False

def test_director_search(collection):
    """Test director search functionality."""
    console.print("\n[bold cyan]Testing director search...[/bold cyan]")
    try:
        import database
        # Try to find movies by a common director
        directors = database.find_movies_by_director(collection, "Christopher Nolan")
        if directors:
            console.print(f"[green]✓ Director search successful[/green]")
            console.print(f"[dim]  Found {len(directors)} movies[/dim]")
        else:
            console.print("[yellow]⚠ No movies found for test director[/yellow]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Director search error: {e}[/red]")
        return False

def main():
    """Run all tests."""
    console.print("\n[bold magenta]========================================[/bold magenta]")
    console.print("[bold magenta]  Movie Recommendation System Tests  [/bold magenta]")
    console.print("[bold magenta]========================================[/bold magenta]\n")
    
    tests_passed = 0
    tests_total = 5
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Database connection
    success, collection = test_database_connection()
    if success:
        tests_passed += 1
    else:
        console.print("\n[red]Cannot continue tests without database connection[/red]")
        sys.exit(1)
    
    # Test 3: Query functionality
    if test_query_functionality(collection):
        tests_passed += 1
    
    # Test 4: Genre distribution
    if test_genre_distribution(collection):
        tests_passed += 1
    
    # Test 5: Director search
    if test_director_search(collection):
        tests_passed += 1
    
    # Summary
    console.print("\n[bold magenta]========================================[/bold magenta]")
    console.print(f"[bold]Test Results: {tests_passed}/{tests_total} passed[/bold]")
    
    if tests_passed == tests_total:
        console.print("[bold green]All tests passed! System is ready to use.[/bold green]")
        console.print("\n[cyan]Run 'python main.py' to start the application[/cyan]")
    else:
        console.print(f"[bold yellow]{tests_total - tests_passed} test(s) failed[/bold yellow]")
    
    console.print("[bold magenta]========================================[/bold magenta]\n")

if __name__ == "__main__":
    main()
