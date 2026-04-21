"""Moteur de construction de requêtes Google Dork."""

from dataclasses import dataclass, field


@dataclass
class DorkComponent:
    operator: str
    value: str
    negated: bool = False

    def build(self) -> str:
        prefix = "-" if self.negated else ""
        if self.operator == "raw":
            return f'{prefix}{self.value}'
        if self.operator == "around":
            # value = "mot1|N|mot2"
            parts = self.value.split("|")
            if len(parts) == 3:
                return f'{parts[0]} AROUND({parts[1]}) {parts[2]}'
            return self.value
        if self.operator in ("OR", "AND"):
            return f' {self.operator} '
        val = self.value.strip()
        if " " in val and not (val.startswith('"') and val.endswith('"')):
            val = f'"{val}"'
        return f'{prefix}{self.operator}:{val}'


@dataclass
class DorkQuery:
    components: list[DorkComponent] = field(default_factory=list)
    target: str = ""

    def add(self, operator: str, value: str, negated: bool = False) -> "DorkQuery":
        self.components.append(DorkComponent(operator, value, negated))
        return self

    def site(self, domain: str, negated: bool = False) -> "DorkQuery":
        return self.add("site", domain, negated)

    def filetype(self, ext: str, negated: bool = False) -> "DorkQuery":
        return self.add("filetype", ext, negated)

    def intitle(self, text: str, negated: bool = False) -> "DorkQuery":
        return self.add("intitle", text, negated)

    def inurl(self, path: str, negated: bool = False) -> "DorkQuery":
        return self.add("inurl", path, negated)

    def intext(self, text: str, negated: bool = False) -> "DorkQuery":
        return self.add("intext", text, negated)

    def around(self, word1: str, n: int, word2: str) -> "DorkQuery":
        return self.add("around", f"{word1}|{n}|{word2}")

    def keyword(self, text: str, exact: bool = False, negated: bool = False) -> "DorkQuery":
        val = f'"{text}"' if exact else text
        return self.add("raw", val, negated)

    def or_group(self, *values: str, operator: str = "filetype") -> "DorkQuery":
        """Crée un groupe OR : filetype:sql OR filetype:env"""
        for i, val in enumerate(values):
            if i > 0:
                self.components.append(DorkComponent("OR", ""))
            self.add(operator, val)
        return self

    def build(self) -> str:
        parts = []
        for comp in self.components:
            built = comp.build()
            if comp.operator in ("OR", "AND"):
                if parts:
                    parts[-1] = parts[-1].rstrip()
                parts.append(built)
            else:
                parts.append(built)
        return " ".join(p for p in parts if p.strip()).replace("  ", " ").strip()

    def apply_target(self, target: str) -> str:
        """Remplace {target} par la cible dans la requête."""
        return self.build().replace("{target}", target)

    def clear(self) -> "DorkQuery":
        self.components.clear()
        return self


class DorkBuilder:
    """
    Construction par blocs — chaque champ est géré séparément,
    les espaces et guillemets sont insérés automatiquement.

    Usage :
        b = DorkBuilder()
        b.set_site("example.com")
        b.set_filetype("sql")
        b.add_term("password")
        b.set_exact_phrase("root user")
        b.add_exclusion("test")
        b.set_proximity("vulnerability", "CVE", 3)
        print(b.build())
        # site:example.com filetype:sql password "root user" vulnerability AROUND(3) CVE -test
    """

    def __init__(self):
        self.parts: dict = {
            "site":          None,   # (value, negated) or None
            "filetype":      None,
            "intitle":       None,
            "inurl":         None,
            "intext":        None,
            "terms":         [],
            "exclusions":    [],
            "exact_phrase":  "",
            "proximity":     None,   # (word1, word2, distance)
            "or_filetypes":  [],     # [ext1, ext2, ...] → filetype:ext1 OR filetype:ext2
        }

    # ── Setters ────────────────────────────────────────────────────────

    def set_site(self, domain: str, negated: bool = False) -> "DorkBuilder":
        self.parts["site"] = (domain.strip(), negated)
        return self

    def set_filetype(self, ext: str, negated: bool = False) -> "DorkBuilder":
        self.parts["filetype"] = (ext.strip().lstrip("."), negated)
        return self

    def set_intitle(self, text: str, negated: bool = False) -> "DorkBuilder":
        self.parts["intitle"] = (text.strip(), negated)
        return self

    def set_inurl(self, path: str, negated: bool = False) -> "DorkBuilder":
        self.parts["inurl"] = (path.strip(), negated)
        return self

    def set_intext(self, text: str, negated: bool = False) -> "DorkBuilder":
        self.parts["intext"] = (text.strip(), negated)
        return self

    def set_exact_phrase(self, phrase: str) -> "DorkBuilder":
        self.parts["exact_phrase"] = phrase.strip()
        return self

    def set_proximity(self, word1: str, word2: str, distance: int) -> "DorkBuilder":
        self.parts["proximity"] = (word1.strip(), word2.strip(), max(1, distance))
        return self

    def add_term(self, term: str) -> "DorkBuilder":
        t = term.strip()
        if t:
            self.parts["terms"].append(t)
        return self

    def add_exclusion(self, term: str) -> "DorkBuilder":
        t = term.strip().lstrip("-")
        if t:
            self.parts["exclusions"].append(t)
        return self

    def add_or_filetype(self, *exts: str) -> "DorkBuilder":
        """Ajoute plusieurs extensions en groupe OR : filetype:sql OR filetype:env"""
        self.parts["or_filetypes"].extend(e.strip().lstrip(".") for e in exts)
        return self

    # ── Builder ────────────────────────────────────────────────────────

    def build(self) -> str:
        query = []

        def _op(name: str, val_tuple) -> str | None:
            if not val_tuple:
                return None
            val, neg = val_tuple
            if not val:
                return None
            if " " in val and not (val.startswith('"') and val.endswith('"')):
                val = f'"{val}"'
            return f"{'-' if neg else ''}{name}:{val}"

        # 1. Opérateurs de portée
        s = _op("site", self.parts["site"])
        if s:
            query.append(s)
        f = _op("filetype", self.parts["filetype"])
        if f:
            query.append(f)
        elif self.parts["or_filetypes"]:
            query.append(" OR ".join(f"filetype:{e}" for e in self.parts["or_filetypes"]))

        # 2. Opérateurs de ciblage
        for op in ("intitle", "inurl", "intext"):
            token = _op(op, self.parts[op])
            if token:
                query.append(token)

        # 3. Termes libres
        for term in self.parts["terms"]:
            query.append(term)

        # 4. Phrase exacte
        if self.parts["exact_phrase"]:
            query.append(f'"{self.parts["exact_phrase"]}"')

        # 5. Proximité AROUND(N)
        if self.parts["proximity"]:
            w1, w2, dist = self.parts["proximity"]
            query.append(f"{w1} AROUND({dist}) {w2}")

        # 6. Exclusions
        for ex in self.parts["exclusions"]:
            query.append(f"-{ex}")

        return " ".join(query).strip()

    # ── Utilitaires ────────────────────────────────────────────────────

    def clear(self) -> "DorkBuilder":
        self.__init__()
        return self

    def to_dork_query(self) -> "DorkQuery":
        """Convertit vers DorkQuery pour chaînage avancé."""
        return DorkQuery().add("raw", self.build())

    def __repr__(self) -> str:
        return f"DorkBuilder({self.build()!r})"


def from_template(template: str, target: str = "") -> str:
    """Applique un target à un template de dork."""
    if not target:
        return template
    return template.replace("{target}", target)


def validate_dork(dork: str) -> dict:
    """Valide et analyse les opérateurs d'un dork."""
    import re

    issues = []
    operators_found = []

    known_ops = ["site:", "filetype:", "intitle:", "inurl:", "intext:",
                 "cache:", "related:", "info:", "allintitle:", "allinurl:",
                 "AROUND(", "ext:"]

    for op in known_ops:
        if op.lower() in dork.lower():
            operators_found.append(op.rstrip(":"))

    # Guillemets équilibrés
    if dork.count('"') % 2 != 0:
        issues.append("Guillemets non équilibrés")

    # Syntaxe AROUND(N) : le N doit être un entier
    if "AROUND" in dork.upper():
        if not re.search(r'AROUND\(\d+\)', dork, re.IGNORECASE):
            issues.append("Syntaxe AROUND invalide — utilisez AROUND(N) avec N entier (ex: AROUND(3))")

    # Parenthèses équilibrées (hors AROUND déjà traité)
    dork_no_around = re.sub(r'AROUND\(\d+\)', '', dork, flags=re.IGNORECASE)
    if dork_no_around.count("(") != dork_no_around.count(")"):
        issues.append("Parenthèses non équilibrées")

    # Longueur max Google (~2048 caractères)
    if len(dork) > 2048:
        issues.append("Requête trop longue (>2048 caractères)")

    # OR consécutifs ou en début/fin
    if re.search(r'^\s*OR\b|\bOR\s*$|\bOR\s+OR\b', dork, re.IGNORECASE):
        issues.append("Opérateur OR mal positionné")

    # Opérateur site: sans valeur
    if re.search(r'site:\s', dork):
        issues.append("site: doit être suivi directement du domaine (sans espace)")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "operators": operators_found,
        "complexity": len(operators_found),
        "length": len(dork)
    }
