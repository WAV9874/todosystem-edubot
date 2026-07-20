import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Corrección para servidores Linux donde SQLite viene desactualizado.
# ChromaDB requiere SQLite >= 3.35.
# Esta corrección debe ir ANTES de importar chromadb.
try:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except Exception:
    pass

import chromadb
import pandas as pd
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


class TodoSystemRAG:
    """
    Pipeline RAG para TodoSystem EduBot.

    Lee documentos PDF y CSV, divide el contenido en fragmentos,
    genera embeddings y los guarda en una base vectorial ChromaDB.
    """

    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent

        self.pdf_dir = self.project_root / "data" / "pdfs"
        self.csv_dir = self.project_root / "data" / "csv"
        self.vectorstore_dir = self.project_root / "vectorstore" / "chroma"

        self.collection_name = "todosystem_base_conocimiento"
        self.embedding_model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

        self.vectorstore_dir.mkdir(parents=True, exist_ok=True)

        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        self.client = chromadb.PersistentClient(path=str(self.vectorstore_dir))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def _read_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Lee un PDF y devuelve una lista de textos por página.
        """
        documents = []

        try:
            reader = PdfReader(str(pdf_path))

            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                text = text.strip()

                if text:
                    documents.append(
                        {
                            "text": text,
                            "metadata": {
                                "source": pdf_path.name,
                                "type": "pdf",
                                "page": page_number,
                            },
                        }
                    )

        except Exception as error:
            print(f"Error leyendo PDF {pdf_path.name}: {error}")

        return documents

    def _read_csv(self, csv_path: Path) -> List[Dict[str, Any]]:
        """
        Lee un CSV y convierte cada fila en texto estructurado.
        """
        documents = []

        try:
            df = pd.read_csv(csv_path)

            for index, row in df.iterrows():
                parts = []

                for column in df.columns:
                    value = row.get(column, "")

                    if pd.notna(value):
                        value = str(value).strip()

                        if value:
                            parts.append(f"{column}: {value}")

                row_text = "\n".join(parts)

                if row_text:
                    documents.append(
                        {
                            "text": row_text,
                            "metadata": {
                                "source": csv_path.name,
                                "type": "csv",
                                "row": int(index) + 1,
                            },
                        }
                    )

        except Exception as error:
            print(f"Error leyendo CSV {csv_path.name}: {error}")

        return documents

    def _split_text(self, text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
        """
        Divide textos largos en fragmentos con solapamiento.
        """
        text = text.strip()

        if not text:
            return []

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    def _load_documents(self) -> List[Dict[str, Any]]:
        """
        Carga todos los documentos PDF y CSV disponibles.
        """
        documents = []

        if self.pdf_dir.exists():
            for pdf_path in self.pdf_dir.glob("*.pdf"):
                documents.extend(self._read_pdf(pdf_path))

        if self.csv_dir.exists():
            for csv_path in self.csv_dir.glob("*.csv"):
                documents.extend(self._read_csv(csv_path))

        return documents

    def build_index(self) -> None:
        """
        Construye o reconstruye el índice vectorial en ChromaDB.
        """
        print("Cargando documentos de TodoSystem...")

        raw_documents = self._load_documents()

        if not raw_documents:
            print("No se encontraron documentos para indexar.")
            return

        ids = []
        texts = []
        metadatas = []

        counter = 0

        for document in raw_documents:
            source_text = document["text"]
            metadata = document["metadata"]

            chunks = self._split_text(source_text)

            for chunk_index, chunk in enumerate(chunks, start=1):
                counter += 1

                chunk_metadata = dict(metadata)
                chunk_metadata["chunk"] = chunk_index

                ids.append(f"doc_{counter}")
                texts.append(chunk)
                metadatas.append(chunk_metadata)

        print(f"Fragmentos preparados: {len(texts)}")

        try:
            existing = self.collection.get()

            if existing and existing.get("ids"):
                self.collection.delete(ids=existing["ids"])
                print("Índice anterior eliminado.")

        except Exception as error:
            print(f"No se pudo limpiar el índice anterior: {error}")

        embeddings = self.embedding_model.encode(texts).tolist()

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        print("Índice RAG construido correctamente.")

    def search(self, question: str, n_results: int = 4) -> List[Dict[str, Any]]:
        """
        Busca fragmentos relevantes para una pregunta.
        """
        question = question.strip()

        if not question:
            return []

        try:
            count = self.collection.count()

            if count == 0:
                self.build_index()

        except Exception:
            self.build_index()

        query_embedding = self.embedding_model.encode([question]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        response = []

        for document, metadata, distance in zip(documents, metadatas, distances):
            source = metadata.get("source", "fuente desconocida")
            source_type = metadata.get("type", "")

            if source_type == "pdf":
                page = metadata.get("page", "")
                source_label = f"{source} - página {page}"
            elif source_type == "csv":
                row = metadata.get("row", "")
                source_label = f"{source} - fila {row}"
            else:
                source_label = source

            response.append(
                {
                    "text": document,
                    "texto": document,
                    "content": document,
                    "source": source_label,
                    "fuente": source_label,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return response


if __name__ == "__main__":
    rag = TodoSystemRAG()
    rag.build_index()

    pregunta = "¿Qué cursos ofrece el Instituto TodoSystem?"
    resultados = rag.search(pregunta)

    print("\nPregunta de prueba:")
    print(pregunta)

    print("\nResultados recuperados:")
    for item in resultados:
        print("-" * 60)
        print("Fuente:", item["fuente"])
        print(item["texto"][:500])