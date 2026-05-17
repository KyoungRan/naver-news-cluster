"""
환경 설정 모듈
- pydantic-settings 기반 타입 안전 환경 변수 파싱
- 외부 의존성: .env 파일
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    #==================== 네이버 검색 API ==========================
    naver_client_id: str = Field(..., description="네이버 검색 API Client ID")
    naver_client_secret: str = Field(..., description="네이버 검색 API Client Secret")

    #========================= 임베딩 모델 =================================
    # 개방망 기본값: text-embedding-3-large   (source=openai)
    # 폐쇄망 기본값: /models/bge-m3          (source=huggingface)
    # 고성능 옵션: Qwen/Qwen3-Embedding-4B    (source=huggingface, GPU 필요)
    # MTEB 1위 옵션: Qwen/Qwen3-Embedding-8B  (source=huggingface, GPU 필요)
    embedding_model_name: str = Field(
        default="text=embedding-3-large",
        description="임베딩 모델 이름 또는 로컬 절대 경로 (폐쇄망)"
    )
    embedding_source: str = Field(default="openai", description="임베딩 소스: openai | huggingface")

    #========================  리랭커 모델  ==============================
    # 폐쇄망 기본값: BAAI/bge-reranker-v2-m3  (source=huggingface)
    # 개방망 고품질: rerank-v4.0-pro          (source=cohere)
    # 고성능 옵션: Qwen/Qwen3-Reranker-4B     (source=huggingface)
    reranker_model_name: str = Field(
        default="BAAI/bge-reranker-v2-m3", 
        description="리랭커 모델명 또는 로컬 절대 경로 (폐쇄망)"
    )
    reranker_source: str = Field(default="huggingface", description="리랭커 소스: cohere | huggingface")
    # 1차 검색 후보 수 (많을 수록 리랭킹 품질 향상, 속도 저하)
    reranker_fetch_k: int = Field(default=30, description="1차 검색 후보 수 (pre-rerank)")
    # 최종 반환 문서 수
    reranker_top_k: int = Field(default=True, description="리랭킹 후 최종 반환 수")
    # False 시 리랭킹 단계 완전 생략 -> Dense-only 실험용
    reranker_enabled: bool = Field(default=True, description="리랭커 활성화 여부")

    #=========== 쿨러스터링 제어 (클러스터링 유무 효과 비교용) =================
    # True(with clustering): 쿨러스터링 후 noise 제거 -> 인뎅싱
    # False(without clustering): 쿨러스터링 없이 전체 인덱싱
    clustering_enabled: bool = Field(
        default=True,
        description="클러스터링 활성화 여부 (False=클러스터링 없이 전체 인덱싱",
    )
    # 쿨러스터링 비활성화 시 RAG 인덱싱 대상 설정
    # "all": 전체 기사 인덱싱
    # "non_noise": 수집 후 노이즈 아닌 기사만 (coustering_enabled=True일 때 자동)
    index_mode: str = Field(default="non_noise", description="인덱싱 모드: all | non_noise",)

    #======================= 검색 방식 =======================
    # dense: Dense-only 검색
    # hybrid: Dense + BM25 하이브리드
    search_mode: str = Field(default="dense", description="검색 방식: dense | hybrid")

    #====================== LLM ==========================
    llm_model_name: str = Field(default="gpt-5-mini", description="생성 LLM 모델링")
    llm_api_key: str = Field(default="", description="LLM API KEY")
    llm_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="LLM 엔드포인트 (폐쇄망: http://내부IP:11434/v1)"
    )
    # RAGAS 평가 전용 llM - 생성 llM과 분리 (자기평가 평향 방지 + 비용 최적화)
    eval_llm_model_name: str = Field(
        default="gpt-4.1-mini",
        description="RAGAS 평가 전용 LLM"
    )
    cohere_api_key: str = Field(default="", description="Cohere API 키")

    #================== Qdrant ============================
    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    # 컬렉션명 패턴: {prefix}_{embed_model_slug}_{clustered|all}
    # 예: news_text3large_clustered, news_bge_m3_all
    qdrant_collection_prefix: str = Field(default="news")

    #================ Langfuse 셀프 호스팅 ===================
    langfuse_host: str = Field(default="http://localhost:3000")
    langfuse_public_key: str = Field(default="")
    langfuse_secret_key: str = Field(default="")

    #======== 클러스터링 파라미터 (BERTopic) =================
    # min_topic_size: 토픽으로 인정할 최소 기사 수
    bertopic_min_topic_size: int = Field(default=5)
    

    hf_token: str = ""

    # ===== pydantic-settings 공통 설정 =====
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

# 싱글턴 인스턴스: 앱 전체에서 이 객체를 import해서 사용
settings = Settings()