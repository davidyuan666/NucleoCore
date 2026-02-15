#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot 启动脚本
通过 Telegram 控制 Twitter 和邮件
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.telegram_bot import TelegramBot
from src.twitter_manager import TwitterManager
from src.email_manager import EmailManager
from src.twitter135_manager import Twitter135Manager
from src.utils.logger import setup_logger


def main():
    """主函数"""
    # 设置日志
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info("启动 Telegram Bot")
    logger.info("=" * 60)

    # 检查配置
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        logger.error("❌ 未配置 Telegram Bot")
        logger.error("请在 .env 文件中配置:")
        logger.error("  TELEGRAM_BOT_TOKEN=你的机器人token")
        logger.error("  TELEGRAM_CHAT_ID=你的chat_id")
        sys.exit(1)

    logger.info(f"Bot Token: {bot_token[:20]}...")
    logger.info(f"Chat ID: {chat_id}")

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
        logger.info("初始化 Twitter 管理器...")
        twitter_manager = TwitterManager(twitter_config)

        logger.info("初始化邮件管理器...")
        email_manager = EmailManager(email_config)

        # 初始化 Twitter135 RapidAPI
        logger.info("初始化 Twitter135 RapidAPI...")
        try:
            twitter135_manager = Twitter135Manager()
            logger.info("✓ Twitter135 API 可用")
        except Exception as e:
            logger.warning(f"Twitter135 API 初始化失败: {e}")
            twitter135_manager = None

        # 初始化 Telegram Bot
        logger.info("初始化 Telegram Bot...")
        telegram_bot = TelegramBot(twitter_manager, email_manager, twitter135_manager)

        logger.info("=" * 60)
        logger.info("✅ Telegram Bot 已启动")
        logger.info("=" * 60)
        logger.info("")
        logger.info("可用命令:")
        logger.info("  /start - 开始使用")
        logger.info("  /help - 帮助信息")
        logger.info("  /tweet - 发送推文")
        logger.info("  /mytweets - 查看推文")
        logger.info("  /twitterinfo - Twitter 账户信息")
        logger.info("  /userinfo - 查看任意用户信息（RapidAPI）")
        logger.info("  /checkemail - 检查邮件")
        logger.info("  /status - 系统状态")
        logger.info("")
        logger.info("💡 提示: 直接发送文字消息将作为推文发布")
        logger.info("")
        logger.info("按 Ctrl+C 停止机器人")
        logger.info("=" * 60)

        # 运行机器人
        telegram_bot.run()

    except KeyboardInterrupt:
        logger.info("\n收到停止信号，正在关闭...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
