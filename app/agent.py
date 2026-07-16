from app.rag_pipeline import TodoSystemRAG
from app.prompts import PROMPT_PRINCIPAL


class TodoSystemAgent:
    """
    Agente académico para el Instituto TodoSystem.

    Este agente usa el pipeline RAG para buscar información en documentos PDF y CSV,
    selecciona los fragmentos más relevantes y construye una respuesta clara para el usuario.
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

    def _parse_csv_text(self, text: str) -> dict:
        """
        Convierte un texto generado desde CSV en un diccionario.

        Ejemplo:
        id: 2 | dato: Ubicación general | descripcion: Bugalagrande...
        """
        data = {}

        parts = text.split("|")

        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                data[key.strip().lower()] = value.strip()

        return data

    def _clean_text(self, text: str) -> str:
        """
        Limpia texto para evitar caracteres raros o saltos innecesarios.
        """
        text = text.replace("\x7f", "-")
        text = " ".join(text.split())
        return text.strip()

    def _build_answer_from_csv(self, data: dict) -> str:
        """
        Construye respuestas claras cuando la información viene desde archivos CSV.
        """

        # Caso FAQ: pregunta y respuesta
        if "pregunta" in data and "respuesta" in data:
            return data["respuesta"]

        # Caso contacto: dato y descripción
        if "dato" in data and "descripcion" in data:
            dato = data.get("dato", "Información")
            descripcion = data.get("descripcion", "")

            return f"{dato}: {descripcion}"

        # Caso cursos
        if "nombre_curso" in data:
            nombre = data.get("nombre_curso", "Curso")
            descripcion = data.get("descripcion", "No disponible")
            duracion = data.get("duracion", "No disponible")
            modalidad = data.get("modalidad", "No disponible")
            horario = data.get("horario", "No disponible")
            requisitos = data.get("requisitos", "No disponible")
            valor = data.get("valor", "Consultar con el área administrativa")
            estado = data.get("estado", "No disponible")

            return (
                f"El curso {nombre} tiene la siguiente información registrada:\n\n"
                f"- Descripción: {descripcion}\n"
                f"- Duración: {duracion}\n"
                f"- Modalidad: {modalidad}\n"
                f"- Horario: {horario}\n"
                f"- Requisitos: {requisitos}\n"
                f"- Valor: {valor}\n"
                f"- Estado: {estado}"
            )

        # Respuesta general si el CSV no coincide con los casos anteriores
        readable_items = []

        for key, value in data.items():
            if key not in ["id", "fuente", "categoria"]:
                readable_items.append(f"- {key.capitalize()}: {value}")

        if readable_items:
            return "\n".join(readable_items)

        return ""

    def _build_answer_from_pdf(self, text: str) -> str:
        """
        Construye una respuesta sencilla cuando la información viene desde PDF.
        """
        clean_text = self._clean_text(text)

        if len(clean_text) > 800:
            clean_text = clean_text[:800].rsplit(" ", 1)[0] + "..."

        return clean_text

    def _is_contact_question(self, question: str) -> bool:
        """
        Detecta si la pregunta está relacionada con contacto, dirección o ubicación.
        """
        contact_keywords = [
            "dirección",
            "direccion",
            "ubicación",
            "ubicacion",
            "ubicados",
            "ubicado",
            "dónde",
            "donde",
            "queda",
            "contacto",
            "teléfono",
            "telefono",
            "whatsapp",
            "correo",
        ]

        normalized_question = question.lower()

        return any(keyword in normalized_question for keyword in contact_keywords)

    def _select_best_result(self, question: str, results: list[dict]) -> dict:
        """
        Selecciona el resultado más adecuado según la intención de la pregunta.
        """

        # Si la pregunta es sobre contacto, ubicación o dirección,
        # damos prioridad al archivo contacto_todosystem.csv.
        if self._is_contact_question(question):
            contact_results = [
                item
                for item in results
                if item.get("metadata", {}).get("source") == "contacto_todosystem.csv"
            ]

            if contact_results:
                return contact_results[0]

        # Si no es una pregunta de contacto, usamos el primer resultado del RAG.
        return results[0]

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

        best_result = self._select_best_result(question, results)

        best_text = best_result.get("text", "")
        best_metadata = best_result.get("metadata", {})

        answer_text = ""

        if best_metadata.get("type") == "csv":
            data = self._parse_csv_text(best_text)
            answer_text = self._build_answer_from_csv(data)

        if best_metadata.get("type") == "pdf" or not answer_text:
            answer_text = self._build_answer_from_pdf(best_text)

        if not answer_text:
            answer_text = (
                "No encontré una respuesta suficientemente clara en la base de conocimiento disponible. "
                "Te recomiendo confirmar esta información directamente con el área administrativa del Instituto TodoSystem."
            )

        final_answer = (
            f"{answer_text}\n\n"
            "Nota: esta respuesta se genera con base en la información disponible en los documentos del proyecto. "
            "Para confirmar datos sensibles como valores, cupos, fechas de inicio o dirección exacta, "
            "se recomienda contactar directamente al área administrativa."
        )

        sources = self._format_sources([best_result])
        contexts = [self._clean_text(item["text"]) for item in results]

        return {
            "answer": final_answer,
            "sources": sources,
            "contexts": contexts,
            "system_prompt": PROMPT_PRINCIPAL,
        }


if __name__ == "__main__":
    agent = TodoSystemAgent()

    questions = [
        "¿Qué documentos necesito para matricularme?",
        "¿En dónde están ubicados?",
        "¿Cuál es la dirección del instituto?",
        "¿Qué cursos ofrece el Instituto TodoSystem?",
        "¿Cuánto cuesta el curso de mantenimiento de computadores?",
    ]

    for question in questions:
        result = agent.answer(question)

        print("=" * 80)
        print("Pregunta:")
        print(question)

        print("\nRespuesta del agente:")
        print(result["answer"])

        print("\nFuentes consultadas:")
        for source in result["sources"]:
            print("-", source)
