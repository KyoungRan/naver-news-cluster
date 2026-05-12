"""
의존성 주입 컨테이너
- init_services(): lifespan에서 앱 시작 시 1회 호출
- teardown_services(): 앱 종료 시 리소스 정리
- get_news_fetcher() / get_cluster_service(): FastAPI Depends()로 라우터에 주입
- 입력: 없음(환경변수 + settings 기반 자동 구성)
- 출력: NaverNewsFetcher, NewsClusterService 싱글턴 인스턴스
- 외부 의존성: EmbeddingModel, TextPreprocessor, NaverNewsFetcher, NewsClusterService
"""
from loguru import logger

from app.infra.embedding import EmbeddingModel
from app.services.text_preprocessor import TextPreprocessor
from app.services.cluster_service import NewsClusterService
from app.services.news_fetcher import NaverNewsFetcher

# 앱 전체 공유 싱글톤 보관 변수 (None으로 시작, init_services()에서 채워짐)
_preprocessor: TextPreprocessor | None = None
_news_fetcher: NaverNewsFetcher | None = None
_cluster_service: NewsClusterService | None = None

def init_services() -> None:
    """앱 시작 시 한 번만 호출 - 모델 로딩 + 객체 생성"""
    global _preprocessor, _news_fetcher, _cluster_service

    # 1. 전처리기 초기화 
    _preprocessor = TextPreprocessor()
    logger.info("TextPreprocessor 초기화 완료")

    # 2. 임베딩 모델 로드
    logger.info("임베딩 모델 로드 시작...")
    embedding_model = EmbeddingModel()  # 모델 로드 
    logger.info("임베딩 모델 로드 완료")

    # 3. NaverNewsFetcher 생성 - preprocessor 주입 (DI)
    _news_fetcher = NaverNewsFetcher(preprocessor=_preprocessor)
    logger.info("NaverNewsFetcher 초기화 완료")

    # 4. NewsClusterService 생성 - embedding_model 주입 (DI)
    _cluster_service = NewsClusterService(embedding_model=embedding_model)
    logger.info("서비스 초기화 완료")

def teardown_services() -> None:
    """앱 종료 시 리소스 정리
    - 싱글턴 참조 해제
    - 임베딩 모델 메모리는 GC가 처리하므로 명시적 del 불필요
    """
    global _preprocessor, _news_fetcher, _cluster_service
    _preprocessor = None
    _news_fetcher = None
    _cluster_service = None
    logger.info("서비스 정리 완료")

def get_news_fetcher() -> NaverNewsFetcher:
    """FastAPI Depends용 - NaverNewsFetcher 싱글톤 반환. 초기화 전 호출 시 에러"""
    if _news_fetcher is None:
        raise RuntimeError("NaverNewsFetcher가 초기화 되지 않음. init_services()를 먼저 호출해야됨.")
    return _news_fetcher

def get_cluster_service() -> NewsClusterService:
    """FastAPI Depends용 - NewsClusterService 싱글톤 반환. 초기화 전 호출 시 에러"""
    if _cluster_service is None:
        raise RuntimeError("NewsClusterService가 초기화되지 않았음. init_services()를 먼저 호출해야됨")
    return _cluster_service