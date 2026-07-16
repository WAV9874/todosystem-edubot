from pathlib import Path
import pandas as pd
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "data" / "pdfs"
CSV_DIR = BASE_DIR / "data" / "csv"
VECTORSTORE_DIR = BASE_DIR / "vectorstore" / "chroma"

COLLECTION_NAME = "todosystem_base_conocimiento"


class TodoSystemRAG:
    """
    Pipeline RAG básico para TodoSystem EduBot.

    Este componente se encarga de:
    1. Leer documentos PDF y CSV.
    2. Convertirlos en fragmentos de texto.
    3. Generar embeddings.
    4. Guardar los fragmentos en ChromaDB.
    5. Buscar información relevante según una pregunta.
    """

    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    def read_pdf(self, pdf_path: Path) -> list[dict]:
        """Lee un PDF y devuelve fragmentos con metadatos."""
        documents = []

        reader = PdfReader(str(pdf_path))

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()

            if text and text.strip():
                documents.append(
                    {
                        "text": text.strip(),
                        "metadata": {
                            "source": pdf_path.name,
                            "type": "pdf",
                            "page": page_number,
                            "category": "Documento institucional",
                        },
                    }
                )

        return documents

    def read_csv(self, csv_path: Path) -> list[dict]:
        """Lee un CSV y convierte cada fila en texto estructurado."""
        documents = []

        df = pd.read_csv(csv_path)

        for index, row in df.iterrows():
            row_text = []

            for column in df.columns:
                row_text.append(f"{column}: {row[column]}")

            text = " | ".join(row_text)

            documents.append(
                {
                    "text": text,
                    "metadata": {
                        "source": csv_path.name,
                        "type": "csv",
                        "row": int(index) + 1,
                        "category": str(row.get("categoria", "Base de conocimiento")),
                    },
                }
            )

        return documents

    def split_text(self, text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
        """
        Divide textos largos en fragmentos pequeños.

        Esto ayuda al agente a recuperar solo la información más relevante.
        """
        chunks = []

        if len(text) <= chunk_size:
            return [text]

        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def load_documents(self) -> list[dict]:
        """Carga todos los documentos PDF y CSV."""
        all_documents = []

        for pdf_file in PDF_DIR.glob("*.pdf"):
            all_documents.extend(self.read_pdf(pdf_file))

        for csv_file in CSV_DIR.glob("*.csv"):
            all_documents.extend(self.read_csv(csv_file))

        processed_documents = []

        for doc in all_documents:
            chunks = self.split_text(doc["text"])

            for chunk_index, chunk in enumerate(chunks, start=1):
                metadata = doc["metadata"].copy()
                metadata["chunk"] = chunk_index

                processed_documents.append(
                    {
                        "text": chunk,
                        "metadata": metadata,
                    }
                )

        return processed_documents

    def build_index(self):
        """
        Crea el índice vectorial en ChromaDB.

        Si la colección ya tiene documentos, primero los elimina para evitar duplicados.
        """
        documents = self.load_documents()

        existing = self.collection.get()

        if existing and existing.get("ids"):
            self.collection.delete(ids=existing["ids"])

        ids = []
        texts = []
        embeddings = []
        metadatas = []

        for index, doc in enumerate(documents, start=1):
            text = doc["text"]
            embedding = self.model.encode(text).tolist()

            ids.append(f"doc_{index}")
            texts.append(text)
            embeddings.append(embedding)
            metadatas.append(doc["metadata"])

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(documents)

    def search(self, question: str, n_results: int = 4) -> list[dict]:
        """
        Busca fragmentos relevantes para una pregunta.
        """
        question_embedding = self.model.encode(question).tolist()

        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=n_results,
        )

        response = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for text, metadata, distance in zip(documents, metadatas, distances):
            response.append(
                {
                    "text": text,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return response


if __name__ == "__main__":
    rag = TodoSystemRAG()
    total = rag.build_index()

    print(f"Índice creado correctamente con {total} fragmentos.")

    pregunta = "¿Qué documentos necesito para matricularme?"
    resultados = rag.search(pregunta)

    print("\nPregunta de prueba:")
    print(pregunta)

    print("\nFragmentos recuperados:")
    for item in resultados:
        print("-" * 80)
        print("Fuente:", item["metadata"])
        print("Texto:", item["text"][:500])