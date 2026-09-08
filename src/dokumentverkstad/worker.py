from __future__ import annotations

from dataclasses import dataclass
from threading import Event, Thread
from time import perf_counter, sleep
from typing import Callable

from .archive import Archive
from .config import AppConfig
from .index import rebuild_document_index
from .ingest import IngestResult, process_ingest_source


LogSink = Callable[[str], None]
AiJobRunner = Callable[[], str | None]
AiRecovery = Callable[[], tuple[str, ...]]


@dataclass(frozen=True)
class WorkerCycleResult:
    ingest_results: tuple[IngestResult, ...] = ()
    ai_run_id: str = ""

    @property
    def did_work(self) -> bool:
        return bool(self.ingest_results or self.ai_run_id)


def process_worker_cycle(
    archive: Archive,
    config: AppConfig,
    run_next_ai_job: AiJobRunner | None = None,
    log: LogSink | None = None,
) -> WorkerCycleResult:
    started = perf_counter()
    ingest_results = tuple(
        process_ingest_source(
            archive=archive,
            ingest_source=config.ingest_source,
            runtime_root=config.runtime_root,
            log=log,
        )
    )
    if any(result.created for result in ingest_results):
        rebuild_document_index(archive, config.runtime_root)

    ai_run_id = run_next_ai_job() if run_next_ai_job else None
    if ingest_results or ai_run_id:
        _log(
            log,
            "worker cycle completed "
            f"ingest_items={len(ingest_results)} "
            f"ai_run_id={ai_run_id or ''} "
            f"duration_ms={(perf_counter() - started) * 1000:.1f}",
        )
    return WorkerCycleResult(
        ingest_results=ingest_results,
        ai_run_id=ai_run_id or "",
    )


def run_worker_loop(
    archive: Archive,
    config: AppConfig,
    run_next_ai_job: AiJobRunner | None = None,
    recover_ai_jobs: AiRecovery | None = None,
    log: LogSink | None = None,
    poll_interval_seconds: float = 5.0,
    stop_event: Event | None = None,
) -> None:
    stop_event = stop_event or Event()
    recovered = recover_ai_jobs() if recover_ai_jobs else ()
    _log(log, f"worker started recovered_ai_runs={len(recovered)}")
    while not stop_event.is_set():
        try:
            result = process_worker_cycle(
                archive=archive,
                config=config,
                run_next_ai_job=run_next_ai_job,
                log=log,
            )
        except Exception as error:
            _log(log, f"worker cycle failed error={error.__class__.__name__}")
            stop_event.wait(poll_interval_seconds)
            continue
        if result.did_work:
            continue
        stop_event.wait(poll_interval_seconds)
    _log(log, "worker stopped")


class BackgroundWorker:
    def __init__(
        self,
        archive: Archive,
        config: AppConfig,
        run_next_ai_job: AiJobRunner | None = None,
        recover_ai_jobs: AiRecovery | None = None,
        log: LogSink | None = None,
        poll_interval_seconds: float = 5.0,
    ) -> None:
        self._stop_event = Event()
        self._thread = Thread(
            target=run_worker_loop,
            kwargs={
                "archive": archive,
                "config": config,
                "run_next_ai_job": run_next_ai_job,
                "recover_ai_jobs": recover_ai_jobs,
                "log": log,
                "poll_interval_seconds": poll_interval_seconds,
                "stop_event": self._stop_event,
            },
            daemon=True,
            name="dokumentverkstad-worker",
        )

    def start(self) -> None:
        self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        self._stop_event.set()
        self._thread.join(timeout=timeout)


def _log(log: LogSink | None, message: str) -> None:
    if log:
        log(message)
