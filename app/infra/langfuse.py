"""
Langfuse 추적 인프라 계층
- 파이프라인 호출 tracing 및 metric 기록
- 입력: trace 이름, 입력값, 출력값
"""
from langfuse import Langfuse
from loguru import logger

from app.core.settings import settings

def get_langfuse_client() -> Langfuse | None:
    """Langfuse 클라이언트를 반환
    
    설정값이 없으면 None을 반환하고 로깅만 수행.
    (개발 환경에서 Langfuse 서버 없이도 동작 가능하도록)
    """
    #public_key가 없으면 관찰성 비활성화
    if not settings.langfuse_public_key:
        logger.warning("Langfuse public_key 미설정 -> 관찰성 비활성화")
        return None
    
    return Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )

langfuse_client: Langfuse | None = get_langfuse_client()
