"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

import re

from src.core.codec.BaseTransformer import BaseTransformer


class UnicodeTransformer(BaseTransformer):
    # \u0041 (BMP) 및 \U0001F600 (non-BMP) 지원
    _pattern = re.compile(r'\\U[0-9a-fA-F]{8}|\\u[0-9a-fA-F]{4}')

    @property
    def codec_type(self) -> str:
        return 'unicode'

    def encode(self, target: str) -> str:
        result = []
        for c in target:
            cp = ord(c)
            if cp > 0xFFFF:
                result.append(f'\\U{cp:08x}')
            elif cp > 127:
                result.append(f'\\u{cp:04x}')
            else:
                result.append(c)
        return ''.join(result)

    def decode(self, target: str) -> str:
        def _replace(m: re.Match) -> str:
            s = m.group(0)
            cp = int(s[2:], 16)
            try:
                return chr(cp)
            except (ValueError, OverflowError):
                return s

        try:
            return self._pattern.sub(_replace, target)
        except Exception:
            return target

    def is_encoded(self, target: str) -> bool:
        return bool(self._pattern.search(target))
