# Deployment Guide

The Movie Recommendation System is built focusing on a localized vector database model. Depending on the traffic tier, deployment can range from simple monoliths via VPS to orchestrated containers with separated UI/API layers.

## 💻 Local Deployment

For testing and immediate localized usage:

1. **Clone & Install**:
   ```bash
   git clone <repo-url>
   cd Movie_Recommendation_System
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Ingest Vectors**:
   ```bash
   python ingest_data.py
   ```
3. **Execute Process**:
   ```bash
   python main.py
   ```

## ☁️ Cloud / VPS Deployment Overview

Deploying to cloud services (AWS EC2, DigitalOcean Droplets) mirrors the local setup since ChromaDB writes locally to the file system (`./movie_db`). 

### Critical Considerations for Cloud Environments

1. **Persistent Storage (Volumes)**
   Since embeddings are persisted locally within `movie_db`, a transient container (like AWS Fargate or standard Heroku instances) will wipe your embeddings on restart.
   - **Solution**: Mount a persistent block volume (AWS EBS) directly to the application directory holding `movie_db`.
2. **Memory Constraints**
   The sentence transformer model `all-MiniLM-L6-v2` runs mostly in RAM. 
   - Ensure the server has at minimum **4GB RAM**. A standard `t3.medium` on AWS is highly recommended.
3. **Authentication Variables**
   The application holds sensitive configurations hard-coded inside `config.py` (e.g., `ADMIN_PASSWORD = "admin123"`).
   - In production, refactor this block to pull from `os.environ.get("ADMIN_PASSWORD")` and configure your `.env` securely.

## 🐳 Docker Containerization

To safely isolate the application and dependencies, a standard `Dockerfile` can be instantiated.

### Proposed Dockerfile
```dockerfile
# Use an official lightweight Python base
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose potential UI/API port
EXPOSE 8000

# Mount external volume to persist ChromaDB embeddings
VOLUME ["/app/movie_db"]

# Default command
CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  recommender_system:
    build: .
    volumes:
      - chroma_data:/app/movie_db
    environment:
      - ADMIN_PASSWORD=SecurePassword123

volumes:
  chroma_data:
```

## Scaling Up 

If scaling requirements shift from 5,000 strings to 5+ Million strings, local-file ChromaDB implementations will cap CPU cycles efficiently. In these instances:
- Move from Local Chroma to the [ChromaDB Client/Server HTTP architecture](https://docs.trychroma.com/getting-started).
- Offload the embedding process from `sentence-transformers` locally via CPU, switching inference handling to external endpoints like OpenAI API or Cohere to eliminate hardware bounding entirely.
