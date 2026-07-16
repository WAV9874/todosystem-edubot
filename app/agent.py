from app.rag_pipeline import TodoSystemRAG
from app.prompts import PROMPT_PRINCIPAL


class TodoSystemAgent:
    """
    Agente académico para el Instituto TodoSystem.

    Este agente usa el pipeline RAG para buscar información en documentos PDF y CSV,
    y luego construye una respuesta clara basada en los fragmentos recuperados.
    """

    def __init__(self):
        self.rag = TodoSystemRAG()

    def _format_sources(self, results: list[dict]) -> list[str]:
        """Extrae fuentes únicas desde los metadatos de los documentos recuperados."""
        sources = []

        for item in results:
            metadata = item.get("metadata", {})
            source = metadata.get("source", "Fuente no identificada")

            detail = source

            if metadata.get("type") == "pdf":
                detail += f" - página {metadata.get('page', 'N/A')}"

            if metadata.get("type") == "csv":
                detail += f" - fila {metadata.get('row', 'N/A')}"

            if detail not in sources:
                sources.append(detail)

        return sources

    def _clean_fragment(self, text: str, max_length: int = 700) -> str:
        """
        Limpia y recorta un fragmento para que la respuesta sea más legible.
        """
        text = " ".join(text.split())

        if len(text) > max_length:
            text = text[:max_length].rsplit(" ", 1)[0] + "..."

        return text

    def answer(self, question: str) -> dict:
        """
        Responde una pregunta usando la base de conocimiento.

        Retorna:
        - respuesta
        - fuentes
        - fragmentos recuperados
        """

        if not question or not question.strip():
            return {
                "answer": "Por favor, escribe una pregunta para poder ayudarte.",
                "sources": [],
                "contexts": [],
            }

        results = self.rag.search(question, n_results=4)

        if not results:
            return {
                "answer": (
                    "No encontré información relacionada en la base de conocimiento disponible. "
                    "Te recomiendo comunicarte directamente con el área administrativa del Instituto TodoSystem."
                ),
                "sources": [],
                "contexts": [],
            }

        contexts = [self._clean_fragment(item["text"]) for item in results]
        sources = self._format_sources(results)

        response = (
            "Según la información disponible en la base de conocimiento del Instituto TodoSystem, "
            "encontré lo siguiente:\n\n"
        )

        for index, context in enumerate(contexts[:3], start=1):
            response += f"{index}. {context}\n\n"

        response += (
            "Recomendación: si la consulta está relacionada con valores, cupos, fechas de inicio "
            "o condiciones específicas, confirma la información directamente con el área administrativa."
        )

        return {
            "answer": response,
            "sources": sources,
            "contexts": contexts,
            "system_prompt": PROMPT_PRINCIPAL,
        }


if __name__ == "__main__":
    agent = TodoSystemAgent()

    question = "¿Qué documentos necesito para matricularme?"
    result = agent.answer(question)

    print("Pregunta:")
    print(question)

    print("\nRespuesta del agente:")
    print(result["answer"])

    print("\nFuentes consultadas:")
    for source in result["sources"]:
        print("-", source)
