"""
임베딩 모델 인프라 계층
- sentence-transformers 기반 텍스트 -> 벡터 변환
- 입력: list[str] (기사 텍스트 목록)
- 출력: list[list[float]] (벡터 목록)
- 외부 의존성: sentence-transformers, settings.embedding_model_path
"""
from loguru import logger
from sentence_transformers import SentenceTransformer

from app.core.settings import settings

class EmbeddingModel:
    """임베딩 모델 래퍼 클래스

    생성자에서 모델을 1회 로드하고, encode()로 벡터를 반환한다
    개방망/폐쇄망 전환은 settings.embedding_model_path로만 처리한다
    """

    def __init__(self) -> None:
        # 모델 경로는 반드시 settings에서 주입
        model_path: str = settings.embedding_model_path
        logger.info("임베딩 모델 로드 시작 | path={path}", path="model_path")
        self._model: SentenceTransformer = SentenceTransformer(model_path)
        logger.info("임베딩 모델 로드 완료 | path={path}", path="model_path")
    
    def encode(self, texts: list[str]) -> list[list[float]]:
        """텍스트 목록을 벡터 목록으로 변환한다
        
        Args:
            texts: 임베딩할 텍스트 목록
        
        Returns:
            각 텍스트에 대한 float 벡터 목록
        """
        # show_progress_bar=Flase: API 응답 로그를 깔끔하게 유지
        vectors = self._model.encode(texts, show_progress_bar=False)
        return vectors.tolist()
