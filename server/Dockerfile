# FastAPI 분석 서버 — analyzer/ 코어 포함
# 빌드 컨텍스트는 레포 루트: docker build -f server/Dockerfile .
FROM python:3.11-slim

# opencv 런타임(libgl/glib) + 한글 HUD 폰트(analyzer/drawing.py가
# /usr/share/fonts/truetype/nanum/NanumGothic.ttf를 후보로 탐색)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 fonts-nanum \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY server/requirements.txt server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt

COPY golf_swing_analyzer/analyzer golf_swing_analyzer/analyzer
COPY golf_swing_analyzer/reference_db.json golf_swing_analyzer/reference_db.json
COPY server server

WORKDIR /app/server

# SQLite 기본 경로를 볼륨 마운트 지점으로 (compose에서 /data 마운트)
ENV DATABASE_URL=sqlite:////data/golf.db

EXPOSE 8010
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
