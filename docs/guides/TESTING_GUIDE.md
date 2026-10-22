# 🧪 Testing Guide - Showcasing ChromaDB Power

## 🎯 Complete Test Workflow

Follow this workflow to see the full capabilities of the Movie Recommendation System and ChromaDB.

---

## Test 1: Semantic Similarity (Vector Search)

### Input
```
Menu: 🎯 Get Movie Recommendations
Movie: Inception
Number: 6
```

### Expected Output
- Similar mind-bending films
- Movies with similar themes (dreams, reality, psychological)
- High similarity scores (>80%)
- Examples: The Matrix, Interstellar, Shutter Island, The Prestige

### ChromaDB Feature Demonstrated
✓ **Vector similarity search** using embeddings
✓ **Cosine distance** calculations
✓ **Semantic understanding** of plot and themes

---

## Test 2: Hybrid Search (Vectors + Filters)

### Input
```
Menu: 🔍 Advanced Search
Query: "A movie about space exploration"
Filters:
  - Year: After 2000
  - Rating: 7.0+
  - Runtime: Max 180 minutes
```

### Expected Output
- High-rated modern space films
- Filtered by metadata constraints
- Examples: Interstellar (2014, 8.6), Gravity (2013, 7.7), The Martian (2015, 7.6)

### ChromaDB Feature Demonstrated
✓ **Hybrid queries** (semantic + metadata)
✓ **Complex filtering** with `$and`, `$gte`, `$lte` operators
✓ **Multi-dimensional search**

---

## Test 3: Metadata Filtering (Genre Search)

### Input
```
Menu: 🎭 Find Movies by Genre
Genre: Sci-Fi
```

### Expected Output
- All science fiction movies
- Wide variety of sub-genres
- Examples: Star Wars, Blade Runner, The Matrix, Interstellar

### ChromaDB Feature Demonstrated
✓ **Metadata-only queries**
✓ **String matching** in metadata fields
✓ **Efficient filtering** without vector search

---

## Test 4: Join-like Operations (Director Exploration)

### Input
```
Menu: 🎬 Explore by Director
Movie: Inception
```

### Expected Output
```
Director: Christopher Nolan

✓ Found 13 movies directed by Christopher Nolan

Movies:
- The Dark Knight Rises
- The Dark Knight
- Interstellar
- Inception
- Batman Begins
- The Prestige
- Memento
- Insomnia
- Dunkirk
- Following
```

### ChromaDB Feature Demonstrated
✓ **Multi-step queries** (join simulation)
✓ **Metadata extraction** and filtering
✓ **Relational-style operations** on vector DB

---

## Test 5: More Director Examples

### Test 5a: Quentin Tarantino
```
Movie: Pulp Fiction
Expected: 16 films including Django Unchained, Kill Bill, Reservoir Dogs
```

### Test 5b: James Cameron
```
Movie: Avatar
Expected: 11 films including Titanic, Terminator 2, Aliens, The Abyss
```

### Test 5c: Steven Spielberg
```
Movie: Jurassic Park
Expected: Multiple blockbusters including E.T., Jaws, Schindler's List
```

---

## Test 6: Advanced Search Variations

### Test 6a: Emotional Themes
```
Query: "A heartwarming story about friendship"
Filters: After 2010, Rating 7.5+
Expected: Inside Out, Coco, The Intouchables
```

### Test 6b: Action Genre
```
Query: "An action-packed heist movie"
Filters: After 1995, Rating 6.5+
Expected: Ocean's Eleven, The Italian Job, Baby Driver
```

### Test 6c: Time Period
```
Query: "Epic war movie"
Filters: Before 2000, Rating 8.0+
Expected: Saving Private Ryan, Schindler's List, Apocalypse Now
```

---

## Test 7: Recommendation Chains

### Workflow
1. Start: `The Matrix`
2. Get recommendations → Find `Inception`
3. Explore director → Find `Interstellar`
4. Get recommendations → Find `Gravity`
5. Explore director → Find `Children of Men`

### ChromaDB Feature Demonstrated
✓ **Chained queries** for discovery
✓ **Graph-like traversal** of movie relationships
✓ **Combining multiple search strategies**

---

## Test 8: Admin Panel Features

### Test 8a: Database Insights
```
Menu: ⚙️ Admin Panel → 📊 Database Insights
Password: admin123

Expected:
- Total movie count: ~8,723
- Top 10 genres with bar chart
- Genre distribution visualization
```

### Test 8b: Benchmark Queries
```
Menu: ⚙️ Admin Panel → ⚡ Benchmark Queries

Expected:
- Average query time: <100ms
- Performance statistics
- HNSW indexing explanation
```

### Test 8c: CRUD Operations
```
Create: Add a new movie
Read: View movie by ID
Update: Modify movie metadata
Delete: Remove a movie (with confirmation)
```

---

## 🎪 Complete Demo Scenario

### Scenario: Finding the Perfect Movie Night Pick

**Step 1: Browse by Genre**
```
Menu: 🎭 Find Movies by Genre
Genre: Thriller
Result: See all thriller movies
```

**Step 2: Narrow Down with Search**
```
Menu: 🔍 Advanced Search
Query: "psychological thriller with plot twists"
Filters: After 2000, Rating 7.5+
Result: Shutter Island, Gone Girl, The Prestige
```

**Step 3: Get Similar Recommendations**
```
Menu: 🎯 Get Movie Recommendations
Movie: Shutter Island
Result: Similar psychological thrillers
```

**Step 4: Explore Director's Work**
```
Menu: 🎬 Explore by Director
Movie: Shutter Island
Director: Martin Scorsese
Result: The Departed, The Wolf of Wall Street, Goodfellas
```

**Step 5: Final Decision**
```
Choose: The Departed (2006, 8.5 rating)
Genre: Crime, Drama, Thriller
Runtime: 151 minutes
```

---

## 📊 Performance Benchmarks

### Expected Performance
- **First query**: 1-3 seconds (model loading)
- **Subsequent queries**: <100ms
- **Batch operations**: ~500 movies/second
- **Database size**: ~8,700 movies
- **Embedding dimension**: 384 (default sentence transformer)

### Optimization Tips
1. First query is slower (model initialization)
2. Keep database size reasonable for fast queries
3. Use metadata filters to reduce search space
4. Batch operations for bulk updates

---

## ✅ Verification Checklist

After testing, verify:

- [ ] Recommendations return similar movies
- [ ] Similarity scores are reasonable (>70% for good matches)
- [ ] Filters correctly exclude movies
- [ ] Director exploration finds all films by director
- [ ] Genre search returns appropriate movies
- [ ] Admin panel shows correct statistics
- [ ] CRUD operations work without errors
- [ ] Performance is acceptable (<1s for most queries)

---

## 🐛 Common Issues & Solutions

### Issue: "Director information not available"
**Solution**: Run `python fix_director_metadata.py`

### Issue: Slow queries
**Solution**: Normal for first query. Subsequent queries should be fast.

### Issue: No results found
**Solution**: Try more common movie titles or broader search terms.

### Issue: Too many results
**Solution**: Add more filters or use more specific queries.

---

## 🎓 What You're Learning

### ChromaDB Concepts
1. **Vector Embeddings**: Text → numerical representations
2. **Similarity Search**: Finding nearest neighbors in vector space
3. **Metadata Filtering**: Combining structured and unstructured data
4. **HNSW Indexing**: Fast approximate nearest neighbor search
5. **Hybrid Queries**: Best of both worlds (semantic + exact match)

### Database Operations
1. **CRUD**: Create, Read, Update, Delete
2. **Batch Processing**: Efficient bulk operations
3. **Query Optimization**: Using filters to reduce search space
4. **Performance Monitoring**: Benchmarking and profiling

---

## 🚀 Next Steps

After completing these tests:

1. **Experiment**: Try your own queries and movie combinations
2. **Analyze**: Look at similarity scores and understand why movies match
3. **Optimize**: Test different filter combinations
4. **Extend**: Add new features or improve existing ones
5. **Learn**: Read about vector databases and embeddings

---

**Happy Testing! 🎬✨**
