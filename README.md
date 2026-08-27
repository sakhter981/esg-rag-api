# Enterprise ESG Document Analytics & RAG API 🌍📊

An enterprise-grade REST API built to automate the extraction and semantic search of unstructured corporate ESG (Environmental, Social, and Governance) reports using AI.

By leveraging a local open-source embedding model, this Retrieval-Augmented Generation (RAG) pipeline guarantees data privacy and eliminates recurring AI API costs, making it ideal for processing sensitive corporate documents.

## 🚀 Tech Stack
* **Backend:** Python, FastAPI, SQLAlchemy
* **AI & NLP:** LangChain, Hugging Face (`all-MiniLM-L6-v2`)
* **Database:** PostgreSQL, Docker, `pgvector`
* **Document Processing:** PyPDF2

## 🧠 Key Features
* **Zero-Cost Local AI:** Uses Hugging Face sentence transformers for generating mathematical vector embeddings directly on your machine.
* **Semantic Search:** Uses Cosine Similarity via `pgvector` to find the exact paragraphs that answer user queries.
* **Automated Chunking:** Intelligently splits 100-page PDFs into overlapping contextual chunks to maintain AI accuracy.

## 🛠️ Quick Start

**1. Clone the repository and install dependencies**
```bash
git clone (https://github.com/sakhter981/esg-rag-api.git)
cd esg-rag-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
