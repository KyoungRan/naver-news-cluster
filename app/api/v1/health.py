"""
헬스체크 라우터
- Docker HEALTHCHECK, 로드밸런서 생존 확인용
- /api/v1/health
"""
from fastapi import APIRouter
from app.core.dependencies import get_cluster_service, get_news_fetcher

router = APIRouter(tags=["system"])

@router.get("/health")
async def health_check() -> dict[str, str]:
    """서버 + 서비스 초기화 상태 확인"""
    get_news_fetcher()
    get_cluster_service()
    return {"status": "ok"}