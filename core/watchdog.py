"""Mode surveillance : alerte quand de nouveaux résultats apparaissent."""

import hashlib
import json
import os
import queue
import random
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Callable, Optional

import requests


def _hash_result(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()


def _hash_result_set(results: list) -> str:
    """Hash stable de l'ensemble des résultats d'un scan (ordre insensible)."""
    digests = sorted(_hash_result(r.url, r.title) for r in results)
    return hashlib.sha256("|".join(digests).encode()).hexdigest()


@dataclass
class WatchdogJob:
    id: str
    name: str
    dork: str
    engines: list[str]
    interval_minutes: int
    webhook_url: str = ""
    discord_webhook: str = ""
    active: bool = True
    last_run: str = ""
    last_status: str = ""
    known_urls: list[str] = field(default_factory=list)
    last_result_hash: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class _ScanTask:
    """Tâche interne placée dans la file du WatchdogManager."""
    __slots__ = ("job", "stop_event")

    def __init__(self, job: WatchdogJob, stop_event: threading.Event):
        self.job = job
        self.stop_event = stop_event


class WatchdogManager:
    """
    Gère les tâches de surveillance de dorks.

    Architecture : un seul thread worker draine une Queue de tâches de scan.
    Les timers par job tournent dans leurs propres threads légers (Event.wait),
    mais tous les appels réseau passent par le worker unique — pas de concurrence
    sur les APIs, pas de freeze UI.
    """

    POISON = object()

    def __init__(self, storage_path: str, search_fn: Callable,
                 on_status: Optional[Callable] = None):
        self.storage_path = storage_path
        self.search_fn    = search_fn
        self.on_status    = on_status  # callback(job_id, status_str) pour l'UI

        self.jobs: dict[str, WatchdogJob] = {}
        self._stop_events:  dict[str, threading.Event]  = {}
        self._timer_threads: dict[str, threading.Thread] = {}

        # File unique drainée par le worker
        self._scan_queue: queue.Queue[_ScanTask | object] = queue.Queue()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

        self._load()

    # ------------------------------------------------------------------ #
    # Persistance                                                          #
    # ------------------------------------------------------------------ #

    def _load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                item.setdefault("last_status", "")
                job = WatchdogJob(**item)
                self.jobs[job.id] = job

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(
                [asdict(j) for j in self.jobs.values()],
                f, indent=2, ensure_ascii=False
            )

    # ------------------------------------------------------------------ #
    # API publique                                                         #
    # ------------------------------------------------------------------ #

    def add_job(self, job: WatchdogJob):
        self.jobs[job.id] = job
        self._save()
        if job.active:
            self._start_timer(job)

    def remove_job(self, job_id: str):
        self._cancel_timer(job_id)
        self.jobs.pop(job_id, None)
        self._save()

    def toggle_job(self, job_id: str):
        job = self.jobs.get(job_id)
        if not job:
            return
        job.active = not job.active
        if job.active:
            self._start_timer(job)
        else:
            self._cancel_timer(job_id)
        self._save()

    def start_all(self):
        for job in self.jobs.values():
            if job.active:
                self._start_timer(job)

    def stop_all(self):
        for job_id in list(self._timer_threads.keys()):
            self._cancel_timer(job_id)
        self._scan_queue.put(self.POISON)

    # ------------------------------------------------------------------ #
    # Timers (un par job, légers — ils ne font qu'enqueuer)               #
    # ------------------------------------------------------------------ #

    def _start_timer(self, job: WatchdogJob):
        if job.id in self._timer_threads and self._timer_threads[job.id].is_alive():
            return
        stop = threading.Event()
        self._stop_events[job.id] = stop
        t = threading.Thread(
            target=self._timer_loop, args=(job, stop), daemon=True
        )
        self._timer_threads[job.id] = t
        t.start()

    def _cancel_timer(self, job_id: str):
        ev = self._stop_events.pop(job_id, None)
        if ev:
            ev.set()

    def _timer_loop(self, job: WatchdogJob, stop: threading.Event):
        """
        Attend l'intervalle puis pousse un ScanTask dans la file.
        Ne fait AUCUN appel réseau — juste du scheduling.
        """
        while not stop.is_set():
            self._scan_queue.put(_ScanTask(job, stop))
            base   = job.interval_minutes * 60
            jitter = base * random.uniform(-0.10, 0.10)
            stop.wait(max(30, base + jitter))

    # ------------------------------------------------------------------ #
    # Worker unique — tous les appels réseau passent ici                  #
    # ------------------------------------------------------------------ #

    def _worker_loop(self):
        while True:
            item = self._scan_queue.get()
            if item is self.POISON:
                break
            task: _ScanTask = item
            if not task.stop_event.is_set() and task.job.active:
                self._execute_scan(task.job)
            self._scan_queue.task_done()

    def _execute_scan(self, job: WatchdogJob):
        try:
            self._set_status(job, "scan en cours...")
            results = self.search_fn(job.dork, job.engines)
            all_results = [r for ers in results.values() for r in ers]
            current_hash = _hash_result_set(all_results)

            if current_hash == job.last_result_hash:
                job.last_run = datetime.now().isoformat()
                self._set_status(job, "aucun changement")
                self._save()
                return

            new_urls = []
            for r in all_results:
                if r.url not in job.known_urls:
                    new_urls.append(r.url)
                    job.known_urls.append(r.url)

            job.last_result_hash = current_hash
            job.last_run = datetime.now().isoformat()

            if new_urls:
                self._set_status(job, f"{len(new_urls)} nouveau(x) résultat(s)")
                self._notify(job, new_urls)
            else:
                self._set_status(job, "aucun changement")

            self._save()

        except Exception as e:
            self._set_status(job, f"erreur : {e}")

    def _set_status(self, job: WatchdogJob, status: str):
        job.last_status = status
        if self.on_status:
            self.on_status(job.id, status)

    # ------------------------------------------------------------------ #
    # Notifications                                                        #
    # ------------------------------------------------------------------ #

    def _notify(self, job: WatchdogJob, new_urls: list[str]):
        message = self._build_message(job, new_urls)
        if job.discord_webhook:
            self._send_discord(job.discord_webhook, message)
        if job.webhook_url:
            self._send_webhook(
                job.webhook_url,
                {"job": job.name, "dork": job.dork, "new_urls": new_urls}
            )

    def _build_message(self, job: WatchdogJob, new_urls: list[str]) -> str:
        lines = [
            f"**Dorking Watchdog** — {job.name}",
            f"**Dork:** `{job.dork}`",
            f"**Nouveaux resultats ({len(new_urls)}) :**",
        ]
        for url in new_urls[:10]:
            lines.append(f"* {url}")
        if len(new_urls) > 10:
            lines.append(f"... et {len(new_urls) - 10} autres")
        return "\n".join(lines)

    def _send_discord(self, webhook_url: str, message: str):
        try:
            requests.post(webhook_url, json={"content": message}, timeout=10)
        except Exception:
            pass

    def _send_webhook(self, webhook_url: str, payload: dict):
        try:
            requests.post(webhook_url, json=payload, timeout=10)
        except Exception:
            pass
