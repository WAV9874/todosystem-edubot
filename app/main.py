import json
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from app.agent import TodoSystemAgent


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "execution_log.jsonl"

LOG_DIR.mkdir(parents=True, exist_ok=True)


def save_log(question: str, answer: str, sources: list[str], response_time: float):
    """
    Guarda un registro básico de ejecución del agente.

    Este log sirve como evidencia de trazabilidad:
    - pregunta realizada
    - respuesta generada
    - fuentes consultadas
    - fecha y hora
    - tiempo de respuesta
    """

    log_data = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "sources": sources,
        "response_time_seconds": round(response_time, 2),
        "status": "answered",
    }

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(log_data, ensure_ascii=False) + "\n")


@st.cache_resource
def load_agent():
    """
    Carga el agente una sola vez para mejorar el rendimiento de la aplicación.
    """
    return TodoSystemAgent()


def main():
    st.set_page_config(
        page_title="TodoSystem EduBot",
        page_icon="🤖",
        layout="centered",
    )

    st.title("🤖 TodoSystem EduBot")

    st.write(
        "Asistente virtual académico del Instituto TodoSystem. "
        "Puedes realizar preguntas sobre cursos, matrículas, requisitos, horarios, pagos, "
        "certificados, reglamento estudiantil y canales de contacto."
    )

    st.info(
        "Este agente responde con base en documentos internos en formato PDF y CSV. "
        "Si no encuentra información suficiente, debe recomendar confirmar con el área administrativa."
    )

    agent = load_agent()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Opciones del agente")

        st.write("Base de conocimiento:")
        st.write("- PDF institucionales")
        st.write("- CSV de cursos, FAQ y contacto")

        if st.button("Reconstruir índice RAG"):
            with st.spinner("Reconstruyendo índice vectorial..."):
                total = agent.rag.build_index()
            st.success(f"Índice reconstruido correctamente con {total} fragmentos.")

        if st.button("Limpiar conversación"):
            st.session_state.messages = []
            st.success("Historial de conversación limpiado.")

        st.divider()
        st.caption("Proyecto desarrollado para el Challenge Alura Agente - ONE AI For Tech.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("Fuentes consultadas"):
                    for source in message["sources"]:
                        st.write(f"- {source}")

    question = st.chat_input("Escribe tu pregunta sobre el Instituto TodoSystem...")

    if question:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
                "sources": [],
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Consultando la base de conocimiento..."):
                start_time = time.time()
                result = agent.answer(question)
                response_time = time.time() - start_time

            answer = result["answer"]
            sources = result["sources"]

            st.markdown(answer)

            if sources:
                with st.expander("Fuentes consultadas"):
                    for source in sources:
                        st.write(f"- {source}")

            save_log(question, answer, sources, response_time)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        )


if __name__ == "__main__":
    main()