"""
클러스터링 API 라우터
- HTTP 라우팅 + 입력 검증
= 서비스 객체는 Depends()로 주입
"""
from fastapi import APIRouter, Depends
from loguru import logger

from app.core.dependencies import get_cluster_service, get_news_fetcher
from app.schemas.cluster import ClusterRequest, ClusterResponse, ClusterMeta
from app.services.cluster_service import NewsClusterService
from app.services.news_fetcher import NaverNewsFetcher

router = APIRouter(prefix="/cluster", tags=["cluster"])

@router.post("/", response_model=ClusterResponse)
async def cluster_news(
    req: ClusterRequest,
    fetcher: NaverNewsFetcher = Depends(get_news_fetcher),
    cluster_service: NewsClusterService = Depends(get_cluster_service),
) -> ClusterResponse:
    """뉴스 수집 -> BERTopic 클러스터링 -> 결과 반환"""

    logger.info("클러스터링 요청 | query={q}, display={d}", q=req.query, d=req.display)

    # 뉴스 수집 (HTML 제거는 fetcher 내부에서 처리)
    articles: list[dict] = fetcher.fetch(query=req.query, display=req.display)

    if not articles:
        logger.warning("수집된 기사 없음 | query={q}", q=req.query)
        return ClusterResponse(
            total_articles=0,
            total_topics=0,
            noise_count=0,
            topics={},
            articles=[],
        )
    
    # 클러스터링
    cluster_result: dict = cluster_service.cluster(articles=articles)

    logger.info(
        "클러스터링 완료 | topics={t}, noise={n}",
        t=cluster_result["total_topics"],
        n=cluster_result["noise_count"],
    )

    return ClusterResponse(
            total_articles=cluster_result["total_articles"],
            total_topics=cluster_result["total_topics"],
            noise_count=cluster_result["noise_count"],
            topics=cluster_result["topics"],
            articles=cluster_result["articles_with_topic"],
            metadata=ClusterMeta(
                embed_elapsed_sec=cluster_result["metadata"]["embed_elapsed_sec"],
                cluster_elapsed_sec=cluster_result["metadata"]["cluster_elapsed_sec"],
                total_elapsed_sec=cluster_result["metadata"]["total_elapsed_sec"]
            )
    )
