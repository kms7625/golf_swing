"""IP 기반 슬라이딩 윈도우 레이트리밋 — 인메모리 단일 프로세스용 (jobs.py와 같은 전제).

멀티 워커로 가면 Redis 카운터로 교체 대상. 프록시 뒤에서는 X-Forwarded-For 첫 항목을 신뢰
(RUNNING.md 배포 구성이 reverse proxy 전제이므로) — 직접 노출 배포에서는 스푸핑 가능함에 유의.
"""
import threading
import time

from fastapi import HTTPException, Request

_windows: dict[str, list[float]] = {}
_lock = threading.Lock()
_MAX_KEYS = 10_000  # 메모리 상한 — 초과 시 전체 리셋(성능보다 안전 우선)


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _allow(key: str, limit: int, per_sec: float) -> bool:
    now = time.time()
    with _lock:
        if len(_windows) > _MAX_KEYS:
            _windows.clear()
        q = _windows.setdefault(key, [])
        cutoff = now - per_sec
        while q and q[0] < cutoff:
            q.pop(0)
        if len(q) >= limit:
            return False
        q.append(now)
        return True


def rate_limited(name: str, limit: int, per_sec: float):
    """FastAPI Depends 팩토리 — 초과 시 429 (서버 메시지는 한국어 원칙)."""

    def dep(request: Request) -> None:
        if not _allow(f"{name}:{_client_ip(request)}", limit, per_sec):
            raise HTTPException(status_code=429, detail="요청이 너무 잦습니다. 잠시 후 다시 시도해주세요.")

    return dep
