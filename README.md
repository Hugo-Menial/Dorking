<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Dorking Tool — OSINT & Security Research</title>
  <style>
    :root {
      --bg:       #0D0D0D;
      --panel:    #141414;
      --card:     #1A1A2E;
      --input:    #1E1E2E;
      --accent:   #00D4FF;
      --accent2:  #FF6B35;
      --accent3:  #A855F7;
      --green:    #00FF88;
      --yellow:   #FFD700;
      --red:      #FF4444;
      --text:     #E0E0E0;
      --dim:      #888888;
      --border:   #2A2A4A;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Segoe UI', system-ui, sans-serif;
      line-height: 1.6;
      overflow-x: hidden;
    }

    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }

    code, pre, .mono {
      font-family: 'Consolas', 'Cascadia Code', monospace;
    }

    /* ── HERO ──────────────────────────────────────────────────── */
    .hero {
      position: relative;
      background: linear-gradient(135deg, #0D0D0D 0%, #0D1A2E 50%, #1A0D2E 100%);
      padding: 80px 40px 60px;
      text-align: center;
      overflow: hidden;
      border-bottom: 1px solid var(--border);
    }

    .hero::before {
      content: '';
      position: absolute;
      inset: 0;
      background:
        radial-gradient(ellipse 60% 40% at 20% 50%, rgba(0,212,255,.07) 0%, transparent 70%),
        radial-gradient(ellipse 50% 40% at 80% 50%, rgba(168,85,247,.07) 0%, transparent 70%);
      pointer-events: none;
    }

    .grid-overlay {
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(rgba(0,212,255,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,.03) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
    }

    .hero-logo {
      font-family: 'Consolas', monospace;
      font-size: 3.6rem;
      font-weight: 900;
      letter-spacing: .12em;
      background: linear-gradient(135deg, var(--accent), var(--accent3));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 8px;
    }

    .hero-logo span { color: var(--accent2); -webkit-text-fill-color: var(--accent2); }

    .hero-tagline {
      font-size: 1.18rem;
      color: var(--dim);
      letter-spacing: .04em;
      margin-bottom: 28px;
    }

    .badge-row {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 10px;
      margin-bottom: 38px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 5px 14px;
      border-radius: 20px;
      font-size: .78rem;
      font-weight: 600;
      letter-spacing: .03em;
      border: 1px solid;
    }

    .badge-blue   { background: rgba(0,212,255,.1);  border-color: rgba(0,212,255,.3);  color: var(--accent);  }
    .badge-purple { background: rgba(168,85,247,.1); border-color: rgba(168,85,247,.3); color: var(--accent3); }
    .badge-orange { background: rgba(255,107,53,.1); border-color: rgba(255,107,53,.3); color: var(--accent2); }
    .badge-green  { background: rgba(0,255,136,.1);  border-color: rgba(0,255,136,.3);  color: var(--green);   }
    .badge-yellow { background: rgba(255,215,0,.1);  border-color: rgba(255,215,0,.3);  color: var(--yellow);  }
    .badge-red    { background: rgba(255,68,68,.1);  border-color: rgba(255,68,68,.3);  color: var(--red);     }

    .btn-primary {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 13px 30px;
      background: var(--accent);
      color: #000;
      font-weight: 700;
      font-size: .95rem;
      border-radius: 8px;
      transition: background .2s, transform .15s;
    }
    .btn-primary:hover { background: #00A8CC; transform: translateY(-2px); text-decoration: none; }

    .btn-ghost {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 13px 30px;
      background: transparent;
      color: var(--text);
      font-weight: 600;
      font-size: .95rem;
      border-radius: 8px;
      border: 1px solid var(--border);
      transition: border-color .2s, transform .15s;
    }
    .btn-ghost:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-2px); text-decoration: none; }

    /* ── LAYOUT ────────────────────────────────────────────────── */
    .container { max-width: 1100px; margin: 0 auto; padding: 0 32px; }

    section { padding: 64px 0; border-bottom: 1px solid var(--border); }
    section:last-child { border-bottom: none; }

    .section-label {
      font-family: 'Consolas', monospace;
      font-size: .8rem;
      letter-spacing: .15em;
      color: var(--dim);
      text-transform: uppercase;
      margin-bottom: 8px;
    }

    .section-title {
      font-size: 2rem;
      font-weight: 800;
      margin-bottom: 12px;
    }

    .section-sub {
      font-size: 1rem;
      color: var(--dim);
      margin-bottom: 40px;
      max-width: 620px;
    }

    /* ── UI MOCKUP ─────────────────────────────────────────────── */
    .mockup-wrap {
      position: relative;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--border);
      box-shadow: 0 24px 80px rgba(0,212,255,.08), 0 8px 30px rgba(0,0,0,.6);
      background: var(--panel);
      max-width: 860px;
      margin: 0 auto 20px;
    }

    .mockup-bar {
      background: #1A1A1A;
      padding: 12px 16px;
      display: flex;
      align-items: center;
      gap: 8px;
      border-bottom: 1px solid var(--border);
    }

    .dot { width: 12px; height: 12px; border-radius: 50%; }
    .dot-r { background: #FF5F57; }
    .dot-y { background: #FEBC2E; }
    .dot-g { background: #28C840; }

    .mockup-title {
      font-family: 'Consolas', monospace;
      font-size: .8rem;
      color: var(--dim);
      margin-left: 8px;
    }

    .mockup-body {
      display: flex;
      height: 380px;
      font-family: 'Consolas', monospace;
      font-size: .82rem;
    }

    .mock-sidebar {
      width: 180px;
      background: var(--panel);
      border-right: 1px solid var(--border);
      padding: 16px 8px;
      flex-shrink: 0;
    }

    .mock-logo {
      color: var(--accent);
      font-weight: 900;
      font-size: .95rem;
      padding: 0 8px 12px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 12px;
      letter-spacing: .08em;
    }

    .mock-nav-item {
      padding: 8px 10px;
      border-radius: 6px;
      color: var(--dim);
      font-size: .78rem;
      margin-bottom: 2px;
      cursor: default;
    }

    .mock-nav-item.active {
      background: var(--card);
      color: var(--accent);
    }

    .mock-main {
      flex: 1;
      padding: 20px 24px;
      overflow: hidden;
    }

    .mock-header-title {
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 4px;
    }

    .mock-header-sub { color: var(--dim); font-size: .72rem; margin-bottom: 16px; }

    .mock-input-wrap {
      background: var(--input);
      border: 1px solid var(--accent);
      border-radius: 6px;
      padding: 10px 14px;
      color: var(--text);
      font-size: .8rem;
      margin-bottom: 10px;
    }

    .mock-tag {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: .68rem;
      margin-right: 4px;
      margin-bottom: 6px;
    }

    .mock-ops {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin-bottom: 14px;
    }

    .mock-op {
      background: var(--input);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 4px 9px;
      font-size: .72rem;
      color: var(--accent);
    }

    .mock-btn-row { display: flex; gap: 8px; }

    .mock-btn {
      padding: 7px 14px;
      border-radius: 5px;
      font-size: .75rem;
      font-weight: 600;
    }

    .mock-btn-a { background: var(--accent);  color: #000; }
    .mock-btn-b { background: var(--accent3); color: #fff; }
    .mock-btn-c { background: var(--accent2); color: #fff; }
    .mock-btn-d { background: var(--input);   color: var(--dim); border: 1px solid var(--border); }

    /* ── FEATURES GRID ─────────────────────────────────────────── */
    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
    }

    .feature-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 26px 24px;
      transition: border-color .2s, transform .15s;
    }

    .feature-card:hover {
      border-color: var(--accent);
      transform: translateY(-3px);
    }

    .feature-icon {
      font-size: 1.8rem;
      margin-bottom: 12px;
    }

    .feature-title {
      font-size: 1.05rem;
      font-weight: 700;
      margin-bottom: 8px;
      color: var(--text);
    }

    .feature-desc {
      font-size: .9rem;
      color: var(--dim);
      line-height: 1.65;
    }

    .feature-tag {
      display: inline-block;
      margin-top: 12px;
      font-family: 'Consolas', monospace;
      font-size: .72rem;
      color: var(--accent);
      background: rgba(0,212,255,.08);
      border: 1px solid rgba(0,212,255,.2);
      padding: 2px 9px;
      border-radius: 10px;
    }

    /* ── TABS SHOWCASE ─────────────────────────────────────────── */
    .tabs-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }

    @media (max-width: 768px) { .tabs-grid { grid-template-columns: repeat(2, 1fr); } }

    .tab-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px 18px;
      text-align: center;
    }

    .tab-card .icon { font-size: 1.6rem; margin-bottom: 8px; }
    .tab-card .name { font-family: 'Consolas', monospace; font-size: .9rem; color: var(--accent); font-weight: 700; margin-bottom: 5px; }
    .tab-card .desc { font-size: .8rem; color: var(--dim); }

    /* ── CODE BLOCK ────────────────────────────────────────────── */
    .code-block {
      background: #0A0A0A;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
    }

    .code-block-header {
      background: var(--panel);
      padding: 10px 16px;
      font-family: 'Consolas', monospace;
      font-size: .8rem;
      color: var(--dim);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .code-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--border); }

    pre {
      padding: 20px 24px;
      overflow-x: auto;
      font-size: .88rem;
      line-height: 1.7;
    }

    .c-comment { color: #555; }
    .c-cmd     { color: var(--accent); }
    .c-str     { color: var(--green); }
    .c-kw      { color: var(--accent3); }
    .c-num     { color: var(--yellow); }
    .c-path    { color: var(--accent2); }

    /* ── STACK TABLE ───────────────────────────────────────────── */
    .stack-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 14px;
    }

    .stack-item {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px 18px;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .stack-item .s-icon { font-size: 1.4rem; }
    .stack-item .s-name { font-weight: 600; font-size: .9rem; color: var(--text); }
    .stack-item .s-role { font-size: .76rem; color: var(--dim); }

    /* ── OPERATORS TABLE ───────────────────────────────────────── */
    .op-table { width: 100%; border-collapse: collapse; }
    .op-table th {
      background: var(--input);
      padding: 10px 14px;
      text-align: left;
      font-family: 'Consolas', monospace;
      font-size: .8rem;
      color: var(--dim);
      text-transform: uppercase;
      letter-spacing: .06em;
      border-bottom: 1px solid var(--border);
    }
    .op-table td {
      padding: 10px 14px;
      border-bottom: 1px solid rgba(42,42,74,.5);
      font-size: .88rem;
      vertical-align: middle;
    }
    .op-table tr:last-child td { border-bottom: none; }
    .op-table tr:hover td { background: rgba(255,255,255,.02); }
    .op-syntax {
      font-family: 'Consolas', monospace;
      color: var(--accent);
      font-size: .85rem;
    }
    .op-ex {
      font-family: 'Consolas', monospace;
      color: var(--dim);
      font-size: .78rem;
    }

    /* ── SEVERITY SECTION ──────────────────────────────────────── */
    .sev-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
    }
    @media (max-width: 600px) { .sev-grid { grid-template-columns: repeat(2, 1fr); } }

    .sev-card {
      padding: 18px 16px;
      border-radius: 8px;
      border: 1px solid;
      text-align: center;
    }
    .sev-card .s-label { font-weight: 700; font-size: .9rem; margin-bottom: 5px; font-family: 'Consolas', monospace; }
    .sev-card .s-desc  { font-size: .78rem; opacity: .75; }

    /* ── INSTALL STEPS ─────────────────────────────────────────── */
    .steps { display: flex; flex-direction: column; gap: 16px; }

    .step {
      display: flex;
      gap: 18px;
      align-items: flex-start;
    }

    .step-num {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: rgba(0,212,255,.1);
      border: 1px solid rgba(0,212,255,.3);
      color: var(--accent);
      font-weight: 700;
      font-size: .9rem;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      margin-top: 2px;
    }

    .step-content h4 { font-size: .95rem; margin-bottom: 4px; }
    .step-content p  { font-size: .85rem; color: var(--dim); }
    .step-content code {
      background: var(--input);
      padding: 2px 7px;
      border-radius: 4px;
      font-size: .82rem;
      color: var(--accent);
    }

    /* ── LEGAL WARNING ─────────────────────────────────────────── */
    .legal-box {
      background: #1A0A00;
      border: 1px solid rgba(255,215,0,.3);
      border-radius: 10px;
      padding: 24px 28px;
      display: flex;
      gap: 18px;
      align-items: flex-start;
    }

    .legal-icon { font-size: 1.8rem; flex-shrink: 0; }
    .legal-title { font-weight: 700; font-size: 1rem; color: var(--yellow); margin-bottom: 8px; }
    .legal-text  { font-size: .88rem; color: #BBAA88; line-height: 1.7; }

    /* ── FOOTER ────────────────────────────────────────────────── */
    .footer {
      background: var(--panel);
      border-top: 1px solid var(--border);
      padding: 36px 40px;
      text-align: center;
      font-size: .85rem;
      color: var(--dim);
    }

    .footer-logo {
      font-family: 'Consolas', monospace;
      font-size: 1.1rem;
      color: var(--accent);
      font-weight: 700;
      margin-bottom: 8px;
    }

    /* ── DIVIDER ───────────────────────────────────────────────── */
    .divider {
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--border), transparent);
      margin: 40px 0;
    }

    /* ── RESPONSIVE ────────────────────────────────────────────── */
    @media (max-width: 700px) {
      .hero-logo { font-size: 2.2rem; }
      .mockup-body { height: auto; flex-direction: column; }
      .mock-sidebar { width: 100%; height: auto; border-right: none; border-bottom: 1px solid var(--border); }
      .tabs-grid { grid-template-columns: repeat(2, 1fr); }
      .sev-grid  { grid-template-columns: repeat(2, 1fr); }
      section { padding: 44px 0; }
    }
  </style>
</head>
<body>

<!-- ═══════════════════════════════════════════════════ HERO -->
<header class="hero">
  <div class="grid-overlay"></div>

  <div style="position:relative; z-index:1;">
    <div class="hero-logo">◈ DORKING<span>.</span></div>
    <p class="hero-tagline">OSINT &amp; Security Research Platform &nbsp;·&nbsp; Google Dork Builder &nbsp;·&nbsp; Multi-Engine &nbsp;·&nbsp; Claude AI</p>

    <div class="badge-row">
      <span class="badge badge-blue">🐍 Python 3.10+</span>
      <span class="badge badge-purple">🖥 CustomTkinter</span>
      <span class="badge badge-orange">🤖 Claude AI</span>
      <span class="badge badge-green">🔍 Multi-Engine Search</span>
      <span class="badge badge-yellow">👁 Watchdog</span>
      <span class="badge badge-red">⚠️ Audit autorisé uniquement</span>
    </div>

    <div style="display:flex; gap:14px; justify-content:center; flex-wrap:wrap;">
      <a href="#install" class="btn-primary">⬇ Installation</a>
      <a href="#features" class="btn-ghost">✦ Fonctionnalités</a>
    </div>
  </div>
</header>


<!-- ═══════════════════════════════════════════════════ MOCKUP UI -->
<section>
  <div class="container">
    <div class="section-label">Interface</div>
    <h2 class="section-title">Application desktop <span style="color:var(--accent)">dark-mode</span></h2>
    <p class="section-sub">Interface native Python avec thème cybersécurité, entièrement offline — aucune donnée envoyée sans votre consentement.</p>

    <div class="mockup-wrap">
      <div class="mockup-bar">
        <div class="dot dot-r"></div>
        <div class="dot dot-y"></div>
        <div class="dot dot-g"></div>
        <span class="mockup-title">Dorking Tool — OSINT &amp; Security Research</span>
      </div>
      <div class="mockup-body">
        <div class="mock-sidebar">
          <div class="mock-logo">◈ DORKING</div>
          <div class="mock-nav-item active">🔍  Dork Builder</div>
          <div class="mock-nav-item">📚  Bibliothèque</div>
          <div class="mock-nav-item">🔣  Opérateurs</div>
          <div class="mock-nav-item">📖  Wiki</div>
          <div class="mock-nav-item">🤖  IA Suggest</div>
          <div class="mock-nav-item">👁  Watchdog</div>
          <div class="mock-nav-item">📊  Résultats</div>
          <div class="mock-nav-item">⚙️  Paramètres</div>
        </div>
        <div class="mock-main">
          <div class="mock-header-title">Dork Builder</div>
          <div class="mock-header-sub">Construisez et exécutez des requêtes avancées</div>
          <div class="mock-input-wrap mono">site:example.com filetype:sql "password"</div>
          <div style="margin-bottom:10px;">
            <span class="mock-tag badge badge-green" style="font-size:.7rem;">✓ Valide</span>
            <span class="mock-tag" style="background:rgba(0,212,255,.08);color:var(--dim);font-size:.7rem;border-radius:10px;padding:2px 8px;">Opérateurs: site, filetype &nbsp;·&nbsp; Complexité: 2</span>
          </div>
          <div class="mock-ops">
            <span class="mock-op">site:</span>
            <span class="mock-op">filetype:</span>
            <span class="mock-op">intitle:</span>
            <span class="mock-op">inurl:</span>
            <span class="mock-op">intext:</span>
            <span class="mock-op">AROUND(N)</span>
            <span class="mock-op">"phrase"</span>
            <span class="mock-op">-mot</span>
            <span class="mock-op">OR</span>
          </div>
          <div class="mock-btn-row">
            <span class="mock-btn mock-btn-a">▶ Rechercher</span>
            <span class="mock-btn mock-btn-b">🌐 Navigateur</span>
            <span class="mock-btn mock-btn-c">📄 Rapport HTML</span>
            <span class="mock-btn mock-btn-d">📋 Copier</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>


<!-- ═══════════════════════════════════════════════════ FEATURES -->
<section id="features">
  <div class="container">
    <div class="section-label">Fonctionnalités</div>
    <h2 class="section-title">Tout ce dont vous avez besoin pour l'<span style="color:var(--accent3)">OSINT</span></h2>
    <p class="section-sub">Du constructeur visuel aux alertes automatiques, Dorking Tool couvre l'intégralité du workflow d'un audit de reconnaissance.</p>

    <div class="features-grid">

      <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Dork Builder visuel</div>
        <div class="feature-desc">Constructeur bloc-par-bloc avec validation en temps réel, auto-quoting des espaces, opérateurs rapides et support de la négation (NOT) par champ.</div>
        <span class="feature-tag">DorkBuilder + DorkQuery</span>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🌐</div>
        <div class="feature-title">Recherche multi-moteurs</div>
        <div class="feature-desc">Google CSE, Bing Web Search API, DuckDuckGo (ddgs) et Shodan — tous en parallèle via une file de priorité non-bloquante. Rate-limiting adaptatif avec exponential backoff.</div>
        <span class="feature-tag">SearchQueue + AdaptiveRateLimiter</span>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">Génération IA — Claude</div>
        <div class="feature-desc">Génère des dorks contextuels via Claude (claude-sonnet-4-6). Prompt enrichi avec les fichiers, CVEs et expositions propres à 7 stacks techniques (WordPress, AWS, Django, Node.js…).</div>
        <span class="feature-tag">Anthropic API · Stack Intel</span>
      </div>

      <div class="feature-card">
        <div class="feature-icon">👁</div>
        <div class="feature-title">Watchdog — Surveillance continue</div>
        <div class="feature-desc">Planifiez des scans automatiques à intervalle personnalisé. Détection des nouveaux résultats par hash SHA-256 stable. Alertes Discord webhook et HTTP avec jitter ±10%.</div>
        <span class="feature-tag">WatchdogManager · Threading</span>
      </div>

      <div class="feature-card">
        <div class="feature-icon">📄</div>
        <div class="feature-title">Rapports HTML — SmartRedirector</div>
        <div class="feature-desc">Génère des rapports d'audit HTML dark-mode avec groupement par sévérité (CRITIQUE → INFO), liens Google paginés (P1/P2/P3), bouton copier et multi-moteurs en un clic.</div>
        <span class="feature-tag">SmartRedirector · HTML auto-open</span>
      </div>

      <div class="feature-card">
        <div class="feature-icon">📚</div>
        <div class="feature-title">Bibliothèque + Wiki intégré</div>
        <div class="feature-desc">~40 dorks préconstruits en 6 catégories avec sévérité et tags. Wiki interactif documentant 18+ opérateurs avec exemples, tips OSINT et boutons Try qui injectent dans le builder.</div>
        <span class="feature-tag">dork_library.json · 5 sections</span>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🔐</div>
        <div class="feature-title">Stockage sécurisé des clés</div>
        <div class="feature-desc">Les clés API sont stockées dans le trousseau OS (Windows Credential Manager via keyring). Fallback JSON avec avertissement si le trousseau est indisponible.</div>
        <span class="feature-tag">keyring · WinVaultKeyring</span>
      </div>

      <div class="feature-card">
        <div class="feature-icon">↓</div>
        <div class="feature-title">Export multi-format</div>
        <div class="feature-desc">Exportez vos résultats en JSON structuré, CSV tabulaire, PDF mise en page professionnelle (ReportLab) ou rapport HTML interactif SmartRedirector.</div>
        <span class="feature-tag">JSON · CSV · PDF · HTML</span>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🌐</div>
        <div class="feature-title">Open in Browser — Human View</div>
        <div class="feature-desc">Ouvre la requête dans votre navigateur réel (Google, Bing, DDG) avec les paramètres d'audit optimaux : num=100, filter=0, safe=off. Ce que vous voyez = ce qu'un humain voit.</div>
        <span class="feature-tag">SearchURLBuilder · webbrowser</span>
      </div>

    </div>
  </div>
</section>


<!-- ═══════════════════════════════════════════════════ TABS -->
<section>
  <div class="container">
    <div class="section-label">Navigation</div>
    <h2 class="section-title">8 onglets, <span style="color:var(--accent)">un workflow complet</span></h2>
    <p class="section-sub">Chaque onglet couvre une étape distincte du workflow OSINT, de la construction à l'alerte.</p>

    <div class="tabs-grid">
      <div class="tab-card">
        <div class="icon">🔍</div>
        <div class="name">Dork Builder</div>
        <div class="desc">Construction visuelle, validation live, opérateurs rapides</div>
      </div>
      <div class="tab-card">
        <div class="icon">📚</div>
        <div class="name">Bibliothèque</div>
        <div class="desc">~40 dorks préconstruits, filtre, rapport HTML complet</div>
      </div>
      <div class="tab-card">
        <div class="icon">🔣</div>
        <div class="name">Opérateurs</div>
        <div class="desc">16 opérateurs référencés avec syntaxe et exemples</div>
      </div>
      <div class="tab-card">
        <div class="icon">📖</div>
        <div class="name">Wiki</div>
        <div class="desc">Documentation complète, tips OSINT, recettes par scénario</div>
      </div>
      <div class="tab-card">
        <div class="icon">🤖</div>
        <div class="name">IA Suggest</div>
        <div class="desc">Génération Claude AI avec contexte stack technique</div>
      </div>
      <div class="tab-card">
        <div class="icon">👁</div>
        <div class="name">Watchdog</div>
        <div class="desc">Surveillance planifiée avec alertes Discord</div>
      </div>
      <div class="tab-card">
        <div class="icon">📊</div>
        <div class="name">Résultats</div>
        <div class="desc">Live console, résultats multi-moteurs, export</div>
      </div>
      <div class="tab-card">
        <div class="icon">⚙️</div>
        <div class="name">Paramètres</div>
        <div class="desc">Clés API sécurisées, moteurs, keyring status</div>
      </div>
    </div>
  </div>
</section>


<!-- ═══════════════════════════════════════════════════ OPERATORS -->
<section>
  <div class="container">
    <div class="section-label">Référence</div>
    <h2 class="section-title">Opérateurs <span style="color:var(--accent)">Google Dork</span> supportés</h2>
    <p class="section-sub">Tous les opérateurs reconnus, validés et documentés dans l'interface.</p>

    <div class="code-block">
      <table class="op-table">
        <thead>
          <tr>
            <th>Opérateur</th>
            <th>Usage</th>
            <th>Exemple</th>
            <th>Catégorie</th>
          </tr>
        </thead>
        <tbody>
          <tr><td class="op-syntax">site:</td><td>Restreindre au domaine</td><td class="op-ex">site:example.com</td><td><span class="badge badge-blue" style="font-size:.7rem;">Portée</span></td></tr>
          <tr><td class="op-syntax">filetype:</td><td>Filtrer par extension</td><td class="op-ex">filetype:sql</td><td><span class="badge badge-blue" style="font-size:.7rem;">Portée</span></td></tr>
          <tr><td class="op-syntax">intitle:</td><td>Texte dans le &lt;title&gt;</td><td class="op-ex">intitle:"index of"</td><td><span class="badge badge-purple" style="font-size:.7rem;">Contenu</span></td></tr>
          <tr><td class="op-syntax">inurl:</td><td>Texte dans l'URL</td><td class="op-ex">inurl:admin</td><td><span class="badge badge-purple" style="font-size:.7rem;">Contenu</span></td></tr>
          <tr><td class="op-syntax">intext:</td><td>Texte dans le corps</td><td class="op-ex">intext:"password="</td><td><span class="badge badge-purple" style="font-size:.7rem;">Contenu</span></td></tr>
          <tr><td class="op-syntax">cache:</td><td>Version en cache Google</td><td class="op-ex">cache:example.com</td><td><span class="badge badge-blue" style="font-size:.7rem;">Portée</span></td></tr>
          <tr><td class="op-syntax">related:</td><td>Sites similaires</td><td class="op-ex">related:github.com</td><td><span class="badge badge-blue" style="font-size:.7rem;">Portée</span></td></tr>
          <tr><td class="op-syntax">AROUND(N)</td><td>Proximité de N mots</td><td class="op-ex">password AROUND(3) user</td><td><span class="badge badge-yellow" style="font-size:.7rem;">Logique</span></td></tr>
          <tr><td class="op-syntax">"phrase"</td><td>Correspondance exacte</td><td class="op-ex">"BEGIN RSA PRIVATE KEY"</td><td><span class="badge badge-yellow" style="font-size:.7rem;">Logique</span></td></tr>
          <tr><td class="op-syntax">-mot</td><td>Exclure un terme</td><td class="op-ex">-intext:sample</td><td><span class="badge badge-yellow" style="font-size:.7rem;">Logique</span></td></tr>
          <tr><td class="op-syntax">OR</td><td>Union logique</td><td class="op-ex">filetype:sql OR filetype:db</td><td><span class="badge badge-yellow" style="font-size:.7rem;">Logique</span></td></tr>
          <tr><td class="op-syntax">allintitle:</td><td>Tous les mots dans le titre</td><td class="op-ex">allintitle:admin panel</td><td><span class="badge badge-purple" style="font-size:.7rem;">Contenu</span></td></tr>
          <tr><td class="op-syntax">allinurl:</td><td>Tous les mots dans l'URL</td><td class="op-ex">allinurl:admin login</td><td><span class="badge badge-purple" style="font-size:.7rem;">Contenu</span></td></tr>
          <tr><td class="op-syntax">ext:</td><td>Alias strict de filetype:</td><td class="op-ex">ext:env</td><td><span class="badge badge-blue" style="font-size:.7rem;">Portée</span></td></tr>
          <tr><td class="op-syntax">info:</td><td>Informations Google sur l'URL</td><td class="op-ex">info:example.com</td><td><span class="badge badge-blue" style="font-size:.7rem;">Portée</span></td></tr>
          <tr><td class="op-syntax">*</td><td>Wildcard (dans les guillemets)</td><td class="op-ex">"Bearer *"</td><td><span class="badge badge-yellow" style="font-size:.7rem;">Logique</span></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>


<!-- ═══════════════════════════════════════════════════ SEVERITY -->
<section>
  <div class="container">
    <div class="section-label">Classification</div>
    <h2 class="section-title">Niveaux de <span style="color:var(--red)">sévérité</span></h2>
    <p class="section-sub">Chaque dork est classé selon son potentiel d'exposition. Les rapports HTML sont groupés par niveau.</p>

    <div class="sev-grid">
      <div class="sev-card" style="background:rgba(255,68,68,.06); border-color:rgba(255,68,68,.3); color:var(--red);">
        <div class="s-label">CRITIQUE</div>
        <div class="s-desc">Credentials, clés privées, bases de données exposées</div>
      </div>
      <div class="sev-card" style="background:rgba(255,107,53,.06); border-color:rgba(255,107,53,.3); color:var(--accent2);">
        <div class="s-label">ÉLEVÉ</div>
        <div class="s-desc">Panneaux admin, fichiers de config, backups</div>
      </div>
      <div class="sev-card" style="background:rgba(255,215,0,.06); border-color:rgba(255,215,0,.3); color:var(--yellow);">
        <div class="s-label">MOYEN</div>
        <div class="s-desc">Documents internes, répertoires, stack traces</div>
      </div>
      <div class="sev-card" style="background:rgba(0,212,255,.06); border-color:rgba(0,212,255,.3); color:var(--accent);">
        <div class="s-label">INFO</div>
        <div class="s-desc">Reconnaissance générale, cartographie de surface</div>
      </div>
    </div>
  </div>
</section>


<!-- ═══════════════════════════════════════════════════ STACK -->
<section>
  <div class="container">
    <div class="section-label">Stack technique</div>
    <h2 class="section-title">Technologies <span style="color:var(--accent3)">utilisées</span></h2>
    <p class="section-sub">Entièrement construit en Python, sans dépendances lourdes — fonctionne sur Windows, macOS et Linux.</p>

    <div class="stack-grid">
      <div class="stack-item">
        <div class="s-icon">🐍</div>
        <div>
          <div class="s-name">Python 3.10+</div>
          <div class="s-role">Langage principal</div>
        </div>
      </div>
      <div class="stack-item">
        <div class="s-icon">🖥</div>
        <div>
          <div class="s-name">CustomTkinter</div>
          <div class="s-role">Interface graphique desktop</div>
        </div>
      </div>
      <div class="stack-item">
        <div class="s-icon">🤖</div>
        <div>
          <div class="s-name">Anthropic SDK</div>
          <div class="s-role">Génération IA (Claude)</div>
        </div>
      </div>
      <div class="stack-item">
        <div class="s-icon">🌊</div>
        <div>
          <div class="s-name">ddgs</div>
          <div class="s-role">DuckDuckGo Search</div>
        </div>
      </div>
      <div class="stack-item">
        <div class="s-icon">📡</div>
        <div>
          <div class="s-name">Shodan</div>
          <div class="s-role">Recherche IoT / infra</div>
        </div>
      </div>
      <div class="stack-item">
        <div class="s-icon">🔐</div>
        <div>
          <div class="s-name">keyring</div>
          <div class="s-role">Stockage sécurisé des clés</div>
        </div>
      </div>
      <div class="stack-item">
        <div class="s-icon">📊</div>
        <div>
          <div class="s-name">ReportLab</div>
          <div class="s-role">Export PDF</div>
        </div>
      </div>
      <div class="stack-item">
        <div class="s-icon">🔗</div>
        <div>
          <div class="s-name">requests</div>
          <div class="s-role">HTTP / webhooks</div>
        </div>
      </div>
    </div>
  </div>
</section>


<!-- ═══════════════════════════════════════════════════ INSTALL -->
<section id="install">
  <div class="container">
    <div class="section-label">Démarrage rapide</div>
    <h2 class="section-title">Installation en <span style="color:var(--green)">3 étapes</span></h2>
    <p class="section-sub">Aucune configuration complexe — un batch lance tout automatiquement sur Windows.</p>

    <div class="steps" style="margin-bottom:32px;">
      <div class="step">
        <div class="step-num">1</div>
        <div class="step-content">
          <h4>Cloner le dépôt</h4>
          <p><code>git clone https://github.com/votre-user/dorking-tool.git</code></p>
        </div>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-content">
          <h4>Installer les dépendances</h4>
          <p>Double-cliquer sur <code>installer.bat</code> — installe automatiquement toutes les dépendances Python.</p>
        </div>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-content">
          <h4>Lancer l'application</h4>
          <p>Double-cliquer sur <code>lancer.bat</code> — l'interface s'ouvre directement.</p>
        </div>
      </div>
    </div>

    <div class="code-block">
      <div class="code-block-header">
        <div class="code-dot"></div>
        <div class="code-dot"></div>
        <div class="code-dot"></div>
        &nbsp; Installation manuelle
      </div>
      <pre><span class="c-comment"># Cloner</span>
<span class="c-cmd">git clone</span> <span class="c-str">https://github.com/votre-user/dorking-tool.git</span>
<span class="c-cmd">cd</span> <span class="c-path">dorking-tool</span>

<span class="c-comment"># Environnement virtuel (recommandé)</span>
<span class="c-cmd">python</span> -m venv .venv
<span class="c-path">.venv\Scripts\activate</span>   <span class="c-comment"># Windows</span>

<span class="c-comment"># Dépendances</span>
<span class="c-cmd">pip install</span> -r requirements.txt

<span class="c-comment"># Lancement</span>
<span class="c-cmd">python</span> <span class="c-path">main.py</span></pre>
    </div>

    <div class="divider"></div>

    <div class="section-label" style="margin-top:0;">Clés API requises</div>
    <div class="code-block" style="margin-top:16px;">
      <div class="code-block-header">
        <div class="code-dot"></div>
        <div class="code-dot"></div>
        <div class="code-dot"></div>
        &nbsp; Configuration (onglet Paramètres)
      </div>
      <pre><span class="c-comment"># Google Custom Search (optionnel — moteur Google CSE)</span>
<span class="c-kw">GOOGLE_API_KEY</span>  = <span class="c-str">"AIza..."</span>      <span class="c-comment"># console.cloud.google.com</span>
<span class="c-kw">GOOGLE_CSE_ID</span>   = <span class="c-str">"cx=..."</span>       <span class="c-comment"># cse.google.com</span>

<span class="c-comment"># Bing Web Search API (optionnel)</span>
<span class="c-kw">BING_API_KEY</span>    = <span class="c-str">"..."</span>           <span class="c-comment"># portal.azure.com</span>

<span class="c-comment"># Shodan (optionnel — recherche IoT/infra)</span>
<span class="c-kw">SHODAN_API_KEY</span>  = <span class="c-str">"..."</span>           <span class="c-comment"># account.shodan.io</span>

<span class="c-comment"># Anthropic Claude (optionnel — IA Suggest)</span>
<span class="c-kw">ANTHROPIC_KEY</span>   = <span class="c-str">"sk-ant-..."</span>    <span class="c-comment"># console.anthropic.com</span>

<span class="c-comment"># DuckDuckGo — aucune clé requise ✓</span></pre>
    </div>
  </div>
</section>


<!-- ═══════════════════════════════════════════════════ ARCHITECTURE -->
<section>
  <div class="container">
    <div class="section-label">Architecture</div>
    <h2 class="section-title">Structure du <span style="color:var(--accent)">projet</span></h2>

    <div class="code-block">
      <div class="code-block-header">
        <div class="code-dot"></div>
        <div class="code-dot"></div>
        <div class="code-dot"></div>
        &nbsp; dorking-tool/
      </div>
      <pre><span class="c-path">dorking-tool/</span>
├── <span class="c-path">core/</span>
│   ├── <span class="c-cmd">dork_builder.py</span>      <span class="c-comment"># DorkBuilder, DorkQuery, validate_dork()</span>
│   ├── <span class="c-cmd">search_engine.py</span>     <span class="c-comment"># MultiEngine, SearchQueue, AdaptiveRateLimiter</span>
│   ├── <span class="c-cmd">smart_redirector.py</span>  <span class="c-comment"># Génération rapports HTML audit</span>
│   ├── <span class="c-cmd">watchdog.py</span>          <span class="c-comment"># WatchdogManager, SHA-256 hashing, webhooks</span>
│   ├── <span class="c-cmd">dork_suggest.py</span>      <span class="c-comment"># Claude AI — génération contextuelle par stack</span>
│   ├── <span class="c-cmd">config_manager.py</span>    <span class="c-comment"># AppConfig, keyring OS, persistance JSON</span>
│   └── <span class="c-cmd">exporter.py</span>          <span class="c-comment"># Export JSON / CSV / PDF (ReportLab)</span>
├── <span class="c-path">ui/</span>
│   └── <span class="c-cmd">app.py</span>               <span class="c-comment"># DorkingApp + 8 frames CustomTkinter</span>
├── <span class="c-path">data/</span>
│   ├── <span class="c-cmd">dork_library.json</span>    <span class="c-comment"># ~40 dorks, 16 opérateurs, 5 stacks</span>
│   └── <span class="c-path">reports/</span>             <span class="c-comment"># Rapports HTML générés (auto-créé)</span>
├── <span class="c-cmd">main.py</span>                  <span class="c-comment"># Point d'entrée</span>
├── <span class="c-cmd">requirements.txt</span>
├── <span class="c-cmd">installer.bat</span>            <span class="c-comment"># Installation automatique Windows</span>
└── <span class="c-cmd">lancer.bat</span>               <span class="c-comment"># Lancement Windows</span></pre>
    </div>
  </div>
</section>


<!-- ═══════════════════════════════════════════════════ LEGAL -->
<section>
  <div class="container">
    <div class="legal-box">
      <div class="legal-icon">⚠️</div>
      <div>
        <div class="legal-title">Avertissement légal — Usage autorisé uniquement</div>
        <p class="legal-text">
          Cet outil est destiné <strong>exclusivement</strong> à la cybersécurité défensive, aux audits de sécurité autorisés
          et à la recherche OSINT légale sur des systèmes dont vous êtes propriétaire ou pour lesquels
          vous disposez d'une <strong>autorisation écrite explicite</strong>.<br><br>
          L'utilisation de Google Dorks pour accéder à des données privées ou des systèmes tiers sans
          autorisation est <strong>illégale</strong> et peut entraîner des poursuites pénales
          (Computer Fraud and Abuse Act, loi Godfrain, RGPD).
          L'auteur décline toute responsabilité en cas d'usage malveillant ou non autorisé.
        </p>
      </div>
    </div>
  </div>
</section>


<!-- ═══════════════════════════════════════════════════ FOOTER -->
<footer class="footer">
  <div class="footer-logo">◈ DORKING TOOL</div>
  <p style="margin-bottom:8px;">OSINT &amp; Security Research Platform &nbsp;·&nbsp; Construit avec Python &amp; CustomTkinter</p>
  <p>Usage légal uniquement &nbsp;·&nbsp; Audit autorisé &amp; OSINT &nbsp;·&nbsp;
     <a href="https://github.com/votre-user/dorking-tool">GitHub</a>
  </p>
</footer>

</body>
</html>
