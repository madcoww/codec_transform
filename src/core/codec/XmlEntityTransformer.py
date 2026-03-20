"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

import re

from src.core.codec.BaseTransformer import BaseTransformer


class XmlEntityTransformer(BaseTransformer):
    _pattern = re.compile(r'&#(x[0-9a-fA-F]+|[0-9]+);')

    @property
    def codec_type(self) -> str:
        return 'xml'

    def encode(self, target: str) -> str:
        return ''.join(f'&#{ord(c)};' for c in target)

    def decode(self, target: str) -> str:
        def _replace(m: re.Match) -> str:
            value = m.group(1)
            code_point = int(value[1:], 16) if value.startswith('x') else int(value)
            try:
                return chr(code_point)
            except (ValueError, OverflowError):
                return m.group(0)

        try:
            return self._pattern.sub(_replace, target)
        except Exception:
            return target

    def is_encoded(self, target: str) -> bool:
        return bool(self._pattern.search(target))
