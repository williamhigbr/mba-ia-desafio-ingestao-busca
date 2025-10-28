import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

def ingest_pdf():

    for k in ("GOOGLE_API_KEY",
              "DATABASE_URL",
              "PG_VECTOR_COLLECTION_NAME",
              "PDF_PATH"):
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")

    PDF_PATH = os.getenv("PDF_PATH")

    docs = PyPDFLoader(str(PDF_PATH)).load()

    splits = RecursiveCharacterTextSplitter(chunk_size=1000,
                                            chunk_overlap=150,
                                            add_start_index=False).split_documents(docs)

    metadata_enriched_records = [
        Document(page_content=d.page_content,
                 metadata={k: v for k, v in d.metadata.items() if v not in ("", None)})
        for d in splits
    ]

    document_ids = [f"mba-challenge-{i}" for i in range(len(metadata_enriched_records))]

    embeddings = GoogleGenerativeAIEmbeddings(model=os.getenv("GOOGLE_MODEL","gemini-embedding-001"))

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

    store.add_documents(documents=metadata_enriched_records, ids=document_ids)

if __name__ == "__main__":
    ingest_pdf()