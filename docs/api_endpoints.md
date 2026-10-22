# API Endpoints & Core Functions

While the current architecture primarily functions as an interactive CLI, the underlying `operations.py` and `admin.py` modules are designed to be easily wrapped by a Python REST framework (like FastAPI or Flask). 

Below defines the core operational functions and their proposed HTTP endpoint equivalents.

---

## 1. Retrieve Recommendations

**Function:** `operations.get_recommendations(collection, movie_title, n_results)`  
**Proposed Endpoint:** `GET /api/v1/recommendations`

**Description:**
Fetches `n_results` nearest neighbors (most similar movies) from the dense vector space based on the target movie's embedding.

**Example Request:**
```http
GET /api/v1/recommendations?movie_title=Inception&limit=3
```

**Example Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "12345",
      "title": "Interstellar",
      "similarity_score": 0.89,
      "metadata": {
        "release_date": "2014-11-05",
        "vote_average": 8.3,
        "genres": "Adventure, Drama, Science Fiction"
      }
    },
    {
      "id": "67890",
      "title": "The Matrix",
      "similarity_score": 0.82,
      ...
    }
  ]
}
```

---

## 2. Advanced Search

**Function:** `operations.advanced_search(collection, query_text, year_filter, rating_filter, runtime_filter)`  
**Proposed Endpoint:** `POST /api/v1/search`

**Description:**
Converts an abstract query string into an embedding, filters against optional constraints (year, min rating, max runtime), and returns contextual matches.

**Example Request:**
```json
{
  "query": "A movie about space exploration",
  "filters": {
    "year_after": 2000,
    "min_rating": 8.0,
    "max_runtime": 150
  }
}
```

**Example Response:**
```json
{
  "status": "success",
  "results_count": 2,
  "data": [
    {
       "title": "Interstellar",
       "match_distance": 0.312
    },
    {
       "title": "The Martian",
       "match_distance": 0.354
    }
  ]
}
```

---

## 3. Explore by Director

**Function:** `operations.explore_by_director(collection, movie_title)`  
**Proposed Endpoint:** `GET /api/v1/movies/director-pivot`

**Description:**
A two-stage deterministic query. It matches the seed movie, extracts the string mapping for `director`, and executes a `$eq` search to fetch the remaining localized filmography.

**Example Request:**
```http
GET /api/v1/movies/director-pivot?seed_movie=The+Dark+Knight
```

**Example Response:**
```json
{
  "director_identified": "Christopher Nolan",
  "data": [
    {"title": "Inception"},
    {"title": "Interstellar"},
    {"title": "Dunkirk"}
  ]
}
```

---

## 4. Admin operations (CRUD)

### Create Movie
**Function:** `admin.create_movie(collection, movie_data)`  
**Proposed Endpoint:** `POST /api/v1/admin/movies`  
*Requires Authorization Header.*

### Delete Movie
**Function:** `admin.delete_movie(collection, movie_id)`  
**Proposed Endpoint:** `DELETE /api/v1/admin/movies/{movie_id}`  
*Requires Authorization Header.*

### Database Insights
**Function:** `admin.show_database_insights(collection)`  
**Proposed Endpoint:** `GET /api/v1/admin/insights`  
*Requires Authorization Header.* Returns JSON aggregation of total movies and distribution of primary genres.
