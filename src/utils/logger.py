"""日志配置"""

import logging
import os
from datetime import datetime


def setup_logger(log_level: str = 'INFO') -> logging.Logger:
    """设置日志系统"""
    # 创建日志目录
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件名
    log_file = f"{log_dir}/app_{datetime.now().strftime('%Y%m%d')}.log"

    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger('social_account_manager')
