# Pruebas funcionales - TodoSystem EduBot

Este documento registra las pruebas funcionales realizadas al agente inteligente **TodoSystem EduBot**, desarrollado para el Challenge Alura Agente - ONE AI For Tech.

El objetivo de estas pruebas es validar que el agente pueda responder preguntas en lenguaje natural utilizando la base de conocimiento construida con documentos PDF y CSV.

## Objetivo de las pruebas

Verificar que el agente:

- Responda preguntas sobre información institucional del Instituto TodoSystem.
- Consulte correctamente archivos CSV y PDF.
- Muestre fuentes consultadas.
- No invente información cuando no exista un dato definitivo.
- Recomiende confirmar con el área administrativa cuando sea necesario.

## Base de conocimiento utilizada

La base de conocimiento del agente está compuesta por:

### Archivos CSV

- `data/csv/cursos_todosystem.csv`
- `data/csv/faq_todosystem.csv`
- `data/csv/contacto_todosystem.csv`

### Archivos PDF

- `data/pdfs/guia_matricula_todosystem.pdf`
- `data/pdfs/reglamento_estudiantil_todosystem.pdf`
- `data/pdfs/politica_pagos_reembolsos_todosystem.pdf`

## Pruebas realizadas

| Nº | Pregunta realizada | Resultado esperado | Resultado obtenido | Fuente consultada | Estado |
|---|---|---|---|---|---|
| 1 | ¿Cuál es la dirección del instituto? | El agente debe informar la ubicación general del Instituto TodoSystem y aclarar que es un dato de referencia del proyecto académico. | El agente respondió que el Instituto TodoSystem se encuentra ubicado de forma general en Bugalagrande, Valle del Cauca, Colombia. | `contacto_todosystem.csv` | Aprobado |
| 2 | ¿Qué cursos ofrece el Instituto TodoSystem? | El agente debe listar los cursos registrados en la base de conocimiento. | El agente listó los cursos: Mantenimiento de Computadores, Ofimática Básica, Excel Básico e Intermedio, Diseño Gráfico Básico, Programación Básica y Redes de Computadores. | `cursos_todosystem.csv` | Aprobado |
| 3 | ¿Cuánto cuesta el curso de mantenimiento de computadores? | El agente no debe inventar precios y debe recomendar consultar con el área administrativa. | El agente mostró la información del curso y en el campo valor indicó: “Consultar con el área administrativa”. | `cursos_todosystem.csv` | Aprobado |
| 4 | ¿Qué documentos necesito para matricularme? | El agente debe informar los documentos básicos requeridos para la matrícula. | El agente respondió que se requiere documento de identidad, formulario de inscripción y confirmación de disponibilidad del curso. | `faq_todosystem.csv` | Aprobado |
| 5 | ¿Cuál es el horario de atención? | El agente debe informar el horario de atención registrado en la base de contacto. | El agente respondió que la atención es de lunes a viernes de 8:00 a.m. a 12:00 p.m. y de 2:00 p.m. a 6:00 p.m.; sábados de 8:00 a.m. a 12:00 p.m. | `contacto_todosystem.csv` | Aprobado |

## Validación de control de alucinaciones

Se validó que el agente no inventa información sensible como valores, cupos o dirección exacta.

Ejemplo:

**Pregunta:**  
¿Cuánto cuesta el curso de mantenimiento de computadores?

**Respuesta validada:**  
El agente no entregó un precio inventado. Respondió que el valor debe consultarse con el área administrativa.

Esto demuestra que el agente sigue una regla importante del proyecto: cuando la base de conocimiento no contiene un dato definitivo, debe indicarlo claramente y recomendar confirmación con el área responsable.

## Observaciones

Durante las primeras pruebas, el agente recuperó algunos fragmentos de documentos que no correspondían directamente a preguntas de ubicación o contacto. Para corregirlo, se mejoró la lógica del archivo `app/agent.py`, permitiendo que las preguntas sobre dirección, ubicación, horario, correo o teléfono se respondan directamente desde `contacto_todosystem.csv`.

También se agregó una lógica especial para que las preguntas sobre la oferta de cursos consulten directamente el archivo `cursos_todosystem.csv`.

## Resultado general

Las pruebas funcionales iniciales fueron aprobadas. El agente responde correctamente preguntas básicas sobre:

- Matrícula.
- Dirección y ubicación.
- Horario de atención.
- Cursos disponibles.
- Valores sin inventar precios.
- Fuentes consultadas.

## Próximas pruebas recomendadas

Para futuras versiones se recomienda probar preguntas adicionales como:

- ¿Entregan certificado?
- ¿Puedo pagar por cuotas?
- ¿Puedo matricular a un menor de edad?
- ¿Tienen WhatsApp?
- ¿Qué requisitos tiene el curso de programación básica?
- ¿Qué pasa si no puedo asistir a clase?