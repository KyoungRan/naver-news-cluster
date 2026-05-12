# build stage
FROM python:3.12-slim AS builder

# uv 설치
RUN pip install uv

WORKDIR /app

# 의존성 파일 먼저 복사 (레이어 캐시 활용)
COPY pyproject.toml uv.lock ./

# 의존성 설치 (--no-dev: 개발 패키지 제외)
RUN uv sync --no-dev

# runtime stage
FROM python:3.12-slim

# KoNLPy MeCab 사용 시 필요한 시스템 패키지
# https://konlpy.org/en/latest/install/
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy build stage pakeage
COPY --from=builder /app/.venv ./.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

RUN mkdir -p logs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
