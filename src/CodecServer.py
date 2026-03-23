"""
Author : Wonjun Kim
e-mail : wonjun.kim@seculayer.com
Powered by Seculayer © 2025 AI Team, R&D Center.
"""
from __future__ import annotations

from src.common.Constant import Constants

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app='src.api.APIRouter:app',
        host='0.0.0.0',
        port=Constants.CODEC_PORT,
        workers=4,
        reload=False,
    )
