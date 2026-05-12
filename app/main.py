"""
FastAPI 어플리케이션 진입점
- 앱 초기화 + 라우터 등록
- lifespan: 무거운 리소스(임베딩 모델)를 앱 시작 시 1회 로드
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1.cluster import router as cluster_router
from app.api.v1.health import router as health_router
from app.core.dependencies import init_services, teardown_services

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """어 시작/종료 실행되는 lifespan 핸들러

    yield 전: 앱 시작 (임베딩 모델 로드 등 무거운 객체 초기화)
    yield 후: 앱종ㅈ료 (리소스 정리)
    """
    # 앱 시작
    logger.info("앱 시작 | 서비스 초기화 중...")
    init_services()     # 임베딩 모델 + 서비스 객체 초기화
    logger.info("앱 시작 완료")

    yield

    # 앱 종료
    logger.info("앱 종료 | 리소스 정리 중...")
    teardown_services()
    logger.info("앱 종료 완료")

app = FastAPI(
    title="Naver News Cluster API",
    description="네이버 뉴스 API + BERTopic 클러스터링 파이프라인",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 설정 - 개발 중전 전체 허용, 운영 시 origins 제한 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 라우터 등록
app.include_router(health_router, prefix="/api/v1")
app.include_router(cluster_router, prefix="/api/v1")