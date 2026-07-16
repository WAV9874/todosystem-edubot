# Arquitectura del sistema - TodoSystem EduBot

Este documento describe la arquitectura general del agente inteligente **TodoSystem EduBot**, desarrollado para el Challenge Alura Agente - ONE AI For Tech.

El objetivo de esta arquitectura es permitir que un usuario realice preguntas en lenguaje natural y que el agente responda utilizando una base de conocimiento construida con documentos internos en formato PDF y CSV.

---

## 1. Descripción general

TodoSystem EduBot es un asistente virtual académico para el Instituto TodoSystem.

El sistema permite responder preguntas sobre:

- Cursos disponibles.
- Matrículas.
- Requisitos.
- Horarios.
- Pagos.
- Certificados.
- Dirección y contacto.
- Reglamento estudiantil.
- Procesos académicos básicos.

Para responder, el agente utiliza una arquitectura basada en **RAG**, sigla de *Retrieval Augmented Generation* o recuperación aumentada por generación.

En términos sencillos, RAG significa que el agente no responde únicamente con conocimiento general del modelo, sino que primero busca información en documentos internos y luego genera una respuesta basada en esos documentos.

---

## 2. Componentes principales

La arquitectura del proyecto está compuesta por los siguientes elementos:

| Componente | Descripción |
|---|---|
| Usuario | Persona que realiza preguntas al agente desde la interfaz web. |
| Streamlit | Herramienta utilizada para crear la interfaz web tipo chat. |
| TodoSystemAgent | Clase principal del agente. Recibe preguntas, decide cómo responder y organiza la respuesta final. |
| TodoSystemRAG | Pipeline encargado de leer documentos, crear embeddings, indexar información y recuperar fragmentos relevantes. |
| Base de conocimiento | Conjunto de documentos PDF y CSV con información institucional del Instituto TodoSystem. |
| ChromaDB | Base vectorial utilizada para almacenar embeddings y realizar búsqueda semántica. |
| Sentence Transformers | Modelo usado para convertir textos y preguntas en embeddings. |
| Logs de ejecución | Registro de preguntas, respuestas, fuentes consultadas y tiempo de respuesta. |

---

## 3. Diagrama general de arquitectura

```text
Usuario
  ↓
Interfaz web con Streamlit
  ↓
TodoSystemAgent
  ↓
Clasificación básica de la pregunta
  ├── Preguntas de contacto → contacto_todosystem.csv
  ├── Preguntas de listado de cursos → cursos_todosystem.csv
  └── Otras preguntas → Pipeline RAG
                          ↓
                    TodoSystemRAG
                          ↓
               Búsqueda en ChromaDB
                          ↓
          Fragmentos relevantes PDF / CSV
                          ↓
              Respuesta final con fuentes
                          ↓
                    Usuario