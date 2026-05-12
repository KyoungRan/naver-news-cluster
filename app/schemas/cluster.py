"""
클러스터링 API 요청/응답 스키마
- extra="forbid": 정의되지 않는 필드 입력 시 422 반환
"""
from pydantic import BaseModel, ConfigDict, Field

class ClusterRequest(BaseModel):
    """뉴스 클러스터링 요청"""
    query: str = Field(..., description="검색 키워드", examples=["AI", "LLM", "반도체"])
    display: int = Field(default=100, ge=1, le=100, description="수집 기사 수 (최대 100)")

    model_config = ConfigDict(extra="forbid")

class ClusterResponse(BaseModel):
    """뉴스 클러스터링 응답"""
    total_articles: int = Field(description="수집된 전체 기사 수")
    total_topics: int = Field(description="클러스터링된 토픽 수 (노이즈 제외)")
    noise_count: int = Field(description="노이즈(-1)로 분류된 기사 수")
    # int 키: JSON 직렬화 시 자동으로 문자열 키로 변환됨
    topics: dict[int, list[str]] = Field(description="토픽 ID -> 키워드 목록")
    articles: list[dict] = Field(description="기사 목록 (topic_id 포함)")

class ClusterMeta(BaseModel):
    """클러스터링 단계별 소요 시간"""
    embed_elapsed_sec: float = Field(description="임베딩 소요시간")
    cluster_elapsed_sec: float = Field(description="클러스터링 소요시간")
    total_elapsed_sec: float = Field(description="총 소요시간")