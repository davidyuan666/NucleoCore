#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作调度器启动脚本
自动检查邮件、执行任务、汇报工作状态
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.work_scheduler import WorkScheduler
from src.email_manager import EmailManager
from src.telegram_bot import TelegramBot
from src.twitter_manager import TwitterManager
from src.twitter135_manager import Twitter135Manager
from src.utils.logger import setup_logger


async def main():
    """主函数"""
    # 设置日志
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info("启动工作调度器")
    logger.info("=" * 60)

    # 检查配置
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    email_address = os.getenv('EMAIL_ADDRESS')

    if not all([bot_token, chat_id, email_address]):
        logger.error("❌ 配置不完整")
        logger.error("请确保 .env 文件中配置了:")
        logger.error("  - TELEGRAM_BOT_TOKEN")
        logger.error("  - TELEGRAM_CHAT_ID")
        logger.error("  - EMAIL_ADDRESS")
        logger.error("  - EMAIL_PASSWORD")
        sys.exit(1)

    logger.info(f"工作邮箱: {email_address}")
    logger.info(f"Telegram Chat ID: {chat_id}")

    # 初始化配置
    twitter_config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    email_config = {
        'rate_limit': {
            'max_emails_per_day': 200
        }
    }

    try:
        # 初始化管理器
        logger.info("初始化 Email 管理器...")
        email_manager = EmailManager(email_config)

        logger.info("初始化 Twitter 管理器...")
        twitter_manager = TwitterManager(twitter_config)

        logger.info("初始化 Twitter135 RapidAPI...")
        try:
            twitter135_manager = Twitter135Manager()
            logger.info("✓ Twitter135 API 可用")
        except Exception as e:
            logger.warning(f"Twitter135 API 初始化失败: {e}")
            twitter135_manager = None

        logger.info("初始化 Telegram Bot...")
        telegram_bot = TelegramBot(twitter_manager, email_manager, twitter135_manager)

        # 初始化工作调度器
        logger.info("初始化工作调度器...")
        work_scheduler = WorkScheduler(email_manager, telegram_bot)

        logger.info("=" * 60)
        logger.info("✅ 所有组件初始化完成")
        logger.info("=" * 60)
        logger.info("")
        logger.info("工作调度器功能:")
        logger.info("  📬 定时检查邮件 (每10分钟)")
        logger.info("  🔄 自动执行任务")
        logger.info("  📊 定时汇报状态 (每60分钟)")
        logger.info("")
        logger.info("按 Ctrl+C 停止")
        logger.info("=" * 60)

        # 运行工作调度器
        await work_scheduler.run()

    except KeyboardInterrupt:
        logger.info("\n收到停止信号，正在关闭...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
