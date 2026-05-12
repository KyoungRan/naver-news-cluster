"""
환경 설정 모듈
- pydantic-settings 기반 타입 안전 환경 변수 파싱
- 외부 의존성: .env 파일
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 네이버 검색 API
    naver_client_id: str
    naver_client_secret: str

    # 임베딩 모델 경로
    embedding_model_path: str = "BAAI/bge-m3"

    # Langfuse 셀프 호스팅
    langfuse_host: str = "http://localhost:3000"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""

    # 클러스터링 파라미터
    # min_topic_size: 토픽으로 인정할 최소 기사 수
    bertopic_min_topic_size: int = 3
    
    hf_token: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

# 싱글턴 인스턴스: 앱 전체에서 이 객체를 import해서 사용
settings = Settings()
