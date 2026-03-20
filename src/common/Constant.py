"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

from typing import cast

from src.common.ConfigManager import ConfigManager
from src.utils.Singleton import Singleton


class Constants(metaclass=Singleton):
    __config_manager = ConfigManager()

    CODEC_PREFIX: str = cast(str, __config_manager.get('codec_prefix'))
    CODEC_ENDPOINT: str = cast(str, __config_manager.get('codec_endpoint'))
    CODEC_PORT: int = int(cast(str, __config_manager.get('codec_port')))
    MAX_ITERATIONS: int = int(cast(str, __config_manager.get('max_iterations')))
