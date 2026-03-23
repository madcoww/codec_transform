"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic import field_validator
from pydantic import model_validator

SUPPORTED_CODECS = {'url', 'base64', 'base64url', 'unicode', 'html', 'hex', 'octal', 'xml'}


class CodecRequest(BaseModel):
    target: str | list[str]
    direction: Literal['encode', 'decode']
    codec_type: str | None = None       # 단일 encode/decode
    encode_chain: list[str] | None = None  # multi-layer encode

    @field_validator('target')
    @classmethod
    def validate_target(cls, v: str | list[str]) -> str | list[str]:
        if isinstance(v, list):
            if len(v) == 0:
                raise ValueError('target list cannot be empty')
            if any(not isinstance(item, str) or not item.strip() for item in v):
                raise ValueError('target list items cannot be empty strings')
        elif not v.strip():
            raise ValueError('target string cannot be empty')
        return v

    @model_validator(mode='after')
    def validate_request(self) -> CodecRequest:
        # codec_type과 encode_chain 동시 지정 차단
        if self.codec_type is not None and self.encode_chain is not None:
            raise ValueError('codec_type and encode_chain cannot be used together')

        # encode 시 codec_type 또는 encode_chain 중 하나 필수
        if self.direction == 'encode' and self.codec_type is None and self.encode_chain is None:
            raise ValueError('codec_type or encode_chain is required for encoding')

        # decode 시 encode_chain 사용 불가
        if self.direction == 'decode' and self.encode_chain is not None:
            raise ValueError('encode_chain cannot be used with decode direction')

        # codec_type 허용값 검증
        if self.codec_type is not None and self.codec_type not in SUPPORTED_CODECS:
            raise ValueError(f"Unsupported codec_type: '{self.codec_type}'. Supported: {sorted(SUPPORTED_CODECS)}")

        # encode_chain 각 항목 허용값 검증
        if self.encode_chain is not None:
            if len(self.encode_chain) == 0:
                raise ValueError('encode_chain cannot be empty')
            invalid = [c for c in self.encode_chain if c not in SUPPORTED_CODECS]
            if invalid:
                raise ValueError(f"Unsupported codec in encode_chain: {invalid}. Supported: {sorted(SUPPORTED_CODECS)}")

        return self
