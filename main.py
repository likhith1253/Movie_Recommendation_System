import chromadb
import uuid

# ANSI color codes for better terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def connect_to_collection():
    """Connects to the Chroma DB and returns the collection object."""
    try:
        client = chromadb.PersistentClient(path="movie_db")
        collection = client.get_collection(name="movies")
        return collection
    except Exception as e:
        print(f"{Colors.FAIL}Error connecting to Chroma DB: {e}{Colors.ENDC}")
        return None

# --- User-Facing Search and Recommendation Functions ---

def get_recommendations(collection):
    """Gets movie recommendations based on a title."""
    movie_title = input(f"{Colors.OKCYAN}Enter a movie title to get recommendations: {Colors.ENDC}")
    if not movie_title:
        print(f"{Colors.WARNING}Movie title cannot be empty.{Colors.ENDC}")
        return

    results = collection.query(
        query_texts=[movie_title],
        n_results=6,
    )

    print(f"\n{Colors.HEADER}Recommendations for '{movie_title}':{Colors.ENDC}")
    if not results['ids'][0]:
        print(f"{Colors.WARNING}No recommendations found.{Colors.ENDC}")
        return

    for i, (movie_id, distance) in enumerate(zip(results['ids'][0], results['distances'][0])):
        # Skip the queried movie itself if it's the first result
        movie_data = collection.get(ids=[movie_id])
        title = movie_data['metadatas'][0].get('title', 'Unknown Title')
        if i == 0 and title.lower() == movie_title.lower():
            continue
        print(f"  - {Colors.OKGREEN}{title}{Colors.ENDC} (Similarity Score: {1 - distance:.2f})")

def list_all_movies(collection):
    """Lists a sample of all movies in the database."""
    print(f"\n{Colors.HEADER}Listing first 20 movies in the database...{Colors.ENDC}")
    results = collection.get(limit=20)
    for metadata in results['metadatas']:
        print(f"  - {Colors.OKGREEN}{metadata.get('title', 'Unknown Title')}{Colors.ENDC}")

def find_movies_by_genre(collection):
    """Finds movies that contain a specific genre in their metadata."""
    genre = input(f"{Colors.OKCYAN}Enter a genre to search for (e.g., Action, Comedy): {Colors.ENDC}").strip().title()
    if not genre:
        print(f"{Colors.WARNING}Genre cannot be empty.{Colors.ENDC}")
        return

    all_movies = collection.get(include=["metadatas"])
    found_movies = []
    for metadata in all_movies['metadatas']:
        movie_genres = metadata.get('genres', '')
        if genre in [g.strip() for g in movie_genres.split(',')]:
            found_movies.append(metadata.get('title', 'Unknown Title'))

    print(f"\n{Colors.HEADER}Movies in the '{genre}' genre:{Colors.ENDC}")
    if not found_movies:
        print(f"{Colors.WARNING}No movies found for this genre.{Colors.ENDC}")
        return
    for title in sorted(found_movies):
        print(f"  - {Colors.OKGREEN}{title}{Colors.ENDC}")

# --- Admin Menu and Functions ---

def admin_add_movie(collection):
    """(Admin) Adds a new movie to the collection."""
    print(f"\n{Colors.HEADER}Admin: Add a New Movie{Colors.ENDC}")
    title = input(f"{Colors.OKCYAN}Enter movie title: {Colors.ENDC}")
    overview = input(f"{Colors.OKCYAN}Enter movie overview: {Colors.ENDC}")
    genres = input(f"{Colors.OKCYAN}Enter genres (comma-separated): {Colors.ENDC}")
    movie_id = input(f"{Colors.OKCYAN}Enter a unique ID (or press Enter to generate one): {Colors.ENDC}")
    if not movie_id:
        movie_id = str(uuid.uuid4())

    if not all([title, overview, genres]):
        print(f"{Colors.FAIL}Title, Overview, and Genres are required.{Colors.ENDC}")
        return

    try:
        # Using upsert is safer as it will update if the ID exists, or insert if it doesn't.
        collection.upsert(
            ids=[movie_id],
            documents=[overview],
            metadatas=[{"title": title, "genres": genres}]
        )
        print(f"\n{Colors.OKGREEN}Movie '{title}' added/updated successfully with ID: {movie_id}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Error adding movie: {e}{Colors.ENDC}")

def admin_get_movie_count(collection):
    """(Admin) Gets the total number of movies in the collection."""
    count = collection.count()
    print(f"\n{Colors.OKGREEN}The database contains {count} movies.{Colors.ENDC}")

def admin_peek_records(collection):
    """(Admin) Views the first 5 records in the collection."""
    print(f"\n{Colors.HEADER}Admin: Peeking at Top 5 Records{Colors.ENDC}")
    results = collection.peek(limit=5)
    for i, movie_id in enumerate(results['ids']):
        metadata = results['metadatas'][i]
        print(f"  - {Colors.BOLD}ID:{Colors.ENDC} {movie_id}")
        print(f"    {Colors.BOLD}Title:{Colors.ENDC} {metadata.get('title', 'N/A')}")

def admin_get_record_by_id(collection):
    """(Admin) Retrieves and displays a movie's details by its ID."""
    movie_id = input(f"{Colors.OKCYAN}Enter the movie ID to fetch: {Colors.ENDC}")
    if not movie_id:
        print(f"{Colors.WARNING}Movie ID cannot be empty.{Colors.ENDC}")
        return
    result = collection.get(ids=[movie_id], include=["metadatas", "documents"])
    if not result['ids']:
        print(f"{Colors.FAIL}Movie with ID '{movie_id}' not found.{Colors.ENDC}")
        return
    metadata = result['metadatas'][0]
    document = result['documents'][0]
    print(f"\n{Colors.HEADER}Details for Movie ID: {movie_id}{Colors.ENDC}")
    print(f"  {Colors.BOLD}Title:{Colors.ENDC} {metadata.get('title', 'N/A')}")
    print(f"  {Colors.BOLD}Genres:{Colors.ENDC} {metadata.get('genres', 'N/A')}")
    print(f"  {Colors.BOLD}Overview:{Colors.ENDC} {document}")

def admin_delete_by_id(collection):
    """(Admin) Deletes a movie from the collection by its ID."""
    movie_id = input(f"{Colors.OKCYAN}Enter the ID of the movie to delete: {Colors.ENDC}")
    if not movie_id:
        print(f"{Colors.WARNING}Movie ID cannot be empty.{Colors.ENDC}")
        return
    if not collection.get(ids=[movie_id])['ids']:
         print(f"{Colors.FAIL}Movie with ID '{movie_id}' not found.{Colors.ENDC}")
         return
    collection.delete(ids=[movie_id])
    print(f"\n{Colors.OKGREEN}Movie with ID '{movie_id}' has been deleted.{Colors.ENDC}")

def admin_filtered_search(collection):
    """(Admin) Performs a semantic search filtered by genre."""
    print(f"\n{Colors.HEADER}Admin: Filtered Semantic Search{Colors.ENDC}")
    genre = input(f"{Colors.OKCYAN}Enter a genre to filter by (e.g., Action): {Colors.ENDC}").strip().title()
    search_term = input(f"{Colors.OKCYAN}Enter a search term for the overview: {Colors.ENDC}")
    if not all([genre, search_term]):
        print(f"{Colors.FAIL}Genre and search term are required.{Colors.ENDC}")
        return

    results = collection.query(
        query_texts=[search_term],
        n_results=50 # Query a larger number to ensure we find matches after filtering
    )

    print(f"\n{Colors.HEADER}Results for '{search_term}' in genre '{genre}':{Colors.ENDC}")
    found_count = 0
    for i, movie_id in enumerate(results['ids'][0]):
        metadata = results['metadatas'][0][i]
        movie_genres = metadata.get('genres', '')
        if genre in [g.strip() for g in movie_genres.split(',')]:
            found_count += 1
            title = metadata.get('title', 'Unknown Title')
            distance = results['distances'][0][i]
            print(f"  - {Colors.OKGREEN}{title}{Colors.ENDC} (Similarity Score: {1 - distance:.2f})")

    if found_count == 0:
        print(f"{Colors.WARNING}No results found matching the criteria.{Colors.ENDC}")

def database_management_menu(collection):
    """Displays the admin menu and handles user input."""
    while True:
        print(f"\n{Colors.HEADER}{Colors.BOLD}--- Database Management Menu ---{Colors.ENDC}")
        print(f"{Colors.OKCYAN}1. Add/Update a Single Movie{Colors.ENDC}")
        print(f"{Colors.OKCYAN}2. Count Total Records{Colors.ENDC}")
        print(f"{Colors.OKCYAN}3. View Top 5 Records (Peek){Colors.ENDC}")
        print(f"{Colors.OKCYAN}4. Get Record by ID{Colors.ENDC}")
        print(f"{Colors.FAIL}5. Delete Record by ID{Colors.ENDC}")
        print(f"{Colors.OKBLUE}6. Advanced: Filtered Search (Genre + Term){Colors.ENDC}")
        print(f"{Colors.WARNING}7. Return to Main Menu{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}------------------------------{Colors.ENDC}")

        choice = input(f"{Colors.BOLD}Enter your choice (1-7): {Colors.ENDC}")
        if choice == '1':
            admin_add_movie(collection)
        elif choice == '2':
            admin_get_movie_count(collection)
        elif choice == '3':
            admin_peek_records(collection)
        elif choice == '4':
            admin_get_record_by_id(collection)
        elif choice == '5':
            admin_delete_by_id(collection)
        elif choice == '6':
            admin_filtered_search(collection)
        elif choice == '7':
            break
        else:
            print(f"{Colors.FAIL}Invalid choice. Please enter a number between 1 and 7.{Colors.ENDC}")

# --- Main Application Loop ---

def main_menu():
    """Displays the main menu and handles user input."""
    collection = connect_to_collection()
    if not collection:
        return

    while True:
        print(f"\n{Colors.HEADER}{Colors.BOLD}===== Chroma DB Movie Recommendation System ====={Colors.ENDC}")
        print(f"{Colors.OKBLUE}1. Get Movie Recommendations (by title){Colors.ENDC}")
        print(f"{Colors.OKCYAN}2. Find Movies by Genre{Colors.ENDC}")
        print(f"{Colors.OKCYAN}3. List First 20 Movies{Colors.ENDC}")
        print(f"{Colors.WARNING}4. Database Management (Admin){Colors.ENDC}")
        print(f"{Colors.FAIL}5. Exit{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}==============================================={Colors.ENDC}")

        choice = input(f"{Colors.BOLD}Enter your choice (1-5) or 'db-manage': {Colors.ENDC}")

        if choice == '1':
            get_recommendations(collection)
        elif choice == '2':
            find_movies_by_genre(collection)
        elif choice == '3':
            list_all_movies(collection)
        elif choice == '4' or choice.lower() == 'db-manage':
            database_management_menu(collection)
        elif choice == '5':
            print(f"{Colors.OKBLUE}Exiting. Goodbye!{Colors.ENDC}")
            break
        else:
            print(f"{Colors.FAIL}Invalid choice. Please try again.{Colors.ENDC}")

if __name__ == "__main__":
    main_menu()