"""Moteur de recherche multi-sources pour les dorks."""

import time
import random
import webbrowser
import requests
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Callable
from urllib.parse import quote_plus


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    timestamp: str = ""


@dataclass
class RateLimitState:
    """Suivi de l'état de limitation pour un moteur."""
    requests_made: int = 0
    window_start: datetime = field(default_factory=datetime.now)
    retry_after: Optional[datetime] = None
    consecutive_errors: int = 0


class RateLimitError(Exception):
    """Levée quand un moteur retourne 429 ou 503."""
    def __init__(self, engine: str, retry_after_seconds: int = 0):
        self.engine = engine
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            f"{engine} : limite de taux atteinte"
            + (f" — réessayez dans {retry_after_seconds}s" if retry_after_seconds else "")
        )


class AdaptiveRateLimiter:
    """
    Temporisation adaptative avec backoff exponentiel.
    Objectif : être un client poli, pas contourner les protections.
    """

    # Délais de base entre requêtes (secondes) par moteur
    BASE_DELAYS = {
        "Google CSE":  1.0,
        "Bing":        0.5,
        "DuckDuckGo":  1.5,
        "Shodan":      1.0,
    }
    MAX_DELAY = 30.0

    def __init__(self):
        self._states: dict[str, RateLimitState] = {}

    def _state(self, engine: str) -> RateLimitState:
        if engine not in self._states:
            self._states[engine] = RateLimitState()
        return self._states[engine]

    def wait(self, engine: str):
        """Attend le délai adaptatif avant la prochaine requête."""
        state = self._state(engine)

        # Moteur en cooldown explicite (Retry-After reçu)
        if state.retry_after and datetime.now() < state.retry_after:
            wait_s = (state.retry_after - datetime.now()).total_seconds()
            raise RateLimitError(engine, int(wait_s))

        # Délai de base + backoff si erreurs consécutives
        base = self.BASE_DELAYS.get(engine, 1.0)
        if state.consecutive_errors > 0:
            backoff = min(base * (2 ** state.consecutive_errors), self.MAX_DELAY)
        else:
            backoff = base

        # Légère variation (±15%) pour naturaliser le timing sans intent d'évasion
        jitter = backoff * random.uniform(-0.15, 0.15)
        time.sleep(max(0.1, backoff + jitter))

    def record_success(self, engine: str):
        state = self._state(engine)
        state.consecutive_errors = 0
        state.retry_after = None
        state.requests_made += 1

    def record_error(self, engine: str, status_code: int, retry_after_header: str = ""):
        state = self._state(engine)
        state.consecutive_errors += 1

        if status_code in (429, 503):
            # Respecte le header Retry-After si présent
            if retry_after_header and retry_after_header.isdigit():
                wait_s = int(retry_after_header)
            else:
                # Backoff exponentiel : 30s, 60s, 120s...
                wait_s = min(30 * (2 ** (state.consecutive_errors - 1)), 600)
            state.retry_after = datetime.now() + timedelta(seconds=wait_s)


def _api_headers(extra: dict = None) -> dict:
    """Headers standard pour les appels API — pas de rotation, identification honnête."""
    headers = {
        "Accept": "application/json",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
    }
    if extra:
        headers.update(extra)
    return headers


# Limiteur partagé entre tous les moteurs
_rate_limiter = AdaptiveRateLimiter()


class GoogleCSEEngine:
    """Recherche via l'API officielle Google Custom Search Engine."""

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id

    def search(self, query: str, num: int = 10, start: int = 1) -> list[SearchResult]:
        if not self.api_key or not self.cse_id:
            raise ValueError("Clé API Google CSE et CX (ID moteur) requis")

        _rate_limiter.wait("Google CSE")

        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": min(num, 10),
            "start": start,
        }

        try:
            resp = requests.get(
                self.BASE_URL, params=params,
                headers=_api_headers(), timeout=15
            )

            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After", "")
                _rate_limiter.record_error("Google CSE", 429, retry_after)
                raise RateLimitError("Google CSE", int(retry_after) if retry_after.isdigit() else 60)

            if resp.status_code == 403:
                data = resp.json()
                reason = data.get("error", {}).get("message", "Quota dépassé ou clé invalide")
                raise ValueError(f"Google CSE API — {reason}")

            resp.raise_for_status()
            _rate_limiter.record_success("Google CSE")
            data = resp.json()

        except RateLimitError:
            raise
        except requests.HTTPError as e:
            _rate_limiter.record_error("Google CSE", e.response.status_code)
            raise

        results = []
        for item in data.get("items", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source="Google CSE",
                timestamp=item.get("pagemap", {}).get("metatags", [{}])[0].get(
                    "article:published_time", ""
                ) if item.get("pagemap") else ""
            ))
        return results


class BingEngine:
    """Recherche via l'API Bing Web Search."""

    BASE_URL = "https://api.bing.microsoft.com/v7.0/search"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, count: int = 10, offset: int = 0) -> list[SearchResult]:
        if not self.api_key:
            raise ValueError("Clé API Bing requise")

        _rate_limiter.wait("Bing")

        headers = _api_headers({"Ocp-Apim-Subscription-Key": self.api_key})
        params = {"q": query, "count": min(count, 50), "offset": offset, "mkt": "fr-FR"}

        try:
            resp = requests.get(self.BASE_URL, headers=headers, params=params, timeout=15)

            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After", "")
                _rate_limiter.record_error("Bing", 429, retry_after)
                raise RateLimitError("Bing", int(retry_after) if retry_after.isdigit() else 60)

            resp.raise_for_status()
            _rate_limiter.record_success("Bing")

        except RateLimitError:
            raise
        except requests.HTTPError as e:
            _rate_limiter.record_error("Bing", e.response.status_code)
            raise

        results = []
        for item in resp.json().get("webPages", {}).get("value", []):
            results.append(SearchResult(
                title=item.get("name", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
                source="Bing",
                timestamp=item.get("dateLastCrawled", "")
            ))
        return results


class DuckDuckGoEngine:
    """Recherche via DuckDuckGo (bibliothèque ddgs)."""

    def search(self, query: str, max_results: int = 20) -> list[SearchResult]:
        try:
            from ddgs import DDGS
        except ImportError:
            try:
                from duckduckgo_search import DDGS
            except ImportError:
                raise ImportError("Installez ddgs : pip install ddgs")

        _rate_limiter.wait("DuckDuckGo")

        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        source="DuckDuckGo",
                        timestamp=r.get("published", "")
                    ))
            _rate_limiter.record_success("DuckDuckGo")
            return results

        except Exception as e:
            err_str = str(e).lower()
            if "ratelimit" in err_str or "202" in err_str or "429" in err_str:
                _rate_limiter.record_error("DuckDuckGo", 429)
                raise RateLimitError("DuckDuckGo", 30)
            raise


class ShodanEngine:
    """Recherche d'appareils/services via Shodan."""

    BASE_URL = "https://api.shodan.io/shodan/host/search"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, page: int = 1) -> list[SearchResult]:
        if not self.api_key:
            raise ValueError("Clé API Shodan requise")

        _rate_limiter.wait("Shodan")

        params = {"key": self.api_key, "query": query, "page": page}

        try:
            resp = requests.get(
                self.BASE_URL, params=params,
                headers=_api_headers(), timeout=20
            )

            if resp.status_code == 429:
                _rate_limiter.record_error("Shodan", 429)
                raise RateLimitError("Shodan", 60)

            resp.raise_for_status()
            _rate_limiter.record_success("Shodan")

        except RateLimitError:
            raise
        except requests.HTTPError as e:
            _rate_limiter.record_error("Shodan", e.response.status_code)
            raise

        results = []
        for match in resp.json().get("matches", []):
            ip = match.get("ip_str", "")
            port = match.get("port", "")
            org = match.get("org", "")
            product = match.get("product", "")
            banner = match.get("data", "")[:200]

            results.append(SearchResult(
                title=f"{ip}:{port} — {product or org}",
                url=f"https://www.shodan.io/host/{ip}",
                snippet=banner.replace("\n", " ").strip(),
                source="Shodan",
                timestamp=match.get("timestamp", "")
            ))
        return results


class SearchURLBuilder:
    """
    Construit des URLs de recherche avec paramètres avancés pour maximiser
    la visibilité des résultats dans un contexte d'audit.

    Deux styles d'appel supportés :
        # Instance (paramètres complets)
        builder = SearchURLBuilder()
        url = builder.build_google(dork, num=100, date_range="qdr:w")

        # Statique (signature courte, compatible avec les scripts externes)
        url = SearchURLBuilder.build_google(dork)
        url = SearchURLBuilder.build_duckduckgo(dork)
        url = SearchURLBuilder.build_shodan(dork)
    """

    GOOGLE_BASE = "https://www.google.com/search"
    BING_BASE   = "https://www.bing.com/search"
    DDG_BASE    = "https://duckduckgo.com/"
    SHODAN_BASE = "https://www.shodan.io/search"

    DATE_RANGES = {
        "Toutes dates":     "",
        "Dernière heure":   "qdr:h",
        "Dernier jour":     "qdr:d",
        "Dernière semaine": "qdr:w",
        "Dernier mois":     "qdr:m",
        "Dernière année":   "qdr:y",
    }

    # ------------------------------------------------------------------ #
    # Méthodes d'instance — paramètres complets                           #
    # ------------------------------------------------------------------ #

    def build_google(
        self,
        query: str,
        num: int = 100,
        filter_duplicates: bool = False,
        date_range: str = "",
        start: int = 0,
        lang: str = "",
        country: str = "",
    ) -> str:
        from urllib.parse import urlencode
        params: dict = {
            "q":      query,
            "num":    min(num, 100),
            "filter": "0" if not filter_duplicates else "1",
            "safe":   "off",
        }
        if start:      params["start"] = start
        if date_range: params["tbs"]   = date_range
        if lang:       params["lr"]    = f"lang_{lang}"
        if country:    params["gl"]    = country
        return f"{self.GOOGLE_BASE}?{urlencode(params)}"

    def build_bing(
        self,
        query: str,
        count: int = 50,
        freshness: str = "",
        market: str = "fr-FR",
    ) -> str:
        from urllib.parse import urlencode
        params: dict = {"q": query, "count": min(count, 50), "safesearch": "Off", "mkt": market}
        if freshness:
            params["freshness"] = freshness
        return f"{self.BING_BASE}?{urlencode(params)}"

    def build_ddg(self, query: str, safe_off: bool = True, lang: str = "fr-fr") -> str:
        from urllib.parse import urlencode
        params = {"q": query, "kl": lang, "kp": "-2" if safe_off else "-1"}
        return f"{self.DDG_BASE}?{urlencode(params)}"

    def build_shodan(self, query: str) -> str:
        return f"{self.SHODAN_BASE}?query={quote_plus(query)}"

    def build_all(self, query: str, **kwargs) -> dict[str, str]:
        return {
            "Google":     self.build_google(query, **{
                k: v for k, v in kwargs.items()
                if k in ("num", "filter_duplicates", "date_range", "start", "lang")
            }),
            "Bing":       self.build_bing(query),
            "DuckDuckGo": self.build_ddg(query),
            "Shodan":     self.build_shodan(query),
        }

    def paginate_google(self, query: str, pages: int = 5, results_per_page: int = 100) -> list[str]:
        return [
            self.build_google(query, num=results_per_page, start=i * results_per_page)
            for i in range(pages)
        ]

    # ------------------------------------------------------------------ #
    # Méthodes statiques — signature courte pour les scripts externes     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def google(dork: str, start: int = 0) -> str:
        """Alias statique : SearchURLBuilder.google(dork, start=100)"""
        from urllib.parse import urlencode
        params = {"q": dork, "num": 100, "filter": "0", "safe": "off"}
        if start:
            params["start"] = start
        return f"https://www.google.com/search?{urlencode(params)}"

    @staticmethod
    def duckduckgo(dork: str) -> str:
        """Alias statique : SearchURLBuilder.duckduckgo(dork)"""
        from urllib.parse import urlencode
        return f"https://duckduckgo.com/?{urlencode({'q': dork, 'kp': '-2'})}"

    @staticmethod
    def shodan(dork: str) -> str:
        """Alias statique : SearchURLBuilder.shodan(dork)"""
        return f"https://www.shodan.io/search?query={quote_plus(dork)}"

    # Compat avec le nom proposé dans les snippets utilisateur
    build_duckduckgo = staticmethod(lambda dork: SearchURLBuilder.duckduckgo(dork))


# Constructeur global partagé
url_builder = SearchURLBuilder()


def open_in_browser(query: str, engine: str = "google", **url_params) -> str:
    """
    Ouvre la requête dans le navigateur réel — vue identique à un humain.
    Utilise SearchURLBuilder pour des paramètres d'audit optimaux.
    """
    if engine == "google":
        url = url_builder.build_google(query, **url_params)
    elif engine == "bing":
        url = url_builder.build_bing(query)
    elif engine == "ddg":
        url = url_builder.build_ddg(query)
    elif engine == "shodan":
        url = url_builder.build_shodan(query)
    else:
        url = url_builder.build_google(query)
    webbrowser.open(url)
    return url


import queue as _queue_module
import threading as _threading_module
from dataclasses import dataclass as _dataclass


@_dataclass
class SearchJob:
    """Un job de recherche en attente dans la file."""
    job_id:      str
    query:       str
    engines:     list
    max_results: int
    on_result:   Optional[Callable] = None
    on_complete: Optional[Callable] = None
    on_error:    Optional[Callable] = None
    priority:    int = 5  # 1=haute, 10=basse


class SearchQueue:
    """
    File d'attente de recherches non-bloquante.
    Le worker tourne dans un thread daemon — l'UI ne freeze jamais.

    Pourquoi threading.Queue et non asyncio.PriorityQueue ?
    --------------------------------------------------------
    tkinter possède sa propre boucle d'événements (mainloop). Exécuter
    asyncio.run() dans le même thread la bloquerait ; dans un thread
    séparé, les callbacks qui mettent à jour des widgets tkinter
    nécessitent after() de toute façon. threading.Queue + thread daemon
    donne exactement le même comportement asynchrone sans ce conflit,
    et sans dépendance externe supplémentaire.
    """

    def __init__(self, engine_ref):
        self._engine = engine_ref
        self._q: _queue_module.PriorityQueue = _queue_module.PriorityQueue()
        self._running = False
        self._current_job: Optional[SearchJob] = None
        self._lock = _threading_module.Lock()
        self._worker: Optional[_threading_module.Thread] = None
        self._sequence = 0  # pour stabiliser le tri PriorityQueue

    def start(self):
        if self._running:
            return
        self._running = True
        self._worker = _threading_module.Thread(target=self._run, daemon=True)
        self._worker.start()

    def stop(self):
        self._running = False
        self._q.put((0, 0, None))  # poison pill

    def enqueue(self, job: SearchJob):
        with self._lock:
            self._sequence += 1
            seq = self._sequence
        # PriorityQueue trie par (priority, sequence) — FIFO à priorité égale
        self._q.put((job.priority, seq, job))

    def enqueue_batch(self, jobs: list[SearchJob]):
        """Enfile plusieurs dorks d'un coup — utile pour la bibliothèque."""
        for i, job in enumerate(jobs):
            job.priority = job.priority + (i * 0.001)  # ordre stable
            self.enqueue(job)

    @property
    def queue_size(self) -> int:
        return self._q.qsize()

    @property
    def is_busy(self) -> bool:
        return self._current_job is not None

    def __repr__(self) -> str:
        status = "actif" if self._running else "arrêté"
        return f"<SearchQueue {status} | en attente={self.queue_size} | en cours={'oui' if self.is_busy else 'non'}>"

    def clear(self):
        while not self._q.empty():
            try:
                self._q.get_nowait()
                self._q.task_done()
            except _queue_module.Empty:
                break

    def _run(self):
        while self._running:
            try:
                item = self._q.get(timeout=1.0)
                _, _, job = item
                if job is None:
                    break
                self._current_job = job
                self._process(job)
                self._current_job = None
                self._q.task_done()
            except _queue_module.Empty:
                continue
            except Exception:
                self._current_job = None

    def _process(self, job: SearchJob):
        try:
            results = self._engine.search(
                job.query,
                engines=job.engines,
                max_results=job.max_results,
                on_result=job.on_result,
            )
            if job.on_complete:
                job.on_complete(job.job_id, results)
        except Exception as e:
            if job.on_error:
                job.on_error(job.job_id, str(e))


class MultiEngine:
    """Orchestrateur multi-moteurs avec rate limiting adaptatif et file de jobs."""

    def __init__(self, config: dict):
        self.engines: dict[str, object] = {}
        self._setup(config)
        self.queue = SearchQueue(self)
        self.queue.start()

    def _setup(self, config: dict):
        if config.get("google_api_key") and config.get("google_cse_id"):
            self.engines["Google CSE"] = GoogleCSEEngine(
                config["google_api_key"], config["google_cse_id"]
            )
        if config.get("bing_api_key"):
            self.engines["Bing"] = BingEngine(config["bing_api_key"])
        if config.get("shodan_api_key"):
            self.engines["Shodan"] = ShodanEngine(config["shodan_api_key"])
        self.engines["DuckDuckGo"] = DuckDuckGoEngine()

    def search(
        self,
        query: str,
        engines: Optional[list[str]] = None,
        max_results: int = 10,
        on_result: Optional[Callable] = None
    ) -> dict[str, list[SearchResult]]:
        targets = engines or list(self.engines.keys())
        all_results: dict[str, list[SearchResult]] = {}

        for name in targets:
            engine = self.engines.get(name)
            if not engine:
                if on_result:
                    on_result(name, [], error=f"Moteur '{name}' non configuré (clé API manquante)")
                continue
            try:
                if name == "Google CSE":
                    results = engine.search(query, num=max_results)
                elif name == "Bing":
                    results = engine.search(query, count=max_results)
                elif name == "Shodan":
                    results = engine.search(query)
                else:
                    results = engine.search(query, max_results=max_results)

                all_results[name] = results
                if on_result:
                    on_result(name, results)

            except RateLimitError as e:
                all_results[name] = []
                if on_result:
                    on_result(name, [], error=str(e))
            except ValueError as e:
                # Erreur de configuration (clé invalide, quota, etc.)
                all_results[name] = []
                if on_result:
                    on_result(name, [], error=f"Config : {e}")
            except Exception as e:
                all_results[name] = []
                if on_result:
                    on_result(name, [], error=f"Erreur inattendue : {e}")

        return all_results

    @property
    def available_engines(self) -> list[str]:
        return list(self.engines.keys())
