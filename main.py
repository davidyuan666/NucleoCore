#!/usr/bin/env python3
"""
Social Account Manager - 主程序入口
安全合规的 Gmail 和 Twitter 账户管理工具
"""

import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

from src.email_manager import EmailManager
from src.twitter_manager import TwitterManager
from src.scheduler import TaskScheduler
from src.utils.config import load_config
from src.utils.logger import setup_logger


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 设置日志
    logger = setup_logger()
    logger.info("启动 Social Account Manager")

    # 加载配置
    try:
        config = load_config()
    except FileNotFoundError:
        logger.error("配置文件不存在，请复制 config.example.json 到 config.json")
        sys.exit(1)

    # 检查是否为演练模式
    if config.get('safety', {}).get('dry_run_mode', True):
        logger.warning("当前处于演练模式，不会执行实际操作")

    # 初始化管理器
    email_manager = EmailManager(config['email'])
    twitter_manager = TwitterManager(config['twitter'])

    # 初始化调度器
    scheduler = TaskScheduler(config['schedule'])

    # 注册任务
    scheduler.register_task('check_email', email_manager.check_new_emails)
    scheduler.register_task('backup', lambda: backup_all(email_manager, twitter_manager))

    logger.info("所有服务已启动")

    # 运行调度器
    try:
        scheduler.run()
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭...")
        sys.exit(0)


def backup_all(email_manager, twitter_manager):
    """执行完整备份"""
    logger = logging.getLogger(__name__)
    logger.info("开始执行备份任务")

    try:
        email_manager.backup_emails()
        twitter_manager.backup_tweets()
        logger.info("备份任务完成")
    except Exception as e:
        logger.error(f"备份失败: {e}")


if __name__ == "__main__":
    main()
