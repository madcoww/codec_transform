"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

from logging import Logger
from typing import AsyncIterator, ClassVar

from src.common.Constant import Constants
from src.common.LoggerManager import LoggerManager
from src.core.codec.Base64Transformer import Base64Transformer
from src.core.codec.Base64UrlTransformer import Base64UrlTransformer
from src.core.codec.BaseTransformer import BaseTransformer
from src.core.codec.HexTransformer import HexTransformer
from src.core.codec.HtmlEntityTransformer import HtmlEntityTransformer
from src.core.codec.OctalTransformer import OctalTransformer
from src.core.codec.UnicodeTransformer import UnicodeTransformer
from src.core.codec.UrlTransformer import UrlTransformer
from src.core.codec.XmlEntityTransformer import XmlEntityTransformer
from src.models.CodecRequest import CodecRequest


class CodecProcessor:
    _registry: ClassVar[dict[str, BaseTransformer]] = {
        'url': UrlTransformer(),
        'base64': Base64Transformer(),
        'base64url': Base64UrlTransformer(),
        'unicode': UnicodeTransformer(),
        'html': HtmlEntityTransformer(),
        'hex': HexTransformer(),
        'octal': OctalTransformer(),
        'xml': XmlEntityTransformer(),
    }
    _detect_order: ClassVar[list[str]] = [
        'hex', 'octal', 'unicode', 'xml', 'html', 'url', 'base64url', 'base64',
    ]

    def __init__(self):
        self.logger: Logger = LoggerManager.get()

    def _get(self, codec_type: str) -> BaseTransformer:
        transformer = self._registry.get(codec_type)
        if transformer is None:
            raise ValueError(f"Unsupported codec type: '{codec_type}'. Available: {list(self._registry.keys())}")
        return transformer

    def _detect(self, target: str) -> str | None:
        for codec_type in self._detect_order:
            if self._registry[codec_type].is_encoded(target):
                return codec_type
        return None

    async def process_stream(self, request: CodecRequest) -> AsyncIterator[dict]:
        targets = [request.target] if isinstance(request.target, str) else request.target
        direction = request.direction
        codec_type = request.codec_type

        self.logger.info(f'Processing request: direction={direction}, codec_type={codec_type}, encode_chain={request.encode_chain}, target_count={len(targets)}')

        if request.encode_chain is not None:
            async for chunk in self._multi_layer_encode(targets, request):
                yield chunk
        elif direction == 'decode' and codec_type is None:
            async for chunk in self._multi_layer_decode(targets, request):
                yield chunk
        else:
            async for chunk in self._single_layer(targets, request):
                yield chunk

    async def _multi_layer_decode(self, targets: list[str], request: CodecRequest) -> AsyncIterator[dict]:
        current = list(targets)
        applied_codecs: list[str] = []

        for i in range(Constants.MAX_ITERATIONS):
            detected = self._detect(current[0])

            if detected is None:
                self.logger.info(f'No more encoding detected after {i} layer(s)')
                break

            self.logger.info(f'[Layer {i + 1}] Detected: {detected}')
            yield {
                'stage': 'detecting',
                'message': f'[Layer {i + 1}] Detected: {detected}',
                'result': {'layer': i + 1, 'codec_type': detected},
            }

            try:
                transformer = self._get(detected)
                decoded = [transformer.decode(item) for item in current]
            except Exception as e:
                self.logger.error(f'[Layer {i + 1}] Decoding failed: {e}')
                yield {
                    'stage': 'error',
                    'message': f'[Layer {i + 1}] Decoding failed',
                    'result': {
                        'status': 'failed',
                        'error': 'ProcessingError',
                        'message': str(e),
                        'result': {},
                    },
                }
                return

            if decoded == current:
                self.logger.info(f'[Layer {i + 1}] No change after decoding, stopping')
                break

            applied_codecs.append(detected)
            current = decoded

            self.logger.info(f'[Layer {i + 1}] Decoded with {detected}')
            yield {
                'stage': 'decoded',
                'message': f'[Layer {i + 1}] Decoded with {detected}',
                'result': {
                    'layer': i + 1,
                    'codec_type': detected,
                    'current': current[0] if isinstance(request.target, str) else current,
                },
            }

        output = current[0] if isinstance(request.target, str) else current
        self.logger.info(f'Multi-layer decode completed: applied_codecs={applied_codecs}')
        yield {
            'stage': 'final',
            'message': f'{len(applied_codecs)} layer(s) decoded',
            'result': {
                'status': 'success',
                'error': None,
                'message': f'Applied codecs: {" → ".join(applied_codecs)}' if applied_codecs else 'No encoding detected',
                'result': {
                    'target': request.target,
                    'output': output,
                    'applied_codecs': applied_codecs,
                    'direction': 'decode',
                },
            },
        }

    async def _multi_layer_encode(self, targets: list[str], request: CodecRequest) -> AsyncIterator[dict]:
        current = list(targets)
        chain = request.encode_chain
        is_single = isinstance(request.target, str)

        for i, codec_type in enumerate(chain):
            self.logger.info(f'[Layer {i + 1}] Encoding with {codec_type}')
            yield {
                'stage': 'encoding',
                'message': f'[Layer {i + 1}] Encoding with {codec_type}',
                'result': {'layer': i + 1, 'codec_type': codec_type},
            }

            try:
                transformer = self._get(codec_type)
                current = [transformer.encode(item) for item in current]
            except Exception as e:
                self.logger.error(f'[Layer {i + 1}] Encoding failed: {e}')
                yield {
                    'stage': 'error',
                    'message': f'[Layer {i + 1}] Encoding failed',
                    'result': {
                        'status': 'failed',
                        'error': 'ProcessingError',
                        'message': str(e),
                        'result': {},
                    },
                }
                return

            yield {
                'stage': 'encoded',
                'message': f'[Layer {i + 1}] Encoded with {codec_type}',
                'result': {
                    'layer': i + 1,
                    'codec_type': codec_type,
                    'current': current[0] if is_single else current,
                },
            }

        output = current[0] if is_single else current
        self.logger.info(f'Multi-layer encode completed: encode_chain={list(chain)}')
        yield {
            'stage': 'final',
            'message': f'{len(chain)} layer(s) encoded',
            'result': {
                'status': 'success',
                'error': None,
                'message': f'Applied codecs: {" → ".join(chain)}',
                'result': {
                    'target': request.target,
                    'output': output,
                    'applied_codecs': list(chain),
                    'direction': 'encode',
                },
            },
        }

    async def _single_layer(self, targets: list[str], request: CodecRequest) -> AsyncIterator[dict]:
        direction = request.direction
        codec_type = request.codec_type
        is_single = isinstance(request.target, str)

        if codec_type is None:
            yield {'stage': 'detecting', 'message': 'Detecting codec type', 'result': {}}
            codec_type = self._detect(targets[0])

            if codec_type is None:
                self.logger.warning('Auto-detect failed: no codec type found')
                yield {
                    'stage': 'error',
                    'message': 'Could not detect codec type',
                    'result': {
                        'status': 'failed',
                        'error': 'DetectionError',
                        'message': 'Unable to detect codec type automatically',
                        'result': {},
                    },
                }
                return

            self.logger.info(f'Auto-detected codec type: {codec_type}')
            yield {
                'stage': 'detected',
                'message': f'Codec detected: {codec_type}',
                'result': {'codec_type': codec_type},
            }

        action = 'Encoding' if direction == 'encode' else 'Decoding'
        self.logger.info(f'{action} with {codec_type}')
        yield {'stage': 'processing', 'message': f'{action} with {codec_type}', 'result': {}}

        try:
            transformer = self._get(codec_type)
            results = [
                transformer.encode(item) if direction == 'encode' else transformer.decode(item)
                for item in targets
            ]
        except Exception as e:
            self.logger.error(f'{action} failed: {e}')
            yield {
                'stage': 'error',
                'message': 'Processing failed',
                'result': {
                    'status': 'failed',
                    'error': 'ProcessingError',
                    'message': str(e),
                    'result': {},
                },
            }
            return

        output = results[0] if is_single else results
        self.logger.info(f'{action} completed with {codec_type}')
        yield {
            'stage': 'final',
            'message': 'Completed',
            'result': {
                'status': 'success',
                'error': None,
                'message': f'{action} completed',
                'result': {
                    'target': request.target,
                    'output': output,
                    'codec_type': codec_type,
                    'direction': direction,
                },
            },
        }
