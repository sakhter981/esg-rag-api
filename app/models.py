from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    company_name = Column(String, index=True)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())

    # This creates a relationship link to the chunks table below
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    
    # The actual text from the PDF paragraph
    chunk_text = Column(Text)
    
    # The AI Vector representation! OpenAI uses 1536 dimensions
    embedding = Column(Vector(384))

    # Link back to the parent document
    document = relationship("Document", back_populates="chunks")