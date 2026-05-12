"""
네이버 뉴스 수집 서비스

- 네이버 검색 API 호출 -> 기사 목록 수집 -> TextPreprocessor로 정제
- 입력: query(str), display(int)
- 출력: list[dict] (title/description 정제 완료된 기사 목록)
- 외부 의존성: 네이버 검색 API, settings.naver_client_id/secret, TextPreprocessor
- metadata: query, fetched_at, elapsed_sec 포함
"""
import time
import httpx
from loguru import logger

from app.core.settings import settings
from app.services.text_preprocessor import TextPreprocessor

# 네이버 검색 API endpoint
_NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"

class NaverNewsFetcher:
    """네이버 뉴스 API 클라이언트
    - API 호출 + 응답 파싱 + 전저치 위임
    - 전처리 로직은 TextPreprocessor에서만하므로 이 클래스는 수집만 담당
    """

    def __init__(self, preprocessor: TextPreprocessor) -> None:
        """전처리 객체를 외부에서 주입받음 (DI)"""
        self._preprocessor = preprocessor
    
    def fetch(self, query: str, display: int = 100) -> list[dict]:
        """네이버 뉴스 API로 뉴스 수집 + 정제된 기사 목록/matadata 반환

        Args:
            query: 검색 키워드 (예: "AI", "반도체")
            display: 수집할 기사 수 (최대 100)
        
        Returns:
            기사 dict 목록. 각 항목: title, description pubDate, link
        
        Reaises:
            httpx.HTTPStatusError: API 호출 실패 시
        """
        start = time.perf_counter()
        logger.info("뉴스 수집 시작 | query={q}, display={d}", q=query, d=display)

        # 인증 헤더 구성
        headers: dict[str, str] = {
            "X-Naver-Client-Id": settings.naver_client_id,
            "X-Naver-Client-Secret": settings.naver_client_secret,
        }
        params: dict[str, str | int] = {
            "query": query,
            "display": min(display, 100),   # 100 초과 시 API 오류 방지
            "sort": "date",     # 최신순 정렬
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get(_NAVER_NEWS_URL, headers=headers, params=params)
            # HTTP 오류 발생 시 즉시 예외
            response.raise_for_status()
        
        article_list: list[dict] = response.json().get("items", [])

        # 전처리는 TextPreprocessor에 위임
        articles: list[dict] = [
            self._preprocessor.clean_article(item) for item in article_list
            if item.get("title") and item.get("description")
        ]

        elapsed = time.perf_counter() - start
        logger.info(
            "뉴스 수집 완료 | query={q}, count={c}, elapsed={e:.2f}s",
            q=query, c=len(articles), e=elapsed,
        )
        return articles