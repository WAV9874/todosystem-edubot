from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.rag_pipeline import TodoSystemRAG
from app.prompts import PROMPT_PRINCIPAL


BASE_DIR = Path(__file__).resolve().parent.parent
CONTACT_FILE = BASE_DIR / "data" / "csv" / "contacto_todosystem.csv"
COURSES_FILE = BASE_DIR / "data" / "csv" / "cursos_todosystem.csv"


class TodoSystemAgent:
    """
    Agente académico para el Instituto TodoSystem.

    Usa RAG para consultar documentos PDF y CSV, pero responde directamente
    desde CSV cuando la pregunta es sobre contacto, ubicación o listado de cursos.
    """

    def __init__(self):
        self.rag = TodoSystemRAG()

    def _format_sources(self, results: list[dict]) -> list[str]:
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
        data = {}

        for part in text.split("|"):
            if ":" in part:
                key, value = part.split(":", 1)
                data[key.strip().lower()] = value.strip()

        return data

    def _clean_text(self, text: str) -> str:
        text = text.replace("\x7f", "-")
        text = " ".join(text.split())
        return text.strip()

    def _build_answer_from_csv(self, data: dict) -> str:
        if "pregunta" in data and "respuesta" in data:
            return data["respuesta"]

        if "dato" in data and "descripcion" in data:
            return f"{data.get('dato')}: {data.get('descripcion')}"

        if "nombre_curso" in data:
            return (
                f"El curso {data.get('nombre_curso')} tiene la siguiente información registrada:\n\n"
                f"- Descripción: {data.get('descripcion', 'No disponible')}\n"
                f"- Duración: {data.get('duracion', 'No disponible')}\n"
                f"- Modalidad: {data.get('modalidad', 'No disponible')}\n"
                f"- Horario: {data.get('horario', 'No disponible')}\n"
                f"- Requisitos: {data.get('requisitos', 'No disponible')}\n"
                f"- Valor: {data.get('valor', 'Consultar con el área administrativa')}\n"
                f"- Estado: {data.get('estado', 'No disponible')}"
            )

        readable_items = []
        for key, value in data.items():
            if key not in ["id", "fuente", "categoria"]:
                readable_items.append(f"- {key.capitalize()}: {value}")

        return "\n".join(readable_items)

    def _build_answer_from_pdf(self, text: str) -> str:
        clean_text = self._clean_text(text)

        if len(clean_text) > 800:
            clean_text = clean_text[:800].rsplit(" ", 1)[0] + "..."

        return clean_text

    def _finalize_answer(self, answer_text: str) -> str:
        return (
            f"{answer_text}\n\n"
            "Nota: esta respuesta se genera con base en la información disponible en los documentos del proyecto. "
            "Para confirmar datos sensibles como valores, cupos, fechas de inicio o dirección exacta, "
            "se recomienda contactar directamente con el área administrativa."
        )

    def _is_contact_question(self, question: str) -> bool:
        keywords = [
            "dirección", "direccion", "ubicación", "ubicacion", "ubicados", "ubicado",
            "dónde", "donde", "queda", "contacto", "teléfono", "telefono",
            "whatsapp", "correo", "horario", "atienden", "atención", "atencion"
        ]
        question = question.lower()
        return any(keyword in question for keyword in keywords)

    def _answer_contact_question(self, question: str) -> dict | None:
        if not self._is_contact_question(question):
            return None

        if not CONTACT_FILE.exists():
            return None

        df = pd.read_csv(CONTACT_FILE)
        question = question.lower()
        selected_row = None

        if any(word in question for word in ["dirección", "direccion"]):
            selected = df[df["dato"].str.contains("Dirección", case=False, na=False)]
            if not selected.empty:
                selected_row = selected.iloc[0]

        elif any(word in question for word in ["ubicación", "ubicacion", "ubicados", "ubicado", "dónde", "donde", "queda"]):
            selected = df[df["dato"].str.contains("Ubicación|Dirección", case=False, na=False)]
            if not selected.empty:
                selected_row = selected.iloc[0]

        elif any(word in question for word in ["horario", "atienden", "atención", "atencion"]):
            selected = df[df["dato"].str.contains("Horario", case=False, na=False)]
            if not selected.empty:
                selected_row = selected.iloc[0]

        elif any(word in question for word in ["correo", "email"]):
            selected = df[df["dato"].str.contains("Correo", case=False, na=False)]
            if not selected.empty:
                selected_row = selected.iloc[0]

        elif any(word in question for word in ["teléfono", "telefono", "whatsapp", "celular"]):
            selected = df[df["dato"].str.contains("Teléfono|WhatsApp", case=False, na=False)]
            if not selected.empty:
                selected_row = selected.iloc[0]

        if selected_row is None:
            selected = df[df["dato"].str.contains("Recomendación|Área administrativa", case=False, na=False)]
            if not selected.empty:
                selected_row = selected.iloc[0]

        if selected_row is None:
            return None

        answer_text = f"{selected_row['dato']}: {selected_row['descripcion']}"

        return {
            "answer": self._finalize_answer(answer_text),
            "sources": [f"contacto_todosystem.csv - fila {int(selected_row.name) + 1}"],
            "contexts": [answer_text],
            "system_prompt": PROMPT_PRINCIPAL,
        }

    def _is_courses_list_question(self, question: str) -> bool:
        question = question.lower()

        patterns = [
            "qué cursos ofrece",
            "que cursos ofrece",
            "cursos ofrece",
            "cursos disponibles",
            "oferta de cursos",
            "lista de cursos",
            "qué cursos tienen",
            "que cursos tienen",
        ]

        return any(pattern in question for pattern in patterns)

    def _answer_courses_list_question(self, question: str) -> dict | None:
        if not self._is_courses_list_question(question):
            return None

        if not COURSES_FILE.exists():
            return None

        df = pd.read_csv(COURSES_FILE)

        lines = ["El Instituto TodoSystem tiene registrados los siguientes cursos:\n"]

        for _, row in df.iterrows():
            lines.append(
                f"- {row['nombre_curso']}: duración {row['duracion']}, "
                f"modalidad {row['modalidad']}, horario {row['horario']}, "
                f"estado {row['estado']}."
            )

        answer_text = "\n".join(lines)

        return {
            "answer": self._finalize_answer(answer_text),
            "sources": ["cursos_todosystem.csv"],
            "contexts": [answer_text],
            "system_prompt": PROMPT_PRINCIPAL,
        }

    def answer(self, question: str) -> dict:
        if not question or not question.strip():
            return {
                "answer": "Por favor, escribe una pregunta para poder ayudarte.",
                "sources": [],
                "contexts": [],
            }

        contact_answer = self._answer_contact_question(question)
        if contact_answer:
            return contact_answer

        courses_answer = self._answer_courses_list_question(question)
        if courses_answer:
            return courses_answer

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

        best_result = results[0]
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

        return {
            "answer": self._finalize_answer(answer_text),
            "sources": self._format_sources([best_result]),
            "contexts": [self._clean_text(item["text"]) for item in results],
            "system_prompt": PROMPT_PRINCIPAL,
        }


if __name__ == "__main__":
    agent = TodoSystemAgent()

    questions = [
        "¿Qué documentos necesito para matricularme?",
        "¿En dónde están ubicados?",
        "¿Cuál es la dirección del instituto?",
        "¿Cuál es el horario de atención?",
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