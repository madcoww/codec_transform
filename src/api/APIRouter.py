"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import StreamingResponse

from src.common.Constant import Constants
from src.core.CodecProcessor import CodecProcessor
from src.models.CodecRequest import CodecRequest


def _sse_event(stage: str, message: str, result: dict | None = None) -> str:
    """SSE(Server-Sent Events) 포맷 문자열 생성.
    형식: "event: {stage}\\ndata: {json}\\n\\n"
    """
    data = {'stage': stage, 'message': message, 'result': result or {}}
    return f"event: {stage}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 CodecProcessor 초기화, 종료 시 정리.
    app.state.processor 에 인스턴스 저장 → 엔드포인트에서 참조.
    """
    app.state.processor = CodecProcessor()
    yield


app = FastAPI(lifespan=lifespan)
router = APIRouter()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> StreamingResponse:
    """Pydantic 검증 실패 시 422 JSON 대신 SSE 에러 스트림으로 반환.
    클라이언트가 항상 SSE 포맷으로 응답 받을 수 있도록 통일.
    """
    messages = [f"{' → '.join(str(l) for l in e['loc'][1:])}: {e['msg']}" for e in exc.errors()]
    message = ' / '.join(messages)

    async def error_stream():
        yield _sse_event('error', message, {'status': 'failed', 'error': 'ValidationError', 'message': message, 'result': {}})

    return StreamingResponse(error_stream(), media_type='text/event-stream')


@router.post(Constants.CODEC_PREFIX + Constants.CODEC_ENDPOINT)
async def codec(request: CodecRequest) -> StreamingResponse:
    """인코딩/디코딩 SSE 스트리밍 엔드포인트.

    SSE 이벤트 흐름:
        정상: start → detecting/encoding/processing → decoded/encoded/final → done
        에러: start → ... → error

    Request Body (CodecRequest):
        target       : str | list[str]          - 변환 대상
        direction    : "encode" | "decode"       - 변환 방향
        codec_type   : str | None               - 단일 변환 시 코덱 지정 (decode None=auto-detect)
        encode_chain : list[str] | None         - multi-layer 인코딩 체이닝 (예: ["url", "url"])
        * codec_type 과 encode_chain 은 동시 사용 불가
    """
    # lifespan 이전 접근 방어 (AttributeError 방지)
    processor: CodecProcessor = getattr(app.state, 'processor', None)
    if processor is None:
        async def not_ready():
            yield _sse_event('error', 'Processor not initialized', {'status': 'failed', 'error': 'ServiceUnavailable', 'message': 'Processor not initialized', 'result': {}})
        return StreamingResponse(not_ready(), media_type='text/event-stream')

    async def event_stream():
        try:
            yield _sse_event('start', 'Codec processing started')

            async for chunk in processor.process_stream(request):
                stage = chunk.get('stage')
                yield f"event: {stage}\ndata: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        except Exception as e:
            # 내부 예외 상세는 노출하지 않고 타입명만 전달
            yield _sse_event('error', f'Stream error: {type(e).__name__}')

        else:
            # 예외 없이 정상 종료 시에만 done 이벤트 전송
            yield _sse_event('done', 'Codec processing completed')

    return StreamingResponse(event_stream(), media_type='text/event-stream')


app.include_router(router)
