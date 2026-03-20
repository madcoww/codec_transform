"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

import re
import urllib.parse

from src.core.codec.BaseTransformer import BaseTransformer


class UrlTransformer(BaseTransformer):
    _pattern = re.compile(r'%[0-9A-Fa-f]{2}')

    @property
    def codec_type(self) -> str:
        return 'url'

    def encode(self, target: str) -> str:
        return urllib.parse.quote(target, safe='')

    def decode(self, target: str) -> str:
        try:
            return urllib.parse.unquote(target)
        except Exception:
            return target

    def is_encoded(self, target: str) -> bool:
        return '%' in target and bool(self._pattern.search(target))
