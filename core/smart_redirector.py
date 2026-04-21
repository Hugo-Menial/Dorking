"""
SmartRedirector — Génère un rapport HTML local avec des liens de recherche
organisés par vagues successives pour un audit manuel dans le navigateur.

Deux interfaces disponibles :

    # Classe avec état (organisation data/reports/, nommage automatique)
    sr = SmartRedirector(output_path="data/reports/")
    path = sr.generate_audit_report(dorks_list, target="example.com")

    # Fonctions standalone (compatibilité modules externes)
    path = open_smart_redirector(dorks, title="...", target="...")
    path = save_smart_redirector(dorks, "/path/to/file.html")
"""

import os
import tempfile
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus

from .search_engine import SearchURLBuilder

url_builder = SearchURLBuilder()

# Répertoire de rapports par défaut (créé automatiquement)
_DEFAULT_REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "reports"
)

SEVERITY_ORDER  = ["CRITIQUE", "ÉLEVÉ", "MOYEN", "INFO"]
SEVERITY_COLORS = {
    "CRITIQUE": "#FF4444",
    "ÉLEVÉ":    "#FF6B35",
    "MOYEN":    "#FFD700",
    "INFO":     "#00D4FF",
}
ENGINE_ICONS = {
    "Google":     "🔍",
    "Bing":       "🔷",
    "DuckDuckGo": "🦆",
    "Shodan":     "📡",
}


def _html_escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def _build_search_links(query: str, engines: list[str]) -> str:
    """Génère les boutons de liens pour une requête."""
    urls = url_builder.build_all(query)
    buttons = []
    for engine in engines:
        if engine not in urls:
            continue
        icon = ENGINE_ICONS.get(engine, "🔗")
        url  = urls[engine]
        buttons.append(
            f'<a href="{url}" target="_blank" class="engine-btn engine-{engine.lower().replace(" ", "-")}">'
            f'{icon} {engine}</a>'
        )
    return "\n".join(buttons)


def generate_html_report(
    dorks: list[dict],
    title: str = "Rapport d'Audit OSINT",
    target: str = "",
    engines: list[str] = None,
    group_by_severity: bool = True,
    show_pagination: bool = True,
) -> str:
    """
    Génère le HTML complet du rapport de redirection.

    Chaque dork reçoit des liens pour chaque moteur, avec les paramètres
    d'audit optimaux (num=100, filter=0, safe=off).

    Paramètres
    ----------
    dorks : list[dict]
        Chaque dict : {"dork": str, "description": str, "severity": str, "category": str}
    engines : list[str]
        Moteurs à inclure. Défaut : Google, Bing, DuckDuckGo, Shodan.
    group_by_severity : bool
        Groupe les dorks par niveau de criticité (vagues d'audit).
    show_pagination : bool
        Ajoute des liens de pagination Google (pages 2, 3...).
    """
    if engines is None:
        engines = ["Google", "Bing", "DuckDuckGo", "Shodan"]

    now   = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
    total = len(dorks)

    # Compteurs par sévérité
    counts = {s: sum(1 for d in dorks if d.get("severity") == s) for s in SEVERITY_ORDER}

    # Groupement
    if group_by_severity:
        groups = {}
        for sev in SEVERITY_ORDER:
            group = [d for d in dorks if d.get("severity") == sev]
            if group:
                groups[sev] = group
        ungrouped = [d for d in dorks if d.get("severity") not in SEVERITY_ORDER]
        if ungrouped:
            groups["AUTRE"] = ungrouped
    else:
        groups = {"Tous les dorks": dorks}

    # Construction des cartes HTML
    waves_html = ""
    wave_num = 1
    for group_name, group_dorks in groups.items():
        color = SEVERITY_COLORS.get(group_name, "#888888")
        wave_label = f"Vague {wave_num}" if group_by_severity else ""
        wave_num += 1

        cards_html = ""
        for i, d in enumerate(group_dorks, 1):
            dork_raw    = d.get("dork", "")
            description = d.get("description", "")
            category    = d.get("category", "")
            dork_esc    = _html_escape(dork_raw)
            dork_js     = dork_esc.replace("'", "&#39;")

            links_html = _build_search_links(dork_raw, engines)

            pagination_html = ""
            if show_pagination and "Google" in engines:
                pages = url_builder.paginate_google(dork_raw, pages=3)
                page_links = "".join(
                    f'<a href="{url}" target="_blank" class="page-link">P{j+1}</a>'
                    for j, url in enumerate(pages)
                )
                pagination_html = f'<div class="pagination">Pages : {page_links}</div>'

            cards_html += f"""
<div class="dork-card" id="dork-{i}">
  <div class="dork-header">
    <span class="dork-num">#{i}</span>
    <span class="dork-category">{_html_escape(category)}</span>
    <button class="copy-btn" onclick="copyDork(this, '{dork_js}')">📋</button>
  </div>
  <code class="dork-query">{dork_esc}</code>
  <p class="dork-desc">{_html_escape(description)}</p>
  <div class="engine-links">
    {links_html}
  </div>
  {pagination_html}
</div>"""

        waves_html += f"""
<section class="wave-section">
  <div class="wave-header" style="border-left: 4px solid {color}">
    <span class="severity-badge" style="background:{color};color:#000">{group_name}</span>
    <span class="wave-label">{wave_label}</span>
    <span class="wave-count">{len(group_dorks)} dork(s)</span>
  </div>
  <div class="dork-grid">
    {cards_html}
  </div>
</section>"""

    # Stat badges
    stat_badges = "".join(
        f'<span class="stat-badge" style="border-color:{SEVERITY_COLORS.get(s,"#888")}">'
        f'<b style="color:{SEVERITY_COLORS.get(s,"#888")}">{s}</b> {counts[s]}</span>'
        for s in SEVERITY_ORDER if counts[s] > 0
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html_escape(title)}</title>
<style>
  :root {{
    --bg:       #0D0D0D;
    --panel:    #141414;
    --card:     #1A1A2E;
    --input:    #1E1E2E;
    --accent:   #00D4FF;
    --accent2:  #FF6B35;
    --accent3:  #A855F7;
    --success:  #00FF88;
    --text:     #E0E0E0;
    --dim:      #888888;
    --border:   #2A2A4A;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; }}

  header {{ background: var(--panel); padding: 24px 32px; border-bottom: 1px solid var(--border); }}
  header h1 {{ font-family: Consolas, monospace; font-size: 22px; color: var(--accent); }}
  header .meta {{ font-size: 12px; color: var(--dim); margin-top: 6px; }}
  .stats {{ display: flex; gap: 12px; margin-top: 14px; flex-wrap: wrap; }}
  .stat-badge {{
    border: 1px solid;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 12px;
    font-family: Consolas, monospace;
  }}

  main {{ max-width: 1200px; margin: 0 auto; padding: 24px 20px; }}

  .wave-section {{ margin-bottom: 36px; }}
  .wave-header {{
    display: flex; align-items: center; gap: 12px;
    padding: 10px 16px; background: var(--panel);
    margin-bottom: 12px; border-radius: 4px;
  }}
  .severity-badge {{
    font-family: Consolas, monospace; font-size: 11px; font-weight: bold;
    padding: 3px 10px; border-radius: 3px;
  }}
  .wave-label {{ color: var(--dim); font-size: 12px; }}
  .wave-count  {{ margin-left: auto; color: var(--dim); font-size: 12px; }}

  .dork-grid {{ display: flex; flex-direction: column; gap: 8px; }}
  .dork-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 16px;
  }}
  .dork-card:hover {{ border-color: var(--accent); }}

  .dork-header {{
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 8px;
  }}
  .dork-num      {{ color: var(--dim); font-size: 11px; font-family: Consolas, monospace; min-width: 30px; }}
  .dork-category {{ color: var(--dim); font-size: 11px; flex: 1; }}
  .copy-btn {{
    background: transparent; border: 1px solid var(--border);
    color: var(--dim); cursor: pointer; border-radius: 3px;
    padding: 2px 8px; font-size: 12px;
  }}
  .copy-btn:hover {{ background: var(--input); color: var(--text); }}

  code.dork-query {{
    display: block;
    font-family: Consolas, monospace; font-size: 12px;
    color: var(--accent);
    background: var(--input);
    padding: 8px 12px; border-radius: 4px;
    word-break: break-all;
    margin-bottom: 8px;
  }}
  .dork-desc {{ font-size: 11px; color: var(--dim); margin-bottom: 10px; }}

  .engine-links {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 6px; }}
  .engine-btn {{
    text-decoration: none; font-size: 11px;
    padding: 5px 14px; border-radius: 4px;
    border: 1px solid var(--border);
    color: var(--text); background: var(--input);
    transition: background 0.15s;
  }}
  .engine-btn:hover {{ background: var(--border); color: white; }}
  .engine-google     {{ border-color: #4285f4; color: #4285f4; }}
  .engine-bing       {{ border-color: #00A4EF; color: #00A4EF; }}
  .engine-duckduckgo {{ border-color: #DE5833; color: #DE5833; }}
  .engine-shodan     {{ border-color: #A855F7; color: #A855F7; }}

  .pagination {{ display: flex; align-items: center; gap: 6px; margin-top: 6px; }}
  .pagination {{ font-size: 10px; color: var(--dim); }}
  .page-link {{
    text-decoration: none; color: var(--dim);
    border: 1px solid var(--border);
    padding: 2px 7px; border-radius: 3px; font-size: 10px;
    background: var(--input);
  }}
  .page-link:hover {{ color: var(--accent); border-color: var(--accent); }}

  .copy-toast {{
    position: fixed; bottom: 20px; right: 20px;
    background: var(--success); color: #000;
    padding: 8px 18px; border-radius: 6px;
    font-size: 13px; font-family: Consolas, monospace;
    display: none; z-index: 9999;
  }}
  footer {{
    text-align: center; padding: 20px;
    font-size: 10px; color: var(--dim);
    border-top: 1px solid var(--border);
    margin-top: 40px;
  }}
</style>
</head>
<body>

<header>
  <h1>◈ {_html_escape(title)}</h1>
  <div class="meta">
    Généré le {now}{f" — Cible : <b>{_html_escape(target)}</b>" if target else ""}
    &nbsp;|&nbsp; {total} dork(s) &nbsp;|&nbsp;
    Moteurs : {", ".join(engines)}
  </div>
  <div class="stats">{stat_badges}</div>
</header>

<main>
{waves_html}
</main>

<div class="copy-toast" id="toast">Copié !</div>

<footer>
  Rapport généré par Dorking Tool — Usage réservé aux audits de sécurité autorisés.
  Les liens ouvrent les moteurs dans votre navigateur avec les paramètres d'audit optimaux
  (num=100, filter=0, safe=off).
</footer>

<script>
function copyDork(btn, dork) {{
  navigator.clipboard.writeText(dork).then(() => {{
    const toast = document.getElementById('toast');
    toast.style.display = 'block';
    setTimeout(() => toast.style.display = 'none', 1500);
  }});
}}
</script>
</body>
</html>"""


def open_smart_redirector(
    dorks: list[dict],
    title: str = "Rapport d'Audit OSINT",
    target: str = "",
    engines: list[str] = None,
    output_path: str = "",
) -> str:
    """
    Génère le rapport HTML et l'ouvre dans le navigateur par défaut.

    Retourne le chemin du fichier créé.
    """
    html = generate_html_report(
        dorks=dorks, title=title, target=target, engines=engines
    )

    if not output_path:
        os.makedirs(_DEFAULT_REPORTS_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(_DEFAULT_REPORTS_DIR, f"dorking_audit_{ts}.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    webbrowser.open(f"file:///{output_path.replace(os.sep, '/')}")
    return output_path


def save_smart_redirector(
    dorks: list[dict],
    output_path: str,
    title: str = "Rapport d'Audit OSINT",
    target: str = "",
    engines: list[str] = None,
) -> str:
    """Sauvegarde le rapport HTML sans l'ouvrir."""
    html = generate_html_report(
        dorks=dorks, title=title, target=target, engines=engines
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


class SmartRedirector:
    """
    Interface orientée objet du générateur de rapports HTML.

    Usage :
        sr = SmartRedirector(output_path="data/reports/")
        path = sr.generate_audit_report(dorks_list, target="example.com")

    Compatible avec la signature proposée dans les snippets utilisateur :
        dorks_list = [{"query": "...", "name": "...", "severity": "CRITICAL"}]
    Les clés "query"/"name" sont normalisées vers "dork"/"description"
    pour s'aligner avec le format interne.
    """

    def __init__(self, output_path: str = ""):
        self.output_path = output_path or _DEFAULT_REPORTS_DIR
        os.makedirs(self.output_path, exist_ok=True)

    def generate_audit_report(
        self,
        dorks_list: list[dict],
        target: str = "",
        open_browser: bool = True,
        engines: list[str] = None,
    ) -> str:
        """
        Génère et (optionnellement) ouvre le rapport HTML d'audit.

        Accepte les formats de dork suivants :
            {"dork": "...", "description": "...", "severity": "CRITIQUE"}   # format interne
            {"query": "...", "name": "...", "severity": "CRITICAL"}          # format snippet
        """
        normalized = []
        for d in dorks_list:
            normalized.append({
                "dork":        d.get("dork") or d.get("query", ""),
                "description": d.get("description") or d.get("name", ""),
                "severity":    self._normalize_severity(d.get("severity", "INFO")),
                "category":    d.get("category", ""),
            })

        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug     = target.replace(".", "_").replace(":", "_") if target else "audit"
        filename = f"audit_{slug}_{ts}.html"
        path     = os.path.join(self.output_path, filename)

        save_smart_redirector(normalized, path,
                               title=f"Audit OSINT{f' — {target}' if target else ''}",
                               target=target, engines=engines)

        if open_browser:
            webbrowser.open(f"file:///{path.replace(os.sep, '/')}")

        return path

    def list_reports(self) -> list[str]:
        """Retourne les rapports HTML générés, du plus récent au plus ancien."""
        try:
            files = [
                os.path.join(self.output_path, f)
                for f in os.listdir(self.output_path)
                if f.endswith(".html")
            ]
            return sorted(files, key=os.path.getmtime, reverse=True)
        except FileNotFoundError:
            return []

    @staticmethod
    def _normalize_severity(sev: str) -> str:
        """Mappe les sévérités anglaises vers le format interne français."""
        mapping = {
            "CRITICAL": "CRITIQUE",
            "HIGH":     "ÉLEVÉ",  # ÉLEVÉ (unicode escape)
            "MEDIUM":   "MOYEN",
            "LOW":      "INFO",
        }
        return mapping.get(sev.upper(), sev)
