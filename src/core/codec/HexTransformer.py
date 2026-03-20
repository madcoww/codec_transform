"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

import re

from src.core.codec.BaseTransformer import BaseTransformer


class HexTransformer(BaseTransformer):
    _escape_pattern = re.compile(r'\\x[0-9a-fA-F]{2}')
    _pure_pattern = re.compile(r'^[0-9a-fA-F]+$')

    @property
    def codec_type(self) -> str:
        return 'hex'

    def encode(self, target: str) -> str:
        # UTF-8 바이트 기준으로 encode (멀티바이트 문자 안전)
        return ''.join(f'\\x{b:02x}' for b in target.encode('utf-8'))

    def decode(self, target: str) -> str:
        # \x48\x65 형태
        if self._escape_pattern.search(target):
            try:
                parts = self._escape_pattern.split(target)
                hex_matches = self._escape_pattern.findall(target)
                raw_bytes = bytearray()
                for idx, part in enumerate(parts):
                    raw_bytes.extend(part.encode('utf-8'))
                    if idx < len(hex_matches):
                        raw_bytes.append(int(hex_matches[idx][2:], 16))
                return raw_bytes.decode('utf-8', errors='replace')
            except Exception:
                return target

        # 순수 hex 페어 형태 (짝수 길이)
        if self._pure_pattern.match(target) and len(target) % 2 == 0:
            try:
                return bytes.fromhex(target).decode('utf-8')
            except Exception:
                return target

        return target

    def is_encoded(self, target: str) -> bool:
        return bool(self._escape_pattern.search(target))
