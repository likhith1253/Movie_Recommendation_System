
# 🎬 Sample Inputs for Movie Recommendation System

This document provides optimal sample inputs that showcase the full power of ChromaDB and the movie recommendation system.

## 📊 Overview

The system demonstrates ChromaDB's capabilities through:
- **Semantic Search**: Vector similarity using embeddings
- **Metadata Filtering**: Advanced queries with multiple conditions
- **Join-like Operations**: Finding related data (movies by same director)
- **Hybrid Search**: Combining semantic search with filters

---

## 🎯 1. Get Movie Recommendations

### Best Sample Inputs:

#### **Input 1: "Inception"**
- **Why**: Complex thriller with multiple thematic elements
- **Expected Results**: Crime/thriller movies with similar plots (Unknown, Minority Report, Catch Me If You Can)
- **Note**: Focuses on crime/espionage aspects rather than pure sci-fi
- **ChromaDB Feature**: Demonstrates semantic similarity based on plot descriptions

#### **Input 2: "The Dark Knight"**
- **Why**: Iconic superhero film with complex themes
- **Expected Results**: Other Christopher Nolan films, superhero movies, crime thrillers
- **ChromaDB Feature**: Shows how embeddings capture multiple dimensions (genre, director style, themes)

#### **Input 3: "The Matrix"**
- **Why**: Pure sci-fi action with clear genre focus
- **Expected Results**: Sci-fi action movies with similar themes
- **ChromaDB Feature**: Demonstrates genre-based clustering

#### **Input 4: "Toy Story"**
- **Why**: Family-friendly animation with strong emotional themes
- **Expected Results**: Other Pixar films, animated features
- **ChromaDB Feature**: Demonstrates clustering of similar content types

#### **Input 5: "Interstellar"**
- **Why**: Space exploration sci-fi with emotional depth
- **Expected Results**: Space movies, hard sci-fi films
- **ChromaDB Feature**: Shows semantic understanding of scientific themes

---

## 🔍 2. Advanced Search (Semantic + Filters)

### Best Sample Inputs:

#### **Query 1: "A movie about space exploration"**
**Filters:**
- Year: After 2000
- Rating: 7.0+
- Runtime: Max 180 minutes

**Why**: Showcases hybrid search combining semantic understanding with metadata filters
**Expected Results**: "Interstellar", "Gravity", "The Martian", "Apollo 13"

#### **Query 2: "A heartwarming story about friendship"**
**Filters:**
- Year: After 2010
- Rating: 7.5+

**Why**: Tests semantic understanding of emotional themes
**Expected Results**: "Inside Out", "Coco", "The Intouchables"

#### **Query 3: "An action-packed heist movie"**
**Filters:**
- Year: After 1995
- Rating: 6.5+
- Runtime: Max 150 minutes

**Why**: Demonstrates genre + plot understanding
**Expected Results**: "Ocean's Eleven", "The Italian Job", "Baby Driver", "Now You See Me"

---

## 🎭 3. Find Movies by Genre

### Best Sample Inputs:

#### **Input 1: "Sci-Fi"**
- **Why**: Large genre with diverse sub-themes
- **Expected**: Wide variety from "Star Wars" to "Blade Runner"

#### **Input 2: "Animation"**
- **Why**: Shows family-friendly content clustering
- **Expected**: Disney, Pixar, DreamWorks films

#### **Input 3: "Thriller"**
- **Why**: Tests genre that often overlaps with others
- **Expected**: Psychological thrillers, crime thrillers, action thrillers

---

## 🎬 4. Explore by Director (Join-like Operation)

### Best Sample Inputs:

#### **Input 1: "Inception"**
- **Director**: Christopher Nolan
- **Expected Results**: "The Dark Knight", "Interstellar", "The Prestige", "Dunkirk", "Memento"
- **ChromaDB Feature**: Demonstrates metadata-based filtering (join-like operation)

#### **Input 2: "Pulp Fiction"**
- **Director**: Quentin Tarantino
- **Expected Results**: "Django Unchained", "Inglourious Basterds", "Kill Bill", "Reservoir Dogs"
- **ChromaDB Feature**: Shows director filmography retrieval

#### **Input 3: "Toy Story"**
- **Director**: John Lasseter
- **Expected Results**: "A Bug's Life", "Toy Story 2", "Cars"
- **ChromaDB Feature**: Animation director portfolio

#### **Input 4: "The Shawshank Redemption"**
- **Director**: Frank Darabont
- **Expected Results**: "The Green Mile", "The Mist"
- **ChromaDB Feature**: Smaller but high-quality filmography

#### **Input 5: "Avatar"**
- **Director**: James Cameron
- **Expected Results**: "Titanic", "The Terminator", "Aliens", "True Lies"
- **ChromaDB Feature**: Blockbuster director catalog

---

## 📋 5. List Sample Movies

### Best Sample Input:

#### **Input: 20-50 movies**
- **Why**: Shows database diversity and metadata richness
- **Use**: Quick overview of available content

---

## 🎪 Complete Workflow Example

### Scenario: Finding the Perfect Sci-Fi Movie

1. **Start with Genre Search**: "Sci-Fi"
   - Browse available sci-fi movies

2. **Narrow with Advanced Search**: "A movie about artificial intelligence and humanity"
   - Filters: After 2000, Rating 7.0+
   - Results: "Ex Machina", "Her", "A.I. Artificial Intelligence"

3. **Get Recommendations**: "Ex Machina"
   - Find similar thought-provoking sci-fi

4. **Explore Director**: "Ex Machina"
   - Discover other Alex Garland films: "Annihilation"

---

## 🚀 ChromaDB Features Demonstrated

### 1. **Vector Similarity Search**
- Semantic understanding of movie plots
- Theme and mood matching
- Genre clustering

### 2. **Metadata Filtering**
- Year range queries
- Rating thresholds
- Runtime constraints
- Genre matching

### 3. **Hybrid Queries**
- Combining semantic search with filters
- Multi-condition filtering with `$and` operator

### 4. **Join-like Operations**
- Finding movies by same director
- Demonstrates relational-style queries on vector DB

### 5. **Scalability**
- Fast queries on 4,800+ movies
- Efficient batch operations
- Real-time semantic search

---

## 💡 Pro Tips

1. **For Best Recommendations**: Use well-known movie titles with rich metadata
2. **For Advanced Search**: Combine descriptive queries with 2-3 filters
3. **For Director Exploration**: Use movies from prolific directors (Nolan, Tarantino, Spielberg)
4. **For Genre Search**: Use standard genre names (Action, Comedy, Drama, Sci-Fi, etc.)

---

## 🎯 Quick Reference: Best Movies to Try

### Recommendations:
- Inception
- The Dark Knight
- Interstellar
- The Matrix
- Pulp Fiction
- The Shawshank Redemption
- Forrest Gump
- The Godfather

### Director Exploration:
- Inception (Christopher Nolan)
- Pulp Fiction (Quentin Tarantino)
- Avatar (James Cameron)
- Jurassic Park (Steven Spielberg)
- The Grand Budapest Hotel (Wes Anderson)

### Advanced Search Queries:
- "A movie about time travel and paradoxes"
- "An epic war movie with emotional depth"
- "A comedy about family and relationships"
- "A thriller with unexpected plot twists"

---

## 📝 Notes

- **Database Size**: ~4,800 movies from TMDB dataset
- **Embedding Model**: ChromaDB's default sentence transformer
- **Metadata Fields**: title, overview, genres, release_date, vote_average, runtime, director
- **Search Performance**: Sub-second queries on full dataset

---

**Enjoy exploring the power of ChromaDB! 🎬✨**
