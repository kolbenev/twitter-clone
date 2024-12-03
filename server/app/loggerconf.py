"""
Модуль конфигурации логгера.
"""

import logging

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)
