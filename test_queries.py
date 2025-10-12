"""
Test script for demonstrating complex ChromaDB queries.
Shows advanced filtering with $and, $or, and nested logical operators.
"""

from rich.console import Console
from rich.panel import Panel
from rich import box
from database import connect_to_collection

console = Console()


def run_test_query(query_text, where_clause=None, n_results=5):
    """
    Executes a test query with semantic search and metadata filters.
    
    Args:
        query_text: Semantic search query string.
        where_clause: ChromaDB where filter dictionary (optional).
        n_results: Number of results to return (default: 5).
    """
    try:
        # Connect to database
        collection = connect_to_collection()
        
        # Execute query
        console.print(f"\n[bold yellow]Query:[/bold yellow] [cyan]{query_text}[/cyan]")
        if where_clause:
            console.print(f"[bold yellow]Filter:[/bold yellow] [dim]{where_clause}[/dim]")
        
        with console.status("[bold green]Searching...", spinner="dots"):
            if where_clause:
                results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where_clause
                )
            else:
                results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results
                )
        
        # Display results
        if not results['ids'][0]:
            console.print("[yellow]No movies found matching the criteria.[/yellow]")
            return
        
        console.print(f"\n[bold green]Found {len(results['ids'][0])} movies:[/bold green]\n")
        
        for i, movie_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i]
            title = metadata.get('title', 'Unknown')
            rating = metadata.get('vote_average', 0.0)
            runtime = metadata.get('runtime', 0)
            director = metadata.get('director', 'Unknown')
            
            console.print(
                f"  - [cyan]{title}[/cyan] "
                f"(Rating: {rating}, Runtime: {runtime} mins, Director: {director})"
            )
        
    except Exception as e:
        console.print(f"[red]Error executing query: {e}[/red]")


if __name__ == "__main__":
    """
    Main execution block - provides examples and allows manual testing.
    """
    console.print("\n[bold cyan]================================================================[/bold cyan]")
    console.print("[bold cyan]     ChromaDB Complex Query Testing Suite                      [/bold cyan]")
    console.print("[bold cyan]================================================================[/bold cyan]\n")
    
    # Display usage instructions
    usage_panel = Panel(
        "[bold yellow]How to Use:[/bold yellow]\n\n"
        "This script provides the run_test_query() function for testing complex queries.\n\n"
        "[bold cyan]Function Signature:[/bold cyan]\n"
        "  run_test_query(query_text, where_clause=None, n_results=5)\n\n"
        "[bold green]Example Usage:[/bold green]\n\n"
        "# Simple semantic search\n"
        "run_test_query('action movie with explosions')\n\n"
        "# With filters\n"
        "run_test_query(\n"
        "    'charming story',\n"
        "    where_clause={'$and': [{'vote_average': {'$gte': 8.0}}, {'runtime': {'$lte': 100}}]}\n"
        ")\n\n"
        "[bold yellow]Supported Operators:[/bold yellow]\n"
        "$and, $or, $gte, $lte, $gt, $lt, $eq, $ne",
        title="[bold cyan]Query Testing Tool[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED
    )
    console.print(usage_panel)
    
    # Show example queries
    console.print("\n[bold magenta]Example Query Templates:[/bold magenta]\n")
    
    examples = [
        {
            "title": "Query 1: Highly-rated short films",
            "code": "run_test_query(\n"
                   "    'charming and beautiful story',\n"
                   "    where_clause={'$and': [{'vote_average': {'$gte': 8.0}}, {'runtime': {'$lte': 100}}]},\n"
                   "    n_results=10\n"
                   ")"
        },
        {
            "title": "Query 2: Epic blockbusters (long runtime)",
            "code": "run_test_query(\n"
                   "    'epic adventure blockbuster',\n"
                   "    where_clause={'runtime': {'$gte': 120}},\n"
                   "    n_results=10\n"
                   ")"
        },
        {
            "title": "Query 3: Recent critically acclaimed films",
            "code": "run_test_query(\n"
                   "    'intense thriller',\n"
                   "    where_clause={'$and': [{'vote_average': {'$gte': 7.5}}, {'runtime': {'$gte': 90}}]},\n"
                   "    n_results=10\n"
                   ")"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        console.print(f"[bold cyan]{i}. {example['title']}[/bold cyan]")
        console.print(f"[dim]{example['code']}[/dim]\n")
    
    console.print("\n[bold yellow]Type your queries below in the Python interpreter or modify this script![/bold yellow]\n")
    console.print("[dim]Tip: Run 'python -i test_queries.py' for interactive mode[/dim]\n")
