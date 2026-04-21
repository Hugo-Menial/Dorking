"""Export des résultats en JSON, CSV et PDF."""

import csv
import json
import os
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .search_engine import SearchResult


def export_json(results: dict, output_path: str, meta: dict = None):
    payload = {
        "exported_at": datetime.now().isoformat(),
        "meta": meta or {},
        "engines": {}
    }
    for engine, items in results.items():
        payload["engines"][engine] = [
            {"title": r.title, "url": r.url, "snippet": r.snippet, "timestamp": r.timestamp}
            for r in items
        ]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def export_csv(results: dict, output_path: str):
    rows = []
    for engine, items in results.items():
        for r in items:
            rows.append({
                "engine": engine,
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet,
                "timestamp": r.timestamp
            })
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["engine", "title", "url", "snippet", "timestamp"])
        writer.writeheader()
        writer.writerows(rows)


def export_pdf(results: dict, output_path: str, dork: str = "", meta: dict = None):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
    except ImportError:
        raise ImportError("Installez reportlab : pip install reportlab")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"],
                                  textColor=colors.HexColor("#00D4FF"),
                                  fontSize=18, spaceAfter=6)
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"],
                                textColor=colors.HexColor("#888888"), fontSize=9)
    engine_style = ParagraphStyle("Engine", parent=styles["Heading2"],
                                   textColor=colors.HexColor("#FF6B35"), fontSize=13, spaceBefore=12)
    url_style = ParagraphStyle("URL", parent=styles["Normal"],
                                textColor=colors.HexColor("#00D4FF"), fontSize=8)
    snippet_style = ParagraphStyle("Snippet", parent=styles["Normal"],
                                    textColor=colors.HexColor("#CCCCCC"), fontSize=8)

    story = []
    story.append(Paragraph("Rapport d'Audit OSINT / Dorking", title_style))
    story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}", sub_style))

    if dork:
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(f"<b>Dork :</b> <font color='#FFFF00'>{dork}</font>", sub_style))

    if meta:
        for k, v in meta.items():
            story.append(Paragraph(f"<b>{k} :</b> {v}", sub_style))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#333333")))
    story.append(Spacer(1, 0.5*cm))

    total = sum(len(v) for v in results.values())
    story.append(Paragraph(f"<b>Total résultats :</b> {total}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))

    for engine, items in results.items():
        if not items:
            continue
        story.append(Paragraph(f"{engine} ({len(items)} résultats)", engine_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#444444")))

        for i, r in enumerate(items, 1):
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(f"<b>{i}. {r.title or '(sans titre)'}</b>", styles["Normal"]))
            story.append(Paragraph(r.url, url_style))
            if r.snippet:
                snippet = r.snippet[:300] + "..." if len(r.snippet) > 300 else r.snippet
                story.append(Paragraph(snippet, snippet_style))

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#333333")))
    story.append(Paragraph(
        "⚠️ Rapport généré par Dorking Tool — Usage réservé aux audits de sécurité autorisés.",
        ParagraphStyle("Footer", parent=styles["Normal"],
                       textColor=colors.HexColor("#666666"), fontSize=7, alignment=TA_CENTER)
    ))

    doc.build(story)
