"""
News Clustering Service
- BERTopic + 한국어 Mecab CountVectorizer 기반 토픽 클러스터링
- 입력: articles(list[dict])
- 출력: cluster_result(dict)
- 외부 의존성: bertopic, hdbscan, konlpy, infra.embedding
- 단계별 elapsed 시간 측정
"""
import time

import numpy as np
from bertopic import BERTopic
from hdbscan import HDBSCAN
from konlpy.tag import Mecab
from loguru import logger
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP

from app.core.settings import settings
from app.infra.embedding import EmbeddingModel
from app.services.text_preprocessor import KO_STOPWORDS

class NewsClusterService:
    """BERTopic 기반 뉴스 토픽 클러스터링 서비스"""

    def __init__(self, embedding_model: EmbeddingModel) -> None:
        # 외부에서 주입받은 임베딩 모델 사용
        self._embedding_model = embedding_model

        # 한국어 형태소 분석기 설정
        # Windows에서는 Mecab 미지원 -> Okt()로 교체 필요
        try:
            morpheme_analyzer = Mecab()
            logger.info("형태소 분석기: Mecab 초기화 성공")
        except Exception:
            # Mecab 설치 실패 시 Okt 풀백
            from konlpy.tag import Okt
            logger.warning("Mecab 초기화 실패 -> Okt 폴백 사용")
            morpheme_analyzer = Okt()
        
        # BERTpoic CountVectorizer에 한국어 형태소 분석기 연결
        # morpheme_analyzer.marphs: 형태소 단위 분리 함수
        self._vectorizer = CountVectorizer(
            tokenizer=morpheme_analyzer.nouns,  # 명사만 추출 -> 조사/어미 원천 차단
            token_pattern=None,     # tokenizer 사용 시 None 필수
            lowercase=True,
            stop_words=KO_STOPWORDS,    # text_preprocessor에서 관리
            min_df=2,  # 최소 2개 문서에 등장한 단어만 사용
            max_df=0.9,
        )

        # random_state 고정: 동일 입력 -> 동일 결과 보장
        umap_model = UMAP(
            n_components=5,
            n_neighbors=15,
            min_dist=0.0,
            metric="cosine",
            random_state=42,
        )
        hdbscan_model = HDBSCAN(
            min_cluster_size=settings.bertopic_min_topic_size,
            min_samples=1,
            prediction_data=True,
        )

        # BERTopic 모델 구성
        self._topic_model = BERTopic(
            language="multilingual",
            min_topic_size=settings.bertopic_min_topic_size,
            vectorizer_model=self._vectorizer,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            calculate_probabilities=False,
            verbose=False,
        )
    
    def cluster(self, articles: list[dict]) -> dict:
        """
        기사 목록을 토픽별로 쿨러스터링

        Args:
            articles: 네이버 API 반환 기사 dict 목록
        
        Returns:
            cluster_result: {
                "topic_ids": list[int],     # -1 = 노이즈(미분류)
                "topics": dict[int, list[str]],     # 토픽별 대표 키워드
                "articles_with_topic": list[dict]
            }
        """
        total_start = time.perf_counter()

        if not articles:
            logger.warning("클러스터링 입력 기사 없음")
            return {
                "topic_ids": [],
                "total_articles": 0,
                "total_topics": 0,
                "noise_count": 0,
                "topics": {},
                "articles_with_topic": [],
                "metadata": {},
            }
        
        # 기사 텍스트 구성: 제목 + 설명 결합 (단문 보완)
        texts: list[str] = [
            f"{a.get('title', '')} {a.get('description', '')}".strip()
            for a in articles
        ]

        #======================== 1. 임베딩=================================
        t0 = time.perf_counter()
        logger.info("임베딩 시작 | 기사 수={n}", n=len(texts))

        # EmbeddingModel.encode() 반환값이 list일 수 있음
        # BERTopic은 반드시 np.ndarray 타입 필요
        raw_embeddings = self._embedding_model.encode(texts)
        embeddings: np.ndarray = np.array(raw_embeddings)
        embed_elapsed = time.perf_counter() - t0
        logger.info("임베딩 완료 | elapsed={e:.2f}s", e=embed_elapsed)

        #================= 2. BERTopic 클러스터링 =======================
        t0 = time.perf_counter()
        logger.info("BBERTopic 클러스터링 시작")
        topic_ids: list[int]
        topic_ids, _ = self._topic_model.fit_transform(texts, embeddings)
        cluster_elapsed = time.perf_counter() - t0
        logger.info("BERTopic 완료 | elapsed={e:.2f}s", e=cluster_elapsed)

        #===============결과: 토픽별 상위 키워드 추출 =====================
        topic_info = self._topic_model.get_topics()
        topics: dict[int, list[str]] = {
            topic_id: [word for word, _ in words[:5]]
            for topic_id, words in topic_info.items()
            if topic_id != -1   # -1(노이즈) 토픽은 키워드 의미 없음
        }

        # 기사에 topic_id 부여
        articles_with_topic: list[dict] = [
            {**article, "topic_id": int(tid)}
            for article, tid in zip(articles, topic_ids)
        ]

        noise_count: int = topic_ids.count(-1)
        noise_ratio: float = noise_count / len(topic_ids)
        total_elapsed = time.perf_counter() - total_start

        logger.info(
            "클러스터링 완료 | 토픽={t}, 노이즈={n}({r:.1%}), 총소요={e:2f}s",
            t=len(topics),
            n=noise_count,
            r=noise_ratio,
            e=total_elapsed,
        )

        # 노이즈 비율 30% 초과 시 경고
        if noise_ratio > 0.3:
            logger.warning(
                "노이즈 비율 {r:.1%} 초과 -> bertopic_min_topic_size 조정 권장",
                r=noise_ratio,
            )
        
        return {
            "topic_ids": [int(t) for t in topic_ids],
            "total_articles": len(articles),
            "total_topics": len(topics),
            "noise_count": noise_count,
            "topics": topics,
            "articles_with_topic": articles_with_topic,
            # metadata: 각 단계 소요 시간 확인됨
            "metadata": {
                "embed_elapsed_sec": round(embed_elapsed, 2),
                "cluster_elapsed_sec": round(cluster_elapsed, 2),
                "total_elapsed_sec": round(total_elapsed, 2),
            },
        }