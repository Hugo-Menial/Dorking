<div align="center">

<h1>◈ DORKING TOOL</h1>

<p><strong>Plateforme OSINT & Security Research — Desktop · Python · Claude AI</strong></p>

<br>

<img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white" alt="Windows">
<img src="https://img.shields.io/badge/UI-CustomTkinter-1A1A2E" alt="CustomTkinter">
<img src="https://img.shields.io/badge/AI-Claude%20Sonnet-D4A017?logo=anthropic&logoColor=white" alt="Claude AI">
<img src="https://img.shields.io/badge/License-MIT-00C853" alt="License">
<img src="https://img.shields.io/badge/Usage-Audit%20autorisé%20uniquement-FF4444" alt="Legal">

<br><br>

<p>
  <a href="#-fonctionnalités">Fonctionnalités</a> ·
  <a href="#-installation">Installation</a> ·
  <a href="#-configuration-des-clés-api">Configuration</a> ·
  <a href="#-structure-du-projet">Architecture</a> ·
  <a href="#️-avertissement-légal">Légal</a>
</p>

</div>

---

## 🎯 Présentation

**Dorking Tool** est une application desktop Python conçue pour les **auditeurs de sécurité**, **chercheurs OSINT** et **pentesters** souhaitant exploiter les Google Dorks de manière structurée, professionnelle et légale.

L'outil regroupe en une seule interface :

- un **constructeur visuel de requêtes** avec validation en temps réel
- une **recherche multi-moteurs** (Google CSE, Bing, DuckDuckGo, Shodan)
- un **assistant IA** (Claude) pour la génération contextuelle de dorks
- un **système de surveillance automatique** (Watchdog) avec alertes Discord
- un **générateur de rapports HTML** d'audit groupés par sévérité
- une **bibliothèque** de dorks préconstruits et un **Wiki** de référence complet

> ⚠️ **Usage légal uniquement.** Cet outil est réservé aux audits de sécurité autorisés et à la recherche OSINT sur des systèmes que vous possédez ou pour lesquels vous avez une autorisation écrite.

---

## ✨ Fonctionnalités

<table>
  <thead>
    <tr>
      <th>Module</th>
      <th>Description</th>
      <th>Technologie</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🔍 <strong>Dork Builder</strong></td>
      <td>Construction bloc-par-bloc avec validation live, auto-quoting, opérateurs rapides et support NOT par champ</td>
      <td><code>DorkBuilder</code> · <code>DorkQuery</code></td>
    </tr>
    <tr>
      <td>🌐 <strong>Multi-Engine Search</strong></td>
      <td>Google CSE, Bing, DuckDuckGo et Shodan en parallèle via une file non-bloquante. Rate-limiting adaptatif avec exponential backoff</td>
      <td><code>SearchQueue</code> · <code>AdaptiveRateLimiter</code></td>
    </tr>
    <tr>
      <td>🤖 <strong>IA Suggest</strong></td>
      <td>Génération de dorks contextuels via Claude (claude-sonnet-4-6). Prompt enrichi selon 7 stacks techniques : WordPress, AWS, Django, Node.js, Apache, Docker, Nginx</td>
      <td><code>Anthropic SDK</code> · <code>Stack Intel</code></td>
    </tr>
    <tr>
      <td>👁 <strong>Watchdog</strong></td>
      <td>Surveillance planifiée à intervalle personnalisé. Détection des nouveaux résultats par hash SHA-256. Alertes Discord webhook avec jitter ±10%</td>
      <td><code>WatchdogManager</code> · <code>threading</code></td>
    </tr>
    <tr>
      <td>📄 <strong>Rapports HTML</strong></td>
      <td>Génère des rapports d'audit dark-mode groupés par sévérité (CRITIQUE → INFO), liens Google paginés P1/P2/P3 et bouton copier</td>
      <td><code>SmartRedirector</code></td>
    </tr>
    <tr>
      <td>📚 <strong>Bibliothèque</strong></td>
      <td>~40 dorks préconstruits en 6 catégories avec sévérité, tags et application de cible dynamique via <code>{target}</code></td>
      <td><code>dork_library.json</code></td>
    </tr>
    <tr>
      <td>📖 <strong>Wiki intégré</strong></td>
      <td>Documentation interactive de 18+ opérateurs en 5 sections : portée, contenu, logique, techniques avancées, recettes OSINT. Bouton <em>Try</em> sur chaque exemple</td>
      <td><code>WikiFrame</code></td>
    </tr>
    <tr>
      <td>🔐 <strong>Stockage sécurisé</strong></td>
      <td>Clés API stockées dans le trousseau OS (Windows Credential Manager). Fallback JSON chiffré avec avertissement</td>
      <td><code>keyring</code> · <code>WinVaultKeyring</code></td>
    </tr>
    <tr>
      <td>↓ <strong>Export multi-format</strong></td>
      <td>Exportez vos résultats en JSON, CSV, PDF (mise en page professionnelle) ou rapport HTML interactif</td>
      <td><code>ReportLab</code> · <code>csv</code> · <code>json</code></td>
    </tr>
  </tbody>
</table>

---

## 🖥️ Interface — 8 onglets

<table>
  <tr>
    <td align="center">🔍<br><strong>Dork Builder</strong><br><sub>Construction visuelle<br>& validation live</sub></td>
    <td align="center">📚<br><strong>Bibliothèque</strong><br><sub>~40 dorks classés<br>par sévérité</sub></td>
    <td align="center">🔣<br><strong>Opérateurs</strong><br><sub>16 opérateurs<br>avec exemples</sub></td>
    <td align="center">📖<br><strong>Wiki</strong><br><sub>Documentation complète<br>& recettes OSINT</sub></td>
  </tr>
  <tr>
    <td align="center">🤖<br><strong>IA Suggest</strong><br><sub>Génération Claude AI<br>par stack technique</sub></td>
    <td align="center">👁<br><strong>Watchdog</strong><br><sub>Surveillance planifiée<br>& alertes Discord</sub></td>
    <td align="center">📊<br><strong>Résultats</strong><br><sub>Live console<br>& export</sub></td>
    <td align="center">⚙️<br><strong>Paramètres</strong><br><sub>Clés API sécurisées<br>& configuration</sub></td>
  </tr>
</table>

---

## 🔣 Opérateurs supportés

<table>
  <thead>
    <tr>
      <th>Opérateur</th>
      <th>Usage</th>
      <th>Exemple</th>
      <th>Catégorie</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>site:</code></td><td>Restreindre au domaine</td><td><code>site:example.com</code></td><td>🎯 Portée</td></tr>
    <tr><td><code>filetype:</code></td><td>Filtrer par extension</td><td><code>filetype:sql</code></td><td>🎯 Portée</td></tr>
    <tr><td><code>intitle:</code></td><td>Texte dans le &lt;title&gt;</td><td><code>intitle:"index of"</code></td><td>📄 Contenu</td></tr>
    <tr><td><code>inurl:</code></td><td>Texte dans l'URL</td><td><code>inurl:admin</code></td><td>📄 Contenu</td></tr>
    <tr><td><code>intext:</code></td><td>Texte dans le corps</td><td><code>intext:"password="</code></td><td>📄 Contenu</td></tr>
    <tr><td><code>cache:</code></td><td>Version en cache Google</td><td><code>cache:example.com</code></td><td>🎯 Portée</td></tr>
    <tr><td><code>related:</code></td><td>Sites similaires</td><td><code>related:github.com</code></td><td>🎯 Portée</td></tr>
    <tr><td><code>AROUND(N)</code></td><td>Proximité de N mots</td><td><code>password AROUND(3) user</code></td><td>⚙️ Logique</td></tr>
    <tr><td><code>"phrase"</code></td><td>Correspondance exacte</td><td><code>"BEGIN RSA PRIVATE KEY"</code></td><td>⚙️ Logique</td></tr>
    <tr><td><code>-mot</code></td><td>Exclure un terme</td><td><code>-intext:sample</code></td><td>⚙️ Logique</td></tr>
    <tr><td><code>OR</code></td><td>Union logique</td><td><code>filetype:sql OR filetype:db</code></td><td>⚙️ Logique</td></tr>
    <tr><td><code>allintitle:</code></td><td>Tous les mots dans le titre</td><td><code>allintitle:admin panel</code></td><td>📄 Contenu</td></tr>
    <tr><td><code>allinurl:</code></td><td>Tous les mots dans l'URL</td><td><code>allinurl:admin login</code></td><td>📄 Contenu</td></tr>
    <tr><td><code>ext:</code></td><td>Alias strict de filetype:</td><td><code>ext:env</code></td><td>🎯 Portée</td></tr>
    <tr><td><code>info:</code></td><td>Informations Google sur l'URL</td><td><code>info:example.com</code></td><td>🎯 Portée</td></tr>
    <tr><td><code>*</code></td><td>Wildcard (dans les guillemets)</td><td><code>"Bearer *"</code></td><td>⚙️ Logique</td></tr>
  </tbody>
</table>

---

## 🚦 Niveaux de sévérité

<table>
  <tr>
    <td align="center"><strong>🔴 CRITIQUE</strong><br><sub>Credentials, clés privées,<br>bases de données exposées</sub></td>
    <td align="center"><strong>🟠 ÉLEVÉ</strong><br><sub>Panneaux admin, fichiers<br>de config, backups</sub></td>
    <td align="center"><strong>🟡 MOYEN</strong><br><sub>Documents internes,<br>répertoires, stack traces</sub></td>
    <td align="center"><strong>🔵 INFO</strong><br><sub>Reconnaissance générale,<br>cartographie de surface</sub></td>
  </tr>
</table>

---

## 📦 Stack technique

<table>
  <thead>
    <tr>
      <th>Dépendance</th>
      <th>Version</th>
      <th>Rôle</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>customtkinter</code></td><td><code>≥ 5.2.0</code></td><td>Interface graphique desktop dark-mode</td></tr>
    <tr><td><code>requests</code></td><td><code>≥ 2.31.0</code></td><td>Requêtes HTTP, webhooks Discord</td></tr>
    <tr><td><code>ddgs</code></td><td><code>≥ 8.0.0</code></td><td>Recherche DuckDuckGo (sans clé API)</td></tr>
    <tr><td><code>shodan</code></td><td><code>≥ 1.31.0</code></td><td>Recherche IoT & infrastructure</td></tr>
    <tr><td><code>anthropic</code></td><td><code>≥ 0.40.0</code></td><td>Claude AI — génération de dorks</td></tr>
    <tr><td><code>reportlab</code></td><td><code>≥ 4.2.0</code></td><td>Export PDF professionnel</td></tr>
    <tr><td><code>pillow</code></td><td><code>≥ 10.0.0</code></td><td>Traitement d'images (UI)</td></tr>
    <tr><td><code>keyring</code></td><td>système</td><td>Stockage sécurisé des clés API (OS keychain)</td></tr>
    <tr><td><code>pyperclip</code></td><td><code>≥ 1.9.0</code></td><td>Copie dans le presse-papier</td></tr>
    <tr><td><code>python-dotenv</code></td><td><code>≥ 1.0.0</code></td><td>Chargement des variables d'environnement</td></tr>
  </tbody>
</table>

---

## 🚀 Installation

### Méthode rapide — Windows

> Double-cliquer sur **`installer.bat`** puis **`lancer.bat`**. C'est tout.

### Méthode manuelle

<pre><code class="language-bash"># 1. Cloner le dépôt
git clone https://github.com/votre-user/dorking-tool.git
cd dorking-tool

# 2. Créer un environnement virtuel (recommandé)
python -m venv .venv
.venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python main.py
</code></pre>

---

## 🔑 Configuration des clés API

Les clés API se configurent directement dans l'onglet **⚙️ Paramètres** de l'application.
Elles sont stockées dans le **trousseau système OS** (Windows Credential Manager).

<table>
  <thead>
    <tr>
      <th>Service</th>
      <th>Obligatoire</th>
      <th>Obtenir la clé</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🔍 <strong>Google CSE API Key</strong></td>
      <td>Optionnel</td>
      <td><a href="https://console.cloud.google.com">console.cloud.google.com</a> → Custom Search API</td>
    </tr>
    <tr>
      <td>🔍 <strong>Google CSE ID (cx)</strong></td>
      <td>Optionnel</td>
      <td><a href="https://cse.google.com">cse.google.com</a> → Créer un moteur</td>
    </tr>
    <tr>
      <td>🔷 <strong>Bing API Key</strong></td>
      <td>Optionnel</td>
      <td><a href="https://portal.azure.com">portal.azure.com</a> → Bing Web Search v7</td>
    </tr>
    <tr>
      <td>🔴 <strong>Shodan API Key</strong></td>
      <td>Optionnel</td>
      <td><a href="https://account.shodan.io">account.shodan.io</a> → My Account</td>
    </tr>
    <tr>
      <td>🤖 <strong>Anthropic API Key</strong></td>
      <td>Optionnel (IA Suggest)</td>
      <td><a href="https://console.anthropic.com">console.anthropic.com</a> → API Keys</td>
    </tr>
    <tr>
      <td>🌊 <strong>DuckDuckGo</strong></td>
      <td>✅ Aucune clé requise</td>
      <td>Fonctionne immédiatement sans compte</td>
    </tr>
  </tbody>
</table>

---

## 🗂️ Structure du projet

<pre><code>dorking-tool/
├── core/
│   ├── dork_builder.py       # DorkBuilder, DorkQuery, validate_dork()
│   ├── search_engine.py      # MultiEngine, SearchQueue, AdaptiveRateLimiter
│   ├── smart_redirector.py   # Génération rapports HTML d'audit
│   ├── watchdog.py           # WatchdogManager, SHA-256 hashing, webhooks
│   ├── dork_suggest.py       # Claude AI — génération contextuelle par stack
│   ├── config_manager.py     # AppConfig, keyring OS, persistance JSON
│   └── exporter.py           # Export JSON / CSV / PDF (ReportLab)
├── ui/
│   └── app.py                # DorkingApp + 8 frames CustomTkinter
├── data/
│   ├── dork_library.json     # ~40 dorks, 16 opérateurs, 5 stacks
│   └── reports/              # Rapports HTML générés (auto-créé)
├── main.py                   # Point d'entrée
├── requirements.txt
├── installer.bat             # Installation automatique Windows
└── lancer.bat                # Lancement Windows
</code></pre>

---

## ⚠️ Avertissement légal

> **Cet outil est destiné exclusivement à :**
> - 🛡️ La cybersécurité **défensive**
> - 📋 Les **audits de sécurité autorisés** (avec accord écrit)
> - 🔍 La recherche **OSINT légale** sur des systèmes que vous possédez
>
> L'utilisation de Google Dorks pour accéder à des données privées ou des systèmes tiers **sans autorisation explicite est illégale** et peut entraîner des poursuites pénales *(Computer Fraud and Abuse Act, Loi Godfrain, RGPD)*.
>
> L'auteur décline toute responsabilité en cas d'usage malveillant ou non autorisé.

---

<div align="center">

<p>Fait avec ❤️ pour la communauté cybersécurité francophone</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Usage-Audit%20autorisé%20uniquement-FF4444" alt="Legal">
</p>

</div>
