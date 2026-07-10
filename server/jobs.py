"""비동기 분석 작업 큐 — 인메모리 단일 프로세스용.

/analyze의 동기 처리(긴 영상 = HTTP 타임아웃)를 대체한다:
클라이언트는 job_id를 받고 GET /jobs/{id}로 진행률을 폴링한다.
진행률은 analyzer/를 수정하지 않기 위해 단계 경계 기준(업로드→트림→포즈분석→스코어)으로만 보고한다.
멀티 워커(prod)로 가면 Redis/DB 큐로 교체 대상 — 단일 uvicorn 프로세스 전제.
"""
import threading
import time
import uuid
from typing import Any, Callable, Optional

_JOB_TTL_SEC = 60 * 60  # 완료 후 1시간 뒤 폐기

_jobs: dict[str, dict[str, Any]] = {}
_lock = threading.Lock()

# 단계 코드는 프론트 i18n 키와 1:1 (job_stage_*) — 서버는 코드만 보낸다
STAGES = ("uploaded", "trimming", "analyzing", "scoring", "done")


def _sweep() -> None:
    now = time.time()
    stale = [k for k, v in _jobs.items() if v.get("finished_at") and now - v["finished_at"] > _JOB_TTL_SEC]
    for k in stale:
        _jobs.pop(k, None)


def create_job() -> str:
    job_id = uuid.uuid4().hex
    with _lock:
        _sweep()
        _jobs[job_id] = {
            "status": "pending",  # pending | running | done | error
            "stage": "uploaded",
            "progress": 5,
            "result": None,
            "error": None,
            "created_at": time.time(),
            "finished_at": None,
        }
    return job_id


def set_stage(job_id: str, stage: str, progress: int) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job is not None:
            job["status"] = "running"
            job["stage"] = stage
            job["progress"] = progress


def finish(job_id: str, result: Any) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job is not None:
            job.update(status="done", stage="done", progress=100, result=result, finished_at=time.time())


def fail(job_id: str, message: str) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job is not None:
            job.update(status="error", error=message, finished_at=time.time())


def get_job(job_id: str) -> Optional[dict[str, Any]]:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        return {k: job[k] for k in ("status", "stage", "progress", "result", "error")}


def run_in_thread(job_id: str, target: Callable[[], None]) -> None:
    """작업을 데몬 스레드로 실행 — 예외는 fail()로 수렴."""

    def _wrap():
        try:
            target()
        except Exception:  # noqa: BLE001 — 상세는 서버 로그로, 클라이언트에는 일반 메시지
            import logging

            logging.getLogger("golf.jobs").exception("job %s failed", job_id)
            fail(job_id, "분석 중 오류가 발생했습니다. 영상 형식을 확인하고 다시 시도해주세요.")

    threading.Thread(target=_wrap, daemon=True).start()
