"""Générateur de dorks intelligent via Claude AI."""

import json
import re
from typing import Optional


STACK_INTEL = {
    "WordPress": {
        "files": ["wp-config.php", "wp-login.php", "debug.log", "xmlrpc.php"],
        "dirs": ["/wp-content/uploads/", "/wp-admin/", "/wp-includes/"],
        "extensions": ["php", "sql", "log", "bak"],
        "exposures": ["DB_PASSWORD", "AUTH_KEY", "LOGGED_IN_KEY", "WordPress database username"],
        "cves": ["XML-RPC bruteforce", "wp-json user enumeration", "TimThumb RCE"],
    },
    "Apache/PHP": {
        "files": ["phpinfo.php", ".htaccess", "config.php", "error_log"],
        "dirs": ["/includes/", "/config/", "/backup/"],
        "extensions": ["php", "inc", "env", "conf", "bak"],
        "exposures": ["PHP Warning", "MySQL error", "include_once failed", "open_basedir"],
        "cves": ["directory traversal", "LFI via include", "PHP object injection"],
    },
    "Node.js": {
        "files": [".env", "package.json", ".npmrc", "ecosystem.config.js"],
        "dirs": ["/node_modules/", "/.git/", "/dist/"],
        "extensions": ["env", "json", "js", "log"],
        "exposures": ["process.env", "JWT_SECRET", "DATABASE_URL", "NODE_ENV=production"],
        "cves": ["prototype pollution", "path traversal in express-static", "npm audit"],
    },
    "Django/Python": {
        "files": ["settings.py", "local_settings.py", "requirements.txt", ".env"],
        "dirs": ["/static/", "/media/", "/__pycache__/"],
        "extensions": ["py", "env", "cfg", "log"],
        "exposures": ["SECRET_KEY", "DEBUG = True", "DATABASES", "Django DEBUG Traceback"],
        "cves": ["SSTI via template", "open redirect", "SQL injection via ORM raw()"],
    },
    "AWS": {
        "files": ["credentials", ".aws/config", "terraform.tfstate", "serverless.yml"],
        "dirs": ["/.aws/", "/terraform/", "/.github/workflows/"],
        "extensions": ["env", "yaml", "yml", "json", "tfstate"],
        "exposures": ["AKIA", "aws_access_key_id", "aws_secret_access_key", "AWSAccessKeyId"],
        "cves": ["S3 public bucket", "IAM privilege escalation", "Lambda env vars exposure"],
    },
    "Docker": {
        "files": ["docker-compose.yml", "Dockerfile", ".dockerenv", "docker-compose.override.yml"],
        "dirs": ["/docker/", "/compose/"],
        "extensions": ["yml", "yaml", "env"],
        "exposures": ["MYSQL_ROOT_PASSWORD", "POSTGRES_PASSWORD", "ports:", "volumes:"],
        "cves": ["exposed Docker API :2375", "privileged container", "Docker socket mount"],
    },
    "Nginx": {
        "files": ["nginx.conf", "default.conf", "sites-enabled/default"],
        "dirs": ["/etc/nginx/", "/var/log/nginx/"],
        "extensions": ["conf", "log"],
        "exposures": ["server_tokens", "autoindex on", "proxy_pass", "access.log"],
        "cves": ["alias traversal", "CRLF injection", "open redirect via proxy"],
    },
}

SUGGEST_PROMPT = """Tu es un expert en cybersécurité offensive et OSINT chargé d'un audit de sécurité autorisé.
Cible : {target}

CONTEXTE DE STACK TECHNIQUE
Stack identifiée : {stack}
Fichiers/endpoints critiques pour ce stack : {stack_files}
Exposures connues à rechercher : {stack_exposures}
CVEs/vecteurs typiques : {stack_cves}

OBJECTIF : {objective}

MISSION : Génère exactement {count} Google Dorks exploitant les spécificités de cette stack.
Chaque dork doit :
- Utiliser au moins un opérateur avancé : site:, filetype:, intitle:, inurl:, intext:, AROUND(N), OR, NOT (-)
- Cibler des faiblesses RÉELLES et documentées de cette stack
- Être directement utilisable sans modification (remplacer {target} par le vrai domaine si nécessaire)

Répartis les dorks entre ces catégories : Credentials, Config Files, Admin Panels, Debug/Info Disclosure, GitHub/Pastebin Leaks, Directory Listing.

Réponds UNIQUEMENT avec un tableau JSON valide, sans markdown, sans texte autour.
[
  {{
    "dork": "requête complète prête à l'emploi",
    "description": "ce que cette requête révèle concrètement",
    "severity": "CRITIQUE|ÉLEVÉ|MOYEN|INFO",
    "category": "catégorie"
  }}
]"""


def _build_stack_context(stack: str) -> dict:
    """Extrait le contexte technique d'un stack pour enrichir le prompt."""
    intel = STACK_INTEL.get(stack, {})
    return {
        "stack_files": ", ".join(intel.get("files", []) + intel.get("extensions", [])) or "générique",
        "stack_exposures": ", ".join(intel.get("exposures", [])) or "credentials, API keys",
        "stack_cves": ", ".join(intel.get("cves", [])) or "vulnérabilités génériques",
    }


def generate_dorks(
    target: str,
    stack: str = "inconnu",
    objective: str = "audit de sécurité général",
    count: int = 20,
    api_key: Optional[str] = None
) -> list[dict]:
    """Génère des dorks via Claude AI avec contexte de stack enrichi."""
    if not api_key:
        raise ValueError("Clé API Anthropic requise pour la génération de dorks IA")

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    stack_ctx = _build_stack_context(stack)
    prompt = SUGGEST_PROMPT.format(
        target=target,
        stack=stack,
        objective=objective,
        count=count,
        **stack_ctx
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    content = message.content[0].text.strip()

    json_match = re.search(r'\[.*\]', content, re.DOTALL)
    if json_match:
        content = json_match.group(0)

    dorks = json.loads(content)
    for d in dorks:
        d["dork"] = d["dork"].replace("{target}", target)
    return dorks


def generate_dorks_from_company(
    company_name: str,
    domain: str = "",
    count: int = 50,
    api_key: Optional[str] = None
) -> list[dict]:
    """Génère les 50 meilleurs dorks pour une entreprise spécifique."""
    if not api_key:
        raise ValueError("Clé API Anthropic requise")

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Tu es un expert en sécurité offensive. Pour l'entreprise "{company_name}"{f" (domaine: {domain})" if domain else ""},
génère les {count} Google Dorks les plus susceptibles de révéler :
1. Des credentials et clés API exposées
2. Des fichiers de configuration sensibles
3. Des panneaux d'administration accessibles
4. Des fuites de données sur GitHub/Pastebin/etc.
5. Des vulnérabilités d'infrastructure
6. Des informations OSINT sur les employés et la stack technique

Réponds UNIQUEMENT avec un tableau JSON valide :
[
  {{
    "dork": "requête complète prête à l'emploi",
    "description": "explication courte",
    "severity": "CRITIQUE|ÉLEVÉ|MOYEN|INFO",
    "category": "catégorie"
  }}
]"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )

    content = message.content[0].text.strip()
    json_match = re.search(r'\[.*\]', content, re.DOTALL)
    if json_match:
        content = json_match.group(0)

    return json.loads(content)


STACK_DORKS = {
    "WordPress": [
        'site:{target} filetype:php inurl:wp-config',
        'site:{target} inurl:/wp-json/wp/v2/users',
        'site:{target} intitle:"WordPress" inurl:/wp-login.php',
        'site:{target} inurl:/wp-content/uploads/ filetype:sql',
        'site:{target} filetype:log inurl:debug.log "WordPress"',
    ],
    "Apache/PHP": [
        'site:{target} intitle:"phpinfo()" "PHP Version"',
        'site:{target} "Warning: include_once" path filetype:php',
        'site:{target} intitle:"Index of" "config.php"',
        'site:{target} filetype:env "DB_HOST" OR "DB_PASSWORD"',
        'site:{target} inurl:".git/config"',
    ],
    "Node.js": [
        'site:{target} filetype:env "NODE_ENV" "PORT"',
        'site:{target} filetype:json "dependencies" "express" -package-lock',
        'site:{target} "TypeError: Cannot read" OR "UnhandledPromiseRejection"',
        'site:github.com {target} "process.env" secret key',
        'site:{target} inurl:/.env "SECRET"',
    ],
    "Django/Python": [
        'site:{target} "Django" "Traceback" "settings"',
        'site:{target} "DisallowedHost" "ALLOWED_HOSTS"',
        'site:{target} filetype:py "SECRET_KEY" "DATABASES"',
        'site:github.com {target} "settings.py" "SECRET_KEY"',
        'site:{target} intitle:"OperationalError" "Django"',
    ],
    "AWS": [
        'site:{target} "AKIA" filetype:env OR filetype:config',
        'site:s3.amazonaws.com {target}',
        'site:{target} "aws_access_key_id" "aws_secret"',
        'site:github.com {target} "AWSAccessKeyId" "aws_secret"',
        'site:{target} filetype:yaml "s3:" "bucket:"',
    ],
}


def get_stack_dorks(stack: str, target: str) -> list[str]:
    """Retourne les dorks prédéfinis pour un stack, avec target appliqué."""
    dorks = STACK_DORKS.get(stack, [])
    return [d.replace("{target}", target) for d in dorks]
