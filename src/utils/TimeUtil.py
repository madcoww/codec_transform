"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


class TimeUtil:

    @staticmethod
    def now_kst() -> datetime:
        """한국시간 기준 datetime 객체"""
        return datetime.now(ZoneInfo('Asia/Seoul'))

    @staticmethod
    def now_kst_standard() -> str:
        """
        한국시간 기준: YYYY-MM-DD HH:MM:SS
        예) 2025-07-14 10:36:00
        """
        return datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def now_kst_compact() -> str:
        """
        한국시간 기준: YYYYMMDDHHMMSS
        예) 20250714103600
        """
        return datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d%H%M%S')
