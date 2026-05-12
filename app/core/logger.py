"""
logger 초기화 모듈
- loguru 기발 구조화 로깅
"""
import sys
from loguru import logger

def setup_logger() -> None:
    """로거 설정을 초기화. main.py lifespan에서 1회 호출"""
    # 기본 핸들러 제거 후 재설정
    logger.remove()

    # 콘솔 출력: 컬러 + 구조화 포맷
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> |"
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> |"
            "{message}"
        ),
        level="INFO",
        colorize=True,
    )

    # 파일 출력: 일별 쿨링, 7일 보관
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        encoding="utf-8"
    )

__all__ = ["logger", "setup_logger"]