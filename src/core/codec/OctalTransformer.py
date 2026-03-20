"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

import re

from src.core.codec.BaseTransformer import BaseTransformer


class OctalTransformer(BaseTransformer):
    _pattern = re.compile(r'\\[0-7]{3}')

    @property
    def codec_type(self) -> str:
        return 'octal'

    def encode(self, target: str) -> str:
        # UTF-8 바이트 기준으로 encode (멀티바이트 문자 안전)
        return ''.join(f'\\{b:03o}' for b in target.encode('utf-8'))

    def decode(self, target: str) -> str:
        try:
            parts = self._pattern.split(target)
            oct_matches = self._pattern.findall(target)
            raw_bytes = bytearray()
            for idx, part in enumerate(parts):
                raw_bytes.extend(part.encode('utf-8'))
                if idx < len(oct_matches):
                    raw_bytes.append(int(oct_matches[idx][1:], 8))
            return raw_bytes.decode('utf-8', errors='replace')
        except Exception:
            return target

    def is_encoded(self, target: str) -> bool:
        return bool(self._pattern.search(target))
