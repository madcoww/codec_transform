"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class BaseTransformer(ABC):

    @property
    @abstractmethod
    def codec_type(self) -> str: ...

    @abstractmethod
    def encode(self, target: str) -> str: ...

    @abstractmethod
    def decode(self, target: str) -> str: ...

    @abstractmethod
    def is_encoded(self, target: str) -> bool: ...
