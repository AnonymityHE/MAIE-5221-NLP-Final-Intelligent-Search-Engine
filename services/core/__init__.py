"""
核心基础设施模块
"""
from services.core.config import settings
from services.core.logger import logger, setup_logger

__all__ = ["settings", "logger", "setup_logger"]

