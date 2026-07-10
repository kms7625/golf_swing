"""테이블 정의 — users / swings (상용화_검토보고서 5-2 최소 스키마 초안 기준).

영상 원본은 저장하지 않는다(개인정보처리방침 '원본 미보관' 원칙).
swings.payload에는 ResultScreen이 소비하는 필드만 담는다
(score/issues/summary/wrist_y_history/phase_boundaries/rep_frames/fps/eff_sample)
— frame_data는 결과 재표시에 불필요해 제외, 행당 용량을 수백 KB 이내로 유지.
"""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    # AI 코칭 무료 횟수 계량 — "YYYY-MM"이 바뀌면 사용량 리셋
    coaching_month: Mapped[str] = mapped_column(String(7), default="")
    coaching_used: Mapped[int] = mapped_column(Integer, default=0)

    swings: Mapped[list["Swing"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Swing(Base):
    __tablename__ = "swings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    video_name: Mapped[str] = mapped_column(String(255), default="")
    score: Mapped[float] = mapped_column(Float)
    # 결과 화면 재구성용 전체 페이로드(JSON) — 서버 응답 한국어 원본 그대로 보존(golf-ui-ux B1)
    payload: Mapped[dict] = mapped_column(JSON)
    # 추이 차트용으로 자주 조회되는 지표는 컬럼으로 승격
    spine_angle_delta: Mapped[float] = mapped_column(Float, default=0.0)
    x_factor: Mapped[float] = mapped_column(Float, default=0.0)
    shoulder_rotation_max: Mapped[float] = mapped_column(Float, default=0.0)
    feedback: Mapped[str] = mapped_column(Text, default="")  # AI 코칭 리포트(생성된 경우)

    user: Mapped[User] = relationship(back_populates="swings")
