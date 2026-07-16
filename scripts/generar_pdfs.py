from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / "docs" / "fuentes"
OUTPUT_DIR = BASE_DIR / "data" / "pdfs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


FILES = {
    "guia_matricula_todosystem.md": "guia_matricula_todosystem.pdf",
    "reglamento_estudiantil_todosystem.md": "reglamento_estudiantil_todosystem.pdf",
    "politica_pagos_reembolsos_todosystem.md": "politica_pagos_reembolsos_todosystem.pdf",
}


def clean_text(text: str) -> str:
    """Limpia caracteres básicos para evitar problemas en el PDF."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def markdown_line_to_paragraph(line: str, styles):
    """Convierte líneas simples de Markdown a elementos de ReportLab."""
    line = line.strip()

    if not line:
        return Spacer(1, 0.12 * inch)

    if line.startswith("# "):
        return Paragraph(clean_text(line.replace("# ", "", 1)), styles["CustomTitle"])

    if line.startswith("## "):
        return Paragraph(clean_text(line.replace("## ", "", 1)), styles["CustomHeading"])

    if line.startswith("- "):
        return Paragraph("• " + clean_text(line.replace("- ", "", 1)), styles["CustomBody"])

    if line[0:2].replace(".", "").isdigit() and ". " in line:
        return Paragraph(clean_text(line), styles["CustomBody"])

    return Paragraph(clean_text(line), styles["CustomBody"])


def generate_pdf(markdown_file: Path, pdf_file: Path):
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="CustomTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_LEFT,
            spaceAfter=16,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CustomHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            spaceBefore=12,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CustomBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            spaceAfter=6,
        )
    )

    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    content = markdown_file.read_text(encoding="utf-8")
    story = []

    for line in content.splitlines():
        story.append(markdown_line_to_paragraph(line, styles))

    doc.build(story)


def main():
    for source_name, output_name in FILES.items():
        source_path = SOURCE_DIR / source_name
        output_path = OUTPUT_DIR / output_name

        if not source_path.exists():
            print(f"No se encontró el archivo fuente: {source_path}")
            continue

        generate_pdf(source_path, output_path)
        print(f"PDF generado: {output_path}")


if __name__ == "__main__":
    main()
    