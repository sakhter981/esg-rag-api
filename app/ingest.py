import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models import Document, DocumentChunk, Base

# --- THE FIX IS HERE ---
# 1. Activate the pgvector extension FIRST
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

# 2. NOW create the tables
Base.metadata.create_all(bind=engine)
# -----------------------

def process_pdf(file_path: str, company_name: str):
    print(f"1. Reading {file_path}...")
    
    reader = PdfReader(file_path)
    text_content = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_content += extracted + "\n"

    print("2. Chunking text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text_content)
    print(f" -> Created {len(chunks)} chunks.")

    print("3. Generating vector embeddings (Running locally on your Mac!)...")
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectors = embeddings_model.embed_documents(chunks)

    print("4. Saving everything to PostgreSQL...")
    db: Session = SessionLocal()
    try:
        filename = os.path.basename(file_path)
        db_doc = Document(filename=filename, company_name=company_name)
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)

        for chunk_text, vector in zip(chunks, vectors):
            db_chunk = DocumentChunk(
                document_id=db_doc.id,
                chunk_text=chunk_text,
                embedding=vector
            )
            db.add(db_chunk)
        
        db.commit()
        print(f"✅ Success! Saved {filename} to the vector database.")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sample_pdf = "data/sample_report.pdf"
    
    if not os.path.exists(sample_pdf):
        print("❌ Error: Please place a PDF named 'sample_report.pdf' inside the data/ folder!")
    else:
        process_pdf(sample_pdf, "Apple")