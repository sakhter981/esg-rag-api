from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings

from app.database import get_db, engine
from app import models

# Ensure tables and the vector extension are created when the API starts
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ESG Document Analytics API")

# Initialize the embedding model globally so it doesn't reload on every request
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Pydantic models define what the JSON data going in and out of the API should look like
class SearchQuery(BaseModel):
    query: str
    limit: int = 3

class SearchResult(BaseModel):
    document_name: str
    company_name: str
    chunk_text: str
    similarity_score: float

@app.get("/")
def health_check(db: Session = Depends(get_db)):
    return {"status": "API is Online", "database": "Connected"}

@app.post("/search", response_model=List[SearchResult])
def search_documents(request: SearchQuery, db: Session = Depends(get_db)):
    try:
        # 1. Convert the user's text question into a mathematical vector
        query_vector = embedding_model.embed_query(request.query)
        
        # 2. Convert the Python list into a string format PostgreSQL understands: "[0.1, 0.2, ...]"
        vector_str = "[" + ",".join(map(str, query_vector)) + "]"
        
        # 3. Perform the Cosine Similarity search directly in SQL!
        # The `<=>` operator tells pgvector to find the closest matching vectors.
        sql_query = text("""
            SELECT 
                d.filename, 
                d.company_name, 
                c.chunk_text,
                1 - (c.embedding <=> :vector) AS similarity_score
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            ORDER BY c.embedding <=> :vector
            LIMIT :limit
        """)
        
        results = db.execute(sql_query, {"vector": vector_str, "limit": request.limit}).fetchall()
        
        # 4. Format the output
        response = []
        for row in results:
            response.append(SearchResult(
                document_name=row[0],
                company_name=row[1],
                chunk_text=row[2],
                similarity_score=round(row[3], 4)
            ))
            
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))