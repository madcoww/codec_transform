"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

import base64
import re

from src.core.codec.BaseTransformer import BaseTransformer


class Base64UrlTransformer(BaseTransformer):
    _pattern = re.compile(r'^[A-Za-z0-9\-_]+=*$')

    @property
    def codec_type(self) -> str:
        return 'base64url'

    def encode(self, target: str) -> str:
        return base64.urlsafe_b64encode(target.encode('utf-8')).decode('utf-8')

    def decode(self, target: str) -> str:
        try:
            padded = target + '=' * (-len(target) % 4)
            decoded_bytes = base64.urlsafe_b64decode(padded)
            for encoding in ['utf-8', 'euc-kr']:
                try:
                    return decoded_bytes.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return decoded_bytes.decode('utf-8', errors='replace')
        except Exception:
            return target

    def is_encoded(self, target: str) -> bool:
        # 반드시 - 또는 _ 가 포함돼야 Base64URL로 구분 (일반 Base64와 구별)
        if len(target) < 8:
            return False
        if '-' not in target and '_' not in target:
            return False
        if not self._pattern.match(target):
            return False
        if len(target) % 4 == 1:
            return False
        try:
            padded = target + '=' * (-len(target) % 4)
            decoded = base64.urlsafe_b64decode(padded)
            decoded_str = decoded.decode('utf-8', errors='replace')
            unprintable = sum(1 for c in decoded_str if not c.isprintable())
            if unprintable > len(decoded_str) * 0.3:
                return False
        except Exception:
            return False
        return True
