"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

import html
import re

from src.core.codec.BaseTransformer import BaseTransformer


class HtmlEntityTransformer(BaseTransformer):
    _pattern = re.compile(r'&[#a-zA-Z0-9]+;')

    @property
    def codec_type(self) -> str:
        return 'html'

    def encode(self, target: str) -> str:
        return html.escape(target)

    def decode(self, target: str) -> str:
        try:
            return html.unescape(target)
        except Exception:
            return target

    def is_encoded(self, target: str) -> bool:
        return bool(self._pattern.search(target))
