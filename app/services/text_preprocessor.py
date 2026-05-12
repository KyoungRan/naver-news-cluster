"""
텍스트 전처리 모듈
- 네이저 뉴스 API 응답의 HTML/특수문자 정제
- BERTopic CountVectorizer용 불용어(stopwords) 정의
- 입력: 원시 문자열(str) 또는 기사(dict)
- 출력: 정제된 문자열(str)
- 외부의존성: 없음
"""
import re
from loguru import logger

# =====================================================
# 한국어 뉴스 특화 불용어(stopwords) 목록
# BERTopic CountVectorizer의 stop_words 인자에 직접 주입
# =====================================================
KO_STOPWORDS: list[str] = [
    # 조사 (형태소 분석 후에도 잔존하는 것들)
    "이", "가", "을", "를", "은", "는", "의", "에", "와", "과",
    "도", "로", "으로", "에서", "에게", "한테", "부터", "까지",
    "이나", "나", "만", "뿐", "마다", "씩", "란", "이란",
    # 어미/보조 용언 (nouns 모드에서도 간혹 등장)
    "하다", "되다", "있다", "없다", "이다", "아니다",
    # 접속/부사
    "그리고", "하지만", "그러나", "또한", "따라서", "그래서",
    "즉", "및", "등", "등등", "또", "더", "매우", "아주",
    "정말", "특히", "약", "각", "여러", "다양한",
    # 의존 명사 (단독으로는 의미 없음)
    "것", "수", "때", "곳", "분", "전", "후", "중",
    "내", "외", "간", "상", "하", "대", "기",
    # 단음절 형태소 파생 잔재
    "화", "형", "용", "별", "식", "형태", "방식",
    # 뉴스 도메인 공통 불용어 (거의 모든 기사에 등장 → 변별력 없음)
    "기자", "뉴스", "보도", "관련", "따른", "통해", "위해",
    "대한", "지난", "오는", "올해", "이번", "해당", "현재", "최근",
    "밝혔다", "했다", "한다", "된다", "있다",    
]

class TextPreprocessor:
    """뉴스 텍스트 전처리 담당 클래스

    - HTML 태그/앤티티 제거
    - 뉴스 특수문자(▲△·…) 제거
    - 괄호류 () [] <> 제거
    - 연속 공백 정리
    - 단독 인스턴스화 후 재사용(매 호출마다 생성 불필요)
    """

    # 전처리 단계별 정규식을 클래스 변수로 캐싱
    # → 인스턴스 생성 시점에 한 번만 컴파일, 호출마다 재컴파일 없음
    _RE_HTML_TAG: re.Pattern[str] = re.compile(r"<[^>]+>")
    _RE_HTML_ENTITY: re.Pattern[str] = re.compile(r"&[a-zA-Z#0-9]+;")
    _RE_SPECIAL_CHARS: re.Pattern[str] = re.compile(
        r"[▲△▶▷◆◇■□●○◎☆★※→←↑↓·…·''""「」『』【】《》〈〉〔〕]"
    )
    # 괄호류 — 네이버 뉴스 description에서 "(AI)" 형태로 자주 등장
    _RE_BRACKETS: re.Pattern[str] = re.compile(r"[(){}\[\]<>]")
    # 한글/영문/숫자/공백 외 모든 문자 제거 (구두점, 특수기호 일괄 처리)
    _RE_NON_WORD: re.Pattern[str] = re.compile(r"[^\w\s가-힣a-zA-Z0-9]")
    # 연속 공백 -> 단일 공백
    _RE_WHITESPACE: re.Pattern[str] = re.compile(r"\s+")

    def clean(self, text: str) -> str:
        """단일 문자열 정제 - 6단계 순차 처리(순서가 중요)
        
        처리 순서:
            1. HTML 태그 제거
            2. HTML 엔티티 제거
            3. 뉴스 특수문자 제거
            4. 괄호류 제거
            5. 나머지 비단어 문자 제거
            6. 연속 공백 -> 단일 공백
        """
        text = self._RE_HTML_TAG.sub("", text)
        text = self._RE_HTML_ENTITY.sub(" ", text)
        text = self._RE_SPECIAL_CHARS.sub(" ", text)
        text = self._RE_BRACKETS.sub(" ", text)
        text = self._RE_NON_WORD.sub(" ", text)
        text = self._RE_WHITESPACE.sub(" ", text)
        return text.strip()
    

    def clean_article(self, article: dict) -> dict:
        """기사 dict의 title + description만 정제해서 새 dict 반환

        원본 dict를 직접 수정하지 않고 새 dict를 반환
        -> 불변성 유지, 디버깅 시 원본 데이터 확인 가능
        """
        return {
            **article,  # originallink, link, pubDate 등 원본유지
            "title": self.clean(article.get("title", "")),
            "description": self.clean(article.get("description", ""))
        }